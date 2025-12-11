# Docker Deployment Guide

This guide explains how to deploy the Vietnam Stock AI Backend using Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB RAM available for Docker
- At least 10GB free disk space

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd vietnam-stock-ai-backend

# Copy environment template
cp .env.template .env

# Edit .env file with your configuration
nano .env
```

### 2. Initialize System

Run the automated initialization script:

```bash
bash scripts/init_system.sh
```

This script will:
- Start infrastructure services (MongoDB, Kafka, Zookeeper)
- Wait for services to be healthy
- Create Kafka topics
- Load stock symbols into MongoDB
- Start application services (Airflow, Consumer, API)

### 3. Access Services

After initialization completes:

- **Airflow UI**: http://localhost:8080
  - Username: `admin`
  - Password: `admin`
  
- **API Documentation**: http://localhost:8000/docs

- **MongoDB**: `mongodb://localhost:27017`

- **Kafka**: `localhost:9092`

## Manual Deployment

If you prefer manual control:

### Step 1: Start Infrastructure

```bash
# Start MongoDB, Kafka, and Zookeeper
docker-compose up -d zookeeper kafka mongodb

# Wait for services to be healthy (check with docker ps)
docker ps
```

### Step 2: Create Kafka Topics

```bash
bash scripts/create_kafka_topics.sh
```

### Step 3: Load Stock Symbols

```bash
# Load VN30 symbols
python scripts/load_symbols.py data/vn30.json

# Or load custom symbols
python scripts/load_symbols.py path/to/your/symbols.json
```

### Step 4: Start Application Services

```bash
# Start Airflow, Consumer, and API
docker-compose up -d airflow kafka-consumer api-service
```

## Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Docker Network                         │
│                  (stock-ai-network)                      │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │Zookeeper │  │  Kafka   │  │ MongoDB  │             │
│  │  :2181   │  │  :9092   │  │  :27017  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│       │             │              │                    │
│       └─────────────┴──────────────┘                   │
│                     │                                   │
│  ┌──────────────────┴──────────────────┐              │
│  │                                      │              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │ Airflow  │  │ Consumer │  │   API    │            │
│  │  :8080   │  │          │  │  :8000   │            │
│  └──────────┘  └──────────┘  └──────────┘            │
└─────────────────────────────────────────────────────────┘
```

## Service Details

### Infrastructure Services

#### Zookeeper
- **Image**: confluentinc/cp-zookeeper:7.5.0
- **Port**: 2181
- **Purpose**: Kafka coordination

#### Kafka
- **Image**: confluentinc/cp-kafka:7.5.0
- **Port**: 9092
- **Purpose**: Message streaming
- **Topics**:
  - `stock_prices_raw` (3 partitions, 7 days retention)
  - `stock_news_raw` (3 partitions, 30 days retention)
  - `stock_prices_dlq` (1 partition, 30 days retention)
  - `stock_news_dlq` (1 partition, 30 days retention)

#### MongoDB
- **Image**: mongo:7.0
- **Port**: 27017
- **Purpose**: Data storage
- **Collections**:
  - `symbols` - Stock symbol metadata
  - `price_history` - Historical price data
  - `news` - News articles
  - `ai_analysis` - AI/ML analysis results
  - `llm_analysis` - LLM analysis results
  - `final_scores` - Aggregated recommendations

### Application Services

#### Airflow
- **Port**: 8080
- **Purpose**: Workflow orchestration
- **Executor**: SequentialExecutor (SQLite backend)
- **DAGs**:
  - `price_collection` - Runs every 5 minutes
  - `news_collection` - Runs every 30 minutes
  - `analysis_pipeline` - Runs every hour

#### Kafka Consumer
- **Purpose**: Consumes messages from Kafka and stores in MongoDB
- **Topics**: Subscribes to `stock_prices_raw` and `stock_news_raw`

#### API Service
- **Port**: 8000
- **Purpose**: REST API for client applications
- **Framework**: FastAPI
- **Endpoints**:
  - `GET /stock/{symbol}/summary` - Stock summary
  - `GET /alerts` - Active alerts
  - `GET /stock/{symbol}/history` - Historical data

## Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# MongoDB
MONGODB_URI=mongodb://mongodb:27017
MONGODB_DATABASE=vietnam_stock_ai

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:29092
KAFKA_PRICE_TOPIC=stock_prices_raw
KAFKA_NEWS_TOPIC=stock_news_raw

# LLM (Optional)
OPENAI_API_KEY=your_key_here
```

