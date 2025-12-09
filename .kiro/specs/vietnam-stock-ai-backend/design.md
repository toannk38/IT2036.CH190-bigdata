# Design Document

## Overview

Hệ thống Backend AI Cổ phiếu Việt Nam được thiết kế đơn giản cho dự án cá nhân, sử dụng Apache Kafka làm message broker và Apache Airflow Standalone làm workflow orchestrator. Hệ thống bao gồm các thành phần chính:

1. **Data Collection Layer**: Thu thập dữ liệu giá (5 phút) và tin tức (30 phút) từ thị trường Việt Nam
2. **Message Streaming Layer**: Kafka topics để truyền tải dữ liệu
3. **Storage Layer**: MongoDB để lưu trữ dữ liệu thô và kết quả phân tích
4. **Analysis Layer**: AI/ML Engine và LLM Engine để phân tích dữ liệu (chạy mỗi giờ)
5. **Aggregation Layer**: Tổng hợp kết quả và tạo recommendations
6. **API Layer**: REST API để phục vụ client applications
7. **Orchestration Layer**: Apache Airflow Standalone (SQLite) để quản lý 3 DAGs độc lập

**Đơn giản hóa cho dự án cá nhân**:
- Airflow chạy standalone mode với SQLite (không cần Postgres)
- 3 DAGs riêng biệt: Price Collection (5 phút), News Collection (30 phút), Analysis Pipeline (1 giờ)
- Loại bỏ các thành phần phức tạp: monitoring, secrets management, load balancing
- Tập trung vào core functionality: thu thập, phân tích, và API

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Apache Airflow                            │
│                    (Workflow Orchestration)                      │
└────────────┬────────────────────────────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────┐          ┌────────────────────────┐
│   Price Collector      │          │   News Collector       │
│   (vnstock library)    │          │   (vnstock library)    │
└──────────┬─────────────┘          └──────────┬─────────────┘
           │                                   │
           │ publish                           │ publish
           ▼                                   ▼
    ┌──────────────────────────────────────────────┐
    │              Apache Kafka                     │
    │  Topics: stock_prices_raw, stock_news_raw    │
    └──────────┬───────────────────────┬───────────┘
               │ consume               │ consume
               ▼                       ▼
    ┌──────────────────┐    ┌──────────────────┐
    │  Kafka Consumer  │    │  Kafka Consumer  │
    │  (Price Data)    │    │  (News Data)     │
    └────────┬─────────┘    └────────┬─────────┘
             │                       │
             │ store                 │ store
             ▼                       ▼
    ┌─────────────────────────────────────────┐
    │            MongoDB                       │
    │  Collections: price_history, news,      │
    │  stocks, ai_analysis, llm_analysis,     │
    │  final_scores                           │
    └────┬────────────────────────────┬───────┘
         │ read                       │ read
         ▼                            ▼
┌─────────────────┐          ┌─────────────────┐
│  AI/ML Engine   │          │   LLM Engine    │
│  (Quantitative) │          │  (Qualitative)  │
└────────┬────────┘          └────────┬────────┘
         │ write                      │ write
         │                            │
         └────────────┬───────────────┘
                      ▼
            ┌──────────────────────┐
            │ Aggregation Service  │
            │  (Final Scoring)     │
            └──────────┬───────────┘
                       │ write
                       ▼
            ┌──────────────────────┐
            │    API Service       │
            │   (REST Endpoints)   │
            └──────────────────────┘
                       │
                       ▼
                  [Clients]
```

### Airflow DAG Structure

**Standalone Mode**: Airflow chạy với SQLite (không cần Postgres), phù hợp cho dự án cá nhân.

```
┌─────────────────────────────────────────┐
│      Price Collection DAG               │
│      (Schedule: */5 * * * *)            │
│      (Every 5 minutes)                  │
└─────────────────────────────────────────┘
                  │
                  ▼
         ┌──────────────────┐
         │ collect_prices   │
         │ (PythonOperator) │
         │ → Kafka          │
         └──────────────────┘


