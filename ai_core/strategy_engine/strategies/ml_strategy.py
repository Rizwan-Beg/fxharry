import time
from typing import Dict, Any, List, Optional
from ai_core.ml_engine.feature_engineering.features import FeatureEngineer
from ai_core.ml_engine.models.xgb_model import OnlineXGBModel
from ai_core.core.logger import get_logger

logger = get_logger(__name__)

class MLStrategy:
    """
    Machine Learning Strategy for Phase 2.
    Uses feature engineering and an XGBoost model to predict market direction.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.id = "ml_xgb"
        self.feature_eng = FeatureEngineer(window_sizes=[3, 5, 10])
        self.model = OnlineXGBModel()
        
        # We need a history of candles to extract features
        self.candle_history: List[Dict[str, Any]] = []
        self.max_history = 20

    async def initialize(self) -> bool:
        logger.info("Initializing ML Strategy Engine (XGBoost)...")
        return True

    async def analyze(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Accumulate 1m candles for feature engineering
        candles_dict = market_data.get("candles", {})
        m1_candle = candles_dict.get("1m")
        
        if not m1_candle:
            return None
            
        # Add to history if it's a new candle (checking timestamp/close to avoid duplicates)
        # Simplified: we just keep the latest state
        if not self.candle_history or self.candle_history[-1].get("timestamp") != m1_candle.get("timestamp"):
            self.candle_history.append(m1_candle)
            if len(self.candle_history) > self.max_history:
                self.candle_history.pop(0)
                
        # Need at least 11 candles for a 10-period rolling window feature
        if len(self.candle_history) < 11:
            return None

        # 1. Feature Engineering
        features = self.feature_eng.compute_features(self.candle_history)
        if not features:
            return None

        # 2. Model Prediction
        probs = self.model.predict_proba(features)
        
        buy_prob = probs.get("BUY", 0.0)
        sell_prob = probs.get("SELL", 0.0)
        
        # 3. Signal Generation Logic
        confidence_threshold = 0.65
        
        if buy_prob > confidence_threshold:
            action = "BUY"
            conf = buy_prob
        elif sell_prob > confidence_threshold:
            action = "SELL"
            conf = sell_prob
        else:
            return None # No strong signal
            
        return {
            "strategy_id": self.id,
            "symbol": market_data.get("symbol", "EURUSD"),
            "action": action,
            "confidence": conf,
            "reason": f"ML model probability: {conf:.1%}",
            "features": features, # We can pass features down for debugging
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        }
