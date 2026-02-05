#!/usr/bin/env python3
"""
Test script for EMA Crossover Filter Strategy

This script simulates price data to test the EMA crossover filter
and verify signal generation works correctly.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_core.strategy_engine.strategy_manager import StrategyManager
import numpy as np

def simulate_bullish_crossover():
    """Simulate a bullish EMA crossover scenario"""
    print("=" * 60)
    print("TEST 1: Simulating Bullish EMA Crossover")
    print("=" * 60)
    
    sm = StrategyManager()
    symbol = "EUR.USD"
    
    # Start with downtrend, then reverse to uptrend
    base_price = 1.10000
    prices = []
    
    # Downtrend phase (100 ticks)
    for i in range(100):
        noise = np.random.normal(0, 0.00010)
        price = base_price - (i * 0.00005) + noise
        prices.append(price)
    
    # Reversal and uptrend phase (100 ticks)
    for i in range(100):
        noise = np.random.normal(0, 0.00010)
        price = prices[-1] + (i * 0.00008) + noise
        prices.append(price)
    
    # Process all prices and look for signals
    signals_generated = []
    for idx, price in enumerate(prices):
        signals = sm.process_tick(symbol, price)
        if signals:
            for signal in signals:
                if signal["strategy_id"] == "EMA_CROSSOVER_FILTER":
                    signals_generated.append((idx, signal))
                    print(f"\n✓ Signal at tick {idx}:")
                    print(f"  Type: {signal['signal']}")
                    print(f"  Reason: {signal['reason']}")
                    print(f"  Confidence: {signal['confidence']:.2%}")
                    if 'metadata' in signal:
                        meta = signal['metadata']
                        print(f"  EMA20: {meta['ema_20']:.5f}")
                        print(f"  EMA50: {meta['ema_50']:.5f}")
                        print(f"  EMA100: {meta['ema_100']:.5f}")
                        print(f"  Crossover: {meta['crossover']}")
    
    print(f"\n✓ Total signals generated: {len(signals_generated)}")
    return len(signals_generated) > 0

def simulate_bearish_crossover():
    """Simulate a bearish EMA crossover scenario"""
    print("\n" + "=" * 60)
    print("TEST 2: Simulating Bearish EMA Crossover")
    print("=" * 60)
    
    sm = StrategyManager()
    symbol = "GBP.USD"
    
    # Start with uptrend, then reverse to downtrend
    base_price = 1.30000
    prices = []
    
    # Uptrend phase (100 ticks)
    for i in range(100):
        noise = np.random.normal(0, 0.00010)
        price = base_price + (i * 0.00005) + noise
        prices.append(price)
    
    # Reversal and downtrend phase (100 ticks)
    for i in range(100):
        noise = np.random.normal(0, 0.00010)
        price = prices[-1] - (i * 0.00008) + noise
        prices.append(price)
    
    # Process all prices and look for signals
    signals_generated = []
    for idx, price in enumerate(prices):
        signals = sm.process_tick(symbol, price)
        if signals:
            for signal in signals:
                if signal["strategy_id"] == "EMA_CROSSOVER_FILTER":
                    signals_generated.append((idx, signal))
                    print(f"\n✓ Signal at tick {idx}:")
                    print(f"  Type: {signal['signal']}")
                    print(f"  Reason: {signal['reason']}")
                    print(f"  Confidence: {signal['confidence']:.2%}")
                    if 'metadata' in signal:
                        meta = signal['metadata']
                        print(f"  EMA20: {meta['ema_20']:.5f}")
                        print(f"  EMA50: {meta['ema_50']:.5f}")
                        print(f"  EMA100: {meta['ema_100']:.5f}")
                        print(f"  Crossover: {meta['crossover']}")
    
    print(f"\n✓ Total signals generated: {len(signals_generated)}")
    return len(signals_generated) > 0

def test_ema_calculations():
    """Test that EMA values are being calculated correctly"""
    print("\n" + "=" * 60)
    print("TEST 3: Verifying EMA Calculations")
    print("=" * 60)
    
    sm = StrategyManager()
    symbol = "TEST.PAIR"
    
    # Feed steady upward prices to verify EMA calculations
    base_price = 1.00000
    for i in range(120):
        price = base_price + (i * 0.00001)
        signals = sm.process_tick(symbol, price)
    
    # Get the feature engine and check final EMAs
    feature_engine = sm.feature_engines[symbol]
    features = feature_engine.compute_features()
    
    print(f"\n✓ After 120 ticks of upward movement:")
    print(f"  EMA20:  {features.get('ema_20', 'N/A'):.5f}")
    print(f"  EMA50:  {features.get('ema_50', 'N/A'):.5f}")
    print(f"  EMA100: {features.get('ema_100', 'N/A'):.5f}")
    
    # Verify EMA20 > EMA50 > EMA100 for uptrend
    ema20 = features.get('ema_20')
    ema50 = features.get('ema_50')
    ema100 = features.get('ema_100')
    
    if ema20 and ema50 and ema100:
        alignment_correct = ema20 > ema50 > ema100
        print(f"\n✓ Bullish alignment check (EMA20 > EMA50 > EMA100): {alignment_correct}")
        return alignment_correct
    
    return False

if __name__ == "__main__":
    print("\n🧪 Testing EMA Crossover Filter Strategy\n")
    
    try:
        test1_passed = simulate_bullish_crossover()
        test2_passed = simulate_bearish_crossover()
        test3_passed = test_ema_calculations()
        
        print("\n" + "=" * 60)
        print("TEST RESULTS")
        print("=" * 60)
        print(f"✓ Bullish Crossover Test: {'PASSED' if test1_passed else 'FAILED'}")
        print(f"✓ Bearish Crossover Test: {'PASSED' if test2_passed else 'FAILED'}")
        print(f"✓ EMA Calculation Test: {'PASSED' if test3_passed else 'FAILED'}")
        
        all_passed = test1_passed and test2_passed and test3_passed
        print(f"\n{'✅ ALL TESTS PASSED!' if all_passed else '❌ SOME TESTS FAILED'}")
        
        sys.exit(0 if all_passed else 1)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
