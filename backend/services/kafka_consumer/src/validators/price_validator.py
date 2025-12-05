import logging
from typing import Dict, Any
from datetime import datetime
from ..exceptions.consumer_exceptions import DataValidationError

logger = logging.getLogger(__name__)

class PriceValidator:
    @staticmethod
    def validate_price_message(data: Dict[str, Any]) -> bool:
        """Validate incoming price data from Kafka"""
        try:
            # Required fields validation
            required_fields = ['symbol', 'time', 'open', 'high', 'low', 'close', 'volume']
            if not all(field in data for field in required_fields):
                missing = [f for f in required_fields if f not in data]
                logger.warning(f"Missing required fields: {missing}")
                return False
            
            # Type validation
            if not isinstance(data['symbol'], str) or not data['symbol'].strip():
                logger.warning("Invalid symbol format")
                return False
            
            # Numeric validation
            numeric_fields = ['open', 'high', 'low', 'close']
            for field in numeric_fields:
                try:
                    float(data[field])
                except (ValueError, TypeError):
                    logger.warning(f"Invalid numeric value for {field}: {data[field]}")
                    return False
            
            # Volume validation
            try:
                volume = int(data['volume'])
                if volume < 0:
                    logger.warning(f"Negative volume: {volume}")
                    return False
            except (ValueError, TypeError):
                logger.warning(f"Invalid volume value: {data['volume']}")
                return False
            
            # Business logic validation
            high = float(data['high'])
            low = float(data['low'])
            if high < low:
                logger.warning(f"High ({high}) < Low ({low})")
                return False
            
            # Time validation
            if isinstance(data['time'], str):
                try:
                    datetime.fromisoformat(data['time'].replace('Z', '+00:00'))
                except ValueError:
                    logger.warning(f"Invalid time format: {data['time']}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False