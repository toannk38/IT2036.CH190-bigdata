import os
from datetime import datetime, timedelta

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'stock_ai')
MONGODB_COLLECTION_PRICES = os.getenv('MONGODB_COLLECTION_PRICES', 'stock_prices')
MONGODB_COLLECTION_NEWS = os.getenv('MONGODB_COLLECTION_NEWS', 'news')

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_PRICE_TOPIC = os.getenv('KAFKA_PRICE_TOPIC', 'stock_prices_raw')
KAFKA_NEWS_TOPIC = os.getenv('KAFKA_NEWS_TOPIC', 'stock_news_raw')
KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'consumer_group')

# Batch Processing Configuration
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '100'))
BATCH_TIMEOUT = int(os.getenv('BATCH_TIMEOUT', '30'))  # seconds

# Rate Limiting Configuration
RATE_LIMIT_PER_SECOND = float(os.getenv('RATE_LIMIT_PER_SECOND', '10.0'))

# Processing Configuration
PROCESSING_INTERVAL = int(os.getenv('PROCESSING_INTERVAL', '5'))  # seconds
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))

# Monitoring Configuration
MONITORING_HOST = os.getenv('MONITORING_HOST', '0.0.0.0')
MONITORING_PORT = int(os.getenv('MONITORING_PORT', '8080'))