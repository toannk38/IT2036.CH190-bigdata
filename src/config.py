"""
Configuration module for Vietnam Stock AI Backend.
Loads settings from environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration."""
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'vietnam_stock_ai')
    
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    KAFKA_PRICE_TOPIC = os.getenv('KAFKA_PRICE_TOPIC', 'stock_prices_raw')
    KAFKA_NEWS_TOPIC = os.getenv('KAFKA_NEWS_TOPIC', 'stock_news_raw')
    
    # Airflow Configuration
    AIRFLOW_HOME = os.getenv('AIRFLOW_HOME', '/opt/airflow')
    
    # LLM Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    
    # Application Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    PRICE_COLLECTION_INTERVAL = int(os.getenv('PRICE_COLLECTION_INTERVAL', '300'))
    NEWS_COLLECTION_INTERVAL = int(os.getenv('NEWS_COLLECTION_INTERVAL', '1800'))
    ANALYSIS_INTERVAL = int(os.getenv('ANALYSIS_INTERVAL', '3600'))
    
    # Aggregation Weights
    WEIGHT_TECHNICAL = float(os.getenv('WEIGHT_TECHNICAL', '0.4'))
    WEIGHT_RISK = float(os.getenv('WEIGHT_RISK', '0.3'))
    WEIGHT_SENTIMENT = float(os.getenv('WEIGHT_SENTIMENT', '0.3'))
    
    # Alert Thresholds
    ALERT_BUY_THRESHOLD = float(os.getenv('ALERT_BUY_THRESHOLD', '70'))
    ALERT_WATCH_THRESHOLD = float(os.getenv('ALERT_WATCH_THRESHOLD', '40'))
    
    # Data Retention
    DATA_RETENTION_DAYS = int(os.getenv('DATA_RETENTION_DAYS', '365'))
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        errors = []
        
        if not cls.MONGODB_URI:
            errors.append("MONGODB_URI is required")
        
        if not cls.KAFKA_BOOTSTRAP_SERVERS:
            errors.append("KAFKA_BOOTSTRAP_SERVERS is required")
        
        # Validate weights sum to 1.0
        total_weight = cls.WEIGHT_TECHNICAL + cls.WEIGHT_RISK + cls.WEIGHT_SENTIMENT
        if abs(total_weight - 1.0) > 0.01:
            errors.append(f"Aggregation weights must sum to 1.0, got {total_weight}")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True


# Create a singleton instance
config = Config()

def get_config():
    """
    Get configuration as a dictionary for the consumer service.
    
    Returns:
        Dictionary containing configuration values
    """
    return {
        'mongo_uri': config.MONGODB_URI,
        'mongo_database': config.MONGODB_DATABASE,
        'kafka_bootstrap_servers': config.KAFKA_BOOTSTRAP_SERVERS,
        'kafka_topics': [config.KAFKA_PRICE_TOPIC, config.KAFKA_NEWS_TOPIC],
        'kafka_consumer_group': 'stock_ai_consumer',
        'kafka_auto_offset_reset': 'earliest',
        'kafka_consumer_timeout_ms': 10000,
        'log_level': config.LOG_LEVEL
    }