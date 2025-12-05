# Aggregation Service Documentation

## Overview

The Aggregation Service combines AI analysis results, LLM insights, and price data to create comprehensive stock insights. It follows Redis patterns for data storage and provides unified data access.

**Status**: 🔄 **PLANNED**

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  AI Analysis    │───►│   Aggregation    │───►│     Redis       │
│   Results       │    │    Service       │    │   (Insights)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ LLM Analysis    │    │    MongoDB       │    │   API Access    │
│   Results       │    │  (Price Data)    │    │   (Queries)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Core Components

### 1. Data Aggregator
**Location**: `services/aggregation/src/aggregators/data_aggregator.py`

- **Multi-source Integration**: Combines AI, LLM, and price data
- **Data Normalization**: Standardizes data from different sources
- **Conflict Resolution**: Handles conflicting signals from different sources
- **Completeness Check**: Ensures data completeness before aggregation

### 2. Redis Manager
**Location**: `services/aggregation/src/storage/redis_manager.py`

- **Connection Management**: Manages Redis connections and pools
- **Data Serialization**: Handles JSON serialization/deserialization
- **Key Management**: Implements consistent key naming patterns
- **TTL Management**: Manages data expiration and cleanup

### 3. Insight Generator
**Location**: `services/aggregation/src/generators/insight_generator.py`

- **Signal Combination**: Combines multiple analysis signals
- **Confidence Calculation**: Calculates overall confidence scores
- **Recommendation Logic**: Generates final recommendations
- **Risk Assessment**: Evaluates overall risk levels

### 4. Kafka Consumer
**Location**: `services/aggregation/src/consumers/analysis_consumer.py`

- **AI Results**: Consumes AI analysis results from Kafka
- **Real-time Processing**: Processes results as they arrive
- **Batch Aggregation**: Groups related analyses for processing
- **Error Recovery**: Handles processing failures gracefully

## Configuration

### Environment Variables
```python
# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_DB=0
REDIS_PASSWORD=your_redis_password
REDIS_MAX_CONNECTIONS=20

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=stock_ai
MONGODB_COLLECTION_PRICES=stock_prices

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_AI_RESULTS_TOPIC=ai_analysis_results
KAFKA_GROUP_ID=aggregation_consumer_group

# Aggregation Configuration
AGGREGATION_INTERVAL=60  # seconds
INSIGHT_TTL=3600  # 1 hour
BATCH_SIZE=50
CONFIDENCE_WEIGHTS_AI=0.4
CONFIDENCE_WEIGHTS_LLM=0.6

# API Configuration
API_HOST=0.0.0.0
API_PORT=8003
```

## Data Models

### Aggregated Insight
```python
@dataclass
class AggregatedInsight:
    symbol: str
    timestamp: datetime
    overall_signal: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float
    ai_signal: Optional[str]
    ai_confidence: Optional[float]
    llm_signal: Optional[str]
    llm_confidence: Optional[float]
    price_trend: str
    risk_level: str
    key_factors: List[str]
    price_target: Optional[float]
    data_completeness: float
```

### Source Data
```python
@dataclass
class SourceAnalysis:
    source: str  # 'AI', 'LLM'
    signal: str
    confidence: float
    timestamp: datetime
    metadata: Dict[str, Any]
```

## Redis Data Patterns

### Key Patterns
```python
# Aggregated insights
insight_key = f"insight:{symbol}"
insight_history_key = f"insight:history:{symbol}"

# Source data cache
ai_result_key = f"ai:{symbol}:{timestamp}"
llm_result_key = f"llm:{symbol}:{timestamp}"

# Market overview
market_overview_key = "market:overview"
sector_insights_key = f"sector:{sector_name}"
```

