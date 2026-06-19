import numpy as np
from typing import List, Dict

class RegimeDetector:
    def __init__(self, period: int = 14):
        self.period = period
        
    def calculate_atr(self, closes: List[float]) -> float:
        """Calculate proxy ATR using only closing prices."""
        if len(closes) < self.period + 1:
            return 0.0
            
        true_ranges = np.abs(np.diff(closes[-self.period-1:]))
        return float(np.mean(true_ranges))

    def calculate_adx(self, closes: List[float]) -> float:
        """
        Calculate proxy ADX using only closing prices.
        """
        if len(closes) < self.period + 1:
            return 0.0
            
        plus_dm = []
        minus_dm = []
        
        for i in range(1, len(closes)):
            move = closes[i] - closes[i-1]
            if move > 0:
                plus_dm.append(move)
                minus_dm.append(0)
            else:
                plus_dm.append(0)
                minus_dm.append(abs(move))
                
        atr = self.calculate_atr(closes)
        if atr == 0:
            return 0.0
            
        plus_di = 100 * (np.mean(plus_dm[-self.period:]) / atr)
        minus_di = 100 * (np.mean(minus_dm[-self.period:]) / atr)
        
        if plus_di + minus_di == 0:
            return 0.0
            
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        return dx

    def detect_regime(self, closes: List[float]) -> Dict[str, any]:
        """
        Identify the market regime.
        ADX > 25: Trending
        ADX < 25: Ranging
        ATR: Volatility context
        """
        adx = self.calculate_adx(closes)
        atr = self.calculate_atr(closes)
        
        if adx > 25:
            regime = "STRONG_TREND"
        elif adx > 20:
            regime = "WEAK_TREND"
        else:
            regime = "RANGING"
            
        return {
            "regime": regime,
            "adx": adx,
            "atr": atr
        }
