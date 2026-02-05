"""
Test script for RSI Reversal Strategy with Market Session Filter
"""

from datetime import datetime
import pytz
from ai_core.strategy_engine.strategies.rsi_reversal import RSIReversalStrategy


def test_rsi_during_london_session():
    """Test RSI signals are generated during London session"""
    print("\n📍 Testing RSI Strategy During London Session")
    
    strategy = RSIReversalStrategy()
    
    # Mock features with oversold RSI
    features = {"rsi_14": 25}
    
    # Simulate time during London session (10:00 UTC)
    import ai_core.strategy_engine.market_session as ms_module
    original_datetime = datetime
    
    # Mock datetime to return London session time
    class MockDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 2, 5, 10, 0, 0, tzinfo=pytz.UTC)
    
    # Temporarily replace datetime
    ms_module.datetime = MockDatetime
    
    try:
        signal = strategy.generate_signal("EUR/USD", 1.0800, features)
        
        assert signal is not None, "Failed: Should generate signal during London session"
        assert signal['signal'] == 'BUY', "Failed: Should be a BUY signal for oversold RSI"
        assert 'london' in signal['reason'].lower() or 'session' in signal['reason'].lower()
        assert signal['metadata']['session'] == 'london'
        
        print(f"✅ Signal generated during London session:")
        print(f"   - Signal: {signal['signal']}")
        print(f"   - Reason: {signal['reason']}")
        print(f"   - Session: {signal['metadata']['session']}")
        print(f"   - Active sessions: {signal['metadata']['active_sessions']}")
    finally:
        # Restore original datetime
        ms_module.datetime = original_datetime


def test_rsi_during_newyork_session():
    """Test RSI signals are generated during New York session"""
    print("\n🗽 Testing RSI Strategy During New York Session")
    
    strategy = RSIReversalStrategy()
    
    # Mock features with overbought RSI
    features = {"rsi_14": 75}
    
    # Mock datetime to return New York session time
    import ai_core.strategy_engine.market_session as ms_module
    original_datetime = datetime
    
    class MockDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 2, 5, 20, 0, 0, tzinfo=pytz.UTC)
    
    ms_module.datetime = MockDatetime
    
    try:
        signal = strategy.generate_signal("EUR/USD", 1.0800, features)
        
        assert signal is not None, "Failed: Should generate signal during New York session"
        assert signal['signal'] == 'SELL', "Failed: Should be a SELL signal for overbought RSI"
        assert 'new_york' in signal['reason'].lower() or 'session' in signal['reason'].lower()
        assert signal['metadata']['session'] == 'new_york'
        
        print(f"✅ Signal generated during New York session:")
        print(f"   - Signal: {signal['signal']}")
        print(f"   - Reason: {signal['reason']}")
        print(f"   - Session: {signal['metadata']['session']}")
        print(f"   - Active sessions: {signal['metadata']['active_sessions']}")
    finally:
        ms_module.datetime = original_datetime


def test_rsi_outside_allowed_sessions():
    """Test RSI signals are BLOCKED outside London/New York sessions"""
    print("\n🚫 Testing RSI Strategy Outside Allowed Sessions")
    
    strategy = RSIReversalStrategy()
    
    # Mock features with oversold RSI
    features = {"rsi_14": 20}
    
    # Mock datetime to return time outside London/New York (03:00 UTC)
    import ai_core.strategy_engine.market_session as ms_module
    original_datetime = datetime
    
    class MockDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 2, 5, 3, 0, 0, tzinfo=pytz.UTC)
    
    ms_module.datetime = MockDatetime
    
    try:
        signal = strategy.generate_signal("EUR/USD", 1.0800, features)
        
        assert signal is None, "Failed: Should NOT generate signal outside allowed sessions"
        
        print(f"✅ Signal correctly blocked outside trading hours (03:00 UTC)")
        print(f"   - Signal: None (as expected)")
        print(f"   - RSI was: {features['rsi_14']} (oversold, but blocked by session filter)")
    finally:
        ms_module.datetime = original_datetime


def test_rsi_during_overlap():
    """Test RSI signals during London/New York overlap period"""
    print("\n🔄 Testing RSI Strategy During Overlap Period")
    
    strategy = RSIReversalStrategy()
    
    # Mock features with oversold RSI
    features = {"rsi_14": 28}
    
    # Mock datetime to return overlap time (14:00 UTC)
    import ai_core.strategy_engine.market_session as ms_module
    original_datetime = datetime
    
    class MockDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 2, 5, 14, 0, 0, tzinfo=pytz.UTC)
    
    ms_module.datetime = MockDatetime
    
    try:
        signal = strategy.generate_signal("EUR/USD", 1.0800, features)
        
        assert signal is not None, "Failed: Should generate signal during overlap"
        assert len(signal['metadata']['active_sessions']) >= 2, "Failed: Should show multiple active sessions"
        
        print(f"✅ Signal generated during overlap period:")
        print(f"   - Signal: {signal['signal']}")
        print(f"   - Current session: {signal['metadata']['session']}")
        print(f"   - All active sessions: {signal['metadata']['active_sessions']}")
        print(f"   - Note: Both London and New York are active!")
    finally:
        ms_module.datetime = original_datetime


def test_no_signal_when_rsi_neutral():
    """Test that no signal is generated when RSI is neutral, even during trading hours"""
    print("\n⚖️ Testing RSI Strategy With Neutral RSI")
    
    strategy = RSIReversalStrategy()
    
    # Mock features with neutral RSI
    features = {"rsi_14": 50}
    
    # Mock datetime to return London session time
    import ai_core.strategy_engine.market_session as ms_module
    original_datetime = datetime
    
    class MockDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 2, 5, 10, 0, 0, tzinfo=pytz.UTC)
    
    ms_module.datetime = MockDatetime
    
    try:
        signal = strategy.generate_signal("EUR/USD", 1.0800, features)
        
        assert signal is None, "Failed: Should not generate signal for neutral RSI"
        
        print(f"✅ No signal for neutral RSI (50) even during trading hours")
        print(f"   - Signal: None (as expected)")
        print(f"   - RSI: {features['rsi_14']} (neutral, no entry condition)")
    finally:
        ms_module.datetime = original_datetime


if __name__ == "__main__":
    print("🧪 RSI Strategy with Session Filter Test Suite")
    print("=" * 70)
    
    try:
        test_rsi_during_london_session()
        test_rsi_during_newyork_session()
        test_rsi_outside_allowed_sessions()
        test_rsi_during_overlap()
        test_no_signal_when_rsi_neutral()
        
        print("\n" + "=" * 70)
        print("✅ ALL RSI STRATEGY TESTS PASSED!")
        print("=" * 70)
        print("\n💡 Key Takeaways:")
        print("   1. Signals are generated during London session (08:00-17:00 UTC)")
        print("   2. Signals are generated during New York session (13:00-22:00 UTC)")
        print("   3. Signals are BLOCKED outside these sessions")
        print("   4. Session information is included in signal metadata")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise
