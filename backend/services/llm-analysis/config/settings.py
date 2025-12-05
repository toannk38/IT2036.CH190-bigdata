import os
from typing import Dict, Any
from pydantic import BaseSettings

class LLMSettings(BaseSettings):
    """LLM Analysis Service Configuration"""
    
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Redis Configuration
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    cache_ttl: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
    
    # MongoDB Configuration
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name: str = os.getenv("DATABASE_NAME", "stock_ai")
    
    # Rate Limiting
    openai_requests_per_minute: int = int(os.getenv("OPENAI_RPM", "3000"))
    openai_tokens_per_minute: int = int(os.getenv("OPENAI_TPM", "250000"))
    anthropic_requests_per_minute: int = int(os.getenv("ANTHROPIC_RPM", "1000"))
    anthropic_tokens_per_minute: int = int(os.getenv("ANTHROPIC_TPM", "100000"))
    
    # Cost Control
    daily_cost_limit: float = float(os.getenv("DAILY_COST_LIMIT", "100.0"))  # USD
    monthly_cost_limit: float = float(os.getenv("MONTHLY_COST_LIMIT", "2000.0"))  # USD
    
    # Processing Configuration
    max_chunk_size: int = int(os.getenv("MAX_CHUNK_SIZE", "2000"))
    min_chunk_size: int = int(os.getenv("MIN_CHUNK_SIZE", "100"))
    overlap_size: int = int(os.getenv("OVERLAP_SIZE", "200"))
    
    # Quality Thresholds
    min_quality_score: float = float(os.getenv("MIN_QUALITY_SCORE", "0.5"))
    min_confidence_score: float = float(os.getenv("MIN_CONFIDENCE_SCORE", "0.6"))
    
    # Service Configuration
    service_name: str = "llm-analysis"
    service_version: str = "1.0.0"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # FastAPI Configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8004"))
    reload: bool = os.getenv("RELOAD", "false").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM client configuration"""
        return {
            'openai_api_key': self.openai_api_key,
            'anthropic_api_key': self.anthropic_api_key,
            'redis_url': self.redis_url,
            'cache_ttl': self.cache_ttl,
            'rate_limits': {
                'openai': {
                    'requests_per_minute': self.openai_requests_per_minute,
                    'tokens_per_minute': self.openai_tokens_per_minute
                },
                'anthropic': {
                    'requests_per_minute': self.anthropic_requests_per_minute,
                    'tokens_per_minute': self.anthropic_tokens_per_minute
                }
            },
            'cost_limits': {
                'daily': self.daily_cost_limit,
                'monthly': self.monthly_cost_limit
            }
        }

settings = LLMSettings()