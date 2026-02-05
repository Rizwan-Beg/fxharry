"""
Stage 0: Global Kill Switch
Hard gate for data quality and external risk events.
"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
import pytz


class NewsEvent:
    """Represents a high-impact news event."""
    
    def __init__(self, timestamp: datetime, currency: str, impact: str, title: str = ""):
        self.timestamp = timestamp
        self.currency = currency.upper()
        self.impact = impact.upper()
        self.title = title


class KillSwitch:
    """
    Stage 0: Global Kill Switch
    
    Checks:
    - Spread threshold
    - Data staleness
    - High-impact news events
    """
    
    def __init__(self, max_spread_pips: float = 2.0, 
                 max_staleness_seconds: int = 30,
                 news_buffer_minutes: int = 30):
        """
        Initialize kill switch.
        
        Args:
            max_spread_pips: Maximum allowed spread in pips
            max_staleness_seconds: Maximum data age in seconds
            news_buffer_minutes: Minutes to avoid trading around news
        """
        self.max_spread_pips = max_spread_pips
        self.max_staleness_seconds = max_staleness_seconds
        self.news_buffer_minutes = news_buffer_minutes
    
    def evaluate(self, spread: float, data_timestamp: datetime, 
                 news_events: Optional[List[NewsEvent]] = None,
                 current_time: Optional[datetime] = None) -> Dict:
        """
        Evaluate kill switch conditions.
        
        Args:
            spread: Current bid-ask spread in pips
            data_timestamp: Timestamp of the latest data
            news_events: List of upcoming/recent news events
            current_time: Current time (defaults to now)
            
        Returns:
            {
                'kill_switch': bool,
                'reason': str,
                'checks': dict
            }
        """
        if current_time is None:
            current_time = datetime.now(pytz.UTC)
        
        # Ensure timestamps are timezone-aware
        if current_time.tzinfo is None:
            current_time = pytz.UTC.localize(current_time)
        if data_timestamp.tzinfo is None:
            data_timestamp = pytz.UTC.localize(data_timestamp)
        
        checks = {}
        reasons = []
        
        # Check 1: Spread
        spread_ok = spread <= self.max_spread_pips
        checks['spread'] = {'pass': spread_ok, 'value': spread, 'limit': self.max_spread_pips}
        if not spread_ok:
            reasons.append(f"Spread too wide: {spread:.2f} pips > {self.max_spread_pips} pips")
        
        # Check 2: Data staleness
        data_age = (current_time - data_timestamp).total_seconds()
        staleness_ok = data_age <= self.max_staleness_seconds
        checks['staleness'] = {'pass': staleness_ok, 'age_seconds': data_age, 
                              'limit': self.max_staleness_seconds}
        if not staleness_ok:
            reasons.append(f"Data stale: {data_age:.1f}s > {self.max_staleness_seconds}s")
        
        # Check 3: News events
        news_ok = True
        if news_events:
            news_ok, news_reason = self._check_news_events(news_events, current_time)
            checks['news'] = {'pass': news_ok, 'reason': news_reason}
            if not news_ok:
                reasons.append(news_reason)
        else:
            checks['news'] = {'pass': True, 'reason': 'No news events'}
        
        # Aggregate
        kill_switch = not (spread_ok and staleness_ok and news_ok)
        reason = '; '.join(reasons) if reasons else 'All checks passed'
        
        return {
            'kill_switch': kill_switch,
            'reason': reason,
            'checks': checks
        }
    
    def _check_news_events(self, news_events: List[NewsEvent], 
                          current_time: datetime) -> tuple[bool, str]:
        """
        Check if any high-impact news events are within buffer window.
        
        Returns:
            (is_safe, reason)
        """
        buffer = timedelta(minutes=self.news_buffer_minutes)
        
        for event in news_events:
            # Ensure event timestamp is timezone-aware
            event_time = event.timestamp
            if event_time.tzinfo is None:
                event_time = pytz.UTC.localize(event_time)
            
            # Check if event is within buffer window
            time_diff = abs((event_time - current_time).total_seconds())
            
            if time_diff <= buffer.total_seconds():
                # Check if it's high impact for EUR or USD
                if event.impact == 'HIGH' and event.currency in ['EUR', 'USD']:
                    return False, f"High-impact {event.currency} news within {self.news_buffer_minutes}min"
        
        return True, 'No high-impact news nearby'
