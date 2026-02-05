# ai_core/strategy_engine/strategies/rsi_reversal.py

import time
from ai_core.strategy_engine.core.market_session import MarketSession


class RSIReversalStrategy:
    def __init__(self):
        """Initialize RSI Reversal Strategy with session filtering."""
        # By default, only allow trading during London and New York sessions
        self.allowed_sessions = ['london', 'new_york']
    
    def generate_signal(self, symbol, price, features):
        # FIRST CHECK: Is trading allowed during current market session?
        session_check = MarketSession.is_trading_allowed(self.allowed_sessions)
        
        if not session_check['allowed']:
            # Market session check failed - no trading allowed
            return None
        
        # Get RSI value
        rsi = features.get("rsi_14")

        if rsi is None:
            return None

        # RSI Oversold - BUY Signal
        if rsi < 30:
            return {
                "symbol": symbol,
                "signal": "BUY",
                "reason": f"RSI Oversold (<30) during {session_check['current_session'].upper()} session",
                "confidence": 0.60,
                "strategy_id": "RSI_REV",
                "timestamp": int(time.time() * 1000),
                "metadata": {
                    "rsi": rsi,
                    "session": session_check['current_session'],
                    "active_sessions": session_check['active_sessions']
                }
            }

        # RSI Overbought - SELL Signal
        if rsi > 70:
            return {
                "symbol": symbol,
                "signal": "SELL",
                "reason": f"RSI Overbought (>70) during {session_check['current_session'].upper()} session",
                "confidence": 0.60,
                "strategy_id": "RSI_REV",
                "timestamp": int(time.time() * 1000),
                "metadata": {
                    "rsi": rsi,
                    "session": session_check['current_session'],
                    "active_sessions": session_check['active_sessions']
                }
            }

        return None
