#!/usr/bin/env python3
"""
Test script for Kafka Consumer Service
"""
import json
import time
import requests
from kafka import KafkaProducer

def test_kafka_producer():
    """Test sending messages to Kafka topics"""
    print("Testing Kafka Producer...")
    
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8') if k else None
    )
    
    # Test price message
    price_message = {
        "symbol": "VCB",
        "time": "2024-12-04T09:15:00+07:00",
        "open": 85.5,
        "high": 86.2,
        "low": 85.0,
        "close": 86.0,
        "volume": 1250000,
        "collected_at": "2024-12-04T09:15:30.123456"
    }
    
    # Test news message
    news_message = {
        "news_id": "test_news_123",
        "symbol": "VCB",
        "title": "VCB công bố kế hoạch tăng vốn điều lệ",
        "content": "Nội dung tin tức test...",
        "source": "Test Source",
        "source_url": "https://test.com/news",
        "published_at": "2024-12-04T08:30:00+07:00",
        "collected_at": "2024-12-04T09:00:00+07:00",
        "category": "corporate_action",
        "tags": ["test", "news"]
    }
    
    try:
        # Send price message
        future = producer.send('stock_prices_raw', key='VCB', value=price_message)
        result = future.get(timeout=10)
        print(f"Price message sent: {result}")
        
        # Send news message
        future = producer.send('stock_news_raw', key='VCB', value=news_message)
        result = future.get(timeout=10)
        print(f"News message sent: {result}")
        
        producer.flush()
        print("Messages sent successfully!")
        
    except Exception as e:
        print(f"Error sending messages: {e}")
    finally:
        producer.close()

def test_health_endpoint():
    """Test health check endpoint"""
    print("Testing Health Endpoint...")
    
    try:
        response = requests.get('http://localhost:8080/health', timeout=5)
        print(f"Health Status: {response.status_code}")
        print(f"Health Response: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")

def test_metrics_endpoint():
    """Test metrics endpoint"""
    print("Testing Metrics Endpoint...")
    
    try:
        response = requests.get('http://localhost:8080/metrics', timeout=5)
        print(f"Metrics Status: {response.status_code}")
        metrics_data = response.json()
        
        # Print key metrics
        print(f"Uptime: {metrics_data.get('uptime_seconds', 0):.2f} seconds")
        print(f"Counters: {metrics_data.get('counters', {})}")
        print(f"Gauges: {metrics_data.get('gauges', {})}")
        
    except Exception as e:
        print(f"Metrics check failed: {e}")

def main():
    """Main test function"""
    print("=== Kafka Consumer Service Test ===")
    
    # Test health endpoint first
    test_health_endpoint()
    print()
    
    # Test metrics endpoint
    test_metrics_endpoint()
    print()
    
    # Send test messages
    test_kafka_producer()
    print()
    
    # Wait a bit for processing
    print("Waiting 5 seconds for message processing...")
    time.sleep(5)
    
    # Check metrics again
    test_metrics_endpoint()
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    main()