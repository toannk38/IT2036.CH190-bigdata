# Deployment Checklist - Vietnam Stock AI Backend

## Pre-Deployment Verification ✅

### Code Quality
- ✅ All 177 unit tests passing
- ✅ All 34 property-based tests passing
- ✅ Zero test failures
- ✅ Error handling validated
- ✅ Retry mechanisms tested

### Docker Configuration
- ✅ docker-compose.yml configured
- ✅ All Dockerfiles created (Airflow, Consumer, API)
- ✅ Health checks defined for all services
- ✅ Networks and volumes configured
- ✅ Environment variables set

### Initialization Scripts
- ✅ init-mongo.js ready
- ✅ create_kafka_topics.sh ready
- ✅ init_system.sh ready
- ✅ load_symbols.py ready

## Deployment Steps

### 1. Environment Setup
```bash
# Copy environment template
cp .env.template .env

# Edit .env and add your API keys
# - OPENAI_API_KEY (required for LLM analysis)
# - Any other custom configurations
```

### 2. Start Infrastructure
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# Expected services:
# - stock-ai-zookeeper (healthy)
# - stock-ai-kafka (healthy)
# - stock-ai-mongodb (healthy)
# - stock-ai-airflow (running)
# - stock-ai-consumer (running)
# - stock-ai-api (running)
```

### 3. Verify Services

#### MongoDB
```bash
# Check MongoDB is accessible
docker exec -it stock-ai-mongodb mongosh --eval "db.adminCommand('ping')"

# Expected: { ok: 1 }
```

#### Kafka
```bash
# List Kafka topics
docker exec -it stock-ai-kafka kafka-topics --list --bootstrap-server localhost:9092

# Expected topics:
# - stock_prices_raw
# - stock_news_raw
# - stock_prices_dlq
# - stock_news_dlq
```

#### Airflow
```bash
# Access Airflow Web UI
# URL: http://localhost:8080
# Username: admin
# Password: admin

# Check DAGs are loaded:
# - price_collection (schedule: */5 * * * *)
# - news_collection (schedule: */30 * * * *)
# - analysis_pipeline (schedule: @hourly)
```

#### API Service
```bash
# Test API health
curl http://localhost:8000/

# Expected: {"message": "Vietnam Stock AI Backend API", "status": "running"}
```

### 4. Load Initial Data
```bash
# Load stock symbols
docker exec -it stock-ai-airflow python /opt/airflow/scripts/load_symbols.py /opt/airflow/data/vn30.json

# Verify symbols loaded
docker exec -it stock-ai-mongodb mongosh vietnam_stock_ai --eval "db.symbols.countDocuments()"

# Expected: 30 (for VN30 index)
```

### 5. Monitor Initial Runs

#### Check Airflow Logs
```bash
# View Airflow scheduler logs
docker logs -f stock-ai-airflow

# Look for:
# - DAG parsing success
# - Task scheduling
# - Task execution
```

#### Check Consumer Logs
```bash
# View Kafka consumer logs
docker logs -f stock-ai-consumer

# Look for:
# - Kafka connection success
# - MongoDB connection success
# - Message consumption
```

#### Check API Logs
```bash
# View API service logs
docker logs -f stock-ai-api

# Look for:
# - FastAPI startup
# - MongoDB connection success
```

### 6. Validate Data Flow

#### Wait for First Collection Run (5 minutes)
```bash
# Check price data collected
docker exec -it stock-ai-mongodb mongosh vietnam_stock_ai --eval "db.price_history.countDocuments()"

# Expected: > 0 after first price collection run
```

#### Wait for News Collection (30 minutes)
```bash
# Check news data collected
docker exec -it stock-ai-mongodb mongosh vietnam_stock_ai --eval "db.news.countDocuments()"

# Expected: > 0 after first news collection run
```

#### Wait for Analysis Run (1 hour)
```bash
# Check AI/ML analysis results
docker exec -it stock-ai-mongodb mongosh vietnam_stock_ai --eval "db.ai_analysis.countDocuments()"

# Check LLM analysis results
docker exec -it stock-ai-mongodb mongosh vietnam_stock_ai --eval "db.llm_analysis.countDocuments()"

# Check final scores
docker exec -it stock-ai-mongodb mongosh vietnam_stock_ai --eval "db.final_scores.countDocuments()"

# Expected: > 0 after first analysis run
```

### 7. Test API Endpoints

#### Get Stock Summary
```bash
curl http://localhost:8000/stock/VNM/summary | jq
```

#### Get Alerts
```bash
curl http://localhost:8000/alerts?limit=10 | jq
```

#### Get Historical Analysis
```bash
curl "http://localhost:8000/stock/VNM/history?start_date=2024-01-01&end_date=2024-12-31" | jq
```

## Post-Deployment Monitoring

### Daily Checks
- [ ] Airflow DAGs running on schedule
- [ ] No failed tasks in Airflow
- [ ] Kafka consumer processing messages
- [ ] MongoDB data growing
- [ ] API responding within 2 seconds

### Weekly Checks
- [ ] Review error logs
- [ ] Check disk usage (MongoDB, Kafka)
- [ ] Verify data quality
- [ ] Review alert accuracy

### Monthly Checks
- [ ] Update stock symbols list
- [ ] Review and tune analysis weights
- [ ] Optimize MongoDB indexes
- [ ] Clean up old data (if needed)

## Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs [service-name]

# Restart specific service
docker-compose restart [service-name]

# Rebuild and restart
docker-compose up -d --build [service-name]
```

### Airflow DAGs Not Loading
```bash
# Check DAG parsing errors
docker exec -it stock-ai-airflow airflow dags list

# Check for syntax errors
docker exec -it stock-ai-airflow python -m py_compile /opt/airflow/dags/*.py
```

### Kafka Consumer Not Processing
```bash
# Check consumer group status
docker exec -it stock-ai-kafka kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group stock-ai-consumer-group

# Reset consumer offset (if needed)
docker exec -it stock-ai-kafka kafka-consumer-groups --bootstrap-server localhost:9092 --group stock-ai-consumer-group --reset-offsets --to-earliest --all-topics --execute
```

### MongoDB Connection Issues
```bash
# Check MongoDB status
docker exec -it stock-ai-mongodb mongosh --eval "db.serverStatus()"

# Check connections
docker exec -it stock-ai-mongodb mongosh --eval "db.serverStatus().connections"
```

## Rollback Procedure

### Stop All Services
```bash
docker-compose down
```

### Preserve Data (Optional)
```bash
# Backup MongoDB data
docker run --rm -v stock-ai_mongodb_data:/data -v $(pwd)/backup:/backup ubuntu tar czf /backup/mongodb-backup-$(date +%Y%m%d).tar.gz /data

# Backup Kafka data
docker run --rm -v stock-ai_kafka_data:/data -v $(pwd)/backup:/backup ubuntu tar czf /backup/kafka-backup-$(date +%Y%m%d).tar.gz /data
```

### Clean Up (If Needed)
```bash
# Remove all containers and volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all
```

## Success Criteria

✅ All services running and healthy  
✅ Airflow DAGs executing on schedule  
✅ Data flowing from collectors → Kafka → MongoDB  
✅ Analysis engines producing results  
✅ API endpoints responding correctly  
✅ No critical errors in logs  
✅ System running for 24+ hours without issues  

---

**Deployment Status:** Ready for deployment  
**Last Verified:** December 11, 2025  
**Test Results:** 177/177 passed (100%)
