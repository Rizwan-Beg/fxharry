import importlib.util
import sys
import json
import subprocess
import os
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from database.models import Strategy, AISignal
from database.database import SessionLocal
import logging
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

class StrategyManager:
    """Manages AI/ML trading strategies"""
    
    def __init__(self):
        self.loaded_strategies = {}
        self.strategy_cache = {}
    
    async def load_strategy(self, strategy_id: int) -> Optional[Any]:
        """Load a strategy module dynamically"""
        db = SessionLocal()
        try:
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                return None
            
            if strategy_id in self.loaded_strategies:
                return self.loaded_strategies[strategy_id]
            
            if strategy.strategy_type == 'python':
                return await self._load_python_strategy(strategy)
            elif strategy.strategy_type == 'cpp':
                return await self._load_cpp_strategy(strategy)
            elif strategy.strategy_type == 'ml_model':
                return await self._load_ml_model(strategy)
            
        except Exception as e:
            logger.error(f"Error loading strategy {strategy_id}: {e}")
            return None
        finally:
            db.close()
    
    async def _load_python_strategy(self, strategy: Strategy) -> Any:
        """Load Python-based strategy"""
        try:
            spec = importlib.util.spec_from_file_location(
                f"strategy_{strategy.id}", 
                strategy.file_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Instantiate the strategy class
            strategy_class = getattr(module, 'Strategy')
            strategy_instance = strategy_class(strategy.parameters or {})
            
            self.loaded_strategies[strategy.id] = strategy_instance
            return strategy_instance
            
        except Exception as e:
            logger.error(f"Error loading Python strategy: {e}")
            return None
    
    async def _load_cpp_strategy(self, strategy: Strategy) -> Any:
        """Load C++ strategy via subprocess wrapper"""
        try:
            # C++ strategies are compiled binaries that communicate via JSON
            class CppStrategyWrapper:
                def __init__(self, binary_path: str, parameters: Dict):
                    self.binary_path = binary_path
                    self.parameters = parameters
                
                def predict(self, market_data: Dict) -> Dict:
                    """Call C++ binary with market data"""
                    input_data = {
                        'market_data': market_data,
                        'parameters': self.parameters
                    }
                    
                    try:
                        result = subprocess.run(
                            [self.binary_path],
                            input=json.dumps(input_data),
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        
                        if result.returncode == 0:
                            return json.loads(result.stdout)
                        else:
                            logger.error(f"C++ strategy error: {result.stderr}")
                            return {'signal': 'HOLD', 'confidence': 0.0}
                    
                    except Exception as e:
                        logger.error(f"Error calling C++ strategy: {e}")
                        return {'signal': 'HOLD', 'confidence': 0.0}
            
            wrapper = CppStrategyWrapper(strategy.file_path, strategy.parameters or {})
            self.loaded_strategies[strategy.id] = wrapper
            return wrapper
            
        except Exception as e:
            logger.error(f"Error loading C++ strategy: {e}")
            return None
    
    async def _load_ml_model(self, strategy: Strategy) -> Any:
        """Load ML model (PyTorch, scikit-learn, etc.)"""
        try:
            import torch
            import pickle
            
            class MLModelWrapper:
                def __init__(self, model_path: str, parameters: Dict):
                    self.parameters = parameters
                    self.model = None
                    self.model_type = parameters.get('model_type', 'sklearn')
                    
                    if self.model_type == 'pytorch':
                        self.model = torch.load(model_path, map_location='cpu')
                        self.model.eval()
                    elif self.model_type == 'sklearn':
                        with open(model_path, 'rb') as f:
                            self.model = pickle.load(f)
                
                def predict(self, market_data: Dict) -> Dict:
                    """Make prediction using ML model"""
                    try:
                        # Extract features from market data
                        features = self._extract_features(market_data)
                        
                        if self.model_type == 'pytorch':
                            with torch.no_grad():
                                prediction = self.model(torch.tensor(features, dtype=torch.float32))
                                prediction = prediction.numpy()
                        else:
                            prediction = self.model.predict_proba([features])[0]
                        
                        # Convert prediction to trading signal
                        return self._prediction_to_signal(prediction)
                    
                    except Exception as e:
                        logger.error(f"ML model prediction error: {e}")
                        return {'signal': 'HOLD', 'confidence': 0.0}
                
                def _extract_features(self, market_data: Dict) -> List[float]:
                    """Extract features from market data for ML model"""
                    # This is a simplified example - customize based on your model
                    features = []
                    
                    for symbol_data in market_data.values():
                        if isinstance(symbol_data, dict):
                            features.extend([
                                symbol_data.get('close', 0),
                                symbol_data.get('volume', 0),
                                symbol_data.get('high', 0) - symbol_data.get('low', 0),  # Range
                                symbol_data.get('close', 0) - symbol_data.get('open', 0),  # Change
                            ])
                    
                    return features[:self.parameters.get('feature_count', 50)]
                
                def _prediction_to_signal(self, prediction) -> Dict:
                    """Convert model prediction to trading signal"""
                    if isinstance(prediction, (list, np.ndarray)):
                        if len(prediction) >= 3:  # [BUY, SELL, HOLD] probabilities
                            signal_idx = np.argmax(prediction)
                            signals = ['BUY', 'SELL', 'HOLD']
                            return {
                                'signal': signals[signal_idx],
                                'confidence': float(prediction[signal_idx]),
                                'probabilities': {
                                    'BUY': float(prediction[0]),
                                    'SELL': float(prediction[1]),
                                    'HOLD': float(prediction[2])
                                }
                            }
                    
                    return {'signal': 'HOLD', 'confidence': 0.0}
            
            wrapper = MLModelWrapper(strategy.file_path, strategy.parameters or {})
            self.loaded_strategies[strategy.id] = wrapper
            return wrapper
            
        except Exception as e:
            logger.error(f"Error loading ML model: {e}")
            return None
    
    async def process_strategy(self, strategy_id: int, market_data: Dict) -> Optional[Dict]:
        """Process market data through a strategy and generate signals"""
        strategy_instance = await self.load_strategy(strategy_id)
        if not strategy_instance:
            return None
        
        try:
            # Generate prediction/signal
            signal = strategy_instance.predict(market_data)
            
            if signal and signal.get('confidence', 0) > 0.1:  # Minimum confidence threshold
                # Store signal in database
                db = SessionLocal()
                try:
                    ai_signal = AISignal(
                        strategy_id=strategy_id,
                        symbol=signal.get('symbol', 'UNKNOWN'),
                        signal_type=signal.get('signal', 'HOLD'),
                        confidence=signal.get('confidence', 0.0),
                        price=signal.get('price', 0.0),
                        features=signal.get('features', {}),
                        model_output=signal
                    )
                    db.add(ai_signal)
                    db.commit()
                    
                    return {
                        'strategy_id': strategy_id,
                        'signal': signal,
                        'timestamp': datetime.now().isoformat()
                    }
                finally:
                    db.close()
            
        except Exception as e:
            logger.error(f"Error processing strategy {strategy_id}: {e}")
        
        return None
    
    def get_active_strategies(self) -> List[Strategy]:
        """Get all active strategies"""
        db = SessionLocal()
        try:
            return db.query(Strategy).filter(Strategy.is_active == True).all()
        finally:
            db.close()
    
    async def activate_strategy(self, strategy_id: int) -> bool:
        """Activate a strategy"""
        db = SessionLocal()
        try:
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if strategy:
                strategy.is_active = True
                db.commit()
                return True
            return False
        finally:
            db.close()
    
    async def deactivate_strategy(self, strategy_id: int) -> bool:
        """Deactivate a strategy"""
        db = SessionLocal()
        try:
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if strategy:
                strategy.is_active = False
                db.commit()
                # Remove from loaded strategies
                if strategy_id in self.loaded_strategies:
                    del self.loaded_strategies[strategy_id]
                return True
            return False
        finally:
            db.close()