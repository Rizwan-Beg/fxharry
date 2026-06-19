import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from typing import Dict, Optional
from ai_core.strategy_engine.strategy_manager import StrategyManager
from ai_core.risk_manager.risk_manager import RiskManager
from ai_core.core.logger import get_logger

# Mute noisy logs for the test
import logging
logging.getLogger().setLevel(logging.CRITICAL)

class ForceTestStrategy:
    """A dummy strategy that always outputs a signal to test the scoring pipeline"""
    def __init__(self):
        self.description = "Always fires for testing pipeline"
        
    def generate_signal(self, symbol: str, price: float, features: dict) -> Optional[Dict]:
        return {
            'action': 'BUY',
            'symbol': symbol,
            'price': price,
            'reason': 'Pipeline Verification Test',
            'confidence': 0.95
        }

def test_pipeline():
    print("="*60)
    print("🧪 TESTING END-TO-END SCORING & RISK PIPELINE")
    print("="*60)
    
    print("\n[1] Initializing Core Engines...")
    strategy_manager = StrategyManager()
    strategy_manager.trade_scorer.min_threshold = 0  # Lower threshold to see everything!
    risk_manager = RiskManager()
    
    # Mock database calls to avoid Postgres connection errors during testing
    risk_manager._get_daily_pnl = lambda: 0.0
    risk_manager._calculate_correlation_exposure = lambda s, a, q: 0.0
    risk_manager._calculate_current_drawdown = lambda: 0.0
    
    # Inject our forced strategy to ensure we get a signal to test the scorers
    strategy_manager.strategies['force_test'] = ForceTestStrategy()
    strategy_manager.active_strategies = {'force_test'}
    
    print("\n[2] Simulating Market Data (Feeding 100 ticks to build Regime Data and Features)...")
    symbol = "EURUSD"
    base_price = 1.1000
    
    signals = []
    # Feed 100 prices to warm up the RegimeDetector and FeatureEngine
    for i in range(100):
        price = base_price + (i * 0.0001)  # Simulate an uptrend
        signals = strategy_manager.process_tick(symbol, price)
        
    print("\n[3] Context & Environment Detection Evaluated:")
    # Pulling the internal state to show the user what happened
    closes = list(strategy_manager.feature_engines[symbol].prices)
    regime = strategy_manager.regime_detector.detect_regime(closes)
    session = strategy_manager.session_filter.get_current_session()
    
    print(f"  • Regime Detected: {regime['regime']} (Trend Strength: {regime.get('trend_strength', 0):.2f})")
    print(f"  • Current Session: {session}")
    print(f"  • LLM Macro Bias Score: {getattr(strategy_manager, 'current_macro_score', 15)}")
    
    if not signals:
        print("\n❌ Pipeline failed: No signal was generated or signal was filtered out by Trade Scorer.")
        print("Note: The TradeQualityScorer requires a minimum score of 80 to pass.")
        return
        
    signal = signals[-1]  # Get the latest processed signal
    
    print("\n[4] Trade Quality Scoring Evaluated:")
    print(f"  • Raw Signal Generated : {signal['action']} @ {signal['price']:.5f}")
    print(f"  • Total Trade Score    : {signal['trade_score']}/100")
    print(f"  • Context Attached     : {signal['context']}")
    print("\n  Score Breakdown:")
    for key, value in signal['score_breakdown'].items():
        print(f"    - {key}: {value}")
        
    print("\n[5] Risk Management Evaluated:")
    # We dynamically calculate position size based on the trade score!
    pos_sizing = risk_manager.calculate_position_size(
        symbol=signal['symbol'], 
        entry_price=signal['price'], 
        stop_loss=signal['price'] * 0.99, # 1% simulated stop
        account_value=100000,
        trade_score=signal['trade_score']
    )
    
    print(f"  • Calculated Risk : {pos_sizing.get('risk_percent', 0) * 100}% of account (Based on trade score)")
    print(f"  • Target Quantity : {pos_sizing.get('quantity', 0):.2f} units")
    
    risk_assessment = risk_manager.assess_trade_risk(
        symbol=signal['symbol'],
        action=signal['action'],
        quantity=pos_sizing.get('quantity', 1000),
        entry_price=signal['price'],
        account_value=100000
    )
    
    print(f"  • Final Risk Level: {risk_assessment.get('risk_level')}")
    
    if risk_assessment.get('approved'):
        print("\n✅ PIPELINE SUCCESS: Trade passed all quality scores and risk checks! Ready for Execution.")
    else:
        print("\n❌ PIPELINE HALT: Trade was rejected by Risk Management.")
        for warning in risk_assessment.get('warnings', []):
            print(f"  - WARNING: {warning}")

if __name__ == "__main__":
    test_pipeline()
