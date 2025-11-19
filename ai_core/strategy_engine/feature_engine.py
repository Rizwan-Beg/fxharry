# ai_core/strategy_engine/feature_engine.py

import numpy as np
from collections import deque

class FeatureEngine:
    def __init__(self, max_history=500):
        self.prices = deque(maxlen=max_history)

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
            "rsi_14": self._compute_rsi(arr, 14),
            "atr_14": self._compute_atr(arr, 14),
            "momentum": arr[-1] - arr[-4] if len(arr) >= 4 else None,
        }

        return features

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
