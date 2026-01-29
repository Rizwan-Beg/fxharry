# ai_core/strategy_engine/strategies/rsi_reversal.py

import time

class RSIReversalStrategy:
    def generate_signal(self, symbol, price, features):
        rsi = features.get("rsi_14")

        if rsi is None:
            return None

        if rsi < 30:
            return {
                "symbol": symbol,
                "signal": "BUY",
                "reason": "RSI Oversold (<30)",
                "confidence": 0.60,
                "strategy_id": "RSI_REV",
                "timestamp": int(time.time() * 1000)
            }

        if rsi > 70:
            return {
                "symbol": symbol,
                "signal": "SELL",
                "reason": "RSI Overbought (>70)",
                "confidence": 0.60,
                "strategy_id": "RSI_REV",
                "timestamp": int(time.time() * 1000)
            }

        return None
