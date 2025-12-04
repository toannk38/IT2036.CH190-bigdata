# Kế hoạch Thiết kế Hệ thống Backend - Phần 3

## Mục lục
- [6. API Layer](#6-api-layer)
- [7. Non-functional Requirements](#7-non-functional-requirements)
- [8. Deployment Plan](#8-deployment-plan)
- [9. Roadmap phát triển 3 tháng](#9-roadmap-phát-triển-3-tháng)

---

## 6. API Layer

### 6.1 Kiến trúc API Service

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Dashboard]
        MOBILE[Mobile App]
        API_CLIENT[Third-party APIs]
    end
    
    subgraph "API Gateway"
        GATEWAY[Kong/Nginx Gateway]
        AUTH[Authentication Service]
        RATE_LIMIT[Rate Limiting]
        CACHE[Redis Cache]
    end
    
    subgraph "API Services"
        STOCK_API[Stock API Service]
        ANALYSIS_API[Analysis API Service]
        ALERT_API[Alert API Service]
        NEWS_API[News API Service]
    end
    
    subgraph "Data Layer"
        MONGO[(MongoDB)]
        REDIS[(Redis Cache)]
    end
    
    WEB --> GATEWAY
    MOBILE --> GATEWAY
    API_CLIENT --> GATEWAY
    
    GATEWAY --> AUTH
    GATEWAY --> RATE_LIMIT
    GATEWAY --> CACHE
    
    AUTH --> STOCK_API
    RATE_LIMIT --> ANALYSIS_API
    CACHE --> ALERT_API
    STOCK_API --> NEWS_API
    
    STOCK_API --> MONGO
    ANALYSIS_API --> MONGO
    ALERT_API --> MONGO
    NEWS_API --> MONGO
    
    STOCK_API --> REDIS
    ANALYSIS_API --> REDIS
```

### 6.2 REST API Endpoints

#### **6.2.1 Stock Information APIs**

**Base URL:** `https://api.stockai.vn/v1`

**GET /stocks**
- **Mục đích:** Lấy danh sách tất cả cổ phiếu
- **Query Parameters:**
  - `exchange`: HOSE, HNX, UPCOM
  - `industry`: Ngành (optional)
  - `limit`: Số lượng (default: 20, max: 100)
  - `offset`: Pagination offset
- **Response:**
```json
{
  "success": true,
  "data": [
    {
      "symbol": "VNM",
      "company_name": "Vinamilk",
      "exchange": "HOSE",
      "industry": "Food & Beverage",
      "current_price": 86.0,
      "change_percent": 1.2,
      "market_cap": 85000000000000,
      "last_updated": "2025-12-04T10:45:00Z"
    }
  ],
  "pagination": {
    "total": 1500,
    "limit": 20,
    "offset": 0,
    "has_next": true
  }
}
```

**GET /stocks/{symbol}**
- **Mục đích:** Thông tin chi tiết một cổ phiếu
- **Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "VNM",
    "company_name": "Vinamilk",
    "exchange": "HOSE",
    "industry": "Food & Beverage",
    "current_price": 86.0,
    "price_change": {
      "change": 1.0,
      "change_percent": 1.18,
      "previous_close": 85.0
    },
    "trading_info": {
      "volume": 1250000,
      "value": 107250000000,
      "high": 86.5,
      "low": 85.2,
      "open": 85.5
    },
    "market_info": {
      "market_cap": 85000000000000,
      "outstanding_shares": 1700000000,
      "pe_ratio": 12.5,
      "eps": 6.88
    },
    "last_updated": "2025-12-04T10:45:00Z"
  }
}
```

**GET /stocks/{symbol}/history**
- **Mục đích:** Lịch sử giá cổ phiếu
- **Query Parameters:**
  - `period`: 1d, 1w, 1m, 3m, 6m, 1y, ytd, all
  - `interval`: 1m, 5m, 15m, 1h, 1d
- **Response:** OHLCV data array

#### **6.2.2 AI Analysis APIs**

**GET /stocks/{symbol}/ai-analysis**
- **Mục đích:** Kết quả phân tích AI/ML
- **Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "VNM",
    "analysis_date": "2025-12-04T11:00:00Z",
    "models": {
      "arima": {
        "prediction": [86.2, 86.5, 86.8, 87.0, 87.3],
        "confidence": 0.75
      },
      "lstm": {
        "prediction": [86.1, 86.4, 87.0, 87.2, 87.8],
        "confidence": 0.82
      },
      "transformer": {
        "prediction": [86.0, 86.3, 86.9, 87.1, 87.5],
        "confidence": 0.88
      },
      "catboost": {
        "prediction_class": "BUY",
        "class_probabilities": {
          "SELL": 0.15,
          "HOLD": 0.25,
          "BUY": 0.60
        },
        "confidence": 0.85
      }
    },
    "ensemble": {
      "prediction": [86.1, 86.4, 86.9, 87.1, 87.5],
      "overall_confidence": 0.83
    },
    "scores": {
      "technical_score": 78.5,
      "trend_score": 45.2,
      "risk_score": 35.8,
      "recommendation": "BUY"
    }
  }
}
```

**GET /stocks/{symbol}/llm-analysis**
- **Mục đích:** Kết quả phân tích LLM từ tin tức
- **Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "VNM",
    "analysis_summary": {
      "total_news_analyzed": 4,
      "sentiment_distribution": {
        "positive": 3,
        "negative": 0,
        "neutral": 1
      },
      "overall_sentiment": "positive",
      "overall_confidence": 0.82
    },
    "recent_analyses": [
      {
        "news_title": "VNM công bố kế hoạch tăng vốn điều lệ",
        "sentiment": "positive",
        "impact_score": 75,
        "summary": "Kế hoạch mở rộng tích cực...",
        "published_at": "2025-12-04T08:30:00Z"
      }
    ],
    "key_insights": [
      {
        "insight": "Kế hoạch mở rộng sản xuất tại miền Bắc",
        "importance": "high",
        "category": "operational"
      }
    ]
  }
}
```

**GET /stocks/{symbol}/final-scores**
- **Mục đích:** Điểm số cuối cùng và khuyến nghị
- **Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "VNM",
    "calculation_date": "2025-12-04T11:00:00Z",
    "final_score": 78.5,
    "recommendation": "BUY",
    "confidence": 0.82,
    "breakdown": {
      "technical_score": 75.2,
      "sentiment_score": 85.3,
      "news_impact_score": 68.7,
      "risk_score": 32.1
    },
    "recommendation_details": {
      "action": "BUY",
      "target_price": 92.0,
      "stop_loss": 82.0,
      "time_horizon": "medium_term",
      "risk_level": "moderate"
    }
  }
}
```