┌─────────────────────────────────────────┐
│      News Collection DAG                │
│      (Schedule: */30 * * * *)           │
│      (Every 30 minutes)                 │
└─────────────────────────────────────────┘
                  │
                  ▼
         ┌──────────────────┐
         │ collect_news     │
         │ (PythonOperator) │
         │ → Kafka          │
         └──────────────────┘


┌─────────────────────────────────────────┐
│      Analysis Pipeline DAG              │
│      (Schedule: 0 * * * *)              │
│      (Every hour)                       │
└─────────────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
┌──────────────┐    ┌──────────────┐
│ run_ai_ml    │    │ run_llm      │
│ (Operator)   │    │ (Operator)   │
└──────┬───────┘    └──────┬───────┘
       │                   │
       └─────────┬─────────┘
                 ▼
      ┌──────────────────────┐
      │ aggregate_results    │
      │ (PythonOperator)     │
      └──────────────────────┘
```

## Components and Interfaces

### 1. Data Collectors

#### Symbol Manager
```python
class SymbolManager:
    def __init__(self, mongo_client: MongoClient):
        self.db = mongo_client
    
    def load_symbols_from_json(self, json_file_path: str) -> int:
        """
        Load symbols from JSON file and upsert to MongoDB
        Returns: Number of symbols loaded
        """
        pass
    
    def get_active_symbols(self) -> List[str]:
        """
        Get list of active symbol codes for data collection
        Returns: List of symbol codes (e.g., ['VNM', 'VIC', 'HPG'])
        """
        pass
    
    def update_symbol(self, symbol: str, metadata: dict) -> bool:
        """
        Update symbol metadata
        Returns: True if successful
        """
        pass
```

#### Price Collector
```python
class PriceCollector:
    def __init__(self, kafka_producer: KafkaProducer, vnstock_client: VnStockClient, 
                 symbol_manager: SymbolManager):
        self.producer = kafka_producer
        self.client = vnstock_client
        self.symbol_manager = symbol_manager
    
    def collect(self) -> CollectionResult:
        """
        Collect price data for all active symbols from database
        Returns: CollectionResult with success/failure status
        """
        symbols = self.symbol_manager.get_active_symbols()
        # Collect data for each symbol
        pass
    
    def publish_to_kafka(self, data: PriceData) -> bool:
        """
        Publish price data to Kafka topic
        Returns: True if successful
        """
        pass
```

#### News Collector
```python
class NewsCollector:
    def __init__(self, kafka_producer: KafkaProducer, vnstock_client: VnStockClient,
                 symbol_manager: SymbolManager):
        self.producer = kafka_producer
        self.client = vnstock_client
        self.symbol_manager = symbol_manager
    
    def collect(self) -> CollectionResult:
        """
        Collect news articles for all active symbols from database
        Returns: CollectionResult with success/failure status
        """
        symbols = self.symbol_manager.get_active_symbols()
        # Collect news for each symbol
        pass
    
    def publish_to_kafka(self, data: NewsData) -> bool:
        """
        Publish news data to Kafka topic
        Returns: True if successful
        """
        pass
```

### 2. Kafka Consumers

```python
class KafkaDataConsumer:
    def __init__(self, consumer: KafkaConsumer, mongo_client: MongoClient):
        self.consumer = consumer
        self.db = mongo_client
    
    def consume_and_store(self, topic: str, collection: str) -> None:
        """
        Consume messages from Kafka topic and store in MongoDB
        Handles offset management and error recovery
        """
        pass
    
    def validate_message(self, message: dict) -> bool:
        """
        Validate message schema before storing
        Returns: True if valid
        """
        pass
```

### 3. AI/ML Engine

```python
class AIMLEngine:
    def __init__(self, mongo_client: MongoClient):
        self.db = mongo_client
        self.models = self._load_models()
    
    def analyze_stock(self, symbol: str, lookback_days: int = 90) -> AnalysisResult:
        """
        Perform quantitative analysis on stock
        Returns: AnalysisResult with scores and predictions
        """
        pass
    
    def calculate_trend(self, price_data: pd.DataFrame) -> TrendPrediction:
        """Calculate trend using time-series analysis"""
        pass
    
    def calculate_risk_score(self, price_data: pd.DataFrame) -> float:
        """Calculate risk score based on volatility"""
        pass
    
    def calculate_technical_score(self, price_data: pd.DataFrame) -> float:
        """Calculate technical score using indicators (RSI, MACD, etc.)"""
        pass
