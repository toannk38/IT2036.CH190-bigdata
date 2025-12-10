"""
Property-based tests for KafkaDataConsumer.

Tests universal properties that should hold across all valid executions.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock, MagicMock, patch
from kafka import KafkaConsumer
from kafka.structs import TopicPartition
from pymongo import MongoClient
import json
from datetime import datetime

from src.consumers.kafka_consumer import KafkaDataConsumer


# Hypothesis strategies for generating test data
symbol_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Lu',)),  # Uppercase letters
    min_size=3,
    max_size=5
)

timestamp_strategy = st.datetimes(
    min_value=datetime(2024, 1, 1),
    max_value=datetime(2024, 12, 31)
).map(lambda dt: dt.isoformat())

price_strategy = st.floats(min_value=1000, max_value=1000000, allow_nan=False, allow_infinity=False)
volume_strategy = st.integers(min_value=0, max_value=100000000)

# Strategy for generating valid price data messages
price_message_strategy = st.fixed_dictionaries({
    'symbol': symbol_strategy,
    'timestamp': timestamp_strategy,
    'open': price_strategy,
    'close': price_strategy,
    'high': price_strategy,
    'low': price_strategy,
    'volume': volume_strategy
})


def create_mock_kafka_consumer(messages_by_topic):
    """
    Create a mock Kafka consumer with pre-configured messages.
    
    Args:
        messages_by_topic: Dict mapping topic names to lists of message data
        
    Returns:
        Mock KafkaConsumer instance
    """
    consumer = Mock(spec=KafkaConsumer)
    consumer.subscription.return_value = list(messages_by_topic.keys())
    
    # Track poll calls
    poll_count = [0]
    
    def mock_poll(timeout_ms, max_records):
        """Mock poll that returns messages on first call, empty on subsequent calls."""
        poll_count[0] += 1
        
        if poll_count[0] == 1:
            # First poll: return all messages
            result = {}
            for topic, messages in messages_by_topic.items():
                tp = TopicPartition(topic, 0)
                
                # Create mock ConsumerRecord objects
                mock_records = []
                for idx, msg_data in enumerate(messages):
                    record = Mock()
                    record.topic = topic
                    record.partition = 0
                    record.offset = idx
                    record.value = json.dumps(msg_data).encode('utf-8')
                    mock_records.append(record)
                
                result[tp] = mock_records
            
            return result
        else:
            # Subsequent polls: return empty
            return {}
    
    consumer.poll = Mock(side_effect=mock_poll)
    consumer.commit = Mock()
    consumer.close = Mock()
    
    return consumer


def create_mock_mongo_client():
    """Create a mock MongoDB client that stores data in memory."""
    client = Mock(spec=MongoClient)
    
    # In-memory storage for collections
    storage = {}
    
    def get_database(db_name):
        """Mock database accessor."""
        db = Mock()
        
        def get_collection(collection_name):
            """Mock collection accessor."""
            collection = Mock()
            
            # Initialize storage for this collection if needed
            if collection_name not in storage:
                storage[collection_name] = []
            
            def insert_one(document):
                """Mock insert that stores document in memory."""
                # Make a copy to avoid mutation issues
                doc_copy = document.copy()
                storage[collection_name].append(doc_copy)
                
                result = Mock()
                result.inserted_id = len(storage[collection_name])
                return result
            
            def find(query=None):
                """Mock find that returns stored documents."""
                return storage[collection_name]
            
            collection.insert_one = Mock(side_effect=insert_one)
            collection.find = Mock(side_effect=find)
            
            return collection
        
        db.__getitem__ = Mock(side_effect=get_collection)
        return db
    
    client.__getitem__ = Mock(side_effect=get_database)
    
    # Store reference to storage for test assertions
    client._test_storage = storage
    
    return client


@given(price_messages=st.lists(price_message_strategy, min_size=1, max_size=20))
@settings(max_examples=100, deadline=None)
def test_property_7_price_data_round_trip_preservation(price_messages):
    """
    **Feature: vietnam-stock-ai-backend, Property 7: Price data round-trip preservation**
    **Validates: Requirements 1.4**
    
    For any price data published to Kafka topic `stock_prices_raw`, when consumed 
    and stored in MongoDB collection `price_history`, all original fields should 
    be preserved.
    
    This property verifies that:
    1. All required fields from the Kafka message are present in MongoDB
    2. Field values are preserved exactly (no data loss or corruption)
    3. The round-trip through Kafka and MongoDB maintains data integrity
    """
    # Create mocks
    mock_mongo_client = create_mock_mongo_client()
    mock_kafka_consumer = create_mock_kafka_consumer({
        'stock_prices_raw': price_messages
    })
    
    # Create consumer
    consumer = KafkaDataConsumer(
        consumer=mock_kafka_consumer,
        mongo_client=mock_mongo_client,
        database_name='test_db'
    )
    
    # Consume and store messages
    stats = consumer.consume_and_store(max_messages=len(price_messages))
    
    # Property verification: All messages should be stored successfully
    assert stats['stored'] == len(price_messages), \
        f"Expected {len(price_messages)} messages to be stored, but got {stats['stored']}"
    
    # Verify that all original fields are preserved in MongoDB
    stored_documents = mock_mongo_client._test_storage.get('price_history', [])
    
    assert len(stored_documents) == len(price_messages), \
        f"Expected {len(price_messages)} documents in MongoDB, but got {len(stored_documents)}"
    
    # Check each stored document against original message
    for original_msg, stored_doc in zip(price_messages, stored_documents):
        # Verify all original fields are present
        for field in ['symbol', 'timestamp', 'open', 'close', 'high', 'low', 'volume']:
            assert field in stored_doc, \
                f"Field '{field}' missing from stored document"
            
            # Verify field values are preserved
            assert stored_doc[field] == original_msg[field], \
                f"Field '{field}' value changed: expected {original_msg[field]}, got {stored_doc[field]}"


@given(price_messages=st.lists(price_message_strategy, min_size=1, max_size=20))
@settings(max_examples=100, deadline=None)
def test_property_8_price_data_completeness(price_messages):
    """
    **Feature: vietnam-stock-ai-backend, Property 8: Price data completeness**
    **Validates: Requirements 1.5**
    
    For any price data stored in MongoDB collection `price_history`, the document 
    should contain all required fields: timestamp, symbol, open, close, high, low, 
    and volume.
    
    This property verifies that:
    1. Every stored document has all required fields
    2. No required fields are missing or null
    3. Data completeness is maintained throughout the pipeline
    """
    # Create mocks
    mock_mongo_client = create_mock_mongo_client()
    mock_kafka_consumer = create_mock_kafka_consumer({
        'stock_prices_raw': price_messages
    })
    
    # Create consumer
    consumer = KafkaDataConsumer(
        consumer=mock_kafka_consumer,
        mongo_client=mock_mongo_client,
        database_name='test_db'
    )
    
    # Consume and store messages
    stats = consumer.consume_and_store(max_messages=len(price_messages))
    
    # Property verification: All stored documents should have required fields
    stored_documents = mock_mongo_client._test_storage.get('price_history', [])
    
    required_fields = {'timestamp', 'symbol', 'open', 'close', 'high', 'low', 'volume'}
    
    for idx, doc in enumerate(stored_documents):
        doc_fields = set(doc.keys())
        
        # Check that all required fields are present
        missing_fields = required_fields - doc_fields
        assert not missing_fields, \
            f"Document {idx} missing required fields: {missing_fields}"
        
        # Check that required fields are not None
        for field in required_fields:
            assert doc[field] is not None, \
                f"Document {idx} has None value for required field '{field}'"


# Strategy for generating valid news data messages
news_message_strategy = st.fixed_dictionaries({
    'symbol': symbol_strategy,
    'title': st.text(min_size=10, max_size=100),
    'content': st.text(min_size=50, max_size=500),
    'source': st.sampled_from(['cafef.vn', 'vnexpress.net', 'vnstock', 'vietstock.vn']),
    'published_at': timestamp_strategy,
    'collected_at': timestamp_strategy
})


@given(news_messages=st.lists(news_message_strategy, min_size=1, max_size=20))
@settings(max_examples=100, deadline=None)
def test_property_11_news_data_round_trip_preservation(news_messages):
    """
    **Feature: vietnam-stock-ai-backend, Property 11: News data round-trip preservation**
    **Validates: Requirements 3.4**
    
    For any news data published to Kafka topic `stock_news_raw`, when consumed 
    and stored in MongoDB collection `news`, all original fields should be preserved.
    
    This property verifies that:
    1. All required fields from the Kafka message are present in MongoDB
    2. Field values are preserved exactly (no data loss or corruption)
    3. The round-trip through Kafka and MongoDB maintains data integrity
    """
    # Create mocks
    mock_mongo_client = create_mock_mongo_client()
    mock_kafka_consumer = create_mock_kafka_consumer({
        'stock_news_raw': news_messages
    })
    
    # Create consumer
    consumer = KafkaDataConsumer(
        consumer=mock_kafka_consumer,
        mongo_client=mock_mongo_client,
        database_name='test_db'
    )
    
    # Consume and store messages
    stats = consumer.consume_and_store(max_messages=len(news_messages))
    
    # Property verification: All messages should be stored successfully
    assert stats['stored'] == len(news_messages), \
        f"Expected {len(news_messages)} messages to be stored, but got {stats['stored']}"
    
    # Verify that all original fields are preserved in MongoDB
    stored_documents = mock_mongo_client._test_storage.get('news', [])
    
    assert len(stored_documents) == len(news_messages), \
        f"Expected {len(news_messages)} documents in MongoDB, but got {len(stored_documents)}"
    
    # Check each stored document against original message
    for original_msg, stored_doc in zip(news_messages, stored_documents):
        # Verify all original fields are present
        for field in ['symbol', 'title', 'content', 'source', 'published_at', 'collected_at']:
            assert field in stored_doc, \
                f"Field '{field}' missing from stored document"
            
            # Verify field values are preserved
            assert stored_doc[field] == original_msg[field], \
                f"Field '{field}' value changed: expected {original_msg[field]}, got {stored_doc[field]}"


@given(news_messages=st.lists(news_message_strategy, min_size=1, max_size=20))
@settings(max_examples=100, deadline=None)
def test_property_12_news_data_completeness(news_messages):
    """
    **Feature: vietnam-stock-ai-backend, Property 12: News data completeness**
    **Validates: Requirements 3.5**
    
    For any news data stored in MongoDB collection `news`, the document should 
    contain all required fields: timestamp, title, content, source, and related 
    stock symbols.
    
    This property verifies that:
    1. Every stored document has all required fields
    2. No required fields are missing or null
    3. Data completeness is maintained throughout the pipeline
    """
    # Create mocks
    mock_mongo_client = create_mock_mongo_client()
    mock_kafka_consumer = create_mock_kafka_consumer({
        'stock_news_raw': news_messages
    })
    
    # Create consumer
    consumer = KafkaDataConsumer(
        consumer=mock_kafka_consumer,
        mongo_client=mock_mongo_client,
        database_name='test_db'
    )
    
    # Consume and store messages
    stats = consumer.consume_and_store(max_messages=len(news_messages))
    
    # Property verification: All stored documents should have required fields
    stored_documents = mock_mongo_client._test_storage.get('news', [])
    
    # Note: The requirement mentions "timestamp" but the schema uses "published_at" and "collected_at"
    # We'll check for the fields that are actually in the schema
    required_fields = {'symbol', 'title', 'content', 'source', 'published_at', 'collected_at'}
    
    for idx, doc in enumerate(stored_documents):
        doc_fields = set(doc.keys())
        
        # Check that all required fields are present
        missing_fields = required_fields - doc_fields
        assert not missing_fields, \
            f"Document {idx} missing required fields: {missing_fields}"
        
        # Check that required fields are not None
        for field in required_fields:
            assert doc[field] is not None, \
                f"Document {idx} has None value for required field '{field}'"
