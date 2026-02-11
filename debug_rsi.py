"""Quick test to check RSI values with trending data"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_core.strategy_engine.core.multi_timeframe_feature_engine import MultiTimeframeFeatureEngine

mtf = MultiTimeframeFeatureEngine()

# Build M15 bullish bias (50 uptrend candles)
print("Building M15 uptrend...")
for i in range(50):
    price = 1.0800 + (i * 0.0001)
    result = mtf.update_m15_candle(price, price, price, price)

print(f"M15 Bias: {result['bias']} ({mtf.get_m15_bias()})")

# Build M5 with varied momentum to get RSI < 70
print("\nBuilding M5 candles...")
for i in range(30):
    price = 1.0850 + (i * 0.00005)
    result = mtf.update_m5_candle(price, price, price, price)

print(f"After 30: SMA10={result.get('sma_10')}, SMA30={result.get('sma_30')}, RSI={result.get('rsi_14')}")

# Add mixed candles to moderate RSI
prices = [1.0865, 1.0866, 1.0865, 1.0867, 1.0868, 1.0867, 1.0869, 1.0870, 1.0869, 1.0871]
for price in prices:
    result = mtf.update_m5_candle(price, price, price, price)

print(f"After mixed: SMA10={result.get('sma_10'):.5f}, SMA30={result.get('sma_30'):.5f}, RSI={result.get('rsi_14'):.1f}")
print(f"SMA10 > SMA30: {result.get('sma_10') > result.get('sma_30')}")
print(f"RSI < 70: {result.get('rsi_14') < 70}")
print(f"M15 bias: {result.get('m15_bias')}")
