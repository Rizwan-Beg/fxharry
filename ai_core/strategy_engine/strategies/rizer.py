# RIZER Strategy Wrapper

import time
from .rizer_eurusd.rizer_strategy import RizerStrategy
from .rizer_eurusd.config import RizerConfig


class RIZER:
    """
    RIZER Strategy Wrapper for integration with existing strategy engine.
    
    9-stage production-grade trading strategy for EUR/USD 5-minute timeframe.
    """
    
    def __init__(self, account_equity: float = 10000.0):
        config = RizerConfig(
            symbol="EUR/USD",
            timeframe="5m",
            allowed_sessions=['london', 'new_york'],
            max_spread_pips=2.0,
            max_data_staleness_seconds=30,
            news_buffer_minutes=30
        )
        self.strategy = RizerStrategy(config=config, account_equity=account_equity)
    
    def generate_signal(self, symbol, price, features):
        spread = 1.5
        volume = 1000.0
        return self.strategy.generate_signal(
            symbol=symbol,
            price=price,
            features=features,
            spread=spread,
            volume=volume,
            high=price,
            low=price
        )