#### **6.2.3 Alert APIs**

**GET /alerts**
- **Mục đích:** Danh sách cảnh báo
- **Query Parameters:**
  - `symbol`: Mã cổ phiếu (optional)
  - `severity`: HIGH, MEDIUM, LOW (optional)
  - `status`: ACTIVE, ACKNOWLEDGED, RESOLVED (optional)
  - `limit`, `offset`: Pagination
- **Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "alert_123",
      "symbol": "VNM",
      "type": "RECOMMENDATION_CHANGE",
      "severity": "HIGH",
      "message": "VNM: Khuyến nghị thay đổi từ WATCH thành BUY",
      "triggered_at": "2025-12-04T11:00:00Z",
      "status": "ACTIVE"
    }
  ]
}
```

**POST /alerts/{alert_id}/acknowledge**
- **Mục đích:** Xác nhận đã đọc cảnh báo
- **Response:** Success message

#### **6.2.4 News APIs**

**GET /news**
- **Mục đích:** Tin tức mới nhất
- **Query Parameters:**
  - `symbol`: Mã cổ phiếu (optional)
  - `category`: Loại tin (optional)
  - `limit`: Số lượng
- **Response:**
```json
{
  "success": true,
  "data": [
    {
      "news_id": "news_123",
      "symbol": "VNM",
      "title": "VNM công bố kế hoạch tăng vốn điều lệ",
      "summary": "Tóm tắt ngắn gọn...",
      "published_at": "2025-12-04T08:30:00Z",
      "sentiment": "positive",
      "impact_score": 75,
      "source_url": "https://..."
    }
  ]
}
```

### 6.3 Authentication & Authorization

#### **6.3.1 Authentication Methods**
- **API Key Authentication:** Cho third-party integrations
- **JWT Token:** Cho web/mobile applications
- **OAuth 2.0:** Cho enterprise clients

#### **6.3.2 Rate Limiting**
```yaml
Free Tier:
  - 100 requests/hour
  - Basic endpoints only
  
Premium Tier:
  - 1000 requests/hour
  - All endpoints
  - Real-time alerts

Enterprise Tier:
  - 10000 requests/hour
  - Custom integrations
  - Dedicated support
