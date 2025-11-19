"""Strategy engine orchestrating rule-based, ML, hybrid strategies."""
# ai_core/strategy_engine/__init__.py

from .strategy_manager import StrategyManager

# Singleton-style instance used across the app
strategy_engine = StrategyManager()
