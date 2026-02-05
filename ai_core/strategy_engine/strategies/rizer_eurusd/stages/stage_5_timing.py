"""
Stage 5: Timing Filter
RSI-based entry timing within established trend.
"""

from typing import Dict, Optional


class TimingFilter:
    """
    Stage 5: Timing Filter
    
    Uses RSI to refine entry timing within the trend.
    
    Scoring:
    - RSI < 30:  +0.5 (oversold - good long timing)
    - RSI < 40:  +0.3 (pullback in uptrend)
    - RSI > 70:  -0.5 (overbought - good short timing)
    - RSI > 60:  -0.3 (pullback in downtrend)
    - Else:       0.0 (neutral timing)
    """
    
    def __init__(self):
        """Initialize timing filter."""
        pass
    
    def evaluate(self, rsi: Optional[float]) -> Dict:
        """
        Evaluate entry timing based on RSI.
        
        Args:
            rsi: RSI(14) value
            
        Returns:
            {
                'timing_score': float,  # [-0.5, +0.5]
                'rsi_value': float,
                'rsi_regime': str
            }
        """
        if rsi is None:
            return {
                'timing_score': 0.0,
                'rsi_value': None,
                'rsi_regime': 'UNKNOWN'
            }
        
        # Score based on RSI levels
        if rsi < 30:
            timing_score = 0.5
            rsi_regime = 'OVERSOLD'
        elif rsi < 40:
            timing_score = 0.3
            rsi_regime = 'PULLBACK_LOW'
        elif rsi > 70:
            timing_score = -0.5
            rsi_regime = 'OVERBOUGHT'
        elif rsi > 60:
            timing_score = -0.3
            rsi_regime = 'PULLBACK_HIGH'
        else:
            timing_score = 0.0
            rsi_regime = 'NEUTRAL'
        
        return {
            'timing_score': timing_score,
            'rsi_value': rsi,
            'rsi_regime': rsi_regime
        }
