# ai_core/strategy_engine/strategy_manager.py

from .feature_engine import FeatureEngine
from .strategies.sma_crossover import SMACrossoverStrategy
from .strategies.rsi_reversal import RSIReversalStrategy

class StrategyManager:
    def __init__(self):
        self.feature_engines = {}
        
        self.strategies = {
            "sma": SMACrossoverStrategy(),
            "rsi": RSIReversalStrategy(),
        }

    def process_tick(self, symbol, price):
        if symbol not in self.feature_engines:
            self.feature_engines[symbol] = FeatureEngine()

        features = self.feature_engines[symbol].update_price(price)

        if not features:
            return None  # Not enough data

        signals = []

        for name, strategy in self.strategies.items():
            signal = strategy.generate_signal(symbol, price, features)
            if signal:
                signals.append(signal)

        return signals
