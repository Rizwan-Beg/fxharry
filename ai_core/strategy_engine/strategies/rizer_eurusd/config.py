"""RIZER Strategy Configuration."""

from dataclasses import dataclass
from typing import List


@dataclass
class RizerConfig:
    """Configuration for RIZER strategy."""
    
    # Market settings
    symbol: str = "EUR/USD"
    timeframe: str = "5m"
    
    # Trading sessions
    allowed_sessions: List[str] = None
    
    # Kill switch thresholds
    max_spread_pips: float = 2.0
    max_data_staleness_seconds: int = 30
    news_buffer_minutes: int = 30
    
    # Stage weights
    weight_regime: float = 0.15
    weight_participation: float = 0.25
    weight_trend: float = 0.20
    weight_timing: float = 0.10
    weight_ml_edge: float = 0.30
    
    # Decision thresholds
    long_threshold: float = 0.35
    short_threshold: float = -0.35
    
    # Risk management
    atr_stop_multiplier: float = 1.2
    risk_reward_ratio: float = 2.0
    risk_per_trade_percent: float = 0.01
    high_volatility_multiplier: float = 1.5
    high_volatility_size_reduction: float = 0.7
    
    def __post_init__(self):
        """Set defaults."""
        if self.allowed_sessions is None:
            self.allowed_sessions = ['london', 'new_york']
        
        # Validate weights sum to 1.0
        total = (self.weight_regime + self.weight_participation + 
                self.weight_trend + self.weight_timing + self.weight_ml_edge)
        assert abs(total - 1.0) < 0.001, f"Weights must sum to 1.0, got {total}"


# Default configuration instance
DEFAULT_CONFIG = RizerConfig()
