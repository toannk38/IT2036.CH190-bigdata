import logging
import time
from typing import List, Dict, Any
from threading import Lock
from ..config.settings import BATCH_SIZE, BATCH_TIMEOUT, RATE_LIMIT_PER_SECOND
from ..adapters.news_mongodb_adapter import NewsMongoDBAdapter
from ..validators.news_validator import NewsValidator
from ..exceptions.consumer_exceptions import BatchProcessingError
from ..metrics.metrics_collector import metrics

logger = logging.getLogger(__name__)

class NewsBatchProcessor:
    def __init__(self):
        self.mongodb_adapter = NewsMongoDBAdapter()
        self.validator = NewsValidator()
        self.batch = []
        self.batch_lock = Lock()
        self.last_process_time = time.time()
        self.rate_limiter = time.time()
    
    def add_message(self, message_data: Dict[str, Any]) -> bool:
        """Add message to batch for processing"""
        metrics.increment_counter('news_messages_received')
        
        if not self.validator.validate_news_message(message_data):
            logger.warning(f"Invalid news message data for symbol {message_data.get('symbol', 'unknown')}")
            metrics.increment_counter('news_messages_invalid')
            return False
        
        metrics.increment_counter('news_messages_valid')
        
        with self.batch_lock:
            self.batch.append(message_data)
            metrics.set_gauge('news_batch_size', len(self.batch))
            
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
            metrics.record_histogram('news_batch_processing_time', processing_time)
            metrics.increment_counter('news_batches_processed')
            metrics.increment_counter('news_records_upserted', stats.get('upserted', 0))
            metrics.increment_counter('news_records_modified', stats.get('modified', 0))
            metrics.set_gauge('news_batch_size', 0)
            
            logger.info(f"Processed news batch of {len(batch_to_process)} messages: {stats}")
            self.rate_limiter = time.time()
            self.last_process_time = time.time()
            
        except Exception as e:
            metrics.increment_counter('news_batch_errors')
            logger.error(f"News batch processing failed: {e}")
            raise BatchProcessingError(f"Failed to process news batch: {e}")
    
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