```

### 4. LLM Engine

```python
class LLMEngine:
    def __init__(self, mongo_client: MongoClient, llm_client: LLMClient):
        self.db = mongo_client
        self.llm = llm_client
    
    def analyze_news(self, symbol: str, lookback_days: int = 7) -> NewsAnalysisResult:
        """
        Perform qualitative analysis on news articles
        Returns: NewsAnalysisResult with sentiment and summaries
        """
        pass
    
    def analyze_sentiment(self, text: str) -> SentimentResult:
        """Analyze sentiment of single article"""
        pass
    
    def generate_summary(self, articles: List[str]) -> str:
        """Generate summary of multiple articles"""
        pass
    
    def calculate_influence_score(self, article: NewsArticle) -> float:
        """Calculate influence score based on source and content"""
        pass
```

### 5. Aggregation Service

```python
class AggregationService:
    def __init__(self, mongo_client: MongoClient):
        self.db = mongo_client
        self.weights = {
            'technical': 0.4,
            'risk': 0.3,
            'sentiment': 0.3
        }
    
    def aggregate(self, symbol: str) -> FinalScore:
        """
        Aggregate AI/ML and LLM results
        Returns: FinalScore with recommendation
        """
        pass
    
    def calculate_final_score(self, ai_result: AnalysisResult, 
                             llm_result: NewsAnalysisResult) -> float:
        """Calculate weighted final score (0-100)"""
        pass
    
    def generate_alerts(self, final_score: float, symbol: str) -> List[Alert]:
        """Generate alerts based on score thresholds"""
        pass
```

### 6. API Service

```python
class APIService:
    def __init__(self, mongo_client: MongoClient):
        self.db = mongo_client
    
    @app.get("/stock/{symbol}/summary")
    def get_stock_summary(self, symbol: str) -> StockSummary:
        """Get comprehensive stock summary"""
        pass
    
    @app.get("/alerts")
    def get_alerts(self, limit: int = 50) -> List[Alert]:
        """Get active alerts sorted by priority"""
        pass
    
    @app.get("/stock/{symbol}/history")
    def get_historical_analysis(self, symbol: str, 
                                start_date: str, 
                                end_date: str) -> HistoricalData:
        """Get historical analysis data"""
        pass
```

### 7. Airflow DAGs

**Airflow Standalone Configuration**:
```bash
# Initialize Airflow with SQLite (standalone mode)
export AIRFLOW_HOME=~/airflow
airflow standalone
```

**Price Collection DAG** (Every 5 minutes):
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    'price_collection',
    default_args=default_args,
    description='Collect stock prices every 5 minutes',
    schedule_interval='*/5 * * * *',  # Every 5 minutes
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:
    
    collect_prices = PythonOperator(
        task_id='collect_prices',
        python_callable=collect_price_data,
    )
```

**News Collection DAG** (Every 30 minutes):
```python
with DAG(
    'news_collection',
    default_args=default_args,
    description='Collect stock news every 30 minutes',
    schedule_interval='*/30 * * * *',  # Every 30 minutes
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:
    
    collect_news = PythonOperator(
        task_id='collect_news',
        python_callable=collect_news_data,
    )
```

**Analysis Pipeline DAG** (Every hour):
```python
with DAG(
    'analysis_pipeline',
    default_args=default_args,
    description='Run analysis and aggregation',
    schedule_interval='@hourly',  # Every hour
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:
    
    run_ai_ml = PythonOperator(
        task_id='run_ai_ml',
        python_callable=run_ai_ml_analysis,
    )
    
    run_llm = PythonOperator(
        task_id='run_llm',
        python_callable=run_llm_analysis,
    )
    
    aggregate = PythonOperator(
        task_id='aggregate_results',
        python_callable=aggregate_analysis,
    )
    
    # Both analyses run in parallel, then aggregate
    [run_ai_ml, run_llm] >> aggregate
```

