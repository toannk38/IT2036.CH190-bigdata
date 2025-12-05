import logging
import time
from typing import Dict, Any
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from ..config.settings import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_PRICE_TOPIC,
    KAFKA_NEWS_TOPIC,
    MONGODB_URI
)

logger = logging.getLogger(__name__)

class HealthChecker:
    def __init__(self):
        self.last_check = 0
        self.check_interval = 30  # seconds
        self.health_status = {
            'kafka': {'status': 'unknown', 'last_check': None},
            'mongodb': {'status': 'unknown', 'last_check': None},
            'overall': {'status': 'unknown', 'last_check': None}
        }
    
    def check_health(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        current_time = time.time()
        
        # Only check if enough time has passed
        if current_time - self.last_check < self.check_interval:
            return self.health_status
        
        self.last_check = current_time
        
        # Check Kafka health
        kafka_health = self._check_kafka()
        self.health_status['kafka'] = {
            'status': 'healthy' if kafka_health else 'unhealthy',
            'last_check': current_time
        }
        
        # Check MongoDB health
        mongodb_health = self._check_mongodb()
        self.health_status['mongodb'] = {
            'status': 'healthy' if mongodb_health else 'unhealthy',
            'last_check': current_time
        }
        
        # Overall health
        overall_healthy = kafka_health and mongodb_health
        self.health_status['overall'] = {
            'status': 'healthy' if overall_healthy else 'unhealthy',
            'last_check': current_time
        }
        
        return self.health_status
    
    def _check_kafka(self) -> bool:
        """Check Kafka connectivity"""
        try:
            # Test consumer connection
            consumer = KafkaConsumer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                consumer_timeout_ms=5000
            )
            
            # Get topic metadata
            topics = consumer.topics()
            consumer.close()
            
            # Check if required topics exist
            required_topics = {KAFKA_PRICE_TOPIC, KAFKA_NEWS_TOPIC}
            if not required_topics.issubset(topics):
                logger.warning(f"Missing Kafka topics: {required_topics - topics}")
                return False
            
            logger.debug("Kafka health check passed")
            return True
            
        except KafkaError as e:
            logger.error(f"Kafka health check failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in Kafka health check: {e}")
            return False
    
    def _check_mongodb(self) -> bool:
        """Check MongoDB connectivity"""
        try:
            client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            
            # Test connection
            client.admin.command('ping')
            client.close()
            
            logger.debug("MongoDB health check passed")
            return True
            
        except ConnectionFailure as e:
            logger.error(f"MongoDB health check failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in MongoDB health check: {e}")
            return False
    
    def is_healthy(self) -> bool:
        """Quick health status check"""
        health = self.check_health()
        return health['overall']['status'] == 'healthy'