# ibkr_streaming/candle_engine.py

from collections import defaultdict
import time
from .logger import get_logger

logger = get_logger(__name__)

TIMEFRAMES = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "1h": 3600,
    "4h": 14400,
}

class CandleEngine:
    def __init__(self):
        self.candles = defaultdict(dict)
        logger.info(f"CandleEngine initialized with timeframes: {list(TIMEFRAMES.keys())}")

    def update(self, tick):
        """Update candle data for all timeframes"""
        import math
        symbol = tick['symbol']
        price = tick['mid']
        
        # Validate price is not NaN or invalid
        if price is None or (isinstance(price, float) and math.isnan(price)) or price <= 0:
            logger.warning(f"Invalid price for {symbol}: {price}, skipping candle update")
            return self.candles
        
        now = int(time.time())

        new_candles = []
        
        for tf, duration in TIMEFRAMES.items():
            bucket = now - (now % duration)

            if bucket not in self.candles[symbol].get(tf, {}):
                # New candle created
                self.candles[symbol].setdefault(tf, {})[bucket] = {
                    "open": price,
                    "high": price,
                    "low": price,
                    "close": price,
                    "timestamp": bucket
                }
                new_candles.append(f"{symbol}:{tf}")
                logger.debug(f"New candle created: {symbol} | {tf} | Bucket: {bucket} | Price: {price}")
            else:
                # Update existing candle
                c = self.candles[symbol][tf][bucket]
                
                # Initialize with current price if candle has NaN values
                if math.isnan(c.get("open", float('nan'))):
                    c["open"] = price
                if math.isnan(c.get("high", float('nan'))):
                    c["high"] = price
                if math.isnan(c.get("low", float('nan'))):
                    c["low"] = price
                if math.isnan(c.get("close", float('nan'))):
                    c["close"] = price
                
                old_high = c["high"]
                old_low = c["low"]
                c["high"] = max(c["high"], price)
                c["low"] = min(c["low"], price)
                c["close"] = price
                
                # Log significant price movements
                if c["high"] != old_high or c["low"] != old_low:
                    logger.debug(f"Candle updated: {symbol} | {tf} | High: {c['high']} | Low: {c['low']} | Close: {c['close']}")

        if new_candles:
            logger.info(f"New candles created: {', '.join(new_candles)}")

        return self.candles
