import logging
import json
import signal
import sys
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from ..config.settings import (
    KAFKA_BOOTSTRAP_SERVERS, 
    KAFKA_NEWS_TOPIC, 
    KAFKA_GROUP_ID
)
from ..processors.news_batch_processor import NewsBatchProcessor
from ..exceptions.consumer_exceptions import ConsumerError

logger = logging.getLogger(__name__)

class NewsConsumer:
    def __init__(self):
        self.consumer = None
        self.batch_processor = NewsBatchProcessor()
        self.running = False
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown handlers"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
    
    def start(self):
        """Start consuming messages from Kafka"""
        try:
            self.consumer = KafkaConsumer(
                KAFKA_NEWS_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id=f"{KAFKA_GROUP_ID}_news",
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda m: m.decode('utf-8') if m else None,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                auto_commit_interval_ms=1000
            )
            
            self.running = True
            logger.info(f"Started consuming from topic: {KAFKA_NEWS_TOPIC}")
            
            for message in self.consumer:
                if not self.running:
                    break
                
                try:
                    # Process message
                    self.batch_processor.add_message(message.value)
                    
                    # Check for timeout-based batch processing
                    if self.batch_processor.should_process_timeout():
                        self.batch_processor.force_process_batch()
                
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue
            
        except KafkaError as e:
            logger.error(f"Kafka error: {e}")
            raise ConsumerError(f"Kafka consumer error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise ConsumerError(f"Consumer error: {e}")
        finally:
            self._cleanup()
    
    def stop(self):
        """Stop the consumer"""
        self.running = False
        logger.info("News consumer stop requested")
    
    def _cleanup(self):
        """Cleanup resources"""
        if self.batch_processor:
            self.batch_processor.close()
        
        if self.consumer:
            self.consumer.close()
        
        logger.info("News consumer cleanup completed")