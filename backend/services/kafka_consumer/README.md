# Kafka Consumer Service

## Tổng quan
Service tiêu thụ dữ liệu giá cổ phiếu từ Kafka và lưu vào MongoDB với batch processing và rate limiting.

**Trạng thái**: ✅ **HOÀN THÀNH**

## Kiến trúc
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Kafka Topics   │───►│ Kafka Consumer   │───►│    MongoDB      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ Batch Processor  │
                       │ (Rate Limited)   │
                       └──────────────────┘
```

## Thành phần chính

### 1. MongoDB Adapter
- **Kết nối MongoDB**: Sử dụng URI từ config
- **Batch Upsert**: UpdateOne với upsert=True
- **Unique Key**: Kết hợp `symbol` + `time`
- **Error Handling**: Xử lý lỗi kết nối và bulk write

### 2. Batch Processor
- **Batch Size**: Có thể cấu hình qua `BATCH_SIZE`
- **Timeout Processing**: Force commit sau `BATCH_TIMEOUT` giây
- **Rate Limiting**: Giới hạn `RATE_LIMIT_PER_SECOND`
- **Thread Safety**: Sử dụng locks cho concurrent handling

### 3. Price Validator
- **Field Validation**: Kiểm tra các trường bắt buộc
- **Type Validation**: Validate kiểu dữ liệu
- **Business Logic**: Validate high >= low, volume >= 0
- **Time Format**: Validate ISO format timestamps

### 4. Price Consumer
- **Kafka Integration**: Consume từ `stock_prices_raw` topic
- **Message Processing**: Thêm messages vào batch processor
- **Graceful Shutdown**: Xử lý SIGINT/SIGTERM signals
- **Auto Commit**: Commit offsets tự động

## Cấu hình

### Environment Variables
```bash
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=stock_ai
MONGODB_COLLECTION_PRICES=stock_prices

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_PRICE_TOPIC=stock_prices_raw
KAFKA_GROUP_ID=price_consumer_group

# Batch Processing Configuration
BATCH_SIZE=100
BATCH_TIMEOUT=30

# Rate Limiting Configuration
RATE_LIMIT_PER_SECOND=10.0
```

## Chạy service

### Development
```bash
cd services/kafka_consumer
pip install -r requirements.txt
cp .env.example .env
python -m src.main
```

### Docker
```bash
docker build -t kafka-consumer .
docker run --env-file .env kafka-consumer
```

## Dependencies
- kafka-python==2.0.2
- pymongo==4.6.1
- python-dotenv==1.0.0