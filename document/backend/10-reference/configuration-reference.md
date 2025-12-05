# Configuration Reference

## Environment Variables

### vnstock Configuration ✅

#### VNSTOCK_SOURCE
- **Type**: String
- **Default**: `VCI`
- **Options**: `VCI`, `TCBS`, `SSI`
- **Description**: Data source for vnstock API
- **Example**: `VNSTOCK_SOURCE=VCI`

#### VNSTOCK_RATE_LIMIT
- **Type**: Float
- **Default**: `0.5`
- **Unit**: Seconds between API calls
- **Description**: Rate limiting for vnstock API calls
- **Example**: `VNSTOCK_RATE_LIMIT=0.5`

### Kafka Configuration ✅

#### KAFKA_BOOTSTRAP_SERVERS
- **Type**: String
- **Default**: `localhost:9092`
- **Description**: Kafka broker addresses
- **Example**: `KAFKA_BOOTSTRAP_SERVERS=kafka1:9092,kafka2:9092`

#### KAFKA_PRICE_TOPIC
- **Type**: String
- **Default**: `stock_prices_raw`
- **Description**: Kafka topic for price data
- **Example**: `KAFKA_PRICE_TOPIC=stock_prices_raw`

#### KAFKA_NEWS_TOPIC
- **Type**: String
- **Default**: `stock_news_raw`
- **Description**: Kafka topic for news data
- **Example**: `KAFKA_NEWS_TOPIC=stock_news_raw`

### Data Collector Configuration ✅

#### COLLECTION_INTERVAL
- **Type**: Integer
- **Default**: `300`
- **Unit**: Seconds
- **Description**: Interval between collection cycles
- **Example**: `COLLECTION_INTERVAL=300`

#### PRICE_HISTORY_DAYS
- **Type**: Integer
- **Default**: `1`
- **Description**: Number of days of price history to collect
- **Example**: `PRICE_HISTORY_DAYS=7`

#### PRICE_INTERVAL
- **Type**: String
- **Default**: `1D`
- **Options**: `1D`, `1H`, `5m`
- **Description**: Price data interval
- **Example**: `PRICE_INTERVAL=1D`

### MongoDB Configuration 📋

#### MONGODB_URI
- **Type**: String
- **Default**: `mongodb://localhost:27017`
- **Description**: MongoDB connection string
- **Example**: `MONGODB_URI=mongodb://user:pass@mongodb:27017/stock_ai`

#### MONGODB_DATABASE
- **Type**: String
- **Default**: `stock_ai`
- **Description**: Database name
- **Example**: `MONGODB_DATABASE=stock_ai`

#### MONGODB_POOL_SIZE
- **Type**: Integer
- **Default**: `50`
- **Description**: Maximum connection pool size
- **Example**: `MONGODB_POOL_SIZE=100`

### Redis Configuration 📋

#### REDIS_URL
- **Type**: String
- **Default**: `redis://localhost:6379`
- **Description**: Redis connection URL
- **Example**: `REDIS_URL=redis://user:pass@redis:6379/0`

#### REDIS_TTL_DEFAULT
- **Type**: Integer
- **Default**: `300`
- **Unit**: Seconds
- **Description**: Default cache TTL
- **Example**: `REDIS_TTL_DEFAULT=600`

### LLM Configuration 📋

#### OPENAI_API_KEY
- **Type**: String
- **Required**: Yes
- **Description**: OpenAI API key for LLM analysis
- **Example**: `OPENAI_API_KEY=sk-...`

#### OPENAI_MODEL
- **Type**: String
- **Default**: `gpt-4`
- **Options**: `gpt-4`, `gpt-3.5-turbo`
- **Description**: OpenAI model to use
- **Example**: `OPENAI_MODEL=gpt-4`

#### LLM_RATE_LIMIT
- **Type**: Float
- **Default**: `1.0`
- **Unit**: Requests per second
- **Description**: Rate limit for LLM API calls
- **Example**: `LLM_RATE_LIMIT=0.5`

### API Configuration 📋

#### API_HOST
- **Type**: String
- **Default**: `0.0.0.0`
- **Description**: API server host
- **Example**: `API_HOST=localhost`

#### API_PORT
- **Type**: Integer
- **Default**: `8000`
- **Description**: API server port
- **Example**: `API_PORT=8080`

#### API_WORKERS
- **Type**: Integer
- **Default**: `4`
- **Description**: Number of API worker processes
- **Example**: `API_WORKERS=8`

### Logging Configuration ✅

#### LOG_LEVEL
- **Type**: String
- **Default**: `INFO`
- **Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Description**: Logging level
- **Example**: `LOG_LEVEL=DEBUG`

#### LOG_FORMAT
- **Type**: String
- **Default**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Description**: Log message format
- **Example**: Custom format string

### Security Configuration 📋

#### JWT_SECRET_KEY
- **Type**: String
- **Required**: Yes (for API auth)
- **Description**: Secret key for JWT token signing
- **Example**: `JWT_SECRET_KEY=your-secret-key`

#### API_KEY_HEADER
- **Type**: String
- **Default**: `X-API-Key`
- **Description**: Header name for API key authentication
- **Example**: `API_KEY_HEADER=Authorization`

## Service-Specific Configuration

### Data Collector Service ✅

**Location**: `services/data_collector/src/config/settings.py`

