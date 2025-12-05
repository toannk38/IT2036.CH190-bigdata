import os
from pydantic import BaseSettings

class AggregationSettings(BaseSettings):
    """Aggregation & Scoring Service Configuration"""
    
    # Service Configuration
    service_name: str = "aggregation"
    service_version: str = "1.0.0"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8005"))
    reload: bool = os.getenv("RELOAD", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Database Configuration
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name: str = os.getenv("DATABASE_NAME", "stock_ai")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # External Services
    ai_analysis_url: str = os.getenv("AI_ANALYSIS_URL", "http://localhost:8003")
    llm_analysis_url: str = os.getenv("LLM_ANALYSIS_URL", "http://localhost:8004")
    
    # Scoring Configuration
    technical_weight: float = float(os.getenv("TECHNICAL_WEIGHT", "0.6"))
    sentiment_weight: float = float(os.getenv("SENTIMENT_WEIGHT", "0.25"))
    risk_weight: float = float(os.getenv("RISK_WEIGHT", "0.15"))
    
    # Optimization Configuration
    optimization_frequency_days: int = int(os.getenv("OPTIMIZATION_FREQUENCY", "7"))
    min_optimization_samples: int = int(os.getenv("MIN_OPTIMIZATION_SAMPLES", "50"))
    optimization_lookback_days: int = int(os.getenv("OPTIMIZATION_LOOKBACK", "90"))
    
    # Alert Configuration
    alert_dedup_minutes: int = int(os.getenv("ALERT_DEDUP_MINUTES", "30"))
    max_alerts_per_stock: int = int(os.getenv("MAX_ALERTS_PER_STOCK", "10"))
    alert_cleanup_days: int = int(os.getenv("ALERT_CLEANUP_DAYS", "7"))
    
    # Real-time Configuration
    websocket_max_connections: int = int(os.getenv("WEBSOCKET_MAX_CONNECTIONS", "1000"))
    realtime_update_interval: int = int(os.getenv("REALTIME_UPDATE_INTERVAL", "60"))
    score_cache_ttl: int = int(os.getenv("SCORE_CACHE_TTL", "300"))
    
    # Thresholds
    buy_threshold: float = float(os.getenv("BUY_THRESHOLD", "0.75"))
    hold_threshold: float = float(os.getenv("HOLD_THRESHOLD", "0.50"))
    sell_threshold: float = float(os.getenv("SELL_THRESHOLD", "0.25"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = AggregationSettings()