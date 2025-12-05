"""Pytest configuration and shared fixtures."""
import os
import sys
import pytest
from pathlib import Path



# Import utilities
from  tests.infrastructure.utils.wait_for_services import wait_for_all_services
from tests.infrastructure.utils.docker_helpers import check_services_running
from tests.infrastructure.fixtures.stock_companies import load_companies
from tests.infrastructure.fixtures.stock_prices import load_prices
from tests.infrastructure.fixtures.stock_news import load_news


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment before running tests."""
    # Load environment variables
    from dotenv import load_dotenv
    env_path = project_root / "infrastructure" / ".env"
    load_dotenv(env_path)
    
    # Check if services are running
    if not check_services_running():
        pytest.exit("Infrastructure services are not running. Please start them first.")
    
    # Wait for all services to be ready
    wait_for_all_services()
    
    yield
    
    # Cleanup after all tests


@pytest.fixture(scope="session")
def mongodb_client():
    """MongoDB client fixture."""
    from pymongo import MongoClient
    
    connection_string = os.getenv("MONGODB_CONNECTION_STRING", 
                                   "mongodb://admin:StockAIMongoDB@127.0.0.1:27017/stock_ai?authSource=admin")
    client = MongoClient(connection_string)
    
    yield client
    
    client.close()


@pytest.fixture(scope="session")
def redis_client():
    """Redis client fixture."""
    import redis
    
    password = os.getenv("REDIS_PASSWORD", "StockAIRedis")
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", "6379"))
    client = redis.Redis(host=host, port=port, password=password, decode_responses=True)
    
    yield client
    
    client.close()


@pytest.fixture(scope="session")
def kafka_producer():
    """Kafka producer fixture."""
    from kafka import KafkaProducer
    import json
    
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    yield producer
    
    producer.close()


@pytest.fixture(scope="session")
def kafka_consumer():
    """Kafka consumer fixture."""
    from kafka import KafkaConsumer
    import json
    
    consumer = KafkaConsumer(
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        consumer_timeout_ms=5000
    )
    
    yield consumer
    
    consumer.close()


@pytest.fixture(scope="session")
def elasticsearch_client():
    """Elasticsearch client fixture."""
    from elasticsearch import Elasticsearch
    
    client = Elasticsearch(['http://localhost:9200'])
    
    yield client
    
    client.close()


@pytest.fixture(scope="session")
def sample_companies():
    """Load sample company data."""
    return load_companies()


@pytest.fixture(scope="session")
def sample_prices():
    """Load sample price data."""
    return load_prices()


@pytest.fixture(scope="session")
def sample_news():
    """Load sample news data."""
    return load_news()


@pytest.fixture
def clean_mongodb(mongodb_client):
    """Clean MongoDB test collections before each test."""
    db = mongodb_client.stock_ai
    
    # Clean test collections
    test_collections = ['test_stocks', 'test_prices', 'test_news']
    for collection in test_collections:
        db[collection].delete_many({})
    
    yield db
    
    # Cleanup after test
    for collection in test_collections:
        db[collection].delete_many({})


@pytest.fixture
def clean_redis(redis_client):
    """Clean Redis test keys before each test."""
    # Delete test keys
    for key in redis_client.scan_iter("test:*"):
        redis_client.delete(key)
    
    yield redis_client
    
    # Cleanup after test
    for key in redis_client.scan_iter("test:*"):
        redis_client.delete(key)
