"""
ADX (Average Directional Index) Indicator
Measures trend strength using Wilder's smoothing method.
"""

import numpy as np
from typing import Optional, Tuple


class ADXIndicator:
    """
    Average Directional Index indicator.
    
    ADX measures trend strength on a scale of 0-100:
    - 0-25: Weak or no trend
    - 25-50: Strong trend
    - 50-75: Very strong trend
    - 75-100: Extremely strong trend
    """
    
    def __init__(self, period: int = 14):
        """
        Initialize ADX indicator.
        
        Args:
            period: Lookback period for ADX calculation (default: 14)
        """
        self.period = period
        self.history = []
        
        # State for smoothed values (Wilder's smoothing)
        self.smoothed_tr = None
        self.smoothed_plus_dm = None
        self.smoothed_minus_dm = None
        self.smoothed_dx = None
    
    def update(self, high: float, low: float, close: float) -> Optional[float]:
        """
        Update ADX with new price bar.
        
        Args:
            high: High price of the bar
            low: Low price of the bar
            close: Close price of the bar
            
        Returns:
            ADX value or None if insufficient data
        """
        self.history.append({'high': high, 'low': low, 'close': close})
        
        if len(self.history) < self.period + 1:
            return None
        
        return self._calculate_adx()
    
    def calculate(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> Optional[float]:
        """
        Calculate ADX from arrays of price data.
        
        Args:
            highs: Array of high prices
            lows: Array of low prices
            closes: Array of close prices
            
        Returns:
            Current ADX value or None if insufficient data
        """
        if len(highs) < self.period + 1:
            return None
        
        return self._calculate_adx_from_arrays(highs, lows, closes)
    
    def _calculate_adx(self) -> float:
        """Calculate ADX from stored history."""
        highs = np.array([bar['high'] for bar in self.history])
        lows = np.array([bar['low'] for bar in self.history])
        closes = np.array([bar['close'] for bar in self.history])
        
        return self._calculate_adx_from_arrays(highs, lows, closes)
    
    def _calculate_adx_from_arrays(self, highs: np.ndarray, lows: np.ndarray, 
                                    closes: np.ndarray) -> float:
        """
        Calculate ADX using Wilder's method.
        
        Steps:
        1. Calculate True Range (TR)
        2. Calculate Directional Movement (+DM, -DM)
        3. Smooth TR, +DM, -DM using Wilder's smoothing
        4. Calculate +DI and -DI
        5. Calculate DX
        6. Smooth DX to get ADX
        """
        # Step 1: True Range
        tr = self._calculate_true_range(highs, lows, closes)
        
        # Step 2: Directional Movement
        plus_dm, minus_dm = self._calculate_directional_movement(highs, lows)
        
        # Step 3: Wilder's smoothing
        smoothed_tr = self._wilders_smoothing(tr)
        smoothed_plus_dm = self._wilders_smoothing(plus_dm)
        smoothed_minus_dm = self._wilders_smoothing(minus_dm)
        
        # Step 4: Calculate +DI and -DI
        plus_di = 100 * (smoothed_plus_dm / smoothed_tr) if smoothed_tr > 0 else 0
        minus_di = 100 * (smoothed_minus_dm / smoothed_tr) if smoothed_tr > 0 else 0
        
        # Step 5: Calculate DX
        di_sum = plus_di + minus_di
        if di_sum == 0:
            return 0.0
        
        dx = 100 * abs(plus_di - minus_di) / di_sum
        
        # Step 6: Smooth DX to get ADX (using Wilder's smoothing)
        if self.smoothed_dx is None:
            # First ADX value is average of first 'period' DX values
            self.smoothed_dx = dx
        else:
            # Subsequent values use Wilder's smoothing
            self.smoothed_dx = ((self.smoothed_dx * (self.period - 1)) + dx) / self.period
        
        return float(self.smoothed_dx)
    
    def _calculate_true_range(self, highs: np.ndarray, lows: np.ndarray, 
                               closes: np.ndarray) -> np.ndarray:
        """
        Calculate True Range.
        TR = max(high - low, abs(high - prev_close), abs(low - prev_close))
        """
        tr = np.zeros(len(highs))
        
        for i in range(1, len(highs)):
            hl = highs[i] - lows[i]
            hc = abs(highs[i] - closes[i-1])
            lc = abs(lows[i] - closes[i-1])
            tr[i] = max(hl, hc, lc)
        
        return tr
    
    def _calculate_directional_movement(self, highs: np.ndarray, 
                                       lows: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate +DM and -DM.
        +DM = current_high - previous_high (if positive and > down_move)
        -DM = previous_low - current_low (if positive and > up_move)
        """
        plus_dm = np.zeros(len(highs))
        minus_dm = np.zeros(len(lows))
        
        for i in range(1, len(highs)):
            up_move = highs[i] - highs[i-1]
            down_move = lows[i-1] - lows[i]
            
            if up_move > down_move and up_move > 0:
                plus_dm[i] = up_move
            
            if down_move > up_move and down_move > 0:
                minus_dm[i] = down_move
        
        return plus_dm, minus_dm
    
    def _wilders_smoothing(self, values: np.ndarray) -> float:
        """
        Apply Wilder's smoothing.
        First value: sum of first 'period' values
        Subsequent: (previous_smooth * (period - 1) + current_value) / period
        """
        # Use the most recent 'period' values
        recent_values = values[-self.period:]
        
        if len(recent_values) < self.period:
            return np.sum(recent_values)
        
        # Initial smooth is the sum of first period values
        smooth = np.sum(recent_values)
        
        return smooth / self.period


def calculate_adx(highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, 
                  period: int = 14) -> Optional[float]:
    """
    Convenience function to calculate ADX from price arrays.
    
    Args:
        highs: Array of high prices
        lows: Array of low prices
        closes: Array of close prices
        period: ADX period (default: 14)
        
    Returns:
        ADX value or None if insufficient data
    """
    adx = ADXIndicator(period=period)
    return adx.calculate(highs, lows, closes)
