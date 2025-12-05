# Microservices Architecture

## Service Overview

The system is designed as a collection of loosely coupled microservices, each with a specific responsibility.

## Service Catalog

### ✅ Implemented Services

#### 1. Data Collector Service
**Location**: `services/data_collector/`
**Responsibility**: Collect stock data from vnstock API
**Dependencies**: vnstock API, Kafka
**Interfaces**: Kafka Producer
```python
class PriceCollector:
    def collect_all_symbols(self, days: int = 1) -> dict
    def collect_symbol_prices(self, symbol: str, start_date: str, end_date: str) -> int
```

### 📋 Planned Services

#### 2. Kafka Consumer Service
**Location**: `services/kafka_consumer/`
**Responsibility**: Consume Kafka messages and store to MongoDB
**Dependencies**: Kafka, MongoDB
**Interfaces**: Kafka Consumer, MongoDB Client

#### 3. AI Analysis Service
**Location**: `services/ai_analysis/`
**Responsibility**: Technical analysis using ML models
**Dependencies**: MongoDB, ML models
**Interfaces**: Analysis API, Model serving

#### 4. LLM Analysis Service
**Location**: `services/llm_analysis/`
**Responsibility**: News sentiment analysis using LLM
**Dependencies**: MongoDB, OpenAI API
**Interfaces**: LLM API, Batch processing

#### 5. Aggregation Service
**Location**: `services/aggregation/`
**Responsibility**: Combine analysis results and generate scores
**Dependencies**: MongoDB (AI + LLM results)
**Interfaces**: Score calculation, Alert generation

#### 6. API Service
**Location**: `services/api/`
**Responsibility**: REST API endpoints for external access
**Dependencies**: MongoDB, Redis (caching)
**Interfaces**: REST API, WebSocket (real-time)

## Service Communication

### Message-Based Communication ✅
```python
# Current implementation pattern
class StockKafkaProducer:
    def send_price_data(self, topic: str, symbol: str, data: Dict[str, Any]):
        future = self.producer.send(topic, key=symbol, value=data)
```

### Planned Communication Patterns 📋

#### Async Messaging
```
Data Collector → Kafka → Kafka Consumer → MongoDB
News Collector → Kafka → Kafka Consumer → MongoDB
```

#### Synchronous APIs
```
API Service → MongoDB (direct read)
API Service → Redis (caching)
```

#### Event-Driven Processing
```
New Price Data → AI Analysis Trigger
New News Data → LLM Analysis Trigger
Analysis Complete → Aggregation Trigger
```

## Service Dependencies

### Current Dependencies ✅
```
Data Collector Service:
├── libs/vnstock (internal)
├── kafka-python (external)
└── vnstock (external API)
```

### Planned Dependencies 📋
```
Kafka Consumer Service:
├── kafka-python
├── pymongo
└── libs/common

AI Analysis Service:
├── pymongo
├── tensorflow/pytorch
├── pandas
└── libs/ml

LLM Analysis Service:
├── pymongo
├── openai
└── libs/common

Aggregation Service:
├── pymongo
└── libs/common

API Service:
├── fastapi
├── pymongo
├── redis
└── libs/common
```

## Service Configuration

### Environment-Based Configuration ✅
```python
# Pattern from services/data_collector/src/config/settings.py
VNSTOCK_SOURCE = os.getenv('VNSTOCK_SOURCE', 'VCI')
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
COLLECTION_INTERVAL = int(os.getenv('COLLECTION_INTERVAL', '300'))
```

### Planned Configuration 📋
```python
# services/kafka_consumer/src/config/settings.py
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
CONSUMER_GROUP_ID = os.getenv('CONSUMER_GROUP_ID', 'storage-consumers')

# services/api/src/config/settings.py
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '8000'))
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
```

## Service Boundaries

### Data Ownership
- **Data Collector**: Raw data collection and initial validation
- **Kafka Consumer**: Data persistence and storage management
- **AI Analysis**: Technical analysis and predictions
- **LLM Analysis**: News sentiment and insights
- **Aggregation**: Final scoring and recommendations
- **API**: Data access and presentation

### Shared Libraries
```
libs/
├── vnstock/          # ✅ vnstock API wrapper
├── common/           # 📋 Common utilities
├── ml/               # 📋 ML utilities
└── database/         # 📋 Database models
```

## Deployment Strategy

### Container-Based Deployment ✅
```dockerfile
# Pattern from services/data_collector/Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
CMD ["python", "-m", "src.main"]
```

### Service Discovery 📋
```yaml
# docker-compose.yml pattern
services:
  data-collector:
    build: ./services/data_collector
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
    depends_on: [kafka]
  
  kafka-consumer:
    build: ./services/kafka_consumer
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - MONGODB_URI=mongodb://mongodb:27017
    depends_on: [kafka, mongodb]
```

## Health Checks and Monitoring

### Service Health ✅
```python
# Current logging pattern
logger = logging.getLogger(__name__)
logger.info(f"Collected {sent_count} price records for {symbol}")
```

### Planned Health Endpoints 📋
```python
# services/api/src/health.py
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "mongodb": await check_mongodb(),
            "kafka": await check_kafka(),
            "redis": await check_redis()
        }
    }
```

## Error Handling Strategy

### Service-Level Error Handling ✅
```python
# From actual implementation
try:
    count = self.collect_symbol_prices(stock.symbol, start_date, end_date, interval)
    if count > 0:
        results['success'] += 1
    else:
        results['failed'] += 1
except Exception as e:
    logger.error(f"Error collecting prices for {symbol}: {e}")
    results['failed'] += 1
```

### Circuit Breaker Pattern 📋
```python
# Planned implementation
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
```

## Service Scaling

### Horizontal Scaling 📋
- **Data Collector**: Multiple instances with different symbol ranges
- **Kafka Consumer**: Consumer groups with multiple instances
- **AI Analysis**: Parallel processing of different symbols
- **API Service**: Load balancer with multiple instances

### Resource Requirements 📋
```yaml
# Planned resource allocation
services:
  data-collector:
    deploy:
      replicas: 2
      resources:
        limits: { memory: 512M, cpus: 0.5 }
  
  ai-analysis:
    deploy:
      replicas: 3
      resources:
        limits: { memory: 2G, cpus: 1.0 }
```

## Service Testing Strategy

### Unit Testing ✅
```python
# Pattern from tests/test_services/data_collector/
class TestPriceCollector:
    def test_collect_symbol_prices_success(self, mock_vnstock_client, mock_kafka_producer)
    def test_collect_all_symbols(self, mock_vnstock_client)
```

### Integration Testing 📋
```python
# Planned service integration tests
class TestServiceIntegration:
    def test_data_collector_to_kafka_consumer_flow(self)
    def test_ai_analysis_service_integration(self)
    def test_api_service_endpoints(self)
```

## Service Governance

### API Contracts 📋
- OpenAPI specifications for all REST endpoints
- Kafka message schemas with versioning
- Database schema migrations

### Service Versioning 📋
- Semantic versioning for all services
- Backward compatibility requirements
- Deprecation policies