# System Design - Stock AI Backend

## High-Level Architecture

Based on the implemented code and architecture plans, the system follows a microservices architecture with event-driven data processing.

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA SOURCES LAYER                           │
│                   ┌──────────────────┐                          │
│                   │  vnstock Library │                          │
│                   └────────┬─────────┘                          │
└────────────────────────────┼─────────────────────────────────────┘
                             │
┌────────────────────────────┼─────────────────────────────────────┐
│               DATA PIPELINE LAYER                                │
│  ┌────────────────┐        │        ┌────────────────┐          │
│  │ Price Collector│◄───────┴───────►│ News Collector │          │
│  │   ✅ DONE      │                 │   📋 PLANNED   │          │
│  └───────┬────────┘                 └───────┬────────┘          │
│          │                                  │                   │
│          │         ┌──────────────────┐     │                   │
│          └────────►│   Apache Kafka   │◄────┘                   │
│                    │  📋 PLANNED      │                         │
│                    └────────┬─────────┘                         │
└─────────────────────────────┼─────────────────────────────────────┘
                              │
┌─────────────────────────────┼─────────────────────────────────────┐
│                    STORAGE LAYER                                 │
│                    ┌────────▼─────────┐                          │
│                    │     MongoDB      │                          │
│                    │  📋 PLANNED      │                          │
│                    └──────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Data Sources Layer

#### vnstock Library Integration ✅
**Location**: `libs/vnstock/`

**Implementation Status**: Complete
- **VnstockClient**: Main API wrapper with rate limiting
- **Data Models**: StockPrice, StockNews, StockListing
- **Error Handling**: Custom exceptions for different error types
- **Caching**: Response caching with TTL

**Key Features**:
```python
# From actual implementation
class VnstockClient:
    def __init__(self, source: str = 'VCI', rate_limit: float = 0.5)
    
    @cached(ttl=3600)
    def get_all_symbols(self) -> List[StockListing]
    
    def get_price_history(self, symbol: str, start: str, end: str, 
                         interval: str = '1D') -> List[StockPrice]
    
    def get_news(self, symbol: str) -> List[StockNews]
```

### 2. Data Pipeline Layer

#### Price Data Collector ✅
**Location**: `services/data_collector/`

**Implementation Status**: Complete
- **PriceCollector**: Orchestrates data collection workflow
- **DataValidator**: Validates price data integrity
- **DataNormalizer**: Normalizes data format for consistency
- **KafkaProducer**: Sends data to Kafka topics

**Architecture**:
```python
# From actual implementation
class PriceCollector:
    def __init__(self, vnstock_client: VnstockClient, 
                 kafka_producer: StockKafkaProducer, kafka_topic: str)
    
    def collect_symbol_prices(self, symbol: str, start_date: str, 
                             end_date: str, interval: str = '1D') -> int
    
    def collect_all_symbols(self, days: int = 1, 
                           interval: str = '1D') -> dict
```

**Data Flow**:
1. VnstockClient fetches price data
2. DataValidator validates data integrity
3. DataNormalizer converts to standard format
4. KafkaProducer sends to Kafka topic

#### News Data Collector 📋
**Status**: Planned (Phase 2.3)
**Purpose**: Collect and process news data from vnstock

### 3. Message Queue Layer

#### Apache Kafka 📋
**Status**: Planned (Phase 1.3)
**Topics**:
- `stock_prices_raw`: Price data from collectors
- `stock_news_raw`: News data from collectors

### 4. Storage Layer

#### MongoDB 📋
**Status**: Planned (Phase 1.2)
**Collections**:
- `stocks`: Stock metadata
- `price_history`: Historical price data
- `news`: News articles
- `ai_analysis`: AI/ML analysis results
- `final_scores`: Aggregated scores

## Data Models

### StockPrice ✅
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

### StockNews ✅
```python
@dataclass
class StockNews:
    symbol: str
    title: str
    publish_date: datetime
    source: str
    url: Optional[str] = None
```

### StockListing ✅
```python
@dataclass
class StockListing:
    symbol: str
    organ_name: str
    icb_name3: Optional[str] = None
    icb_name2: Optional[str] = None
    icb_name4: Optional[str] = None
```

## Error Handling Strategy

### Custom Exceptions ✅
```python
class VnstockError(Exception):
    """Base exception for vnstock wrapper"""

class RateLimitError(VnstockError):
    """Raised when rate limit is exceeded"""

class DataNotFoundError(VnstockError):
    """Raised when requested data is not found"""
```

### Error Handling Flow
1. **Rate Limiting**: Automatic retry with exponential backoff
2. **Data Validation**: Invalid data logged and skipped
3. **Network Errors**: Retry mechanism with circuit breaker pattern
4. **Logging**: Structured logging for monitoring and debugging

## Scalability Design

### Horizontal Scaling
- **Microservices**: Independent scaling per service
- **Kafka Partitioning**: Parallel processing of messages
- **Docker Containers**: Easy deployment and scaling

### Performance Optimization
- **Caching**: Response caching in vnstock client
- **Batch Processing**: Efficient data collection and processing
- **Async Processing**: Non-blocking operations where possible

## Security Considerations

### API Security
- **Rate Limiting**: Implemented in vnstock client
- **Error Handling**: No sensitive data in error messages
- **Input Validation**: Comprehensive data validation

### Data Security
- **Data Validation**: Prevents injection attacks
- **Structured Logging**: No sensitive data in logs
- **Environment Variables**: Configuration via environment

## Monitoring & Observability

### Logging ✅
```python
# From actual implementation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Metrics (Planned)
- Collection success/failure rates
- Processing latency
- Data quality metrics
- System resource usage

## Technology Stack

### Implemented ✅
- **Python 3.9+**: Core programming language
- **vnstock**: Vietnamese stock data API
- **Kafka-Python**: Kafka client library
- **pytest**: Testing framework

### Planned 📋
- **MongoDB**: Primary database
- **Redis**: Caching layer
- **Docker**: Containerization
- **FastAPI**: REST API framework
- **TensorFlow/PyTorch**: ML frameworks

## Next Implementation Steps

1. **Infrastructure Setup** (Phase 1)
   - Docker Compose configuration
   - MongoDB and Kafka containers
   - Network configuration

2. **Consumer Services** (Phase 2.4)
   - Kafka consumers for price and news data
   - MongoDB integration

3. **AI/ML Engine** (Phase 3)
   - Feature engineering pipeline
   - Model training and inference

4. **API Layer** (Phase 6)
   - REST API endpoints
   - Authentication and authorization