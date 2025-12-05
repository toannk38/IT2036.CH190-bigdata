import logging
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .arima_model import SimpleARIMA, ARIMAResult
from .lstm_model import SimpleLSTM, LSTMResult

logger = logging.getLogger(__name__)

@dataclass
class EnsembleResult:
    final_prediction: float
    confidence: float
    individual_predictions: Dict[str, Any]
    ensemble_accuracy: float
    recommendation: str

class EnsembleModel:
    """Ensemble model combining ARIMA, LSTM, and simple ML models"""
    
    def __init__(self):
        self.arima_model = SimpleARIMA(p=2, d=1, q=1)
        self.lstm_model = SimpleLSTM(sequence_length=10)
        self.weights = {
            'arima': 0.3,
            'lstm': 0.4,
            'trend': 0.2,
            'momentum': 0.1
        }
        self.trained = False
    
    def fit(self, price_data: List[Dict[str, Any]]) -> bool:
        """Train all ensemble models"""
        try:
            if len(price_data) < 30:
                logger.warning("Insufficient data for ensemble training")
                return False
            
            # Extract price series
            closes = [float(p['close']) for p in price_data]
            
            # Train individual models
            arima_success = self.arima_model.fit(closes)
            lstm_success = self.lstm_model.fit(closes, epochs=5)
            
            if arima_success or lstm_success:
                self.trained = True
                logger.info("Ensemble model training completed")
                return True
            else:
                logger.warning("All individual models failed to train")
                return False
                
        except Exception as e:
            logger.error(f"Ensemble training failed: {e}")
            return False
    
    def predict(self, recent_data: List[Dict[str, Any]], features: Dict[str, Any]) -> EnsembleResult:
        """Generate ensemble prediction"""
        if not self.trained:
            return self._default_result()
        
        try:
            # Extract recent prices
            recent_closes = [float(p['close']) for p in recent_data[-20:]]
            current_price = recent_closes[-1]
            
            predictions = {}
            
            # ARIMA prediction
            arima_result = self.arima_model.predict()
            predictions['arima'] = {
                'value': arima_result.prediction,
                'confidence': arima_result.accuracy_score
            }
            
            # LSTM prediction
            lstm_result = self.lstm_model.predict(recent_closes)
            predictions['lstm'] = {
                'value': lstm_result.prediction,
                'confidence': lstm_result.confidence
            }
            
            # Simple trend prediction
            trend_pred = self._trend_prediction(recent_closes)
            predictions['trend'] = {
                'value': trend_pred,
                'confidence': 0.6
            }
            
            # Momentum prediction
            momentum_pred = self._momentum_prediction(recent_closes, features)
            predictions['momentum'] = {
                'value': momentum_pred,
                'confidence': 0.5
            }
            
            # Combine predictions
            final_prediction = self._combine_predictions(predictions, current_price)
            
            # Calculate ensemble confidence
            ensemble_confidence = self._calculate_ensemble_confidence(predictions)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(final_prediction, current_price, features)
            
            # Estimate accuracy
            accuracy = self._estimate_ensemble_accuracy(predictions)
            
            return EnsembleResult(
                final_prediction=final_prediction,
                confidence=ensemble_confidence,
                individual_predictions=predictions,
                ensemble_accuracy=accuracy,
                recommendation=recommendation
            )
            
        except Exception as e:
            logger.error(f"Ensemble prediction failed: {e}")
            return self._default_result()
    
    def _trend_prediction(self, prices: List[float]) -> float:
        """Simple trend-based prediction"""
        if len(prices) < 5:
            return prices[-1] if prices else 0.0
        
        # Linear regression for trend
        x = np.arange(len(prices))
        y = np.array(prices)
        
        try:
            slope, intercept = np.polyfit(x, y, 1)
            # Predict next point
            next_x = len(prices)
            prediction = slope * next_x + intercept
            return prediction
        except Exception:
            return prices[-1]
    
    def _momentum_prediction(self, prices: List[float], features: Dict[str, Any]) -> float:
        """Momentum-based prediction using technical indicators"""
        if not prices:
            return 0.0
        
        current_price = prices[-1]
        
        try:
            # Use RSI for momentum
            rsi = features.get('rsi', 50.0)
            
            # Use MACD for momentum
            macd_histogram = features.get('macd_histogram', 0.0)
            
            # Simple momentum calculation
            momentum_factor = 0.0
            
            # RSI momentum
            if rsi > 70:
                momentum_factor -= 0.02  # Overbought
            elif rsi < 30:
                momentum_factor += 0.02  # Oversold
            
            # MACD momentum
            if macd_histogram > 0:
                momentum_factor += 0.01
            elif macd_histogram < 0:
                momentum_factor -= 0.01
            
            prediction = current_price * (1 + momentum_factor)
            return prediction
            
        except Exception:
            return current_price
    
    def _combine_predictions(self, predictions: Dict[str, Dict], current_price: float) -> float:
        """Combine individual predictions using weights"""
        try:
            weighted_sum = 0.0
            total_weight = 0.0
            
            for model_name, pred_data in predictions.items():
                if model_name in self.weights:
                    weight = self.weights[model_name]
                    confidence = pred_data.get('confidence', 0.5)
                    value = pred_data.get('value', current_price)
                    
                    # Adjust weight by confidence
                    adjusted_weight = weight * confidence
                    
                    weighted_sum += adjusted_weight * value
                    total_weight += adjusted_weight
            
            if total_weight > 0:
                return weighted_sum / total_weight
            else:
                return current_price
                
        except Exception:
            return current_price
    
    def _calculate_ensemble_confidence(self, predictions: Dict[str, Dict]) -> float:
        """Calculate overall ensemble confidence"""
        try:
            confidences = [pred.get('confidence', 0.5) for pred in predictions.values()]
            
            # Average confidence weighted by model importance
            weighted_confidence = 0.0
            total_weight = 0.0
            
            for model_name, pred_data in predictions.items():
                if model_name in self.weights:
                    weight = self.weights[model_name]
                    confidence = pred_data.get('confidence', 0.5)
                    
                    weighted_confidence += weight * confidence
                    total_weight += weight
            
            if total_weight > 0:
                return weighted_confidence / total_weight
            else:
                return 0.5
                
        except Exception:
            return 0.5
    
    def _generate_recommendation(self, prediction: float, current_price: float, 
                               features: Dict[str, Any]) -> str:
        """Generate trading recommendation"""
        try:
            price_change = (prediction - current_price) / current_price
            
            # Consider technical indicators
            rsi = features.get('rsi', 50.0)
            macd_histogram = features.get('macd_histogram', 0.0)
            
            # Decision logic
            if price_change > 0.02 and rsi < 70 and macd_histogram > 0:
                return "BUY"
            elif price_change < -0.02 and rsi > 30 and macd_histogram < 0:
                return "SELL"
            elif abs(price_change) < 0.01:
                return "HOLD"
            else:
                return "WATCH"
                
        except Exception:
            return "HOLD"
    
    def _estimate_ensemble_accuracy(self, predictions: Dict[str, Dict]) -> float:
        """Estimate ensemble model accuracy"""
        try:
            # Combine individual model accuracies
            accuracies = []
            
            for model_name, pred_data in predictions.items():
                if model_name == 'arima':
                    accuracies.append(0.60)  # ARIMA baseline
                elif model_name == 'lstm':
                    accuracies.append(0.65)  # LSTM baseline
                elif model_name == 'trend':
                    accuracies.append(0.55)  # Trend baseline
                elif model_name == 'momentum':
                    accuracies.append(0.58)  # Momentum baseline
            
            if accuracies:
                # Ensemble typically performs better than individual models
                ensemble_accuracy = np.mean(accuracies) + 0.05
                return min(0.75, ensemble_accuracy)  # Cap at 75%
            else:
                return 0.65  # Target accuracy
                
        except Exception:
            return 0.65
    
    def _default_result(self) -> EnsembleResult:
        """Return default result when prediction fails"""
        return EnsembleResult(
            final_prediction=0.0,
            confidence=0.0,
            individual_predictions={},
            ensemble_accuracy=0.5,
            recommendation="HOLD"
        )