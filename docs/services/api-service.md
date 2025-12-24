# API Service Documentation

## Overview

The API Service provides a RESTful interface for accessing Vietnam Stock AI analysis data. Built with FastAPI, it offers high-performance endpoints for retrieving stock summaries, alerts, and historical analysis data from the MongoDB database.

## Architecture

### Technology Stack
- **Framework**: FastAPI (Python)
- **Database**: MongoDB with PyMongo driver
- **Validation**: Pydantic models
- **Deployment**: Docker container with Uvicorn server

### Service Responsibilities
- Serve REST API endpoints for stock data access
- Validate input parameters and responses
- Handle database connections and queries
- Provide comprehensive error handling
- Format data for client consumption

## API Endpoints

### Health Check
**Endpoint**: `GET /health`
**Purpose**: Verify API and database connectivity

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "version": "1.0.0",
  "services": {
    "api": "healthy",
    "database": {
      "status": "healthy",
      "message": "Database connection successful"
    }
  }
}
```

### Root Information
**Endpoint**: `GET /`
**Purpose**: API information and available endpoints

**Response**:
```json
{
  "message": "Vietnam Stock AI Backend API",
  "version": "1.0.0",
  "endpoints": {
    "stock_summary": "/stock/{symbol}/summary",
    "alerts": "/alerts",
    "historical_analysis": "/stock/{symbol}/history",
    "active_symbols": "/symbols"
  }
}
```

### Stock Summary
**Endpoint**: `GET /stock/{symbol}/summary`
**Purpose**: Comprehensive stock analysis data

**Parameters**:
- `symbol` (path): Stock symbol code (e.g., "VIC", "VCB")

**Response Model**: `StockSummary`
```json
{
  "symbol": "VIC",
  "current_price": {
    "timestamp": "2024-01-01T12:00:00Z",
    "open": 85.5,
    "close": 87.2,
    "high": 88.0,
    "low": 85.0,
    "volume": 1250000
  },
  "ai_ml_analysis": {
    "timestamp": "2024-01-01T12:00:00Z",
    "trend_prediction": {
      "direction": "up",
      "confidence": 0.75,
      "predicted_price": 89.5
    },
    "risk_score": 0.3,
    "technical_score": 0.8,
    "indicators": {}
  },
  "llm_analysis": {
    "timestamp": "2024-01-01T12:00:00Z",
    "sentiment": {
      "overall": "positive",
      "score": 0.7,
      "confidence": 0.85
    },
    "summary": "Positive market sentiment...",
    "influence_score": 0.6,
    "articles_analyzed": 15
  },
  "final_score": 0.75,
  "recommendation": "BUY",
  "component_scores": {
    "technical_score": 0.8,
    "risk_score": 0.3,
    "sentiment_score": 0.7
  },
  "alerts": [
    {
      "type": "price_movement",
      "priority": "medium",
      "message": "Price increased by 5% in last hour"
    }
  ],
  "last_updated": "2024-01-01T12:00:00Z"
}
```

### Alerts
**Endpoint**: `GET /alerts`
**Purpose**: Active alerts sorted by priority and timestamp

**Query Parameters**:
- `limit` (optional): Maximum alerts to return (1-200, default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response Model**: `AlertResponse`
```json
{
  "alerts": [
    {
      "symbol": "VIC",
      "timestamp": "2024-01-01T12:00:00Z",
      "final_score": 0.75,
      "recommendation": "BUY",
      "type": "price_movement",
      "priority": "high",
      "message": "Significant price increase detected"
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 50
}
```

**Alert Sorting**:
1. Priority: high → medium → low
2. Timestamp: most recent first

### Historical Analysis
**Endpoint**: `GET /stock/{symbol}/history`
**Purpose**: Time-series analysis data for date range

**Parameters**:
- `symbol` (path): Stock symbol code
- `start_date` (query): Start date (YYYY-MM-DD format)
- `end_date` (query): End date (YYYY-MM-DD format)

**Response Model**: `HistoricalData`
```json
{
  "symbol": "VIC",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "data": [
    {
      "timestamp": "2024-01-01T12:00:00Z",
      "final_score": 0.75,
      "recommendation": "BUY",
      "components": {
        "technical_score": 0.8,
        "risk_score": 0.3,
        "sentiment_score": 0.7
      }
    }
  ],
  "total_points": 31
}
```

### Active Symbols
**Endpoint**: `GET /symbols`
**Purpose**: Get list of all active symbols with comprehensive information

**Response Model**: `SymbolsResponse`
```json
{
  "symbols": [
    {
      "symbol": "VIC",
      "organ_name": "Tập đoàn Vingroup - Công ty CP",
      "icb_name2": "Bất động sản",
      "icb_name3": "Bất động sản",
      "icb_name4": "Bất động sản",
      "com_type_code": "CT",
      "icb_code1": "8000",
      "icb_code2": "8600",
      "icb_code3": "8630",
      "icb_code4": "8633",
      "active": true,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    },
    {
      "symbol": "VCB",
      "organ_name": "Ngân hàng Thương mại Cổ phần Ngoại thương Việt Nam",
      "icb_name2": "Ngân hàng",
      "icb_name3": "Ngân hàng",
      "icb_name4": "Ngân hàng",
      "com_type_code": "NH",
      "icb_code1": "8301",
      "icb_code2": "8300",
      "icb_code3": "8350",
      "icb_code4": "8355",
      "active": true,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 50,
  "active_count": 30
}
```

**Features**:
- Returns all active symbols (where `active` field is `true`)
- Includes comprehensive company information:
  - Symbol code and company name
  - Industry Classification Benchmark (ICB) codes and names
  - Company type code (CT=Company, NH=Bank, CK=Securities)
  - Creation and update timestamps
- Symbols are sorted alphabetically by symbol code
- Provides total count and active count for reference

## Data Models

### Core Models

**PriceData**
```python
class PriceData(BaseModel):
    timestamp: str  # ISO format
    open: float
    close: float
    high: float
    low: float
    volume: int
```

**ComponentScores**
```python
class ComponentScores(BaseModel):
    technical_score: float
    risk_score: float
    sentiment_score: float
```

**Alert**
```python
class Alert(BaseModel):
    type: str
    priority: str  # "high", "medium", "low"
    message: str
```

**SymbolInfo**
```python
class SymbolInfo(BaseModel):
    symbol: str
    organ_name: str
    icb_name2: Optional[str] = None
    icb_name3: Optional[str] = None
    icb_name4: Optional[str] = None
    com_type_code: Optional[str] = None
    icb_code1: Optional[str] = None
    icb_code2: Optional[str] = None
    icb_code3: Optional[str] = None
    icb_code4: Optional[str] = None
    active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
```

**SymbolsResponse**
```python
class SymbolsResponse(BaseModel):
    symbols: List[SymbolInfo]
    total: int
    active_count: int
```

## Database Integration

### Collections Used
- `symbols`: Active stock symbols
- `price_history`: Current price data
- `ai_analysis`: AI/ML analysis results
- `llm_analysis`: LLM sentiment analysis
- `final_scores`: Combined analysis scores

### Query Patterns

**Latest Data Queries**:
```python
# Get most recent price
price_collection.find_one(
    {'symbol': symbol},
    sort=[('timestamp', -1)]
)

# Get latest analysis
ai_analysis_collection.find_one(
    {'symbol': symbol},
    sort=[('timestamp', -1)]
)
```

**Historical Data Queries**:
```python
# Date range query (supports both epoch and ISO timestamps)
final_scores_collection.find({
    'symbol': symbol,
    '$or': [
        {'timestamp': {'$gte': start_epoch, '$lte': end_epoch}},
        {'timestamp': {'$gte': start_iso, '$lte': end_iso}}
    ]
})
```

**Alert Aggregation**:
```python
# Complex aggregation for alert sorting
pipeline = [
    {'$match': {'alerts': {'$exists': True, '$ne': []}}},
    {'$unwind': '$alerts'},
    {'$addFields': {'priority_order': priority_mapping}},
    {'$sort': {'priority_order': 1, 'timestamp': -1}}
]
```

## Configuration

### Environment Variables
```bash
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=vietnam_stock_ai

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Logging
LOG_LEVEL=INFO
```

### Docker Configuration
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
EXPOSE 8000

CMD ["uvicorn", "src.services.api_service:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Error Handling

### HTTP Status Codes
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `404`: Not Found (symbol not found)
- `500`: Internal Server Error

### Error Response Format
```json
{
  "error": "HTTPException",
  "message": "Symbol 'INVALID' not found",
  "status_code": 404
}
```

### Exception Handling
```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )
```

## Performance Optimization

### Database Indexing
```javascript
// Recommended MongoDB indexes
db.price_history.createIndex({"symbol": 1, "timestamp": -1})
db.ai_analysis.createIndex({"symbol": 1, "timestamp": -1})
db.llm_analysis.createIndex({"symbol": 1, "timestamp": -1})
db.final_scores.createIndex({"symbol": 1, "timestamp": -1})
db.final_scores.createIndex({"alerts": 1, "timestamp": -1})
```

### Caching Strategy
- Consider Redis for frequently accessed data
- Cache latest analysis results
- Implement cache invalidation on data updates

### Query Optimization
- Use projection to limit returned fields
- Implement pagination for large result sets
- Optimize aggregation pipelines

## Deployment

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Start API server
uvicorn src.services.api_service:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment
```bash
# Build image
docker build -f docker/Dockerfile.api -t vietnam-stock-api .

# Run container
docker run -p 8000:8000 \
  -e MONGODB_URI=mongodb://mongodb:27017 \
  vietnam-stock-api
```

### Production Considerations
- Use multiple worker processes
- Configure reverse proxy (nginx)
- Implement rate limiting
- Set up monitoring and logging
- Use environment-specific configurations

## Testing

### Unit Tests
```python
# Test API endpoints
def test_stock_summary():
    response = client.get("/stock/VIC/summary")
    assert response.status_code == 200
    assert response.json()["symbol"] == "VIC"

def test_alerts_pagination():
    response = client.get("/alerts?limit=10&offset=0")
    assert response.status_code == 200
    assert len(response.json()["alerts"]) <= 10
```

### Integration Tests
- Test database connectivity
- Verify data retrieval accuracy
- Test error handling scenarios
- Validate response schemas

## Monitoring

### Health Monitoring
- `/health` endpoint for service status
- Database connectivity checks
- Response time monitoring

### Logging
```python
# Structured logging with context
logger.info(
    "Stock summary retrieved",
    context={'symbol': symbol, 'response_time': elapsed}
)
```

### Metrics
- Request count and response times
- Error rates by endpoint
- Database query performance
- Active connections

## Security

### Input Validation
- Pydantic models for request/response validation
- SQL injection prevention (NoSQL)
- Parameter sanitization

### Access Control
- Consider API key authentication for production
- Rate limiting per client
- CORS configuration for web clients

### Data Security
- No sensitive data exposure
- Public stock information only
- Secure database connections

## API Documentation

### Interactive Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI spec: `http://localhost:8000/openapi.json`

### Client Libraries
Consider generating client libraries for:
- Python (requests-based)
- JavaScript/TypeScript
- Mobile applications

## Troubleshooting

### Common Issues

**1. Database Connection Errors**
```bash
# Check MongoDB connectivity
docker logs stock-ai-mongodb
mongosh --host localhost:27017
```

**2. Symbol Not Found Errors**
```bash
# Verify symbols in database
mongosh vietnam_stock_ai --eval "db.symbols.find()"
```

**3. Performance Issues**
- Check database indexes
- Monitor query execution times
- Review aggregation pipeline efficiency

**4. Memory Issues**
- Limit result set sizes
- Implement proper pagination
- Monitor memory usage

### Debug Mode
```bash
# Run with debug logging
LOG_LEVEL=DEBUG uvicorn src.services.api_service:app --reload
```