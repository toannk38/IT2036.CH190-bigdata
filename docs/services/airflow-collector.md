# Airflow Collector Service Documentation

## Overview

The Airflow Collector Service orchestrates automated data collection for the Vietnam Stock AI system. It manages scheduled workflows (DAGs) that collect stock prices and news articles from external sources, ensuring reliable and timely data ingestion into the system.

## Architecture

### Technology Stack
- **Orchestrator**: Apache Airflow
- **Language**: Python
- **Scheduler**: Cron-based scheduling
- **Data Sources**: vnstock API
- **Message Queue**: Kafka
- **Database**: MongoDB (for metadata)

### Service Responsibilities
- Schedule and execute data collection workflows
- Manage task dependencies and retry logic
- Monitor data collection success/failure rates
- Handle error recovery and alerting
- Coordinate between data sources and Kafka topics

## DAGs (Directed Acyclic Graphs)

### Price Collection DAG
**File**: `dags/price_collection_dag.py`
**DAG ID**: `price_collection`
**Schedule**: Every 5 minutes (`*/5 * * * *`)

**Purpose**: Collect real-time stock price data for all active symbols

**Workflow**:
```
Start → Get Active Symbols → Fetch Price Data → Publish to Kafka → End
```

**Configuration**:
```python
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
    'execution_timeout': timedelta(minutes=10),
}
```

**Task Details**:
- **Task ID**: `collect_prices`
- **Operator**: `PythonOperator`
- **Function**: `collect_price_data()`
- **Timeout**: 10 minutes
- **Retries**: 2 attempts with 1-minute delay

### News Collection DAG
**File**: `dags/news_collection_dag.py`
**DAG ID**: `news_collection`
**Schedule**: Every 30 minutes (`*/30 * * * *`)

**Purpose**: Collect stock-related news articles and sentiment data

**Workflow**:
```
Start → Get Active Symbols → Fetch News Articles → Publish to Kafka → End
```

**Configuration**:
```python
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
    'execution_timeout': timedelta(minutes=15),
}
```

**Task Details**:
- **Task ID**: `collect_news`
- **Operator**: `PythonOperator`
- **Function**: `collect_news_data()`
- **Timeout**: 15 minutes
- **Retries**: 2 attempts with 2-minute delay

### Analysis Pipeline DAG
**File**: `dags/analysis_pipeline_dag.py`
**DAG ID**: `analysis_pipeline`
**Schedule**: Every hour (`0 * * * *`)

**Purpose**: Process collected data through AI/ML and LLM analysis engines

**Workflow**:
```
Start → AI Analysis → LLM Analysis → Score Calculation → Store Results → End
```

## Data Collectors

### Price Collector
**Location**: `src/collectors/price_collector.py`
**Class**: `PriceCollector`

**Functionality**:
- Connects to vnstock API for price data
- Fetches OHLCV data for active symbols
- Publishes structured data to Kafka topic `stock_prices_raw`
- Handles individual symbol failures gracefully

**Data Structure**:
```python
@dataclass
class PriceData:
    symbol: str
    timestamp: float  # Epoch timestamp
    open: float
    close: float
    high: float
    low: float
    volume: int
```

**Error Handling**:
- Individual symbol failures don't stop entire collection
- Comprehensive logging for debugging
- Retry logic for transient failures
- Graceful degradation when API is unavailable

### News Collector
**Location**: `src/collectors/news_collector.py`
**Class**: `NewsCollector`

**Functionality**:
- Fetches news articles from vnstock news API
- Extracts article metadata and content
- Publishes to Kafka topic `stock_news_raw`
- Handles duplicate article detection

**Data Structure**:
```python
@dataclass
class NewsData:
    symbol: str
    title: str
    content: str
    source: str
    published_at: float  # Epoch timestamp
    collected_at: float  # Epoch timestamp
```

## Task Implementation

