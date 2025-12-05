import logging
import sys
import threading
from consumers.price_consumer import PriceConsumer
from consumers.news_consumer import NewsConsumer
from monitoring.http_server import MonitoringServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('kafka_consumer.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for Kafka Consumer Service"""
    logger.info("Starting Kafka Consumer Service")
    
    # Initialize components
    price_consumer = PriceConsumer()
    news_consumer = NewsConsumer()
    from config.settings import MONITORING_HOST, MONITORING_PORT
    monitoring_server = MonitoringServer(host=MONITORING_HOST, port=MONITORING_PORT)
    
    try:
        # Start monitoring server
        monitoring_server.start()
        
        # Start consumers in separate threads
        price_thread = threading.Thread(target=price_consumer.start, name="PriceConsumer")
        news_thread = threading.Thread(target=news_consumer.start, name="NewsConsumer")
        
        price_thread.start()
        news_thread.start()
        
        # Wait for threads to complete
        price_thread.join()
        news_thread.join()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        price_consumer.stop()
        news_consumer.stop()
    except Exception as e:
        logger.error(f"Consumer failed: {e}")
        sys.exit(1)
    finally:
        monitoring_server.stop()
        logger.info("Kafka Consumer Service stopped")

if __name__ == "__main__":
    main()