```

#### **6.3.3 API Security**
- **HTTPS Only:** TLS 1.3 encryption
- **CORS Policy:** Configured allowed origins
- **Input Validation:** JSON schema validation
- **SQL Injection Prevention:** Parameterized queries
- **DDoS Protection:** Rate limiting + CloudFlare

### 6.4 Caching Strategy

#### **6.4.1 Redis Cache Layers**

```mermaid
graph LR
    A[API Request] --> B{Cache Check}
    B -->|Hit| C[Return Cached Data]
    B -->|Miss| D[Query Database]
    D --> E[Cache Result]
    E --> F[Return Data]
    
    subgraph "Cache TTL"
        G[Stock Prices: 5 minutes]
        H[AI Analysis: 1 hour]
        I[News: 15 minutes]
        J[Final Scores: 30 minutes]
    end
```

**Cache Keys Pattern:**
- `stock:price:{symbol}` - TTL: 5 minutes
- `stock:analysis:{symbol}` - TTL: 1 hour  
- `stock:news:{symbol}` - TTL: 15 minutes
- `stock:scores:{symbol}` - TTL: 30 minutes
- `alerts:active` - TTL: 5 minutes

#### **6.4.2 Cache Invalidation**
- **Time-based:** TTL expiration
- **Event-based:** New analysis results trigger cache clear
- **Manual:** Admin cache flush endpoint

---

## 7. Non-functional Requirements

### 7.1 Performance Requirements

#### **7.1.1 Response Time**
- **API Endpoints:**
  - Stock info: < 200ms (95th percentile)
  - AI Analysis: < 500ms (95th percentile)
  - News feed: < 300ms (95th percentile)
  - Search: < 1000ms (95th percentile)

- **Data Processing:**
  - Price data processing: < 10 seconds after collection
  - AI analysis: < 5 minutes after new data
  - LLM analysis: < 2 minutes per news article
  - Final score calculation: < 1 minute after inputs ready

#### **7.1.2 Throughput**
- **API Gateway:** 10,000 requests/second peak
- **Kafka Pipeline:** 100,000 messages/second
- **Database Operations:** 5,000 queries/second

### 7.2 Scalability & Availability

#### **7.2.1 Horizontal Scaling Strategy**

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[NGINX Load Balancer]
    end
    
    subgraph "API Services (Auto-scaling)"
        API1[API Service 1]
        API2[API Service 2]
        API3[API Service N...]
    end
    
    subgraph "Processing Services"
        PROC1[AI Analysis Service 1]
        PROC2[AI Analysis Service 2]
        PROC3[LLM Service 1]
        PROC4[LLM Service 2]
    end
    
    subgraph "Data Layer"
        MONGO[MongoDB Cluster<br/>3 Replicas + Sharding]
        KAFKA[Kafka Cluster<br/>3 Brokers]
        REDIS[Redis Cluster<br/>6 Nodes]
    end
    
    LB --> API1 & API2 & API3
    API1 --> MONGO & REDIS
    PROC1 --> MONGO & KAFKA
```

**Scaling Triggers:**
- **CPU Usage > 70%:** Scale out API services
- **Memory Usage > 80%:** Scale out processing services
- **Queue Length > 1000:** Scale out consumers
- **Response Time > SLA:** Add more replicas

#### **7.2.2 High Availability**
- **Uptime SLA:** 99.9% (8.76 hours downtime/year)
- **Multi-AZ Deployment:** Services distributed across availability zones
- **Database Replication:** MongoDB replica set with 3 nodes
- **Failover:** Automatic failover within 30 seconds
- **Backup Strategy:** Daily full backup + continuous incremental

### 7.3 Security Requirements

#### **7.3.1 Data Protection**
- **Encryption at Rest:** AES-256 for MongoDB and Redis
- **Encryption in Transit:** TLS 1.3 for all communications
- **API Security:** OAuth 2.0, JWT tokens, API key rotation
- **Access Control:** RBAC (Role-Based Access Control)

#### **7.3.2 Compliance & Privacy**
- **Data Retention:** 2 years for historical data, 30 days for logs
- **GDPR Compliance:** Data anonymization, right to be forgotten
- **Audit Logging:** All API access and data modifications logged
- **Vulnerability Management:** Monthly security scans

### 7.4 Monitoring & Observability

#### **7.4.1 Logging Stack (ELK)**

