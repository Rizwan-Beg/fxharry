"""
Unit tests for EUR/USD Multi-Timeframe Entry Signals

Tests the entry logic:
- LONG: SMA(10) > SMA(30), M15 bias = +1, in session, RSI < 70
- SHORT: SMA(10) < SMA(30), M15 bias = -1, in session, RSI > 30
- No signal when conditions not met
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock
from ai_core.strategy_engine.strategies.apex_strategy import ApexStrategy


class TestApexEntry:
    """Test EUR/USD MTF strategy entry conditions."""
    
    def setup_method(self):
        """Set up test strategy instance."""
        self.strategy = ApexStrategy()
    
    @patch('ai_core.strategy_engine.core.market_session.MarketSession.is_trading_allowed')
    def test_long_entry_all_conditions_met(self, mock_session):
        """Test LONG entry when all conditions are met."""
        # Mock London session active
        mock_session.return_value = {
            'allowed': True,
            'current_session': 'london',
            'active_sessions': ['london']
        }
        
        # Build up M15 bias first (50 candles with uptrend)
        for i in range(50):
            price = 1.0800 + (i * 0.0001)  # Uptrend
            self.strategy.update_m15_candle(price, price, price, price)
        
        # Verify M15 bias is BULLISH
        assert self.strategy.mtf_engine.get_m15_bias() == +1
        
        # Build up M5 history with oscillating pattern to keep RSI moderate
        # This creates upward bias but with pullbacks to avoid overbought
        base = 1.0850
        for i in range(30):
            # Oscillate: 2 steps up, 1 step down
            if i % 3 == 2:
                price = base - 0.00002
            else:
                price = base + 0.00003
            base = price
            self.strategy.update_m5_candle(price, price, price, price)
        
        # Now create clear bullish momentum for final signal
        # Add some sideways/pullback movement first to lower RSI
        for i in range(5):
            price = base + (0.00001 if i % 2 == 0 else -0.00001)
            self.strategy.update_m5_candle(price, price, price, price)
        
        # Then add bullish candles  
        for i in range(8):
            price = base + (i * 0.00005)
            self.strategy.update_m5_candle(price, price, price, price)
        
        # Final M5 update should trigger LONG signal
        signal = self.strategy.update_m5_candle(price + 0.00005, price + 0.00005, price + 0.00005, price + 0.00005)
        
        assert signal is not None, "Signal should be generated when all conditions met"
        assert signal['signal'] == 'LONG'
        assert signal['symbol'] == 'EUR/USD'
        assert signal['strategy_id'] == 'APEX'
        assert 'entry_price' in signal['metadata']
        assert 'stop_loss' in signal['metadata']
        assert 'take_profit' in signal['metadata']
        
        # Verify stop-loss is 2% below entry
        entry = signal['metadata']['entry_price']
        sl = signal['metadata']['stop_loss']
        assert abs((entry - sl) / entry - 0.02) < 0.0001
        
        # Verify take-profit is 6% above entry
        tp = signal['metadata']['take_profit']
        assert abs((tp - entry) / entry - 0.06) < 0.0001
    
    @patch('ai_core.strategy_engine.core.market_session.MarketSession.is_trading_allowed')
    def test_short_entry_all_conditions_met(self, mock_session):
        """Test SHORT entry when all conditions are met."""
        # Mock New York session active
        mock_session.return_value = {
            'allowed': True,
            'current_session': 'new_york',
            'active_sessions': ['new_york']
        }
        
        # Build up M15 bias first (50 candles with downtrend)
        for i in range(50):
            price = 1.0900 - (i * 0.0001)  # Downtrend
            self.strategy.update_m15_candle(price, price, price, price)
        
        # Verify M15 bias is BEARISH
        assert self.strategy.mtf_engine.get_m15_bias() == -1
        
        # Build up M5 history with oscillating pattern
        base = 1.0850
        for i in range(30):
            # Oscillate: 2 steps down, 1 step up
            if i % 3 == 2:
                price = base + 0.00002
            else:
                price = base - 0.00003
            base = price
            self.strategy.update_m5_candle(price, price, price, price)
        
        # Add sideways movement to moderate RSI
        for i in range(5):
            price = base + (0.00001 if i % 2 == 0 else -0.00001)
            self.strategy.update_m5_candle(price, price, price, price)
        
        # Then add bearish candles
        for i in range(8):
            price = base - (i * 0.00005)
            self.strategy.update_m5_candle(price, price, price, price)
        
        # Final M5 update should trigger SHORT signal
        signal = self.strategy.update_m5_candle(price - 0.00005, price - 0.00005, price - 0.00005, price - 0.00005)
        
        assert signal is not None, "Signal should be generated when all conditions met"
        assert signal['signal'] == 'SHORT'
        assert signal['symbol'] == 'EUR/USD'
        assert signal['strategy_id'] == 'APEX'
        
        # Verify stop-loss is 2% above entry
        entry = signal['metadata']['entry_price']
        sl = signal['metadata']['stop_loss']
        assert abs((sl - entry) / entry - 0.02) < 0.0001
        
        # Verify take-profit is 6% below entry
        tp = signal['metadata']['take_profit']
        assert abs((entry - tp) / entry - 0.06) < 0.0001
    
    @patch('ai_core.strategy_engine.core.market_session.MarketSession.is_trading_allowed')
    def test_no_signal_outside_session(self, mock_session):
        """Test no signal when outside London/NY sessions."""
        # Mock session not active
        mock_session.return_value = {
            'allowed': False,
            'current_session': None,
            'active_sessions': ['tokyo']
        }
        
        # Build M15 bullish bias
        for i in range(50):
            price = 1.0800 + (i * 0.0001)
            self.strategy.update_m15_candle(price, price, price, price)
        
        # Build M5 bullish setup
        for i in range(40):
            price = 1.0850 + (i * 0.0001)
            self.strategy.update_m5_candle(price, price, price, price)
        
        # Should return None (no signal outside session)
        signal = self.strategy.update_m5_candle(1.0890, 1.0890, 1.0890, 1.0890)
        assert signal is None
    
    @patch('ai_core.strategy_engine.core.market_session.MarketSession.is_trading_allowed')
    def test_no_signal_when_bias_conflicts(self, mock_session):
        """Test no signal when M5 direction conflicts with M15 bias."""
        mock_session.return_value = {
            'allowed': True,
            'current_session': 'london',
            'active_sessions': ['london']
        }
        
        # Build M15 BULLISH bias
        for i in range(50):
            price = 1.0800 + (i * 0.0001)
            self.strategy.update_m15_candle(price, price, price, price)
        
        assert self.strategy.mtf_engine.get_m15_bias() == +1
        
        # Build M5 BEARISH setup (conflicts with M15)
        for i in range(40):
            price = 1.0850 - (i * 0.0001)  # Downtrend
            self.strategy.update_m5_candle(price, price, price, price)
        
        # Should return None (M5 bearish but M15 bullish)
        signal = self.strategy.update_m5_candle(1.0810, 1.0810, 1.0810, 1.0810)
        assert signal is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
