"""Kafka unit tests."""
import pytest
import time
from kafka import KafkaConsumer


@pytest.mark.unit
def test_kafka_producer_connection(kafka_producer):
    """Test Kafka producer connection."""
    assert kafka_producer.bootstrap_connected()


@pytest.mark.unit
def test_send_message(kafka_producer):
    """Test sending message to Kafka."""
    topic = "test_topic"
    message = {"test": "data", "timestamp": time.time()}
    
    future = kafka_producer.send(topic, message)
    result = future.get(timeout=10)
    
    assert result is not None


@pytest.mark.unit
def test_send_stock_price(kafka_producer, sample_prices):
    """Test sending stock price data."""
    topic = "stock_prices_raw"
    price = sample_prices[0]
    
    future = kafka_producer.send(topic, price)
    result = future.get(timeout=10)
    
    assert result.topic == topic


@pytest.mark.unit
def test_send_multiple_messages(kafka_producer, sample_prices):
    """Test sending multiple messages."""
    topic = "test_prices"
    prices = sample_prices[:10]
    
    for price in prices:
        kafka_producer.send(topic, price)
    
    kafka_producer.flush()


@pytest.mark.unit
def test_consumer_subscribe():
    """Test Kafka consumer subscription."""
    consumer = KafkaConsumer(
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        consumer_timeout_ms=1000
    )
    
    consumer.subscribe(['test_topic'])
    assert 'test_topic' in consumer.subscription()
    
    consumer.close()


@pytest.mark.unit
def test_produce_consume(kafka_producer):
    """Test produce and consume message."""
    topic = "test_produce_consume"
    message = {"test": "message", "id": 123}
    
    # Produce
    kafka_producer.send(topic, message)
    kafka_producer.flush()
    
    # Consume
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        consumer_timeout_ms=5000,
        value_deserializer=lambda m: __import__('json').loads(m.decode('utf-8'))
    )
    
    messages = []
    for msg in consumer:
        messages.append(msg.value)
        break
    
    consumer.close()
    
    assert len(messages) > 0


@pytest.mark.unit
def test_send_news_data(kafka_producer, sample_news):
    """Test sending news data."""
    topic = "stock_news_raw"
    news = sample_news[0]
    
    future = kafka_producer.send(topic, news)
    result = future.get(timeout=10)
    
    assert result.topic == topic
