"""
Stage 3: Participation Filter
VWAP-based institutional participation scoring.
"""

from typing import Dict, Optional


class ParticipationFilter:
    """
    Stage 3: Participation Filter
    
    Scores price action relative to VWAP to measure institutional participation.
    
    Logic:
    - Price reclaims and holds VWAP → positive score
    - Extended distance (>1 ATR) → negative score (fade)
    - Choppy around VWAP → near zero
    """
    
    def __init__(self):
        """Initialize participation filter."""
        pass
    
    def evaluate(self, price: float, vwap: Optional[float], 
                 atr: Optional[float]) -> Dict:
        """
        Evaluate institutional participation via VWAP.
        
        Args:
            price: Current price
            vwap: Volume Weighted Average Price
            atr: Average True Range (14)
            
        Returns:
            {
                'participation_score': float,  # [-1.0, +1.0]
                'vwap_distance_atr': float,
                'participation_type': str
            }
        """
        if vwap is None or atr is None or atr == 0:
            return {
                'participation_score': 0.0,
                'vwap_distance_atr': 0.0,
                'participation_type': 'UNKNOWN'
            }
        
        # Calculate distance in ATR units
        distance = (price - vwap) / atr
        
        # Score based on VWAP relationship
        if abs(distance) > 1.0:
            # Extended from VWAP - fade the move
            participation_score = -0.8 * (distance / abs(distance))  # -0.8 or +0.8 (opposite direction)
            participation_type = 'EXTENDED_FADE'
            
        elif distance > 0.2:
            # Above VWAP, reclaimed and holding
            # Scale position: 0.2 to 1.0 ATR → score 0.4 to 0.7
            participation_score = min(0.7, 0.4 + (distance - 0.2) * 0.5)
            participation_type = 'ABOVE_VWAP'
            
        elif distance < -0.2:
            # Below VWAP
            # Scale position: -0.2 to -1.0 ATR → score -0.4 to -0.7
            participation_score = max(-0.7, -0.4 + (distance + 0.2) * 0.5)
            participation_type = 'BELOW_VWAP'
            
        else:
            # Choppy around VWAP (-0.2 to +0.2 ATR)
            participation_score = 0.0
            participation_type = 'CHOPPY'
        
        return {
            'participation_score': float(participation_score),
            'vwap_distance_atr': float(distance),
            'participation_type': participation_type
        }
