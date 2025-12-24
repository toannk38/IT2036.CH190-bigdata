# Kafka Service Documentation

## Overview

The Kafka service acts as the central message broker for the Vietnam Stock AI system, handling real-time data streaming between data collectors, processors, and consumers. It provides reliable, scalable message queuing for stock prices, news articles, and analysis results.

## Architecture

### Components
- **Kafka Broker**: Core message streaming platform
- **Zookeeper**: Coordination service for Kafka cluster management
- **Topics**: Organized message channels for different data types
- **Producers**: Services that publish messages to topics
- **Consumers**: Services that subscribe to and process messages

### Data Flow
```
Data Collectors → Kafka Topics → Data Consumers → MongoDB
     ↓              ↓              ↓
Price Collector → stock_prices_raw → Price Consumer
News Collector  → stock_news_raw  → News Consumer
```

## Topics

### stock_prices_raw
**Purpose**: Real-time stock price data from vnstock API

**Message Schema**:
```json
{
  "symbol": "VIC",
  "timestamp": 1703123456.789,
  "open": 85.5,
  "close": 87.2,
  "high": 88.0,
  "low": 85.0,
  "volume": 1250000
}
```

**Producers**: Price Collection DAG (Airflow)
**Consumers**: Kafka Data Consumer
**Frequency**: Every 5 minutes
**Retention**: 7 days

### stock_news_raw
**Purpose**: Stock-related news articles and sentiment data

**Message Schema**:
```json
{
  "symbol": "VIC",
  "title": "VIC announces Q4 results",
  "content": "Full article content...",
  "source": "vnstock",
  "published_at": 1703123456.789,
  "collected_at": 1703123456.789
}
```

**Producers**: News Collection DAG (Airflow)
**Consumers**: Kafka Data Consumer
**Frequency**: Every 30 minutes
**Retention**: 30 days

## Configuration

### Docker Compose Setup
```yaml
kafka:
  image: confluentinc/cp-kafka:7.5.0
  ports:
    - "127.0.0.1:9092:9092"
  environment:
    KAFKA_BROKER_ID: 1
    KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
    KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
    KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
    KAFKA_LOG_RETENTION_HOURS: 168
```

### Environment Variables
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker addresses (default: localhost:9092)
- `KAFKA_CONSUMER_GROUP`: Consumer group ID for offset management
- `KAFKA_AUTO_OFFSET_RESET`: Offset reset policy (earliest/latest)

## Producers

### Price Collector
**Location**: `src/collectors/price_collector.py`
**Trigger**: Airflow DAG every 5 minutes
**Function**: Fetches stock prices from vnstock and publishes to `stock_prices_raw`

**Key Features**:
- Batch processing of all active symbols
- Error handling for individual symbol failures
- Automatic retry logic
- Structured logging

### News Collector
**Location**: `src/collectors/news_collector.py`
**Trigger**: Airflow DAG every 30 minutes
**Function**: Fetches news articles and publishes to `stock_news_raw`

## Consumers

### Kafka Data Consumer
**Location**: `src/consumers/kafka_consumer.py`
**Function**: Consumes messages from all topics and stores in MongoDB

**Key Features**:
- Schema validation for incoming messages
- Automatic timestamp conversion (ISO to epoch)
- Offset management with manual commits
- Retry logic for MongoDB operations
- Error recovery and logging

**Consumer Groups**:
- `stock_ai_consumer`: Main consumer group for data processing

## Operations

### Starting the Service
```bash
# Start infrastructure services
cd infrastructure
docker-compose up -d kafka zookeeper

# Verify Kafka is running
docker logs stock-ai-kafka
```

### Topic Management
```bash
# List topics
docker exec stock-ai-kafka kafka-topics --bootstrap-server localhost:9092 --list

# Create topic manually
docker exec stock-ai-kafka kafka-topics --bootstrap-server localhost:9092 \
  --create --topic stock_prices_raw --partitions 3 --replication-factor 1

# Check topic details
docker exec stock-ai-kafka kafka-topics --bootstrap-server localhost:9092 \
  --describe --topic stock_prices_raw
```

### Monitoring
```bash
# Check consumer group status
docker exec stock-ai-kafka kafka-consumer-groups --bootstrap-server localhost:9092 \
  --describe --group stock_ai_consumer

# Monitor message flow
docker exec stock-ai-kafka kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic stock_prices_raw --from-beginning --max-messages 10
```

## Health Checks

### Kafka Broker Health
```bash
# Check broker API versions (health check)
docker exec stock-ai-kafka kafka-broker-api-versions --bootstrap-server localhost:9092
```

### Message Flow Verification
```bash
# Produce test message
echo '{"test": "message"}' | docker exec -i stock-ai-kafka \
  kafka-console-producer --bootstrap-server localhost:9092 --topic test

# Consume test message
docker exec stock-ai-kafka kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic test --from-beginning --timeout-ms 5000
```

## Troubleshooting

### Common Issues

**1. Connection Refused**
- Check if Kafka container is running: `docker ps | grep kafka`
- Verify port mapping: `docker port stock-ai-kafka`
- Check Zookeeper connectivity

**2. Topic Not Found**
- Enable auto-create topics: `KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"`
- Create topic manually using kafka-topics command

**3. Consumer Lag**
- Monitor consumer group lag: `kafka-consumer-groups --describe`
- Scale consumers or optimize processing logic
- Check MongoDB connection and performance

**4. Message Serialization Errors**
- Verify message schema matches expected format
- Check JSON encoding/decoding in producers/consumers
- Review error logs for specific validation failures

### Log Locations
- Kafka logs: `docker logs stock-ai-kafka`
- Consumer logs: Application logs in `src/consumers/kafka_consumer.py`
- Producer logs: Application logs in `src/collectors/`

## Performance Tuning

### Kafka Configuration
```yaml
# High throughput settings
KAFKA_NUM_NETWORK_THREADS: 8
KAFKA_NUM_IO_THREADS: 8
KAFKA_SOCKET_SEND_BUFFER_BYTES: 102400
KAFKA_SOCKET_RECEIVE_BUFFER_BYTES: 102400
KAFKA_SOCKET_REQUEST_MAX_BYTES: 104857600
```

### Consumer Optimization
- Adjust `max_records` in poll() for batch size
- Use multiple consumer instances for parallel processing
- Optimize MongoDB write operations with bulk inserts

## Security

### Network Security
- Kafka bound to localhost (127.0.0.1) only
- Internal Docker network isolation
- No external exposure by default

### Data Security
- Messages contain no sensitive authentication data
- Stock symbols and prices are public information
- Consider encryption for production deployments

## Backup and Recovery

### Data Persistence
- Kafka data: `./volumes/kafka/data`
- Zookeeper data: `./volumes/zookeeper/data`
- Retention policies prevent indefinite storage

### Recovery Procedures
1. Stop services: `docker-compose down`
2. Backup volumes: `cp -r volumes volumes_backup`
3. Restart services: `docker-compose up -d`
4. Verify topic and data integrity

## Integration Points

### With Airflow
- DAGs trigger data collection every 5-30 minutes
- Producers publish to Kafka topics
- Error handling and retry logic in DAG tasks

### With MongoDB
- Consumers store processed messages
- Schema validation before storage
- Automatic timestamp conversion

### With API Service
- API reads processed data from MongoDB
- Real-time data availability through Kafka pipeline
- Historical data access for analysis