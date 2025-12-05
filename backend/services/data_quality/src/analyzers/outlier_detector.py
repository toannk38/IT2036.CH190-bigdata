import logging
import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class OutlierResult:
    is_outlier: bool
    confidence: float
    method: str
    details: Dict[str, Any]

class OutlierDetector:
    def __init__(self):
        self.z_score_threshold = 3.0
        self.iqr_multiplier = 1.5
    
    def detect_price_outliers(self, current_price: Dict[str, Any], 
                            historical_prices: List[Dict[str, Any]]) -> OutlierResult:
        """Detect price outliers using multiple methods"""
        if len(historical_prices) < 10:
            return OutlierResult(False, 0.0, "insufficient_data", {})
        
        # Extract close prices for analysis
        close_prices = [float(p['close']) for p in historical_prices]
        current_close = float(current_price['close'])
        
        # Z-score method
        z_result = self._z_score_detection(current_close, close_prices)
        
        # IQR method
        iqr_result = self._iqr_detection(current_close, close_prices)
        
        # Volume outlier detection
        volumes = [int(p['volume']) for p in historical_prices]
        current_volume = int(current_price['volume'])
        volume_result = self._volume_outlier_detection(current_volume, volumes)
        
        # Combine results
        is_outlier = z_result.is_outlier or iqr_result.is_outlier or volume_result.is_outlier
        confidence = max(z_result.confidence, iqr_result.confidence, volume_result.confidence)
        
        return OutlierResult(
            is_outlier=is_outlier,
            confidence=confidence,
            method="combined",
            details={
                "z_score": z_result.details,
                "iqr": iqr_result.details,
                "volume": volume_result.details
            }
        )
    
    def detect_volume_spike(self, current_volume: int, 
                          historical_volumes: List[int]) -> OutlierResult:
        """Detect unusual volume spikes"""
        if len(historical_volumes) < 5:
            return OutlierResult(False, 0.0, "insufficient_data", {})
        
        avg_volume = np.mean(historical_volumes)
        std_volume = np.std(historical_volumes)
        
        if std_volume == 0:
            return OutlierResult(False, 0.0, "no_variance", {})
        
        # Volume spike detection (more than 3x average)
        volume_ratio = current_volume / avg_volume
        is_spike = volume_ratio > 3.0
        
        # Z-score for volume
        z_score = (current_volume - avg_volume) / std_volume
        
        return OutlierResult(
            is_outlier=is_spike,
            confidence=min(1.0, volume_ratio / 5.0),
            method="volume_spike",
            details={
                "volume_ratio": volume_ratio,
                "z_score": z_score,
                "threshold": 3.0
            }
        )
    
    def _z_score_detection(self, current_value: float, 
                          historical_values: List[float]) -> OutlierResult:
        """Z-score based outlier detection"""
        mean_val = np.mean(historical_values)
        std_val = np.std(historical_values)
        
        if std_val == 0:
            return OutlierResult(False, 0.0, "z_score", {"z_score": 0.0})
        
        z_score = abs(current_value - mean_val) / std_val
        is_outlier = z_score > self.z_score_threshold
        confidence = min(1.0, z_score / (self.z_score_threshold * 2))
        
        return OutlierResult(
            is_outlier=is_outlier,
            confidence=confidence,
            method="z_score",
            details={
                "z_score": z_score,
                "threshold": self.z_score_threshold,
                "mean": mean_val,
                "std": std_val
            }
        )
    
    def _iqr_detection(self, current_value: float, 
                      historical_values: List[float]) -> OutlierResult:
        """IQR based outlier detection"""
        q1 = np.percentile(historical_values, 25)
        q3 = np.percentile(historical_values, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - self.iqr_multiplier * iqr
        upper_bound = q3 + self.iqr_multiplier * iqr
        
        is_outlier = current_value < lower_bound or current_value > upper_bound
        
        # Calculate confidence based on distance from bounds
        if current_value < lower_bound:
            distance = lower_bound - current_value
            confidence = min(1.0, distance / (iqr * 2))
        elif current_value > upper_bound:
            distance = current_value - upper_bound
            confidence = min(1.0, distance / (iqr * 2))
        else:
            confidence = 0.0
        
        return OutlierResult(
            is_outlier=is_outlier,
            confidence=confidence,
            method="iqr",
            details={
                "q1": q1,
                "q3": q3,
                "iqr": iqr,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "current_value": current_value
            }
        )
    
    def _volume_outlier_detection(self, current_volume: int, 
                                historical_volumes: List[int]) -> OutlierResult:
        """Volume-specific outlier detection"""
        if len(historical_volumes) < 5:
            return OutlierResult(False, 0.0, "volume", {})
        
        # Use median for volume analysis (more robust)
        median_volume = np.median(historical_volumes)
        mad = np.median([abs(v - median_volume) for v in historical_volumes])
        
        if mad == 0:
            return OutlierResult(False, 0.0, "volume", {"mad": 0})
        
        # Modified Z-score using MAD
        modified_z = 0.6745 * (current_volume - median_volume) / mad
        is_outlier = abs(modified_z) > 3.5
        confidence = min(1.0, abs(modified_z) / 7.0)
        
        return OutlierResult(
            is_outlier=is_outlier,
            confidence=confidence,
            method="volume",
            details={
                "modified_z_score": modified_z,
                "median_volume": median_volume,
                "mad": mad,
                "threshold": 3.5
            }
        )