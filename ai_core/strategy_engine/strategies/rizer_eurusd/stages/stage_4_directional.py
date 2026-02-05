"""
Stage 4: Directional Bias
EMA structure analysis for trend direction and strength.
"""

from typing import Dict, Optional


class DirectionalBias:
    """
    Stage 4: Directional Bias
    
    Analyzes EMA(20, 50, 100) structure to determine trend direction.
    
    Rules:
    - LONG: EMA20 > EMA50 > EMA100
    - SHORT: EMA20 < EMA50 < EMA100
    - NEUTRAL: Otherwise
    
    Trend score based on EMA separation.
    """
    
    def __init__(self):
        """Initialize directional bias filter."""
        pass
    
    def evaluate(self, ema_20: Optional[float], ema_50: Optional[float], 
                 ema_100: Optional[float]) -> Dict:
        """
        Evaluate directional bias from EMA structure.
        
        Args:
            ema_20: 20-period EMA
            ema_50: 50-period EMA
            ema_100: 100-period EMA
            
        Returns:
            {
                'directional_bias': str,  # 'LONG', 'SHORT', 'NEUTRAL'
                'trend_score': float,     # [-1.0, +1.0]
                'ema_alignment': bool
            }
        """
        if ema_20 is None or ema_50 is None or ema_100 is None:
            return {
                'directional_bias': 'NEUTRAL',
                'trend_score': 0.0,
                'ema_alignment': False
            }
        
        # Check for LONG alignment
        if ema_20 > ema_50 > ema_100:
            directional_bias = 'LONG'
            ema_alignment = True
            
            # Calculate separation strength
            # Use percentage separation between fastest and slowest EMA
            separation = ((ema_20 - ema_100) / ema_100) * 100 if ema_100 > 0 else 0
            
            # Scale to [0, 1.0]
            # Typical 5-min separation: 0.05% to 0.5%
            # Scale: 0.1% = 0.2, 0.5% = 1.0
            trend_score = min(1.0, max(0.0, separation * 200))
            
        # Check for SHORT alignment
        elif ema_20 < ema_50 < ema_100:
            directional_bias = 'SHORT'
            ema_alignment = True
            
            # Calculate separation strength (negative)
            separation = ((ema_100 - ema_20) / ema_100) * 100 if ema_100 > 0 else 0
            
            # Scale to [-1.0, 0]
            trend_score = -min(1.0, max(0.0, separation * 200))
            
        # NEUTRAL - EMAs not aligned
        else:
            directional_bias = 'NEUTRAL'
            ema_alignment = False
            trend_score = 0.0
        
        return {
            'directional_bias': directional_bias,
            'trend_score': float(trend_score),
            'ema_alignment': ema_alignment
        }
