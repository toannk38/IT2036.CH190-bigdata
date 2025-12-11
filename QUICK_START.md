# Quick Start Guide

Get the Vietnam Stock AI Backend up and running in 5 minutes!

## Prerequisites

- Docker Engine 20.10+ and Docker Compose 2.0+
- 4GB RAM available
- 10GB free disk space

## Installation Steps

### 1. Setup Environment

```bash
# Copy environment template
cp .env.template .env

# Edit with your API keys (optional for basic testing)
nano .env
```

### 2. Initialize System

Run the automated setup script:

```bash
bash scripts/init_system.sh
```

This will:
- ✓ Start all infrastructure services
- ✓ Create Kafka topics
- ✓ Initialize MongoDB with indexes
- ✓ Load stock symbols
- ✓ Start application services

### 3. Access Services

**Airflow UI**: http://localhost:8080
- Username: `admin`
- Password: `admin`

**API Documentation**: http://localhost:8000/docs

**MongoDB**: `mongodb://localhost:27017`

## Enable Data Collection

1. Open Airflow UI: http://localhost:8080
2. Enable these DAGs:
   - `price_collection` (runs every 5 minutes)
   - `news_collection` (runs every 30 minutes)
   - `analysis_pipeline` (runs every hour)

## Verify System

### Check Services

```bash
docker compose ps
```

All services should show "Up" or "Up (healthy)".

### Check Logs

```bash
# View all logs
docker compose logs -f

# View specific service
docker compose logs -f airflow
docker compose logs -f kafka-consumer
docker compose logs -f api-service
```

### Test API

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

### Check MongoDB

```bash
# List collections
docker exec stock-ai-mongodb mongosh vietnam_stock_ai --eval "db.getCollectionNames()"

# Count symbols
docker exec stock-ai-mongodb mongosh vietnam_stock_ai --eval "db.symbols.countDocuments()"
```

### Check Kafka Topics

```bash
# List topics
docker exec stock-ai-kafka kafka-topics --list --bootstrap-server localhost:9092

# Check topic details
docker exec stock-ai-kafka kafka-topics --describe --bootstrap-server localhost:9092 --topic stock_prices_raw
```

## Common Commands

### Start/Stop

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Restart a service
docker compose restart airflow
```

### View Logs

```bash
# Follow all logs
docker compose logs -f

# Follow specific service
docker compose logs -f kafka-consumer

# Last 100 lines
docker compose logs --tail=100 api-service
```

### Load More Symbols

```bash
# Load custom symbols file
python scripts/load_symbols.py data/your-symbols.json
```

## Troubleshooting

### Services Won't Start

```bash
# Check Docker resources
docker system df

# Clean up if needed
docker system prune

# Check specific service
docker compose logs [service-name]
```

### Port Already in Use

```bash
# Check what's using the port
sudo netstat -tuln | grep -E '8080|8000|27017|9092'

# Stop conflicting services or change ports in docker-compose.yml
```

### Reset Everything

```bash
# Stop and remove all containers and volumes
docker compose down -v

# Start fresh
bash scripts/init_system.sh
```

## Next Steps

1. **Configure LLM**: Add your OpenAI or Anthropic API key to `.env`
2. **Add More Symbols**: Load additional stock symbols
3. **Monitor DAGs**: Check Airflow UI for task execution
4. **Query API**: Use the API to get stock analysis

## Architecture Overview

```
┌─────────────┐
│   Airflow   │ ← Orchestrates workflows
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│  Collector  │ ──→ │    Kafka    │ ← Message streaming
└─────────────┘     └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Consumer   │ ← Stores data
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   MongoDB   │ ← Data storage
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Analysis   │ ← AI/ML + LLM
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │     API     │ ← REST endpoints
                    └─────────────┘
```

## Support

- **Documentation**: See `DOCKER_DEPLOYMENT.md` for detailed guide
- **Logs**: `docker compose logs -f [service]`
- **Issues**: Check GitHub issues

## Success Indicators

✓ All containers running: `docker compose ps`
✓ Airflow accessible: http://localhost:8080
✓ API accessible: http://localhost:8000/docs
✓ Symbols loaded: Check MongoDB
✓ DAGs enabled: Check Airflow UI
✓ Data flowing: Check Kafka topics

Happy analyzing! 📈
