# ai_core/strategy_engine/feature_engine.py

import numpy as np
from collections import deque

class FeatureEngine:
    def __init__(self, max_history=500):
        self.prices = deque(maxlen=max_history)
        # Store EMA state for efficient continuous calculation
        self.ema_20_prev = None
        self.ema_50_prev = None
        self.ema_100_prev = None

    def update_price(self, price: float):
        self.prices.append(price)
        return self.compute_features()

    def compute_features(self):
        if len(self.prices) < 20:
            return {}

        arr = np.array(self.prices)

        features = {
            "sma_20": np.mean(arr[-20:]),
            "sma_50": np.mean(arr[-50:]) if len(arr) >= 50 else None,
            "ema_20": self._compute_ema(arr, 20),
            "ema_50": self._compute_ema(arr, 50) if len(arr) >= 50 else None,
            "ema_100": self._compute_ema(arr, 100) if len(arr) >= 100 else None,
            "rsi_14": self._compute_rsi(arr, 14),
            "atr_14": self._compute_atr(arr, 14),
            "momentum": arr[-1] - arr[-4] if len(arr) >= 4 else None,
        }

        return features

    def _compute_ema(self, prices, period):
        """
        Compute Exponential Moving Average using standard formula.
        For efficiency, uses previous EMA value if available.
        Smoothing factor: α = 2/(period + 1)
        """
        if len(prices) < period:
            return None
        
        # Smoothing factor
        alpha = 2 / (period + 1)
        
        # Determine which previous EMA to use based on period
        if period == 20:
            prev_ema = self.ema_20_prev
        elif period == 50:
            prev_ema = self.ema_50_prev
        elif period == 100:
            prev_ema = self.ema_100_prev
        else:
            prev_ema = None
        
        # If we have a previous EMA, use it for efficient calculation
        if prev_ema is not None:
            current_ema = alpha * prices[-1] + (1 - alpha) * prev_ema
        else:
            # First time: use SMA as initial EMA
            current_ema = np.mean(prices[-period:])
        
        # Store the current EMA for next iteration
        if period == 20:
            self.ema_20_prev = current_ema
        elif period == 50:
            self.ema_50_prev = current_ema
        elif period == 100:
            self.ema_100_prev = current_ema
        
        return float(current_ema)

    def _compute_rsi(self, prices, period):
        if len(prices) < period + 1:
            return None

        diffs = np.diff(prices)
        gains = np.maximum(diffs, 0)
        losses = np.maximum(-diffs, 0)

        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def _compute_atr(self, prices, period):
        if len(prices) < period + 1:
            return None
        true_ranges = np.abs(np.diff(prices[-period:]))
        return float(np.mean(true_ranges))
