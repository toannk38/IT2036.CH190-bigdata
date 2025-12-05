# API Service Documentation

## Overview

The API Service provides REST endpoints for accessing stock data, analysis results, and insights. It serves as the main interface for frontend applications and external integrations. Current version does not require authentication.

**Status**: 🔄 **PLANNED**

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │───►│   API Service    │───►│     Redis       │
│  Applications   │    │  (REST API)      │    │   (Insights)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ External APIs   │    │    MongoDB       │    │ LLM Analysis    │
│   (Webhooks)    │    │  (Price Data)    │    │    Service      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Core Components

### 1. Stock Data API
**Location**: `services/api/src/routers/stocks.py`

- **Price Data**: Historical and real-time price information
- **Stock Listings**: Available symbols and company information
- **Market Data**: Market-wide statistics and indicators
- **Data Filtering**: Time range and symbol filtering

### 2. Analysis API
**Location**: `services/api/src/routers/analysis.py`

- **AI Insights**: Technical analysis results from AI service
- **LLM Analysis**: On-demand LLM analysis via service calls
- **Aggregated Insights**: Combined analysis from aggregation service
- **Historical Analysis**: Past analysis results and trends

### 3. Market API
**Location**: `services/api/src/routers/market.py`

- **Market Overview**: Overall market sentiment and trends
- **Sector Analysis**: Sector-specific insights and performance
- **Top Movers**: Best and worst performing stocks
- **Market Indicators**: Key market metrics and indices

### 4. Data Manager
**Location**: `services/api/src/managers/data_manager.py`

- **Redis Integration**: Fetches insights from Redis cache
- **MongoDB Integration**: Retrieves historical price data
- **Service Integration**: Calls LLM analysis service when needed
- **Data Aggregation**: Combines data from multiple sources

## Configuration

### Environment Variables
```python
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_TITLE="Stock AI Backend API"
API_VERSION="1.0.0"
DEBUG=false

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_DB=0

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=stock_ai
MONGODB_COLLECTION_PRICES=stock_prices

# Service URLs
LLM_ANALYSIS_SERVICE_URL=http://localhost:8002
AGGREGATION_SERVICE_URL=http://localhost:8003

# Rate Limiting
API_RATE_LIMIT=100  # requests per minute per IP
BURST_LIMIT=20      # burst requests

# Caching
CACHE_TTL=300       # 5 minutes
RESPONSE_CACHE_SIZE=1000
```

## API Endpoints

### Stock Data Endpoints

#### Get Stock Price History
```
GET /api/v1/stocks/{symbol}/prices
Query Parameters:
- start_date: ISO date (optional)
- end_date: ISO date (optional)  
- interval: 1D, 1H, 5M (default: 1D)
- limit: max records (default: 100)
```

**Response:**
```json
{
  "symbol": "VCB",
  "data": [
    {
      "time": "2024-12-04T09:15:00+07:00",
      "open": 85.5,
      "high": 86.2,
      "low": 85.0,
      "close": 86.0,
      "volume": 1250000
    }
  ],
  "count": 1,
  "has_more": false
}
```

#### Get Stock Information
```
GET /api/v1/stocks/{symbol}/info
```

#### Get All Stocks
```
GET /api/v1/stocks
Query Parameters:
- sector: filter by sector
- limit: max results
- offset: pagination offset
```

### Analysis Endpoints

#### Get Current Insight
```
GET /api/v1/analysis/{symbol}/insight
```

**Response:**
```json
{
  "symbol": "VCB",
  "overall_signal": "BUY",
  "confidence": 0.85,
  "ai_signal": "BUY",
  "llm_signal": "HOLD",
  "price_trend": "UPWARD",
  "risk_level": "MEDIUM",
  "key_factors": ["Strong momentum", "Positive earnings"],
  "last_updated": "2024-12-04T10:30:00Z"
}
```

#### Request LLM Analysis
```
POST /api/v1/analysis/{symbol}/llm
Body:
{
  "analysis_type": "comprehensive",
  "time_horizon": "medium",
  "include_news": true
}
```

#### Get Analysis History
```
GET /api/v1/analysis/{symbol}/history
Query Parameters:
- days: number of days (default: 7)
- analysis_type: filter by type
```

### Market Endpoints

#### Get Market Overview
```
GET /api/v1/market/overview
```

