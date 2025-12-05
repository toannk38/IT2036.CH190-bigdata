import logging
from datetime import datetime, timedelta

from libs.vnstock import VnstockClient
from libs.vnstock.exceptions import VnstockError, DataNotFoundError

from ..processors.data_validator import DataValidator
from ..processors.data_normalizer import DataNormalizer
from ..producers.kafka_producer import StockKafkaProducer

logger = logging.getLogger(__name__)

class PriceCollector:
    def __init__(self, vnstock_client: VnstockClient, kafka_producer: StockKafkaProducer, 
                 kafka_topic: str):
        self.vnstock_client = vnstock_client
        self.kafka_producer = kafka_producer
        self.kafka_topic = kafka_topic
        self.validator = DataValidator()
        self.normalizer = DataNormalizer()
    
    def collect_symbol_prices(self, symbol: str, start_date: str, end_date: str, 
                             interval: str = '1D') -> int:
        try:
            prices = self.vnstock_client.get_price_history(symbol, start_date, end_date, interval)
            sent_count = 0
            
            for price in prices:
                normalized = self.normalizer.normalize_price_data(price)
                
                if self.validator.validate_price_data(normalized):
                    self.kafka_producer.send_price_data(self.kafka_topic, symbol, normalized)
                    sent_count += 1
                else:
                    logger.warning(f"Invalid price data for {symbol}: {normalized}")
            
            logger.info(f"Collected {sent_count} price records for {symbol}")
            return sent_count
            
        except DataNotFoundError:
            logger.warning(f"No price data found for {symbol}")
            return 0
        except VnstockError as e:
            logger.error(f"Error collecting prices for {symbol}: {e}")
            return 0
    
    def collect_all_symbols(self, days: int = 1, interval: str = '1D') -> dict:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        symbols = self.vnstock_client.get_all_symbols()
        results = {'success': 0, 'failed': 0, 'total_records': 0}
        
        for stock in symbols:
            count = self.collect_symbol_prices(stock.symbol, start_date, end_date, interval)
            if count > 0:
                results['success'] += 1
                results['total_records'] += count
            else:
                results['failed'] += 1
        
        logger.info(f"Collection complete: {results}")
        return results
