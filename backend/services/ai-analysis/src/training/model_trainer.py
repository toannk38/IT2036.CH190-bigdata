import logging
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pymongo import MongoClient
from ..models.ensemble_model import EnsembleModel
from ..features.feature_calculator import FeatureCalculator

logger = logging.getLogger(__name__)

class ModelTrainer:
    """Model training and management system"""
    
    def __init__(self, mongodb_uri: str = "mongodb://localhost:27017"):
        self.mongodb_uri = mongodb_uri
        self.feature_calculator = FeatureCalculator()
        self.models = {}
        self.model_versions = {}
        
    def train_model_for_symbol(self, symbol: str, retrain: bool = False) -> Dict[str, Any]:
        """Train model for a specific stock symbol"""
        try:
            logger.info(f"Training model for symbol: {symbol}")
            
            # Check if model exists and is recent
            if not retrain and self._is_model_recent(symbol):
                logger.info(f"Recent model exists for {symbol}, skipping training")
                return {'status': 'skipped', 'reason': 'recent_model_exists'}
            
            # Fetch training data
            training_data = self._fetch_training_data(symbol)
            
            if len(training_data) < 50:
                logger.warning(f"Insufficient data for {symbol}: {len(training_data)} records")
                return {'status': 'failed', 'reason': 'insufficient_data'}
            
            # Initialize and train ensemble model
            model = EnsembleModel()
            training_success = model.fit(training_data)
            
            if not training_success:
                logger.error(f"Model training failed for {symbol}")
                return {'status': 'failed', 'reason': 'training_failed'}
            
            # Save model
            model_info = self._save_model(symbol, model, training_data)
            
            # Update model registry
            self.models[symbol] = model
            self.model_versions[symbol] = model_info['version']
            
            logger.info(f"Model training completed for {symbol}")
            
            return {
                'status': 'success',
                'symbol': symbol,
                'model_version': model_info['version'],
                'training_data_size': len(training_data),
                'model_info': model_info
            }
            
        except Exception as e:
            logger.error(f"Model training failed for {symbol}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def batch_train_models(self, symbols: List[str]) -> Dict[str, Any]:
        """Train models for multiple symbols"""
        results = {}
        
        for symbol in symbols:
            try:
                result = self.train_model_for_symbol(symbol)
                results[symbol] = result
                
                # Log progress
                if result['status'] == 'success':
                    logger.info(f"✅ {symbol}: Training successful")
                else:
                    logger.warning(f"⚠️ {symbol}: {result.get('reason', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"❌ {symbol}: Training error - {e}")
                results[symbol] = {'status': 'error', 'error': str(e)}
        
        # Summary
        successful = sum(1 for r in results.values() if r['status'] == 'success')
        total = len(symbols)
        
        logger.info(f"Batch training completed: {successful}/{total} successful")
        
        return {
            'summary': {
                'total_symbols': total,
                'successful': successful,
                'failed': total - successful,
                'success_rate': successful / total if total > 0 else 0
            },
            'results': results
        }
    
    def get_model(self, symbol: str) -> Optional[EnsembleModel]:
        """Get trained model for symbol"""
        if symbol in self.models:
            return self.models[symbol]
        
        # Try to load from disk
        loaded_model = self._load_model(symbol)
        if loaded_model:
            self.models[symbol] = loaded_model
            return loaded_model
        
        return None
    
    def _fetch_training_data(self, symbol: str, limit: int = 200) -> List[Dict[str, Any]]:
        """Fetch training data from MongoDB"""
        try:
            client = MongoClient(self.mongodb_uri)
            db = client['stock_ai']
            collection = db['stock_prices']
            
            # Fetch recent price data for the symbol
            cursor = collection.find(
                {'symbol': symbol},
                sort=[('time', -1)],
                limit=limit
            )
            
            data = list(cursor)
            client.close()
            
            # Reverse to get chronological order
            data.reverse()
            
            logger.info(f"Fetched {len(data)} records for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch training data for {symbol}: {e}")
            return []
    
    def _save_model(self, symbol: str, model: EnsembleModel, training_data: List[Dict]) -> Dict[str, Any]:
        """Save trained model to disk"""
        try:
            # Create models directory
            models_dir = "models"
            os.makedirs(models_dir, exist_ok=True)
            
            # Model version
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Model metadata
            model_info = {
                'symbol': symbol,
                'version': version,
                'created_at': datetime.now().isoformat(),
                'training_data_size': len(training_data),
                'model_type': 'ensemble',
                'weights': model.weights,
                'trained': model.trained
            }
            
            # Save metadata
            metadata_path = os.path.join(models_dir, f"{symbol}_{version}_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(model_info, f, indent=2)
            
            # Save model state (simplified - in production would use pickle/joblib)
            model_state = {
                'weights': model.weights,
                'trained': model.trained,
                'arima_params': {
                    'p': model.arima_model.p,
                    'd': model.arima_model.d,
                    'q': model.arima_model.q
                },
                'lstm_params': {
                    'sequence_length': model.lstm_model.sequence_length,
                    'hidden_size': model.lstm_model.hidden_size
                }
            }
            
            model_path = os.path.join(models_dir, f"{symbol}_{version}_model.json")
            with open(model_path, 'w') as f:
                json.dump(model_state, f, indent=2)
            
            logger.info(f"Model saved for {symbol} version {version}")
            return model_info
            
        except Exception as e:
            logger.error(f"Failed to save model for {symbol}: {e}")
            return {}
    
    def _load_model(self, symbol: str) -> Optional[EnsembleModel]:
        """Load model from disk"""
        try:
            models_dir = "models"
            
            # Find latest model file for symbol
            model_files = [f for f in os.listdir(models_dir) 
                          if f.startswith(f"{symbol}_") and f.endswith("_model.json")]
            
            if not model_files:
                return None
            
            # Get latest version
            latest_file = sorted(model_files)[-1]
            model_path = os.path.join(models_dir, latest_file)
            
            # Load model state
            with open(model_path, 'r') as f:
                model_state = json.load(f)
            
            # Recreate model
            model = EnsembleModel()
            model.weights = model_state.get('weights', model.weights)
            model.trained = model_state.get('trained', False)
            
            logger.info(f"Model loaded for {symbol}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load model for {symbol}: {e}")
            return None
    
    def _is_model_recent(self, symbol: str, max_age_hours: int = 24) -> bool:
        """Check if model is recent enough"""
        try:
            models_dir = "models"
            
            # Find latest metadata file
            metadata_files = [f for f in os.listdir(models_dir) 
                             if f.startswith(f"{symbol}_") and f.endswith("_metadata.json")]
            
            if not metadata_files:
                return False
            
            latest_file = sorted(metadata_files)[-1]
            metadata_path = os.path.join(models_dir, latest_file)
            
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            created_at = datetime.fromisoformat(metadata['created_at'])
            age_hours = (datetime.now() - created_at).total_seconds() / 3600
            
            return age_hours < max_age_hours
            
        except Exception:
            return False
    
    def get_training_summary(self) -> Dict[str, Any]:
        """Get summary of all trained models"""
        try:
            models_dir = "models"
            
            if not os.path.exists(models_dir):
                return {'total_models': 0, 'symbols': []}
            
            # Count models by symbol
            symbols = set()
            total_models = 0
            
            for filename in os.listdir(models_dir):
                if filename.endswith("_metadata.json"):
                    symbol = filename.split('_')[0]
                    symbols.add(symbol)
                    total_models += 1
            
            return {
                'total_models': total_models,
                'unique_symbols': len(symbols),
                'symbols': list(symbols),
                'models_in_memory': len(self.models)
            }
            
        except Exception as e:
            logger.error(f"Failed to get training summary: {e}")
            return {'error': str(e)}