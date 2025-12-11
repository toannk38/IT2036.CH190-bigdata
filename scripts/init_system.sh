#!/bin/bash
# System Initialization Script
# Requirements: 2.3, 9.1, 10.1, 10.2, 10.3, 10.4
# 
# This script initializes the entire Vietnam Stock AI Backend system:
# 1. Starts infrastructure services (MongoDB, Kafka, Zookeeper)
# 2. Waits for services to be healthy
# 3. Creates Kafka topics
# 4. Loads stock symbols into MongoDB
# 5. Starts application services (Airflow, Consumer, API)

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
SYMBOLS_FILE="${SYMBOLS_FILE:-data/vn30.json}"
MAX_WAIT_TIME=120  # Maximum wait time in seconds

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Vietnam Stock AI Backend - System Initialization        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to check if a service is healthy
check_service_health() {
    local service_name=$1
    local max_attempts=$2
    local attempt=0
    
    echo -e "${YELLOW}Waiting for $service_name to be healthy...${NC}"
    
    while [ $attempt -lt $max_attempts ]; do
        if docker inspect --format='{{.State.Health.Status}}' "stock-ai-$service_name" 2>/dev/null | grep -q "healthy"; then
            echo -e "${GREEN}✓ $service_name is healthy${NC}"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo "  Attempt $attempt/$max_attempts..."
        sleep 2
    done
    
    echo -e "${RED}✗ $service_name failed to become healthy${NC}"
    return 1
}

# Function to check if a container is running
check_container_running() {
    local container_name=$1
    
    if docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
        return 0
    else
        return 1
    fi
}

# Step 1: Check if Docker is running
echo -e "${BLUE}[1/7] Checking Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"
echo ""

# Step 2: Start infrastructure services
echo -e "${BLUE}[2/7] Starting infrastructure services...${NC}"
docker-compose up -d zookeeper kafka mongodb
echo -e "${GREEN}✓ Infrastructure services started${NC}"
echo ""

# Step 3: Wait for services to be healthy
echo -e "${BLUE}[3/7] Waiting for services to be healthy...${NC}"

# Wait for MongoDB
if ! check_service_health "mongodb" 30; then
    echo -e "${RED}Failed to start MongoDB. Check logs with: docker logs stock-ai-mongodb${NC}"
    exit 1
fi

# Wait for Kafka
if ! check_service_health "kafka" 30; then
    echo -e "${RED}Failed to start Kafka. Check logs with: docker logs stock-ai-kafka${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All infrastructure services are healthy${NC}"
echo ""

# Step 4: Create Kafka topics
echo -e "${BLUE}[4/7] Creating Kafka topics...${NC}"
if bash scripts/create_kafka_topics.sh; then
    echo -e "${GREEN}✓ Kafka topics created${NC}"
else
    echo -e "${YELLOW}Warning: Some Kafka topics may already exist${NC}"
fi
echo ""

# Step 5: Load stock symbols
echo -e "${BLUE}[5/7] Loading stock symbols...${NC}"
if [ -f "$SYMBOLS_FILE" ]; then
    if python3 scripts/load_symbols.py "$SYMBOLS_FILE"; then
        echo -e "${GREEN}✓ Stock symbols loaded${NC}"
    else
        echo -e "${YELLOW}Warning: Failed to load symbols, but continuing...${NC}"
    fi
else
    echo -e "${YELLOW}Warning: Symbols file not found: $SYMBOLS_FILE${NC}"
    echo -e "${YELLOW}You can load symbols later with: python scripts/load_symbols.py <file>${NC}"
fi
echo ""

# Step 6: Start application services
echo -e "${BLUE}[6/7] Starting application services...${NC}"
docker-compose up -d airflow kafka-consumer api-service
echo -e "${GREEN}✓ Application services started${NC}"
echo ""

# Step 7: Wait for application services
echo -e "${BLUE}[7/7] Waiting for application services to be ready...${NC}"

# Wait for Airflow (no health check, just wait)
echo -e "${YELLOW}Waiting for Airflow to initialize (this may take 1-2 minutes)...${NC}"
sleep 30

# Wait for API service
if ! check_service_health "api" 20; then
    echo -e "${YELLOW}Warning: API service may not be fully ready${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   System Initialization Complete!                         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Service URLs:${NC}"
echo "  • Airflow UI:  http://localhost:8080 (admin/admin)"
echo "  • API Service: http://localhost:8000"
echo "  • MongoDB:     mongodb://localhost:27017"
echo "  • Kafka:       localhost:9092"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "  • View logs:        docker-compose logs -f [service]"
echo "  • Stop services:    docker-compose down"
echo "  • Restart service:  docker-compose restart [service]"
echo "  • Check status:     docker-compose ps"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Access Airflow UI at http://localhost:8080"
echo "  2. Enable DAGs: price_collection, news_collection, analysis_pipeline"
echo "  3. Monitor API at http://localhost:8000/docs"
echo ""
echo -e "${GREEN}✓ Ready to collect and analyze stock data!${NC}"
