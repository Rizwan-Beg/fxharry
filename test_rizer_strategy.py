"""
Comprehensive test suite for RIZER strategy.
Tests each stage independently and the full integration.
"""

import sys
import numpy as np
from datetime import datetime, timedelta
import pytz

# Import all stages from new location
from ai_core.strategy_engine.strategies.rizer_eurusd.stages.stage_0_kill_switch import KillSwitch, NewsEvent
from ai_core.strategy_engine.strategies.rizer_eurusd.stages.stage_1_session import SessionFilter
from ai_core.strategy_engine.strategies.rizer_eurusd.stages.stage_2_regime import RegimeFilter
from ai_core.strategy_engine.strategies.rizer_eurusd.stages.stage_3_participation import ParticipationFilter
from ai_core.strategy_engine.strategies.rizer_eurusd.stages.stage_4_directional import DirectionalBias
from ai_core.strategy_engine.strategies.rizer_eurusd.stages.stage_5_timing import TimingFilter
from ai_core.strategy_engine.strategies.rizer_eurusd.stages.stage_6_ml_edge import MLEdge
from ai_core.strategy_engine.strategies.rizer_eurusd.stages.stage_7_decision import DecisionEngine
from ai_core.strategy_engine.strategies.rizer_eurusd.stages.stage_8_risk import RiskManagement
from ai_core.strategy_engine.strategies.rizer_eurusd.stages.stage_9_monitor import TradeMonitoring

# Import indicators from shared location
from ai_core.strategy_engine.indicators.adx import calculate_adx
from ai_core.strategy_engine.indicators.vwap import calculate_vwap

# Import main strategy
from ai_core.strategy_engine.strategies.rizer import RIZER


def test_stage_0_kill_switch():
    """Test Stage 0: Kill Switch"""
    print("\n🔴 Testing Stage 0: Kill Switch")
    
    kill_switch = KillSwitch(max_spread_pips=2.0)
    
    # Test 1: Normal conditions - should pass
    result = kill_switch.evaluate(
        spread=1.5,
        data_timestamp=datetime.now(pytz.UTC)
    )
    assert result['kill_switch'] == False, f"Should pass with normal spread"
    print("✅ Test 1: Normal conditions passed")
    
    # Test 2: Wide spread - should fail
    result = kill_switch.evaluate(
        spread=3.0,
        data_timestamp=datetime.now(pytz.UTC)
    )
    assert result['kill_switch'] == True, "Should fail with wide spread"
    print("✅ Test 2: Wide spread correctly rejected")
    
    # Test 3: Stale data - should fail
    old_timestamp = datetime.now(pytz.UTC) - timedelta(seconds=60)
    result = kill_switch.evaluate(
        spread=1.5,
        data_timestamp=old_timestamp
    )
    assert result['kill_switch'] == True, "Should fail with stale data"
    print("✅ Test 3: Stale data correctly rejected")
    
    # Test 4: High-impact news - should fail
    news_event = NewsEvent(
        timestamp=datetime.now(pytz.UTC),
        currency="USD",
        impact="HIGH",
        title="NFP Report"
    )
    result = kill_switch.evaluate(
        spread=1.5,
        data_timestamp=datetime.now(pytz.UTC),
        news_events=[news_event]
    )
    assert result['kill_switch'] == True, "Should fail with high-impact news"
    print("✅ Test 4: High-impact news correctly rejected")


def test_stage_1_session():
    """Test Stage 1: Session Filter"""
    print("\n🕐 Testing Stage 1: Session Filter")
    
    session_filter = SessionFilter(allowed_sessions=['london', 'new_york'])
    
    # Test during London session (10:00 UTC)
    london_time = datetime(2026, 2, 5, 10, 0, 0, tzinfo=pytz.UTC)
    result = session_filter.evaluate(london_time)
    assert result['session_allowed'] == True, "Should allow London session"
    assert 'london' in result['current_session']
    print("✅ London session allowed")
    
    # Test outside sessions (3:00 UTC)
    outside_time = datetime(2026, 2, 5, 3, 0, 0, tzinfo=pytz.UTC)
    result = session_filter.evaluate(outside_time)
    assert result['session_allowed'] == False, "Should block outside sessions"
    print("✅ Outside sessions correctly blocked")


