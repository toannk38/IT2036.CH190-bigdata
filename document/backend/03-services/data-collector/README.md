# Data Collector Service Documentation

## Overview

The Data Collector Service is responsible for collecting stock price and news data from the vnstock API and publishing it to Kafka topics for downstream processing.

**Status**: ✅ **IMPLEMENTED** (Price Collection Complete)

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   vnstock API   │───►│  Data Collector  │───►│  Kafka Topics   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Validation &   │
                       │  Normalization   │
                       └──────────────────┘
```

## Implementation Details

### Core Components

#### 1. PriceCollector ✅
**Location**: `services/data_collector/src/collectors/price_collector.py`

```python
class PriceCollector:
    def __init__(self, vnstock_client: VnstockClient, 
                 kafka_producer: StockKafkaProducer, kafka_topic: str):
        self.vnstock_client = vnstock_client
        self.kafka_producer = kafka_producer
        self.kafka_topic = kafka_topic
        self.validator = DataValidator()
        self.normalizer = DataNormalizer()
```

**Key Methods**:
- `collect_symbol_prices()`: Collects price data for a single symbol
- `collect_all_symbols()`: Collects data for all available symbols

#### 2. DataValidator ✅
**Location**: `services/data_collector/src/processors/data_validator.py`

**Validation Rules**:
```python
@staticmethod
def validate_price_data(data: Dict[str, Any]) -> bool:
    # Required fields validation
    required_fields = ['symbol', 'time', 'open', 'high', 'low', 'close', 'volume']
    if not all(field in data for field in required_fields):
        return False
    
    # Business logic validation
    if data['high'] < data['low']:  # High must be >= Low
        return False
    
    if data['volume'] < 0:  # Volume must be non-negative
        return False
    
    return True
```

#### 3. DataNormalizer ✅
**Location**: `services/data_collector/src/processors/data_normalizer.py`

**Normalization Process**:
```python
@staticmethod
def normalize_price_data(price_data) -> Dict[str, Any]:
    return {
        'symbol': price_data.symbol,
        'time': price_data.time.isoformat() if isinstance(price_data.time, datetime) else price_data.time,
        'open': float(price_data.open),
        'high': float(price_data.high),
        'low': float(price_data.low),
        'close': float(price_data.close),
        'volume': int(price_data.volume),
        'collected_at': datetime.utcnow().isoformat()
    }
```

#### 4. StockKafkaProducer ✅
**Location**: `services/data_collector/src/producers/kafka_producer.py`

```python
class StockKafkaProducer:
    def __init__(self, bootstrap_servers: str):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
    
    def send_price_data(self, topic: str, symbol: str, data: Dict[str, Any]):
        future = self.producer.send(topic, key=symbol, value=data)
        future.get(timeout=10)  # Synchronous send with timeout
```

## Configuration

### Environment Variables
**Location**: `services/data_collector/src/config/settings.py`

```python
# vnstock Configuration
VNSTOCK_SOURCE = os.getenv('VNSTOCK_SOURCE', 'VCI')
VNSTOCK_RATE_LIMIT = float(os.getenv('VNSTOCK_RATE_LIMIT', '0.5'))

# Kafka Configuration  
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_PRICE_TOPIC = os.getenv('KAFKA_PRICE_TOPIC', 'stock_prices_raw')

