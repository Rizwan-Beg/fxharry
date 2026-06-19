import xgboost as xgb
import pandas as pd
import numpy as np
import os
from typing import Dict, Any

class OnlineXGBModel:
    """
    Placeholder/Online XGBoost model for Phase 2.
    In a real production environment, this loads a .json or .ubj model file.
    For this phase, it uses a lightweight online learning approach to simulate real ML predictions.
    """
    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.model = xgb.XGBClassifier(
            n_estimators=10, 
            max_depth=3, 
            learning_rate=0.1,
            objective="binary:logistic"
        )
        self.is_trained = False
        
        # Buffer for online training
        self.feature_buffer = []
        self.label_buffer = []
        
        # Attempt to load if path provided
        if model_path and os.path.exists(model_path):
            self.model.load_model(model_path)
            self.is_trained = True

    def _dummy_train_if_needed(self, feature_names):
        """Creates a dummy pre-trained state so we can predict immediately."""
        X_dummy = pd.DataFrame([
            {f: 0.1 for f in feature_names},
            {f: -0.1 for f in feature_names}
        ])
        y_dummy = pd.Series([1, 0])
        self.model.fit(X_dummy, y_dummy)
        self.is_trained = True

    def predict_proba(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Returns probabilities for BUY (1) and SELL (0).
        """
        if not features:
            return {"BUY": 0.0, "SELL": 0.0}
            
        df = pd.DataFrame([features])
        
        if not self.is_trained:
            self._dummy_train_if_needed(df.columns)
            
        # Predict probability of class 1 (BUY)
        prob_buy = self.model.predict_proba(df)[0][1]
        
        # Online learning heuristic: we append features and pseudo-labels for future retraining
        # (A real system would wait for the actual outcome n-periods later)
        if prob_buy > 0.6:
            self.feature_buffer.append(features)
            self.label_buffer.append(1)
        elif prob_buy < 0.4:
            self.feature_buffer.append(features)
            self.label_buffer.append(0)
            
        return {
            "BUY": float(prob_buy),
            "SELL": float(1.0 - prob_buy)
        }
