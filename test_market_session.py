"""
Test script for Market Session utility
"""

from datetime import datetime
import pytz
from ai_core.strategy_engine.core.market_session import MarketSession


def test_london_session():
    """Test London session detection (08:00-17:00 UTC)"""
    print("\n📍 Testing London Session (08:00-17:00 UTC)")
    
    # During London session
    london_time = datetime(2026, 2, 5, 10, 0, 0, tzinfo=pytz.UTC)
    result = MarketSession.is_session_active("london", london_time)
    assert result == True, "Failed: Should be active at 10:00 UTC"
    print(f"✅ 10:00 UTC - London session active: {result}")
    
    # Before London session
    before_london = datetime(2026, 2, 5, 7, 0, 0, tzinfo=pytz.UTC)
    result = MarketSession.is_session_active("london", before_london)
    assert result == False, "Failed: Should be inactive at 07:00 UTC"
    print(f"✅ 07:00 UTC - London session inactive: {not result}")
    
    # After London session
    after_london = datetime(2026, 2, 5, 18, 0, 0, tzinfo=pytz.UTC)
    result = MarketSession.is_session_active("london", after_london)
    assert result == False, "Failed: Should be inactive at 18:00 UTC"
    print(f"✅ 18:00 UTC - London session inactive: {not result}")


def test_newyork_session():
    """Test New York session detection (13:00-22:00 UTC)"""
    print("\n🗽 Testing New York Session (13:00-22:00 UTC)")
    
    # During New York session
    ny_time = datetime(2026, 2, 5, 15, 0, 0, tzinfo=pytz.UTC)
    result = MarketSession.is_session_active("new_york", ny_time)
    assert result == True, "Failed: Should be active at 15:00 UTC"
    print(f"✅ 15:00 UTC - New York session active: {result}")
    
    # Before New York session
    before_ny = datetime(2026, 2, 5, 12, 0, 0, tzinfo=pytz.UTC)
    result = MarketSession.is_session_active("new_york", before_ny)
    assert result == False, "Failed: Should be inactive at 12:00 UTC"
    print(f"✅ 12:00 UTC - New York session inactive: {not result}")
    
    # After New York session
    after_ny = datetime(2026, 2, 5, 23, 0, 0, tzinfo=pytz.UTC)
    result = MarketSession.is_session_active("new_york", after_ny)
    assert result == False, "Failed: Should be inactive at 23:00 UTC"
    print(f"✅ 23:00 UTC - New York session inactive: {not result}")


def test_overlap_period():
    """Test overlap period when both London and New York are active (13:00-17:00 UTC)"""
    print("\n🔄 Testing Overlap Period (13:00-17:00 UTC)")
    
    # During overlap
    overlap_time = datetime(2026, 2, 5, 14, 0, 0, tzinfo=pytz.UTC)
    result = MarketSession.is_trading_allowed(['london', 'new_york'], overlap_time)
    
    assert result['allowed'] == True, "Failed: Trading should be allowed during overlap"
    assert 'london' in result['active_sessions'], "Failed: London should be active"
    assert 'new_york' in result['active_sessions'], "Failed: New York should be active"
    
    print(f"✅ 14:00 UTC - Both sessions active:")
    print(f"   - Trading allowed: {result['allowed']}")
    print(f"   - Current session: {result['current_session']}")
    print(f"   - All active: {result['active_sessions']}")


def test_outside_hours():
    """Test when neither London nor New York is active"""
    print("\n🌙 Testing Outside Trading Hours")
    
    # 03:00 UTC - Between Tokyo and London
    outside_time = datetime(2026, 2, 5, 3, 0, 0, tzinfo=pytz.UTC)
    result = MarketSession.is_trading_allowed(['london', 'new_york'], outside_time)
    
    assert result['allowed'] == False, "Failed: Trading should not be allowed at 03:00 UTC"
    assert result['current_session'] is None, "Failed: No current session should be set"
    
    print(f"✅ 03:00 UTC - Outside trading hours:")
    print(f"   - Trading allowed: {result['allowed']}")
    print(f"   - Current session: {result['current_session']}")
    print(f"   - All active: {result['active_sessions']}")


def test_convenience_method():
    """Test the convenience method for London/New York check"""
    print("\n⚡ Testing Convenience Method")
    
    # During London session
    london_time = datetime(2026, 2, 5, 10, 0, 0, tzinfo=pytz.UTC)
    result = MarketSession.is_london_or_newyork_active(london_time)
    assert result == True, "Failed: Should return True during London hours"
    print(f"✅ 10:00 UTC - is_london_or_newyork_active(): {result}")
    
    # During New York session
    ny_time = datetime(2026, 2, 5, 20, 0, 0, tzinfo=pytz.UTC)
    result = MarketSession.is_london_or_newyork_active(ny_time)
    assert result == True, "Failed: Should return True during NY hours"
    print(f"✅ 20:00 UTC - is_london_or_newyork_active(): {result}")
    
    # Outside both sessions
    outside_time = datetime(2026, 2, 5, 3, 0, 0, tzinfo=pytz.UTC)
    result = MarketSession.is_london_or_newyork_active(outside_time)
    assert result == False, "Failed: Should return False outside hours"
    print(f"✅ 03:00 UTC - is_london_or_newyork_active(): {result}")


def test_get_current_sessions():
    """Test getting all active sessions"""
    print("\n📊 Testing Get Current Sessions")
    
    # During overlap period
    overlap_time = datetime(2026, 2, 5, 14, 0, 0, tzinfo=pytz.UTC)
    sessions = MarketSession.get_current_sessions(overlap_time)
    print(f"✅ 14:00 UTC - Active sessions: {sessions}")
    assert 'london' in sessions and 'new_york' in sessions
    
    # During only London
    london_only = datetime(2026, 2, 5, 10, 0, 0, tzinfo=pytz.UTC)
    sessions = MarketSession.get_current_sessions(london_only)
    print(f"✅ 10:00 UTC - Active sessions: {sessions}")
    assert 'london' in sessions and 'new_york' not in sessions
    
    # During only New York
    ny_only = datetime(2026, 2, 5, 20, 0, 0, tzinfo=pytz.UTC)
    sessions = MarketSession.get_current_sessions(ny_only)
    print(f"✅ 20:00 UTC - Active sessions: {sessions}")
    assert 'new_york' in sessions and 'london' not in sessions


if __name__ == "__main__":
    print("🧪 Market Session Utility Test Suite")
    print("=" * 60)
    
    try:
        test_london_session()
        test_newyork_session()
        test_overlap_period()
        test_outside_hours()
        test_convenience_method()
        test_get_current_sessions()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise
