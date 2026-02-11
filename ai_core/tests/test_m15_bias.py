"""
Unit tests for M15 Bias Calculation

Tests that M15 SMA(50) correctly determines directional bias:
- Bullish bias (+1) when M15 close > M15 SMA(50)
- Bearish bias (-1) when M15 close < M15 SMA(50)
- Bias is forward-filled to M5 timeframe
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from ai_core.strategy_engine.core.multi_timeframe_feature_engine import MultiTimeframeFeatureEngine


class TestM15Bias:
    """Test M15 bias calculation and forward-filling."""
    
    def setup_method(self):
        """Set up test MTF engine instance."""
        self.mtf_engine = MultiTimeframeFeatureEngine()
    
    def test_bullish_bias_when_close_above_sma50(self):
        """Test bullish bias when M15 close > SMA(50)."""
        # Build 50 candles with uptrend, then one above SMA
        for i in range(50):
            price = 1.0800 + (i * 0.0001)
            self.mtf_engine.update_m15_candle(price, price, price, price)
        
        # SMA(50) should be around 1.08245
        # Add candle above SMA
        result = self.mtf_engine.update_m15_candle(1.0850, 1.0850, 1.0850, 1.0850)
        
        assert result['bias'] == 'BULLISH'
        assert self.mtf_engine.get_m15_bias() == +1
        assert result['sma_50'] is not None
        assert result['sma_50'] < 1.0850
    
    def test_bearish_bias_when_close_below_sma50(self):
        """Test bearish bias when M15 close < SMA(50)."""
        # Build 50 candles with downtrend, then one below SMA
        for i in range(50):
            price = 1.0900 - (i * 0.0001)
            self.mtf_engine.update_m15_candle(price, price, price, price)
        
        # Add candle below SMA
        result = self.mtf_engine.update_m15_candle(1.0850, 1.0850, 1.0850, 1.0850)
        
        assert result['bias'] == 'BEARISH'
        assert self.mtf_engine.get_m15_bias() == -1
        assert result['sma_50'] is not None
        assert result['sma_50'] > 1.0850
    
    def test_insufficient_data_before_50_candles(self):
        """Test bias is neutral when insufficient M15 candles."""
        # Add only 49 candles
        for i in range(49):
            price = 1.0800 + (i * 0.0001)
            result = self.mtf_engine.update_m15_candle(price, price, price, price)
        
        assert result['bias'] == 'INSUFFICIENT_DATA'
        assert self.mtf_engine.get_m15_bias() == 0
        assert result['sma_50'] is None
    
    def test_bias_forward_filled_to_m5(self):
        """Test that M15 bias is forward-filled to M5 features."""
        # Build M15 bullish bias
        for i in range(50):
            price = 1.0800 + (i * 0.0001)
            self.mtf_engine.update_m15_candle(price, price, price, price)
        
        # Verify M15 bias is bullish
        assert self.mtf_engine.get_m15_bias() == +1
        
        # Update M5 candle and check bias is included
        m5_result = self.mtf_engine.update_m5_candle(1.0850, 1.0850, 1.0850, 1.0850)
        
        assert m5_result['m15_bias'] == +1
    
    def test_bias_changes_with_price_movement(self):
        """Test bias changes when price crosses SMA(50)."""
        # Build uptrend (bullish bias)
        for i in range(50):
            price = 1.0800 + (i * 0.0001)
            self.mtf_engine.update_m15_candle(price, price, price, price)
        
        # Add more bullish candles
        for i in range(5):
            price = 1.0850 + (i * 0.0001)
            result = self.mtf_engine.update_m15_candle(price, price, price, price)
        
        assert result['bias'] == 'BULLISH'
        
        # Now add strong downward candles to cross below SMA
        for i in range(10):
            price = 1.0820 - (i * 0.0002)
            result = self.mtf_engine.update_m15_candle(price, price, price, price)
        
        # Bias should now be bearish
        assert result['bias'] == 'BEARISH'
        assert self.mtf_engine.get_m15_bias() == -1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
