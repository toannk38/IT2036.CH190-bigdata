# Implementation Specifications for Remaining Modules

## 1. Gap Analysis

### ✅ **Implemented Components**
- `libs/vnstock/` - Complete vnstock API wrapper
- `services/data_collector/` - Price data collection service
- Testing framework with comprehensive unit tests

### 📋 **Missing Components (From Architecture Plan)**

#### **Phase 1: Infrastructure Layer**
- Docker Compose configuration
- MongoDB setup and schemas
- Kafka cluster configuration
- Redis caching layer

#### **Phase 2: Data Pipeline Completion**
- `services/kafka_consumer/` - Kafka to MongoDB consumer
- News collector service (extends data_collector pattern)

#### **Phase 3: AI/ML Analysis Engine**
- `services/ai_analysis/` - Technical analysis service
- `libs/ml/` - ML utilities and feature engineering

#### **Phase 4: LLM News Analysis**
- `services/llm_analysis/` - News sentiment analysis

#### **Phase 5: Aggregation Service**
- `services/aggregation/` - Score calculation and alerts

#### **Phase 6: API Layer**
- `services/api/` - REST API endpoints

---

## 2. Detailed Specifications for Missing Modules

### 2.1 Kafka Consumer Service

#### **Responsibility**
Consume messages from Kafka topics and persist data to MongoDB following the established data flow pattern.

#### **Interface Design**
```python
# services/kafka_consumer/src/consumers/base_consumer.py
class BaseConsumer:
    def __init__(self, bootstrap_servers: str, group_id: str):
        self.consumer = KafkaConsumer(
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
    
    def consume_messages(self, topics: List[str]) -> None:
        """Abstract method for message consumption"""
        pass

# services/kafka_consumer/src/consumers/price_consumer.py
class PriceConsumer(BaseConsumer):
    def __init__(self, bootstrap_servers: str, mongodb_client):
        super().__init__(bootstrap_servers, 'price-storage-consumers')
        self.storage = PriceStorage(mongodb_client)
        self.validator = DataValidator()
    
    def consume_messages(self, topics: List[str]) -> None:
        """Consume price messages and store to MongoDB"""
        pass
    
    def process_price_message(self, message: dict) -> bool:
        """Process single price message"""
        pass

# services/kafka_consumer/src/storage/mongodb_storage.py
class PriceStorage:
    def __init__(self, mongodb_client):
        self.db = mongodb_client
        self.price_collection = self.db.price_history
        self.stocks_collection = self.db.stocks
    
    def store_price_data(self, price_data: dict) -> bool:
        """Store price data to MongoDB"""
        pass
    
    def upsert_stock_metadata(self, symbol: str, last_price: float) -> bool:
        """Update stock metadata with latest price"""
        pass
```

#### **Data Flow**
```
Kafka Topics → PriceConsumer → DataValidator → PriceStorage → MongoDB
     ↓              ↓              ↓              ↓           ↓
stock_prices_raw → Deserialize → Validate → Transform → price_history
                                                    → stocks (metadata)
```

#### **Database Schema**
```javascript
// MongoDB Collections

// stocks collection
{
  "_id": ObjectId("..."),
  "symbol": "VCB",
  "company_name": "Vietcombank",
  "exchange": "HOSE", 
  "industry": "Banking",
  "last_price": 86.0,
  "last_update": ISODate("2024-12-04T09:15:00Z"),
  "market_cap": 850000000000,
  "outstanding_shares": 3500000000,
  "created_at": ISODate("2024-01-01T00:00:00Z"),
  "updated_at": ISODate("2024-12-04T09:15:00Z")
}

// price_history collection  
{
  "_id": ObjectId("..."),
  "symbol": "VCB",
  "timestamp": ISODate("2024-12-04T09:15:00Z"),
  "open": 85.5,
  "high": 86.2,
  "low": 85.0,
  "close": 86.0,
  "volume": 1250000,
  "source": "vnstock",
  "created_at": ISODate("2024-12-04T09:15:30Z")
}

// Indexes
db.stocks.createIndex({ "symbol": 1 }, { unique: true })
db.price_history.createIndex({ "symbol": 1, "timestamp": -1 })
db.price_history.createIndex({ "timestamp": -1 })
```

