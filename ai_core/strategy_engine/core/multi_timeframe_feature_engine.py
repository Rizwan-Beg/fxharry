"""
Multi-Timeframe Feature Engine for EUR/USD Strategy

Manages separate M5 and M15 candle histories and computes timeframe-specific indicators:
- M15: SMA(50) for directional bias
- M5: SMA(10), SMA(30), RSI(14) for execution timing
"""

import numpy as np
from collections import deque
from typing import Dict, Optional


class MultiTimeframeFeatureEngine:
    """
    Feature engine for multi-timeframe strategy.
    
    Tracks M5 and M15 candle data separately and computes:
    - M15 bias: SMA(50)
    - M5 execution: SMA(10), SMA(30), RSI(14)
    """
    
    def __init__(self, max_m5_candles: int = 200, max_m15_candles: int = 100):
        """
        Initialize multi-timeframe feature engine.
        
        Args:
            max_m5_candles: Maximum M5 candles to store
            max_m15_candles: Maximum M15 candles to store
        """
        # M5 candle storage (OHLC)
        self.m5_open = deque(maxlen=max_m5_candles)
        self.m5_high = deque(maxlen=max_m5_candles)
        self.m5_low = deque(maxlen=max_m5_candles)
        self.m5_close = deque(maxlen=max_m5_candles)
        
        # M15 candle storage (OHLC)
        self.m15_open = deque(maxlen=max_m15_candles)
        self.m15_high = deque(maxlen=max_m15_candles)
        self.m15_low = deque(maxlen=max_m15_candles)
        self.m15_close = deque(maxlen=max_m15_candles)
        
        # Current M15 bias (forward-filled to M5)
        self.m15_bias = 0  # +1 = bullish, -1 = bearish, 0 = neutral/insufficient data
    
    def update_m5_candle(self, open_price: float, high: float, low: float, close: float) -> Dict:
        """
        Update M5 candle data and compute M5 indicators.
        
        Args:
            open_price: Open price of M5 candle
            high: High price of M5 candle
            low: Low price of M5 candle
            close: Close price of M5 candle
            
        Returns:
            Dict with M5 indicators: sma_10, sma_30, rsi_14, m15_bias
        """
        # Store M5 candle
        self.m5_open.append(open_price)
        self.m5_high.append(high)
        self.m5_low.append(low)
        self.m5_close.append(close)
        
        # Compute M5 indicators
        features = {}
        
        # SMA(10)
        if len(self.m5_close) >= 10:
            features['sma_10'] = float(np.mean(list(self.m5_close)[-10:]))
        else:
            features['sma_10'] = None
        
        # SMA(30)
        if len(self.m5_close) >= 30:
            features['sma_30'] = float(np.mean(list(self.m5_close)[-30:]))
        else:
            features['sma_30'] = None
        
        # RSI(14)
        if len(self.m5_close) >= 15:
            features['rsi_14'] = self._compute_rsi(np.array(self.m5_close), 14)
        else:
            features['rsi_14'] = None
        
        # Include M15 bias (forward-filled)
        features['m15_bias'] = self.m15_bias
        
        return features
    
    def update_m15_candle(self, open_price: float, high: float, low: float, close: float) -> Dict:
        """
        Update M15 candle data and compute M15 bias.
        
        Args:
            open_price: Open price of M15 candle
            high: High price of M15 candle
            low: Low price of M15 candle
            close: Close price of M15 candle
            
        Returns:
            Dict with M15 indicators: sma_50, bias
        """
        # Store M15 candle
        self.m15_open.append(open_price)
        self.m15_high.append(high)
        self.m15_low.append(low)
        self.m15_close.append(close)
        
        # Compute M15 SMA(50)
        features = {}
        
        if len(self.m15_close) >= 50:
            sma_50 = float(np.mean(list(self.m15_close)[-50:]))
            features['sma_50'] = sma_50
            
            # Determine bias
            if close > sma_50:
                self.m15_bias = +1  # Bullish
                features['bias'] = 'BULLISH'
            elif close < sma_50:
                self.m15_bias = -1  # Bearish
                features['bias'] = 'BEARISH'
            else:
                self.m15_bias = 0  # Neutral
                features['bias'] = 'NEUTRAL'
        else:
            features['sma_50'] = None
            features['bias'] = 'INSUFFICIENT_DATA'
            self.m15_bias = 0
        
        return features
    
    def _compute_rsi(self, prices: np.ndarray, period: int) -> Optional[float]:
        """
        Compute RSI indicator.
        
        Args:
            prices: Array of prices
            period: RSI period
            
        Returns:
            RSI value or None if insufficient data
        """
        if len(prices) < period + 1:
            return None
        
        diffs = np.diff(prices)
        gains = np.maximum(diffs, 0)
        losses = np.maximum(-diffs, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi)
    
    def get_m15_bias(self) -> int:
        """
        Get current M15 bias.
        
        Returns:
            +1 for bullish, -1 for bearish, 0 for neutral/insufficient data
        """
        return self.m15_bias
    
    def reset(self):
        """Reset all stored candle data and bias."""
        self.m5_open.clear()
        self.m5_high.clear()
        self.m5_low.clear()
        self.m5_close.clear()
        
        self.m15_open.clear()
        self.m15_high.clear()
        self.m15_low.clear()
        self.m15_close.clear()
        
        self.m15_bias = 0