```python
# vnstock Configuration
VNSTOCK_SOURCE = os.getenv('VNSTOCK_SOURCE', 'VCI')
VNSTOCK_RATE_LIMIT = float(os.getenv('VNSTOCK_RATE_LIMIT', '0.5'))

# Kafka Configuration  
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_PRICE_TOPIC = os.getenv('KAFKA_PRICE_TOPIC', 'stock_prices_raw')

# Collection Configuration
COLLECTION_INTERVAL = int(os.getenv('COLLECTION_INTERVAL', '300'))
PRICE_HISTORY_DAYS = int(os.getenv('PRICE_HISTORY_DAYS', '1'))
PRICE_INTERVAL = os.getenv('PRICE_INTERVAL', '1D')
```

### Kafka Consumer Service 📋

```python
# services/kafka_consumer/src/config/settings.py
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_CONSUMER_GROUP = os.getenv('KAFKA_CONSUMER_GROUP', 'storage-consumers')
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'stock_ai')
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '100'))
```

### AI Analysis Service 📋

```python
# services/ai_analysis/src/config/settings.py
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MODEL_PATH = os.getenv('MODEL_PATH', '/app/models')
ANALYSIS_BATCH_SIZE = int(os.getenv('ANALYSIS_BATCH_SIZE', '100'))
FEATURE_WINDOW_DAYS = int(os.getenv('FEATURE_WINDOW_DAYS', '60'))
```

### LLM Analysis Service 📋

```python
# services/llm_analysis/src/config/settings.py
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
LLM_RATE_LIMIT = float(os.getenv('LLM_RATE_LIMIT', '1.0'))
BATCH_SIZE = int(os.getenv('LLM_BATCH_SIZE', '10'))
```

### API Service 📋

```python
# services/api/src/config/settings.py
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '8000'))
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
```

## Docker Configuration

### docker-compose.yml 📋

```yaml
version: '3.8'

services:
  data-collector:
    build: ./services/data_collector
    environment:
      - VNSTOCK_SOURCE=${VNSTOCK_SOURCE:-VCI}
      - VNSTOCK_RATE_LIMIT=${VNSTOCK_RATE_LIMIT:-0.5}
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - KAFKA_PRICE_TOPIC=${KAFKA_PRICE_TOPIC:-stock_prices_raw}
      - COLLECTION_INTERVAL=${COLLECTION_INTERVAL:-300}
    depends_on:
      - kafka

  kafka-consumer:
    build: ./services/kafka_consumer
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - MONGODB_URI=mongodb://mongodb:27017
      - MONGODB_DATABASE=${MONGODB_DATABASE:-stock_ai}
    depends_on:
      - kafka
      - mongodb

  api:
    build: ./services/api
    ports:
      - "${API_PORT:-8000}:8000"
    environment:
      - MONGODB_URI=mongodb://mongodb:27017
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - mongodb
      - redis
```

### Environment Files

#### .env.example ✅
```bash
# vnstock Configuration
VNSTOCK_SOURCE=VCI
VNSTOCK_RATE_LIMIT=0.5

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_PRICE_TOPIC=stock_prices_raw
KAFKA_NEWS_TOPIC=stock_news_raw

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=stock_ai

# Redis Configuration
REDIS_URL=redis://localhost:6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
JWT_SECRET_KEY=your-secret-key-here

# LLM Configuration
OPENAI_API_KEY=your-openai-key-here
OPENAI_MODEL=gpt-4

# Logging
LOG_LEVEL=INFO
```

#### .env.development
```bash
# Development-specific overrides
LOG_LEVEL=DEBUG
VNSTOCK_RATE_LIMIT=0.1
COLLECTION_INTERVAL=60
API_PORT=8001
```

#### .env.production
```bash
# Production-specific settings
LOG_LEVEL=WARNING
VNSTOCK_RATE_LIMIT=1.0
COLLECTION_INTERVAL=300
API_WORKERS=8
MONGODB_POOL_SIZE=100
```

## Configuration Validation

### Environment Validation 📋

```python
# libs/common/config_validator.py
import os
from typing import Dict, Any

class ConfigValidator:
    REQUIRED_VARS = [
        'KAFKA_BOOTSTRAP_SERVERS',
        'MONGODB_URI',
        'OPENAI_API_KEY'
    ]
    
    OPTIONAL_VARS = {
        'VNSTOCK_SOURCE': 'VCI',
        'VNSTOCK_RATE_LIMIT': '0.5',
        'LOG_LEVEL': 'INFO'
    }
    
    def validate_config(self) -> Dict[str, Any]:
        config = {}
        errors = []
        
        # Check required variables
        for var in self.REQUIRED_VARS:
            value = os.getenv(var)
            if not value:
                errors.append(f"Missing required environment variable: {var}")
            else:
                config[var] = value
        
        # Set optional variables with defaults
        for var, default in self.OPTIONAL_VARS.items():
            config[var] = os.getenv(var, default)
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return config
```

### Type Conversion 📋

```python
# Configuration type helpers
def get_int_env(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        raise ValueError(f"Invalid integer value for {key}")

def get_float_env(key: str, default: float) -> float:
    try:
        return float(os.getenv(key, str(default)))
    except ValueError:
        raise ValueError(f"Invalid float value for {key}")

def get_bool_env(key: str, default: bool) -> bool:
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')

def get_list_env(key: str, default: list, separator: str = ',') -> list:
    value = os.getenv(key)
    if not value:
        return default
    return [item.strip() for item in value.split(separator)]
```

## Configuration Best Practices

### Security
- Never commit sensitive values to version control
- Use environment variables for all configuration
- Encrypt sensitive configuration in production
- Rotate API keys and secrets regularly

### Organization
- Group related configuration variables
- Use consistent naming conventions
- Provide sensible defaults for optional settings
- Document all configuration options

### Validation
- Validate configuration at startup
- Provide clear error messages for invalid config
- Use type conversion helpers
- Test configuration in different environments