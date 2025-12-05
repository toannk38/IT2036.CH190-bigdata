import os
from typing import List
from pydantic import BaseSettings

class APISettings(BaseSettings):
    """API Layer Configuration"""
    
    # Service Configuration
    service_name: str = "api"
    service_version: str = "1.0.0"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    reload: bool = os.getenv("RELOAD", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Security Configuration
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    allowed_origins: List[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # Database Configuration
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name: str = os.getenv("DATABASE_NAME", "stock_ai")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # External Services
    ai_analysis_url: str = os.getenv("AI_ANALYSIS_URL", "http://localhost:8003")
    llm_analysis_url: str = os.getenv("LLM_ANALYSIS_URL", "http://localhost:8004")
    aggregation_url: str = os.getenv("AGGREGATION_URL", "http://localhost:8005")
    
    # Cache Configuration
    cache_ttl_short: int = int(os.getenv("CACHE_TTL_SHORT", "180"))  # 3 minutes
    cache_ttl_medium: int = int(os.getenv("CACHE_TTL_MEDIUM", "300"))  # 5 minutes
    cache_ttl_long: int = int(os.getenv("CACHE_TTL_LONG", "900"))  # 15 minutes
    
    # Rate Limiting
    global_rate_limit: int = int(os.getenv("GLOBAL_RATE_LIMIT", "1000"))  # Per minute per IP
    
    # Performance
    max_connections: int = int(os.getenv("MAX_CONNECTIONS", "1000"))
    connection_timeout: int = int(os.getenv("CONNECTION_TIMEOUT", "30"))
    
    # Pagination
    default_page_size: int = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
    max_page_size: int = int(os.getenv("MAX_PAGE_SIZE", "100"))
    
    # Runtime tracking
    start_time: float = 0.0
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = APISettings()