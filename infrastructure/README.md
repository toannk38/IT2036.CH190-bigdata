# Infrastructure Services

This directory contains the infrastructure services for the Vietnam Stock AI Backend system.

## Services

### 1. MongoDB (Port 27017)
- **Purpose**: Primary database for storing stock data, analysis results, and system metadata
- **Data Location**: `./volumes/mongodb/data`
- **Version**: MongoDB 7.0

### 2. Apache Kafka (Port 9092)
- **Purpose**: Message broker for streaming stock prices and news data
- **Data Location**: `./volumes/kafka/data`
- **Version**: Confluent Kafka 7.5.0
- **Topics**: 
  - `stock_prices_raw`: Real-time stock price data
  - `stock_news_raw`: Stock news articles

### 3. Zookeeper (Port 2181)
- **Purpose**: Coordination service for Kafka
- **Data Location**: `./volumes/zookeeper/data`
- **Version**: Confluent Zookeeper 7.5.0

## Quick Start

### Start Infrastructure Services

```bash
# From the infrastructure directory
cd infrastructure
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### Stop Infrastructure Services

```bash
cd infrastructure
docker-compose down

# To remove volumes as well (WARNING: This deletes all data)
docker-compose down -v
```

### Verify Services

```bash
# Check MongoDB
mongosh mongodb://localhost:27017/vietnam_stock_ai

# Check Kafka topics
docker exec -it stock-ai-kafka kafka-topics --list --bootstrap-server localhost:9092

# Create Kafka topics manually (if needed)
docker exec -it stock-ai-kafka kafka-topics --create --topic stock_prices_raw --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
docker exec -it stock-ai-kafka kafka-topics --create --topic stock_news_raw --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

## Data Persistence

All data is stored in the `./volumes/` directory:

```
infrastructure/volumes/
├── mongodb/
│   ├── data/          # MongoDB database files
│   └── config/        # MongoDB configuration
├── kafka/
│   └── data/          # Kafka message logs
├── zookeeper/
│   ├── data/          # Zookeeper data
│   └── logs/          # Zookeeper logs
└── airflow/
    ├── data/          # Airflow metadata (SQLite)
    └── logs/          # Airflow task logs
```

### Backup

To backup all infrastructure data:

```bash
cd infrastructure
tar -czf backup-$(date +%Y%m%d).tar.gz volumes/
```

### Restore

To restore from backup:

```bash
cd infrastructure
docker-compose down
tar -xzf backup-YYYYMMDD.tar.gz
docker-compose up -d
```

## Network

All services are connected via the `stock-ai-network` bridge network. This network is shared with application services in the root docker-compose.yml.

## Health Checks

- **MongoDB**: Checks if MongoDB is responding to ping commands
- **Kafka**: Checks if Kafka broker API is accessible

## Troubleshooting

### MongoDB Connection Issues

```bash
# Check MongoDB logs
docker logs stock-ai-mongodb

# Connect to MongoDB shell
docker exec -it stock-ai-mongodb mongosh
```

### Kafka Connection Issues

```bash
# Check Kafka logs
docker logs stock-ai-kafka

# Check Zookeeper logs
docker logs stock-ai-zookeeper

# List Kafka topics
docker exec -it stock-ai-kafka kafka-topics --list --bootstrap-server localhost:9092
```

### Port Conflicts

If you get port binding errors, check if ports are already in use:

```bash
# Check port usage
sudo lsof -i :27017  # MongoDB
sudo lsof -i :9092   # Kafka
sudo lsof -i :2181   # Zookeeper
```

## Resource Requirements

- **Memory**: Minimum 4GB RAM recommended
- **Disk**: Minimum 10GB free space for data volumes
- **CPU**: 2+ cores recommended

## Security Notes

- All services are bound to `127.0.0.1` (localhost only) for security
- No authentication is configured by default (suitable for development only)
- For production, enable authentication and use proper secrets management
