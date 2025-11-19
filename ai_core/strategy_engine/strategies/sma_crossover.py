# ai_core/strategy_engine/strategies/sma_crossover.py

class SMACrossoverStrategy:
    def generate_signal(self, symbol, price, features):
        sma20 = features.get("sma_20")
        sma50 = features.get("sma_50")

        if sma20 is None or sma50 is None:
            return None

        if sma20 > sma50:
            return {
                "symbol": symbol,
                "signal": "BUY",
                "reason": "SMA20 crossed above SMA50",
                "confidence": 0.72
            }

        if sma20 < sma50:
            return {
                "symbol": symbol,
                "signal": "SELL",
                "reason": "SMA20 crossed below SMA50",
                "confidence": 0.68
            }

        return None
