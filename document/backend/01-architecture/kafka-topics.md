# Kafka Topics Design

## Overview

Message queue architecture using Apache Kafka for asynchronous data processing, based on the producer pattern established in the existing code.

## Topic Configuration

### 1. stock_prices_raw

**Purpose**: Raw price data from data collector service
**Producer**: `StockKafkaProducer` from `services/data_collector`
**Consumer**: Kafka Consumer Service (planned)

```yaml
Topic: stock_prices_raw
Partitions: 10
Replication Factor: 3
Retention: 7 days (168 hours)
Compression: snappy
Cleanup Policy: delete
```

**Message Format** (Based on `DataNormalizer.normalize_price_data()`):
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

**Partitioning Strategy**:
```python
# Hash-based partitioning by symbol
partition = hash(symbol) % num_partitions
```

### 2. stock_news_raw

**Purpose**: Raw news data from news collector service
**Producer**: News Collector Service (planned)
**Consumer**: Kafka Consumer Service (planned)

```yaml
Topic: stock_news_raw
Partitions: 5
Replication Factor: 3
Retention: 30 days (720 hours)
Compression: gzip
Cleanup Policy: delete
```

**Message Format** (Based on planned `NewsNormalizer`):
```json
{
  "news_id": "hash_abc123",
  "symbol": "VCB",
  "title": "VCB công bố kế hoạch tăng vốn điều lệ",
  "content": "Nội dung tin tức đầy đủ...",
  "source": "VnExpress",
  "source_url": "https://vnexpress.net/...",
  "published_at": "2024-12-04T08:30:00+07:00",
  "collected_at": "2024-12-04T09:00:00+07:00",
  "category": "corporate_action",
  "tags": ["tăng vốn", "cổ phiếu"]
}
```

### 3. analysis_triggers

**Purpose**: Trigger analysis jobs for specific symbols
**Producer**: Kafka Consumer Service, Scheduler
**Consumer**: AI Analysis Service, LLM Analysis Service

```yaml
Topic: analysis_triggers
Partitions: 3
Replication Factor: 3
Retention: 24 hours
Compression: snappy
Cleanup Policy: delete
```

**Message Format**:
```json
{
  "trigger_id": "uuid-123",
  "symbol": "VCB",
  "trigger_type": "price_update", // price_update, news_update, scheduled
  "timestamp": "2024-12-04T09:15:00+07:00",
  "metadata": {
    "data_count": 1,
    "priority": "normal"
  }
}
```

### 4. analysis_results

**Purpose**: Analysis results for aggregation
**Producer**: AI Analysis Service, LLM Analysis Service
**Consumer**: Aggregation Service

```yaml
Topic: analysis_results
Partitions: 5
Replication Factor: 3
Retention: 7 days
Compression: snappy
Cleanup Policy: delete
```

**Message Format**:
```json
{
  "result_id": "uuid-456",
  "symbol": "VCB",
  "analysis_type": "technical", // technical, sentiment
  "timestamp": "2024-12-04T10:00:00+07:00",
  "results": {
    "score": 0.8,
    "confidence": 0.75,
    "details": { /* analysis-specific data */ }
  },
  "metadata": {
    "model_version": "v1.2",
    "processing_time": 2.5
  }
}
```

### 5. alerts

**Purpose**: Generated alerts and notifications
**Producer**: Aggregation Service
**Consumer**: Notification Service, API Service

```yaml
Topic: alerts
Partitions: 3
Replication Factor: 3
Retention: 30 days
Compression: snappy
Cleanup Policy: delete
```

**Message Format**:
```json
{
  "alert_id": "uuid-789",
  "symbol": "VCB",
  "alert_type": "buy_signal", // buy_signal, sell_signal, risk_alert
  "priority": "high", // low, medium, high, critical
  "timestamp": "2024-12-04T11:00:00+07:00",
  "message": "Strong technical and sentiment alignment",
  "data": {
    "final_score": 0.85,
    "recommendation": "BUY",
    "target_price": 92.0
  }
}
```

