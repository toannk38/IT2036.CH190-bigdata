"""Wait for services to be ready."""
import os
import time
import pymongo
import redis
from kafka import KafkaProducer
from elasticsearch import Elasticsearch


def wait_for_mongodb(max_wait=60):
    """Wait for MongoDB to be ready."""
    connection_string = os.getenv(
        "MONGODB_CONNECTION_STRING",
        "mongodb://admin:StockAIMongoDB@localhost:27017/stock_ai?authSource=admin"
    )
    start = time.time()
    while time.time() - start < max_wait:
        try:
            client = pymongo.MongoClient(
                connection_string,
                serverSelectionTimeoutMS=2000
            )
            client.server_info()
            print("✓ MongoDB is ready")
            return True
        except Exception:
            time.sleep(2)
    print("✗ MongoDB timeout")
    return False


def wait_for_redis(max_wait=30):
    """Wait for Redis to be ready."""
    password = os.getenv("REDIS_PASSWORD", "StockAIRedis")
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", "6379"))
    
    start = time.time()
    while time.time() - start < max_wait:
        try:
            client = redis.Redis(host=host, port=port, password=password)
            client.ping()
            print("✓ Redis is ready")
            return True
        except Exception:
            time.sleep(2)
    print("✗ Redis timeout")
    return False


def wait_for_kafka(max_wait=60):
    """Wait for Kafka to be ready."""
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(",")
    
    start = time.time()
    while time.time() - start < max_wait:
        try:
            producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                request_timeout_ms=5000
            )
            producer.close()
            print("✓ Kafka is ready")
            return True
        except Exception:
            time.sleep(2)
    print("✗ Kafka timeout")
    return False


def wait_for_elasticsearch(max_wait=60):
    """Wait for Elasticsearch to be ready."""
    host = os.getenv("ELASTICSEARCH_HOST", "localhost")
    port = os.getenv("ELASTICSEARCH_PORT", "9200")
    
    start = time.time()
    while time.time() - start < max_wait:
        try:
            client = Elasticsearch([f'http://{host}:{port}'])
            if client.ping():
                print("✓ Elasticsearch is ready")
                return True
        except Exception:
            time.sleep(2)
    print("✗ Elasticsearch timeout")
    return False


def wait_for_all_services():
    """Wait for all services to be ready."""
    print("\nWaiting for services to be ready...")
    
    services = [
        wait_for_mongodb,
        wait_for_redis,
        wait_for_kafka,
        wait_for_elasticsearch
    ]
    
    for service in services:
        if not service():
            raise Exception(f"Service {service.__name__} failed to start")
    
    print("✓ All services are ready\n")
