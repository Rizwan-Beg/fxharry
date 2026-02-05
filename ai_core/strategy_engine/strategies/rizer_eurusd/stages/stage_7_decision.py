"""
Stage 7: Decision Engine
Weighted aggregation of all signals to generate trading decision.
"""

from typing import Dict, Optional


class DecisionEngine:
    """
    Stage 7: Decision Engine
    
    Aggregates scores from stages 2-6 with configurable weights.
    
    Default weights:
    - regime_score: 0.15
    - participation_score: 0.25
    - trend_score: 0.20
    - timing_score: 0.10
    - ml_edge_score: 0.30
    
    Decision thresholds:
    - final_score >= +0.35 → LONG
    - final_score <= -0.35 → SHORT
    - else → NO TRADE
    """
    
    def __init__(self, weight_regime: float = 0.15,
                 weight_participation: float = 0.25,
                 weight_trend: float = 0.20,
                 weight_timing: float = 0.10,
                 weight_ml_edge: float = 0.30,
                 long_threshold: float = 0.35,
                 short_threshold: float = -0.35):
        """
        Initialize decision engine.
        
        Args:
            weight_regime: Weight for regime score
            weight_participation: Weight for participation score
            weight_trend: Weight for trend score
            weight_timing: Weight for timing score
            weight_ml_edge: Weight for ML edge score
            long_threshold: Threshold for long signal
            short_threshold: Threshold for short signal
        """
        self.weight_regime = weight_regime
        self.weight_participation = weight_participation
        self.weight_trend = weight_trend
        self.weight_timing = weight_timing
        self.weight_ml_edge = weight_ml_edge
        
        self.long_threshold = long_threshold
        self.short_threshold = short_threshold
        
        # Validate weights sum to 1.0
        total_weight = (weight_regime + weight_participation + weight_trend + 
                       weight_timing + weight_ml_edge)
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total_weight}")
    
    def evaluate(self, regime_score: float, participation_score: float,
                 trend_score: float, timing_score: float,
                 ml_edge_score: float) -> Dict:
        """
        Aggregate scores and generate trading decision.
        
        Args:
            regime_score: From Stage 2 [0.0, 1.0]
            participation_score: From Stage 3 [-1.0, +1.0]
            trend_score: From Stage 4 [-1.0, +1.0]
            timing_score: From Stage 5 [-0.5, +0.5]
            ml_edge_score: From Stage 6 [-1.0, +1.0]
            
        Returns:
            {
                'signal': str,        # 'LONG', 'SHORT', or None
                'final_score': float, # [-1.0, +1.0]
                'breakdown': dict     # Individual weighted contributions
            }
        """
        # Calculate weighted contributions
        regime_contribution = regime_score * self.weight_regime
        participation_contribution = participation_score * self.weight_participation
        trend_contribution = trend_score * self.weight_trend
        timing_contribution = timing_score * self.weight_timing
        ml_edge_contribution = ml_edge_score * self.weight_ml_edge
        
        # Aggregate final score
        final_score = (
            regime_contribution +
            participation_contribution +
            trend_contribution +
            timing_contribution +
            ml_edge_contribution
        )
        
        # Decision logic
        if final_score >= self.long_threshold:
            signal = 'LONG'
        elif final_score <= self.short_threshold:
            signal = 'SHORT'
        else:
            signal = None
        
        # Breakdown for transparency
        breakdown = {
            'regime': regime_contribution,
            'participation': participation_contribution,
            'trend': trend_contribution,
            'timing': timing_contribution,
            'ml_edge': ml_edge_contribution,
            'inputs': {
                'regime_score': regime_score,
                'participation_score': participation_score,
                'trend_score': trend_score,
                'timing_score': timing_score,
                'ml_edge_score': ml_edge_score
            }
        }
        
        return {
            'signal': signal,
            'final_score': float(final_score),
            'breakdown': breakdown
        }
