"""
RIZER Strategy - Main Orchestrator
Production-grade 9-stage modular trading strategy for EUR/USD 5-minute timeframe.
"""

import time
from typing import Dict, Optional
from datetime import datetime
import numpy as np

from .config import RizerConfig, DEFAULT_CONFIG
from .stages.stage_0_kill_switch import KillSwitch, NewsEvent
from .stages.stage_1_session import SessionFilter
from .stages.stage_2_regime import RegimeFilter
from .stages.stage_3_participation import ParticipationFilter
from .stages.stage_4_directional import DirectionalBias
from .stages.stage_5_timing import TimingFilter
from .stages.stage_6_ml_edge import MLEdge
from .stages.stage_7_decision import DecisionEngine
from .stages.stage_8_risk import RiskManagement
from .stages.stage_9_monitor import TradeMonitoring
from ai_core.strategy_engine.indicators.adx import ADXIndicator
from ai_core.strategy_engine.indicators.vwap import SessionVWAP


class RizerStrategy:
    """
    RIZER - Production-grade 9-stage trading strategy.
    
    Stages:
    0. Kill Switch (hard gate)
    1. Session Filter (hard gate)
    2. Market Regime (ADX scoring)
    3. Participation (VWAP scoring)
    4. Directional Bias (EMA scoring)
    5. Timing (RSI scoring)
    6. ML Edge (statistical edge)
    7. Decision Engine (weighted aggregation)
    8. Risk Management (ATR-based sizing)
    9. Trade Monitoring (exit conditions)
    """
    
    def __init__(self, config: RizerConfig = None, account_equity: float = 10000.0):
        """
        Initialize RIZER strategy.
        
        Args:
            config: Strategy configuration
            account_equity: Account equity for position sizing
        """
        self.config = config or DEFAULT_CONFIG
        self.account_equity = account_equity
        
        # Initialize all stages
        self.stage_0 = KillSwitch(
            max_spread_pips=self.config.max_spread_pips,
            max_staleness_seconds=self.config.max_data_staleness_seconds,
            news_buffer_minutes=self.config.news_buffer_minutes
        )
        
        self.stage_1 = SessionFilter(
            allowed_sessions=self.config.allowed_sessions
        )
        
        self.stage_2 = RegimeFilter()
        self.stage_3 = ParticipationFilter()
        self.stage_4 = DirectionalBias()
        self.stage_5 = TimingFilter()
        self.stage_6 = MLEdge()
        
        self.stage_7 = DecisionEngine(
            weight_regime=self.config.weight_regime,
            weight_participation=self.config.weight_participation,
            weight_trend=self.config.weight_trend,
            weight_timing=self.config.weight_timing,
            weight_ml_edge=self.config.weight_ml_edge,
            long_threshold=self.config.long_threshold,
            short_threshold=self.config.short_threshold
        )
        
        self.stage_8 = RiskManagement(
            atr_stop_multiplier=self.config.atr_stop_multiplier,
            risk_reward_ratio=self.config.risk_reward_ratio,
            risk_per_trade_percent=self.config.risk_per_trade_percent
        )
        
        self.stage_9 = TradeMonitoring()
        
        # Initialize indicators
        self.adx_indicator = ADXIndicator(period=14)
        self.vwap_indicator = SessionVWAP(session='london')  # Will auto-switch
        
        # Price history for ADX (needs high, low, close)
        self.price_history = {
            'high': [],
            'low': [],
            'close': []
        }
        self.max_history = 200
        
        # Current position tracking
        self.current_position = None  # 'LONG', 'SHORT', or None
        self.entry_price = None
    
    def generate_signal(self, symbol: str, price: float, features: dict,
                       spread: float = 1.0, volume: float = 1000.0,
                       high: float = None, low: float = None,
                       data_timestamp: datetime = None,
                       news_events: list = None) -> Optional[Dict]:
        """
        Generate trading signal by orchestrating all 9 stages.
        
        Args:
            symbol: Trading symbol (should be EUR/USD)
            price: Current price (close)
            features: Feature dict from feature engine
            spread: Current spread in pips
            volume: Current volume
            high: High price of bar
            low: Low price of bar
            data_timestamp: Timestamp of data
            news_events: List of NewsEvent objects
            
        Returns:
            Signal dict or None
        """
        if data_timestamp is None:
            data_timestamp = datetime.now()
        
        # Use price as high/low if not provided
        if high is None:
            high = price
        if low is None:
            low = price
        
        # Update price history for ADX
        self.price_history['high'].append(high)
        self.price_history['low'].append(low)
        self.price_history['close'].append(price)
        
        # Trim history
        if len(self.price_history['high']) > self.max_history:
            self.price_history['high'].pop(0)
            self.price_history['low'].pop(0)
            self.price_history['close'].pop(0)
        
        # Calculate ADX
        adx = None
        if len(self.price_history['high']) >= 15:
            highs = np.array(self.price_history['high'])
            lows = np.array(self.price_history['low'])
            closes = np.array(self.price_history['close'])
            adx = self.adx_indicator.calculate(highs, lows, closes)
        
        # Update VWAP
        vwap = self.vwap_indicator.update(high, low, price, volume, data_timestamp)
        
        # ================== STAGE 0: KILL SWITCH ==================
        kill_switch_result = self.stage_0.evaluate(
            spread=spread,
            data_timestamp=data_timestamp,
            news_events=news_events
        )
        
        if kill_switch_result['kill_switch']:
            # Hard gate failed - abort
            return None
        
        # ================== STAGE 1: SESSION FILTER ==================
        session_result = self.stage_1.evaluate()
        
        if not session_result['session_allowed']:
            # Hard gate failed - abort
            return None
        
        # ================== CHECK FOR EXITS (if in position) ==================
        if self.current_position is not None:
            exit_result = self.stage_9.evaluate(
                position_side=self.current_position,
                price=price,
                vwap=vwap,
                ema_20=features.get('ema_20'),
                ema_50=features.get('ema_50'),
                rsi=features.get('rsi_14'),
                entry_price=self.entry_price
            )
            
            if exit_result['should_exit']:
                # Generate exit signal
                exit_signal = {
                    'symbol': symbol,
                    'signal': 'EXIT',
                    'position': self.current_position,
                    'reason': f"{exit_result['exit_reason']} - closing {self.current_position} position",
                    'strategy_id': 'RIZER',
                    'timestamp': int(time.time() * 1000),
                    'metadata': {
                        'exit_conditions': exit_result['exit_conditions'],
                        'entry_price': self.entry_price,
                        'current_price': price
                    }
                }
                
                # Reset position
                self.current_position = None
                self.entry_price = None
                self.stage_9.reset_position_state(self.current_position)
                
                return exit_signal
        
        # ================== STAGES 2-6: SCORING ==================
        regime_result = self.stage_2.evaluate(adx)
        participation_result = self.stage_3.evaluate(price, vwap, features.get('atr_14'))
        directional_result = self.stage_4.evaluate(
            features.get('ema_20'),
            features.get('ema_50'),
            features.get('ema_100')
        )
        timing_result = self.stage_5.evaluate(features.get('rsi_14'))
        ml_edge_result = self.stage_6.evaluate(
            regime_result['regime_score'],
            participation_result['participation_score'],
            directional_result['trend_score'],
            timing_result['timing_score']
        )
        
        # ================== STAGE 7: DECISION ENGINE ==================
        decision_result = self.stage_7.evaluate(
            regime_result['regime_score'],
            participation_result['participation_score'],
            directional_result['trend_score'],
            timing_result['timing_score'],
            ml_edge_result['ml_edge_score']
        )
        
        if decision_result['signal'] is None:
            # No trade signal
            return None
        
        # ================== STAGE 8: RISK MANAGEMENT ==================
        risk_result = self.stage_8.evaluate(
            atr=features.get('atr_14'),
            account_equity=self.account_equity,
            signal=decision_result['signal'],
            current_price=price
        )
        
        # Build final signal
        signal = {
            'symbol': symbol,
            'signal': decision_result['signal'],  # 'LONG' or 'SHORT'
            'reason': self._build_reason(decision_result, regime_result, participation_result,
                                         directional_result, timing_result, session_result),
            'confidence': abs(decision_result['final_score']),
            'strategy_id': 'RIZER',
            'timestamp': int(time.time() * 1000),
            'metadata': {
                'final_score': decision_result['final_score'],
                'breakdown': decision_result['breakdown'],
                'regime': regime_result,
                'participation': participation_result,
                'directional': directional_result,
                'timing': timing_result,
                'ml_edge': ml_edge_result,
                'risk': risk_result,
                'session': session_result['current_session'],
                'adx': adx,
                'vwap': vwap
            }
        }
        
        # Update position tracking
        self.current_position = decision_result['signal']
        self.entry_price = price
        
        return signal
    
    def _build_reason(self, decision, regime, participation, directional, timing, session):
        """Build human-readable reason for signal."""
        signal = decision['signal']
        score = decision['final_score']
        
        components = []
        
        # Regime
        components.append(f"{regime['regime_type']} (ADX: {regime['adx_value']:.1f})")
        
        # Directional
        components.append(f"{directional['directional_bias']} bias")
        
        # Participation
        if participation['participation_type'] != 'UNKNOWN':
            components.append(f"{participation['participation_type']}")
        
        # Timing
        if timing['rsi_regime'] != 'NEUTRAL':
            components.append(f"RSI {timing['rsi_regime']}")
        
        reason = f"{signal} signal (score: {score:.2f}) - {', '.join(components)} during {session['current_session'].upper()} session"
        
        return reason