## Producer Configuration

### Current Implementation ✅
```python
# From services/data_collector/src/producers/kafka_producer.py
class StockKafkaProducer:
    def __init__(self, bootstrap_servers: str):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            # Additional configuration
            acks='all',                    # Wait for all replicas
            retries=3,                     # Retry failed sends
            batch_size=16384,              # Batch size in bytes
            linger_ms=10,                  # Wait time for batching
            buffer_memory=33554432,        # Total memory for buffering
            compression_type='snappy'       # Compression algorithm
        )
```

### Planned Producer Extensions 📋
```python
# Enhanced producer with monitoring
class EnhancedKafkaProducer(StockKafkaProducer):
    def __init__(self, bootstrap_servers: str, metrics_client=None):
        super().__init__(bootstrap_servers)
        self.metrics = metrics_client
    
    def send_with_metrics(self, topic: str, key: str, value: dict):
        start_time = time.time()
        try:
            future = self.producer.send(topic, key=key, value=value)
            result = future.get(timeout=10)
            
            # Record success metrics
            if self.metrics:
                self.metrics.increment(f'kafka.producer.success.{topic}')
                self.metrics.timing(f'kafka.producer.latency.{topic}', 
                                  time.time() - start_time)
            
            return result
        except Exception as e:
            # Record failure metrics
            if self.metrics:
                self.metrics.increment(f'kafka.producer.error.{topic}')
            raise
```

## Consumer Configuration

### Planned Consumer Groups 📋

#### 1. storage-consumers
**Purpose**: Store raw data to MongoDB
**Topics**: `stock_prices_raw`, `stock_news_raw`
**Instances**: 3-5 consumers

```python
# services/kafka_consumer/src/consumers/base_consumer.py
class BaseConsumer:
    def __init__(self, bootstrap_servers: str, group_id: str):
        self.consumer = KafkaConsumer(
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda m: m.decode('utf-8') if m else None,
            # Consumer configuration
            auto_offset_reset='earliest',   # Start from beginning if no offset
            enable_auto_commit=False,       # Manual offset management
            max_poll_records=100,           # Records per poll
            session_timeout_ms=30000,       # Session timeout
            heartbeat_interval_ms=10000,    # Heartbeat interval
            fetch_min_bytes=1024,           # Minimum fetch size
            fetch_max_wait_ms=500           # Maximum wait time
        )
```

#### 2. analysis-consumers
**Purpose**: Trigger analysis jobs
**Topics**: `analysis_triggers`
**Instances**: 2-3 consumers

#### 3. aggregation-consumers
**Purpose**: Process analysis results
**Topics**: `analysis_results`
**Instances**: 1-2 consumers

#### 4. notification-consumers
**Purpose**: Handle alerts and notifications
**Topics**: `alerts`
**Instances**: 1-2 consumers

## Message Serialization

### Current JSON Serialization ✅
```python
# From actual implementation
value_serializer=lambda v: json.dumps(v).encode('utf-8')
key_serializer=lambda k: k.encode('utf-8') if k else None
```

### Planned Schema Evolution 📋
```python
# Avro serialization for schema evolution
from confluent_kafka.avro import AvroProducer, AvroConsumer

# Schema registry configuration
schema_registry_conf = {
    'url': 'http://schema-registry:8081'
}

# Avro producer
avro_producer = AvroProducer({
    'bootstrap.servers': 'kafka:9092',
    'schema.registry.url': 'http://schema-registry:8081'
}, default_key_schema=key_schema, default_value_schema=value_schema)
```

## Error Handling and Dead Letter Queues

### Error Topics 📋
```yaml
# Dead letter queue for failed messages
Topic: stock_prices_raw_dlq
Partitions: 3
Retention: 7 days

Topic: stock_news_raw_dlq  
Partitions: 3
Retention: 7 days
```

