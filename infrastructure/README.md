# Stock AI Infrastructure

Hệ thống infrastructure cho dự án Stock AI sử dụng Docker Compose để quản lý các thành phần sau:

## 🏗️ Kiến trúc hệ thống

### Database Layer
- **MongoDB**: Lưu trữ dữ liệu chính (stocks, price_history, news, analysis)
- **Redis**: Caching và session storage

### Message Queue
- **Apache Kafka**: Message streaming cho data pipeline
- **Zookeeper**: Kafka cluster coordination
- **Kafka UI**: Web interface quản lý Kafka

### Monitoring & Observability
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization và dashboards
- **Elasticsearch**: Log storage
- **Logstash**: Log processing
- **Kibana**: Log analysis và visualization

### API Gateway & Load Balancer
- **Nginx**: Reverse proxy, load balancer và SSL termination

### System Monitoring
- **Node Exporter**: System metrics
- **cAdvisor**: Container metrics

## 📁 Cấu trúc thư mục

```
infrastructure/
├── configs/                    # Configuration files
│   ├── mongodb/               # MongoDB init scripts
│   ├── nginx/                 # Nginx configuration
│   ├── prometheus/            # Prometheus config và alert rules
│   ├── grafana/               # Grafana provisioning
│   ├── logstash/              # Logstash pipeline
│   └── kibana/                # Kibana configuration
├── docker_volumes/            # Persistent data volumes
│   ├── mongodb/               # MongoDB data
│   ├── redis/                 # Redis data
│   ├── kafka/                 # Kafka data
│   ├── zookeeper/             # Zookeeper data
│   ├── elasticsearch/         # Elasticsearch data
│   ├── prometheus/            # Prometheus data
│   ├── grafana/               # Grafana data
│   └── nginx/logs/            # Nginx logs
├── docker_backups/            # Local backup storage
├── scripts/                   # Management scripts
│   ├── manage.sh              # Main infrastructure management
│   └── backup.sh              # Backup management
├── docker-compose.yml         # Main compose file
├── docker-compose.dev.yml     # Development overrides
├── docker-compose.prod.yml    # Production overrides
└── .env                       # Environment variables
```

## 🚀 Khởi động nhanh

### 1. Chuẩn bị môi trường

```bash
# Clone repository
cd /path/to/bigdata/infrastructure

# Copy và cấu hình environment variables
cp .env.example .env
nano .env  # Cấu hình các biến môi trường

# Tạo các thư mục cần thiết
mkdir -p docker_volumes/{mongodb,redis,kafka,zookeeper,elasticsearch,prometheus,grafana,nginx/logs}
mkdir -p docker_backups

# Set permissions
sudo chown -R $USER:$USER docker_volumes/
chmod 755 docker_volumes/*
```

### 2. Khởi động infrastructure

```bash
# Development environment
./scripts/manage.sh start development

# Production environment
./scripts/manage.sh start production

# Hoặc sử dụng docker-compose trực tiếp
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### 3. Kiểm tra trạng thái

```bash
# Xem trạng thái services
./scripts/manage.sh status

# Xem logs
./scripts/manage.sh logs

# Xem logs của service cụ thể
./scripts/manage.sh logs mongodb
```

## 🔧 Quản lý hệ thống

### Các lệnh chính

```bash
# Khởi động
./scripts/manage.sh start [development|production]

# Dừng
./scripts/manage.sh stop

# Khởi động lại
./scripts/manage.sh restart [development|production]

# Xem trạng thái
./scripts/manage.sh status

# Xem logs
./scripts/manage.sh logs [service_name]

# Backup dữ liệu
./scripts/manage.sh backup

# Cleanup (XÓA TẤT CẢ DỮ LIỆU)
./scripts/manage.sh clean

# Xem help
./scripts/manage.sh help
```

### Quản lý Backup

```bash
# Tạo backup
./scripts/backup.sh backup

# Xem danh sách backup
./scripts/backup.sh list

# Restore từ backup
./scripts/backup.sh restore /path/to/backup.tar.gz