### Price Collection Task
```python
def collect_price_data():
    """
    Main task function for price data collection.
    Called by Airflow PythonOperator.
    """
    # Initialize connections
    mongo_client = MongoClient(config.MONGODB_URI)
    kafka_producer = KafkaProducer(
        bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS.split(','),
        value_serializer=lambda v: v
    )
    
    # Initialize services
    symbol_manager = SymbolManager(mongo_client, config.MONGODB_DATABASE)
    price_collector = PriceCollector(kafka_producer, symbol_manager)
    
    # Execute collection
    result = price_collector.collect()
    
    # Handle results
    if result.total_symbols > 0 and result.success_count == 0:
        raise Exception("All price data collections failed")
    
    return {
        'success_count': result.success_count,
        'failure_count': result.failure_count,
        'total_symbols': result.total_symbols
    }
```

### Error Handling Strategy
1. **Connection Errors**: Retry with exponential backoff
2. **API Rate Limits**: Implement delays between requests
3. **Data Validation**: Skip invalid data, log errors
4. **Kafka Failures**: Retry publishing with timeout
5. **Complete Failures**: Fail task only if all symbols fail

## Scheduling and Execution

### Schedule Intervals
- **Price Collection**: `*/5 * * * *` (every 5 minutes)
- **News Collection**: `*/30 * * * *` (every 30 minutes)
- **Analysis Pipeline**: `0 * * * *` (every hour)

### Execution Windows
- **Price Collection**: 5-minute windows, 10-minute timeout
- **News Collection**: 30-minute windows, 15-minute timeout
- **Analysis Pipeline**: 1-hour windows, 30-minute timeout

### Catchup Behavior
```python
# Disabled catchup to prevent backfill of missed runs
catchup=False
```

## Configuration

### Airflow Configuration
```python
# airflow.cfg settings
[core]
dags_folder = /opt/airflow/dags
executor = LocalExecutor
sql_alchemy_conn = postgresql://airflow:airflow@postgres:5432/airflow

[scheduler]
dag_dir_list_interval = 300
catchup_by_default = False
max_active_runs_per_dag = 1
```

### Environment Variables
```bash
# Airflow Core
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql://airflow:airflow@postgres:5432/airflow
AIRFLOW__CORE__FERNET_KEY=your_fernet_key_here

# Database Connections
MONGODB_URI=mongodb://mongodb:27017
MONGODB_DATABASE=vietnam_stock_ai

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=kafka:29092

# Data Source APIs
VNSTOCK_API_TIMEOUT=30
VNSTOCK_RATE_LIMIT_DELAY=1
```

### Docker Configuration
```yaml
# docker-compose.yml for Airflow
airflow-webserver:
  image: apache/airflow:2.7.0
  environment:
    - AIRFLOW__CORE__EXECUTOR=LocalExecutor
    - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql://airflow:airflow@postgres:5432/airflow
  volumes:
    - ./dags:/opt/airflow/dags
    - ./src:/opt/airflow/src
  ports:
    - "8080:8080"
  depends_on:
    - postgres
    - kafka
    - mongodb
```

## Monitoring and Observability

### Airflow Web UI
**URL**: `http://localhost:8080`
**Features**:
- DAG status and execution history
- Task logs and error details
- Performance metrics and timing
- Manual trigger capabilities

### Key Metrics
- **Success Rate**: Percentage of successful task executions
- **Execution Time**: Average task duration
- **Data Volume**: Number of symbols/articles processed
- **Error Rate**: Failed tasks per time period

### Logging Strategy
```python
# Structured logging in tasks
logger.info(
    "Price data collection completed",
    context={
        'success_count': result.success_count,
        'failure_count': result.failure_count,
        'total_symbols': result.total_symbols,
        'failed_symbols': result.failed_symbols
    }
)
```

### Alerting
- **Task Failures**: Email notifications (configurable)
- **Data Quality Issues**: Custom alerts for data anomalies
- **System Health**: Monitor resource usage and performance

## Data Quality and Validation

### Input Validation
```python
# Symbol validation
def validate_symbol(symbol: str) -> bool:
    return bool(symbol and len(symbol) <= 10 and symbol.isalnum())

# Price data validation
def validate_price_data(data: PriceData) -> bool:
    return all([
        data.open > 0,
        data.close > 0,
        data.high >= max(data.open, data.close),
        data.low <= min(data.open, data.close),
        data.volume >= 0
    ])
```

