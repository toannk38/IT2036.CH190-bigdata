import logging
import time
from typing import Dict, List, Any
from collections import defaultdict, deque
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class QualityMetrics:
    total_records: int
    valid_records: int
    invalid_records: int
    avg_quality_score: float
    outlier_count: int
    duplicate_count: int
    timestamp: datetime

class QualityMonitor:
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.price_metrics = deque(maxlen=window_size)
        self.news_metrics = deque(maxlen=window_size)
        
        # Real-time counters
        self.counters = defaultdict(int)
        self.quality_scores = deque(maxlen=window_size)
        
        # Alerts
        self.alert_thresholds = {
            'min_quality_score': 0.8,
            'max_outlier_rate': 0.05,
            'max_invalid_rate': 0.1
        }
    
    def record_price_validation(self, validation_result, is_outlier: bool = False):
        """Record price validation result"""
        self.counters['price_total'] += 1
        
        if validation_result.is_valid:
            self.counters['price_valid'] += 1
        else:
            self.counters['price_invalid'] += 1
        
        if is_outlier:
            self.counters['price_outliers'] += 1
        
        self.quality_scores.append(validation_result.score)
        
        # Store detailed metrics
        metrics = QualityMetrics(
            total_records=self.counters['price_total'],
            valid_records=self.counters['price_valid'],
            invalid_records=self.counters['price_invalid'],
            avg_quality_score=validation_result.score,
            outlier_count=1 if is_outlier else 0,
            duplicate_count=0,
            timestamp=datetime.now()
        )
        self.price_metrics.append(metrics)
    
    def record_news_validation(self, validation_result, is_duplicate: bool = False):
        """Record news validation result"""
        self.counters['news_total'] += 1
        
        if validation_result.is_valid:
            self.counters['news_valid'] += 1
        else:
            self.counters['news_invalid'] += 1
        
        if is_duplicate:
            self.counters['news_duplicates'] += 1
        
        self.quality_scores.append(validation_result.score)
        
        # Store detailed metrics
        metrics = QualityMetrics(
            total_records=self.counters['news_total'],
            valid_records=self.counters['news_valid'],
            invalid_records=self.counters['news_invalid'],
            avg_quality_score=validation_result.score,
            outlier_count=0,
            duplicate_count=1 if is_duplicate else 0,
            timestamp=datetime.now()
        )
        self.news_metrics.append(metrics)
    
    def get_quality_summary(self) -> Dict[str, Any]:
        """Get overall quality summary"""
        current_time = datetime.now()
        
        # Calculate rates
        total_records = self.counters['price_total'] + self.counters['news_total']
        if total_records == 0:
            return self._empty_summary()
        
        valid_records = self.counters['price_valid'] + self.counters['news_valid']
        invalid_records = self.counters['price_invalid'] + self.counters['news_invalid']
        
        validity_rate = valid_records / total_records
        avg_quality_score = sum(self.quality_scores) / len(self.quality_scores) if self.quality_scores else 0.0
        
        # Price specific metrics
        price_total = self.counters['price_total']
        price_outlier_rate = self.counters['price_outliers'] / price_total if price_total > 0 else 0.0
        
        # News specific metrics
        news_total = self.counters['news_total']
        news_duplicate_rate = self.counters['news_duplicates'] / news_total if news_total > 0 else 0.0
        
        # Generate alerts
        alerts = self._generate_alerts(validity_rate, avg_quality_score, price_outlier_rate)
        
        return {
            'timestamp': current_time.isoformat(),
            'overall': {
                'total_records': total_records,
                'valid_records': valid_records,
                'invalid_records': invalid_records,
                'validity_rate': validity_rate,
                'avg_quality_score': avg_quality_score
            },
            'price_data': {
                'total': price_total,
                'valid': self.counters['price_valid'],
                'invalid': self.counters['price_invalid'],
                'outliers': self.counters['price_outliers'],
                'outlier_rate': price_outlier_rate
            },
            'news_data': {
                'total': news_total,
                'valid': self.counters['news_valid'],
                'invalid': self.counters['news_invalid'],
                'duplicates': self.counters['news_duplicates'],
                'duplicate_rate': news_duplicate_rate
            },
            'alerts': alerts,
            'thresholds': self.alert_thresholds
        }
    
    def get_trend_analysis(self, hours: int = 24) -> Dict[str, Any]:
        """Get quality trends over time"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter recent metrics
        recent_price_metrics = [m for m in self.price_metrics if m.timestamp >= cutoff_time]
        recent_news_metrics = [m for m in self.news_metrics if m.timestamp >= cutoff_time]
        
        if not recent_price_metrics and not recent_news_metrics:
            return {'trend': 'no_data', 'hours': hours}
        
        # Calculate trends
        price_trend = self._calculate_trend([m.avg_quality_score for m in recent_price_metrics])
        news_trend = self._calculate_trend([m.avg_quality_score for m in recent_news_metrics])
        
        return {
            'hours': hours,
            'price_trend': price_trend,
            'news_trend': news_trend,
            'price_samples': len(recent_price_metrics),
            'news_samples': len(recent_news_metrics)
        }
    
    def _empty_summary(self) -> Dict[str, Any]:
        """Return empty summary when no data available"""
        return {
            'timestamp': datetime.now().isoformat(),
            'overall': {
                'total_records': 0,
                'valid_records': 0,
                'invalid_records': 0,
                'validity_rate': 0.0,
                'avg_quality_score': 0.0
            },
            'price_data': {'total': 0, 'valid': 0, 'invalid': 0, 'outliers': 0, 'outlier_rate': 0.0},
            'news_data': {'total': 0, 'valid': 0, 'invalid': 0, 'duplicates': 0, 'duplicate_rate': 0.0},
            'alerts': [],
            'thresholds': self.alert_thresholds
        }
    
    def _generate_alerts(self, validity_rate: float, avg_quality_score: float, 
                        outlier_rate: float) -> List[Dict[str, Any]]:
        """Generate quality alerts"""
        alerts = []
        
        if avg_quality_score < self.alert_thresholds['min_quality_score']:
            alerts.append({
                'type': 'low_quality_score',
                'severity': 'warning',
                'message': f"Average quality score ({avg_quality_score:.3f}) below threshold ({self.alert_thresholds['min_quality_score']})",
                'timestamp': datetime.now().isoformat()
            })
        
        if outlier_rate > self.alert_thresholds['max_outlier_rate']:
            alerts.append({
                'type': 'high_outlier_rate',
                'severity': 'warning',
                'message': f"Outlier rate ({outlier_rate:.3f}) above threshold ({self.alert_thresholds['max_outlier_rate']})",
                'timestamp': datetime.now().isoformat()
            })
        
        invalid_rate = 1.0 - validity_rate
        if invalid_rate > self.alert_thresholds['max_invalid_rate']:
            alerts.append({
                'type': 'high_invalid_rate',
                'severity': 'critical',
                'message': f"Invalid data rate ({invalid_rate:.3f}) above threshold ({self.alert_thresholds['max_invalid_rate']})",
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values"""
        if len(values) < 2:
            return 'stable'
        
        # Simple trend calculation
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        if not first_half or not second_half:
            return 'stable'
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        diff = second_avg - first_avg
        
        if diff > 0.05:
            return 'improving'
        elif diff < -0.05:
            return 'declining'
        else:
            return 'stable'