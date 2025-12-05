import logging
import time
from typing import Dict, Any
from threading import Lock
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class MetricsCollector:
    def __init__(self, max_history=1000):
        self.max_history = max_history
        self.metrics_lock = Lock()
        
        # Counters
        self.counters = defaultdict(int)
        
        # Gauges
        self.gauges = defaultdict(float)
        
        # Histograms (for latency tracking)
        self.histograms = defaultdict(lambda: deque(maxlen=max_history))
        
        # Timestamps for rate calculations
        self.timestamps = defaultdict(lambda: deque(maxlen=max_history))
        
        self.start_time = time.time()
    
    def increment_counter(self, metric_name: str, value: int = 1):
        """Increment a counter metric"""
        with self.metrics_lock:
            self.counters[metric_name] += value
            self.timestamps[metric_name].append(time.time())
    
    def set_gauge(self, metric_name: str, value: float):
        """Set a gauge metric"""
        with self.metrics_lock:
            self.gauges[metric_name] = value
    
    def record_histogram(self, metric_name: str, value: float):
        """Record a histogram value (e.g., processing time)"""
        with self.metrics_lock:
            self.histograms[metric_name].append(value)
            self.timestamps[f"{metric_name}_hist"].append(time.time())
    
    def get_counter(self, metric_name: str) -> int:
        """Get counter value"""
        return self.counters.get(metric_name, 0)
    
    def get_gauge(self, metric_name: str) -> float:
        """Get gauge value"""
        return self.gauges.get(metric_name, 0.0)
    
    def get_rate(self, metric_name: str, window_seconds: int = 60) -> float:
        """Calculate rate per second for a metric over time window"""
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        timestamps = self.timestamps.get(metric_name, deque())
        recent_events = sum(1 for ts in timestamps if ts >= cutoff_time)
        
        return recent_events / window_seconds if window_seconds > 0 else 0.0
    
    def get_histogram_stats(self, metric_name: str) -> Dict[str, float]:
        """Get histogram statistics"""
        values = list(self.histograms.get(metric_name, []))
        
        if not values:
            return {'count': 0, 'avg': 0.0, 'min': 0.0, 'max': 0.0, 'p95': 0.0}
        
        values.sort()
        count = len(values)
        
        return {
            'count': count,
            'avg': sum(values) / count,
            'min': values[0],
            'max': values[-1],
            'p95': values[int(count * 0.95)] if count > 0 else 0.0
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics as a dictionary"""
        with self.metrics_lock:
            uptime = time.time() - self.start_time
            
            metrics = {
                'uptime_seconds': uptime,
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'rates': {},
                'histograms': {}
            }
            
            # Calculate rates for all counters
            for counter_name in self.counters.keys():
                metrics['rates'][f"{counter_name}_per_minute"] = self.get_rate(counter_name, 60)
                metrics['rates'][f"{counter_name}_per_second"] = self.get_rate(counter_name, 1)
            
            # Get histogram stats
            for hist_name in self.histograms.keys():
                metrics['histograms'][hist_name] = self.get_histogram_stats(hist_name)
            
            return metrics
    
    def reset_metrics(self):
        """Reset all metrics"""
        with self.metrics_lock:
            self.counters.clear()
            self.gauges.clear()
            self.histograms.clear()
            self.timestamps.clear()
            self.start_time = time.time()

# Global metrics instance
metrics = MetricsCollector()