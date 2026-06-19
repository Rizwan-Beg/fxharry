import vectorbt as vbt
import yfinance as yf
import pandas as pd
import numpy as np
from ai_core.core.logger import get_logger

logger = get_logger(__name__)

class VectorBTEngine:
    """High-performance vectorised backtesting engine using VectorBT and yfinance"""
    
    def __init__(self):
        pass

    def run_backtest(
        self, 
        strategy_id: str, 
        start_date: str, 
        end_date: str, 
        initial_capital: float, 
        symbols: list, 
        timeframe: str = "1h", 
        sl_stop: float = 0.02, 
        tp_stop: float = 0.06, 
        fees: float = 0.0001,
        leverage: int = 1
    ):
        logger.info(f"🚀 Starting VectorBT Backtest for Strategy {strategy_id} on {symbols} ({timeframe}) from {start_date} to {end_date}")
        
        try:
            # VectorBT YFData.download sometimes fails with multiple symbols if one doesn't exist.
            # Convert to Yahoo Finance ticker format for Forex
            yf_symbols = []
            for s in symbols:
                if len(s) == 6 and '/' not in s:  # EURUSD
                    yf_symbols.append(f"{s}=X")
                else:
                    yf_symbols.append(s)
            
            import pandas_ta as ta
            
            if not yf_symbols:
                yf_symbols = ["EURUSD=X"]
                
            # Fetch real historical data
            data = vbt.YFData.download(yf_symbols, start=start_date, end=end_date, interval=timeframe)
            close = data.get('Close')
            high = data.get('High')
            low = data.get('Low')
            
            if close.empty:
                return {"error": f"No data found for symbols {symbols} from {start_date} to {end_date} at {timeframe} interval. Please adjust your date range."}
                
            # Phase 7: Calculate Institutional Architecture Filters
            
            # 1. Regime Filter (ADX > 25 = Strong Trend)
            # pandas_ta returns a DataFrame with ADX_14, DMP_14, DMN_14
            adx_df = ta.adx(high, low, close, length=14)
            if adx_df is not None and not adx_df.empty:
                adx_col = [c for c in adx_df.columns if c.startswith('ADX')][0]
                adx = adx_df[adx_col]
                # Pad to match close index if needed
                adx = adx.reindex(close.index).fillna(0)
                is_trending = adx > 25
            else:
                is_trending = pd.Series(True, index=close.index) # Fallback if error
                
            # 2. Session Filter (London-NY Overlap: 13:00 - 17:00 UTC)
            is_overlap_session = (close.index.hour >= 13) & (close.index.hour < 17)
            
            # Master Trade Quality Filter (Only allow trades when trending AND during high liquidity)
            master_filter = is_trending & is_overlap_session
            
            # Map strategy logic to vectorized signals
            # 1. Apex Strategy Approximation (Trend Following)
            if str(strategy_id) in ["1", "apex"]:
                sma10 = vbt.MA.run(close, 10)
                sma30 = vbt.MA.run(close, 30)
                rsi = vbt.RSI.run(close, 14)
                # Buy when fast SMA crosses above slow SMA and RSI > 50
                entries = sma10.ma_crossed_above(sma30) & (rsi.rsi > 50) & master_filter
                exits = sma10.ma_crossed_below(sma30)
                
            # 2. SMC Strategy Approximation (Smart Money Concepts)
            elif str(strategy_id) in ["3", "smc"]:
                ema200 = vbt.MA.run(close, 200, ewm=True)
                ema50 = vbt.MA.run(close, 50, ewm=True)
                ema9 = vbt.MA.run(close, 9, ewm=True)
                rsi = vbt.RSI.run(close, 14)
                
                # Strong macro uptrend
                uptrend = (close > ema50.ma) & (ema50.ma > ema200.ma)
                
                # Pullback condition (RSI dipped below 40 recently)
                discount_zone = rsi.rsi < 40
                recent_discount = discount_zone.rolling(10).sum() > 0
                
                # Momentum shift back to the upside
                momentum_shift = close.vbt.crossed_above(ema9.ma)
                
                entries = uptrend & recent_discount & momentum_shift & master_filter
                
                # Exit when trend momentum dies or overbought
                exits = (rsi.rsi > 70) | close.vbt.crossed_below(ema50.ma)

            # 3. ML Strategy Approximation (Mean Reversion)
            elif str(strategy_id) in ["2", "mean_reversion", "ml_strategy", "ml"]:
                rsi = vbt.RSI.run(close, 14)
                entries = rsi.rsi_crossed_below(30) & master_filter
                exits = rsi.rsi_crossed_above(70)

            # 4. RizTest Strategy (High Frequency)
            elif str(strategy_id) in ["riztest", "4"]:
                # strictly alternate entry and exit to ensure trades are closed
                entries = pd.Series(False, index=close.index)
                entries.iloc[::2] = True  # Enter on 0, 2, 4...
                entries = entries & master_filter
                
                exits = pd.Series(False, index=close.index)
                exits.iloc[1::2] = True   # Exit on 1, 3, 5...
                
            else:
                # Default Scalper (Fast EMA cross)
                ema5 = vbt.MA.run(close, 5, ewm=True)
                ema15 = vbt.MA.run(close, 15, ewm=True)
                entries = ema5.ma_crossed_above(ema15)
                exits = ema5.ma_crossed_below(ema15)

            # Build Portfolio
            # Simulate leverage by multiplying available cash by leverage
            # The metrics will be scaled back relative to the original capital
            trading_capital = initial_capital * leverage
            
            # Using 1 pip slippage for realistic broker simulation
            slippage_rate = 0.0001
            portfolio = vbt.Portfolio.from_signals(
                close, entries, exits, 
                init_cash=trading_capital,
                fees=fees,
                slippage=slippage_rate,
                sl_stop=sl_stop,
                tp_stop=tp_stop
            )
            
            stats = portfolio.stats()
            
            # Equity curve calculation moved to after portfolio.value() extraction
            
            # Extract metrics safely (handling NaN values from VectorBT stats)
            def safe_float(val, default=0.0):
                try:
                    f = float(val)
                    return f if not pd.isna(f) else default
                except:
                    return default

            total_trades = int(safe_float(stats.get('Total Closed Trades', 0)))
            win_rate = safe_float(stats.get('Win Rate [%]', 0)) / 100
            winning_trades = int(total_trades * win_rate)
            losing_trades = total_trades - winning_trades
            
            # Handle Pandas Timedelta
            avg_duration_td = stats.get('Avg Winning Trade Duration', None)
            duration_hours = 0
            if isinstance(avg_duration_td, pd.Timedelta):
                duration_hours = avg_duration_td.total_seconds() / 3600
                
            # Broker Cost Analysis
            records = portfolio.orders.records_readable
            total_fees_paid = float(records['Fees'].sum()) if not records.empty else 0.0
            
            # Slippage cost = Size * Price * slippage_rate
            total_slippage_cost = float((records['Size'] * records['Price'] * slippage_rate).sum()) if not records.empty else 0.0
            
            avg_commission_per_trade = (total_fees_paid / total_trades) if total_trades > 0 else 0.0
            
            net_profit_amount = portfolio.total_profit()
            if isinstance(net_profit_amount, pd.Series):
                net_profit_amount = net_profit_amount.sum()
            
            gross_profit_amount = net_profit_amount + total_fees_paid + total_slippage_cost
            
            # Calculate Percentage Impacts relative to actual user capital
            gross_return_pct = (gross_profit_amount / initial_capital) * 100
            commission_impact_pct = (total_fees_paid / initial_capital) * 100
            slippage_impact_pct = (total_slippage_cost / initial_capital) * 100
            net_return_pct = (net_profit_amount / initial_capital) * 100
            
            # Divide equity curve minus initial_capital by leverage, or just show actual PnL scaled
            # The easiest way to show actual un-leveraged user capital curve is:
            # User Equity = initial_capital + (Portfolio Value - trading_capital)
            equity_series = initial_capital + (portfolio.value() - trading_capital)
            if isinstance(equity_series, pd.DataFrame):
                equity_series = equity_series.sum(axis=1) # Sum multiple symbols
                
            equity_curve = []
            for ts, val in equity_series.items():
                equity_curve.append({
                    'timestamp': ts.isoformat(),
                    'equity': float(val)
                })
            
            results = {
                "initial_capital": initial_capital,
                "final_capital": initial_capital + net_profit_amount,
                "total_return": net_profit_amount / initial_capital if initial_capital > 0 else 0,
                "leverage_used": leverage,
                "total_trades": total_trades,
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "win_rate": safe_float(stats.get('Win Rate [%]', 0)) / 100,
                "profit_factor": safe_float(stats.get('Profit Factor', 0)),
                "sharpe_ratio": safe_float(stats.get('Sharpe Ratio', 0)),
                "max_drawdown": safe_float(stats.get('Max Drawdown [%]', 0)) / 100,
                "avg_trade_duration": duration_hours,
                "equity_curve": equity_curve,
                
                # New Cost Analysis Metrics
                "total_fees_paid": total_fees_paid,
                "avg_commission_per_trade": avg_commission_per_trade,
                "total_slippage_cost": total_slippage_cost,
                "gross_profit": gross_profit_amount,
                "net_profit": net_profit_amount,
                "gross_return_pct": gross_return_pct,
                "commission_impact_pct": commission_impact_pct,
                "slippage_impact_pct": slippage_impact_pct,
                "net_return_pct": net_return_pct,
            }
            
            logger.info(f"✅ Backtest completed successfully. Final Capital: ${results['final_capital']:.2f}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error during VectorBT backtest: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