```mermaid
graph LR
    subgraph "Applications"
        APP1[API Services]
        APP2[AI Services]
        APP3[LLM Services]
    end
    
    subgraph "Log Collection"
        BEATS[Filebeat/Metricbeat]
    end
    
    subgraph "ELK Stack"
        LOGSTASH[Logstash]
        ELASTICSEARCH[Elasticsearch]
        KIBANA[Kibana]
    end
    
    APP1 --> BEATS
    APP2 --> BEATS
    APP3 --> BEATS
    BEATS --> LOGSTASH
    LOGSTASH --> ELASTICSEARCH
    ELASTICSEARCH --> KIBANA
```

**Log Levels & Retention:**
- **ERROR:** 90 days retention, immediate alerts
- **WARN:** 30 days retention, daily summary
- **INFO:** 7 days retention, no alerts
- **DEBUG:** 1 day retention (development only)

#### **7.4.2 Metrics & Alerting (Prometheus + Grafana)**

**Key Metrics to Monitor:**
- **Application Metrics:**
  - API response times (percentiles: 50th, 95th, 99th)
  - Request rate (requests/second)
  - Error rate (4xx, 5xx responses)
  - Active connections

- **Infrastructure Metrics:**
  - CPU, Memory, Disk usage
  - Network I/O
  - Database connections
  - Kafka lag

- **Business Metrics:**
  - Number of stocks analyzed/hour
  - AI model accuracy trends
  - Alert generation rate
  - User engagement metrics

**Alerting Rules:**
```yaml
Critical Alerts (PagerDuty):
  - API error rate > 5%
  - Response time > 2000ms
  - Service down > 1 minute
  - Database connection failure

Warning Alerts (Slack):
  - CPU usage > 80%
  - Memory usage > 85%
  - Disk usage > 90%
  - Kafka consumer lag > 1000
```

### 7.5 Data Quality & Reliability

#### **7.5.1 Data Validation**
- **Input Validation:** Schema validation for all incoming data
- **Business Logic Validation:** Price range checks, volume validation
- **Cross-Reference Validation:** Compare multiple data sources
- **Outlier Detection:** Statistical methods to detect anomalies

#### **7.5.2 Error Handling**
- **Retry Logic:** Exponential backoff for transient failures
- **Circuit Breaker:** Prevent cascading failures
- **Graceful Degradation:** Serve cached data when services unavailable
- **Dead Letter Queue:** Handle permanently failed messages

---

## 8. Deployment Plan

### 8.1 Container Architecture

#### **8.1.1 Docker Services Overview**

```mermaid
graph TB
    subgraph "Docker Compose Services"
        subgraph "API Layer"
            API[stock-api<br/>Flask/FastAPI]
            GATEWAY[api-gateway<br/>NGINX]
        end
        
        subgraph "Processing Layer"
            COLLECTOR[data-collector<br/>Python]
            AI_SERVICE[ai-analysis<br/>Python + TensorFlow]
            LLM_SERVICE[llm-analysis<br/>Python + OpenAI]
            AGGREGATOR[score-aggregator<br/>Python]
        end
        
        subgraph "Message Queue"
            KAFKA_SVC[kafka<br/>Confluent Kafka]
            ZOOKEEPER[zookeeper]
        end
        
        subgraph "Databases"
            MONGO_SVC[mongodb<br/>MongoDB 6.0]
            REDIS_SVC[redis<br/>Redis 7.0]
        end
        
        subgraph "Monitoring"
            PROMETHEUS[prometheus]
            GRAFANA[grafana]
            ELASTICSEARCH[elasticsearch]
            KIBANA[kibana]
        end
        
        subgraph "Scheduler"
            AIRFLOW[airflow<br/>Apache Airflow]
        end
    end
    
    API --> MONGO_SVC & REDIS_SVC
    COLLECTOR --> KAFKA_SVC
    AI_SERVICE --> MONGO_SVC & KAFKA_SVC
    LLM_SERVICE --> MONGO_SVC & KAFKA_SVC
    AGGREGATOR --> MONGO_SVC
    KAFKA_SVC --> ZOOKEEPER
```

#### **8.1.2 Docker Compose Structure**