### 2.2 News Collector Service (Extension of data_collector)

#### **Responsibility**
Extend existing data_collector pattern to collect and process news data from vnstock.

#### **Interface Design**
```python
# services/data_collector/src/collectors/news_collector.py
class NewsCollector:
    def __init__(self, vnstock_client: VnstockClient, 
                 kafka_producer: StockKafkaProducer, kafka_topic: str):
        self.vnstock_client = vnstock_client
        self.kafka_producer = kafka_producer
        self.kafka_topic = kafka_topic
        self.validator = NewsValidator()
        self.normalizer = NewsNormalizer()
        self.deduplicator = NewsDeduplicator()
    
    def collect_symbol_news(self, symbol: str) -> int:
        """Collect news for a single symbol"""
        pass
    
    def collect_all_news(self) -> dict:
        """Collect news for all symbols"""
        pass

# services/data_collector/src/processors/news_validator.py
class NewsValidator:
    @staticmethod
    def validate_news_data(data: Dict[str, Any]) -> bool:
        required_fields = ['symbol', 'title', 'publish_date', 'source']
        return all(field in data for field in required_fields)

# services/data_collector/src/processors/news_normalizer.py  
class NewsNormalizer:
    @staticmethod
    def normalize_news_data(news_data) -> Dict[str, Any]:
        return {
            'news_id': hashlib.md5(news_data.title.encode()).hexdigest(),
            'symbol': news_data.symbol,
            'title': news_data.title,
            'publish_date': news_data.publish_date.isoformat(),
            'source': news_data.source,
            'url': news_data.url,
            'collected_at': datetime.utcnow().isoformat()
        }

# services/data_collector/src/processors/news_deduplicator.py
class NewsDeduplicator:
    def __init__(self):
        self.seen_hashes = set()
    
    def is_duplicate(self, news_id: str) -> bool:
        """Check if news already processed"""
        pass
```

#### **Data Flow**
```
vnstock.get_news() → NewsCollector → NewsValidator → NewsNormalizer → Kafka
                                                                        ↓
                                                              stock_news_raw
```

### 2.3 AI Analysis Service

#### **Responsibility**
Perform technical analysis on price data using ML models, following the established error handling and logging patterns.

#### **Interface Design**
```python
# services/ai_analysis/src/analyzers/technical_analyzer.py
class TechnicalAnalyzer:
    def __init__(self, mongodb_client):
        self.price_repository = PriceRepository(mongodb_client)
        self.feature_engine = FeatureEngine()
        self.model_loader = ModelLoader()
    
    def analyze_symbol(self, symbol: str, days: int = 60) -> dict:
        """Analyze single symbol technical indicators"""
        pass
    
    def analyze_all_symbols(self) -> dict:
        """Analyze all symbols in batch"""
        pass

# libs/ml/feature_engineering.py
class FeatureEngine:
    @staticmethod
    def calculate_technical_indicators(price_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI, MACD, Bollinger Bands following vnstock data format"""
        pass
    
    @staticmethod
    def detect_patterns(price_df: pd.DataFrame) -> dict:
        """Detect candlestick patterns"""
        pass

# services/ai_analysis/src/models/prediction_service.py
class PredictionService:
    def __init__(self):
        self.models = self._load_models()
    
    def predict_trend(self, features: pd.DataFrame) -> dict:
        """Predict price trend using ensemble models"""
        return {
            'trend_direction': 'bullish',  # bullish/bearish/neutral
            'confidence': 0.75,
            'risk_score': 0.3,
            'technical_score': 0.8
        }
```

#### **Database Schema**
```javascript
// ai_analysis collection
{
  "_id": ObjectId("..."),
  "symbol": "VCB",
  "analysis_date": ISODate("2024-12-04T10:00:00Z"),
  "technical_indicators": {
    "rsi_14": 65.5,
    "macd": 0.8,
    "bollinger_position": 0.7,
    "volume_sma_ratio": 1.2
  },
  "patterns": {
    "hammer": false,
    "doji": true,
    "engulfing": false
  },
  "predictions": {
    "trend_direction": "bullish",
    "confidence": 0.75,
    "risk_score": 0.3,
    "technical_score": 0.8
  },
  "created_at": ISODate("2024-12-04T10:00:00Z")
}
```

