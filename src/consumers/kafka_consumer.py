"""
Kafka Data Consumer for consuming messages from Kafka topics and storing in MongoDB.
Handles offset management and error recovery.
"""

from datetime import datetime
from typing import Dict, Any, Optional, Set
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import json
import time

from src.logging_config import get_logger
from src.config import get_config

logger = get_logger(__name__)


class KafkaDataConsumer:
    """
    Consumes messages from Kafka topics and stores them in MongoDB.
    
    Responsibilities:
    - Consume messages from Kafka topics
    - Validate message schemas
    - Store validated messages in MongoDB
    - Handle offset management and error recovery
    """
    
    # Schema definitions for validation
    PRICE_SCHEMA = {
        'required_fields': {'symbol', 'timestamp', 'open', 'close', 'high', 'low', 'volume'},
        'field_types': {
            'symbol': str,
            'timestamp': str,
            'open': (int, float),
            'close': (int, float),
            'high': (int, float),
            'low': (int, float),
            'volume': int
        }
    }
    
    NEWS_SCHEMA = {
        'required_fields': {'symbol', 'title', 'content', 'source', 'published_at', 'collected_at'},
        'field_types': {
            'symbol': str,
            'title': str,
            'content': str,
            'source': str,
            'published_at': str,
            'collected_at': str
        }
    }
    
    def __init__(self, consumer: KafkaConsumer, mongo_client: MongoClient, database_name: str = 'vietnam_stock_ai'):
        """
        Initialize KafkaDataConsumer.
        
        Args:
            consumer: KafkaConsumer instance configured with topics
            mongo_client: MongoDB client instance
            database_name: Name of the MongoDB database to use
        """
        self.consumer = consumer
        self.mongo_client = mongo_client
        self.db = mongo_client[database_name]
        
        # Topic to collection mapping
        self.topic_collection_map = {
            'stock_prices_raw': 'price_history',
            'stock_news_raw': 'news'
        }
        
        # Topic to schema mapping
        self.topic_schema_map = {
            'stock_prices_raw': self.PRICE_SCHEMA,
            'stock_news_raw': self.NEWS_SCHEMA
        }
        
        logger.info(
            "KafkaDataConsumer initialized",
            context={
                'topics': list(consumer.subscription()),
                'database': database_name
            }
        )
    
    def consume_and_store(self, max_messages: Optional[int] = None, timeout_ms: int = 1000) -> Dict[str, int]:
        """
        Consume messages from Kafka topics and store in MongoDB.
        Handles offset management and error recovery.
        
        Args:
            max_messages: Maximum number of messages to consume (None for continuous)
            timeout_ms: Consumer poll timeout in milliseconds
            
        Returns:
            Dictionary with statistics: {'processed': int, 'failed': int, 'stored': int}
        """
        logger.info("Starting message consumption")
        
        processed_count = 0
        failed_count = 0
        stored_count = 0
        
        try:
            while True:
                # Poll for messages
                message_batch = self.consumer.poll(timeout_ms=timeout_ms, max_records=100)
                
                if not message_batch:
                    # No messages received in this poll
                    # If we have a max_messages limit and we've processed at least that many, stop
                    # Also stop if max_messages is set and we got an empty poll (no more messages available)
                    if max_messages is not None:
                        if processed_count >= max_messages:
                            break
                        # If we got an empty poll and have a message limit, assume no more messages
                        # This prevents hanging when consuming from topics with no data
                        if processed_count == 0:
                            break
                    continue
                
                # Process messages by topic partition
                for topic_partition, messages in message_batch.items():
                    topic = topic_partition.topic
                    collection_name = self.topic_collection_map.get(topic)
                    
                    if not collection_name:
                        logger.warning(
                            f"Unknown topic, skipping messages",
                            context={'topic': topic, 'message_count': len(messages)}
                        )
                        continue
                    
                    # Process each message
                    for message in messages:
                        processed_count += 1
                        
                        try:
                            # Decode and parse message
                            message_data = json.loads(message.value.decode('utf-8'))
                            
                            # Validate message schema
                            if not self.validate_message(message_data, topic):
                                failed_count += 1
                                logger.error(
                                    "Message validation failed",
                                    context={
                                        'topic': topic,
                                        'offset': message.offset,
                                        'partition': message.partition
                                    }
                                )
                                continue
                            
                            # Store in MongoDB
                            if self._store_message(message_data, collection_name):
                                stored_count += 1
                                logger.debug(
                                    "Message stored successfully",
                                    context={
                                        'topic': topic,
                                        'collection': collection_name,
                                        'offset': message.offset
                                    }
                                )
                            else:
                                failed_count += 1
                                
                        except json.JSONDecodeError as e:
                            failed_count += 1
                            logger.error(
                                "Failed to decode message JSON",
                                context={
                                    'topic': topic,
                                    'offset': message.offset,
                                    'error': str(e)
                                },
                                exc_info=True
                            )
                        except Exception as e:
                            failed_count += 1
                            logger.error(
                                "Error processing message",
                                context={
                                    'topic': topic,
                                    'offset': message.offset,
                                    'error': str(e)
                                },
                                exc_info=True
                            )
                
                # Commit offsets after processing batch
                try:
                    self.consumer.commit()
                    logger.debug("Offsets committed successfully")
                except KafkaError as e:
                    logger.error(
                        "Failed to commit offsets",
                        context={'error': str(e)},
                        exc_info=True
                    )
                
                # Check if we've reached the max message limit
                if max_messages is not None and processed_count >= max_messages:
                    break
        
        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        except Exception as e:
            logger.error(
                "Unexpected error in consume loop",
                context={'error': str(e)},
                exc_info=True
            )
        finally:
            logger.info(
                "Message consumption completed",
                context={
                    'processed': processed_count,
                    'stored': stored_count,
                    'failed': failed_count
                }
            )
        
        return {
            'processed': processed_count,
            'failed': failed_count,
            'stored': stored_count
        }
    
    def validate_message(self, message: Dict[str, Any], topic: str) -> bool:
        """
        Validate message schema before storing.
        
        Args:
            message: Message data dictionary
            topic: Kafka topic name
            
        Returns:
            True if valid, False otherwise
        """
        schema = self.topic_schema_map.get(topic)
        
        if not schema:
            logger.warning(f"No schema defined for topic: {topic}")
            return False
        
        # Check required fields
        required_fields = schema['required_fields']
        message_fields = set(message.keys())
        
        missing_fields = required_fields - message_fields
        if missing_fields:
            logger.error(
                "Message missing required fields",
                context={
                    'topic': topic,
                    'missing_fields': list(missing_fields),
                    'message_fields': list(message_fields)
                }
            )
            return False
        
        # Check field types
        field_types = schema['field_types']
        for field, expected_type in field_types.items():
            if field in message:
                value = message[field]
                if not isinstance(value, expected_type):
                    logger.error(
                        "Message field has incorrect type",
                        context={
                            'topic': topic,
                            'field': field,
                            'expected_type': str(expected_type),
                            'actual_type': str(type(value)),
                            'value': str(value)
                        }
                    )
                    return False
        
        return True
    
    def _store_message(self, message: Dict[str, Any], collection_name: str, max_retries: int = 3) -> bool:
        """
        Store message in MongoDB with retry logic.
        
        Args:
            message: Message data to store
            collection_name: MongoDB collection name
            max_retries: Maximum number of retry attempts
            
        Returns:
            True if stored successfully, False otherwise
        """
        collection = self.db[collection_name]
        
        # Add created_at timestamp if not present
        if 'created_at' not in message:
            message['created_at'] = datetime.utcnow().isoformat()
        
        # Retry logic with exponential backoff
        for attempt in range(max_retries):
            try:
                result = collection.insert_one(message)
                
                if result.inserted_id:
                    return True
                else:
                    logger.warning(
                        "Insert operation did not return inserted_id",
                        context={'collection': collection_name, 'attempt': attempt + 1}
                    )
                    
            except PyMongoError as e:
                delay = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                logger.warning(
                    "MongoDB insert failed, retrying",
                    context={
                        'collection': collection_name,
                        'attempt': attempt + 1,
                        'max_retries': max_retries,
                        'delay': delay,
                        'error': str(e)
                    }
                )
                
                if attempt < max_retries - 1:
                    time.sleep(delay)
                else:
                    logger.error(
                        "Failed to store message after all retries",
                        context={
                            'collection': collection_name,
                            'error': str(e)
                        },
                        exc_info=True
                    )
            except Exception as e:
                logger.error(
                    "Unexpected error storing message",
                    context={
                        'collection': collection_name,
                        'error': str(e)
                    },
                    exc_info=True
                )
                return False
        
        return False
    
    def close(self):
        """Close the consumer and release resources."""
        try:
            self.consumer.close()
            logger.info("KafkaDataConsumer closed successfully")
        except Exception as e:
            logger.error(
                "Error closing consumer",
                context={'error': str(e)},
                exc_info=True
            )