def test_stage_2_regime():
    """Test Stage 2: Market Regime"""
    print("\n📊 Testing Stage 2: Market Regime (ADX)")
    
    regime_filter = RegimeFilter()
    
    # Test choppy market (ADX < 15)
    result = regime_filter.evaluate(adx=12)
    assert result['regime_score'] == 0.0
    assert result['regime_type'] == 'CHOPPY'
    print(f"✅ Choppy market: score={result['regime_score']}")
    
    # Test strong trend (ADX > 30)
    result = regime_filter.evaluate(adx=35)
    assert result['regime_score'] == 0.9
    assert result['regime_type'] == 'STRONG_TREND'
    print(f"✅ Strong trend: score={result['regime_score']}")


def test_stage_3_participation():
    """Test Stage 3: Participation Filter (VWAP)"""
    print("\n💵 Testing Stage 3: Participation (VWAP)")
    
    participation_filter = ParticipationFilter()
    
    vwap = 1.0800
    atr = 0.0020
    
    # Test price above VWAP
    result = participation_filter.evaluate(price=1.0810, vwap=vwap, atr=atr)
    assert result['participation_score'] > 0, "Should be positive above VWAP"
    print(f"✅ Above VWAP: score={result['participation_score']:.2f}")
    
    # Test price extended from VWAP
    result = participation_filter.evaluate(price=1.0830, vwap=vwap, atr=atr)  # >1 ATR away
    assert result['participation_score'] < 0, "Should be negative when extended"
    print(f"✅ Extended from VWAP: score={result['participation_score']:.2f}")


def test_stage_4_directional():
    """Test Stage 4: Directional Bias (EMA)"""
    print("\n📈 Testing Stage 4: Directional Bias (EMA)")
    
    directional_bias = DirectionalBias()
    
    # Test LONG alignment
    result = directional_bias.evaluate(ema_20=1.0820, ema_50=1.0810, ema_100=1.0800)
    assert result['directional_bias'] == 'LONG'
    assert result['ema_alignment'] == True
    assert result['trend_score'] > 0
    print(f"✅ LONG alignment: score={result['trend_score']:.2f}")
    
    # Test SHORT alignment
    result = directional_bias.evaluate(ema_20=1.0800, ema_50=1.0810, ema_100=1.0820)
    assert result['directional_bias'] == 'SHORT'
    assert result['trend_score'] < 0
    print(f"✅ SHORT alignment: score={result['trend_score']:.2f}")
    
    # Test NEUTRAL
    result = directional_bias.evaluate(ema_20=1.0810, ema_50=1.0800, ema_100=1.0820)
    assert result['directional_bias'] == 'NEUTRAL'
    assert result['trend_score'] == 0.0
    print(f"✅ NEUTRAL: score={result['trend_score']:.2f}")


def test_stage_5_timing():
    """Test Stage 5: Timing Filter (RSI)"""
    print("\n⏱️  Testing Stage 5: Timing (RSI)")
    
    timing_filter = TimingFilter()
    
    # Test oversold
    result = timing_filter.evaluate(rsi=25)
    assert result['timing_score'] == 0.5
    assert result['rsi_regime'] == 'OVERSOLD'
    print(f"✅ Oversold: score={result['timing_score']}")
    
    # Test overbought
    result = timing_filter.evaluate(rsi=75)
    assert result['timing_score'] == -0.5
    assert result['rsi_regime'] == 'OVERBOUGHT'
    print(f"✅ Overbought: score={result['timing_score']}")


def test_stage_6_ml_edge():
    """Test Stage 6: ML Edge"""
    print("\n🤖 Testing Stage 6: ML Edge")
    
    ml_edge = MLEdge()
    
    # Test placeholder (should return 0.0)
    result = ml_edge.evaluate(
        regime_score=0.6,
        participation_score=0.5,
        trend_score=0.7,
        timing_score=0.3
    )
    assert result['ml_edge_score'] == 0.0, "Placeholder should return 0.0"
    print(f"✅ ML Edge placeholder: score={result['ml_edge_score']}")


def test_stage_7_decision():
    """Test Stage 7: Decision Engine"""
    print("\n🎯 Testing Stage 7: Decision Engine")
    
    decision_engine = DecisionEngine()
    
    # Test LONG signal
    result = decision_engine.evaluate(
        regime_score=0.6,      # 0.09
        participation_score=0.7,  # 0.175
        trend_score=0.8,       # 0.16
        timing_score=0.3,      # 0.03
        ml_edge_score=0.0      # 0.0
    )
    # Total: 0.455 > 0.35 → LONG
    assert result['signal'] == 'LONG', f"Should be LONG, got {result['signal']}"
    print(f"✅ LONG signal: final_score={result['final_score']:.3f}")
    
    # Test NO TRADE
    result = decision_engine.evaluate(
        regime_score=0.3,
        participation_score=0.0,
        trend_score=0.2,
        timing_score=0.0,
        ml_edge_score=0.0
    )
    assert result['signal'] is None, "Should be NO TRADE"
    print(f"✅ NO TRADE: final_score={result['final_score']:.3f}")


