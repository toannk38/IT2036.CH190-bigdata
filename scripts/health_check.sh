#!/bin/bash
# Health check script for all services

echo "Checking service health..."
echo ""

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "✗ Docker is not running"
    exit 1
fi
echo "✓ Docker is running"

# Check containers
echo ""
echo "Container Status:"
docker-compose ps

# Check Kafka
echo ""
echo -n "Kafka: "
if docker exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092 > /dev/null 2>&1; then
    echo "✓ Healthy"
else
    echo "✗ Not healthy"
fi

# Check MongoDB
echo -n "MongoDB: "
if docker exec mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo "✓ Healthy"
else
    echo "✗ Not healthy"
fi

# Check API
echo -n "API Service: "
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo "✓ Healthy"
else
    echo "✗ Not healthy"
fi

# Check Airflow
echo -n "Airflow: "
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo "✓ Healthy"
else
    echo "✗ Not healthy"
fi

echo ""
echo "Health check complete!"
