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
from .tick_stream import TickStreamer
from .candle_engine import CandleEngine
from .microstructure import compute_microstructure
from .ws_push import push
from .logger import get_logger
from ai_core.strategy_engine.strategy_manager import StrategyManager
from ai_core.strategy_engine.signal_router import SignalRouter

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

        # Initialize Strategy Manager
        logger.info("Initializing Strategy Engine...")
        strategy_manager = StrategyManager()
        
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
                        logger.info(f"📝 Received remote order: {order_data}")
                        if execution_engine:
                            # Run in background to not block WS loop
                            asyncio.create_task(execution_engine.execute_order(
                                symbol=order_data.get("symbol"),
                                action=order_data.get("action"),
                                quantity=order_data.get("quantity"),
                                order_type=order_data.get("order_type", "MKT"),
                                strategy_id="MANUAL"
                            ))
                        else:
                            logger.error("Execution engine not available for remote order")

                elif cmd_type == "data_command":
                    command = data.get("command")
                    if command == "GET_TRADE_HISTORY":
                        history = get_trade_history()
                        await push({"type": "trade_history", "data": history})

            except Exception as e:
                logger.error(f"Error handling remote command: {e}")

        # Register the handler
        from . import ws_push
        ws_push.register_command_handler(handle_remote_command)
        
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
        await push({
            "type": "connection_status",
            "data": {"ibkr_connected": True}
        })
        await push({
            "type": "strategy_status",
            "data": strategy_manager.get_strategy_status()
        })
        
        logger.info(f"Subscribed symbols: {list(tick_stream.subscribed.keys())}")
        logger.info(f"Tick collection interval: 1.0 seconds (~1 ticks/second)")
        logger.info("=" * 80)
        
        while not shutdown_flag:
            iteration += 1
            try:
                # Get tick data
                ticks = tick_stream.get_ticks()
                
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

                        # Process Apex Strategy (EURUSD Multi-Timeframe)
                        # This strategy requires M5 and M15 candle updates
                        signals = []
                        
                        if sym == "EURUSD" and sym in candles:
                            # Get Apex strategy
                            apex_strategy = None
                            if "apex" in strategy_manager.active_strategies:
                                apex_strategy = strategy_manager.strategies.get("apex")
                                
                            if apex_strategy:
                                # Update M15 candle if available
                                if "15m" in candles[sym]:
                                    m15_candles = candles[sym]["15m"]
                                    if m15_candles:
                                        latest_m15_bucket = max(m15_candles.keys())
                                        m15_candle = m15_candles[latest_m15_bucket]
                                        apex_strategy.update_m15_candle(
                                            m15_candle['open'],
                                            m15_candle['high'],
                                            m15_candle['low'],
                                            m15_candle['close']
                                        )
                                
                                # Update M5 candle and check for signals
                                if "5m" in candles[sym]:
                                    m5_candles = candles[sym]["5m"]
                                    if m5_candles:
                                        latest_m5_bucket = max(m5_candles.keys())
                                        m5_candle = m5_candles[latest_m5_bucket]
                                        strategy_signal = apex_strategy.update_m5_candle(
                                            m5_candle['open'],
                                            m5_candle['high'],
                                            m5_candle['low'],
                                            m5_candle['close']
                                            )
                                        if strategy_signal:
                                            signals.append(strategy_signal)
                            
                            # Process RizTest Strategy
                            # Check if active
                            riztest_strategy = None
                            if "riztest" in strategy_manager.active_strategies:
                                riztest_strategy = strategy_manager.strategies.get("riztest")

                            if riztest_strategy and sym == "EURUSD" and sym in candles:
                                if "1m" in candles[sym]:
                                    m1_candles = candles[sym]["1m"]
                                    if m1_candles:
                                        latest_m1_bucket = max(m1_candles.keys())
                                        m1_candle = m1_candles[latest_m1_bucket]
                                        test_signal = riztest_strategy.update_m1_candle(
                                            m1_candle['open'],
                                            m1_candle['high'],
                                            m1_candle['low'],
                                            m1_candle['close']
                                        )
                                        if test_signal:
                                            signals.append(test_signal)
                        
                        # Broadcast signals if any
                        if signals:
                            logger.info(f"Signals generated for {sym}: {signals}")
                            await signal_router.broadcast_signals(signals)
                        
                        tick_count += 1
                        
                        # Log periodic status (every 100 ticks)
                        if tick_count % 100 == 0:
                            logger.info(f"Processed {tick_count} ticks | Symbol: {sym} | Bid: {tick['bid']} | Ask: {tick['ask']} | Mid: {tick['mid']}")
                        
                        # Get latest candles for all timeframes
                        all_candles = {}
                        if sym in candles:
                            for tf in ["1m", "5m", "15m", "1h", "4h"]:
                                if tf in candles[sym]:
                                    candle_buckets = candles[sym][tf]
                                    if candle_buckets:
                                        latest_bucket = max(candle_buckets.keys())
                                        all_candles[tf] = candle_buckets[latest_bucket]
                        
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
                        
                        await push({
                            "type": "account_data",
                            "data": {
                                "summary": summary,
                                "positions": positions
                            }
                        })
                except Exception as e:
                    logger.error(f"Error pushing account data: {e}")

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
