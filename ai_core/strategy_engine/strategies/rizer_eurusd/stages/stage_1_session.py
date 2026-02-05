"""
Stage 1: Session Filter
Validates trading is allowed during London or New York sessions.
"""

from typing import Dict
from datetime import datetime
from ai_core.strategy_engine.core.market_session import MarketSession



class SessionFilter:
    """
    Stage 1: Session Filter
    
    Only allows trading during specified sessions (London, New York by default).
    """
    
    def __init__(self, allowed_sessions: list = None):
        """
        Initialize session filter.
        
        Args:
            allowed_sessions: List of allowed sessions (['london', 'new_york'])
        """
        if allowed_sessions is None:
            allowed_sessions = ['london', 'new_york']
        self.allowed_sessions = allowed_sessions
    
    def evaluate(self, current_time: datetime = None) -> Dict:
        """
        Check if current session allows trading.
        
        Args:
            current_time: Current time (defaults to now UTC)
            
        Returns:
            {
                'session_allowed': bool,
                'current_session': str or None,
                'active_sessions': list,
                'checked_time_utc': str
            }
        """
        result = MarketSession.is_trading_allowed(
            allowed_sessions=self.allowed_sessions,
            current_time=current_time
        )
        
        return {
            'session_allowed': result['allowed'],
            'current_session': result['current_session'],
            'active_sessions': result['active_sessions'],
            'checked_time_utc': result['checked_time_utc']
        }