## Data Models

### MongoDB Collections

#### symbols
```json
{
  "_id": "ObjectId",
  "symbol": "YTC",
  "organ_name": "Công ty Cổ phần Xuất nhập khẩu Y tế Thành phố Hồ Chí Minh",
  "icb_name2": "Y tế",
  "icb_name3": "Thiết bị và Dịch vụ Y tế",
  "icb_name4": "Dụng cụ y tế",
  "com_type_code": "CT",
  "icb_code1": "4000",
  "icb_code2": "4500",
  "icb_code3": "4530",
  "icb_code4": "4537",
  "active": true,
  "created_at": "2024-01-15T08:00:00Z",
  "updated_at": "2024-01-15T08:00:00Z"
}
```

#### price_history
```json
{
  "_id": "ObjectId",
  "symbol": "VNM",
  "timestamp": "2024-01-15T09:30:00Z",
  "open": 85000,
  "close": 86500,
  "high": 87000,
  "low": 84500,
  "volume": 1250000,
  "created_at": "2024-01-15T09:35:00Z"
}
```

#### news
```json
{
  "_id": "ObjectId",
  "symbol": "VNM",
  "title": "VNM công bố kết quả kinh doanh Q4",
  "content": "...",
  "source": "cafef.vn",
  "published_at": "2024-01-15T08:00:00Z",
  "collected_at": "2024-01-15T08:05:00Z"
}
```

#### ai_analysis
```json
{
  "_id": "ObjectId",
  "symbol": "VNM",
  "timestamp": "2024-01-15T10:00:00Z",
  "trend_prediction": {
    "direction": "up",
    "confidence": 0.75,
    "predicted_price": 88000
  },
  "risk_score": 0.35,
  "technical_score": 0.72,
  "indicators": {
    "rsi": 65,
    "macd": 1250,
    "moving_avg_20": 85500
  }
}
```

#### llm_analysis
```json
{
  "_id": "ObjectId",
  "symbol": "VNM",
  "timestamp": "2024-01-15T10:00:00Z",
  "sentiment": {
    "overall": "positive",
    "score": 0.68,
    "confidence": 0.82
  },
  "summary": "Công ty báo cáo tăng trưởng doanh thu...",
  "influence_score": 0.75,
  "articles_analyzed": 5
}
```

#### final_scores
```json
{
  "_id": "ObjectId",
  "symbol": "VNM",
  "timestamp": "2024-01-15T10:05:00Z",
  "final_score": 72.5,
  "recommendation": "BUY",
  "components": {
    "technical_score": 0.72,
    "risk_score": 0.35,
    "sentiment_score": 0.68
  },
  "alerts": [
    {
      "type": "BUY",
      "priority": "high",
      "message": "Strong buy signal detected"
    }
  ]
}
```

### Kafka Message Schemas

#### stock_prices_raw
```json
{
  "symbol": "VNM",
  "timestamp": "2024-01-15T09:30:00Z",
  "open": 85000,
  "close": 86500,
  "high": 87000,
  "low": 84500,
  "volume": 1250000
}
```

