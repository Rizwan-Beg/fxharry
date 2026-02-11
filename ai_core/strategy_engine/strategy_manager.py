# ai_core/strategy_engine/strategy_manager.py

from .core.feature_engine import FeatureEngine
from .strategies.apex_strategy import ApexStrategy
from .strategies.riztest_strategy import RizTestStrategy

class StrategyManager:
    def __init__(self):
        self.feature_engines = {}
        
        # Apex V1: Multi-timeframe trend-following strategy
        # RizTest: Simple test strategy for end-to-end verification
        self.strategies = {
            "apex": ApexStrategy(),
            "riztest": RizTestStrategy(),  # Test strategy
        }
        
        # Track active strategies (default: apex)
        # TODO: Load from config/database in future
        self.active_strategies = {"apex"}

    def activate_strategy(self, strategy_id: str) -> bool:
        """Enable a specific strategy."""
        if strategy_id in self.strategies:
            self.active_strategies.add(strategy_id)
            return True
        return False

    def deactivate_strategy(self, strategy_id: str) -> bool:
        """Disable a specific strategy."""
        if strategy_id in self.active_strategies:
            self.active_strategies.remove(strategy_id)
            return True
        return False

    def get_strategy_status(self) -> list:
        """Get status of all strategies."""
        status_list = []
        for s_id, strategy in self.strategies.items():
            status_list.append({
                "id": s_id,
                "name": strategy.__class__.__name__,
                "is_active": s_id in self.active_strategies,
                "description": getattr(strategy, "description", "No description")
            })
        return status_list

    def process_tick(self, symbol, price):
        if symbol not in self.feature_engines:
            self.feature_engines[symbol] = FeatureEngine()

        features = self.feature_engines[symbol].update_price(price)

        if not features:
            return None  # Not enough data

        signals = []

        for name, strategy in self.strategies.items():
            # Only process if strategy is active
            if name not in self.active_strategies:
                continue
                
            signal = strategy.generate_signal(symbol, price, features)
            if signal:
                signals.append(signal)

        return signals
