# Airflow DAGs for Vietnam Stock AI Backend

This directory contains the Airflow DAGs for orchestrating data collection and analysis workflows.

## DAGs Overview

### 1. Price Collection DAG (`price_collection_dag.py`)

**Schedule**: Every 5 minutes (`*/5 * * * *`)

**Purpose**: Collects stock price data for all active symbols from vnstock and publishes to Kafka.

**Tasks**:
- `collect_prices`: Fetches price data and publishes to `stock_prices_raw` topic

**Configuration**:
- Retries: 2 attempts with 1-minute delay
- Timeout: 10 minutes
- Error handling: Individual symbol failures don't fail the entire task

### 2. News Collection DAG (`news_collection_dag.py`)

**Schedule**: Every 30 minutes (`*/30 * * * *`)

**Purpose**: Collects stock news articles for all active symbols from vnstock and publishes to Kafka.

**Tasks**:
- `collect_news`: Fetches news articles and publishes to `stock_news_raw` topic

**Configuration**:
- Retries: 2 attempts with 2-minute delay
- Timeout: 15 minutes
- Error handling: Individual symbol failures don't fail the entire task

### 3. Analysis Pipeline DAG (`analysis_pipeline_dag.py`)

**Schedule**: Every hour (`@hourly`)

**Purpose**: Runs AI/ML and LLM analysis in parallel, then aggregates results.

**Tasks**:
- `run_ai_ml`: Performs quantitative analysis (trend, risk, technical scores)
- `run_llm`: Performs qualitative analysis (sentiment, summaries)
- `aggregate_results`: Combines both analyses and generates recommendations

**Task Dependencies**:
```
run_ai_ml ──┐
            ├──> aggregate_results
run_llm ────┘
```

**Configuration**:
- Retries: 1 attempt with 5-minute delay
- Timeout: 30 minutes per task
- Trigger rule: Aggregation only runs if BOTH analyses succeed

## Setup Instructions

### 1. Install Airflow

```bash
pip install apache-airflow==2.7.3
```

### 2. Initialize Airflow (Standalone Mode)

```bash
export AIRFLOW_HOME=~/airflow
airflow standalone
```

This will:
- Create the Airflow database (SQLite)
- Start the web server (port 8080)
- Start the scheduler
- Create an admin user

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=vietnam_stock_ai

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_PRICE_TOPIC=stock_prices_raw
KAFKA_NEWS_TOPIC=stock_news_raw

# LLM Configuration (optional)
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Aggregation Weights
WEIGHT_TECHNICAL=0.4
WEIGHT_RISK=0.3
WEIGHT_SENTIMENT=0.3
```

### 4. Copy DAGs to Airflow

```bash
# Option 1: Symlink (recommended for development)
ln -s $(pwd)/dags $AIRFLOW_HOME/dags

# Option 2: Copy files
cp dags/*.py $AIRFLOW_HOME/dags/
```

### 5. Access Airflow Web UI

1. Open browser to http://localhost:8080
2. Login with credentials from `airflow standalone` output
3. Enable the DAGs you want to run

## Monitoring and Logs

### View DAG Status

```bash
# List all DAGs
airflow dags list

# Show DAG details
airflow dags show price_collection
airflow dags show news_collection
airflow dags show analysis_pipeline
```

### View Task Logs

```bash
# View logs for a specific task run
airflow tasks logs price_collection collect_prices 2024-01-15T10:00:00+00:00

# View logs in web UI
# Navigate to DAG > Task > Logs
```

### Trigger Manual Run

```bash
# Trigger a DAG manually
airflow dags trigger price_collection
airflow dags trigger news_collection
airflow dags trigger analysis_pipeline
```

## Testing

### Run DAG Validation Tests

```bash
# Test DAG parsing and structure
python -m pytest tests/test_dags_integration.py -v

# Test property-based tests
python -m pytest tests/test_analysis_pipeline_dag_properties.py -v
```

### Test Individual DAG Functions

```bash
# Test price collection function
python -c "from dags.price_collection_dag import collect_price_data; collect_price_data()"

# Test news collection function
python -c "from dags.news_collection_dag import collect_news_data; collect_news_data()"

# Test AI/ML analysis function
python -c "from dags.analysis_pipeline_dag import run_ai_ml_analysis; run_ai_ml_analysis()"
```

## Troubleshooting

### DAG Not Appearing in UI

1. Check for import errors:
   ```bash
   airflow dags list-import-errors
   ```

2. Verify DAG file is in correct location:
   ```bash
   ls $AIRFLOW_HOME/dags/
   ```

3. Check Airflow logs:
   ```bash
   tail -f $AIRFLOW_HOME/logs/scheduler/latest/*.log
   ```

### Task Failures

1. Check task logs in web UI or CLI
2. Verify MongoDB and Kafka are running
3. Check environment variables are set correctly
4. Verify vnstock API is accessible

### Connection Issues

1. Test MongoDB connection:
   ```bash
   python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017'); print(client.server_info())"
   ```

2. Test Kafka connection:
   ```bash
   python -c "from kafka import KafkaProducer; producer = KafkaProducer(bootstrap_servers='localhost:9092'); print('Connected')"
   ```

## Architecture Notes

### Standalone Mode vs Production

This setup uses Airflow Standalone mode with SQLite, which is suitable for:
- Personal projects
- Development environments
- Single-machine deployments

For production, consider:
- Using PostgreSQL instead of SQLite
- Running Airflow with Celery Executor for distributed task execution
- Setting up proper monitoring and alerting
- Using Docker Compose for service orchestration

### Data Flow

```
Price Collector ──> Kafka (stock_prices_raw) ──> Consumer ──> MongoDB (price_history)
                                                                    │
                                                                    ▼
News Collector ──> Kafka (stock_news_raw) ──> Consumer ──> MongoDB (news)
                                                                    │
                                                                    ▼
                                                            AI/ML Engine ──┐
                                                                           ├──> Aggregation ──> MongoDB (final_scores)
                                                            LLM Engine ────┘
```

### Scheduling Strategy

- **Price Collection (5 min)**: Frequent updates for real-time price tracking
- **News Collection (30 min)**: Less frequent as news doesn't change as rapidly
- **Analysis Pipeline (1 hour)**: Balanced frequency for analysis without overloading

## Best Practices

1. **Monitor DAG Performance**: Check execution times and adjust schedules if needed
2. **Handle Failures Gracefully**: Individual symbol failures shouldn't fail entire tasks
3. **Use Appropriate Timeouts**: Prevent tasks from hanging indefinitely
4. **Log Important Events**: Use structured logging for debugging
5. **Test Before Deploying**: Run integration tests before enabling DAGs

## Additional Resources

- [Airflow Documentation](https://airflow.apache.org/docs/)
- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [DAG Writing Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html#writing-a-dag)