```yaml
# docker-compose.yml (主要服务)
version: '3.8'
services:
  # API Gateway
  api-gateway:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - stock-api
    
  # Main API Service
  stock-api:
    build: ./services/api
    environment:
      - MONGODB_URI=mongodb://mongodb:27017/stockai
      - REDIS_URI=redis://redis:6379
      - KAFKA_URI=kafka:9092
    depends_on:
      - mongodb
      - redis
      - kafka
    
  # Data Collector
  data-collector:
    build: ./services/collector
    environment:
      - VNSTOCK_CONFIG=/app/config/vnstock.yml
      - KAFKA_URI=kafka:9092
    depends_on:
      - kafka
    
  # AI Analysis Service
  ai-analysis:
    build: ./services/ai-analysis
    environment:
      - MONGODB_URI=mongodb://mongodb:27017/stockai
      - MODEL_PATH=/app/models
    volumes:
      - ./models:/app/models
    depends_on:
      - mongodb
    
  # LLM Analysis Service  
  llm-analysis:
    build: ./services/llm-analysis
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MONGODB_URI=mongodb://mongodb:27017/stockai
    depends_on:
      - mongodb
    
  # Score Aggregator
  score-aggregator:
    build: ./services/aggregator
    environment:
      - MONGODB_URI=mongodb://mongodb:27017/stockai
    depends_on:
      - mongodb
      - ai-analysis
      - llm-analysis

  # Infrastructure Services
  mongodb:
    image: mongo:6.0
    volumes:
      - mongodb_data:/data/db
      - ./mongo/mongod.conf:/etc/mongod.conf
    ports:
      - "27017:27017"
    
  redis:
    image: redis:7.0-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      
  kafka:
    image: confluentinc/cp-kafka:latest
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"

  # Airflow for scheduling
  airflow:
    image: apache/airflow:2.7.0
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql://airflow:airflow@postgres:5432/airflow
    volumes:
      - ./airflow/dags:/opt/airflow/dags
    depends_on:
      - postgres
    
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  mongodb_data:
  redis_data:
  postgres_data:
```

### 8.2 Environment Configuration

#### **8.2.1 Environment Variables**

**Production (.env.prod):**
```bash
# Database
MONGODB_URI=mongodb://mongodb-prod:27017/stockai_prod
REDIS_URI=redis://redis-prod:6379/0

# Message Queue
KAFKA_BROKERS=kafka-prod-1:9092,kafka-prod-2:9092,kafka-prod-3:9092

# External APIs
VNSTOCK_API_KEY=your_vnstock_api_key
OPENAI_API_KEY=your_openai_api_key
CLAUDE_API_KEY=your_claude_api_key

# Security
JWT_SECRET_KEY=your_jwt_secret_key_here
API_KEY_SALT=your_api_key_salt_here

# Monitoring
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000

# Logging
LOG_LEVEL=INFO
ELK_HOST=elasticsearch:9200

# Performance
CACHE_TTL_SECONDS=300
MAX_WORKERS=4
BATCH_SIZE=100
```

**Development (.env.dev):**
```bash
# Simplified config for development
MONGODB_URI=mongodb://localhost:27017/stockai_dev
REDIS_URI=redis://localhost:6379/1
KAFKA_BROKERS=localhost:9092

# Debug settings
LOG_LEVEL=DEBUG
CACHE_TTL_SECONDS=60
```

#### **8.2.2 Secrets Management**

**Docker Secrets (Production):**
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  stock-api:
    secrets:
      - mongodb_password
      - jwt_secret
      - openai_api_key
    environment:
      - MONGODB_PASSWORD_FILE=/run/secrets/mongodb_password
      - JWT_SECRET_FILE=/run/secrets/jwt_secret
      - OPENAI_API_KEY_FILE=/run/secrets/openai_api_key

secrets:
  mongodb_password:
    file: ./secrets/mongodb_password.txt
  jwt_secret:
    file: ./secrets/jwt_secret.txt
  openai_api_key:
    file: ./secrets/openai_api_key.txt
```

### 8.3 Deployment Environments

#### **8.3.1 Development Environment**
```bash
# Quick start for development
git clone https://github.com/your-org/stock-ai-backend.git
cd stock-ai-backend

# Setup environment
cp .env.example .env.dev
# Edit .env.dev with your API keys

# Start services
docker-compose -f docker-compose.dev.yml up -d

# Run database migrations
docker-compose exec stock-api python manage.py migrate

# Load sample data
docker-compose exec stock-api python manage.py load_sample_data
```

#### **8.3.2 Staging Environment**
```bash
# Staging deployment (similar to production)
docker-compose -f docker-compose.staging.yml up -d

# Health checks
curl http://staging-api.stockai.vn/health
curl http://staging-api.stockai.vn/v1/stocks/VNM
```

#### **8.3.3 Production Deployment**
```bash
# Production deployment with proper secrets
docker-compose -f docker-compose.prod.yml up -d

# Verify all services are running
docker-compose ps

# Check logs
docker-compose logs -f stock-api
docker-compose logs -f ai-analysis
```

### 8.4 Database Setup & Migration

#### **8.4.1 MongoDB Initialization**
```javascript
// mongo-init.js
db = db.getSiblingDB('stockai');

