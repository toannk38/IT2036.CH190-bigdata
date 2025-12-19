"""
News Collector for collecting stock news data from vnstock.
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
from src.utils.time_utils import current_epoch, safe_convert_to_epoch

logger = get_logger(__name__)


@dataclass
class NewsData:
    """Data class for stock news information."""
    symbol: str
    title: str
    content: str
    source: str
    published_at: float  # Changed to float for epoch timestamp
    collected_at: float  # Changed to float for epoch timestamp
    
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


class NewsCollector:
    """
    Collects stock news data for active symbols and publishes to Kafka.
    
    Responsibilities:
    - Fetch news data from vnstock for all active symbols
    - Publish data to Kafka topic
    - Handle errors and log failures
    """
    
    def __init__(
        self,
        kafka_producer: KafkaProducer,
        symbol_manager: SymbolManager
    ):
        """
        Initialize NewsCollector.
        
        Args:
            kafka_producer: Kafka producer instance for publishing messages
            symbol_manager: SymbolManager instance for getting active symbols
        """
        self.producer = kafka_producer
        self.symbol_manager = symbol_manager
        
        logger.info("NewsCollector initialized")
    
    def collect(self) -> CollectionResult:
        """
        Collect news data for all active symbols from database.
        
        Returns:
            CollectionResult with success/failure status
        """
        logger.info("Starting news data collection")
        
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
        
        logger.info(f"Collecting news data for {len(symbols)} symbols")
        
        # Collect data for each symbol
        success_count = 0
        failure_count = 0
        failed_symbols = []
        
        for symbol in symbols:
            try:
                # Fetch news data from vnstock
                news_articles = self._fetch_news_data(symbol)
                
                # Check if fetch failed (returns None on error)
                if news_articles is None:
                    failure_count += 1
                    failed_symbols.append(symbol)
                    logger.error(f"Failed to fetch news data for {symbol}")
                elif news_articles:
                    # Publish each article to Kafka
                    published_count = 0
                    for article in news_articles:
                        if self.publish_to_kafka(article):
                            published_count += 1
                    
                    if published_count > 0:
                        success_count += 1
                        logger.debug(f"Successfully collected and published {published_count} articles for {symbol}")
                    else:
                        failure_count += 1
                        failed_symbols.append(symbol)
                        logger.error(f"Failed to publish any articles for {symbol}")
                else:
                    # Empty list means no news articles found (not an error)
                    # Some symbols may not have recent news
                    success_count += 1
                    logger.debug(f"No news articles found for {symbol}")
                    
            except Exception as e:
                failure_count += 1
                failed_symbols.append(symbol)
                logger.error(
                    f"Failed to collect news for symbol",
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
            "News data collection completed",
            context={
                'success': success_count,
                'failed': failure_count,
                'total': len(symbols)
            }
        )
        
        return result
    
    def _fetch_news_data(self, symbol: str) -> Optional[List[NewsData]]:
        """
        Fetch news data for a single symbol from vnstock.
        
        Args:
            symbol: Stock symbol code
            
        Returns:
            List of NewsData objects, empty list if no news, or None if fetch fails
        """
        try:
            from vnstock import Company
            
            # Use vnstock Company class to get news data
            company = Company(symbol=symbol, source='VCI')
            
            # Get news articles
            df = company.news()
            
            if df is None or df.empty:
                logger.debug(f"No news data returned from vnstock for {symbol}")
                return []
            
            # Convert DataFrame rows to NewsData objects
            news_articles = []
            collected_at = current_epoch()
            
            for _, row in df.iterrows():
                try:
                    # Map vnstock news columns to our NewsData structure
                    # vnstock columns: ['id', 'news_title', 'news_sub_title', 'friendly_sub_title',
                    #                   'news_image_url', 'news_source_link', 'created_at', 'public_date',
                    #                   'updated_at', 'lang_code', 'news_id', 'news_short_content',
                    #                   'news_full_content', 'close_price', 'ref_price', 'floor', 'ceiling',
                    #                   'price_change_pct']
                    
                    # Convert published_at to epoch if it's a string
                    published_at_raw = row.get('public_date', row.get('created_at', collected_at))
                    published_at = safe_convert_to_epoch(published_at_raw)
                    if published_at is None:
                        published_at = collected_at
                    
                    news_data = NewsData(
                        symbol=symbol,
                        title=str(row.get('news_title', '')),
                        content=str(row.get('news_full_content', row.get('news_short_content', ''))),
                        source=str(row.get('news_source_link', 'vnstock')),
                        published_at=published_at,
                        collected_at=collected_at
                    )
                    news_articles.append(news_data)
                except Exception as e:
                    logger.warning(
                        f"Failed to parse news article row",
                        context={'symbol': symbol, 'error': str(e)}
                    )
                    continue
            
            return news_articles
            
        except Exception as e:
            logger.error(
                f"Error fetching news data from vnstock",
                context={'symbol': symbol, 'error': str(e)},
                exc_info=True
            )
            return None
    
    def publish_to_kafka(self, data: NewsData, topic: str = 'stock_news_raw') -> bool:
        """
        Publish news data to Kafka topic.
        
        Args:
            data: NewsData object to publish
            topic: Kafka topic name (default: stock_news_raw)
            
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
                f"Published news data to Kafka",
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
                f"Kafka error while publishing news data",
                context={'symbol': data.symbol, 'error': str(e)},
                exc_info=True
            )
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error while publishing news data",
                context={'symbol': data.symbol, 'error': str(e)},
                exc_info=True
            )
            return False
