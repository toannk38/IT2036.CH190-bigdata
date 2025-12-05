import json
import logging
from kafka import KafkaProducer
from typing import Dict, Any

logger = logging.getLogger(__name__)

class StockKafkaProducer:
    def __init__(self, bootstrap_servers: str):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
    
    def send_price_data(self, topic: str, symbol: str, data: Dict[str, Any]):
        try:
            future = self.producer.send(topic, key=symbol, value=data)
            future.get(timeout=10)
            logger.debug(f"Sent price data for {symbol} to {topic}")
        except Exception as e:
            logger.error(f"Failed to send price data for {symbol}: {e}")
            raise
    
    def close(self):
        self.producer.flush()
        self.producer.close()
