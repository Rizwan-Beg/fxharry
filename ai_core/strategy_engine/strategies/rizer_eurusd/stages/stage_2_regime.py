"""
Stage 2: Market Regime Filter
ADX-based trend strength classification.
"""

from typing import Dict, Optional


class RegimeFilter:
    """
    Stage 2: Market Regime Filter
    
    Uses ADX to classify market regime and assign regime score.
    
    Scoring:
    - ADX < 15:  0.0 (choppy/ranging)
    - ADX 15-20: 0.3 (weak trend forming)
    - ADX 20-30: 0.6 (moderate trend)
    - ADX > 30:  0.9 (strong trend)
    """
    
    def __init__(self):
        """Initialize regime filter."""
        pass
    
    def evaluate(self, adx: Optional[float]) -> Dict:
        """
        Evaluate market regime based on ADX.
        
        Args:
            adx: ADX(14) value
            
        Returns:
            {
                'regime_score': float,  # [0.0, 1.0]
                'adx_value': float,
                'regime_type': str
            }
        """
        if adx is None:
            return {
                'regime_score': 0.0,
                'adx_value': None,
                'regime_type': 'UNKNOWN'
            }
        
        # Classify regime
        if adx < 15:
            regime_score = 0.0
            regime_type = 'CHOPPY'
        elif adx < 20:
            regime_score = 0.3
            regime_type = 'WEAK_TREND'
        elif adx < 30:
            regime_score = 0.6
            regime_type = 'MODERATE_TREND'
        else:
            regime_score = 0.9
            regime_type = 'STRONG_TREND'
        
        return {
            'regime_score': regime_score,
            'adx_value': adx,
            'regime_type': regime_type
        }
