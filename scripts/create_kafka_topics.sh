#!/bin/bash
# Script to create Kafka topics for the Vietnam Stock AI Backend
# Requirements: 9.1
# Creates topics with appropriate partitions and retention policies

set -e

# Configuration
KAFKA_CONTAINER="${KAFKA_CONTAINER:-stock-ai-kafka}"
KAFKA_BOOTSTRAP_SERVER="${KAFKA_BOOTSTRAP_SERVER:-localhost:9092}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Kafka Topics Creation Script ===${NC}"
echo "Container: $KAFKA_CONTAINER"
echo "Bootstrap Server: $KAFKA_BOOTSTRAP_SERVER"
echo ""

# Wait for Kafka to be ready
echo -e "${YELLOW}Waiting for Kafka to be ready...${NC}"
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
  if docker exec $KAFKA_CONTAINER kafka-broker-api-versions --bootstrap-server $KAFKA_BOOTSTRAP_SERVER > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Kafka is ready${NC}"
    break
  fi
  attempt=$((attempt + 1))
  echo "Attempt $attempt/$max_attempts - waiting..."
  sleep 2
done

if [ $attempt -eq $max_attempts ]; then
  echo -e "${YELLOW}Warning: Could not verify Kafka readiness, proceeding anyway...${NC}"
fi

echo ""
echo -e "${BLUE}Creating Kafka topics...${NC}"

# Create stock_prices_raw topic
# Retention: 7 days (604800000 ms)
# Partitions: 3 for parallel processing
echo "Creating topic: stock_prices_raw"
docker exec $KAFKA_CONTAINER kafka-topics --create \
  --bootstrap-server $KAFKA_BOOTSTRAP_SERVER \
  --topic stock_prices_raw \
  --partitions 3 \
  --replication-factor 1 \
  --config retention.ms=604800000 \
  --config segment.ms=86400000 \
  --config compression.type=lz4 \
  --if-not-exists

echo -e "${GREEN}✓ Created topic: stock_prices_raw (retention: 7 days, partitions: 3)${NC}"

# Create stock_news_raw topic
# Retention: 30 days (2592000000 ms)
# Partitions: 3 for parallel processing
echo "Creating topic: stock_news_raw"
docker exec $KAFKA_CONTAINER kafka-topics --create \
  --bootstrap-server $KAFKA_BOOTSTRAP_SERVER \
  --topic stock_news_raw \
  --partitions 3 \
  --replication-factor 1 \
  --config retention.ms=2592000000 \
  --config segment.ms=86400000 \
  --config compression.type=lz4 \
  --if-not-exists

echo -e "${GREEN}✓ Created topic: stock_news_raw (retention: 30 days, partitions: 3)${NC}"

# Create dead letter queue topics
# Retention: 30 days (2592000000 ms)
# Partitions: 1 (DLQ doesn't need parallelism)
echo "Creating topic: stock_prices_dlq"
docker exec $KAFKA_CONTAINER kafka-topics --create \
  --bootstrap-server $KAFKA_BOOTSTRAP_SERVER \
  --topic stock_prices_dlq \
  --partitions 1 \
  --replication-factor 1 \
  --config retention.ms=2592000000 \
  --if-not-exists

echo -e "${GREEN}✓ Created topic: stock_prices_dlq (retention: 30 days, partitions: 1)${NC}"

echo "Creating topic: stock_news_dlq"
docker exec $KAFKA_CONTAINER kafka-topics --create \
  --bootstrap-server $KAFKA_BOOTSTRAP_SERVER \
  --topic stock_news_dlq \
  --partitions 1 \
  --replication-factor 1 \
  --config retention.ms=2592000000 \
  --if-not-exists

echo -e "${GREEN}✓ Created topic: stock_news_dlq (retention: 30 days, partitions: 1)${NC}"

# List all topics
echo ""
echo -e "${BLUE}=== All Kafka Topics ===${NC}"
docker exec $KAFKA_CONTAINER kafka-topics --list --bootstrap-server $KAFKA_BOOTSTRAP_SERVER

# Describe topics for verification
echo ""
echo -e "${BLUE}=== Topic Details ===${NC}"
for topic in stock_prices_raw stock_news_raw stock_prices_dlq stock_news_dlq; do
  echo ""
  echo "Topic: $topic"
  docker exec $KAFKA_CONTAINER kafka-topics --describe \
    --bootstrap-server $KAFKA_BOOTSTRAP_SERVER \
    --topic $topic
done

echo ""
echo -e "${GREEN}✓ Kafka topics created successfully!${NC}"
