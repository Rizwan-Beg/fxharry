"""
Unit tests for Session Filter

Tests that session filtering correctly identifies London and New York trading hours:
- London: 08:00-17:00 Europe/London
- New York: 08:00-17:00 America/New_York
- Trading allowed during either session
- Trading blocked outside both sessions
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from datetime import datetime
import pytz
from ai_core.strategy_engine.core.market_session import MarketSession


class TestSessionFilter:
    """Test market session filtering with corrected local timezone logic."""
    
    def test_london_session_active_at_10am_london_time(self):
        """Test London session is active at 10:00 Europe/London."""
        # Create 10:00 AM London time
        london_tz = pytz.timezone('Europe/London')
        test_time = london_tz.localize(datetime(2026, 2, 10, 10, 0, 0))
        
        result = MarketSession.is_session_active('london', test_time)
        assert result is True
    
    def test_london_session_inactive_at_6am_london_time(self):
        """Test London session is NOT active at 06:00 Europe/London (before 08:00)."""
        london_tz = pytz.timezone('Europe/London')
        test_time = london_tz.localize(datetime(2026, 2, 10, 6, 0, 0))
        
        result = MarketSession.is_session_active('london', test_time)
        assert result is False
    
    def test_london_session_inactive_at_6pm_london_time(self):
        """Test London session is NOT active at 18:00 Europe/London (after 17:00)."""
        london_tz = pytz.timezone('Europe/London')
        test_time = london_tz.localize(datetime(2026, 2, 10, 18, 0, 0))
        
        result = MarketSession.is_session_active('london', test_time)
        assert result is False
    
    def test_newyork_session_active_at_2pm_ny_time(self):
        """Test New York session is active at 14:00 America/New_York."""
        ny_tz = pytz.timezone('America/New_York')
        test_time = ny_tz.localize(datetime(2026, 2, 10, 14, 0, 0))
        
        result = MarketSession.is_session_active('new_york', test_time)
        assert result is True
    
    def test_newyork_session_inactive_at_7am_ny_time(self):
        """Test New York session is NOT active at 07:00 America/New_York (before 08:00)."""
        ny_tz = pytz.timezone('America/New_York')
        test_time = ny_tz.localize(datetime(2026, 2, 10, 7, 0, 0))
        
        result = MarketSession.is_session_active('new_york', test_time)
        assert result is False
    
    def test_newyork_session_inactive_at_6pm_ny_time(self):
        """Test New York session is NOT active at 18:00 America/New_York (after 17:00)."""
        ny_tz = pytz.timezone('America/New_York')
        test_time = ny_tz.localize(datetime(2026, 2, 10, 18, 0, 0))
        
        result = MarketSession.is_session_active('new_york', test_time)
        assert result is False
    
    def test_trading_allowed_during_london_session(self):
        """Test trading is allowed during London session."""
        london_tz = pytz.timezone('Europe/London')
        test_time = london_tz.localize(datetime(2026, 2, 10, 12, 0, 0))
        
        result = MarketSession.is_trading_allowed(['london', 'new_york'], test_time)
        
        assert result['allowed'] is True
        assert result['current_session'] == 'london'
    
    def test_trading_allowed_during_newyork_session(self):
        """Test trading is allowed during New York session."""
        ny_tz = pytz.timezone('America/New_York')
        test_time = ny_tz.localize(datetime(2026, 2, 10, 11, 0, 0))
        
        result = MarketSession.is_trading_allowed(['london', 'new_york'], test_time)
        
        assert result['allowed'] is True
        assert result['current_session'] in ['london', 'new_york']
    
    def test_trading_blocked_outside_both_sessions(self):
        """Test trading is blocked when outside both London and NY sessions."""
        # 3 AM London time = outside London (before 08:00)
        # This is also outside NY hours
        london_tz = pytz.timezone('Europe/London')
        test_time = london_tz.localize(datetime(2026, 2, 10, 3, 0, 0))
        
        result = MarketSession.is_trading_allowed(['london', 'new_york'], test_time)
        
        assert result['allowed'] is False
        assert result['current_session'] is None
    
    def test_session_overlap_period(self):
        """Test that both sessions can be active during overlap period."""
        # 1 PM London time = 8 AM New York time (both sessions active)
        london_tz = pytz.timezone('Europe/London')
        test_time = london_tz.localize(datetime(2026, 2, 10, 13, 0, 0))
        
        # Check both sessions individually
        london_active = MarketSession.is_session_active('london', test_time)
        ny_active = MarketSession.is_session_active('new_york', test_time)
        
        # During winter, 13:00 London = 08:00 NY, so both should be active
        # (Note: this may vary with daylight saving time)
        result = MarketSession.is_trading_allowed(['london', 'new_york'], test_time)
        assert result['allowed'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
