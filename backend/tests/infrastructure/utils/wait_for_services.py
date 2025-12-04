"""Wait for services to be ready."""
import time
import pymongo
import redis
from kafka import KafkaProducer
from elasticsearch import Elasticsearch


def wait_for_mongodb(max_wait=60):
    """Wait for MongoDB to be ready."""
    start = time.time()
    while time.time() - start < max_wait:
        try:
            client = pymongo.MongoClient(
                "mongodb://admin:StockAI@MongoDB2024@localhost:27017/stock_ai?authSource=admin",
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
    start = time.time()
    while time.time() - start < max_wait:
        try:
            client = redis.Redis(host='localhost', port=6379, password='StockAI@Redis2024')
            client.ping()
            print("✓ Redis is ready")
            return True
        except Exception:
            time.sleep(2)
    print("✗ Redis timeout")
    return False


def wait_for_kafka(max_wait=60):
    """Wait for Kafka to be ready."""
    start = time.time()
    while time.time() - start < max_wait:
        try:
            producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
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
    start = time.time()
    while time.time() - start < max_wait:
        try:
            client = Elasticsearch(['http://localhost:9200'])
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
