# ai_core/strategy_engine/strategy_manager.py

from .core.feature_engine import FeatureEngine
from .strategies.apex_strategy import ApexStrategy
from .strategies.riztest_strategy import RizTestStrategy
from .strategies.ml_strategy import MLStrategy
from .strategies.smart_money_strategy import SmartMoneyStrategy

from .regime_detector import RegimeDetector
from .session_filter import SessionFilter
from .trade_scorer import TradeQualityScorer
from ai_core.data.feature_store import FeatureStore

class StrategyManager:
    def __init__(self):
        self.feature_engines = {}
        
        # Apex V1: Multi-timeframe trend-following strategy
        # RizTest: Simple test strategy for end-to-end verification
        # MLStrategy: ML-based prediction strategy
        # SMC: Smart Money Concepts (4H -> 1H -> 5M)
        self.strategies = {
            "apex": ApexStrategy(),
            "riztest": RizTestStrategy(),  # Test strategy
            "ml": MLStrategy(),
            "smc": SmartMoneyStrategy(),
        }
        
        # Track active strategies
        # Default active strategies
        self.active_strategies = {"apex"}
        self.recent_rejected_signals = []
        
        # Initialize context awareness and scoring engines
        self.regime_detector = RegimeDetector(period=14)
        self.session_filter = SessionFilter()
        self.trade_scorer = TradeQualityScorer(min_threshold=80)
        self.feature_store = FeatureStore(db_path="data/features.db")

    def activate_strategy(self, strategy_id: str) -> bool:
        """Enable a specific strategy."""
        if strategy_id in self.strategies:
            self.active_strategies.add(strategy_id)
            return True
        return False

    def deactivate_strategy(self, strategy_id: str) -> bool:
        """Disable a specific strategy."""
        if strategy_id in self.active_strategies:
            self.active_strategies.remove(strategy_id)
            return True
        return False

    def get_strategy_status(self) -> list:
        """Get status of all strategies."""
        status_list = []
        for s_id, strategy in self.strategies.items():
            status_list.append({
                "id": s_id,
                "name": strategy.__class__.__name__,
                "is_active": s_id in self.active_strategies,
                "description": getattr(strategy, "description", "No description")
            })
        return status_list

    def process_tick(self, symbol, price):
        if symbol not in self.feature_engines:
            self.feature_engines[symbol] = FeatureEngine()

        features = self.feature_engines[symbol].update_price(price)

        if not features:
            return None  # Not enough data

        signals = []
        
        # 1. Detect Context & Environment
        closes = list(self.feature_engines[symbol].prices)
        regime_data = self.regime_detector.detect_regime(closes)
        
        current_session = self.session_filter.get_current_session()
        session_score = self.session_filter.get_session_quality_score(current_session)
        
        # 1.5. LLM Macro Bias (Phase 6)
        # We read the dynamically updated macro score injected by the background task
        llm_macro_score = getattr(self, "current_macro_score", 15) 

        for name, strategy in self.strategies.items():
            # Only process if strategy is active
            if name not in self.active_strategies:
                continue
                
            # 2. Strategy generates a raw signal (Technical evaluation)
            # In Phase 2, strategies will return a 0-40 technical score. 
            # For now, we map binary signals to a 35/40 technical score.
            raw_signal = strategy.generate_signal(symbol, price, features)
            
            if raw_signal:
                technical_score = 35 
                
                # 3. Score the trade combining Technicals, Regime, Session, and LLM Bias
                scored_trade = self.trade_scorer.score_trade(
                    technical_score=technical_score,
                    regime_data=regime_data,
                    session_score=session_score,
                    llm_sentiment_score=llm_macro_score,
                    action=raw_signal['action']
                )
                
                # 4. Filter by Trade Quality Threshold
                if scored_trade['passed_threshold']:
                    raw_signal['trade_score'] = scored_trade['total_score']
                    raw_signal['score_breakdown'] = scored_trade['breakdown']
                    raw_signal['context'] = scored_trade['context']
                    
                    # Log institutional analysis attached to the signal
                    raw_signal['reason'] = f"{raw_signal.get('reason', '')} | Score: {scored_trade['total_score']}/100 | {scored_trade['context']}"
                    
                    signals.append(raw_signal)
                else:
                    raw_signal['trade_score'] = scored_trade['total_score']
                    raw_signal['reason'] = f"{raw_signal.get('reason', '')} | Rejected by Scorer. Score: {scored_trade['total_score']}/100 | {scored_trade['context']}"
                    self.recent_rejected_signals.insert(0, raw_signal)
                    if len(self.recent_rejected_signals) > 10:
                        self.recent_rejected_signals.pop()
                    
                # 5. Log all signals (both passed and rejected) to Feature Store
                self.feature_store.log_signal(
                    symbol=symbol,
                    strategy_id=name,
                    action=raw_signal['action'],
                    price=price,
                    regime_data=regime_data,
                    session_name=current_session,
                    session_score=session_score,
                    llm_score=llm_macro_score,
                    technical_score=technical_score,
                    total_score=scored_trade['total_score'],
                    passed=scored_trade['passed_threshold'],
                    raw_features=features
                )

        return signals

    def get_diagnostics(self, symbol: str) -> dict:
        """Get live diagnostics for the frontend."""
        if symbol not in self.feature_engines or not self.feature_engines[symbol].prices:
            return None
        
        closes = list(self.feature_engines[symbol].prices)
        regime = self.regime_detector.detect_regime(closes)
        session = self.session_filter.get_current_session()
        session_score = self.session_filter.get_session_quality_score(session)
        llm_score = getattr(self, "current_macro_score", 15)
        
        # Pull basic indicators
        indicators = {}
        if hasattr(self.feature_engines[symbol], "features") and self.feature_engines[symbol].features:
            features = self.feature_engines[symbol].features[-1]
            indicators = {
                'sma_10': features.get('sma_10'),
                'sma_30': features.get('sma_30'),
                'rsi_14': features.get('rsi_14'),
                'm15_bias': features.get('m15_bias', 0)
            }
            
        return {
            'regime': regime,
            'session': session,
            'session_score': session_score,
            'llm_macro_score': llm_score,
            'indicators': indicators
        }
