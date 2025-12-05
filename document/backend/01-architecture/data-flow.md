# Data Flow Architecture

## Overview

Data flows through the system in a pipeline architecture from vnstock API to final analysis results.

## Current Data Flow ✅

```
vnstock API → PriceCollector → DataValidator → DataNormalizer → KafkaProducer
     ↓              ↓              ↓              ↓              ↓
Stock Data → Collection → Validation → Normalization → stock_prices_raw
```

## Planned Complete Flow 📋

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│ vnstock API │───►│ Data Collector│───►│ Kafka Topics│───►│ Kafka Consumer│
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
                                                                   │
                                                                   ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│    API      │◄───│ Aggregation  │◄───│ AI Analysis │◄───│   MongoDB    │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
                           ▲                   ▲
                           │                   │
                   ┌──────────────┐    ┌─────────────┐
                   │ LLM Analysis │    │ News Data   │
                   └──────────────┘    └─────────────┘
```

## Data Transformations

### 1. Raw Data Collection ✅
**Input**: vnstock API responses
**Output**: Normalized JSON messages
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

### 2. Storage Layer 📋
**Input**: Kafka messages
**Output**: MongoDB documents
```javascript
{
  "_id": ObjectId("..."),
  "symbol": "VCB",
  "timestamp": ISODate("2024-12-04T09:15:00Z"),
  "open": 85.5,
  "high": 86.2,
  "low": 85.0,
  "close": 86.0,
  "volume": 1250000
}
```

### 3. Analysis Layer 📋
**Input**: Historical price data
**Output**: Technical indicators and predictions
```javascript
{
  "symbol": "VCB",
  "technical_indicators": {
    "rsi_14": 65.5,
    "macd": 0.8,
    "bollinger_position": 0.7
  },
  "predictions": {
    "trend_direction": "bullish",
    "confidence": 0.75
  }
}
```

## Message Flow Patterns

### Producer Pattern ✅
```python
# From actual implementation
class StockKafkaProducer:
    def send_price_data(self, topic: str, symbol: str, data: Dict[str, Any]):
        future = self.producer.send(topic, key=symbol, value=data)
        future.get(timeout=10)
```

### Consumer Pattern 📋
```python
# Planned implementation
class PriceConsumer:
    def consume_messages(self, topics: List[str]):
        for message in self.consumer:
            self.process_message(message.value)
```

## Error Handling Flow

### Current Implementation ✅
```python
# From libs/vnstock/exceptions.py
try:
    prices = client.get_price_history(symbol, start, end)
except DataNotFoundError:
    logger.warning(f"No data found for {symbol}")
except RateLimitError:
    logger.error("Rate limit exceeded")
```

### Planned Error Flow 📋
```
Error → Log → Dead Letter Queue → Manual Review → Retry/Discard
```

## Data Quality Pipeline

### Validation Rules ✅
```python
# From actual implementation
def validate_price_data(data: Dict[str, Any]) -> bool:
    required_fields = ['symbol', 'time', 'open', 'high', 'low', 'close', 'volume']
    if not all(field in data for field in required_fields):
        return False
    
    if data['high'] < data['low']:
        return False
    
    if data['volume'] < 0:
        return False
    
    return True
```

### Quality Metrics 📋
- Data completeness: 95%+ required fields present
- Business logic: High >= Low, Volume >= 0
- Timeliness: Data processed within 10 seconds
- Accuracy: Cross-validation with multiple sources

## Scalability Considerations

### Horizontal Scaling 📋
- Kafka partitioning by symbol hash
- Multiple consumer instances
- Database sharding by date ranges
- Load balancing across analysis services

### Performance Targets 📋
- **Throughput**: 1000+ stocks processed per minute
- **Latency**: < 10 seconds end-to-end
- **Availability**: 99.9% uptime
- **Data Quality**: > 95% accuracy