**Response:**
```json
{
  "market_sentiment": "BULLISH",
  "total_symbols": 1500,
  "active_symbols": 1200,
  "top_gainers": [
    {"symbol": "VCB", "change": 5.2},
    {"symbol": "VIC", "change": 3.8}
  ],
  "top_losers": [
    {"symbol": "ABC", "change": -2.1}
  ],
  "sector_performance": {
    "Banking": 2.5,
    "Technology": 1.8
  }
}
```

#### Get Sector Analysis
```
GET /api/v1/market/sectors/{sector}
```

#### Get Top Movers
```
GET /api/v1/market/movers
Query Parameters:
- type: gainers, losers, volume
- limit: max results (default: 10)
```

## Data Flow

### Request Processing
1. **Request Validation**: Validate parameters and headers
2. **Rate Limiting**: Check request rate limits
3. **Cache Check**: Check Redis cache for recent data
4. **Data Fetching**: Fetch from MongoDB/services if cache miss
5. **Response Formatting**: Format data for API response
6. **Cache Update**: Update cache with fresh data
7. **Response**: Return formatted response

### LLM Analysis Flow
1. **Request Received**: API receives LLM analysis request
2. **Parameter Validation**: Validate symbol and analysis parameters
3. **Service Call**: Call LLM Analysis Service via HTTP
4. **Response Processing**: Process and validate service response
5. **Cache Update**: Cache analysis result in Redis
6. **API Response**: Return analysis to client

## Response Formats

### Standard Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Success",
  "timestamp": "2024-12-04T10:30:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "SYMBOL_NOT_FOUND",
    "message": "Symbol VCB not found",
    "details": "The requested symbol does not exist in our database"
  },
  "timestamp": "2024-12-04T10:30:00Z"
}
```

### Pagination Response
```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 1500,
    "has_next": true,
    "has_prev": false
  }
}
```

## Rate Limiting

### Implementation
- **Redis-based**: Uses Redis for distributed rate limiting
- **Per-IP Limits**: 100 requests per minute per IP address
- **Burst Handling**: Allows burst of 20 requests
- **Sliding Window**: Uses sliding window algorithm

### Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1701684660
```

## Caching Strategy

### Multi-level Caching
1. **Application Cache**: In-memory cache for frequent data
2. **Redis Cache**: Distributed cache for shared data
3. **HTTP Cache**: Browser/CDN caching with appropriate headers

### Cache Keys
```python
# Price data cache
price_cache_key = f"prices:{symbol}:{start_date}:{end_date}:{interval}"

# Insight cache
insight_cache_key = f"insight:{symbol}"

# Market overview cache
market_cache_key = "market:overview"

# Analysis history cache
history_cache_key = f"analysis:history:{symbol}:{days}"
```

## Error Handling

### Error Categories
- **Validation Errors**: Invalid parameters or request format
- **Not Found Errors**: Requested resource doesn't exist
- **Service Errors**: Downstream service failures
- **Rate Limit Errors**: Request rate exceeded
- **Internal Errors**: Unexpected server errors

### Fallback Strategy
- **Service Unavailable**: Return cached data with warning
- **Partial Data**: Return available data with completeness indicator
- **Analysis Unavailable**: Return price data only

## Security

### Current Implementation
- **No Authentication**: Open API access (as specified)
- **Rate Limiting**: Prevents abuse and DoS attacks
- **Input Validation**: Validates all input parameters
- **CORS**: Configurable CORS policies

### Future Security (When Authentication Added)
- **JWT Tokens**: Stateless authentication
- **API Keys**: Service-to-service authentication
- **Role-based Access**: Different access levels
- **Request Signing**: Secure API requests

## Monitoring

### Metrics
- **Request Rate**: Requests per second/minute
- **Response Time**: API response latency
- **Error Rate**: Error percentage by endpoint
- **Cache Hit Rate**: Cache effectiveness
- **Service Health**: Downstream service availability

### Health Checks
```
GET /health
GET /health/detailed
```

## Deployment

### Docker Configuration
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dependencies
- fastapi==0.104.1
- uvicorn==0.24.0
- redis==5.0.1
- pymongo==4.6.1
- httpx==0.25.2
- pydantic==2.5.0

### Load Balancing
- **Multiple Instances**: Run multiple API instances
- **Load Balancer**: Nginx or cloud load balancer
- **Health Checks**: Automatic instance health monitoring
- **Graceful Shutdown**: Handle shutdown signals properly