### Data Quality Checks
- **Completeness**: Verify all active symbols processed
- **Accuracy**: Validate price ranges and volume
- **Timeliness**: Check data freshness and collection delays
- **Consistency**: Compare with previous data points

### Failure Recovery
```python
# Graceful failure handling
try:
    price_data = fetch_price_data(symbol)
    if validate_price_data(price_data):
        publish_to_kafka(price_data)
        success_count += 1
    else:
        log_validation_error(symbol, price_data)
        failure_count += 1
except Exception as e:
    log_collection_error(symbol, e)
    failure_count += 1
```

## Performance Optimization

### Parallel Processing
```python
# Process symbols in batches
from concurrent.futures import ThreadPoolExecutor

def collect_batch(symbols_batch):
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(collect_symbol, symbol) for symbol in symbols_batch]
        results = [future.result() for future in futures]
    return results
```

### Resource Management
- **Memory**: Limit batch sizes to prevent OOM
- **Network**: Implement connection pooling
- **CPU**: Balance parallelism with system resources
- **Storage**: Manage temporary data and logs

### Caching Strategy
- **Symbol Lists**: Cache active symbols between runs
- **API Responses**: Cache recent data to reduce API calls
- **Configuration**: Cache database connections

## Deployment

### Local Development
```bash
# Initialize Airflow database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com

# Start scheduler and webserver
airflow scheduler &
airflow webserver --port 8080
```

### Docker Deployment
```bash
# Start Airflow services
docker-compose up -d airflow-webserver airflow-scheduler

# Check service status
docker-compose ps
docker logs airflow-webserver
```

### Production Considerations
- **Executor**: Use CeleryExecutor for scalability
- **Database**: PostgreSQL for metadata storage
- **Security**: Configure authentication and authorization
- **Monitoring**: Integrate with monitoring systems
- **Backup**: Regular backup of Airflow metadata

## Troubleshooting

### Common Issues

**1. DAG Import Errors**
```bash
# Check DAG syntax
python -m py_compile dags/price_collection_dag.py

# View import errors in UI
# Navigate to Admin > Import Errors in Airflow UI
```

**2. Task Failures**
```bash
# View task logs
docker logs airflow-scheduler
# Or check logs in Airflow UI: Graph View > Task > Logs
```

**3. Connection Issues**
```bash
# Test MongoDB connection
docker exec airflow-webserver python -c "
from pymongo import MongoClient
client = MongoClient('mongodb://mongodb:27017')
print(client.admin.command('ping'))
"

# Test Kafka connection
docker exec airflow-webserver python -c "
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers=['kafka:29092'])
print('Kafka connection successful')
"
```

**4. Performance Issues**
- Monitor task execution times in Airflow UI
- Check resource usage: `docker stats`
- Review database query performance
- Optimize batch sizes and parallelism

### Debug Mode
```bash
# Run task manually for debugging
docker exec airflow-webserver airflow tasks run price_collection collect_prices 2024-01-01

# Enable debug logging
export AIRFLOW__LOGGING__LOGGING_LEVEL=DEBUG
```

### Log Analysis
```bash
# View scheduler logs
docker logs airflow-scheduler | grep ERROR

# View task-specific logs
docker exec airflow-webserver find /opt/airflow/logs -name "*.log" -exec grep -l "ERROR" {} \;
```

## Best Practices

### DAG Design
- Keep tasks idempotent
- Use appropriate retry strategies
- Implement proper error handling
- Document task purposes and dependencies

### Resource Management
- Set appropriate timeouts
- Limit concurrent task execution
- Monitor memory and CPU usage
- Implement graceful shutdowns

### Data Handling
- Validate data before processing
- Handle missing or invalid data gracefully
- Implement data quality checks
- Log data processing statistics

### Security
- Use secure connections to external services
- Implement proper authentication
- Limit access to sensitive operations
- Regular security updates and patches