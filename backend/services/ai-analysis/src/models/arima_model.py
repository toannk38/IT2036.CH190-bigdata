import logging
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ARIMAResult:
    prediction: float
    confidence_interval: Tuple[float, float]
    model_params: Dict[str, Any]
    accuracy_score: float

class SimpleARIMA:
    """Simplified ARIMA implementation for stock price prediction"""
    
    def __init__(self, p: int = 1, d: int = 1, q: int = 1):
        self.p = p  # AR order
        self.d = d  # Differencing order
        self.q = q  # MA order
        self.ar_params = None
        self.ma_params = None
        self.residuals = None
        self.fitted_values = None
        
    def fit(self, data: List[float]) -> bool:
        """Fit ARIMA model to data"""
        try:
            if len(data) < max(self.p, self.q) + self.d + 5:
                logger.warning("Insufficient data for ARIMA model")
                return False
            
            # Differencing
            diff_data = self._difference(data, self.d)
            
            if len(diff_data) < max(self.p, self.q) + 2:
                return False
            
            # Fit AR and MA components using simple methods
            self.ar_params = self._fit_ar(diff_data, self.p)
            self.ma_params = self._fit_ma(diff_data, self.q)
            
            # Calculate residuals and fitted values
            self._calculate_residuals(diff_data)
            
            return True
            
        except Exception as e:
            logger.error(f"ARIMA fitting failed: {e}")
            return False
    
    def predict(self, steps: int = 1) -> ARIMAResult:
        """Predict next values"""
        if self.ar_params is None:
            return ARIMAResult(0.0, (0.0, 0.0), {}, 0.0)
        
        try:
            # Simple prediction using AR component
            if len(self.fitted_values) >= self.p:
                recent_values = self.fitted_values[-self.p:]
                prediction = sum(self.ar_params[i] * recent_values[-(i+1)] 
                               for i in range(len(self.ar_params)))
            else:
                prediction = 0.0
            
            # Estimate confidence interval
            if self.residuals:
                residual_std = np.std(self.residuals)
                ci_lower = prediction - 1.96 * residual_std
                ci_upper = prediction + 1.96 * residual_std
            else:
                ci_lower = prediction * 0.95
                ci_upper = prediction * 1.05
            
            # Calculate accuracy (simplified)
            accuracy = self._calculate_accuracy()
            
            return ARIMAResult(
                prediction=prediction,
                confidence_interval=(ci_lower, ci_upper),
                model_params={
                    'p': self.p, 'd': self.d, 'q': self.q,
                    'ar_params': self.ar_params,
                    'ma_params': self.ma_params
                },
                accuracy_score=accuracy
            )
            
        except Exception as e:
            logger.error(f"ARIMA prediction failed: {e}")
            return ARIMAResult(0.0, (0.0, 0.0), {}, 0.0)
    
    def _difference(self, data: List[float], order: int) -> List[float]:
        """Apply differencing to make series stationary"""
        result = data[:]
        
        for _ in range(order):
            if len(result) <= 1:
                break
            result = [result[i] - result[i-1] for i in range(1, len(result))]
        
        return result
    
    def _fit_ar(self, data: List[float], p: int) -> List[float]:
        """Fit AR component using simple linear regression"""
        if len(data) <= p:
            return [0.1] * p
        
        try:
            # Create lagged variables
            X = []
            y = []
            
            for i in range(p, len(data)):
                X.append([data[i-j-1] for j in range(p)])
                y.append(data[i])
            
            if not X or not y:
                return [0.1] * p
            
            X = np.array(X)
            y = np.array(y)
            
            # Simple least squares
            if X.shape[0] > X.shape[1]:
                params = np.linalg.lstsq(X, y, rcond=None)[0]
                return params.tolist()
            else:
                return [0.1] * p
                
        except Exception as e:
            logger.warning(f"AR fitting failed: {e}")
            return [0.1] * p
    
    def _fit_ma(self, data: List[float], q: int) -> List[float]:
        """Fit MA component (simplified)"""
        # For simplicity, use small random values
        return [0.05] * q
    
    def _calculate_residuals(self, data: List[float]):
        """Calculate model residuals"""
        try:
            fitted = []
            residuals = []
            
            for i in range(max(self.p, self.q), len(data)):
                # Simple fitted value calculation
                if i >= self.p:
                    fitted_val = sum(self.ar_params[j] * data[i-j-1] 
                                   for j in range(len(self.ar_params)))
                else:
                    fitted_val = data[i-1]
                
                fitted.append(fitted_val)
                residuals.append(data[i] - fitted_val)
            
            self.fitted_values = fitted
            self.residuals = residuals
            
        except Exception as e:
            logger.warning(f"Residual calculation failed: {e}")
            self.fitted_values = []
            self.residuals = []
    
    def _calculate_accuracy(self) -> float:
        """Calculate model accuracy"""
        if not self.residuals or not self.fitted_values:
            return 0.5
        
        try:
            # Mean Absolute Percentage Error (MAPE)
            mape_values = []
            for i, residual in enumerate(self.residuals):
                if i < len(self.fitted_values) and self.fitted_values[i] != 0:
                    mape = abs(residual / self.fitted_values[i])
                    mape_values.append(mape)
            
            if mape_values:
                avg_mape = np.mean(mape_values)
                accuracy = max(0.0, 1.0 - avg_mape)
                return min(1.0, accuracy)
            
            return 0.5
            
        except Exception as e:
            logger.warning(f"Accuracy calculation failed: {e}")
            return 0.5