### Error Handling Strategy 📋
```python
class ErrorHandler:
    def __init__(self, dlq_producer: KafkaProducer):
        self.dlq_producer = dlq_producer
        self.max_retries = 3
    
    def handle_processing_error(self, message, error, topic):
        retry_count = message.get('retry_count', 0)
        
        if retry_count < self.max_retries:
            # Retry with exponential backoff
            message['retry_count'] = retry_count + 1
            message['last_error'] = str(error)
            
            # Send back to original topic with delay
            self.schedule_retry(message, topic, delay=2**retry_count)
        else:
            # Send to dead letter queue
            dlq_topic = f"{topic}_dlq"
            self.dlq_producer.send(dlq_topic, value=message)
```

## Monitoring and Metrics

### Kafka Metrics 📋
```python
# Key metrics to monitor
metrics = {
    'producer': [
        'kafka.producer.record-send-rate',
        'kafka.producer.record-error-rate',
        'kafka.producer.request-latency-avg'
    ],
    'consumer': [
        'kafka.consumer.records-consumed-rate',
        'kafka.consumer.fetch-latency-avg',
        'kafka.consumer.lag-sum'
    ],
    'topics': [
        'kafka.topic.bytes-in-per-sec',
        'kafka.topic.bytes-out-per-sec',
        'kafka.topic.messages-in-per-sec'
    ]
}
```

### Health Checks 📋
```python
# Kafka health check
async def check_kafka_health():
    try:
        # Test producer
        producer = KafkaProducer(bootstrap_servers=KAFKA_SERVERS)
        producer.send('health-check', value={'timestamp': time.time()})
        producer.flush(timeout=5)
        
        # Test consumer
        consumer = KafkaConsumer('health-check', bootstrap_servers=KAFKA_SERVERS)
        consumer.poll(timeout_ms=5000)
        
        return {'status': 'healthy', 'latency': 'normal'}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}
```

## Performance Tuning

### Producer Optimization 📋
```python
# High-throughput producer configuration
producer_config = {
    'bootstrap_servers': KAFKA_SERVERS,
    'acks': 1,                      # Leader acknowledgment only
    'retries': 0,                   # No retries for speed
    'batch_size': 65536,            # Larger batch size
    'linger_ms': 50,                # Higher linger time
    'compression_type': 'lz4',      # Fast compression
    'buffer_memory': 67108864,      # Larger buffer
    'max_in_flight_requests_per_connection': 5
}
```

### Consumer Optimization 📋
```python
# High-throughput consumer configuration
consumer_config = {
    'bootstrap_servers': KAFKA_SERVERS,
    'group_id': 'high-throughput-consumers',
    'max_poll_records': 1000,       # Process more records per poll
    'fetch_min_bytes': 50000,       # Larger fetch size
    'fetch_max_wait_ms': 100,       # Lower wait time
    'session_timeout_ms': 60000,    # Longer session timeout
    'auto_offset_reset': 'latest'   # Start from latest
}
```

## Security Configuration

### Authentication 📋
```python
# SASL/SCRAM authentication
security_config = {
    'security_protocol': 'SASL_SSL',
    'sasl_mechanism': 'SCRAM-SHA-256',
    'sasl_plain_username': os.getenv('KAFKA_USERNAME'),
    'sasl_plain_password': os.getenv('KAFKA_PASSWORD'),
    'ssl_ca_location': '/path/to/ca-cert',
    'ssl_certificate_location': '/path/to/client-cert',
    'ssl_key_location': '/path/to/client-key'
}
```

### Topic ACLs 📋
```bash
# Producer permissions
kafka-acls --authorizer-properties zookeeper.connect=zk:2181 \
  --add --allow-principal User:data-collector \
  --operation Write --topic stock_prices_raw

# Consumer permissions  
kafka-acls --authorizer-properties zookeeper.connect=zk:2181 \
  --add --allow-principal User:kafka-consumer \
  --operation Read --topic stock_prices_raw \
  --group storage-consumers
```