"""
Unit tests for EUR/USD MTF Risk Management

Tests that risk parameters are correctly applied:
- Stop-loss is exactly 2% from entry
- Take-profit is exactly 6% from entry
- Risk-reward ratio is 1:3
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch
from ai_core.strategy_engine.strategies.apex_strategy import ApexStrategy


class TestApexRisk:
    """Test EUR/USD MTF strategy risk management."""
    
    def setup_method(self):
        """Set up test strategy instance."""
        self.strategy = ApexStrategy()
    
    @patch('ai_core.strategy_engine.core.market_session.MarketSession.is_trading_allowed')
    def test_long_stop_loss_2_percent_below_entry(self, mock_session):
        """Test LONG stop-loss is exactly 2% below entry price."""
        mock_session.return_value = {
            'allowed': True,
            'current_session': 'london',
            'active_sessions': ['london']
        }
        
        # Build M15 bullish bias
        for i in range(50):
            price = 1.0800 + (i * 0.0001)
            self.strategy.update_m15_candle(price, price, price, price)
        
        # Build M5 bullish setup
        for i in range(40):
            price = 1.0850 + (i * 0.0001)
            self.strategy.update_m5_candle(price, price, price, price)
        
        # Get signal
        signal = self.strategy.update_m5_candle(1.0890, 1.0890, 1.0890, 1.0890)
        
        assert signal is not None
        assert signal['signal'] == 'LONG'
        
        entry = signal['metadata']['entry_price']
        sl = signal['metadata']['stop_loss']
        
        # Stop-loss should be exactly 2% below entry
        expected_sl = entry * 0.98
        assert abs(sl - expected_sl) < 0.000001
    
    @patch('ai_core.strategy_engine.core.market_session.MarketSession.is_trading_allowed')
    def test_long_take_profit_6_percent_above_entry(self, mock_session):
        """Test LONG take-profit is exactly 6% above entry price."""
        mock_session.return_value = {
            'allowed': True,
            'current_session': 'new_york',
            'active_sessions': ['new_york']
        }
        
        # Build M15 bullish bias
        for i in range(50):
            price = 1.0800 + (i * 0.0001)
            self.strategy.update_m15_candle(price, price, price, price)
        
        # Build M5 bullish setup
        for i in range(40):
            price = 1.0850 + (i * 0.0001)
            self.strategy.update_m5_candle(price, price, price, price)
        
        # Get signal
        signal = self.strategy.update_m5_candle(1.0890, 1.0890, 1.0890, 1.0890)
        
        entry = signal['metadata']['entry_price']
        tp = signal['metadata']['take_profit']
        
        # Take-profit should be exactly 6% above entry
        expected_tp = entry * 1.06
        assert abs(tp - expected_tp) < 0.000001
    
    @patch('ai_core.strategy_engine.core.market_session.MarketSession.is_trading_allowed')
    def test_short_stop_loss_2_percent_above_entry(self, mock_session):
        """Test SHORT stop-loss is exactly 2% above entry price."""
        mock_session.return_value = {
            'allowed': True,
            'current_session': 'london',
            'active_sessions': ['london']
        }
        
        # Build M15 bearish bias
        for i in range(50):
            price = 1.0900 - (i * 0.0001)
            self.strategy.update_m15_candle(price, price, price, price)
        
        # Build M5 bearish setup
        for i in range(40):
            price = 1.0850 - (i * 0.0001)
            self.strategy.update_m5_candle(price, price, price, price)
        
        # Get signal
        signal = self.strategy.update_m5_candle(1.0810, 1.0810, 1.0810, 1.0810)
        
        assert signal is not None
        assert signal['signal'] == 'SHORT'
        
        entry = signal['metadata']['entry_price']
        sl = signal['metadata']['stop_loss']
        
        # Stop-loss should be exactly 2% above entry
        expected_sl = entry * 1.02
        assert abs(sl - expected_sl) < 0.000001
    
    @patch('ai_core.strategy_engine.core.market_session.MarketSession.is_trading_allowed')
    def test_short_take_profit_6_percent_below_entry(self, mock_session):
        """Test SHORT take-profit is exactly 6% below entry price."""
        mock_session.return_value = {
            'allowed': True,
            'current_session': 'london',
            'active_sessions': ['london']
        }
        
        # Build M15 bearish bias
        for i in range(50):
            price = 1.0900 - (i * 0.0001)
            self.strategy.update_m15_candle(price, price, price, price)
        
        # Build M5 bearish setup
        for i in range(40):
            price = 1.0850 - (i * 0.0001)
            self.strategy.update_m5_candle(price, price, price, price)
        
        # Get signal
        signal = self.strategy.update_m5_candle(1.0810, 1.0810, 1.0810, 1.0810)
        
        entry = signal['metadata']['entry_price']
        tp = signal['metadata']['take_profit']
        
        # Take-profit should be exactly 6% below entry
        expected_tp = entry * 0.94
        assert abs(tp - expected_tp) < 0.000001
    
    @patch('ai_core.strategy_engine.core.market_session.MarketSession.is_trading_allowed')
    def test_risk_reward_ratio_is_1_to_3(self, mock_session):
        """Test that risk-reward ratio is 1:3."""
        mock_session.return_value = {
            'allowed': True,
            'current_session': 'london',
            'active_sessions': ['london']
        }
        
        # Build M15 bullish bias
        for i in range(50):
            self.strategy.update_m15_candle(1.08 + i*0.0001, 1.08 + i*0.0001, 1.08 + i*0.0001, 1.08 + i*0.0001)
        
        # Build M5 bullish setup
        for i in range(40):
            self.strategy.update_m5_candle(1.085 + i*0.0001, 1.085 + i*0.0001, 1.085 + i*0.0001, 1.085 + i*0.0001)
        
        signal = self.strategy.update_m5_candle(1.089, 1.089, 1.089, 1.089)
        
        entry = signal['metadata']['entry_price']
        sl = signal['metadata']['stop_loss']
        tp = signal['metadata']['take_profit']
        
        # Calculate risk and reward
        risk = abs(entry - sl)
        reward = abs(tp - entry)
        
        # Reward should be 3x risk
        ratio = reward / risk
        assert abs(ratio - 3.0) < 0.01  # Allow small floating point error


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
