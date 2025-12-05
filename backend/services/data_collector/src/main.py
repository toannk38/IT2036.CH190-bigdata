import time
import logging
from datetime import datetime

from libs.vnstock import VnstockClient

from services.data_collector.src.config.settings import (
    VNSTOCK_SOURCE, VNSTOCK_RATE_LIMIT,
    KAFKA_BOOTSTRAP_SERVERS, KAFKA_PRICE_TOPIC,
    COLLECTION_INTERVAL, PRICE_HISTORY_DAYS, PRICE_INTERVAL
)
from services.data_collector.src.collectors.price_collector import PriceCollector
from services.data_collector.src.producers.kafka_producer import StockKafkaProducer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Price Data Collector Service")
    
    vnstock_client = VnstockClient(source=VNSTOCK_SOURCE, rate_limit=VNSTOCK_RATE_LIMIT)
    kafka_producer = StockKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    price_collector = PriceCollector(vnstock_client, kafka_producer, KAFKA_PRICE_TOPIC)
    
    try:
        while True:
            logger.info(f"Starting collection cycle at {datetime.now()}")
            results = price_collector.collect_all_symbols(
                days=PRICE_HISTORY_DAYS,
                interval=PRICE_INTERVAL
            )
            logger.info(f"Collection cycle complete: {results}")
            
            logger.info(f"Sleeping for {COLLECTION_INTERVAL} seconds")
            time.sleep(COLLECTION_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully")
    finally:
        kafka_producer.close()

if __name__ == '__main__':
    main()
