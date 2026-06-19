"""
Apex V1 - Multi-Timeframe Trend-Following Strategy

Institutional-style execution model:
- M15 timeframe: Defines directional bias using SMA(50)
- M5 timeframe: Executes trades using SMA(10), SMA(30), RSI(14)
- Session filter: Only trade during London or New York sessions
- Risk management: Fixed 2% SL, 6% TP (1:3 R:R) hello 
"""

import time
from typing import Dict, Optional
from datetime import datetime

from ai_core.strategy_engine.core.multi_timeframe_feature_engine import MultiTimeframeFeatureEngine
from ai_core.strategy_engine.core.market_session import MarketSession


class ApexStrategy:
    """
    Apex V1 - Multi-Timeframe Trend-Following Strategy.
    
    Higher timeframe (M15) defines direction.
    Lower timeframe (M5) defines timing.
    Liquidity (London/NY sessions) determines when.
    """
    
    def __init__(self):
        """Initialize EUR/USD multi-timeframe strategy."""
        self.mtf_engine = MultiTimeframeFeatureEngine()
        
        # Allowed trading sessions (London and New York only)
        self.allowed_sessions = ['london', 'new_york']
        
        # Position tracking
        self.current_position = None  # 'LONG', 'SHORT', or None
        self.entry_price = None
        self.stop_loss = None
        self.take_profit = None
        
        # Risk management parameters
        self.stop_loss_pct = 0.02  # 2%
        self.take_profit_pct = 0.06  # 6%
        
        # Track last M5 crossover state for exit detection
        self.last_m5_sma_10 = None
        self.last_m5_sma_30 = None
    
    def update_m5_candle(self, open_price: float, high: float, low: float, close: float) -> Optional[Dict]:
        """
        Update M5 candle and potentially generate signal.
        
        This is called when a new M5 candle is formed or updated.
        
        Args:
            open_price: M5 candle open
            high: M5 candle high
            low: M5 candle low
            close: M5 candle close
            
        Returns:
            Trading signal dict or None
        """
        # Update M5 features
        m5_features = self.mtf_engine.update_m5_candle(open_price, high, low, close)
        
        # Check if we're in a tradeable session
        session_check = MarketSession.is_trading_allowed(self.allowed_sessions)
        
        if not session_check['allowed']:
            # Outside trading session - no new trades, but check exits
            if self.current_position:
                return self._check_exit_conditions(close, m5_features, "Outside trading session")
            return None
        
        # Check for exit conditions if in position
        if self.current_position:
            exit_signal = self._check_exit_conditions(close, m5_features, session_check['current_session'])
            if exit_signal:
                return exit_signal
        
        # Check for entry conditions if not in position
        if self.current_position is None:
            return self._check_entry_conditions(close, m5_features, session_check['current_session'])
        
        return None
    
    def update_m15_candle(self, open_price: float, high: float, low: float, close: float) -> Dict:
        """
        Update M15 candle and compute M15 bias.
        
        This is called when a new M15 candle is formed or updated.
        
        Args:
            open_price: M15 candle open
            high: M15 candle high
            low: M15 candle low
            close: M15 candle close
            
        Returns:
            M15 features including bias
        """
        return self.mtf_engine.update_m15_candle(open_price, high, low, close)
    
    def _check_entry_conditions(self, price: float, m5_features: Dict, session: str) -> Optional[Dict]:
        """
        Check if entry conditions are met.
        
        Args:
            price: Current M5 close price
            m5_features: M5 features from MTF engine
            session: Current trading session
            
        Returns:
            Entry signal or None
        """
        sma_10 = m5_features.get('sma_10')
        sma_30 = m5_features.get('sma_30')
        rsi_14 = m5_features.get('rsi_14')
        m15_bias = m5_features.get('m15_bias')
        
        # Need all indicators
        if sma_10 is None or sma_30 is None or rsi_14 is None:
            return None
        
        # Need M15 bias established
        if m15_bias == 0:
            return None
        
        # Store for exit detection
        self.last_m5_sma_10 = sma_10
        self.last_m5_sma_30 = sma_30
        
        # LONG ENTRY CONDITIONS
        if (sma_10 > sma_30 and          # Short-term momentum bullish
            m15_bias == +1 and           # Higher timeframe confirms trend
            rsi_14 < 70):                # Avoid overbought
            
            # Enter long
            self.current_position = 'LONG'
            self.entry_price = price
            self.stop_loss = price * (1 - self.stop_loss_pct)  # 2% below
            self.take_profit = price * (1 + self.take_profit_pct)  # 6% above
            
            return {
                'symbol': 'EUR/USD',
                'action': 'LONG',
                'reason': f'LONG: SMA(10)>SMA(30), M15 BULLISH, RSI={rsi_14:.1f} during {session.upper()}',
                'confidence': 0.85,
                'strategy_id': 'APEX',
                'timestamp': int(time.time() * 1000),
                'metadata': {
                    'entry_price': self.entry_price,
                    'stop_loss': self.stop_loss,
                    'take_profit': self.take_profit,
                    'sma_10': sma_10,
                    'sma_30': sma_30,
                    'rsi_14': rsi_14,
                    'm15_bias': 'BULLISH',
                    'session': session
                }
            }
        
        # SHORT ENTRY CONDITIONS
        elif (sma_10 < sma_30 and        # Short-term momentum bearish
              m15_bias == -1 and         # Higher timeframe confirms trend
              rsi_14 > 30):              # Avoid oversold
            
            # Enter short
            self.current_position = 'SHORT'
            self.entry_price = price
            self.stop_loss = price * (1 + self.stop_loss_pct)  # 2% above
            self.take_profit = price * (1 - self.take_profit_pct)  # 6% below
            
            return {
                'symbol': 'EUR/USD',
                'action': 'SHORT',
                'reason': f'SHORT: SMA(10)<SMA(30), M15 BEARISH, RSI={rsi_14:.1f} during {session.upper()}',
                'confidence': 0.85,
                'strategy_id': 'APEX',
                'timestamp': int(time.time() * 1000),
                'metadata': {
                    'entry_price': self.entry_price,
                    'stop_loss': self.stop_loss,
                    'take_profit': self.take_profit,
                    'sma_10': sma_10,
                    'sma_30': sma_30,
                    'rsi_14': rsi_14,
                    'm15_bias': 'BEARISH',
                    'session': session
                }
            }
        
        return None
    
    def _check_exit_conditions(self, price: float, m5_features: Dict, session: str) -> Optional[Dict]:
        """
        Check if exit conditions are met.
        
        Exit triggers:
        1. Opposite SMA crossover on M5
        2. M15 bias changes against position
        3. Hard stop-loss or take-profit hit
        
        Args:
            price: Current M5 close price
            m5_features: M5 features from MTF engine
            session: Current session or reason string
            
        Returns:
            Exit signal or None
        """
        if self.current_position is None:
            return None
        
        sma_10 = m5_features.get('sma_10')
        sma_30 = m5_features.get('sma_30')
        m15_bias = m5_features.get('m15_bias')
        
        exit_reason = None
        
        # Check hard stops first (highest priority)
        if self.current_position == 'LONG':
            if price <= self.stop_loss:
                exit_reason = 'Stop-loss hit (2%)'
            elif price >= self.take_profit:
                exit_reason = 'Take-profit hit (6%)'
            elif m15_bias == -1:
                exit_reason = 'M15 bias changed to BEARISH'
            elif sma_10 is not None and sma_30 is not None and sma_10 < sma_30:
                # Check for crossover
                if self.last_m5_sma_10 is not None and self.last_m5_sma_30 is not None:
                    if self.last_m5_sma_10 >= self.last_m5_sma_30:
                        exit_reason = 'SMA(10) crossed below SMA(30)'
        
        elif self.current_position == 'SHORT':
            if price >= self.stop_loss:
                exit_reason = 'Stop-loss hit (2%)'
            elif price <= self.take_profit:
                exit_reason = 'Take-profit hit (6%)'
            elif m15_bias == +1:
                exit_reason = 'M15 bias changed to BULLISH'
            elif sma_10 is not None and sma_30 is not None and sma_10 > sma_30:
                # Check for crossover
                if self.last_m5_sma_10 is not None and self.last_m5_sma_30 is not None:
                    if self.last_m5_sma_10 <= self.last_m5_sma_30:
                        exit_reason = 'SMA(10) crossed above SMA(30)'
        
        # Update last SMA values for next check
        if sma_10 is not None and sma_30 is not None:
            self.last_m5_sma_10 = sma_10
            self.last_m5_sma_30 = sma_30
        
        if exit_reason:
            # Generate exit signal
            pnl_pct = ((price - self.entry_price) / self.entry_price) * 100
            if self.current_position == 'SHORT':
                pnl_pct = -pnl_pct
            
            exit_signal = {
                'symbol': 'EUR/USD',
                'action': 'EXIT',
                'position': self.current_position,
                'reason': f'EXIT {self.current_position}: {exit_reason}',
                'confidence': 1.0,
                'strategy_id': 'APEX',
                'timestamp': int(time.time() * 1000),
                'metadata': {
                    'exit_price': price,
                    'entry_price': self.entry_price,
                    'pnl_pct': round(pnl_pct, 2),
                    'exit_reason': exit_reason,
                    'session': session
                }
            }
            
            # Reset position
            self.current_position = None
            self.entry_price = None
            self.stop_loss = None
            self.take_profit = None
            self.last_m5_sma_10 = None
            self.last_m5_sma_30 = None
            
            return exit_signal
        
        return None
        
    def get_diagnostics(self) -> dict:
        """
        Get live diagnostic features for frontend visualization.
        """
        features = {
            'sma_10': None,
            'sma_30': None,
            'rsi_14': None,
            'm15_bias': self.mtf_engine.m15_bias if self.mtf_engine else 0,
            'position': self.current_position,
            'm5_closes': list(self.mtf_engine.m5_close) if self.mtf_engine else []
        }
        
        # Calculate current indicators based on latest data
        if self.mtf_engine and len(self.mtf_engine.m5_close) > 0:
            import numpy as np
            closes = list(self.mtf_engine.m5_close)
            if len(closes) >= 10:
                features['sma_10'] = float(np.mean(closes[-10:]))
            if len(closes) >= 30:
                features['sma_30'] = float(np.mean(closes[-30:]))
            if len(closes) >= 15:
                features['rsi_14'] = self.mtf_engine._compute_rsi(np.array(closes), 14)
                
        return features
    
    def generate_signal(self, symbol: str, price: float, features: dict) -> Optional[Dict]:
        """
        Legacy interface for compatibility with StrategyManager.
        
        This method is called by the current StrategyManager which expects
        this interface. However, this strategy is designed to work with
        candle-level updates (update_m5_candle, update_m15_candle).
        
        For now, this returns None. The strategy should be integrated
        at the candle engine level in ibkr_streaming/run.py.
        
        Args:
            symbol: Trading symbol
            price: Current price
            features: Feature dict
            
        Returns:
            None (strategy works at candle level, not tick level)
        """
        # This strategy operates at candle level, not tick level
        # Integration point should be in ibkr_streaming/run.py
        # where M5 and M15 candles are available
        return None
