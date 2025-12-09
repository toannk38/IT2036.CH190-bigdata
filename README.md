# Vietnam Stock AI Backend

Hệ thống Backend AI Cổ phiếu Việt Nam - A data-driven stock analysis platform using AI/ML and LLM for Vietnamese stock market.

## Project Structure

```
.
├── dags/                   # Airflow DAGs
├── docker/                 # Dockerfiles for services
│   ├── Dockerfile.airflow
│   ├── Dockerfile.api
│   └── Dockerfile.consumer
├── scripts/                # Initialization scripts
│   ├── init-mongo.js
│   ├── load_symbols.py
│   └── create_kafka_topics.sh
├── src/                    # Source code
│   ├── collectors/         # Data collectors (price, news)
│   ├── consumers/          # Kafka consumers
│   ├── engines/            # Analysis engines (AI/ML, LLM)
│   └── services/           # API and aggregation services
├── tests/                  # Test suite
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
└── .env.template          # Environment variables template

```

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- At least 8GB RAM for running all services

## Quick Start

### 1. Setup Environment

Copy the environment template and configure your settings:

```bash
cp .env.template .env
# Edit .env with your configuration (API keys, etc.)
```

### 2. Start Services

Start all services using Docker Compose:

```bash
docker-compose up -d
```

This will start:
- **Zookeeper** (port 2181)
- **Kafka** (port 9092)
- **MongoDB** (port 27017)
- **Airflow** (port 8080)
- **Kafka Consumer** (background service)
- **API Service** (port 8000)

### 3. Initialize Kafka Topics

Create the required Kafka topics:

```bash
chmod +x scripts/create_kafka_topics.sh
./scripts/create_kafka_topics.sh
```

### 4. Load Stock Symbols

Load stock symbols from a JSON file:

```bash
python scripts/load_symbols.py data/symbols.json
```

### 5. Access Services

- **Airflow UI**: http://localhost:8080 (username: admin, password: admin)
- **API Documentation**: http://localhost:8000/docs
- **MongoDB**: mongodb://localhost:27017

## Development

### Install Dependencies

#### Using Conda (Recommended)

```bash
# Activate your conda environment
conda activate stock

# Install dependencies
pip install -r requirements.txt
```

#### Using pip with virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run Tests

```bash
pytest tests/
```

### Run Property-Based Tests

```bash
pytest tests/ -k "property"
```

## Architecture

The system uses a microservices architecture with:

1. **Data Collection Layer**: Collects price (every 5 min) and news (every 30 min)
2. **Message Streaming**: Kafka for data pipeline
3. **Storage**: MongoDB for all data
4. **Analysis Layer**: AI/ML and LLM engines (runs hourly)
5. **Aggregation**: Combines analysis results
6. **API Layer**: REST API for clients
7. **Orchestration**: Airflow for workflow management

## Airflow DAGs

- **price_collection**: Runs every 5 minutes
- **news_collection**: Runs every 30 minutes
- **analysis_pipeline**: Runs every hour (AI/ML → LLM → Aggregation)

## Configuration

Key environment variables in `.env`:

- `MONGODB_URI`: MongoDB connection string
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker address
- `OPENAI_API_KEY`: OpenAI API key for LLM
- `WEIGHT_TECHNICAL`, `WEIGHT_RISK`, `WEIGHT_SENTIMENT`: Aggregation weights
- `ALERT_BUY_THRESHOLD`, `ALERT_WATCH_THRESHOLD`: Alert thresholds

## Monitoring

- View Airflow task execution: http://localhost:8080
- Check Kafka topics: `docker exec kafka kafka-topics --list --bootstrap-server localhost:9092`
- MongoDB data: Use MongoDB Compass or mongosh

## Troubleshooting

### Services not starting

Check logs:
```bash
docker-compose logs -f [service_name]
```

### Kafka connection issues

Ensure Kafka is healthy:
```bash
docker exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092
```

### MongoDB connection issues

Check MongoDB status:
```bash
docker exec mongodb mongosh --eval "db.adminCommand('ping')"
```

## License

Private project for personal use.
