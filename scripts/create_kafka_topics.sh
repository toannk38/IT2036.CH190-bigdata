#!/bin/bash
# Script to create Kafka topics for the Vietnam Stock AI Backend

set -e

KAFKA_CONTAINER="kafka"
KAFKA_BOOTSTRAP_SERVER="localhost:9092"

echo "Creating Kafka topics..."

# Create stock_prices_raw topic
docker exec $KAFKA_CONTAINER kafka-topics --create \
  --bootstrap-server $KAFKA_BOOTSTRAP_SERVER \
  --topic stock_prices_raw \
  --partitions 3 \
  --replication-factor 1 \
  --config retention.ms=604800000 \
  --if-not-exists

echo "Created topic: stock_prices_raw (retention: 7 days)"

# Create stock_news_raw topic
docker exec $KAFKA_CONTAINER kafka-topics --create \
  --bootstrap-server $KAFKA_BOOTSTRAP_SERVER \
  --topic stock_news_raw \
  --partitions 3 \
  --replication-factor 1 \
  --config retention.ms=2592000000 \
  --if-not-exists

echo "Created topic: stock_news_raw (retention: 30 days)"

# Create dead letter queue topics
docker exec $KAFKA_CONTAINER kafka-topics --create \
  --bootstrap-server $KAFKA_BOOTSTRAP_SERVER \
  --topic stock_prices_dlq \
  --partitions 1 \
  --replication-factor 1 \
  --config retention.ms=2592000000 \
  --if-not-exists

echo "Created topic: stock_prices_dlq (retention: 30 days)"

docker exec $KAFKA_CONTAINER kafka-topics --create \
  --bootstrap-server $KAFKA_BOOTSTRAP_SERVER \
  --topic stock_news_dlq \
  --partitions 1 \
  --replication-factor 1 \
  --config retention.ms=2592000000 \
  --if-not-exists

echo "Created topic: stock_news_dlq (retention: 30 days)"

# List all topics
echo ""
echo "All Kafka topics:"
docker exec $KAFKA_CONTAINER kafka-topics --list --bootstrap-server $KAFKA_BOOTSTRAP_SERVER

echo ""
echo "Kafka topics created successfully!"
