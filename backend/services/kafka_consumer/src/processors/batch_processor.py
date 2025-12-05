import logging
import time
from typing import List, Dict, Any
from threading import Lock
from ..config.settings import BATCH_SIZE, BATCH_TIMEOUT, RATE_LIMIT_PER_SECOND
from ..adapters.mongodb_adapter import MongoDBAdapter
from ..validators.price_validator import PriceValidator
from ..exceptions.consumer_exceptions import BatchProcessingError, RateLimitExceededError
from ..metrics.metrics_collector import metrics
from ...data_quality.src.validators.data_quality_validator import DataQualityValidator
from ...data_quality.src.analyzers.outlier_detector import OutlierDetector
from ...data_quality.src.monitors.quality_monitor import QualityMonitor

logger = logging.getLogger(__name__)

class BatchProcessor:
    def __init__(self):
        self.mongodb_adapter = MongoDBAdapter()
        self.validator = PriceValidator()
        self.quality_validator = DataQualityValidator()
        self.outlier_detector = OutlierDetector()
        self.quality_monitor = QualityMonitor()
        self.batch = []
        self.batch_lock = Lock()
        self.last_process_time = time.time()
        self.rate_limiter = time.time()
    
    def add_message(self, message_data: Dict[str, Any]) -> bool:
        """Add message to batch for processing"""
        metrics.increment_counter('price_messages_received')
        
        # Basic validation
        if not self.validator.validate_price_message(message_data):
            logger.warning(f"Invalid message data for symbol {message_data.get('symbol', 'unknown')}")
            metrics.increment_counter('price_messages_invalid')
            return False
        
        # Quality validation
        quality_result = self.quality_validator.validate_price_data(message_data)
        
        # Record quality metrics
        self.quality_monitor.record_price_validation(quality_result, False)
        
        if not quality_result.is_valid:
            logger.warning(f"Quality validation failed for {message_data.get('symbol')}: {quality_result.issues}")
            metrics.increment_counter('price_messages_quality_failed')
        
        metrics.increment_counter('price_messages_valid')
        metrics.set_gauge('price_quality_score', quality_result.score)
        
        with self.batch_lock:
            self.batch.append(message_data)
            metrics.set_gauge('price_batch_size', len(self.batch))
            
            # Check if batch is ready for processing
            if len(self.batch) >= BATCH_SIZE:
                self._process_batch()
                return True
        
        return True
    
    def _process_batch(self):
        """Process current batch with rate limiting"""
        if not self.batch:
            return
        
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.rate_limiter
        min_interval = 1.0 / RATE_LIMIT_PER_SECOND
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
        
        try:
            start_time = time.time()
            batch_to_process = self.batch.copy()
            self.batch.clear()
            
            stats = self.mongodb_adapter.upsert_batch(batch_to_process)
            
            processing_time = time.time() - start_time
            metrics.record_histogram('price_batch_processing_time', processing_time)
            metrics.increment_counter('price_batches_processed')
            metrics.increment_counter('price_records_upserted', stats.get('upserted', 0))
            metrics.increment_counter('price_records_modified', stats.get('modified', 0))
            metrics.set_gauge('price_batch_size', 0)
            
            logger.info(f"Processed batch of {len(batch_to_process)} messages: {stats}")
            self.rate_limiter = time.time()
            self.last_process_time = time.time()
            
        except Exception as e:
            metrics.increment_counter('price_batch_errors')
            logger.error(f"Batch processing failed: {e}")
            raise BatchProcessingError(f"Failed to process batch: {e}")
    
    def force_process_batch(self):
        """Force process current batch regardless of size"""
        with self.batch_lock:
            if self.batch:
                self._process_batch()
    
    def should_process_timeout(self) -> bool:
        """Check if batch should be processed due to timeout"""
        if not self.batch:
            return False
        
        current_time = time.time()
        return (current_time - self.last_process_time) >= BATCH_TIMEOUT
    
    def close(self):
        """Close processor and flush remaining data"""
        self.force_process_batch()
        self.mongodb_adapter.close()