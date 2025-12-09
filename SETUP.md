# Setup Guide - Vietnam Stock AI Backend

This guide will help you set up and run the Vietnam Stock AI Backend system.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the System](#running-the-system)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Python** (version 3.11+)
- **Make** (optional, for convenience commands)

### System Requirements

- **RAM**: Minimum 8GB (recommended 16GB)
- **Disk Space**: Minimum 10GB free space
- **OS**: Linux, macOS, or Windows with WSL2

### API Keys

You'll need API keys for LLM services:
- OpenAI API key (for GPT models)
- Anthropic API key (for Claude models)

## Installation

### 1. Clone or Navigate to Project

```bash
cd /path/to/vietnam-stock-ai-backend
```

### 2. Install Python Dependencies

#### Option A: Using Conda (Recommended for this project)

```bash
# Activate your conda environment
conda activate stock

# Install dependencies
pip install -r requirements.txt
```

#### Option B: Using pip with virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Option C: Create new conda environment from scratch

```bash
conda env create -f environment.yml
conda activate stock
```

## Configuration

### 1. Create Environment File

```bash
cp .env.template .env
```

### 2. Edit Configuration

Open `.env` and configure the following:

```bash
# Required: Add your API keys
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here

# Optional: Adjust other settings as needed
LOG_LEVEL=INFO
WEIGHT_TECHNICAL=0.4
WEIGHT_RISK=0.3
WEIGHT_SENTIMENT=0.3
```

### 3. Prepare Stock Symbols Data

Create a JSON file with stock symbols you want to track:

```bash
# Use the example file as a template
cp data/symbols.example.json data/symbols.json
# Edit data/symbols.json to add your symbols
```

## Running the System

### Option 1: Quick Start (Recommended)

```bash
./scripts/quickstart.sh
```

This script will:
- Start all Docker services
- Initialize Kafka topics
- Load example symbols
- Verify service health

### Option 2: Manual Start

#### Step 1: Start Services

```bash
docker-compose up -d
```

#### Step 2: Wait for Services

```bash
# Wait about 30 seconds for all services to start
sleep 30
```

#### Step 3: Initialize Kafka Topics

```bash
./scripts/create_kafka_topics.sh
```

#### Step 4: Load Stock Symbols

```bash
python scripts/load_symbols.py data/symbols.json
```

### Option 3: Using Makefile

```bash
make setup    # Setup environment
make start    # Start services
make init-kafka  # Initialize Kafka
make load-symbols FILE=data/symbols.json  # Load symbols
```

## Verification

### 1. Check Service Health

```bash
./scripts/health_check.sh
```

Or manually:

```bash
# Check all containers
docker-compose ps

# Check logs
docker-compose logs -f
```

### 2. Access Web Interfaces

- **Airflow UI**: http://localhost:8080
  - Username: `admin`
  - Password: `admin`
  
- **API Documentation**: http://localhost:8000/docs
  - Interactive Swagger UI
  - Test API endpoints

### 3. Verify Data Flow

#### Check MongoDB Collections

```bash
docker exec -it mongodb mongosh vietnam_stock_ai --eval "show collections"
```

#### Check Kafka Topics

```bash
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

#### View Kafka Messages

```bash
# View price data
docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic stock_prices_raw \
  --from-beginning \
  --max-messages 5

# View news data
docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic stock_news_raw \
  --from-beginning \
  --max-messages 5
```

### 4. Monitor Airflow DAGs

1. Open http://localhost:8080
2. Login with admin/admin
3. Check DAG status:
   - `price_collection` - Should run every 5 minutes
   - `news_collection` - Should run every 30 minutes
   - `analysis_pipeline` - Should run every hour

## Troubleshooting

### Services Won't Start

**Problem**: Docker containers fail to start

**Solution**:
```bash
# Check Docker is running
docker info

# Check logs for specific service
docker-compose logs kafka
docker-compose logs mongodb
docker-compose logs airflow

# Restart services
docker-compose restart
```

### Kafka Connection Issues

**Problem**: Cannot connect to Kafka

**Solution**:
```bash
# Check Kafka health
docker exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092

# Recreate Kafka topics
./scripts/create_kafka_topics.sh

# Check Kafka logs
docker-compose logs kafka
```

### MongoDB Connection Issues

**Problem**: Cannot connect to MongoDB

**Solution**:
```bash
# Check MongoDB health
docker exec mongodb mongosh --eval "db.adminCommand('ping')"

# Check MongoDB logs
docker-compose logs mongodb

# Restart MongoDB
docker-compose restart mongodb
```

### Airflow DAGs Not Running

**Problem**: DAGs are not executing

**Solution**:
1. Check Airflow UI at http://localhost:8080
2. Ensure DAGs are enabled (toggle switch)
3. Check task logs in Airflow UI
4. Verify environment variables in `.env`

### Port Conflicts

**Problem**: Ports already in use

**Solution**:
```bash
# Check what's using the ports
lsof -i :8080  # Airflow
lsof -i :8000  # API
lsof -i :9092  # Kafka
lsof -i :27017 # MongoDB

# Stop conflicting services or change ports in docker-compose.yml
```

### Out of Memory

**Problem**: Services crash due to memory

**Solution**:
- Increase Docker memory limit (Docker Desktop settings)
- Stop unnecessary services
- Reduce Kafka retention settings

### API Returns Errors

**Problem**: API endpoints return 500 errors

**Solution**:
```bash
# Check API logs
docker-compose logs api

# Check MongoDB connection
docker exec mongodb mongosh vietnam_stock_ai --eval "db.stats()"

# Restart API service
docker-compose restart api
```

## Stopping the System

### Stop All Services

```bash
docker-compose down
```

### Stop and Remove Volumes (Clean Slate)

```bash
docker-compose down -v
```

Or using Makefile:

```bash
make clean
```

## Next Steps

After successful setup:

1. **Monitor Data Collection**: Check Airflow UI for task execution
2. **Verify Data Storage**: Query MongoDB collections
3. **Test API Endpoints**: Use Swagger UI at http://localhost:8000/docs
4. **Review Logs**: Monitor logs for any errors
5. **Implement Collectors**: Continue with task 2 in the implementation plan

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Support

For issues or questions:
1. Check the logs: `docker-compose logs -f`
2. Run health check: `./scripts/health_check.sh`
3. Review this troubleshooting guide
4. Check the main README.md for architecture details
