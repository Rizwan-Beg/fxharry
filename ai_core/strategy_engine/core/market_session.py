"""Market session utilities for trading strategies."""

from datetime import datetime, time
import pytz


class MarketSession:
    """Utility class for checking market trading sessions."""
    
    # Define major forex trading sessions in their LOCAL timezones
    # Each session runs from 08:00 to 17:00 in its local timezone
    SESSIONS = {
        "london": {
            "open": time(8, 0),   # 08:00 Europe/London
            "close": time(17, 0),  # 17:00 Europe/London
            "timezone": "Europe/London"
        },
        "new_york": {
            "open": time(8, 0),   # 08:00 America/New_York
            "close": time(17, 0),  # 17:00 America/New_York
            "timezone": "America/New_York"
        },
        "tokyo": {
            "open": time(8, 0),    # 08:00 Asia/Tokyo
            "close": time(17, 0),   # 17:00 Asia/Tokyo
            "timezone": "Asia/Tokyo"
        },
        "sydney": {
            "open": time(8, 0),   # 08:00 Australia/Sydney
            "close": time(17, 0),   # 17:00 Australia/Sydney
            "timezone": "Australia/Sydney"
        }
    }
    
    @staticmethod
    def is_session_active(session_name: str, current_time: datetime = None) -> bool:
        """
        Check if a specific trading session is currently active.
        
        Args:
            session_name: Name of the session ('london', 'new_york', 'tokyo', 'sydney')
            current_time: Optional datetime to check (defaults to current UTC time)
            
        Returns:
            bool: True if the session is active, False otherwise
        """
        if current_time is None:
            current_time = datetime.now(pytz.UTC)
        
        # Ensure we have a timezone-aware datetime
        if current_time.tzinfo is None:
            current_time = pytz.UTC.localize(current_time)
        
        session = MarketSession.SESSIONS.get(session_name.lower())
        if not session:
            raise ValueError(f"Unknown session: {session_name}")
        
        # Convert current time to the session's local timezone
        session_tz = pytz.timezone(session["timezone"])
        local_time = current_time.astimezone(session_tz)
        local_time_only = local_time.time()
        
        open_time = session["open"]
        close_time = session["close"]
        
        # Handle sessions that cross midnight
        if open_time > close_time:
            # Session spans midnight
            return local_time_only >= open_time or local_time_only < close_time
        else:
            # Normal session (e.g., London: 08:00 to 17:00 local time)
            return open_time <= local_time_only < close_time
    
    @staticmethod
    def is_trading_allowed(allowed_sessions: list = None, current_time: datetime = None) -> dict:
        """
        Check if trading is allowed based on specified sessions.
        
        Args:
            allowed_sessions: List of session names to check (e.g., ['london', 'new_york'])
                             If None, defaults to ['london', 'new_york']
            current_time: Optional datetime to check (defaults to current UTC time)
            
        Returns:
            dict: {
                'allowed': bool,
                'current_session': str or None,
                'active_sessions': list
            }
        """
        if allowed_sessions is None:
            allowed_sessions = ['london', 'new_york']
        
        if current_time is None:
            current_time = datetime.now(pytz.UTC)
        
        # Check which sessions are currently active
        active_sessions = []
        for session_name in MarketSession.SESSIONS.keys():
            if MarketSession.is_session_active(session_name, current_time):
                active_sessions.append(session_name)
        
        # Check if any of the allowed sessions are active
        allowed_active_sessions = [s for s in active_sessions if s in [sess.lower() for sess in allowed_sessions]]
        
        return {
            'allowed': len(allowed_active_sessions) > 0,
            'current_session': allowed_active_sessions[0] if allowed_active_sessions else None,
            'active_sessions': active_sessions,
            'checked_time_utc': current_time.isoformat()
        }
    
    @staticmethod
    def is_london_or_newyork_active(current_time: datetime = None) -> bool:
        """
        Convenience method to check if London or New York session is active.
        
        Args:
            current_time: Optional datetime to check (defaults to current UTC time)
            
        Returns:
            bool: True if either London or New York session is active
        """
        result = MarketSession.is_trading_allowed(['london', 'new_york'], current_time)
        return result['allowed']
    
    @staticmethod
    def get_current_sessions(current_time: datetime = None) -> list:
        """
        Get all currently active trading sessions.
        
        Args:
            current_time: Optional datetime to check (defaults to current UTC time)
            
        Returns:
            list: Names of all active sessions
        """
        if current_time is None:
            current_time = datetime.now(pytz.UTC)
        
        active_sessions = []
        for session_name in MarketSession.SESSIONS.keys():
            if MarketSession.is_session_active(session_name, current_time):
                active_sessions.append(session_name)
        
        return active_sessions
