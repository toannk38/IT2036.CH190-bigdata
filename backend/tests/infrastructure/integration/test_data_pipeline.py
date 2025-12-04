"""Data pipeline integration tests."""
import pytest
import time
from kafka import KafkaConsumer
import json


@pytest.mark.integration
def test_kafka_to_mongodb_pipeline(kafka_producer, clean_mongodb, sample_prices):
    """Test full pipeline: Kafka -> MongoDB."""
    topic = "test_pipeline"
    
    # Send data to Kafka
    for price in sample_prices[:10]:
        kafka_producer.send(topic, price)
    kafka_producer.flush()
    
    # Consume and save to MongoDB
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        consumer_timeout_ms=5000,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    
    saved_count = 0
    for message in consumer:
        clean_mongodb.test_prices.insert_one(message.value)
        saved_count += 1
        if saved_count >= 10:
            break
    
    consumer.close()
    
    # Verify data in MongoDB
    count = clean_mongodb.test_prices.count_documents({})
    assert count >= 10


@pytest.mark.integration
def test_price_data_flow(kafka_producer, clean_mongodb, sample_prices):
    """Test price data flow through pipeline."""
    topic = "stock_prices_raw"
    
    # Send prices
    prices = sample_prices[:5]
    for price in prices:
        kafka_producer.send(topic, price)
    kafka_producer.flush()
    
    time.sleep(2)
    
    # Simulate consumer saving to MongoDB
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='latest',
        consumer_timeout_ms=3000,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    
    for message in consumer:
        clean_mongodb.test_prices.insert_one(message.value)
    
    consumer.close()


@pytest.mark.integration
def test_news_data_flow(kafka_producer, clean_mongodb, sample_news):
    """Test news data flow through pipeline."""
    topic = "stock_news_raw"
    
    # Send news
    news_items = sample_news[:3]
    for news in news_items:
        kafka_producer.send(topic, news)
    kafka_producer.flush()
    
    time.sleep(2)


@pytest.mark.integration
def test_multiple_topics(kafka_producer, sample_prices, sample_news):
    """Test sending to multiple topics."""
    # Send to prices topic
    for price in sample_prices[:5]:
        kafka_producer.send("stock_prices_raw", price)
    
    # Send to news topic
    for news in sample_news[:3]:
        kafka_producer.send("stock_news_raw", news)
    
    kafka_producer.flush()