#### stock_news_raw
```json
{
  "symbol": "VNM",
  "title": "VNM công bố kết quả kinh doanh Q4",
  "content": "...",
  "source": "cafef.vn",
  "published_at": "2024-01-15T08:00:00Z"
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Symbol Management Properties

**Property 1: Symbol collection initialization**
*For any* system startup, if the symbols collection does not exist, it should be created successfully
**Validates: Requirements 2.1**

**Property 2: Symbol data completeness**
*For any* symbol stored in the symbols collection, the document should contain all required fields: symbol, organ_name, icb_name2, icb_name3, icb_name4, com_type_code, and icb_code fields
**Validates: Requirements 2.2**

**Property 3: Symbol upsert idempotence**
*For any* symbol loaded from JSON file, if the symbol already exists in the collection, the existing record should be updated with new metadata without creating duplicates
**Validates: Requirements 2.4**

**Property 4: Active symbols retrieval**
*For any* query for active symbols, only symbols with active=true should be returned
**Validates: Requirements 2.5**

### Data Collection Properties

**Property 5: Symbol-based price collection**
*For any* price collection run, price data should be collected for all symbols returned by get_active_symbols()
**Validates: Requirements 1.2**

**Property 6: Price data Kafka publishing**
*For any* successfully retrieved price data, the data should be published to the Kafka topic `stock_prices_raw`
**Validates: Requirements 1.3**

**Property 7: Price data round-trip preservation**
*For any* price data published to Kafka topic `stock_prices_raw`, when consumed and stored in MongoDB collection `price_history`, all original fields should be preserved
**Validates: Requirements 1.4**

**Property 8: Price data completeness**
*For any* price data stored in MongoDB collection `price_history`, the document should contain all required fields: timestamp, symbol, open, close, high, low, and volume
**Validates: Requirements 1.5**

**Property 9: Symbol-based news collection**
*For any* news collection run, news data should be collected for all symbols returned by get_active_symbols()
**Validates: Requirements 3.2**

**Property 10: News data Kafka publishing**
*For any* successfully retrieved news articles, the articles should be published to the Kafka topic `stock_news_raw`
**Validates: Requirements 3.3**

**Property 11: News data round-trip preservation**
*For any* news data published to Kafka topic `stock_news_raw`, when consumed and stored in MongoDB collection `news`, all original fields should be preserved
**Validates: Requirements 3.4**

**Property 12: News data completeness**
*For any* news data stored in MongoDB collection `news`, the document should contain all required fields: timestamp, title, content, source, and related stock symbols
**Validates: Requirements 3.5**

### Analysis Properties

**Property 13: AI/ML analysis data retrieval**
*For any* AI/ML analysis request for a stock symbol, historical price data should be successfully retrieved from the `price_history` collection
**Validates: Requirements 4.1**

**Property 14: Risk score validity**
*For any* price data analyzed by the AI/ML Engine, the calculated risk score should be a valid number between 0 and 1
**Validates: Requirements 4.3**

**Property 15: Technical score validity**
*For any* price data analyzed by the AI/ML Engine, the calculated technical score should be a valid number between 0 and 1
**Validates: Requirements 4.4**

**Property 16: AI/ML results storage completeness**
*For any* completed AI/ML analysis, the results stored in `ai_analysis` collection should include timestamp, stock symbol, trend prediction, risk score, and technical score
**Validates: Requirements 4.5**

**Property 17: Sentiment classification validity**
*For any* news article analyzed by the LLM Engine, the sentiment classification should be one of: positive, negative, or neutral, and include a confidence score between 0 and 1
**Validates: Requirements 5.2**

**Property 18: Influence score validity**
*For any* news article analyzed by the LLM Engine, the calculated influence score should be a valid number between 0 and 1
**Validates: Requirements 5.4**

**Property 19: LLM results storage completeness**
*For any* completed LLM analysis, the results stored in `llm_analysis` collection should include timestamp, stock symbol, sentiment classification, summary, and influence score
**Validates: Requirements 5.5**

### Aggregation Properties

**Property 20: Aggregation data retrieval completeness**
*For any* aggregation request for a stock symbol, both `ai_analysis` and `llm_analysis` results should be successfully retrieved
**Validates: Requirements 6.1**

**Property 21: Final score range validity**
*For any* aggregated analysis results, the calculated final recommendation score should be between 0 and 100
**Validates: Requirements 6.3**

**Property 22: Alert generation consistency**
*For any* final score calculated, if the score is above 70, an alert of type BUY should be generated; if between 40-70, type WATCH; if below 40, type RISK
**Validates: Requirements 6.4**

**Property 23: Final scores storage completeness**
*For any* completed aggregation, the results stored in `final_scores` collection should include timestamp, stock symbol, final score, recommendation, component scores, and alerts
**Validates: Requirements 6.5**

### API Properties

**Property 24: Stock summary response completeness**
*For any* valid stock symbol requested via API, the response should include current price data, AI/ML scores, LLM sentiment, and final recommendation
**Validates: Requirements 7.1**

**Property 25: Alert list sorting**
*For any* alert list returned by the API, alerts should be sorted first by priority (high, medium, low) then by timestamp (most recent first)
**Validates: Requirements 7.2**

**Property 26: Historical data date range filtering**
*For any* historical analysis request with start and end dates, all returned data should have timestamps within the specified date range (inclusive)
**Validates: Requirements 7.3**

**Property 27: API error response validity**
*For any* API request with invalid parameters, the response should include an appropriate HTTP error code (4xx) and a descriptive error message
**Validates: Requirements 7.4**

### Data Integrity Properties

**Property 28: Kafka consumer offset recovery**
*For any* Kafka consumer that fails and restarts, processing should resume from the last committed offset without data loss or duplication
**Validates: Requirements 8.3**

**Property 29: Referential integrity maintenance**
*For any* analysis result stored in `ai_analysis`, `llm_analysis`, or `final_scores` collections, the referenced stock symbol should exist in the `symbols` collection
**Validates: Requirements 9.3**

**Property 30: Data archival by retention period**
*For any* data record in any collection, if the record's timestamp is older than the configured retention period, it should be moved to the archive collection
**Validates: Requirements 9.4**

**Property 31: Database retry with exponential backoff**
*For any* failed database operation, retry attempts should occur with exponentially increasing delays (e.g., 1s, 2s, 4s, 8s)
**Validates: Requirements 9.5**

### Workflow Orchestration Properties

**Property 32: Airflow task retry on failure**
*For any* Airflow task that fails, the task should be retried according to the configured retry policy (max retries and retry delay)
**Validates: Requirements 11.4**

**Property 33: Price collection DAG scheduling**
*For any* 5-minute interval, the price collection DAG should trigger and execute the price collection task
**Validates: Requirements 11.2**

**Property 34: News collection DAG scheduling**
*For any* 30-minute interval, the news collection DAG should trigger and execute the news collection task
**Validates: Requirements 11.3**

**Property 35: Aggregation triggering after dual analysis**
*For any* stock symbol in the analysis pipeline DAG, the Aggregation Service should only be triggered after both AI/ML analysis and LLM analysis have completed successfully
**Validates: Requirements 12.3**

**Property 36: Failure isolation between DAGs**
*For any* task failure in one DAG (price, news, or analysis), the failure should not affect the execution of other independent DAGs
**Validates: Requirements 12.4**

**Property 37: Workflow execution metadata recording**
*For any* workflow execution in Airflow, metadata including start time, end time, and task duration should be recorded in the SQLite database
**Validates: Requirements 12.5**

### Error Handling and Logging Properties

**Property 38: Error logging completeness**
*For any* error encountered by any component, the error log should include timestamp, component name, error message, and stack trace
**Validates: Requirements 13.1**

**Property 39: Critical error notification**
*For any* critical error (system failure, data corruption), a notification should be sent to administrators through the configured notification channel
**Validates: Requirements 13.2**

**Property 40: Input validation with descriptive errors**
*For any* invalid input data received by any component, the data should be rejected and a descriptive error message should be generated
**Validates: Requirements 13.3**

**Property 41: Metric threshold alerting**
*For any* system metric (CPU, memory, disk, queue depth) that exceeds its configured threshold, an alert should be generated for the monitoring system
**Validates: Requirements 13.5**

## Error Handling

### Error Categories

1. **Data Collection Errors**
   - Network failures when accessing vnstock API
   - Invalid or malformed data from external sources
   - Rate limiting from data providers

2. **Kafka Errors**
   - Producer failures (unable to publish)
   - Consumer failures (unable to consume)
   - Broker unavailability

3. **Database Errors**
   - Connection failures
   - Write conflicts
   - Query timeouts

4. **Analysis Errors**
   - Insufficient historical data
   - Model inference failures
   - LLM API failures or timeouts

5. **Airflow Errors**
   - Task execution failures
   - DAG parsing errors
   - Scheduler issues

### Error Handling Strategies

#### Retry with Exponential Backoff
```python
def retry_with_backoff(func, max_retries=5, base_delay=1):
    """
    Retry function with exponential backoff
    Used for: Database operations, API calls, Kafka operations
    """
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            time.sleep(delay)
            logger.warning(f"Retry attempt {attempt + 1} after {delay}s")
