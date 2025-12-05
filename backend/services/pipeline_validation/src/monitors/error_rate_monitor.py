import logging
import time
from typing import Dict, List, Any
from collections import deque, defaultdict
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ErrorMetrics:
    total_operations: int
    failed_operations: int
    error_rate: float
    error_types: Dict[str, int]
    timestamp: datetime

class ErrorRateMonitor:
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.operations = deque(maxlen=window_size)
        self.error_counts = defaultdict(int)
        self.total_operations = 0
        
        # Error rate thresholds
        self.thresholds = {
            'critical': 0.05,  # 5% error rate
            'warning': 0.02,   # 2% error rate
            'target': 0.01     # 1% target error rate
        }
    
    def record_operation(self, success: bool, error_type: str = None):
        """Record an operation result"""
        self.total_operations += 1
        
        operation = {
            'timestamp': datetime.now(),
            'success': success,
            'error_type': error_type if not success else None
        }
        
        self.operations.append(operation)
        
        if not success and error_type:
            self.error_counts[error_type] += 1
    
    def get_current_metrics(self) -> ErrorMetrics:
        """Get current error rate metrics"""
        if not self.operations:
            return ErrorMetrics(0, 0, 0.0, {}, datetime.now())
        
        total_ops = len(self.operations)
        failed_ops = sum(1 for op in self.operations if not op['success'])
        error_rate = failed_ops / total_ops if total_ops > 0 else 0.0
        
        # Count error types in current window
        error_types = defaultdict(int)
        for op in self.operations:
            if not op['success'] and op['error_type']:
                error_types[op['error_type']] += 1
        
        return ErrorMetrics(
            total_operations=total_ops,
            failed_operations=failed_ops,
            error_rate=error_rate,
            error_types=dict(error_types),
            timestamp=datetime.now()
        )
    
    def get_error_trend(self, hours: int = 24) -> Dict[str, Any]:
        """Get error rate trend over time"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter recent operations
        recent_ops = [op for op in self.operations if op['timestamp'] >= cutoff_time]
        
        if not recent_ops:
            return {
                'trend': 'no_data',
                'hours': hours,
                'data_points': 0
            }
        
        # Calculate hourly error rates
        hourly_rates = []
        for hour in range(hours):
            hour_start = cutoff_time + timedelta(hours=hour)
            hour_end = hour_start + timedelta(hours=1)
            
            hour_ops = [op for op in recent_ops 
                       if hour_start <= op['timestamp'] < hour_end]
            
            if hour_ops:
                failed = sum(1 for op in hour_ops if not op['success'])
                rate = failed / len(hour_ops)
                hourly_rates.append(rate)
        
        if len(hourly_rates) < 2:
            trend = 'stable'
        else:
            # Simple trend calculation
            first_half = hourly_rates[:len(hourly_rates)//2]
            second_half = hourly_rates[len(hourly_rates)//2:]
            
            first_avg = sum(first_half) / len(first_half) if first_half else 0
            second_avg = sum(second_half) / len(second_half) if second_half else 0
            
            if second_avg > first_avg + 0.01:
                trend = 'increasing'
            elif second_avg < first_avg - 0.01:
                trend = 'decreasing'
            else:
                trend = 'stable'
        
        return {
            'trend': trend,
            'hours': hours,
            'data_points': len(recent_ops),
            'hourly_rates': hourly_rates,
            'average_rate': sum(hourly_rates) / len(hourly_rates) if hourly_rates else 0
        }
    
    def check_error_thresholds(self) -> List[Dict[str, Any]]:
        """Check if error rates exceed thresholds"""
        metrics = self.get_current_metrics()
        alerts = []
        
        if metrics.error_rate >= self.thresholds['critical']:
            alerts.append({
                'level': 'critical',
                'message': f"Critical error rate: {metrics.error_rate:.3f} >= {self.thresholds['critical']}",
                'error_rate': metrics.error_rate,
                'threshold': self.thresholds['critical'],
                'timestamp': datetime.now().isoformat()
            })
        elif metrics.error_rate >= self.thresholds['warning']:
            alerts.append({
                'level': 'warning',
                'message': f"High error rate: {metrics.error_rate:.3f} >= {self.thresholds['warning']}",
                'error_rate': metrics.error_rate,
                'threshold': self.thresholds['warning'],
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts
    
    def get_top_errors(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most common error types"""
        sorted_errors = sorted(
            self.error_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        total_errors = sum(self.error_counts.values())
        
        top_errors = []
        for error_type, count in sorted_errors[:limit]:
            percentage = (count / total_errors * 100) if total_errors > 0 else 0
            top_errors.append({
                'error_type': error_type,
                'count': count,
                'percentage': percentage
            })
        
        return top_errors
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get comprehensive monitoring summary"""
        metrics = self.get_current_metrics()
        alerts = self.check_error_thresholds()
        trend = self.get_error_trend()
        top_errors = self.get_top_errors()
        
        # Calculate health status
        if metrics.error_rate <= self.thresholds['target']:
            health_status = 'healthy'
        elif metrics.error_rate <= self.thresholds['warning']:
            health_status = 'warning'
        else:
            health_status = 'critical'
        
        return {
            'timestamp': datetime.now().isoformat(),
            'health_status': health_status,
            'current_metrics': {
                'total_operations': metrics.total_operations,
                'failed_operations': metrics.failed_operations,
                'error_rate': metrics.error_rate,
                'success_rate': 1.0 - metrics.error_rate
            },
            'thresholds': self.thresholds,
            'alerts': alerts,
            'trend': trend,
            'top_errors': top_errors,
            'total_lifetime_operations': self.total_operations
        }