#!/bin/bash
# Quick start script for Vietnam Stock AI Backend

set -e

echo "=========================================="
echo "Vietnam Stock AI Backend - Quick Start"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.template .env
    echo "✓ Created .env file"
    echo "⚠ Please edit .env file with your API keys before proceeding"
    echo ""
    read -p "Press Enter to continue after editing .env..."
fi

# Start services
echo ""
echo "Starting Docker services..."
docker-compose up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 15

# Check service health
echo ""
echo "Checking service health..."

# Check Kafka
if docker exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092 > /dev/null 2>&1; then
    echo "✓ Kafka is healthy"
else
    echo "✗ Kafka is not healthy"
fi

# Check MongoDB
if docker exec mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo "✓ MongoDB is healthy"
else
    echo "✗ MongoDB is not healthy"
fi

# Initialize Kafka topics
echo ""
echo "Initializing Kafka topics..."
chmod +x scripts/create_kafka_topics.sh
./scripts/create_kafka_topics.sh

# Load example symbols (if file exists)
if [ -f data/symbols.example.json ]; then
    echo ""
    echo "Loading example symbols..."
    python scripts/load_symbols.py data/symbols.example.json
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Access the services:"
echo "  - Airflow UI: http://localhost:8080 (admin/admin)"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - MongoDB: mongodb://localhost:27017"
echo ""
echo "View logs:"
echo "  docker-compose logs -f"
echo ""
echo "Stop services:"
echo "  docker-compose down"
echo ""