def create_kafka_consumer(config: Dict[str, Any]) -> KafkaConsumer:
    """
    Create and configure a Kafka consumer instance.
    
    Args:
        config: Configuration dictionary containing Kafka settings
        
    Returns:
        Configured KafkaConsumer instance
    """
    kafka_config = {
        'bootstrap_servers': config.get('kafka_bootstrap_servers', 'localhost:9092'),
        'group_id': config.get('kafka_consumer_group', 'stock_ai_consumer'),
        'auto_offset_reset': config.get('kafka_auto_offset_reset', 'earliest'),
        'enable_auto_commit': False,  # Manual commit for better control
        'value_deserializer': lambda x: x,  # We'll handle JSON decoding manually
        'consumer_timeout_ms': config.get('kafka_consumer_timeout_ms', 10000)
    }
    
    topics = config.get('kafka_topics', ['stock_prices_raw', 'stock_news_raw'])
    
    consumer = KafkaConsumer(*topics, **kafka_config)
    
    logger.info(
        "Kafka consumer created",
        context={
            'topics': topics,
            'bootstrap_servers': kafka_config['bootstrap_servers'],
            'group_id': kafka_config['group_id']
        }
    )
    
    return consumer


def create_mongo_client(config: Dict[str, Any]) -> MongoClient:
    """
    Create and configure a MongoDB client instance.
    
    Args:
        config: Configuration dictionary containing MongoDB settings
        
    Returns:
        Configured MongoClient instance
    """
    mongo_uri = config.get('mongo_uri', 'mongodb://localhost:27017')
    
    client = MongoClient(mongo_uri)
    
    # Test connection
    try:
        client.admin.command('ping')
        logger.info(
            "MongoDB connection established",
            context={'uri': mongo_uri}
        )
    except Exception as e:
        logger.error(
            "Failed to connect to MongoDB",
            context={'uri': mongo_uri, 'error': str(e)},
            exc_info=True
        )
        raise
    
    return client


