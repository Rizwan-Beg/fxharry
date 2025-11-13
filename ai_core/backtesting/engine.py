import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from ai_core.core.logger import get_logger
from ai_core.database.models import Strategy, BacktestResult, Trade
from ai_core.database.database import SessionLocal
from ..strategy_engine.market_data.market_data_service import MarketDataService
from ..strategy_engine.rule_based import StrategyManager

import asyncio

logger = get_logger(__name__)

class BacktestingEngine:
    """Backtesting engine for trading strategies"""
    
    def __init__(self):
        self.market_data_service = MarketDataService()
        self.strategy_manager = StrategyManager()
        
    async def run_backtest(self, strategy_id: int, start_date: datetime, 
                          end_date: datetime, initial_capital: float = 100000,
                          symbols: List[str] = None) -> Dict[str, Any]:
        """Run backtest for a strategy"""
        
        if not symbols:
            symbols = ['EURUSD', 'GBPUSD', 'XAUUSD']
        
        logger.info(f"Starting backtest for strategy {strategy_id} from {start_date} to {end_date}")
        
        try:
            # Load strategy
            strategy_instance = await self.strategy_manager.load_strategy(strategy_id)
            if not strategy_instance:
                return {'error': 'Failed to load strategy'}
            
            # Get historical data for all symbols
            historical_data = {}
            for symbol in symbols:
                data = await self.market_data_service.get_historical_data(
                    symbol, '1H', start_date, end_date
                )
                historical_data[symbol] = pd.DataFrame(data)
                historical_data[symbol]['timestamp'] = pd.to_datetime(historical_data[symbol]['timestamp'])
                historical_data[symbol].set_index('timestamp', inplace=True)
            
            # Initialize backtest state
            backtest_state = {
                'capital': initial_capital,
                'positions': {},  # symbol -> position info
                'trades': [],
                'equity_curve': [],
                'daily_returns': [],
                'drawdowns': []
            }
            
            # Get all unique timestamps and sort them
            all_timestamps = set()
            for symbol_data in historical_data.values():
                all_timestamps.update(symbol_data.index)
            
            timestamps = sorted(list(all_timestamps))
            
            # Run simulation through each timestamp
            for i, timestamp in enumerate(timestamps):
                # Prepare market data for this timestamp
                current_market_data = {}
                for symbol, data in historical_data.items():
                    if timestamp in data.index:
                        row = data.loc[timestamp]
                        current_market_data[symbol] = {
                            'symbol': symbol,
                            'timestamp': timestamp.isoformat(),
                            'open': row['open'],
                            'high': row['high'],
                            'low': row['low'],
                            'close': row['close'],
                            'volume': row['volume'],
                            'bid': row['close'] - 0.0002,
                            'ask': row['close'] + 0.0002,
                            'last': row['close']
                        }
                
                if not current_market_data:
                    continue
                
                # Update position values
                self._update_positions(backtest_state, current_market_data)
                
                # Get strategy signal
                try:
                    signal = strategy_instance.predict(current_market_data)
                    if signal and signal.get('confidence', 0) > 0.5:  # Confidence threshold
                        await self._process_signal(backtest_state, signal, current_market_data, timestamp)
                except Exception as e:
                    logger.warning(f"Strategy prediction error at {timestamp}: {e}")
                
                # Record equity
                current_equity = self._calculate_equity(backtest_state, current_market_data)
                backtest_state['equity_curve'].append({
                    'timestamp': timestamp.isoformat(),
                    'equity': current_equity,
                    'cash': backtest_state['capital'],
                    'positions_value': current_equity - backtest_state['capital']
                })
                
                # Calculate daily return if we have previous equity
                if len(backtest_state['equity_curve']) > 1:
                    prev_equity = backtest_state['equity_curve'][-2]['equity']
                    daily_return = (current_equity - prev_equity) / prev_equity
                    backtest_state['daily_returns'].append(daily_return)
                
                # Progress logging
                if i % 100 == 0:
                    logger.info(f"Backtest progress: {i}/{len(timestamps)} ({i/len(timestamps)*100:.1f}%)")
            
            # Calculate final metrics
            results = self._calculate_backtest_metrics(backtest_state, initial_capital)
            
            # Save results to database
            await self._save_backtest_results(strategy_id, start_date, end_date, 
                                            initial_capital, backtest_state, results)
            
            logger.info(f"Backtest completed. Final equity: ${results['final_capital']:,.2f}")
            
            return results
            
        except Exception as e:
            logger.error(f"Backtest error: {e}")
            return {'error': str(e)}
    
    async def _process_signal(self, backtest_state: Dict, signal: Dict, 
                             market_data: Dict, timestamp: datetime):
        """Process trading signal during backtest"""
        symbol = signal.get('symbol', 'EURUSD')
        signal_type = signal.get('signal', 'HOLD')
        confidence = signal.get('confidence', 0)
        
        if signal_type == 'HOLD' or confidence < 0.5:
            return
        
        if symbol not in market_data:
            return
        
        current_price = market_data[symbol]['close']
        
        # Position sizing (risk 1% of capital per trade)
        risk_per_trade = backtest_state['capital'] * 0.01
        stop_loss_distance = current_price * 0.002  # 0.2% stop loss
        position_size = risk_per_trade / stop_loss_distance
        
        # Limit position size to available capital
        max_position_value = backtest_state['capital'] * 0.1  # Max 10% per position
        max_position_size = max_position_value / current_price
        position_size = min(position_size, max_position_size)
        
        if position_size * current_price > backtest_state['capital'] * 0.1:
            return  # Not enough capital
        
        # Check if we already have a position in this symbol
        if symbol in backtest_state['positions']:
            # Close existing position first
            await self._close_position(backtest_state, symbol, current_price, timestamp)
        
        # Open new position
        if signal_type in ['BUY', 'SELL']:
            trade = {
                'id': len(backtest_state['trades']) + 1,
                'symbol': symbol,
                'action': signal_type,
                'quantity': position_size,
                'entry_price': current_price,
                'entry_time': timestamp,
                'stop_loss': current_price - stop_loss_distance if signal_type == 'BUY' 
                            else current_price + stop_loss_distance,
                'take_profit': current_price + (stop_loss_distance * 2) if signal_type == 'BUY'
                              else current_price - (stop_loss_distance * 2),
                'status': 'OPEN',
                'confidence': confidence
            }
            
            backtest_state['positions'][symbol] = trade
            backtest_state['trades'].append(trade)
            
            # Update capital (assuming no commission for simplicity)
            position_value = position_size * current_price
            backtest_state['capital'] -= position_value if signal_type == 'BUY' else -position_value
    
    async def _close_position(self, backtest_state: Dict, symbol: str, 
                             current_price: float, timestamp: datetime):
        """Close an open position"""
        if symbol not in backtest_state['positions']:
            return
        
        position = backtest_state['positions'][symbol]
        
        # Calculate P&L
        if position['action'] == 'BUY':
            pnl = (current_price - position['entry_price']) * position['quantity']
        else:  # SELL
            pnl = (position['entry_price'] - current_price) * position['quantity']
        
        # Update trade record
        position['exit_price'] = current_price
        position['exit_time'] = timestamp
        position['pnl'] = pnl
        position['status'] = 'CLOSED'
        
        # Update capital
        if position['action'] == 'BUY':
            backtest_state['capital'] += position['quantity'] * current_price
        else:  # SELL
            backtest_state['capital'] += position['quantity'] * (2 * position['entry_price'] - current_price)
        
        # Remove from open positions
        del backtest_state['positions'][symbol]
    
    def _update_positions(self, backtest_state: Dict, market_data: Dict):
        """Update open positions with current market prices"""
        positions_to_close = []
        
        for symbol, position in backtest_state['positions'].items():
            if symbol not in market_data:
                continue
            
            current_price = market_data[symbol]['close']
            
            # Check stop loss and take profit
            if position['action'] == 'BUY':
                if current_price <= position['stop_loss'] or current_price >= position['take_profit']:
                    positions_to_close.append((symbol, current_price))
            else:  # SELL
                if current_price >= position['stop_loss'] or current_price <= position['take_profit']:
                    positions_to_close.append((symbol, current_price))
        
        # Close positions that hit stop loss or take profit
        for symbol, price in positions_to_close:
            asyncio.create_task(self._close_position(backtest_state, symbol, price, 
                                                   datetime.now()))  # Timestamp will be updated
    
    def _calculate_equity(self, backtest_state: Dict, market_data: Dict) -> float:
        """Calculate current portfolio equity"""
        equity = backtest_state['capital']
        
        for symbol, position in backtest_state['positions'].items():
            if symbol in market_data:
                current_price = market_data[symbol]['close']
                if position['action'] == 'BUY':
                    position_value = position['quantity'] * current_price
                    equity += position_value
                else:  # SELL
                    # For short positions, add the difference
                    unrealized_pnl = (position['entry_price'] - current_price) * position['quantity']
                    equity += unrealized_pnl
        
        return equity
    
    def _calculate_backtest_metrics(self, backtest_state: Dict, initial_capital: float) -> Dict[str, Any]:
        """Calculate backtest performance metrics"""
        equity_curve = backtest_state['equity_curve']
        trades = [t for t in backtest_state['trades'] if t['status'] == 'CLOSED']
        
        if not equity_curve:
            return {'error': 'No equity data'}
        
        final_equity = equity_curve[-1]['equity']
        total_return = (final_equity - initial_capital) / initial_capital
        
        # Trade statistics
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.get('pnl', 0) > 0])
        losing_trades = total_trades - winning_trades
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # P&L statistics
        total_pnl = sum(t.get('pnl', 0) for t in trades)
        winning_pnl = sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0)
        losing_pnl = sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0)
        
        profit_factor = abs(winning_pnl / losing_pnl) if losing_pnl != 0 else float('inf')
        
        # Drawdown calculation
        equity_values = [point['equity'] for point in equity_curve]
        peak = equity_values[0]
        max_drawdown = 0
        
        for equity in equity_values:
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        # Sharpe ratio (simplified)
        if backtest_state['daily_returns']:
            daily_returns = np.array(backtest_state['daily_returns'])
            excess_return = np.mean(daily_returns)
            volatility = np.std(daily_returns)
            sharpe_ratio = (excess_return / volatility) * np.sqrt(252) if volatility > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Average trade duration
        trade_durations = []
        for trade in trades:
            if trade.get('entry_time') and trade.get('exit_time'):
                if isinstance(trade['entry_time'], str):
                    entry_time = datetime.fromisoformat(trade['entry_time'])
                    exit_time = datetime.fromisoformat(trade['exit_time'])
                else:
                    entry_time = trade['entry_time']
                    exit_time = trade['exit_time']
                
                duration = (exit_time - entry_time).total_seconds() / 3600  # in hours
                trade_durations.append(duration)
        
        avg_trade_duration = np.mean(trade_durations) if trade_durations else 0
        
        return {
            'initial_capital': initial_capital,
            'final_capital': final_equity,
            'total_return': total_return,
            'total_pnl': total_pnl,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'avg_trade_duration': avg_trade_duration,
            'equity_curve': equity_curve,
            'trades': trades
        }
    
    async def _save_backtest_results(self, strategy_id: int, start_date: datetime,
                                   end_date: datetime, initial_capital: float,
                                   backtest_state: Dict, results: Dict):
        """Save backtest results to database"""
        db = SessionLocal()
        try:
            backtest_result = BacktestResult(
                strategy_id=strategy_id,
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_capital,
                final_capital=results['final_capital'],
                total_return=results['total_return'],
                total_trades=results['total_trades'],
                winning_trades=results['winning_trades'],
                losing_trades=results['losing_trades'],
                win_rate=results['win_rate'],
                profit_factor=results['profit_factor'],
                sharpe_ratio=results['sharpe_ratio'],
                max_drawdown=results['max_drawdown'],
                avg_trade_duration=results['avg_trade_duration'],
                trade_history=results['trades'],
                equity_curve=results['equity_curve']
            )
            
            db.add(backtest_result)
            db.commit()
            logger.info(f"Backtest results saved for strategy {strategy_id}")
            
        except Exception as e:
            logger.error(f"Error saving backtest results: {e}")
        finally:
            db.close()
    
    async def get_backtest_results(self, strategy_id: int) -> List[Dict[str, Any]]:
        """Get historical backtest results for a strategy"""
        db = SessionLocal()
        try:
            results = db.query(BacktestResult).filter(
                BacktestResult.strategy_id == strategy_id
            ).order_by(BacktestResult.created_at.desc()).all()
            
            return [
                {
                    'id': result.id,
                    'start_date': result.start_date.isoformat(),
                    'end_date': result.end_date.isoformat(),
                    'initial_capital': result.initial_capital,
                    'final_capital': result.final_capital,
                    'total_return': result.total_return,
                    'total_trades': result.total_trades,
                    'win_rate': result.win_rate,
                    'sharpe_ratio': result.sharpe_ratio,
                    'max_drawdown': result.max_drawdown,
                    'created_at': result.created_at.isoformat()
                }
                for result in results
            ]
            
        finally:
            db.close()