### Volume Mounts

Data is persisted in Docker volumes:

- `mongodb_data` - MongoDB database files
- `kafka_data` - Kafka message logs
- `airflow_data` - Airflow metadata (SQLite)
- `airflow_logs` - Airflow task logs

## Common Operations

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f airflow
docker-compose logs -f kafka-consumer
docker-compose logs -f api-service
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart airflow
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v
```

### Check Service Status

```bash
# List running containers
docker-compose ps

# Check service health
docker inspect stock-ai-mongodb --format='{{.State.Health.Status}}'
docker inspect stock-ai-kafka --format='{{.State.Health.Status}}'
```

### Scale Consumer

```bash
# Run multiple consumer instances
docker-compose up -d --scale kafka-consumer=3
```

## Troubleshooting

### Services Won't Start

1. Check Docker resources:
   ```bash
   docker system df
   docker system prune  # Clean up if needed
   ```

2. Check service logs:
   ```bash
   docker-compose logs [service-name]
   ```

3. Verify ports are not in use:
   ```bash
   netstat -tuln | grep -E '8080|8000|27017|9092'
   ```

### Kafka Connection Issues

1. Verify Kafka is healthy:
   ```bash
   docker exec stock-ai-kafka kafka-broker-api-versions --bootstrap-server localhost:9092
   ```

2. List topics:
   ```bash
   docker exec stock-ai-kafka kafka-topics --list --bootstrap-server localhost:9092
   ```

3. Check consumer groups:
   ```bash
   docker exec stock-ai-kafka kafka-consumer-groups --list --bootstrap-server localhost:9092
   ```

### MongoDB Connection Issues

1. Test connection:
   ```bash
   docker exec stock-ai-mongodb mongosh --eval "db.adminCommand('ping')"
   ```

2. Check collections:
   ```bash
   docker exec stock-ai-mongodb mongosh vietnam_stock_ai --eval "db.getCollectionNames()"
   ```

### Airflow Issues

1. Check Airflow logs:
   ```bash
   docker-compose logs -f airflow
   ```

2. Access Airflow CLI:
   ```bash
   docker exec -it stock-ai-airflow airflow dags list
   docker exec -it stock-ai-airflow airflow tasks list price_collection
   ```

3. Reset Airflow database:
   ```bash
   docker-compose down airflow
   docker volume rm vietnam-stock-ai-backend_airflow_data
   docker-compose up -d airflow
   ```

## Performance Tuning

### For Development

The default configuration is optimized for development with minimal resource usage.

### For Production

1. **Increase Kafka partitions**:
   ```bash
   docker exec stock-ai-kafka kafka-topics --alter \
     --bootstrap-server localhost:9092 \
     --topic stock_prices_raw \
     --partitions 6
   ```

2. **Add MongoDB indexes** (already done in init-mongo.js)

3. **Scale consumers**:
   ```bash
   docker-compose up -d --scale kafka-consumer=3
   ```

4. **Increase API workers** (edit docker/Dockerfile.api):
   ```dockerfile
   CMD ["uvicorn", "src.services.api_service:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
   ```

## Backup and Restore

### Backup MongoDB

```bash
# Create backup
docker exec stock-ai-mongodb mongodump --out=/data/backup

# Copy backup to host
docker cp stock-ai-mongodb:/data/backup ./mongodb-backup
```

### Restore MongoDB

```bash
# Copy backup to container
docker cp ./mongodb-backup stock-ai-mongodb:/data/restore

# Restore
docker exec stock-ai-mongodb mongorestore /data/restore
```

### Backup Kafka Topics

```bash
# Export topic data
docker exec stock-ai-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic stock_prices_raw \
  --from-beginning \
  --max-messages 10000 > kafka-backup.json
```

## Security Considerations

For production deployment:

1. **Change default passwords** in Airflow
2. **Use Docker secrets** for sensitive data
3. **Enable MongoDB authentication**
4. **Use SSL/TLS** for Kafka
5. **Implement API authentication**
6. **Use reverse proxy** (nginx) for API
7. **Restrict network access** with firewall rules

## Monitoring

### Health Checks

All services have health checks configured. Check status:

```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Resource Usage

```bash
# Monitor resource usage
docker stats

# Check disk usage
docker system df
```

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f [service]`
2. Review this documentation
3. Check GitHub issues
4. Contact maintainers

## License

[Your License Here]
