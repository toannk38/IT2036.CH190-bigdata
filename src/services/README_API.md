# API Service

REST API for accessing Vietnam Stock AI Backend analysis data.

## Running the API Service

### Development Mode

```bash
# Run directly with uvicorn
python -m uvicorn src.services.api_service:app --reload --host 0.0.0.0 --port 8000

# Or run the module directly
python -m src.services.api_service
```

### Production Mode

```bash
# Run with multiple workers
uvicorn src.services.api_service:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Root Endpoint
- **GET** `/`
- Returns API information and available endpoints

### Stock Summary
- **GET** `/stock/{symbol}/summary`
- Returns comprehensive stock analysis including:
  - Current price data
  - AI/ML analysis (technical score, risk score, trend prediction)
  - LLM analysis (sentiment, summary, influence score)
  - Final recommendation score
  - Alerts

**Example:**
```bash
curl http://localhost:8000/stock/VNM/summary
```

### Alerts
- **GET** `/alerts?limit=50&offset=0`
- Returns active alerts sorted by priority and timestamp
- Supports pagination with `limit` and `offset` parameters

**Example:**
```bash
curl http://localhost:8000/alerts?limit=10&offset=0
```

### Historical Analysis
- **GET** `/stock/{symbol}/history?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- Returns time-series analysis data for specified date range
- Dates must be in ISO format (YYYY-MM-DD)

**Example:**
```bash
curl "http://localhost:8000/stock/VNM/history?start_date=2024-01-01&end_date=2024-01-31"
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Configuration

The API service uses environment variables from `.env`:

```bash
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=vietnam_stock_ai

# Other configurations are loaded from src/config.py
```

## Error Responses

All errors return a JSON response with:
```json
{
  "error": "ErrorType",
  "message": "Descriptive error message",
  "status_code": 400
}
```

Common status codes:
- `400`: Bad Request (invalid parameters)
- `404`: Not Found (symbol doesn't exist)
- `500`: Internal Server Error

## Testing

Run tests with:
```bash
# Unit tests
pytest tests/test_api_service.py -v

# Property-based tests
pytest tests/test_api_service_properties.py -v

# All API tests
pytest tests/test_api_service*.py -v
```