```

#### Circuit Breaker Pattern
```python
class CircuitBreaker:
    """
    Prevent cascading failures
    Used for: External API calls, LLM service calls
    """
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
```

#### Dead Letter Queue
```python
# For Kafka messages that fail processing after max retries
DEAD_LETTER_TOPICS = {
    'stock_prices_raw': 'stock_prices_dlq',
    'stock_news_raw': 'stock_news_dlq'
}
```

### Logging Strategy

#### Log Levels
- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages (task start/complete)
- **WARNING**: Warning messages (retries, degraded performance)
- **ERROR**: Error messages (recoverable failures)
- **CRITICAL**: Critical errors (system failures, data corruption)

#### Structured Logging Format
```json
{
  "timestamp": "2024-01-15T10:00:00Z",
  "level": "ERROR",
  "component": "price_collector",
  "message": "Failed to retrieve price data",
  "context": {
    "symbol": "VNM",
    "error": "ConnectionTimeout",
    "stack_trace": "..."
  }
}
```

## Testing Strategy

### Unit Testing

Unit tests will verify specific functionality of individual components:

- **Data Collectors**: Test data retrieval and Kafka publishing logic
- **Kafka Consumers**: Test message consumption and MongoDB storage
- **AI/ML Engine**: Test individual calculation functions (trend, risk, technical scores)
- **LLM Engine**: Test sentiment analysis and summary generation (with mocked LLM)
- **Aggregation Service**: Test score calculation and alert generation logic
- **API Service**: Test endpoint responses and error handling

**Testing Framework**: pytest
**Mocking**: unittest.mock for external dependencies (vnstock, LLM API)

Example unit test:
```python
def test_calculate_risk_score():
    """Test risk score calculation with known data"""
    price_data = pd.DataFrame({
        'close': [100, 102, 98, 105, 95],
        'timestamp': pd.date_range('2024-01-01', periods=5)
    })
    engine = AIMLEngine(mock_mongo_client)
    risk_score = engine.calculate_risk_score(price_data)
    assert 0 <= risk_score <= 1
    assert isinstance(risk_score, float)