### Data Structures
```python
# Hash for current insight
HSET insight:VCB signal BUY
HSET insight:VCB confidence 0.85
HSET insight:VCB timestamp 2024-12-04T10:30:00Z
HSET insight:VCB ai_signal BUY
HSET insight:VCB llm_signal HOLD

# Sorted set for historical insights
ZADD insight:history:VCB 1701684600 "BUY:0.85"
ZADD insight:history:VCB 1701688200 "HOLD:0.72"

# List for key factors
LPUSH insight:VCB:factors "Strong technical momentum"
LPUSH insight:VCB:factors "Positive earnings outlook"
```

## Processing Flow

### Real-time Aggregation
1. **Consume Results**: Receive AI/LLM analysis from Kafka/API
2. **Data Validation**: Validate incoming analysis data
3. **Fetch Context**: Get existing insights and price data
4. **Signal Combination**: Combine multiple signals using weights
5. **Confidence Calculation**: Calculate overall confidence score
6. **Redis Storage**: Store aggregated insight in Redis
7. **Notification**: Notify subscribers of updates

### Batch Processing
1. **Scheduled Trigger**: Run aggregation at regular intervals
2. **Symbol Selection**: Select symbols needing aggregation
3. **Data Collection**: Collect all available analysis data
4. **Bulk Aggregation**: Process multiple symbols in batch
5. **Redis Update**: Update Redis with batch results

## API Endpoints

### Get Insight
```
GET /api/v1/insights/{symbol}
```

**Response:**
```json
{
  "symbol": "VCB",
  "overall_signal": "BUY",
  "confidence": 0.85,
  "ai_signal": "BUY",
  "llm_signal": "HOLD",
  "price_trend": "UPWARD",
  "risk_level": "MEDIUM",
  "key_factors": ["Strong momentum", "Positive earnings"],
  "data_completeness": 0.9
}
```

### Get Market Overview
```
GET /api/v1/market/overview
```

### Get Historical Insights
```
GET /api/v1/insights/{symbol}/history?days=7
```

## Signal Combination Logic

### Weighted Average
```python
def combine_signals(ai_result, llm_result):
    ai_weight = CONFIDENCE_WEIGHTS_AI
    llm_weight = CONFIDENCE_WEIGHTS_LLM
    
    # Convert signals to numeric scores
    ai_score = signal_to_score(ai_result.signal) * ai_result.confidence
    llm_score = signal_to_score(llm_result.signal) * llm_result.confidence
    
    # Calculate weighted average
    combined_score = (ai_score * ai_weight + llm_score * llm_weight)
    overall_confidence = (ai_result.confidence * ai_weight + 
                         llm_result.confidence * llm_weight)
    
    return score_to_signal(combined_score), overall_confidence
```

### Fallback Strategy
- **No LLM Analysis**: Use AI analysis only with adjusted confidence
- **No AI Analysis**: Use price trend analysis with low confidence
- **Conflicting Signals**: Use HOLD with medium confidence

## Caching Strategy

### TTL Management
- **Current Insights**: 1 hour TTL
- **Historical Data**: 24 hour TTL
- **Market Overview**: 30 minutes TTL
- **Price Context**: 15 minutes TTL

### Cache Invalidation
- **New Analysis**: Invalidate related insight cache
- **Market Events**: Invalidate market overview cache
- **Data Updates**: Selective cache invalidation

## Monitoring

### Metrics
- **Processing Latency**: Time from analysis to aggregated insight
- **Data Completeness**: Percentage of complete insights
- **Signal Accuracy**: Historical signal performance
- **Cache Hit Rate**: Redis cache effectiveness

### Health Checks
- **Redis Connectivity**: Monitor Redis connection health
- **Kafka Consumption**: Monitor message processing lag
- **Data Freshness**: Monitor data age and staleness

## Deployment

### Docker Configuration
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
EXPOSE 8003
CMD ["python", "-m", "src.main"]
```

### Dependencies
- redis==5.0.1
- fastapi==0.104.1
- kafka-python==2.0.2
- pymongo==4.6.1
- pydantic==2.5.0
- celery==5.3.4