# Kafka Consumer Service Documentation

## Overview

The Kafka Consumer Service consumes stock price data from Kafka topics and stores it in MongoDB using batch processing with upsert operations to prevent data redundancy.

**Status**: 🔄 **PLANNED**

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Kafka Topics   │───►│ Kafka Consumer   │───►│    MongoDB      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ Batch Processor  │
                       │ (Rate Limited)   │
                       └──────────────────┘
```

## Core Components

### 1. MongoDB Adapter
**Location**: `services/kafka_consumer/src/adapters/mongodb_adapter.py`

- **Connection Management**: Connects to MongoDB using URI from config
- **Batch Upsert**: Uses `UpdateOne` with upsert=True
- **Unique Key**: Combines `symbol` and `time` to prevent duplicates
- **Error Handling**: Handles connection failures and bulk write errors

### 2. Batch Processor
**Location**: `services/kafka_consumer/src/processors/batch_processor.py`

- **Batch Size**: Configurable via `BATCH_SIZE` environment variable
- **Timeout Processing**: Forces batch commit after `BATCH_TIMEOUT` seconds
- **Rate Limiting**: Limits processing to `RATE_LIMIT_PER_SECOND`
- **Thread Safety**: Uses locks for concurrent message handling

### 3. Price Validator
**Location**: `services/kafka_consumer/src/validators/price_validator.py`

- **Field Validation**: Ensures all required fields present
- **Type Validation**: Validates numeric and string types
- **Business Logic**: Validates high >= low, volume >= 0
- **Time Format**: Validates ISO format timestamps

### 4. Price Consumer
**Location**: `services/kafka_consumer/src/consumers/price_consumer.py`

- **Kafka Integration**: Consumes from `stock_prices_raw` topic
- **Message Processing**: Adds messages to batch processor
- **Graceful Shutdown**: Handles SIGINT/SIGTERM signals
- **Auto Commit**: Commits offsets automatically

## Configuration

### Environment Variables
```python
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=stock_ai
MONGODB_COLLECTION_PRICES=stock_prices

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_PRICE_TOPIC=stock_prices_raw
KAFKA_GROUP_ID=price_consumer_group

# Batch Processing Configuration
BATCH_SIZE=100
BATCH_TIMEOUT=30

# Rate Limiting Configuration
RATE_LIMIT_PER_SECOND=10.0
```

## Data Models

Uses same data models from `libs/vnstock/models.py`:
- **StockPrice**: symbol, time, open, high, low, close, volume

## Exception Handling

### Custom Exceptions
- **ConsumerError**: Base exception
- **MongoDBConnectionError**: Database connection issues
- **BatchProcessingError**: Batch operation failures
- **DataValidationError**: Invalid data format
- **RateLimitExceededError**: Rate limit violations

## Processing Flow

1. **Message Consumption**: Consume from Kafka topic
2. **Validation**: Validate message format and business rules
3. **Batch Accumulation**: Add to batch until size/timeout reached
4. **Rate Limiting**: Apply processing rate limits
5. **MongoDB Upsert**: Bulk upsert with symbol+time uniqueness
6. **Error Handling**: Log errors and continue processing

## Deployment

### Docker Configuration
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
CMD ["python", "-m", "src.main"]
```

### Dependencies
- kafka-python==2.0.2
- pymongo==4.6.1
- python-dotenv==1.0.0