def main():
    """
    Main entry point for the Kafka consumer service.
    """
    logger.info("Starting Kafka Data Consumer service")
    
    try:
        # Load configuration
        config = get_config()
        
        # Create Kafka consumer
        consumer = create_kafka_consumer(config)
        
        # Create MongoDB client
        mongo_client = create_mongo_client(config)
        
        # Create consumer instance
        kafka_data_consumer = KafkaDataConsumer(
            consumer=consumer,
            mongo_client=mongo_client,
            database_name=config.get('mongo_database', 'vietnam_stock_ai')
        )
        
        # Start consuming messages
        logger.info("Starting message consumption loop")
        stats = kafka_data_consumer.consume_and_store()
        
        logger.info(
            "Consumer finished",
            context=stats
        )
        
    except KeyboardInterrupt:
        logger.info("Consumer service interrupted by user")
    except Exception as e:
        logger.error(
            "Consumer service failed",
            context={'error': str(e)},
            exc_info=True
        )
        raise
    finally:
        # Cleanup
        try:
            if 'kafka_data_consumer' in locals():
                kafka_data_consumer.close()
            if 'mongo_client' in locals():
                mongo_client.close()
        except Exception as e:
            logger.error(
                "Error during cleanup",
                context={'error': str(e)},
                exc_info=True
            )


if __name__ == "__main__":
    main()