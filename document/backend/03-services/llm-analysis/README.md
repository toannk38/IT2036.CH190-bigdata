# LLM Analysis Service Documentation

## Overview

The LLM Analysis Service provides on-demand natural language analysis of stock data via API calls. It analyzes stock fundamentals, news sentiment, and market conditions using Large Language Models.

**Status**: 🔄 **PLANNED**

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   API Request   │───►│  LLM Analysis    │───►│   API Response  │
│  (Symbol Info)  │    │    Service       │    │  (Analysis)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │    MongoDB       │
                       │ (Price + News)   │
                       └──────────────────┘
```

## Core Components

### 1. LLM Client
**Location**: `services/llm_analysis/src/clients/llm_client.py`

- **Model Integration**: Connects to LLM APIs (OpenAI, Anthropic, etc.)
- **Prompt Management**: Manages analysis prompts and templates
- **Response Parsing**: Parses and validates LLM responses
- **Rate Limiting**: Handles API rate limits and costs

### 2. Analysis Engine
**Location**: `services/llm_analysis/src/engines/analysis_engine.py`

- **Data Aggregation**: Combines price data, news, and market context
- **Prompt Generation**: Creates context-aware prompts for LLM
- **Response Processing**: Processes and structures LLM outputs
- **Caching**: Caches recent analyses to reduce API calls

### 3. API Handler
**Location**: `services/llm_analysis/src/api/handlers.py`

- **Request Processing**: Handles incoming analysis requests
- **Parameter Validation**: Validates symbol and analysis parameters
- **Response Formatting**: Formats analysis results for API response
- **Error Handling**: Manages API errors and fallbacks

### 4. Data Aggregator
**Location**: `services/llm_analysis/src/data/aggregator.py`

- **Price Data**: Fetches recent price history and trends
- **News Data**: Retrieves relevant news articles
- **Market Context**: Adds market-wide context and indicators
- **Data Synthesis**: Combines all data sources for analysis

## Configuration

### Environment Variables
```python
# LLM Configuration
LLM_PROVIDER=openai  # openai, anthropic, local
LLM_API_KEY=your_api_key_here
LLM_MODEL=gpt-4
LLM_MAX_TOKENS=2000
LLM_TEMPERATURE=0.3

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=stock_ai
MONGODB_COLLECTION_PRICES=stock_prices
MONGODB_COLLECTION_NEWS=stock_news

# API Configuration
API_HOST=0.0.0.0
API_PORT=8002
API_RATE_LIMIT=10.0  # requests per second

# Cache Configuration
CACHE_TTL=3600  # 1 hour
REDIS_URL=redis://localhost:6379

# Analysis Configuration
MAX_PRICE_DAYS=30
MAX_NEWS_ARTICLES=10
ANALYSIS_TIMEOUT=30  # seconds
```

## Data Models

### Request Model
```python
@dataclass
class AnalysisRequest:
    symbol: str
    analysis_type: str  # 'fundamental', 'technical', 'sentiment', 'comprehensive'
    time_horizon: str   # 'short', 'medium', 'long'
    include_news: bool = True
    include_technical: bool = True
```

### Response Model
```python
@dataclass
class LLMAnalysisResult:
    symbol: str
    analysis_time: datetime
    analysis_type: str
    summary: str
    key_insights: List[str]
    sentiment: str  # 'BULLISH', 'BEARISH', 'NEUTRAL'
    confidence: float
    price_outlook: str
    risk_factors: List[str]
    opportunities: List[str]
    recommendation: str
```

## API Endpoints

### Analysis Endpoint
```
POST /api/v1/analysis/{symbol}
```

**Request Body:**
```json
{
  "analysis_type": "comprehensive",
  "time_horizon": "medium",
  "include_news": true,
  "include_technical": true
}
```

**Response:**
```json
{
  "symbol": "VCB",
  "analysis_time": "2024-12-04T10:30:00Z",
  "summary": "VCB shows strong fundamentals with positive technical indicators...",
  "sentiment": "BULLISH",
  "confidence": 0.85,
  "recommendation": "BUY"
}
```

## Processing Flow

1. **API Request**: Receive analysis request for symbol
2. **Data Collection**: Fetch price data, news, and market context
3. **Prompt Generation**: Create LLM prompt with collected data
4. **LLM Analysis**: Send prompt to LLM and get response
5. **Response Processing**: Parse and validate LLM output
6. **Result Formatting**: Format analysis for API response
7. **Caching**: Cache result for future requests

## LLM Integration

### Prompt Templates
```python
ANALYSIS_PROMPT = """
Analyze the following stock data for {symbol}:

Price Data (Last 30 days):
{price_summary}

Recent News:
{news_summary}

Technical Indicators:
{technical_indicators}

Provide a comprehensive analysis including:
1. Overall sentiment (BULLISH/BEARISH/NEUTRAL)
2. Key insights and trends
3. Risk factors and opportunities
4. Price outlook and recommendation
"""
```

### Response Parsing
- **Structured Output**: Parse LLM response into structured format
- **Validation**: Validate sentiment, confidence, and recommendations
- **Fallback**: Handle parsing errors with default responses

## Caching Strategy

### Redis Integration
- **Analysis Cache**: Cache complete analyses by symbol+parameters
- **Data Cache**: Cache fetched price and news data
- **TTL Management**: Configurable time-to-live for different data types

### Cache Keys
```python
analysis_key = f"llm_analysis:{symbol}:{analysis_type}:{time_horizon}"
price_key = f"price_data:{symbol}:{days}"
news_key = f"news_data:{symbol}:{hours}"
```

## Rate Limiting

### API Rate Limits
- **Per-client limits**: Configurable requests per second
- **LLM API limits**: Respect provider rate limits
- **Cost management**: Track and limit API costs

## Error Handling

### Fallback Strategy
- **LLM Unavailable**: Return cached analysis or basic technical analysis
- **Data Unavailable**: Use price-only analysis
- **API Errors**: Return appropriate error responses with fallbacks

## Deployment

### Docker Configuration
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
EXPOSE 8002
CMD ["python", "-m", "src.main"]
```

### Dependencies
- fastapi==0.104.1
- openai==1.3.0
- anthropic==0.7.0
- redis==5.0.1
- pymongo==4.6.1
- pydantic==2.5.0