```

### Property-Based Testing

Property-based tests will verify universal properties across many randomly generated inputs using **Hypothesis** library.

**Configuration**: Each property test will run a minimum of 100 iterations.

**Property Test Tagging**: Each property-based test must include a comment explicitly referencing the correctness property from this design document using the format: `**Feature: vietnam-stock-ai-backend, Property {number}: {property_text}**`

Example property test:
```python
from hypothesis import given, strategies as st

@given(st.lists(st.floats(min_value=1000, max_value=100000), min_size=10))
def test_risk_score_validity(prices):
    """
    **Feature: vietnam-stock-ai-backend, Property 8: Risk score validity**
    
    For any price data analyzed by the AI/ML Engine, 
    the calculated risk score should be between 0 and 1
    """
    price_data = pd.DataFrame({
        'close': prices,
        'timestamp': pd.date_range('2024-01-01', periods=len(prices))
    })
    engine = AIMLEngine(mock_mongo_client)
    risk_score = engine.calculate_risk_score(price_data)
    assert 0 <= risk_score <= 1
```

### Integration Testing

Integration tests will verify interactions between components:

- **End-to-end data flow**: Price collection → Kafka → MongoDB → Analysis → Aggregation → API
- **Airflow DAG execution**: Verify task dependencies and execution order
- **Database operations**: Test MongoDB queries with real database (test container)
- **Kafka integration**: Test producer-consumer flow with Kafka test container

**Testing Framework**: pytest with testcontainers for MongoDB and Kafka

### Property-Based Test Coverage

The following correctness properties will be implemented as property-based tests:

- Properties 1-6: Data collection and storage
- Properties 7-13: Analysis engine validations
- Properties 14-17: Aggregation logic
- Properties 18-21: API responses
- Properties 22-25: Data integrity
- Properties 26-31: Workflow orchestration
- Properties 32-35: Error handling and logging

Each property will have its own dedicated test function with appropriate Hypothesis strategies for generating test data.

## Technology Stack

### Core Technologies
- **Language**: Python 3.11+
- **Workflow Orchestration**: Apache Airflow 2.8+
- **Message Broker**: Apache Kafka 3.6+
- **Database**: MongoDB 7.0+
- **API Framework**: FastAPI 0.109+
- **Data Processing**: pandas, numpy
- **ML Libraries**: scikit-learn, statsmodels
- **LLM Integration**: OpenAI API or local LLM (Ollama)

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Secrets Management**: Docker Secrets or HashiCorp Vault
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)

### Testing
- **Unit Testing**: pytest
- **Property-Based Testing**: Hypothesis
- **Integration Testing**: testcontainers
- **API Testing**: httpx

### Development Tools
- **Code Quality**: black, flake8, mypy
- **Dependency Management**: poetry or pip-tools
- **Version Control**: Git

## Deployment Architecture

### Docker Compose Services

**Simplified for Personal Project**:

```yaml
services:
  # Core Infrastructure
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
  
  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
  
  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
  
  # Airflow Standalone (SQLite backend)
  airflow:
    build: ./airflow
    ports:
      - "8080:8080"
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - airflow_data:/opt/airflow
    environment:
      AIRFLOW__CORE__EXECUTOR: SequentialExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: sqlite:////opt/airflow/airflow.db
      AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
    command: standalone
    depends_on:
      - kafka
      - mongodb
  
  # Kafka Consumer (always running)
  kafka-consumer:
    build: ./consumers
    depends_on:
      - kafka
      - mongodb
    restart: always
  
  # API Service
  api-service:
    build: ./services/api
    ports:
      - "8000:8000"
    depends_on:
      - mongodb
    restart: always

