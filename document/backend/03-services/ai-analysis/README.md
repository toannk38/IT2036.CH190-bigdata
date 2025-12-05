# AI Analysis Service Documentation

## Overview

The AI Analysis Service performs technical analysis on stock price data using machine learning models with internal scheduling and batch processing.

**Status**: 🔄 **PLANNED**

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│    MongoDB      │───►│  AI Analysis     │───►│  Kafka Topics   │
│  (Price Data)   │    │    Service       │    │ (AI Results)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Model Manager   │
                       │ (ML Models)      │
                       └──────────────────┘
```

## Core Components

### 1. Model Manager
**Location**: `services/ai_analysis/src/models/model_manager.py`

- **Model Loading**: Loads pre-trained ML models from disk
- **Model Caching**: Keeps models in memory for performance
- **Model Versioning**: Supports multiple model versions
- **Prediction Interface**: Unified interface for all models

### 2. Technical Analyzer
**Location**: `services/ai_analysis/src/analyzers/technical_analyzer.py`

- **Price Analysis**: Analyzes price patterns and trends
- **Indicator Calculation**: RSI, MACD, Bollinger Bands, etc.
- **Signal Generation**: Buy/sell/hold signals
- **Confidence Scoring**: Prediction confidence levels

### 3. Batch Scheduler
**Location**: `services/ai_analysis/src/schedulers/batch_scheduler.py`

- **Internal Scheduling**: Runs analysis at configured intervals
- **Batch Processing**: Processes multiple symbols in batches
- **Rate Limiting**: Controls analysis frequency per symbol
- **Error Recovery**: Handles failed analysis attempts

### 4. Data Fetcher
**Location**: `services/ai_analysis/src/data/data_fetcher.py`

- **MongoDB Integration**: Fetches price data from MongoDB
- **Data Windowing**: Gets historical data windows for analysis
- **Data Validation**: Ensures sufficient data for analysis
- **Caching**: Caches recent data for performance

## Configuration

### Environment Variables
```python
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=stock_ai
MONGODB_COLLECTION_PRICES=stock_prices

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_AI_RESULTS_TOPIC=ai_analysis_results

# Analysis Configuration
ANALYSIS_INTERVAL=300  # 5 minutes
BATCH_SIZE=50
LOOKBACK_DAYS=30
MIN_DATA_POINTS=20

# Model Configuration
MODEL_PATH=/app/models
MODEL_VERSION=v1.0
CONFIDENCE_THRESHOLD=0.7

# Rate Limiting
ANALYSIS_RATE_LIMIT=5.0  # analyses per second
```

## Data Models

### Input Data
Uses `StockPrice` from `libs/vnstock/models.py`

### Output Data
```python
@dataclass
class AIAnalysisResult:
    symbol: str
    analysis_time: datetime
    signal: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float
    indicators: Dict[str, float]
    price_target: Optional[float]
    risk_level: str  # 'LOW', 'MEDIUM', 'HIGH'
```

## Processing Flow

1. **Scheduled Trigger**: Internal scheduler triggers analysis
2. **Data Fetching**: Fetch historical price data from MongoDB
3. **Data Validation**: Ensure sufficient data quality
4. **Model Prediction**: Run ML models on price data
5. **Signal Generation**: Generate trading signals
6. **Result Publishing**: Publish results to Kafka topic
7. **Rate Limiting**: Apply processing rate limits

## Model Types

### Technical Analysis Models
- **Trend Analysis**: Moving averages, trend lines
- **Momentum Analysis**: RSI, MACD indicators
- **Volatility Analysis**: Bollinger Bands, ATR
- **Pattern Recognition**: Chart patterns, candlestick patterns

### Machine Learning Models
- **LSTM Networks**: Time series prediction
- **Random Forest**: Feature-based classification
- **SVM**: Support vector machines for signals
- **Ensemble Methods**: Combined model predictions

## Deployment

### Docker Configuration
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY models/ ./models/
COPY src/ ./src/
CMD ["python", "-m", "src.main"]
```

### Dependencies
- scikit-learn==1.3.0
- tensorflow==2.13.0
- pandas==2.0.3
- numpy==1.24.3
- kafka-python==2.0.2
- pymongo==4.6.1