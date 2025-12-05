import os
from datetime import datetime, timedelta

VNSTOCK_SOURCE = os.getenv('VNSTOCK_SOURCE', 'VCI')
VNSTOCK_RATE_LIMIT = float(os.getenv('VNSTOCK_RATE_LIMIT', '0.5'))

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_PRICE_TOPIC = os.getenv('KAFKA_PRICE_TOPIC', 'stock_prices_raw')

COLLECTION_INTERVAL = int(os.getenv('COLLECTION_INTERVAL', '300'))  # 5 minutes
PRICE_HISTORY_DAYS = int(os.getenv('PRICE_HISTORY_DAYS', '1'))
PRICE_INTERVAL = os.getenv('PRICE_INTERVAL', '1D')  # 1D, 1m, 5m, etc.
