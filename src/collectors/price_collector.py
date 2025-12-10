"""
Price Collector for collecting stock price data from vnstock.
Publishes collected data to Kafka for downstream processing.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json

from src.logging_config import get_logger
from src.services.symbol_manager import SymbolManager

logger = get_logger(__name__)


@dataclass
class PriceData:
    """Data class for stock price information."""
    symbol: str
    timestamp: str
    open: float
    close: float
    high: float
    low: float
    volume: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class CollectionResult:
    """Result of a data collection operation."""
    success_count: int
    failure_count: int
    total_symbols: int
    failed_symbols: List[str]
    
    @property
    def success(self) -> bool:
        """Check if collection was successful overall."""
        return self.failure_count == 0


class PriceCollector:
    """
    Collects stock price data for active symbols and publishes to Kafka.
    
    Responsibilities:
    - Fetch price data from vnstock for all active symbols
    - Publish data to Kafka topic
    - Handle errors and log failures
    """
    
    def __init__(
        self,
        kafka_producer: KafkaProducer,
        vnstock_client: Any,
        symbol_manager: SymbolManager
    ):
        """
        Initialize PriceCollector.
        
        Args:
            kafka_producer: Kafka producer instance for publishing messages
            vnstock_client: vnstock client for fetching stock data
            symbol_manager: SymbolManager instance for getting active symbols
        """
        self.producer = kafka_producer
        self.client = vnstock_client
        self.symbol_manager = symbol_manager
        
        logger.info("PriceCollector initialized")
    
    def collect(self) -> CollectionResult:
        """
        Collect price data for all active symbols from database.
        
        Returns:
            CollectionResult with success/failure status
        """
        logger.info("Starting price data collection")
        
        # Get active symbols from database
        try:
            symbols = self.symbol_manager.get_active_symbols()
        except Exception as e:
            logger.error(
                "Failed to retrieve active symbols",
                context={'error': str(e)},
                exc_info=True
            )
            return CollectionResult(
                success_count=0,
                failure_count=0,
                total_symbols=0,
                failed_symbols=[]
            )
        
        if not symbols:
            logger.warning("No active symbols found for collection")
            return CollectionResult(
                success_count=0,
                failure_count=0,
                total_symbols=0,
                failed_symbols=[]
            )
        
        logger.info(f"Collecting price data for {len(symbols)} symbols")
        
        # Collect data for each symbol
        success_count = 0
        failure_count = 0
        failed_symbols = []
        
        for symbol in symbols:
            try:
                # Fetch price data from vnstock
                price_data = self._fetch_price_data(symbol)
                
                if price_data:
                    # Publish to Kafka
                    if self.publish_to_kafka(price_data):
                        success_count += 1
                        logger.debug(f"Successfully collected and published data for {symbol}")
                    else:
                        failure_count += 1
                        failed_symbols.append(symbol)
                        logger.error(f"Failed to publish data for {symbol}")
                else:
                    failure_count += 1
                    failed_symbols.append(symbol)
                    logger.error(f"No price data retrieved for {symbol}")
                    
            except Exception as e:
                failure_count += 1
                failed_symbols.append(symbol)
                logger.error(
                    f"Failed to collect data for symbol",
                    context={'symbol': symbol, 'error': str(e)},
                    exc_info=True
                )
        
        result = CollectionResult(
            success_count=success_count,
            failure_count=failure_count,
            total_symbols=len(symbols),
            failed_symbols=failed_symbols
        )
        
        logger.info(
            "Price data collection completed",
            context={
                'success': success_count,
                'failed': failure_count,
                'total': len(symbols)
            }
        )
        
        return result
    
    def _fetch_price_data(self, symbol: str) -> Optional[PriceData]:
        """
        Fetch price data for a single symbol from vnstock.
        
        Args:
            symbol: Stock symbol code
            
        Returns:
            PriceData object or None if fetch fails
        """
        try:
            # Use vnstock to get latest price data
            # vnstock3 API: stock(symbol=symbol, source='VCI').quote.history(...)
            stock = self.client.stock(symbol=symbol, source='VCI')
            
            # Get latest trading data (1 day)
            df = stock.quote.history(start='2024-01-01', end='2024-12-31')
            
            if df is None or df.empty:
                logger.warning(f"No data returned from vnstock for {symbol}")
                return None
            
            # Get the most recent row
            latest = df.iloc[-1]
            
            # Extract price data
            price_data = PriceData(
                symbol=symbol,
                timestamp=datetime.utcnow().isoformat(),
                open=float(latest.get('open', 0)),
                close=float(latest.get('close', 0)),
                high=float(latest.get('high', 0)),
                low=float(latest.get('low', 0)),
                volume=int(latest.get('volume', 0))
            )
            
            return price_data
            
        except Exception as e:
            logger.error(
                f"Error fetching price data from vnstock",
                context={'symbol': symbol, 'error': str(e)},
                exc_info=True
            )
            return None
    
    def publish_to_kafka(self, data: PriceData, topic: str = 'stock_prices_raw') -> bool:
        """
        Publish price data to Kafka topic.
        
        Args:
            data: PriceData object to publish
            topic: Kafka topic name (default: stock_prices_raw)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert data to JSON
            message = json.dumps(data.to_dict()).encode('utf-8')
            
            # Send to Kafka
            future = self.producer.send(topic, value=message)
            
            # Wait for confirmation (with timeout)
            record_metadata = future.get(timeout=10)
            
            logger.debug(
                f"Published price data to Kafka",
                context={
                    'symbol': data.symbol,
                    'topic': topic,
                    'partition': record_metadata.partition,
                    'offset': record_metadata.offset
                }
            )
            
            return True
            
        except KafkaError as e:
            logger.error(
                f"Kafka error while publishing data",
                context={'symbol': data.symbol, 'error': str(e)},
                exc_info=True
            )
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error while publishing data",
                context={'symbol': data.symbol, 'error': str(e)},
                exc_info=True
            )
            return False
