# Price Data Collector Service

Collects stock price data from vnstock and sends to Kafka.

## Features

- ✅ Collects price history for all Vietnamese stocks
- ✅ Validates data before sending
- ✅ Sends to Kafka topic `stock_prices_raw`
- ✅ Configurable collection interval
- ✅ Error handling and logging

## Running

From `/home/toannk/Desktop/project/bigdata/backend`:

```bash
# Run service
python -m services.data_collector.src.main

# Run tests
pytest tests/services/data_collector/ -v
```

## Configuration

Environment variables (see `.env.example`):
- `VNSTOCK_SOURCE`: Data source (default: VCI)
- `VNSTOCK_RATE_LIMIT`: Rate limit in seconds (default: 0.5)
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka servers (default: localhost:9092)
- `KAFKA_PRICE_TOPIC`: Kafka topic (default: stock_prices_raw)
- `COLLECTION_INTERVAL`: Collection interval in seconds (default: 300)
- `PRICE_HISTORY_DAYS`: Days of history to collect (default: 1)
- `PRICE_INTERVAL`: Price interval (default: 1D)

## Architecture

```
PriceCollector
  ├── VnstockClient (libs/vnstock)
  ├── DataValidator
  ├── DataNormalizer
  └── KafkaProducer
```
