"""
Unit tests for KafkaDataConsumer.

Tests specific functionality and edge cases.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from kafka import KafkaConsumer
from kafka.structs import TopicPartition
from kafka.errors import KafkaError
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import json

from src.consumers.kafka_consumer import KafkaDataConsumer


@pytest.fixture
def mock_kafka_consumer():
    """Create a mock Kafka consumer."""
    consumer = Mock(spec=KafkaConsumer)
    consumer.subscription.return_value = ['stock_prices_raw', 'stock_news_raw']
    consumer.poll.return_value = {}
    consumer.commit.return_value = None
    consumer.close.return_value = None
    return consumer


@pytest.fixture
def mock_mongo_client():
    """Create a mock MongoDB client."""
    client = Mock(spec=MongoClient)
    db = Mock()
    collection = Mock()
    
    # Mock insert_one to return a result with inserted_id
    result = Mock()
    result.inserted_id = 'test_id_123'
    collection.insert_one.return_value = result
    
    db.__getitem__ = Mock(return_value=collection)
    client.__getitem__ = Mock(return_value=db)
    
    return client


@pytest.fixture
def kafka_data_consumer(mock_kafka_consumer, mock_mongo_client):
    """Create a KafkaDataConsumer instance with mocked dependencies."""
    return KafkaDataConsumer(
        consumer=mock_kafka_consumer,
        mongo_client=mock_mongo_client,
        database_name='test_db'
    )


def test_kafka_consumer_initialization(kafka_data_consumer):
    """Test that KafkaDataConsumer initializes correctly."""
    assert kafka_data_consumer.consumer is not None
    assert kafka_data_consumer.mongo_client is not None
    assert kafka_data_consumer.db is not None
    assert 'stock_prices_raw' in kafka_data_consumer.topic_collection_map
    assert 'stock_news_raw' in kafka_data_consumer.topic_collection_map


def test_consume_and_store_with_valid_price_data(mock_kafka_consumer, mock_mongo_client):
    """Test consuming and storing valid price data."""
    # Setup: Create price message
    price_message = {
        'symbol': 'VNM',
        'timestamp': '2024-01-15T10:00:00Z',
        'open': 50000.0,
        'close': 51000.0,
        'high': 52000.0,
        'low': 49000.0,
        'volume': 1000000
    }
    
    # Mock Kafka message
    mock_record = Mock()
    mock_record.topic = 'stock_prices_raw'
    mock_record.partition = 0
    mock_record.offset = 0
    mock_record.value = json.dumps(price_message).encode('utf-8')
    
    tp = TopicPartition('stock_prices_raw', 0)
    
    # Configure poll to return message on first call, empty on second
    poll_count = [0]
    def mock_poll(timeout_ms, max_records):
        poll_count[0] += 1
        if poll_count[0] == 1:
            return {tp: [mock_record]}
        return {}
    
    mock_kafka_consumer.poll = Mock(side_effect=mock_poll)
    
    # Create consumer
    consumer = KafkaDataConsumer(
        consumer=mock_kafka_consumer,
        mongo_client=mock_mongo_client,
        database_name='test_db'
    )
    
    # Execute
    stats = consumer.consume_and_store(max_messages=1)
    
    # Assert
    assert stats['processed'] == 1
    assert stats['stored'] == 1
    assert stats['failed'] == 0
    
    # Verify MongoDB insert was called
    db = mock_mongo_client['test_db']
    collection = db['price_history']
    assert collection.insert_one.called


def test_consume_and_store_with_valid_news_data(mock_kafka_consumer, mock_mongo_client):
    """Test consuming and storing valid news data."""
    # Setup: Create news message
    news_message = {
        'symbol': 'VNM',
        'title': 'VNM announces Q4 results',
        'content': 'Company reports strong growth...',
        'source': 'cafef.vn',
        'published_at': '2024-01-15T08:00:00Z',
        'collected_at': '2024-01-15T08:05:00Z'
    }
    
    # Mock Kafka message
    mock_record = Mock()
    mock_record.topic = 'stock_news_raw'
    mock_record.partition = 0
    mock_record.offset = 0
    mock_record.value = json.dumps(news_message).encode('utf-8')
    
    tp = TopicPartition('stock_news_raw', 0)
    
    # Configure poll to return message on first call, empty on second
    poll_count = [0]
    def mock_poll(timeout_ms, max_records):
        poll_count[0] += 1
        if poll_count[0] == 1:
            return {tp: [mock_record]}
        return {}
    
    mock_kafka_consumer.poll = Mock(side_effect=mock_poll)
    
    # Create consumer
    consumer = KafkaDataConsumer(
        consumer=mock_kafka_consumer,
        mongo_client=mock_mongo_client,
        database_name='test_db'
    )
    
    # Execute
    stats = consumer.consume_and_store(max_messages=1)
    
    # Assert
    assert stats['processed'] == 1
    assert stats['stored'] == 1
    assert stats['failed'] == 0
    
    # Verify MongoDB insert was called
    db = mock_mongo_client['test_db']
    collection = db['news']
    assert collection.insert_one.called


def test_validate_message_with_valid_price_data(kafka_data_consumer):
    """Test message validation with valid price data."""
    message = {
        'symbol': 'VNM',
        'timestamp': '2024-01-15T10:00:00Z',
        'open': 50000.0,
        'close': 51000.0,
        'high': 52000.0,
        'low': 49000.0,
        'volume': 1000000
    }
    
    result = kafka_data_consumer.validate_message(message, 'stock_prices_raw')
    assert result is True


def test_validate_message_with_missing_fields(kafka_data_consumer):
    """Test message validation with missing required fields."""
    message = {
        'symbol': 'VNM',
        'timestamp': '2024-01-15T10:00:00Z',
        'open': 50000.0
        # Missing: close, high, low, volume
    }
    
    result = kafka_data_consumer.validate_message(message, 'stock_prices_raw')
    assert result is False


def test_validate_message_with_incorrect_types(kafka_data_consumer):
    """Test message validation with incorrect field types."""
    message = {
        'symbol': 'VNM',
        'timestamp': '2024-01-15T10:00:00Z',
        'open': '50000',  # Should be float, not string
        'close': 51000.0,
        'high': 52000.0,
        'low': 49000.0,
        'volume': 1000000
    }
    
    result = kafka_data_consumer.validate_message(message, 'stock_prices_raw')
    assert result is False


def test_validate_message_with_valid_news_data(kafka_data_consumer):
    """Test message validation with valid news data."""
    message = {
        'symbol': 'VNM',
        'title': 'VNM announces Q4 results',
        'content': 'Company reports strong growth...',
        'source': 'cafef.vn',
        'published_at': '2024-01-15T08:00:00Z',
        'collected_at': '2024-01-15T08:05:00Z'
    }
    
    result = kafka_data_consumer.validate_message(message, 'stock_news_raw')
    assert result is True


def test_validate_message_with_unknown_topic(kafka_data_consumer):
    """Test message validation with unknown topic."""
    message = {'some': 'data'}
    
    result = kafka_data_consumer.validate_message(message, 'unknown_topic')
    assert result is False


def test_consume_with_invalid_json(mock_kafka_consumer, mock_mongo_client):
    """Test handling of invalid JSON in Kafka message."""
    # Mock Kafka message with invalid JSON
    mock_record = Mock()
    mock_record.topic = 'stock_prices_raw'
    mock_record.partition = 0
    mock_record.offset = 0
    mock_record.value = b'invalid json {'  # Invalid JSON
    
    tp = TopicPartition('stock_prices_raw', 0)
    
    # Configure poll to return message on first call, empty on second
    poll_count = [0]
    def mock_poll(timeout_ms, max_records):
        poll_count[0] += 1
        if poll_count[0] == 1:
            return {tp: [mock_record]}
        return {}
    
    mock_kafka_consumer.poll = Mock(side_effect=mock_poll)
    
    # Create consumer
    consumer = KafkaDataConsumer(
        consumer=mock_kafka_consumer,
        mongo_client=mock_mongo_client,
        database_name='test_db'
    )
    
    # Execute
    stats = consumer.consume_and_store(max_messages=1)
    
    # Assert
    assert stats['processed'] == 1
    assert stats['stored'] == 0
    assert stats['failed'] == 1


def test_consume_with_validation_failure(mock_kafka_consumer, mock_mongo_client):
    """Test handling of message validation failure."""
    # Setup: Create invalid price message (missing required fields)
    invalid_message = {
        'symbol': 'VNM',
        'timestamp': '2024-01-15T10:00:00Z'
        # Missing: open, close, high, low, volume
    }
    
    # Mock Kafka message
    mock_record = Mock()
    mock_record.topic = 'stock_prices_raw'
    mock_record.partition = 0
    mock_record.offset = 0
    mock_record.value = json.dumps(invalid_message).encode('utf-8')
    
    tp = TopicPartition('stock_prices_raw', 0)
    
    # Configure poll to return message on first call, empty on second
    poll_count = [0]
    def mock_poll(timeout_ms, max_records):
        poll_count[0] += 1
        if poll_count[0] == 1:
            return {tp: [mock_record]}
        return {}
    
    mock_kafka_consumer.poll = Mock(side_effect=mock_poll)
    
    # Create consumer
    consumer = KafkaDataConsumer(
        consumer=mock_kafka_consumer,
        mongo_client=mock_mongo_client,
        database_name='test_db'
    )
    
    # Execute
    stats = consumer.consume_and_store(max_messages=1)
    
    # Assert
    assert stats['processed'] == 1
    assert stats['stored'] == 0
    assert stats['failed'] == 1


def test_offset_recovery_after_failure(mock_kafka_consumer, mock_mongo_client):
    """Test that consumer commits offsets after processing batch."""
    # Setup: Create valid price message
    price_message = {
        'symbol': 'VNM',
        'timestamp': '2024-01-15T10:00:00Z',
        'open': 50000.0,
        'close': 51000.0,
        'high': 52000.0,
        'low': 49000.0,
        'volume': 1000000
    }
    
    # Mock Kafka message
    mock_record = Mock()
    mock_record.topic = 'stock_prices_raw'
    mock_record.partition = 0
    mock_record.offset = 0
    mock_record.value = json.dumps(price_message).encode('utf-8')
    
    tp = TopicPartition('stock_prices_raw', 0)
    
    # Configure poll to return message on first call, empty on second
    poll_count = [0]
    def mock_poll(timeout_ms, max_records):
        poll_count[0] += 1
        if poll_count[0] == 1:
            return {tp: [mock_record]}
        return {}
    
    mock_kafka_consumer.poll = Mock(side_effect=mock_poll)
    
    # Create consumer
    consumer = KafkaDataConsumer(
        consumer=mock_kafka_consumer,
        mongo_client=mock_mongo_client,
        database_name='test_db'
    )
    
    # Execute
    stats = consumer.consume_and_store(max_messages=1)
    
    # Assert: Verify that commit was called
    assert mock_kafka_consumer.commit.called
    assert stats['stored'] == 1


def test_mongodb_retry_on_failure(mock_kafka_consumer):
    """Test retry logic when MongoDB insert fails."""
    # Setup: Create mock MongoDB client that fails on first attempts
    mock_mongo_client = Mock(spec=MongoClient)
    db = Mock()
    collection = Mock()
    
    # Configure insert_one to fail twice, then succeed
    attempt_count = [0]
    def mock_insert_one(document):
        attempt_count[0] += 1
        if attempt_count[0] < 3:
            raise PyMongoError("Connection error")
        result = Mock()
        result.inserted_id = 'test_id_123'
        return result
    
    collection.insert_one = Mock(side_effect=mock_insert_one)
    db.__getitem__ = Mock(return_value=collection)
    mock_mongo_client.__getitem__ = Mock(return_value=db)
    
    # Setup: Create valid price message
    price_message = {
        'symbol': 'VNM',
        'timestamp': '2024-01-15T10:00:00Z',
        'open': 50000.0,
        'close': 51000.0,
        'high': 52000.0,
        'low': 49000.0,
        'volume': 1000000
    }
    
    # Mock Kafka message
    mock_record = Mock()
    mock_record.topic = 'stock_prices_raw'
    mock_record.partition = 0
    mock_record.offset = 0
    mock_record.value = json.dumps(price_message).encode('utf-8')
    
    tp = TopicPartition('stock_prices_raw', 0)
    
    # Configure poll to return message on first call, empty on second
    poll_count = [0]
    def mock_poll(timeout_ms, max_records):
        poll_count[0] += 1
        if poll_count[0] == 1:
            return {tp: [mock_record]}
        return {}
    
    mock_kafka_consumer.poll = Mock(side_effect=mock_poll)
    
    # Create consumer
    consumer = KafkaDataConsumer(
        consumer=mock_kafka_consumer,
        mongo_client=mock_mongo_client,
        database_name='test_db'
    )
    
    # Execute
    stats = consumer.consume_and_store(max_messages=1)
    
    # Assert: Message should be stored after retries
    assert stats['stored'] == 1
    assert stats['failed'] == 0
    assert attempt_count[0] == 3  # Failed twice, succeeded on third attempt


def test_mongodb_failure_after_max_retries(mock_kafka_consumer):
    """Test that consumer gives up after max retries."""
    # Setup: Create mock MongoDB client that always fails
    mock_mongo_client = Mock(spec=MongoClient)
    db = Mock()
    collection = Mock()
    
    # Configure insert_one to always fail
    collection.insert_one.side_effect = PyMongoError("Connection error")
    db.__getitem__ = Mock(return_value=collection)
    mock_mongo_client.__getitem__ = Mock(return_value=db)
    
    # Setup: Create valid price message
    price_message = {
        'symbol': 'VNM',
        'timestamp': '2024-01-15T10:00:00Z',
        'open': 50000.0,
        'close': 51000.0,
        'high': 52000.0,
        'low': 49000.0,
        'volume': 1000000
    }
    
    # Mock Kafka message
    mock_record = Mock()
    mock_record.topic = 'stock_prices_raw'
    mock_record.partition = 0
    mock_record.offset = 0
    mock_record.value = json.dumps(price_message).encode('utf-8')
    
    tp = TopicPartition('stock_prices_raw', 0)
    
    # Configure poll to return message on first call, empty on second
    poll_count = [0]
    def mock_poll(timeout_ms, max_records):
        poll_count[0] += 1
        if poll_count[0] == 1:
            return {tp: [mock_record]}
        return {}
    
    mock_kafka_consumer.poll = Mock(side_effect=mock_poll)
    
    # Create consumer
    consumer = KafkaDataConsumer(
        consumer=mock_kafka_consumer,
        mongo_client=mock_mongo_client,
        database_name='test_db'
    )
    
    # Execute
    stats = consumer.consume_and_store(max_messages=1)
    
    # Assert: Message should fail after max retries
    assert stats['stored'] == 0
    assert stats['failed'] == 1
    assert collection.insert_one.call_count == 3  # Max retries


def test_consume_multiple_messages(mock_kafka_consumer, mock_mongo_client):
    """Test consuming multiple messages in a batch."""
    # Setup: Create multiple price messages
    messages = []
    for i in range(5):
        message = {
            'symbol': f'SYM{i}',
            'timestamp': '2024-01-15T10:00:00Z',
            'open': 50000.0 + i,
            'close': 51000.0 + i,
            'high': 52000.0 + i,
            'low': 49000.0 + i,
            'volume': 1000000 + i
        }
        
        mock_record = Mock()
        mock_record.topic = 'stock_prices_raw'
        mock_record.partition = 0
        mock_record.offset = i
        mock_record.value = json.dumps(message).encode('utf-8')
        messages.append(mock_record)
    
    tp = TopicPartition('stock_prices_raw', 0)
    
    # Configure poll to return all messages on first call, empty on second
    poll_count = [0]
    def mock_poll(timeout_ms, max_records):
        poll_count[0] += 1
        if poll_count[0] == 1:
            return {tp: messages}
        return {}
    
    mock_kafka_consumer.poll = Mock(side_effect=mock_poll)
    
    # Create consumer
    consumer = KafkaDataConsumer(
        consumer=mock_kafka_consumer,
        mongo_client=mock_mongo_client,
        database_name='test_db'
    )
    
    # Execute
    stats = consumer.consume_and_store(max_messages=5)
    
    # Assert
    assert stats['processed'] == 5
    assert stats['stored'] == 5
    assert stats['failed'] == 0


def test_consumer_close(kafka_data_consumer, mock_kafka_consumer):
    """Test that consumer closes properly."""
    kafka_data_consumer.close()
    assert mock_kafka_consumer.close.called


def test_consume_with_unknown_topic(mock_kafka_consumer, mock_mongo_client):
    """Test handling of messages from unknown topics."""
    # Setup: Create message for unknown topic
    message = {'some': 'data'}
    
    # Mock Kafka message
    mock_record = Mock()
    mock_record.topic = 'unknown_topic'
    mock_record.partition = 0
    mock_record.offset = 0
    mock_record.value = json.dumps(message).encode('utf-8')
    
    tp = TopicPartition('unknown_topic', 0)
    
    # Configure poll to return message on first call, empty on second
    poll_count = [0]
    def mock_poll(timeout_ms, max_records):
        poll_count[0] += 1
        if poll_count[0] == 1:
            return {tp: [mock_record]}
        return {}
    
    mock_kafka_consumer.poll = Mock(side_effect=mock_poll)
    
    # Create consumer
    consumer = KafkaDataConsumer(
        consumer=mock_kafka_consumer,
        mongo_client=mock_mongo_client,
        database_name='test_db'
    )
    
    # Execute
    stats = consumer.consume_and_store(max_messages=1)
    
    # Assert: Message should be skipped (not processed)
    assert stats['processed'] == 0
    assert stats['stored'] == 0
    assert stats['failed'] == 0