def test_stage_8_risk():
    """Test Stage 8: Risk Management"""
    print("\n💰 Testing Stage 8: Risk Management")
    
    risk_mgmt = RiskManagement()
    
    # Test position sizing
    result = risk_mgmt.evaluate(
        atr=0.0020,
        account_equity=10000.0,
        signal='LONG'
    )
    
    assert result['stop_loss_pips'] > 0
    assert result['take_profit_pips'] == result['stop_loss_pips'] * 2.0
    assert result['position_size'] > 0
    print(f"✅ Risk params: SL={result['stop_loss_pips']:.4f}, TP={result['take_profit_pips']:.4f}, Size={result['position_size']:.2f}")


def test_stage_9_monitoring():
    """Test Stage 9: Trade Monitoring"""
    print("\n👁️  Testing Stage 9: Trade Monitoring")
    
    monitor = TradeMonitoring()
    
    # Test LONG position with structure break
    result = monitor.evaluate(
        position_side='LONG',
        price=1.0810,
        vwap=1.0805,
        ema_20=1.0800,  # EMA20 < EMA50 → structure break
        ema_50=1.0810,
        rsi=50
    )
    
    assert result['should_exit'] == True
    assert 'STRUCTURE_BREAK' in result['exit_reason']
    print(f"✅ Exit signal: {result['exit_reason']}")


def test_adx_indicator():
    """Test ADX indicator calculation"""
    print("\n📐 Testing ADX Indicator")
    
    # Generate sample price data
    np.random.seed(42)
    n = 50
    close = np.cumsum(np.random.randn(n) * 0.01) + 1.0800
    high = close + np.random.rand(n) * 0.001
    low = close - np.random.rand(n) * 0.001
    
    adx = calculate_adx(high, low, close, period=14)
    
    assert adx is not None, "ADX should be calculated"
    assert 0 <= adx <= 100, f"ADX should be between 0-100, got {adx}"
    print(f"✅ ADX calculated: {adx:.2f}")


def test_vwap_indicator():
    """Test VWAP indicator calculation"""
    print("\n📊 Testing VWAP Indicator")
    
    prices = np.array([1.0800, 1.0805, 1.0810, 1.0808, 1.0812])
    volumes = np.array([1000, 1200, 800, 1500, 900])
    
    vwap = calculate_vwap(prices, volumes)
    
    assert vwap is not None, "VWAP should be calculated"
    assert vwap > 0, "VWAP should be positive"
    print(f"✅ VWAP calculated: {vwap:.4f}")


def test_full_integration():
    """Test full RIZER strategy integration"""
    print("\n🎬 Testing Full RIZER Integration")
    
    strategy = RIZER(account_equity=10000.0)
    
    # Create bullish features
    features = {
        'ema_20': 1.0820,
        'ema_50': 1.0810,
        'ema_100': 1.0800,
        'rsi_14': 35,  # Slight pullback
        'atr_14': 0.0020
    }
    
    # Generate signal during London session
    import ai_core.strategy_engine.core.market_session as ms_module
    from datetime import datetime
    
    class MockDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 2, 5, 10, 0, 0, tzinfo=pytz.UTC)
    
    original_datetime = ms_module.datetime
    ms_module.datetime = MockDatetime
    
    try:
        signal = strategy.generate_signal(
            symbol="EUR/USD",
            price=1.0815,
            features=features
        )
        
        if signal:
            print(f"✅ Signal generated: {signal['signal']}")
            print(f"   Reason: {signal['reason']}")
            print(f"   Confidence: {signal['confidence']:.2f}")
            print(f"   Final Score: {signal['metadata']['final_score']:.3f}")
        else:
            print("ℹ️  No signal (may need stronger conditions)")
    finally:
        ms_module.datetime = original_datetime


if __name__ == "__main__":
    print("="* 70)
    print("🧪 RIZER STRATEGY TEST SUITE")
    print("=" * 70)
    
    try:
        test_stage_0_kill_switch()
        test_stage_1_session()
        test_stage_2_regime()
        test_stage_3_participation()
        test_stage_4_directional()
        test_stage_5_timing()
        test_stage_6_ml_edge()
        test_stage_7_decision()
        test_stage_8_risk()
        test_stage_9_monitoring()
        test_adx_indicator()
        test_vwap_indicator()
        test_full_integration()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
