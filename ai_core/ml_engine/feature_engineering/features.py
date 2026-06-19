import pandas as pd
import numpy as np
from typing import Dict, Any, List

class FeatureEngineer:
    """
    Computes real-time ML features from a sequence of live candles.
    """
    def __init__(self, window_sizes: List[int] = [3, 5, 10]):
        self.window_sizes = window_sizes
        
    def compute_features(self, candles: List[Dict[str, float]]) -> Dict[str, float]:
        """
        Takes a list of chronological candles (oldest to newest) 
        and extracts predictive features.
        """
        if len(candles) < max(self.window_sizes) + 1:
            return {} # Not enough data
            
        df = pd.DataFrame(candles)
        
        features = {}
        
        # Price change
        df['returns'] = df['close'].pct_change()
        
        # Current tick stats
        features['close'] = df['close'].iloc[-1]
        features['spread_estimate'] = (df['high'].iloc[-1] - df['low'].iloc[-1])
        features['body_size'] = abs(df['close'].iloc[-1] - df['open'].iloc[-1])
        features['upper_shadow'] = df['high'].iloc[-1] - max(df['open'].iloc[-1], df['close'].iloc[-1])
        features['lower_shadow'] = min(df['open'].iloc[-1], df['close'].iloc[-1]) - df['low'].iloc[-1]
        
        # Rolling features
        for w in self.window_sizes:
            if len(df) >= w:
                features[f'ma_{w}'] = df['close'].rolling(w).mean().iloc[-1]
                features[f'volatility_{w}'] = df['returns'].rolling(w).std().iloc[-1]
                features[f'momentum_{w}'] = df['close'].iloc[-1] - df['close'].iloc[-w]
                
        # Fill NaNs with 0 (initial periods)
        features = {k: (0.0 if np.isnan(v) else v) for k, v in features.items()}
        
        return features
