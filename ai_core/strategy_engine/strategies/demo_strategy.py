import time
import random

class DemoStrategy:
    def __init__(self):
        self.last_signal_time = 0
        self.signal_interval = 5  # Generate a signal every 5 seconds

    def generate_signal(self, symbol, price, features):
        current_time = time.time()
        
        # Only generate signal if enough time has passed
        if current_time - self.last_signal_time < self.signal_interval:
            return None

        self.last_signal_time = current_time
        
        # Randomly decide BUY or SELL
        signal_type = "BUY" if random.random() > 0.5 else "SELL"
        
        return {
            "symbol": symbol,
            "signal": signal_type,
            "reason": f"Demo Signal: Random {signal_type} for verification",
            "confidence": round(random.uniform(0.5, 0.99), 2),
            "strategy_id": "DEMO_STRAT",
            "timestamp": int(current_time * 1000)
        }
