# Placeholder to prevent error since I am just checking state

import asyncio
import signal
import sys
import time
from datetime import datetime
import nest_asyncio
nest_asyncio.apply()
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from .env file before any other imports that might use them
load_dotenv()

from .tick_stream import TickStreamer
from .candle_engine import CandleEngine
from .microstructure import compute_microstructure
from .ws_push import push, start_connection
from .logger import get_logger
from ai_core.strategy_engine.strategy_manager import StrategyManager
from ai_core.strategy_engine.signal_router import SignalRouter
from ai_core.genai.llm_agent import LLMAgent
from ai_core.genai.news_analyzer import NewsAnalyzer
from ai_core.backtesting.vbt_engine import VectorBTEngine

logger = get_logger(__name__)

# Global flag for graceful shutdown
shutdown_flag = False

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_flag
    logger.info("=" * 80)
    logger.info("Shutdown signal received. Initiating graceful shutdown...")
    shutdown_flag = True

def get_trade_history():
    """Fetch recent trades from SQLite database."""
    try:
        engine = create_engine("sqlite:///./trading.db")
        # Ensure we don't lock the DB, use read_sql
        df = pd.read_sql("SELECT * FROM trades ORDER BY id DESC LIMIT 50", engine)
        if df.empty:
            return []
        # Convert timestamp to string/float as needed for JSON
        # df['entry_time'] = df['entry_time'].astype(str) 
        return df.to_dict(orient='records')
    except Exception as e:
        logger.error(f"Error reading trade history: {e}")
        return []