# Cleanup old backups
./scripts/backup.sh cleanup
```

## 🌐 Access URLs

Khi hệ thống đang chạy, bạn có thể truy cập:

| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana | http://localhost:3000 | admin/StockAI@Grafana2024 |
| Prometheus | http://localhost:9090 | - |
| Kibana | http://localhost:5601 | - |
| Kafka UI | http://localhost:8080 | - |
| Elasticsearch | http://localhost:9200 | - |
| MongoDB | mongodb://localhost:27017 | admin/StockAI@MongoDB2024 |
| Redis | redis://localhost:6379 | StockAI@Redis2024 |

## 📊 Kafka Topics

Hệ thống tự động tạo các Kafka topics sau:

| Topic | Partitions | Description |
|-------|------------|-------------|
| stock_prices_raw | 3 | Raw stock price data |
| stock_news_raw | 3 | Raw stock news data |
| ai_analysis_results | 2 | AI/ML analysis results |
| llm_analysis_results | 2 | LLM analysis results |
| stock_alerts | 2 | Generated stock alerts |

## 🗄️ MongoDB Collections

Các collections được tự động tạo với schema validation:

- `stocks` - Company metadata
- `price_history` - Historical price data
- `news` - News articles
- `ai_analysis` - AI/ML analysis results
- `llm_analysis` - LLM analysis results
- `final_scores` - Aggregated scores
- `alerts` - Generated alerts

## 📈 Monitoring

### Prometheus Metrics

- System metrics (CPU, Memory, Disk, Network)
- Container metrics (Docker containers)
- Application metrics (sẽ được thêm khi implement services)
- Database metrics
- Kafka metrics

### Grafana Dashboards

- System Overview
- Application Performance
- Database Performance
- Kafka Monitoring
- Alert Management

### ELK Stack

- Centralized logging
- Log analysis và search
- Error tracking
- Performance monitoring

## 🔒 Security

### Development Environment

- Basic authentication cho các services
- CORS enabled cho development
- Debug logs enabled
- All ports exposed

### Production Environment

- Strong passwords
- SSL/TLS encryption (cần cấu hình certificates)
- Network isolation
- Resource limits
- Security headers
- Rate limiting

## 🔧 Cấu hình

### Environment Variables

Xem file `.env` để biết tất cả các biến môi trường có thể cấu hình.

Các biến quan trọng:

```bash
# Environment
ENVIRONMENT=development|production

# Database
MONGODB_ROOT_PASSWORD=your_strong_password
REDIS_PASSWORD=your_redis_password

# API Keys (cần thiết cho LLM services)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Resource Limits
MONGODB_MEMORY_LIMIT=2g
KAFKA_MEMORY_LIMIT=2g
ELASTICSEARCH_MEMORY_LIMIT=2g
```

### Resource Requirements

#### Minimum (Development)
- RAM: 8GB
- CPU: 4 cores
- Disk: 50GB free space

#### Recommended (Production)
- RAM: 16GB
- CPU: 8 cores
- Disk: 200GB+ free space (SSD preferred)

## 🚨 Troubleshooting

### Common Issues

1. **Services không start được**
   ```bash
   # Kiểm tra logs
   docker-compose logs [service_name]
   
   # Kiểm tra resource usage
   docker stats
   
   # Restart specific service
   docker-compose restart [service_name]
   ```

2. **Out of memory errors**
   ```bash
   # Giảm memory limits trong .env
   ELASTICSEARCH_HEAP_SIZE=512m
   KAFKA_HEAP_SIZE=512m
   ```

3. **Port conflicts**
   ```bash
   # Kiểm tra ports đang sử dụng
   netstat -tulpn | grep LISTEN
   
   # Thay đổi ports trong docker-compose files
   ```

4. **Permission issues**
   ```bash
   # Fix permissions
   sudo chown -R $USER:$USER docker_volumes/
   chmod -R 755 docker_volumes/
   ```

### Health Checks

```bash
# Kiểm tra tất cả services
./scripts/manage.sh status

# Test MongoDB connection
docker-compose exec mongodb mongosh --eval "db.runCommand('ping')"

# Test Redis connection
docker-compose exec redis redis-cli -a $REDIS_PASSWORD ping

# Test Kafka
docker-compose exec kafka kafka-topics.sh --bootstrap-server localhost:9093 --list

# Test Elasticsearch
curl -X GET "localhost:9200/_cluster/health"
```

## 📝 Logs

### Xem logs

```bash
# Tất cả services
docker-compose logs -f

# Service cụ thể
docker-compose logs -f mongodb

# Recent logs only
docker-compose logs --tail=100 -f
```

### Log locations

- Container logs: `docker-compose logs`
- Nginx logs: `docker_volumes/nginx/logs/`
- ELK Stack: Kibana interface
- Application logs: Sẽ được gửi đến Logstash

## 🔄 Backup & Restore

### Automated Backups

Backup được scheduled để chạy hàng ngày lúc 2:00 AM (cấu hình trong cron).

### Manual Backup

```bash
# Full backup
./scripts/backup.sh backup

# Backup được lưu tại: docker_backups/stock_ai_backup_YYYYMMDD_HHMMSS.tar.gz
```

### Restore

```bash
# List available backups
./scripts/backup.sh list

# Restore from specific backup
./scripts/backup.sh restore docker_backups/stock_ai_backup_20241204_020000.tar.gz
```

## 🎯 Next Steps

1. **Implement Application Services**: Data collector, AI analysis, API services
2. **Setup SSL Certificates**: For production deployment
3. **Configure Alerting**: Email/Slack notifications
4. **Add More Dashboards**: Business metrics dashboards
5. **Setup CI/CD**: Automated deployment pipeline
6. **Load Testing**: Performance testing và optimization

## 📞 Support

Để được hỗ trợ, vui lòng:

1. Kiểm tra logs: `./scripts/manage.sh logs`
2. Kiểm tra status: `./scripts/manage.sh status`
3. Xem troubleshooting section
4. Tạo GitHub issue với logs và error messages

---

**Note**: Đây là infrastructure layer. Application services (data-collector, ai-analysis, api, etc.) sẽ được implement và thêm vào sau.