### 2.4 LLM Analysis Service

#### **Responsibility**
Analyze news sentiment and extract insights using LLM APIs, following established error handling patterns.

#### **Interface Design**
```python
# services/llm_analysis/src/analyzers/sentiment_analyzer.py
class SentimentAnalyzer:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.prompt_templates = PromptTemplates()
    
    def analyze_news_sentiment(self, news_data: dict) -> dict:
        """Analyze sentiment of single news article"""
        pass
    
    def batch_analyze_news(self, news_list: List[dict]) -> List[dict]:
        """Batch analyze multiple news articles"""
        pass

# services/llm_analysis/src/llm/openai_client.py
class OpenAIClient:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.rate_limiter = RateLimiter(requests_per_minute=60)
    
    def analyze_text(self, prompt: str, text: str) -> dict:
        """Send text to OpenAI for analysis"""
        pass

# services/llm_analysis/src/prompts/prompt_templates.py
class PromptTemplates:
    SENTIMENT_ANALYSIS = """
    Analyze the sentiment of this Vietnamese stock news article.
    Return JSON with: sentiment (positive/negative/neutral), 
    confidence (0-1), impact_score (0-1), key_insights (list).
    
    Article: {text}
    """
```

#### **Database Schema**
```javascript
// llm_analysis collection
{
  "_id": ObjectId("..."),
  "news_id": "hash_abc123",
  "symbol": "VCB",
  "analysis_date": ISODate("2024-12-04T10:30:00Z"),
  "sentiment": {
    "sentiment": "positive",
    "confidence": 0.85,
    "impact_score": 0.7
  },
  "insights": [
    "Positive earnings report",
    "Strong market position"
  ],
  "summary": "Company reports strong Q4 results...",
  "created_at": ISODate("2024-12-04T10:30:00Z")
}
```

### 2.5 Aggregation Service

#### **Responsibility**
Combine AI and LLM analysis results to generate final scores and alerts.

#### **Interface Design**
```python
# services/aggregation/src/aggregators/score_aggregator.py
class ScoreAggregator:
    def __init__(self, mongodb_client):
        self.ai_repository = AIAnalysisRepository(mongodb_client)
        self.llm_repository = LLMAnalysisRepository(mongodb_client)
        self.score_calculator = ScoreCalculator()
    
    def calculate_final_scores(self, symbol: str) -> dict:
        """Calculate final aggregated scores"""
        pass
    
    def generate_alerts(self, scores: dict) -> List[dict]:
        """Generate buy/sell/watch alerts"""
        pass

# services/aggregation/src/scoring/score_calculator.py
class ScoreCalculator:
    def combine_scores(self, technical_score: float, 
                      sentiment_score: float, weights: dict) -> dict:
        """Combine technical and sentiment scores"""
        final_score = (
            technical_score * weights['technical'] + 
            sentiment_score * weights['sentiment']
        )
        return {
            'final_score': final_score,
            'recommendation': self._get_recommendation(final_score),
            'confidence': min(technical_score, sentiment_score)
        }
    
    def _get_recommendation(self, score: float) -> str:
        if score >= 0.7: return 'BUY'
        elif score <= 0.3: return 'SELL'
        else: return 'WATCH'
```

### 2.6 API Service

#### **Responsibility**
Provide REST API endpoints following FastAPI patterns established in the codebase.

#### **Interface Design**
```python
# services/api/src/main.py
from fastapi import FastAPI, HTTPException
from .routes import stocks, analysis, alerts

app = FastAPI(title="Stock AI API", version="1.0.0")
app.include_router(stocks.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")

# services/api/src/routes/stocks.py
@router.get("/stocks/{symbol}/summary")
async def get_stock_summary(symbol: str) -> StockSummaryResponse:
    """Get comprehensive stock summary"""
    pass

@router.get("/stocks/{symbol}/analysis")
async def get_stock_analysis(symbol: str) -> AnalysisResponse:
    """Get AI and LLM analysis results"""
    pass

# services/api/src/models/responses.py
class StockSummaryResponse(BaseModel):
    symbol: str
    company_name: str
    last_price: float
    change_percent: float
    final_score: float
    recommendation: str
    
class AnalysisResponse(BaseModel):
    symbol: str
    technical_analysis: dict
    sentiment_analysis: dict
    final_scores: dict
```

