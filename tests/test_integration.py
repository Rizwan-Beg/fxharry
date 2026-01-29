import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_core.strategy_engine.strategy_manager import StrategyManager
from ai_core.strategy_engine.signal_router import SignalRouter

async def mock_ws_broadcaster(payload):
    print(f"MOCK BROADCAST: {payload}")

async def test_integration():
    print("Initializing StrategyManager...")
    strategy_manager = StrategyManager()
    
    print("Initializing SignalRouter...")
    signal_router = SignalRouter(ws_broadcaster=mock_ws_broadcaster)
    
    symbol = "EURUSD"
    prices = [1.1000, 1.1005, 1.1010, 1.1015, 1.1020] * 10 # Generate enough data
    
    print("Processing ticks...")
    for price in prices:
        signals = strategy_manager.process_tick(symbol, price)
        if signals:
            print(f"Signals generated: {signals}")
            # Verify new fields
            for signal in signals:
                if "strategy_id" not in signal:
                    print("ERROR: strategy_id missing")
                if "timestamp" not in signal:
                    print("ERROR: timestamp missing")
            await signal_router.broadcast_signals(signals)
        else:
            # print("No signals")
            pass

    print("Test completed successfully.")

if __name__ == "__main__":
    asyncio.run(test_integration())