// Create collections with validation
db.createCollection("stocks", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["symbol", "company_name", "exchange"],
         properties: {
            symbol: { bsonType: "string" },
            company_name: { bsonType: "string" },
            exchange: { enum: ["HOSE", "HNX", "UPCOM"] }
         }
      }
   }
});

// Create indexes
db.stocks.createIndex({ "symbol": 1 }, { unique: true });
db.price_history.createIndex({ "symbol": 1, "timestamp": -1 });
db.news.createIndex({ "news_id": 1 }, { unique: true });
db.ai_analysis.createIndex({ "symbol": 1, "analysis_date": -1 });
db.llm_analysis.createIndex({ "news_id": 1 }, { unique: true });
db.final_scores.createIndex({ "symbol": 1, "calculation_date": -1 });
db.alerts.createIndex({ "symbol": 1, "triggered_at": -1 });

// Create users
db.createUser({
  user: "api_user",
  pwd: "secure_password_here",
  roles: [
    { role: "readWrite", db: "stockai" }
  ]
});
```

#### **8.4.2 Data Migration Scripts**
```bash
# Migration script structure
./scripts/
├── migrate_v1_to_v2.py      # Schema migrations
├── seed_stock_list.py       # Initial stock data
├── backfill_historical.py   # Historical price data
└── setup_indexes.py         # Database indexes
```

### 8.5 Monitoring & Health Checks

#### **8.5.1 Health Check Endpoints**
```yaml
# Health check configuration
/health:
  - Database connectivity: MongoDB, Redis
  - External API status: vnstock, OpenAI
  - Message queue status: Kafka
  - Cache status: Redis cache hit rate
  - Background jobs: AI analysis status

/health/detailed:
  - Service-specific health metrics
  - Dependencies status
  - Performance metrics
  - Resource usage
```

#### **8.5.2 Deployment Verification**
```bash
#!/bin/bash
# deployment-verify.sh

echo "Starting deployment verification..."

# Check core services
curl -f http://localhost/health || exit 1
echo "✓ API health check passed"

# Check database connectivity
curl -f http://localhost/v1/stocks?limit=1 || exit 1
echo "✓ Database connectivity verified"

# Check AI analysis
curl -f http://localhost/v1/stocks/VNM/ai-analysis || exit 1
echo "✓ AI analysis service working"

# Check Kafka connectivity
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092 || exit 1
echo "✓ Kafka connectivity verified"

echo "All deployment checks passed! 🚀"
```

---

## 9. Roadmap phát triển 3 tháng

### 9.1 Tổng quan Timeline

```mermaid
gantt
    title Stock AI Backend Development Roadmap
    dateFormat  YYYY-MM-DD
    section Phase 1
    Data Pipeline Setup       :done, phase1, 2025-12-04, 2025-12-20
    Basic Infrastructure      :done, infra1, 2025-12-04, 2025-12-15
    vnstock Integration       :active, vnstock, 2025-12-10, 2025-12-25
    
    section Phase 2
    AI/ML Development         :ai-dev, 2025-12-20, 2026-01-15
    Model Training            :model, 2025-12-25, 2026-01-20
    Technical Analysis        :tech, 2026-01-01, 2026-01-25
    
    section Phase 3
    LLM Integration          :llm, 2026-01-15, 2026-02-10
    News Analysis Engine     :news, 2026-01-20, 2026-02-15
    Sentiment Analysis       :sentiment, 2026-01-25, 2026-02-15
    
    section Phase 4
    Aggregation Service      :agg, 2026-02-10, 2026-02-28
    API Development          :api, 2026-02-01, 2026-02-25
    Alert System             :alerts, 2026-02-15, 2026-03-05
    
    section Phase 5
    Dashboard Development    :dashboard, 2026-02-20, 2026-03-15
    Testing & Optimization   :testing, 2026-03-01, 2026-03-20
    Production Deployment    :prod, 2026-03-15, 2026-03-31
