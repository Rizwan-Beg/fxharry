from ai_core.backtesting.vbt_engine import VectorBTEngine
import asyncio

engine = VectorBTEngine()
res = engine.run_backtest("1", "2026-01-01", "2026-02-01", 100000, ["EURUSD=X"], "1h")
print(res)
