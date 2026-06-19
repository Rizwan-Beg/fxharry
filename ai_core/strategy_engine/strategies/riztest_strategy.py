"""
RizTest Strategy - Simple Test Strategy for End-to-End Verification

This strategy generates a BUY signal on every M5 candle update for EUR/USD.
Purpose: Verify the complete flow from data → strategy → execution → IBKR order placement.

WARNING: This is a TEST strategy only. Do not use in production!good weldone
"""

from typing import Dict, Optional
from datetime import datetime


class RizTestStrategy:
    """
    Simple test strategy that generates a signal on every M5 candle.
    
    Used to verify end-to-end integration:
    - IBKR data → Candles → Strategy → Signal → Execution → Order in TWS
    """
    
    def __init__(self):
        """Initialize the RizTest strategy."""
        self.strategy_id = "riztest"
        self.signal_count = 0
        self.max_signals = 1000  # Increased for continuous testing
        
        print(f"🧪 RizTest Strategy Initialized")
        print(f"   Will generate up to {self.max_signals} test signal(s)")
        print(f"   Symbol: EUR/USD")
        print(f"   Action: LONG (BUY)")
        print(f"   Trigger: M1 candles (every 1 minute)")
    
    def update_m1_candle(self, open_price: float, high: float, low: float, close: float) -> Optional[Dict]:
        """
        Called when a new M1 candle is formed.
        
        Generates a test LONG signal if we haven't reached max_signals.
        
        Args:
            open_price: M1 candle open
            high: M1 candle high
            low: M1 candle low
            close: M1 candle close
            
        Returns:
            Trading signal dict or None
        """
        # Check if we've already generated enough signals
        if self.signal_count >= self.max_signals:
            return None
        
        # Generate test signal
        self.signal_count += 1
        
        # Calculate stop loss and take profit (simple example)
        stop_loss = close * 0.995  # 0.5% below current price
        take_profit = close * 1.010  # 1.0% above current price
        
        signal = {
            'strategy_id': self.strategy_id,
            'symbol': 'EUR/USD',
            'action': 'LONG',  # BUY signal
            'price': close,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'reason': f'RizTest #{self.signal_count} - Testing end-to-end execution (M1 close: {close})',
            'timestamp': datetime.now().isoformat(),
            'confidence': 0.99,  # High confidence for testing
        }
        
        print(f"\n{'='*80}")
        print(f"🧪 RIZTEST SIGNAL GENERATED!")
        print(f"{'='*80}")
        print(f"Signal #{self.signal_count}/{self.max_signals}")
        print(f"Symbol: {signal['symbol']}")
        print(f"Action: {signal['action']}")
        print(f"Price: {signal['price']:.5f}")
        print(f"Stop Loss: {signal['stop_loss']:.5f}")
        print(f"Take Profit: {signal['take_profit']:.5f}")
        print(f"Reason: {signal['reason']}")
        print(f"{'='*80}\n")
        
        return signal
    
    def update_m15_candle(self, open_price: float, high: float, low: float, close: float):
        """
        Called when a new M15 candle is formed.
        
        RizTest doesn't use M15 candles, so this is a no-op.
        """
        pass
    
    def generate_signal(self, symbol: str, price: float, features: dict) -> Optional[Dict]:
        """
        Generate a test BUY signal based on real-time price ticks.
        """
        # Check if we've already generated enough signals
        if self.signal_count >= self.max_signals:
            return None
            
        self.signal_count += 1
        
        # Calculate stop loss and take profit
        stop_loss = price * 0.995  # 0.5% below current price
        take_profit = price * 1.010  # 1.0% above current price
        
        signal = {
            'strategy_id': self.strategy_id,
            'symbol': symbol,
            'action': 'LONG',  # BUY signal
            'price': price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'reason': f'RizTest #{self.signal_count} - Testing end-to-end execution (Price: {price})',
            'timestamp': datetime.now().isoformat(),
            'confidence': 0.99,  # High confidence for testing
        }
        
        print(f"\n{'='*80}")
        print(f"🧪 RIZTEST SIGNAL GENERATED!")
        print(f"{'='*80}")
        print(f"Signal #{self.signal_count}/{self.max_signals}")
        print(f"Symbol: {signal['symbol']}")
        print(f"Action: {signal['action']}")
        print(f"Price: {signal['price']:.5f}")
        print(f"Reason: {signal['reason']}")
        print(f"{'='*80}\n")
        
        return signal