```

### 9.2 Phase 1: Data Pipeline Foundation (Tháng 1 - Tuần 1-3)

#### **9.2.1 Mục tiêu chính**
- ✅ Thiết lập infrastructure cơ bản
- ✅ Tích hợp vnstock library
- ✅ Xây dựng data pipeline từ vnstock → Kafka → MongoDB
- ✅ Monitoring và logging cơ bản

#### **9.2.2 Deliverables**

**Tuần 1 (04-10/12/2025):**
- [ ] **Docker Environment Setup**
  - Docker compose cho development environment
  - MongoDB, Redis, Kafka containers
  - Basic NGINX reverse proxy
  
- [ ] **Database Schema Design**
  - MongoDB collections: stocks, price_history, news
  - Indexes và validation rules
  - Migration scripts

**Tuần 2 (11-17/12/2025):**
- [ ] **Price Data Collector Service**
  - Integrate vnstock for price data
  - Kafka producer cho stock_prices_raw topic
  - Error handling và retry logic
  - Basic logging
  
- [ ] **News Data Collector Service**
  - Integrate vnstock for news data
  - Kafka producer cho stock_news_raw topic
  - Duplicate detection
  - Content cleaning

**Tuần 3 (18-24/12/2025):**
- [ ] **Consumer Services**
  - Price consumer: Kafka → MongoDB
  - News consumer: Kafka → MongoDB
  - Data validation và quality checks
  
- [ ] **Basic Monitoring**
  - Prometheus metrics collection
  - Grafana dashboards
  - Health check endpoints

#### **9.2.3 Success Criteria**
- ✅ Thu thập được dữ liệu giá cho 100+ cổ phiếu HOSE
- ✅ Thu thập được tin tức hàng ngày (50+ bài/ngày)
- ✅ Data pipeline stable với uptime > 95%
- ✅ Basic monitoring dashboard hoạt động

### 9.3 Phase 2: AI/ML Analysis Engine (Tháng 1 - Tuần 4 đến Tháng 2 - Tuần 3)

#### **9.3.1 Mục tiêu chính**
- 🔄 Xây dựng AI/ML models cho technical analysis
- 🔄 Feature engineering từ price data
- 🔄 Model training và evaluation
- 🔄 Prediction service

#### **9.3.2 Deliverables**

**Tuần 4 (25-31/12/2025):**
- [ ] **Feature Engineering Pipeline**
  - Technical indicators: RSI, MACD, Bollinger Bands
  - Candlestick pattern detection
  - Volume analysis features
  - Rolling statistics

**Tuần 5-6 (01-14/01/2026):**
- [ ] **Model Development**
  - ARIMA model cho short-term prediction
  - LSTM model cho medium-term prediction
  - Transformer model cho pattern recognition
  - CatBoost cho classification

**Tuần 7-8 (15-28/01/2026):**
- [ ] **Model Training & Evaluation**
  - Historical data preparation (2+ years)
  - Backtesting framework
  - Performance metrics calculation
  - Model selection và tuning

**Tuần 9 (29/01-04/02/2026):**
- [ ] **AI Analysis Service**
  - Model serving với FastAPI
  - Batch prediction pipeline
  - Results storage in ai_analysis collection
  - Airflow DAGs cho scheduled analysis

#### **9.3.3 Success Criteria**
- ✅ Models achieve accuracy > 65% cho 5-day predictions
- ✅ Feature pipeline processes 1000+ stocks trong < 10 minutes
- ✅ AI analysis results available for top 100 stocks daily
- ✅ Prediction confidence scores calibrated properly

### 9.4 Phase 3: LLM News Analysis Engine (Tháng 2 - Tuần 2-4)

#### **9.4.1 Mục tiêu chính**
- 🔄 Tích hợp LLM APIs (OpenAI GPT-4, Claude)
- 🔄 Sentiment analysis cho tin tức
- 🔄 Impact assessment và insights extraction
- 🔄 News analysis automation

#### **9.4.2 Deliverables**

**Tuần 6-7 (05-18/02/2026):**
- [ ] **LLM Integration**
  - OpenAI API integration với rate limiting
  - Prompt engineering cho sentiment analysis
  - Prompt engineering cho summary & insights
  - Batch processing capability

**Tuần 8 (19-25/02/2026):**
- [ ] **News Analysis Pipeline**
  - Automated news processing workflow
  - Quality validation cho LLM outputs
  - Results storage in llm_analysis collection
  - Error handling và fallback mechanisms

**Tuần 9 (26/02-04/03/2026):**
- [ ] **Analysis Quality Control**
  - Output validation rules
  - Confidence scoring
  - A/B testing different prompts
  - Performance optimization

#### **9.4.3 Success Criteria**
- ✅ Process 200+ news articles per day
- ✅ Sentiment accuracy > 80% (manual validation)
- ✅ Average processing time < 2 minutes per article
- ✅ LLM API costs under $500/month

### 9.5 Phase 4: Aggregation & API Layer (Tháng 3 - Tuần 1-3)

#### **9.4.1 Mục tiêu chính**
- 🔄 Kết hợp AI/ML và LLM analysis
- 🔄 Final scoring algorithm
- 🔄 REST API development
- 🔄 Alert system

#### **9.5.2 Deliverables**

**Tuần 10 (05-11/03/2026):**
- [ ] **Scoring Service**
  - Score calculation algorithms
  - Weight optimization
  - Risk assessment integration
  - Alert generation logic

**Tuần 11 (12-18/03/2026):**
- [ ] **REST API Development**
  - FastAPI implementation
  - All endpoints từ section 6.2
  - Authentication & authorization
  - Rate limiting & caching

**Tuần 12 (19-25/03/2026):**
- [ ] **Alert System**
  - Real-time alert generation
  - Multiple notification channels
  - Alert management API
  - Dashboard integration

#### **9.5.3 Success Criteria**
- ✅ API response times < 200ms (95th percentile)
- ✅ Final scores available cho 500+ stocks daily
- ✅ Alert system generates relevant notifications
- ✅ API documentation complete với examples

### 9.6 Phase 5: Dashboard & Production (Tháng 3 - Tuần 3-4)

#### **9.6.1 Mục tiêu chính**
- 🔄 Frontend dashboard development
- 🔄 Production deployment
- 🔄 Performance optimization
- 🔄 User acceptance testing

#### **9.6.2 Deliverables**

**Tuần 13 (26/03-01/04/2026):**
- [ ] **Dashboard Frontend**
  - React/Vue.js dashboard
  - Stock analysis views
  - Alert management interface
  - Real-time data updates

**Tuần 14 (02-08/04/2026):**
- [ ] **Production Deployment**
  - Production environment setup
  - CI/CD pipeline
  - Security hardening
  - Performance monitoring

#### **9.6.3 Success Criteria**
- ✅ Complete end-to-end workflow working
- ✅ Production deployment stable
- ✅ User feedback positive (> 4/5 rating)
- ✅ System handles 1000+ concurrent users

### 9.7 Resource Requirements

#### **9.7.1 Team Structure**
```
Backend Engineers (2-3 người):
  - Senior: System architecture, AI/ML models
  - Mid-level: API development, data pipeline
  - Junior: Testing, documentation

