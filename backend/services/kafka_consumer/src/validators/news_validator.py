import logging
from typing import Dict, Any
from datetime import datetime
from ..exceptions.consumer_exceptions import DataValidationError

logger = logging.getLogger(__name__)

class NewsValidator:
    @staticmethod
    def validate_news_message(data: Dict[str, Any]) -> bool:
        """Validate incoming news data from Kafka"""
        try:
            # Required fields validation
            required_fields = ['news_id', 'symbol', 'title', 'content', 'source', 'published_at']
            if not all(field in data for field in required_fields):
                missing = [f for f in required_fields if f not in data]
                logger.warning(f"Missing required news fields: {missing}")
                return False
            
            # Type validation
            if not isinstance(data['symbol'], str) or not data['symbol'].strip():
                logger.warning("Invalid symbol format in news")
                return False
            
            if not isinstance(data['title'], str) or not data['title'].strip():
                logger.warning("Invalid title format in news")
                return False
            
            if not isinstance(data['content'], str) or not data['content'].strip():
                logger.warning("Invalid content format in news")
                return False
            
            if not isinstance(data['source'], str) or not data['source'].strip():
                logger.warning("Invalid source format in news")
                return False
            
            # News ID validation
            if not isinstance(data['news_id'], str) or not data['news_id'].strip():
                logger.warning("Invalid news_id format")
                return False
            
            # Time validation
            if isinstance(data['published_at'], str):
                try:
                    datetime.fromisoformat(data['published_at'].replace('Z', '+00:00'))
                except ValueError:
                    logger.warning(f"Invalid published_at format: {data['published_at']}")
                    return False
            
            # Optional fields validation
            if 'collected_at' in data and isinstance(data['collected_at'], str):
                try:
                    datetime.fromisoformat(data['collected_at'].replace('Z', '+00:00'))
                except ValueError:
                    logger.warning(f"Invalid collected_at format: {data['collected_at']}")
                    return False
            
            # Content length validation
            if len(data['content']) > 50000:  # 50KB limit
                logger.warning(f"Content too long: {len(data['content'])} characters")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"News validation error: {e}")
            return False