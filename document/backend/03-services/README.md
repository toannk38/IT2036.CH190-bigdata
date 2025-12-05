# Services Documentation

## Overview

The Stock AI Backend System consists of 5 microservices that work together to collect, process, analyze, and serve stock market data with AI-powered insights.

## Service Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data          │───►│   Kafka          │───►│   AI Analysis   │
│   Collector     │    │   Consumer       │    │   Service       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Kafka Topics   │    │    MongoDB       │    │  Kafka Topics   │
│ (Raw Prices)    │    │  (Price Data)    │    │ (AI Results)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  LLM Analysis   │◄───│   Aggregation    │◄───│   API Service   │
│   Service       │    │    Service       │    │  (REST API)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   On-Demand     │    │     Redis        │    │   Frontend      │
│   Analysis      │    │   (Insights)     │    │ Applications    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Services Overview

### 1. Data Collector Service ✅
**Status**: IMPLEMENTED  
**Port**: N/A (Background Service)  
**Purpose**: Collects stock price data from vnstock API and publishes to Kafka

**Key Features**:
- Real-time price data collection
- Data validation and normalization
- Kafka message publishing
- Rate limiting and error handling

**Technologies**: Python, vnstock, Kafka, Docker

---

### 2. Kafka Consumer Service 🔄
**Status**: PLANNED  
**Port**: N/A (Background Service)  
**Purpose**: Consumes price data from Kafka and stores in MongoDB with batch processing

**Key Features**:
- MongoDB adapter with upsert operations
- Batch processing with configurable size
- Rate limiting and validation
- Consumer-specific exception handling

**Technologies**: Python, Kafka, MongoDB, Docker

---

### 3. AI Analysis Service 🔄
**Status**: PLANNED  
**Port**: N/A (Background Service)  
**Purpose**: Performs technical analysis using ML models with internal scheduling

**Key Features**:
- ModelManager for ML model management
- Technical indicator calculation
- Internal batch scheduling
- Signal generation with confidence scores

**Technologies**: Python, scikit-learn, TensorFlow, Kafka, MongoDB

---

### 4. LLM Analysis Service 🔄
**Status**: PLANNED  
**Port**: 8002  
**Purpose**: Provides on-demand natural language analysis via API calls

**Key Features**:
- LLM integration (OpenAI, Anthropic)
- On-demand analysis via API requests
- Context-aware prompt generation
- Response caching and rate limiting

**Technologies**: Python, FastAPI, OpenAI/Anthropic APIs, Redis

---

### 5. Aggregation Service 🔄
**Status**: PLANNED  
**Port**: 8003  
**Purpose**: Combines AI and LLM results following Redis patterns

**Key Features**:
- Multi-source data aggregation
- Redis-based storage patterns
- Signal combination logic
- Confidence score calculation

**Technologies**: Python, FastAPI, Redis, Kafka, MongoDB

---

### 6. API Service 🔄
**Status**: PLANNED  
**Port**: 8000  
**Purpose**: REST API for frontend applications (no authentication required)

**Key Features**:
- Stock data and analysis endpoints
- LLM analysis integration
- Rate limiting and caching
- Market overview and insights

**Technologies**: Python, FastAPI, Redis, MongoDB, Docker

## Shared Configuration

All services use a common configuration pattern based on `src/config/settings.py`:

```python
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=stock_ai

# Kafka Configuration  
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Rate Limiting
RATE_LIMIT_PER_SECOND=10.0

# Batch Processing
BATCH_SIZE=100
BATCH_TIMEOUT=30
```

## Data Models

All services use shared data models from `libs/vnstock/models.py`:

```python
@dataclass
class StockPrice:
    symbol: str
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
```

## Docker Deployment

### Unified Docker Setup

All services share a common Docker configuration pattern:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
CMD ["python", "-m", "src.main"]
```

### Docker Compose

Single `docker-compose.yml` runs all services:

```yaml
version: '3.8'
services:
  # Infrastructure
  mongodb:
    image: mongo:7
    ports: ["27017:27017"]
  
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
  
  kafka:
    image: confluentinc/cp-kafka:latest
    ports: ["9092:9092"]
  
  # Application Services
  data-collector:
    build: ./services/data_collector
    depends_on: [kafka]
  
  kafka-consumer:
    build: ./services/kafka_consumer
    depends_on: [kafka, mongodb]
  
  ai-analysis:
    build: ./services/ai_analysis
    depends_on: [mongodb, kafka]
  
  llm-analysis:
    build: ./services/llm_analysis
    ports: ["8002:8002"]
    depends_on: [mongodb, redis]
  
  aggregation:
    build: ./services/aggregation
    ports: ["8003:8003"]
    depends_on: [redis, kafka]
  
  api:
    build: ./services/api
    ports: ["8000:8000"]
    depends_on: [redis, mongodb]
```

## Service Communication

### Data Flow Patterns

1. **Data Collection**: Data Collector → Kafka → Kafka Consumer → MongoDB
2. **AI Analysis**: AI Service → MongoDB (read) → Kafka (results)
3. **LLM Analysis**: API calls → LLM Service → Response
4. **Aggregation**: Kafka Consumer → Redis storage
5. **API Access**: Frontend → API Service → Redis/MongoDB

### Message Formats

**Kafka Topics**:
- `stock_prices_raw`: Raw price data from collector
- `ai_analysis_results`: AI analysis results

**Redis Keys**:
- `insight:{symbol}`: Current aggregated insights
- `analysis:history:{symbol}`: Historical analysis data

## Development Workflow

### Local Development

1. **Start Infrastructure**:
   ```bash
   docker-compose up mongodb redis kafka -d
   ```

2. **Run Individual Services**:
   ```bash
   cd services/data_collector && python -m src.main
   cd services/kafka_consumer && python -m src.main
   # ... etc
   ```

3. **Full System**:
   ```bash
   docker-compose up
   ```

### Testing Strategy

Each service includes:
- Unit tests for core components
- Integration tests with dependencies
- End-to-end workflow tests
- Performance and load tests

### Monitoring

Shared monitoring approach:
- **Logging**: Structured JSON logging
- **Metrics**: Prometheus metrics collection
- **Health Checks**: HTTP health endpoints
- **Tracing**: Distributed tracing support

## Deployment Considerations

### Scalability
- **Horizontal Scaling**: Multiple instances per service
- **Load Balancing**: Nginx or cloud load balancers
- **Auto Scaling**: Based on CPU/memory/queue metrics

### Reliability
- **Circuit Breakers**: Prevent cascade failures
- **Retry Logic**: Exponential backoff strategies
- **Graceful Degradation**: Fallback to cached data
- **Health Monitoring**: Automated health checks

### Security
- **Network Isolation**: Service-to-service communication
- **Secrets Management**: Environment-based configuration
- **Rate Limiting**: Prevent abuse and DoS
- **Input Validation**: Comprehensive parameter validation

## Next Steps

1. **Phase 1**: Implement Kafka Consumer Service
2. **Phase 2**: Implement AI Analysis Service with ModelManager
3. **Phase 3**: Implement LLM Analysis Service
4. **Phase 4**: Implement Aggregation Service with Redis patterns
5. **Phase 5**: Implement API Service with comprehensive endpoints
6. **Phase 6**: Integration testing and deployment optimization