DevOps Engineer (1 người):
  - Infrastructure setup
  - CI/CD pipeline
  - Monitoring & alerting

Data Scientist (1 người):
  - Feature engineering
  - Model development
  - Performance analysis

Frontend Developer (1 người):
  - Dashboard development
  - API integration
```

#### **9.7.2 Infrastructure Costs (Monthly)**
```
AWS/GCP Compute:
  - API Services: $200/month
  - AI/ML Processing: $300/month
  - Database (MongoDB): $150/month
  - Cache (Redis): $50/month
  - Message Queue (Kafka): $100/month

External APIs:
  - OpenAI API: $500/month
  - vnstock Premium: $100/month

Monitoring:
  - Datadog/New Relic: $100/month

Total: ~$1,500/month
```

#### **9.7.3 Risk Mitigation**

**Technical Risks:**
- **Model Performance:** Implement ensemble methods, continuous retraining
- **API Rate Limits:** Implement caching, backup providers
- **Data Quality:** Multiple validation layers, manual review process
- **Scalability:** Horizontal scaling design, load testing

**Business Risks:**
- **Market Changes:** Flexible model architecture, rapid retraining capability
- **Competition:** Focus on unique insights, superior user experience
- **Regulatory:** Ensure compliance, legal review

**Operational Risks:**
- **Team Knowledge:** Documentation, knowledge sharing sessions
- **Timeline Delays:** Buffer time, parallel development streams
- **Budget Overrun:** Monthly cost tracking, optimization reviews

---

## Kết luận

Kế hoạch 3 tháng này cung cấp roadmap chi tiết để xây dựng một hệ thống AI gợi ý cổ phiếu hoàn chỉnh với:

- ✅ **Kiến trúc scalable** từ data collection đến user interface
- ✅ **Technology stack hiện đại** (Python, MongoDB, Kafka, Docker, AI/ML, LLM)
- ✅ **Timeline thực tế** với deliverables rõ ràng cho từng tuần
- ✅ **Risk management** và contingency plans
- ✅ **Success criteria** measurable cho từng phase

Hệ thống này sẽ có khả năng phân tích hàng ngàn cổ phiếu Việt Nam, kết hợp AI/ML analysis với natural language processing để cung cấp insights độc đáo và actionable cho nhà đầu tư.