async def main():
    """Main execution loop for IBKR streaming service"""
    global shutdown_flag
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("=" * 80)
    logger.info("IBKR Streaming Service Starting")
    logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    
    tick_count = 0  # Initialize before try block for finally clause
    iteration = 0
    
    try:
        # Initialize components
        logger.info("Initializing TickStreamer...")
        tick_stream = TickStreamer()
        await tick_stream.initialize()
        
        logger.info("Initializing CandleEngine...")
        candle_engine = CandleEngine()

        # Initialize Strategy Engine
        logger.info("Initializing Strategy Engine...")
        strategy_manager = StrategyManager()
        signal_router = SignalRouter(push)
        vector_bt_engine = VectorBTEngine()

        # Initialize LLM Brain Agent
        logger.info("Initializing LLM Brain Agent (Groq)...")
        try:
            llm_agent = LLMAgent()
            logger.info(f"✅ LLM Brain Agent ready — model: {llm_agent.model_name}")
        except Exception as llm_init_err:
            logger.warning(f"⚠️  LLM Agent unavailable: {llm_init_err}")
            llm_agent = None

        # Initialize News Analyzer
        logger.info("Initializing News Sentiment Analyzer...")
        try:
            news_analyzer = NewsAnalyzer()
            logger.info("✅ News Analyzer ready")
        except Exception as news_init_err:
            logger.warning(f"⚠️  News Analyzer unavailable: {news_init_err}")
            news_analyzer = None
            
        global_news_state = {}
        
        # ----------------------------------------------------------------------------
        # BACKGROUND TASKS
        # ----------------------------------------------------------------------------
        async def fetch_macro_bias():
            """Phase 6: Real LLM Scheduled Bias (Every 4 hours)"""
            while not shutdown_flag:
                try:
                    if news_analyzer:
                        logger.info("🌍 [LLM MACRO] Fetching global news for Macro Sentiment Bias...")
                        macro_analysis = await news_analyzer.analyze_by_symbol("EURUSD")
                        
                        # Convert JSON sentiment to a 0-20 score for the TradeQualityScorer
                        sentiment = macro_analysis.get('sentiment', 'NEUTRAL')
                        if sentiment == "BULLISH":
                            # Assuming trend-following systems benefit from bullish structure when long
                            score = 18 
                        elif sentiment == "BEARISH":
                            score = 18 # Strong trend in either direction is good
                        else:
                            score = 10
                            
                        # Inject into StrategyManager
                        strategy_manager.current_macro_score = score
                        strategy_manager.current_macro_summary = macro_analysis.get('summary', '')
                        logger.info(f"🧠 [LLM MACRO] Updated Macro Score: {score}/20 - {macro_analysis.get('summary', '')[:100]}...")
                except Exception as e:
                    logger.error(f"Error fetching macro bias: {e}")
                    
                # Sleep for 4 hours (14400 seconds)
                await asyncio.sleep(14400)
                
        # Start background macro loop
        if news_analyzer:
            asyncio.create_task(fetch_macro_bias())
            
        async def fetch_news_loop():
            while not shutdown_flag:
                try:
                    if news_analyzer:
                        logger.info("Fetching and analyzing latest news...")
                        news_data = await news_analyzer.analyze_by_symbol("EURUSD")
                        global_news_state["EURUSD"] = news_data
                        await push({"type": "news_sentiment", "data": news_data})
                except Exception as e:
                    logger.error(f"News fetch loop error: {e}")
                
                # Sleep for 1 minute (60 seconds) as requested by user
                await asyncio.sleep(400)
                
        asyncio.create_task(fetch_news_loop())
        
        # ----------------------------------------------------------------------------
        # COMMAND HANDLER for Remote Strategy Control
        # ----------------------------------------------------------------------------
        async def handle_remote_command(data: dict):
            """Handle incoming commands from Node Gateway/Frontend."""
            try:
                cmd_type = data.get("type")
                
                if cmd_type == "structure_command": # From Node Gateway
                    command = data.get("command")
                    strategy_id = data.get("strategy_id")
                    
                    if command == "ACTIVATE_STRATEGY":
                        if strategy_manager.activate_strategy(strategy_id):
                            logger.info(f"✅ Strategy activated via remote command: {strategy_id}")
                            # Broadcast new status
                            await push({
                                "type": "strategy_status",
                                "data": strategy_manager.get_strategy_status()
                            })
                            
                    elif command == "DEACTIVATE_STRATEGY":
                        if strategy_manager.deactivate_strategy(strategy_id):
                            logger.info(f"⛔ Strategy deactivated via remote command: {strategy_id}")
                            # Broadcast new status
                            await push({
                                "type": "strategy_status",
                                "data": strategy_manager.get_strategy_status()
                            })
                            
                    elif command == "GET_STRATEGY_STATUS":
                        await push({
                            "type": "strategy_status",
                            "data": strategy_manager.get_strategy_status()
                        })

                elif cmd_type == "strategy_command":
                    command = data.get("command")
                    strategy_id = data.get("strategy_id")
                    
                    if command == "ACTIVATE_STRATEGY":
                        if strategy_manager.activate_strategy(strategy_id):
                            logger.info(f"✅ Strategy activated: {strategy_id}")
                            await push({"type": "strategy_status", "data": strategy_manager.get_strategy_status()})
                            
                    elif command == "DEACTIVATE_STRATEGY":
                        if strategy_manager.deactivate_strategy(strategy_id):
                            logger.info(f"⛔ Strategy deactivated: {strategy_id}")
                            await push({"type": "strategy_status", "data": strategy_manager.get_strategy_status()})
                            
                    elif command == "GET_STRATEGY_STATUS":
                        await push({"type": "strategy_status", "data": strategy_manager.get_strategy_status()})

                elif cmd_type == "trade_command":
                    command = data.get("command")
                    if command == "PLACE_ORDER":
                        order_data = data.get("data", {})
                        
                        # Normalize symbol format (EURUSD -> EUR/USD)
                        raw_symbol = order_data.get("symbol", "")
                        if "/" not in raw_symbol and len(raw_symbol) == 6:
                            # Convert EURUSD to EUR/USD
                            normalized_symbol = f"{raw_symbol[:3]}/{raw_symbol[3:]}"
                        else:
                            normalized_symbol = raw_symbol
                        
                        logger.info(f"📝 Received remote order from frontend:")
                        logger.info(f"   Symbol: {raw_symbol} → {normalized_symbol}")
                        logger.info(f"   Action: {order_data.get('action')}")
                        logger.info(f"   Quantity: {order_data.get('quantity')}")
                        logger.info(f"   Order Type: {order_data.get('order_type', 'MKT')}")
                        
                        if execution_engine:
                            # Run in background to not block WS loop
                            asyncio.create_task(execution_engine.execute_order(
                                symbol=normalized_symbol,  # Use normalized symbol
                                action=order_data.get("action"),
                                quantity=order_data.get("quantity"),
                                order_type=order_data.get("order_type", "MKT"),
                                strategy_id="MANUAL"
                            ))
                            logger.info(f"✅ Order submitted to execution engine")
                        else:
                            logger.error("❌ Execution engine not available for remote order")

                    elif command == "CLOSE_POSITION":
                        order_data = data.get("data", {})
                        raw_symbol = order_data.get("symbol", "")
                        quantity = order_data.get("quantity", 0)
                        current_side = order_data.get("side", "LONG")  # Current position side
                        
                        # Normalize symbol
                        if "/" not in raw_symbol and len(raw_symbol) == 6:
                            normalized_symbol = f"{raw_symbol[:3]}/{raw_symbol[3:]}"
                        else:
                            normalized_symbol = raw_symbol
                        
                        # Close = opposite action
                        close_action = "SELL" if current_side == "LONG" else "BUY"
                        
                        logger.info(f"🔴 Closing position: {normalized_symbol} | Side: {current_side} → {close_action} | Qty: {quantity}")
                        
                        if execution_engine:
                            asyncio.create_task(execution_engine.execute_order(
                                symbol=normalized_symbol,
                                action=close_action,
                                quantity=abs(int(quantity)),
                                order_type="MKT",
                                strategy_id="MANUAL_CLOSE"
                            ))
                            logger.info(f"✅ Close order submitted")
                        else:
                            logger.error("❌ Execution engine not available")

                elif cmd_type == "data_command":
                    command = data.get("command")
                    if command == "GET_TRADE_HISTORY":
                        history = get_trade_history()
                        await push({"type": "trade_history", "data": history})

                elif cmd_type == "risk_command":
                    command = data.get("command")
                    if command == "GET_RISK_LIMITS":
                        await push({
                            "type": "risk_limits",
                            "data": risk_manager.get_risk_limits()
                        })
                        logger.info("🛡️ Sent risk limits to frontend.")
                    elif command == "UPDATE_RISK_LIMITS":
                        new_limits = data.get("data", {})
                        if risk_manager.update_risk_limits(new_limits):
                            logger.info("✅ Risk limits updated successfully.")
                            await push({
                                "type": "risk_limits",
                                "data": risk_manager.get_risk_limits()
                            })

                elif cmd_type == "backtest_command":
                    command = data.get("command")
                    if command == "RUN_BACKTEST":
                        payload = data.get("data", {})
                        strategy_id = payload.get("strategyId", "apex")
                        start_date = payload.get("startDate", "2024-01-01")
                        end_date = payload.get("endDate", "2024-12-01")
                        initial_capital = float(payload.get('initialCapital', 100000))
                        symbols = payload.get("symbols", ["EURUSD"])
                        timeframe = payload.get('timeframe', '1h')
                        sl_stop = float(payload.get('slStop', 0.02))
                        tp_stop = float(payload.get('tpStop', 0.06))
                        fees = float(payload.get('fees', 0.0001))
                        leverage = int(payload.get('leverage', 1))

                        logger.info(f"VectorBT backtest requested for {symbols} from {start_date} to {end_date} with {leverage}x leverage")

                        async def run_vbt_task():
                            try:
                                # Run synchronously wrapped in asyncio to avoid blocking
                                results = await asyncio.to_thread(
                                    vector_bt_engine.run_backtest,
                                    str(strategy_id), start_date, end_date, initial_capital, symbols, timeframe, sl_stop, tp_stop, fees, leverage
                                )
                                await push({
                                    "type": "backtest_result",
                                    "data": results
                                })
                            except Exception as e:
                                logger.error(f"Backtest task failed: {e}")
                                await push({
                                    "type": "backtest_result",
                                    "data": {"error": str(e)}
                                })

                        asyncio.create_task(run_vbt_task())
                        logger.info(f"⏳ Backtest started for strategy {strategy_id}...")

                elif cmd_type == "strategy_code_command":
                    command = data.get("command")
                    strategy_id = data.get("strategy_id", "")
                    
                    # Map strategy IDs to their source file paths
                    import os
                    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    strategy_files = {
                        "apex": os.path.join(base_dir, "ai_core", "strategy_engine", "strategies", "apex_strategy.py"),
                        "riztest": os.path.join(base_dir, "ai_core", "strategy_engine", "strategies", "riztest_strategy.py"),
                    }
                    
                    if command == "GET_STRATEGY_CODE":
                        filepath = strategy_files.get(strategy_id)
                        if filepath and os.path.exists(filepath):
                            with open(filepath, "r") as f:
                                code = f.read()
                            await push({
                                "type": "strategy_code",
                                "data": {
                                    "strategy_id": strategy_id,
                                    "code": code,
                                    "filepath": filepath
                                }
                            })
                            logger.info(f"📄 Sent strategy code for: {strategy_id}")
                        else:
                            await push({
                                "type": "strategy_code",
                                "data": {
                                    "strategy_id": strategy_id,
                                    "code": "",
                                    "error": f"Strategy file not found: {strategy_id}"
                                }
                            })
                    
                    elif command == "UPDATE_STRATEGY_CODE":
                        filepath = strategy_files.get(strategy_id)
                        new_code = data.get("code", "")
                        
                        if not filepath:
                            await push({"type": "strategy_code_update", "data": {"success": False, "error": "Unknown strategy"}})
                            return
                        
                        # Validate Python syntax
                        try:
                            compile(new_code, filepath, "exec")
                        except SyntaxError as se:
                            await push({"type": "strategy_code_update", "data": {
                                "success": False, 
                                "error": f"Syntax error at line {se.lineno}: {se.msg}"
                            }})
                            logger.warning(f"❌ Strategy code syntax error: {se}")
                            return
                        
                        # Backup existing file
                        import shutil
                        backup_path = filepath + ".bak"
                        if os.path.exists(filepath):
                            shutil.copy2(filepath, backup_path)
                        
                        # Write new code
                        with open(filepath, "w") as f:
                            f.write(new_code)
                        
                        # Reload strategy module
                        try:
                            import importlib
                            if strategy_id == "riztest":
                                import ai_core.strategy_engine.strategies.riztest_strategy as mod
                                importlib.reload(mod)
                                strategy_manager.strategies["riztest"] = mod.RizTestStrategy()
                            elif strategy_id == "apex":
                                import ai_core.strategy_engine.strategies.apex_strategy as mod_apex
                                importlib.reload(mod_apex)
                                strategy_manager.strategies["apex"] = mod_apex.ApexStrategy()
                            
                            await push({"type": "strategy_code_update", "data": {"success": True, "message": "Strategy updated and reloaded"}})
                            logger.info(f"✅ Strategy code updated and reloaded: {strategy_id}")
                        except Exception as reload_err:
                            # Restore backup on reload failure
                            if os.path.exists(backup_path):
                                shutil.copy2(backup_path, filepath)
                            await push({"type": "strategy_code_update", "data": {
                                "success": False, 
                                "error": f"Reload failed: {str(reload_err)}. Code reverted."
                            }})
                            logger.error(f"❌ Strategy reload failed: {reload_err}")

            except Exception as e:
                logger.error(f"Error handling remote command: {e}")

        # Register the handler & start WebSocket connection to Node Gateway eagerly
        from . import ws_push
        ws_push.register_command_handler(handle_remote_command)
        logger.info("Starting WebSocket connection to Node Gateway...")
        await start_connection()
        logger.info("WebSocket connection task started")
        
        # Initialize Execution Engine
        logger.info("Initializing Execution Engine...")
        try:
            from ai_core.execution.execution_engine import ExecutionEngine
            from ai_core.risk_manager.risk_manager import RiskManager
            from ai_core.strategy_engine.broker.ibkr_async_service import IBKRAsyncService
            from ai_core.execution.execution_config import EXECUTION_MODE, ExecutionMode
            
            risk_manager = RiskManager()
            
            # Determine port based on execution mode
            # 7496 = Live Trading, 7497 = Paper Trading
            primary_port = 7496 if EXECUTION_MODE == ExecutionMode.LIVE_TRADING else 7497
            fallback_port = 7497 if primary_port == 7496 else None
            
            # Initialize IBKR broker service
            logger.info(f"Connecting to IBKR broker on port {primary_port} ({EXECUTION_MODE.value})...")
            ibkr_broker = IBKRAsyncService(host="127.0.0.1", port=primary_port, client_id=997)
            
            try:
                await ibkr_broker.connect()
            except Exception as e:
                if fallback_port:
                    logger.warning(f"Failed to connect to primary port {primary_port}: {e}")
                    logger.info(f"Attempting fallback to port {fallback_port} (Paper/Gateway)...")
                    ibkr_broker = IBKRAsyncService(host="127.0.0.1", port=fallback_port, client_id=997)
                    await ibkr_broker.connect()
                else:
                    raise
            
            # Initialize execution engine with broker
            execution_engine = ExecutionEngine(
                broker_service=ibkr_broker,  # Now with real IBKR broker
                risk_manager=risk_manager
            )
            
            logger.info(f"Execution Engine: {'ENABLED' if execution_engine else 'DISABLED'}")
            logger.info(f"Execution Mode: {execution_engine.execution_mode.value}")
            logger.info(f"Broker Status: {await ibkr_broker.health()}")
        except Exception as e:
            logger.error(f"Failed to initialize execution engine: {e}", exc_info=True)
            execution_engine = None
        
        signal_router = SignalRouter(
            ws_broadcaster=push,
            execution_engine=execution_engine
        )
        
        logger.info("Starting market data subscriptions...")
        await tick_stream.start()
        
        logger.info("=" * 80)
        logger.info("Streaming service started successfully. Beginning data collection...")
        
        # Push initial connection status and strategy status
        logger.info("Pushing initial connection_status to frontend...")
        await push({
            "type": "connection_status",
            "data": {"ibkr_connected": True}
        })
        logger.info("Pushing initial strategy_status to frontend...")
        await push({
            "type": "strategy_status",
            "data": strategy_manager.get_strategy_status()
        })
        logger.info("✅ Initial status pushed to frontend")
        
        logger.info(f"Subscribed symbols: {list(tick_stream.subscribed.keys())}")
        logger.info(f"Tick collection interval: 1.0 seconds (~1 ticks/second)")
        logger.info("=" * 80)
        
        # ---- Candle bucket tracking to avoid re-processing ----
        last_m1_bucket_riztest = None
        last_m5_bucket_apex = None
        last_m15_processed_apex = None
        last_4h_bucket_smc = None
        last_1h_bucket_smc = None
        last_5m_bucket_smc = None
        last_llm_call_time: float = 0.0   # epoch seconds of last LLM call
        LLM_CALL_INTERVAL = 60            # minimum seconds between LLM calls
        
        while not shutdown_flag:
            iteration += 1
            try:
                # Get tick data
                ticks = tick_stream.get_ticks()
                
                # Periodically push risk assessment (e.g. every 10 seconds)
                if iteration % 10 == 0:
                    try:
                        portfolio_risk = risk_manager.assess_portfolio_risk()
                        await push({"type": "risk_assessment", "data": portfolio_risk})
                    except Exception as e:
                        logger.error(f"Error assessing portfolio risk: {e}")
                        
                if not ticks:
                    logger.warning("No tick data received in this iteration")
                    await asyncio.sleep(1.0)
                    continue
                
                # Process each symbol
                for sym, tick in ticks.items():
                    try:
                        # Update candles (will skip if price is invalid)
                        candles = candle_engine.update(tick)
                        micro = compute_microstructure(tick)

                        # Get latest candles for all timeframes (Fixing bug where all_candles was used before definition)
                        all_candles = {}
                        if sym in candles:
                            for tf in ["1m", "5m", "15m", "1h", "4h"]:
                                if tf in candles[sym]:
                                    candle_buckets = candles[sym][tf]
                                    if candle_buckets:
                                        latest_bucket = max(candle_buckets.keys())
                                        all_candles[tf] = candle_buckets[latest_bucket]

                        # Process Apex Strategy (EURUSD Multi-Timeframe)
                        # This strategy requires M5 and M15 candle updates
                        signals = []
                        
                        if sym == "EURUSD" and sym in candles:
                            # Get Apex strategy
                            apex_strategy = None
                            if "apex" in strategy_manager.active_strategies:
                                apex_strategy = strategy_manager.strategies.get("apex")
                                
                            if apex_strategy:
                                # Update M15 candle if available (only on NEW candle)
                                if "15m" in candles[sym]:
                                    m15_candles = candles[sym]["15m"]
                                    if m15_candles:
                                        latest_m15_bucket = max(m15_candles.keys())
                                        if latest_m15_bucket != last_m15_processed_apex:
                                            last_m15_processed_apex = latest_m15_bucket
                                            m15_candle = m15_candles[latest_m15_bucket]
                                            apex_strategy.update_m15_candle(
                                                m15_candle['open'],
                                                m15_candle['high'],
                                                m15_candle['low'],
                                                m15_candle['close']
                                            )
                                            logger.info(f"📊 Apex: New M15 candle processed (bucket={latest_m15_bucket})")
                                
                                # Update M5 candle and check for signals (only on NEW candle)
                                if "5m" in candles[sym]:
                                    m5_candles = candles[sym]["5m"]
                                    if m5_candles:
                                        latest_m5_bucket = max(m5_candles.keys())
                                        if latest_m5_bucket != last_m5_bucket_apex:
                                            last_m5_bucket_apex = latest_m5_bucket
                                            m5_candle = m5_candles[latest_m5_bucket]
                                            strategy_signal = apex_strategy.update_m5_candle(
                                                m5_candle['open'],
                                                m5_candle['high'],
                                                m5_candle['low'],
                                                m5_candle['close']
                                            )
                                            if strategy_signal:
                                                signals.append(strategy_signal)
                                                logger.info(f"📊 Apex: Signal generated on M5 candle!")
                            
                            # Process RizTest Strategy (only on NEW M1 candle)
                            riztest_strategy = None
                            if "riztest" in strategy_manager.active_strategies:
                                riztest_strategy = strategy_manager.strategies.get("riztest")

                            if riztest_strategy and sym == "EURUSD" and sym in candles:
                                if "1m" in candles[sym]:
                                    m1_candles = candles[sym]["1m"]
                                    if m1_candles:
                                        latest_m1_bucket = max(m1_candles.keys())
                                        if latest_m1_bucket != last_m1_bucket_riztest:
                                            last_m1_bucket_riztest = latest_m1_bucket
                                            m1_candle = m1_candles[latest_m1_bucket]
                                            test_signal = riztest_strategy.update_m1_candle(
                                                m1_candle['open'],
                                                m1_candle['high'],
                                                m1_candle['low'],
                                                m1_candle['close']
                                            )
                                            if test_signal:
                                                signals.append(test_signal)
                                                logger.info(f"🧪 RizTest: Signal generated on NEW M1 candle (bucket={latest_m1_bucket})")

                            # Process SMC Strategy (4H, 1H, 5M)
                            smc_strategy = None
                            if "smc" in strategy_manager.active_strategies:
                                smc_strategy = strategy_manager.strategies.get("smc")
                                
                            if smc_strategy and sym == "EURUSD" and sym in candles:
                                # Update 4H candle
                                if "4h" in candles[sym]:
                                    h4_candles = candles[sym]["4h"]
                                    if h4_candles:
                                        latest_4h_bucket = max(h4_candles.keys())
                                        if latest_4h_bucket != last_4h_bucket_smc:
                                            last_4h_bucket_smc = latest_4h_bucket
                                            h4_candle = h4_candles[latest_4h_bucket]
                                            smc_strategy.update_4h_candle(
                                                h4_candle['open'], h4_candle['high'],
                                                h4_candle['low'], h4_candle['close']
                                            )
                                            logger.info(f"📊 SMC: New 4H candle processed (bucket={latest_4h_bucket})")
                                            
                                # Update 1H candle
                                if "1h" in candles[sym]:
                                    h1_candles = candles[sym]["1h"]
                                    if h1_candles:
                                        latest_1h_bucket = max(h1_candles.keys())
                                        if latest_1h_bucket != last_1h_bucket_smc:
                                            last_1h_bucket_smc = latest_1h_bucket
                                            h1_candle = h1_candles[latest_1h_bucket]
                                            smc_strategy.update_1h_candle(
                                                h1_candle['open'], h1_candle['high'],
                                                h1_candle['low'], h1_candle['close']
                                            )
                                            logger.info(f"📊 SMC: New 1H candle processed (bucket={latest_1h_bucket})")
                                            
                                # Update 5M candle and generate signals
                                if "5m" in candles[sym]:
                                    m5_candles = candles[sym]["5m"]
                                    if m5_candles:
                                        latest_5m_bucket = max(m5_candles.keys())
                                        if latest_5m_bucket != last_5m_bucket_smc:
                                            last_5m_bucket_smc = latest_5m_bucket
                                            m5_candle = m5_candles[latest_5m_bucket]
                                            smc_signal = smc_strategy.update_5m_candle(
                                                m5_candle['open'], m5_candle['high'],
                                                m5_candle['low'], m5_candle['close']
                                            )
                                            if smc_signal:
                                                signals.append(smc_signal)
                                                logger.info(f"🚀 SMC: Signal generated on M5 candle! {smc_signal['action']}")

                            # Process ML Strategy
                            ml_strategy = None
                            if "ml" in strategy_manager.active_strategies:
                                ml_strategy = strategy_manager.strategies.get("ml")
                            
                            if ml_strategy and sym == "EURUSD":
                                # Build a context dict similar to LLMAgent
                                ml_ctx = {
                                    "symbol": sym,
                                    "candles": dict(all_candles)
                                }
                                # MLStrategy analyze is async
                                ml_signal = await ml_strategy.analyze(ml_ctx)
                                if ml_signal:
                                    signals.append(ml_signal)
                                    logger.info(f"🤖 ML Engine: Signal generated! {ml_signal['action']} ({ml_signal['confidence']:.0%})")
                        
                        # ── Strategy Diagnostics Broadcast ──
                        if sym == "EURUSD":
                            current_session = strategy_manager.session_filter.get_current_session()
                            session_score = strategy_manager.session_filter.get_session_quality_score(current_session)
                            
                            # Get real regime data from M15 candles if available
                            regime_data = {"regime": "RANGING", "adx": 0.0, "atr": 0.0}
                            apex_strat = strategy_manager.strategies.get("apex")
                            if apex_strat and hasattr(apex_strat, 'mtf_engine') and apex_strat.mtf_engine:
                                m15_closes = list(apex_strat.mtf_engine.m15_close)
                                if len(m15_closes) >= 15:
                                    regime_data = strategy_manager.regime_detector.detect_regime(m15_closes)
                                    
                            llm_macro_score = getattr(strategy_manager, "current_macro_score", 15)
                            
                            diag_payload = {
                                "symbol": sym,
                                "session": current_session,
                                "session_score": session_score,
                                "regime": regime_data,
                                "llm_macro_score": llm_macro_score,
                                "indicators": {}
                            }
                            
                            if apex_strat and hasattr(apex_strat, 'get_diagnostics'):
                                diag_payload["indicators"] = apex_strat.get_diagnostics()
                                
                            await push({"type": "strategy_diagnostics", "data": diag_payload})

                        # Broadcast signals if any
                        if signals:
                            logger.info(f"Signals generated for {sym}: {signals}")
                            
                            # LLM Gatekeeper & Trade Scorer task
                            async def evaluate_and_execute(sigs, current_sym, current_tick, current_candles, current_regime, current_session, session_scr, macro_scr):
                                approved_signals = []
                                for sig in sigs:
                                    # Skip scoring for EXIT signals, they must execute regardless of threshold
                                    if sig.get("action") == "EXIT":
                                        approved_signals.append(sig)
                                        continue
                                        
                                    # 1. TRADE QUALITY SCORING (Layer 7)
                                    technical_score = 35 # Base technical score for a valid signal
                                    
                                    scored_trade = strategy_manager.trade_scorer.score_trade(
                                        technical_score=technical_score,
                                        regime_data=current_regime,
                                        session_score=session_scr,
                                        llm_sentiment_score=macro_scr,
                                        action=sig.get("action", "")
                                    )
                                    
                                    sig['trade_score'] = scored_trade['total_score']
                                    sig['score_breakdown'] = scored_trade['breakdown']
                                    sig['reason'] = f"{sig.get('reason', '')} | Score: {scored_trade['total_score']}/100 | {scored_trade['context']}"
                                    
                                    if not scored_trade['passed_threshold']:
                                        logger.warning(f"🛑 Trade Scorer REJECTED {sig['action']} signal for {current_sym}. Score: {scored_trade['total_score']}/100")
                                        await push({"type": "notification", "data": f"Rejected {sig['action']} on {current_sym}: Score {scored_trade['total_score']}/100 is below 80 threshold."})
                                        await push({"type": "rejected_signal", "data": sig})
                                        continue
                                        
                                    logger.info(f"✅ Trade Scorer PASSED {sig['action']} signal for {current_sym}. Score: {scored_trade['total_score']}/100")
                                    
                                    # 2. LLM VETO CHECK
                                    if llm_agent:
                                        logger.info(f"🛡️ LLM Gatekeeper reviewing signal: {sig['action']} {current_sym}")
                                        ctx = {
                                            "symbol": current_sym,
                                            "bid": current_tick["bid"],
                                            "ask": current_tick["ask"],
                                            "spread": current_tick.get("spread", 0),
                                            "candles": current_candles,
                                            "signals": [sig],
                                            "trigger": "VETO_CHECK",
                                            "news": global_news_state.get(current_sym, {}),
                                            "balance": None,
                                            "position_count": 0,
                                        }
                                        
                                        if execution_engine and execution_engine.broker:
                                            try:
                                                _summary = await execution_engine.broker.get_account_summary()
                                                ctx["balance"] = _summary.get("NetLiquidation")
                                                _pos = await execution_engine.broker.get_positions()
                                                ctx["position_count"] = len(_pos) if _pos else 0
                                            except Exception:
                                                pass
                                                
                                        reasoning = await llm_agent.reason(ctx)
                                        # Push AI reasoning to frontend
                                        await push({"type": "ai_reasoning", "data": reasoning})
                                        
                                        sentiment = reasoning.get("sentiment", "NEUTRAL")
                                        action = sig.get("action", "")
                                        
                                        veto = False
                                        # Strict veto: If ML wants to BUY but Sentiment is BEARISH, veto it.
                                        if action in ("BUY", "LONG") and sentiment == "BEARISH":
                                            veto = True
                                        elif action in ("SELL", "SHORT") and sentiment == "BULLISH":
                                            veto = True
                                            
                                        if veto:
                                            logger.warning(f"🛑 LLM Gatekeeper VETOED {action} signal for {current_sym} due to {sentiment} sentiment.")
                                            await push({"type": "notification", "data": f"LLM Vetoed {action} trade on {current_sym}!"})
                                            await push({"type": "rejected_signal", "data": sig})
                                        else:
                                            logger.info(f"✅ LLM Gatekeeper APPROVED {action} signal for {current_sym}.")
                                            approved_signals.append(sig)
                                    else:
                                        approved_signals.append(sig)
                                
                                if approved_signals:
                                    await signal_router.broadcast_signals(approved_signals)
                            
                            # Capture variables and spawn task
                            _c_session = current_session if 'current_session' in locals() else strategy_manager.session_filter.get_current_session()
                            _c_s_score = session_score if 'session_score' in locals() else strategy_manager.session_filter.get_session_quality_score(_c_session)
                            _c_regime = regime_data if 'regime_data' in locals() else {"regime": "RANGING", "adx": 0.0, "atr": 0.0}
                            _c_macro = llm_macro_score if 'llm_macro_score' in locals() else 15
                            
                            asyncio.create_task(evaluate_and_execute(
                                list(signals), sym, dict(tick), dict(all_candles), 
                                _c_regime, _c_session, _c_s_score, _c_macro
                            ))
                        
                        tick_count += 1
                        
                        # Log periodic status (every 100 ticks)
                        if tick_count % 100 == 0:
                            logger.info(f"Processed {tick_count} ticks | Symbol: {sym} | Bid: {tick['bid']} | Ask: {tick['ask']} | Mid: {tick['mid']}")
                        
                        # Get 1m candle for primary display
                        latest_candle = all_candles.get("1m", {})
                        
                        # Normalize message format for frontend
                        # Include type field for Node Gateway routing
                        message = {
                            "type": "tick",
                            "symbol": sym,
                            "tick": {
                                "bid": float(tick["bid"]),
                                "ask": float(tick["ask"]),
                                "mid": float(tick["mid"]),
                                "spread": float(tick.get("spread", tick["ask"] - tick["bid"])),
                                "timestamp": float(tick.get("timestamp", time.time()))
                            },
                            "candle": latest_candle,
                            "candles": all_candles,  # All timeframes
                            "micro": micro
                        }
                        
                        await push(message)

                        # ── LLM Brain Reasoning (non-blocking background task) ──
                        if llm_agent and sym == "EURUSD":
                            now = time.time()
                            trigger = "SIGNAL" if signals else "PERIODIC"
                            
                            # Phase 2: Massive reduction in LLM API calls to prevent 429 Rate Limit.
                            # We only update the LLM reasoning every 15 minutes (900 seconds) 
                            # or if there is a signal AND it has been at least 5 minutes (300 seconds).
                            should_call = (
                                (now - last_llm_call_time) >= 900
                                or (signals and (now - last_llm_call_time) >= 300)
                            )
                            if should_call:
                                last_llm_call_time = now

                                # Capture loop-local values for the closure
                                _sym      = sym
                                _tick     = dict(tick)
                                _candles  = dict(all_candles)
                                _signals  = list(signals)
                                _trigger  = trigger
                                _exec_eng = execution_engine

                                async def _run_llm():
                                    try:
                                        ctx: dict = {
                                            "symbol":         _sym,
                                            "bid":            _tick["bid"],
                                            "ask":            _tick["ask"],
                                            "spread":         _tick.get("spread", 0),
                                            "candles":        _candles,
                                            "signals":        _signals,
                                            "trigger":        _trigger,
                                            "news":           global_news_state.get(_sym, {}),
                                            "balance":        None,
                                            "position_count": 0,
                                        }
                                        if _exec_eng and _exec_eng.broker:
                                            try:
                                                _summary = await _exec_eng.broker.get_account_summary()
                                                ctx["balance"] = _summary.get("NetLiquidation")
                                                _pos = await _exec_eng.broker.get_positions()
                                                ctx["position_count"] = len(_pos) if _pos else 0
                                            except Exception:
                                                pass
                                        reasoning = await llm_agent.reason(ctx)
                                        await push({"type": "ai_reasoning", "data": reasoning})
                                    except Exception as _e:
                                        logger.error(f"LLM background task error: {_e}")

                                asyncio.create_task(_run_llm())

                    except Exception as e:
                        logger.error(f"Error processing tick for {sym}: {e}", exc_info=True)
                
                # Log iteration summary every 50 iterations
                if iteration % 50 == 0:
                    logger.info(f"Iteration #{iteration} | Total ticks processed: {tick_count} | Active symbols: {len(ticks)}")
                    await push({
                        "type": "connection_status",
                        "data": {"ibkr_connected": True}
                    })
                    # Push Strategy Status Periodically to ensure UI stays synced
                    await push({
                        "type": "strategy_status",
                        "data": strategy_manager.get_strategy_status()
                    })

                # Periodic Account Metrics Push (every ~1s, same as main loop)
                try:
                    if execution_engine and execution_engine.broker:
                        summary = await execution_engine.broker.get_account_summary()
                        positions = await execution_engine.broker.get_positions()
                        
                        # Normalize positions for frontend if needed, or send as is
                        # ensuring list format
                        if positions is None: positions = []
                        
                        # IBKR async cache can sometimes be temporarily empty during updates.
                        # Only push if we actually got summary data to prevent UI flickering to 0.
                        if summary and len(summary) > 0:
                            await push({
                                "type": "account_data",
                                "data": {
                                    "summary": summary,
                                    "positions": positions
                                }
                            })
                        
                        # Update position prices for SL/TP monitoring
                        if ticks:
                            market_prices = {}
                            for sym_key, tick_data in ticks.items():
                                # Convert EURUSD -> EUR/USD for position tracker matching
                                norm_sym = f"{sym_key[:3]}/{sym_key[3:]}" if len(sym_key) == 6 and "/" not in sym_key else sym_key
                                market_prices[norm_sym] = float(tick_data.get('mid', 0))
                            if market_prices:
                                execution_engine.update_position_prices(market_prices)
                except Exception as e:
                    logger.error(f"Error pushing account data: {e}")

                # Periodic Trade Sync with Broker (every 30 iterations ~30s)
                if iteration % 30 == 0:
                    try:
                        if execution_engine and execution_engine.broker:
                            await execution_engine.sync_trades_with_broker()
                    except Exception as e:
                        logger.error(f"Error syncing trades: {e}")

                # Periodic Trade History Push (every 10s is enough)
                if iteration % 10 == 0:
                     history = get_trade_history()
                     if history:
                        await push({"type": "trade_history", "data": history})
                
                await asyncio.sleep(1.0)   # ~1 ticks/second
                
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                shutdown_flag = True
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                await asyncio.sleep(1)  # Wait before retrying
        
    except Exception as e:
        logger.critical(f"Fatal error in main execution: {e}", exc_info=True)
        raise
    finally:
        logger.info("=" * 80)
        logger.info("IBKR Streaming Service Shutting Down")
        logger.info(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Total ticks processed: {tick_count}")
        logger.info("=" * 80)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service terminated by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
        sys.exit(1)