# Collection Configuration
COLLECTION_INTERVAL = int(os.getenv('COLLECTION_INTERVAL', '300'))  # 5 minutes
PRICE_HISTORY_DAYS = int(os.getenv('PRICE_HISTORY_DAYS', '1'))
PRICE_INTERVAL = os.getenv('PRICE_INTERVAL', '1D')
```

## Data Flow

### Price Collection Workflow

1. **Initialization**
   ```python
   vnstock_client = VnstockClient(source=VNSTOCK_SOURCE, rate_limit=VNSTOCK_RATE_LIMIT)
   kafka_producer = StockKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
   price_collector = PriceCollector(vnstock_client, kafka_producer, KAFKA_PRICE_TOPIC)
   ```

2. **Collection Process**
   ```python
   # Get all available symbols
   symbols = vnstock_client.get_all_symbols()
   
   # For each symbol:
   for stock in symbols:
       # Fetch price history
       prices = vnstock_client.get_price_history(stock.symbol, start_date, end_date)
       
       # Process each price record
       for price in prices:
           normalized = normalizer.normalize_price_data(price)
           if validator.validate_price_data(normalized):
               kafka_producer.send_price_data(topic, symbol, normalized)
   ```

3. **Output Format**
   ```json
   {
     "symbol": "VCB",
     "time": "2024-12-04T09:15:00+07:00",
     "open": 85.5,
     "high": 86.2,
     "low": 85.0,
     "close": 86.0,
     "volume": 1250000,
     "collected_at": "2024-12-04T09:15:30.123456"
   }
   ```

## Error Handling

### Exception Hierarchy
```python
VnstockError (Base)
├── RateLimitError (Rate limit exceeded)
└── DataNotFoundError (No data available)
```

### Error Handling Strategy
1. **Data Not Found**: Log warning, continue with next symbol
2. **Rate Limit**: Handled by vnstock client with automatic retry
3. **Kafka Errors**: Log error and raise exception
4. **Validation Errors**: Log warning, skip invalid records

### Logging
```python
# From actual implementation
logger = logging.getLogger(__name__)

# Success logging
logger.info(f"Collected {sent_count} price records for {symbol}")

# Warning logging  
logger.warning(f"No price data found for {symbol}")
logger.warning(f"Invalid price data for {symbol}: {normalized}")

# Error logging
logger.error(f"Error collecting prices for {symbol}: {e}")
```

## Performance Characteristics

### Collection Metrics (From Implementation)
```python
# Return format from collect_all_symbols()
results = {
    'success': 150,      # Successfully processed symbols
    'failed': 5,         # Failed symbols
    'total_records': 3000 # Total price records collected
}
```

### Rate Limiting
- **Default Rate**: 0.5 seconds between API calls
- **Configurable**: Via VNSTOCK_RATE_LIMIT environment variable
- **Implementation**: Built into VnstockClient

## Testing

### Test Coverage ✅
**Location**: `tests/test_services/data_collector/`

#### Unit Tests
```python
class TestDataValidator:
    def test_validate_valid_data(self)
    def test_validate_missing_field(self)
    def test_validate_invalid_high_low(self)

class TestDataNormalizer:
    def test_normalize_price_data(self, sample_price)

class TestPriceCollector:
    def test_collect_symbol_prices_success(self)
    def test_collect_symbol_prices_not_found(self)
    def test_collect_all_symbols(self)
```

#### Test Fixtures
```python
@pytest.fixture
def sample_price():
    return StockPrice(
        symbol='VCB',
        time=datetime(2024, 1, 1),
        open=100.0,
        high=105.0,
        low=99.0,
        close=103.0,
        volume=1000000
    )
```

## Deployment

### Docker Configuration ✅
**Location**: `services/data_collector/Dockerfile`

### Environment File ✅
**Location**: `services/data_collector/.env.example`

### Requirements ✅
**Location**: `services/data_collector/requirements.txt`

## Usage

### Development Mode
```bash
cd services/data_collector
python -m src.main
```

### Production Mode (Planned)
```bash
docker run -d --name data-collector \
  --env-file .env \
  stock-ai/data-collector:latest
```

## Monitoring

### Health Checks (Planned)
- Collection success rate
- Processing latency
- Kafka connectivity
- vnstock API availability

### Metrics (Planned)
- Records processed per minute
- Error rates by type
- API response times
- Memory and CPU usage

## Future Enhancements

### News Collection (Phase 2.3)
- Similar architecture to price collection
- Additional text processing and deduplication
- Separate Kafka topic: `stock_news_raw`

### Batch Processing
- Historical data backfill
- Scheduled collection jobs
- Data quality monitoring

## Troubleshooting

### Common Issues

1. **Rate Limit Errors**
   - Increase VNSTOCK_RATE_LIMIT value
   - Check vnstock API status

2. **Kafka Connection Errors**
   - Verify KAFKA_BOOTSTRAP_SERVERS configuration
   - Check Kafka cluster health

3. **Data Validation Failures**
   - Review validation logs
   - Check vnstock data quality

4. **Memory Issues**
   - Reduce PRICE_HISTORY_DAYS
   - Implement batch processing