---

## 3. Integration Strategy

### 3.1 Data Flow Integration

#### **Current Flow** ✅
```
vnstock → data_collector → Kafka → [MISSING: kafka_consumer] → [MISSING: MongoDB]
```

#### **Complete Flow** 📋
```
vnstock → data_collector → Kafka → kafka_consumer → MongoDB
                                        ↓
                                   ai_analysis ← MongoDB
                                        ↓
                                   llm_analysis ← MongoDB  
                                        ↓
                                   aggregation ← MongoDB
                                        ↓
                                      API ← MongoDB
```

### 3.2 Configuration Integration

#### **Extend Existing Pattern**
```python
# Follow services/data_collector/src/config/settings.py pattern
# services/kafka_consumer/src/config/settings.py
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'stock_ai')
KAFKA_CONSUMER_GROUP = os.getenv('KAFKA_CONSUMER_GROUP', 'storage-consumers')

# services/ai_analysis/src/config/settings.py  
MODEL_PATH = os.getenv('MODEL_PATH', '/app/models')
ANALYSIS_BATCH_SIZE = int(os.getenv('ANALYSIS_BATCH_SIZE', '100'))

# services/llm_analysis/src/config/settings.py
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LLM_RATE_LIMIT = float(os.getenv('LLM_RATE_LIMIT', '1.0'))
```

### 3.3 Error Handling Integration

#### **Extend Exception Hierarchy**
```python
# libs/common/exceptions.py (new)
class StockAIError(Exception):
    """Base exception for Stock AI system"""
    pass

class DatabaseError(StockAIError):
    """Database operation errors"""
    pass

class AnalysisError(StockAIError):
    """Analysis processing errors"""
    pass

class APIError(StockAIError):
    """API service errors"""
    pass
```

### 3.4 Testing Integration

#### **Follow Established Pattern**
```python
# tests/test_services/kafka_consumer/test_price_consumer.py
class TestPriceConsumer:
    def test_consume_messages_success(self, mock_kafka_consumer, mock_mongodb)
    def test_process_price_message_valid(self, sample_price_message)
    def test_storage_failure_handling(self, mock_storage_error)

# tests/test_services/ai_analysis/test_technical_analyzer.py  
class TestTechnicalAnalyzer:
    def test_analyze_symbol_success(self, mock_price_data)
    def test_feature_calculation(self, sample_price_df)
    def test_prediction_service(self, mock_model_output)
```

### 3.5 Docker Integration

#### **Extend docker-compose.yml**
```yaml
# Add to existing docker-compose structure
services:
  kafka-consumer:
    build: ./services/kafka_consumer
    depends_on: [kafka, mongodb]
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - MONGODB_URI=mongodb://mongodb:27017
  
  ai-analysis:
    build: ./services/ai_analysis  
    depends_on: [mongodb]
    volumes:
      - ./models:/app/models
  
  api:
    build: ./services/api
    ports: ["8000:8000"]
    depends_on: [mongodb]
```

### 3.6 Monitoring Integration

#### **Extend Logging Pattern**
```python
# Follow services/data_collector/src/main.py logging pattern
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add service-specific loggers
logger = logging.getLogger('kafka_consumer')
logger = logging.getLogger('ai_analysis')  
logger = logging.getLogger('llm_analysis')
```

---

## 4. Implementation Priority

### **Phase 1: Infrastructure** (Immediate)
1. Docker Compose setup
2. MongoDB configuration
3. Kafka consumer service

### **Phase 2: Core Analysis** (Week 2-3)
1. AI analysis service
2. LLM analysis service  

### **Phase 3: Integration** (Week 4)
1. Aggregation service
2. API service

### **Phase 4: Production** (Week 5+)
1. Monitoring integration
2. Performance optimization
3. Security hardening

This specification maintains strict consistency with existing code patterns while providing clear implementation guidance for the remaining system components.