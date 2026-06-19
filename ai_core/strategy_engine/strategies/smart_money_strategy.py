"""
Smart Money Concepts (SMC) Strategy

Institutional-style top-down analysis:
- 4H timeframe: Trend bias (SMA 10 vs SMA 50)
- 1H timeframe: Market structure confirmation
- 5M timeframe: Execution trigger (SMA 10 crosses SMA 30)
- Risk management: 1:5 R:R ratio
"""

import time
import numpy as np
from typing import Dict, Optional
from collections import deque

class SmartMoneyStrategy:
    def __init__(self):
        """Initialize the SMC Strategy."""
        self.strategy_id = "smc"
        self.description = "Smart Money Concepts: 4H Trend, 1H Structure, 5M Entry"
        
        # Deques to store closing prices for moving average calculations
        self.h4_close = deque(maxlen=60)
        self.h1_close = deque(maxlen=60)
        self.m5_close = deque(maxlen=60)
        
        # State tracking
        self.trend_bias = 0        # 4H bias: +1 (Bullish), -1 (Bearish), 0 (Neutral)
        self.structure_bias = 0    # 1H bias: +1 (Bullish), -1 (Bearish), 0 (Neutral)
        self.last_m5_sma_10 = None
        self.last_m5_sma_30 = None
        
        # Position tracking for simulated exit logic
        self.current_position = None
        self.entry_price = None
        
        # Fixed 1:5 Risk Reward (10 pips risk, 50 pips reward)
        # Assuming 1 pip = 0.0001 for EUR/USD
        self.stop_loss_pips = 0.0010
        self.take_profit_pips = 0.0050

    def update_4h_candle(self, open_price: float, high: float, low: float, close: float) -> None:
        """Update 4H trend bias."""
        self.h4_close.append(close)
        
        if len(self.h4_close) >= 50:
            sma_10 = np.mean(list(self.h4_close)[-10:])
            sma_50 = np.mean(list(self.h4_close)[-50:])
            
            if sma_10 > sma_50:
                self.trend_bias = 1
            elif sma_10 < sma_50:
                self.trend_bias = -1
            else:
                self.trend_bias = 0

    def update_1h_candle(self, open_price: float, high: float, low: float, close: float) -> None:
        """Update 1H structure bias."""
        self.h1_close.append(close)
        
        # Simple confirmation: if the close is above the open, structure is bullish, else bearish
        # To make it more robust, we can use a short moving average on 1H
        if len(self.h1_close) >= 20:
            sma_20 = np.mean(list(self.h1_close)[-20:])
            if close > sma_20:
                self.structure_bias = 1
            elif close < sma_20:
                self.structure_bias = -1
            else:
                self.structure_bias = 0

    def update_5m_candle(self, open_price: float, high: float, low: float, close: float) -> Optional[Dict]:
        """Update 5M candle and check for execution trigger."""
        self.m5_close.append(close)
        
        if len(self.m5_close) < 30:
            return None  # Not enough data
            
        sma_10 = float(np.mean(list(self.m5_close)[-10:]))
        sma_30 = float(np.mean(list(self.m5_close)[-30:]))
        
        # Exit logic if we are already in a position
        if self.current_position:
            # Check for trend reversal on 1H
            exit_signal = None
            if self.current_position == 'LONG' and self.structure_bias == -1:
                exit_signal = 'EXIT LONG (1H Structure Reversed)'
            elif self.current_position == 'SHORT' and self.structure_bias == 1:
                exit_signal = 'EXIT SHORT (1H Structure Reversed)'
                
            if exit_signal:
                sig = {
                    'symbol': 'EUR/USD',
                    'action': 'EXIT',
                    'position': self.current_position,
                    'reason': exit_signal,
                    'confidence': 1.0,
                    'strategy_id': self.strategy_id,
                    'timestamp': int(time.time() * 1000)
                }
                self.current_position = None
                return sig
            
            # If not exiting, store latest M5 and return
            self.last_m5_sma_10 = sma_10
            self.last_m5_sma_30 = sma_30
            return None

        # Entry logic
        signal = None
        
        # Check alignment: 4H and 1H must agree
        if self.trend_bias == 1 and self.structure_bias == 1:
            # Look for 5M bullish crossover
            if self.last_m5_sma_10 is not None and self.last_m5_sma_30 is not None:
                if self.last_m5_sma_10 <= self.last_m5_sma_30 and sma_10 > sma_30:
                    self.current_position = 'LONG'
                    signal = {
                        'symbol': 'EUR/USD',
                        'action': 'LONG',
                        'reason': 'SMC LONG: 4H Bullish, 1H Confirmed, 5M Golden Cross',
                        'confidence': 0.90,
                        'strategy_id': self.strategy_id,
                        'timestamp': int(time.time() * 1000),
                        'stop_loss': close - self.stop_loss_pips,
                        'take_profit': close + self.take_profit_pips
                    }
                    
        elif self.trend_bias == -1 and self.structure_bias == -1:
            # Look for 5M bearish crossover
            if self.last_m5_sma_10 is not None and self.last_m5_sma_30 is not None:
                if self.last_m5_sma_10 >= self.last_m5_sma_30 and sma_10 < sma_30:
                    self.current_position = 'SHORT'
                    signal = {
                        'symbol': 'EUR/USD',
                        'action': 'SHORT',
                        'reason': 'SMC SHORT: 4H Bearish, 1H Confirmed, 5M Death Cross',
                        'confidence': 0.90,
                        'strategy_id': self.strategy_id,
                        'timestamp': int(time.time() * 1000),
                        'stop_loss': close + self.stop_loss_pips,
                        'take_profit': close - self.take_profit_pips
                    }

        # Store SMAs for next tick crossover check
        self.last_m5_sma_10 = sma_10
        self.last_m5_sma_30 = sma_30
        
        return signal

    def generate_signal(self, symbol: str, price: float, features: dict) -> Optional[Dict]:
        """Legacy interface for compatibility."""
        return None
