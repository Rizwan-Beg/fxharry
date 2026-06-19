from datetime import datetime, timezone, time

class SessionFilter:
    """
    Forex Session Times (UTC)
    Sydney: 22:00 - 07:00
    Tokyo: 00:00 - 09:00
    London: 08:00 - 17:00
    New York: 13:00 - 22:00
    """
    
    @staticmethod
    def get_current_session(dt_utc: datetime = None) -> str:
        if dt_utc is None:
            dt_utc = datetime.now(timezone.utc)
            
        current_time = dt_utc.time()
        
        # Check Overlap first (highest volume/liquidity)
        if time(13, 0) <= current_time <= time(17, 0):
            return "LONDON_NY_OVERLAP"
            
        # Check London solo
        if time(8, 0) <= current_time < time(13, 0):
            return "LONDON"
            
        # Check NY solo
        if time(17, 0) < current_time <= time(22, 0):
            return "NEW_YORK"
            
        # Check Asian (Tokyo/Sydney overlap)
        if time(0, 0) <= current_time <= time(7, 0):
            return "ASIAN"
            
        return "DEAD_ZONE"
        
    @staticmethod
    def get_session_quality_score(session: str) -> int:
        """Return a score (0-100) based on historical session liquidity/quality."""
        scores = {
            "LONDON_NY_OVERLAP": 100,  # Peak volume, best for trends
            "LONDON": 80,              # Strong volume, early trends
            "NEW_YORK": 60,            # Declining volume after overlap
            "ASIAN": 30,               # Often ranging, bad for trend strategies
            "DEAD_ZONE": 10            # Avoid trading
        }
        return scores.get(session, 0)