volumes:
  mongodb_data:
  airflow_data:
```

### Environment Configuration

**Simplified Configuration** for personal project:

```bash
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_TOPIC_PRICES=stock_prices_raw
KAFKA_TOPIC_NEWS=stock_news_raw

# MongoDB Configuration
MONGO_URI=mongodb://mongodb:27017
MONGO_DATABASE=stock_analysis

# Airflow Configuration (Standalone with SQLite)
AIRFLOW__CORE__EXECUTOR=SequentialExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=sqlite:////opt/airflow/airflow.db
AIRFLOW__CORE__LOAD_EXAMPLES=false
AIRFLOW_HOME=/opt/airflow

# LLM Configuration
OPENAI_API_KEY=${OPENAI_API_KEY}

# Stock Symbols to Track
STOCK_SYMBOLS=VNM,VIC,VHM,HPG,TCB
```

## Security Considerations (Simplified for Personal Project)

1. **Input Validation**: Validate all external inputs to prevent injection attacks
2. **Environment Variables**: Store sensitive credentials (API keys) in .env file
3. **Network Isolation**: Use Docker networks to isolate services
4. **Basic Authentication**: Simple API key authentication for API endpoints (optional)

## Performance Considerations (Simplified)

1. **MongoDB Indexing**: Create compound indexes on (symbol, timestamp) for efficient queries
2. **Batch Processing**: Process multiple stocks in batches where possible
3. **Connection Pooling**: Use connection pools for MongoDB and Kafka
4. **Async Operations**: Use async/await for I/O-bound operations in API service

## Scalability Strategy

Dự án cá nhân không cần scalability phức tạp. Nếu cần mở rộng trong tương lai:
1. Tăng số lượng Kafka partitions
2. Thêm indexes cho MongoDB
3. Nâng cấp từ Airflow Standalone sang Airflow với Celery Executor
