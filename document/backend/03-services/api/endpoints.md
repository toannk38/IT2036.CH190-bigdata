# API Endpoints Reference

## Base URL
```
Development: http://localhost:8000
Production: https://api.stockai.example.com
```

## Authentication
All endpoints require authentication via JWT token or API key.

```bash
# JWT Authentication
Authorization: Bearer <jwt_token>

# API Key Authentication  
X-API-Key: <api_key>
```

## Stock Information Endpoints

### GET /api/v1/stocks
List all available stocks with basic information.

**Parameters:**
- `limit` (optional): Number of results (default: 100, max: 1000)
- `offset` (optional): Pagination offset (default: 0)
- `exchange` (optional): Filter by exchange (HOSE, HNX, UPCOM)

**Response:**
```json
{
  "success": true,
  "data": {
    "stocks": [
      {
        "symbol": "VCB",
        "company_name": "Vietcombank",
        "exchange": "HOSE",
        "industry": "Banking",
        "last_price": 86.0,
        "change_percent": 2.5
      }
    ],
    "total": 1500,
    "limit": 100,
    "offset": 0
  },
  "message": "Success",
  "timestamp": "2024-12-04T10:00:00Z"
}
```

### GET /api/v1/stocks/{symbol}
Get detailed information for a specific stock.

**Parameters:**
- `symbol` (required): Stock symbol (e.g., VCB, VNM)

**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "VCB",
    "company_name": "Vietcombank",
    "exchange": "HOSE",
    "industry": "Banking",
    "market_cap": 850000000000,
    "outstanding_shares": 3500000000,
    "last_price": 86.0,
    "change": 2.1,
    "change_percent": 2.5,
    "volume": 1250000,
    "last_updated": "2024-12-04T09:15:00Z"
  }
}
```

### GET /api/v1/stocks/{symbol}/summary
Get comprehensive stock summary with AI analysis scores.

**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "VCB",
    "company_name": "Vietcombank",
    "last_price": 86.0,
    "change_percent": 2.5,
    "final_score": 0.75,
    "recommendation": "BUY",
    "confidence": 0.8,
    "technical_score": 0.7,
    "sentiment_score": 0.8,
    "risk_score": 0.3,
    "target_price": 92.0,
    "last_analysis": "2024-12-04T10:00:00Z"
  }
}
```

### GET /api/v1/stocks/{symbol}/prices
Get historical price data for a stock.

**Parameters:**
- `start_date` (optional): Start date (YYYY-MM-DD, default: 30 days ago)
- `end_date` (optional): End date (YYYY-MM-DD, default: today)
- `interval` (optional): Data interval (1D, 1H, 5m, default: 1D)

**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "VCB",
    "prices": [
      {
        "timestamp": "2024-12-04T09:15:00Z",
        "open": 85.5,
        "high": 86.2,
        "low": 85.0,
        "close": 86.0,
        "volume": 1250000
      }
    ],
    "count": 30
  }
}
```

## Analysis Endpoints

### GET /api/v1/stocks/{symbol}/analysis/technical
Get technical analysis results for a stock.

**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "VCB",
    "analysis_date": "2024-12-04T10:00:00Z",
    "technical_indicators": {
      "rsi_14": 65.5,
      "macd": 0.8,
      "macd_signal": 0.6,
      "bollinger_position": 0.7,
      "sma_20": 84.2,
      "volume_sma_ratio": 1.2
    },
    "patterns": {
      "hammer": false,
      "doji": true,
      "bullish_engulfing": false
    },
    "predictions": {
      "trend_direction": "bullish",
      "confidence": 0.75,
      "technical_score": 0.8,
      "price_targets": {
        "1_day": 86.5,
        "5_day": 88.0,
        "30_day": 92.0
      }
    }
  }
}
```

### GET /api/v1/stocks/{symbol}/analysis/sentiment
Get news sentiment analysis for a stock.

**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "VCB",
    "analysis_date": "2024-12-04T10:30:00Z",
    "overall_sentiment": {
      "sentiment": "positive",
      "confidence": 0.85,
      "impact_score": 0.7
    },
    "recent_news": [
      {
        "title": "VCB reports strong Q4 earnings",
        "sentiment": "positive",
        "confidence": 0.9,
        "published_at": "2024-12-04T08:30:00Z"
      }
    ],
    "key_insights": [
      "Strong earnings growth",
      "Positive market outlook",
      "Expansion plans announced"
    ]
  }
}
```

### GET /api/v1/stocks/{symbol}/analysis/combined
Get combined technical and sentiment analysis.

**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "VCB",
    "analysis_date": "2024-12-04T11:00:00Z",
    "scores": {
      "technical_score": 0.8,
      "sentiment_score": 0.7,
      "final_score": 0.75,
      "confidence": 0.72
    },
    "recommendation": {
      "action": "BUY",
      "strength": "strong",
      "target_price": 92.0,
      "stop_loss": 82.0
    },
    "summary": "Strong technical indicators combined with positive sentiment"
  }
}
```

## Alert Endpoints

### GET /api/v1/alerts
Get list of active alerts.

**Parameters:**
- `symbol` (optional): Filter by stock symbol
- `type` (optional): Filter by alert type (buy_signal, sell_signal, risk_alert)
- `priority` (optional): Filter by priority (low, medium, high, critical)

**Response:**
```json
{
  "success": true,
  "data": {
    "alerts": [
      {
        "alert_id": "uuid-789",
        "symbol": "VCB",
        "alert_type": "buy_signal",
        "priority": "high",
        "message": "Strong technical and sentiment alignment",
        "created_at": "2024-12-04T11:00:00Z",
        "data": {
          "final_score": 0.85,
          "recommendation": "BUY",
          "target_price": 92.0
        }
      }
    ],
    "count": 1
  }
}
```

### GET /api/v1/alerts/{symbol}
Get alerts for a specific stock symbol.

### POST /api/v1/alerts/subscribe
Subscribe to alerts for specific stocks or conditions.

**Request Body:**
```json
{
  "symbols": ["VCB", "VNM"],
  "alert_types": ["buy_signal", "sell_signal"],
  "min_score": 0.7,
  "notification_method": "email"
}
```

### DELETE /api/v1/alerts/{alert_id}
Unsubscribe from a specific alert.

## News Endpoints

### GET /api/v1/news
Get latest market news.

**Parameters:**
- `limit` (optional): Number of articles (default: 20, max: 100)
- `symbol` (optional): Filter by stock symbol
- `category` (optional): Filter by news category

**Response:**
```json
{
  "success": true,
  "data": {
    "news": [
      {
        "news_id": "hash_abc123",
        "symbol": "VCB",
        "title": "VCB announces dividend payment",
        "summary": "Vietcombank announces quarterly dividend...",
        "published_at": "2024-12-04T08:30:00Z",
        "source": "VnExpress",
        "sentiment": "positive",
        "impact_score": 0.7
      }
    ],
    "count": 20
  }
}
```

### GET /api/v1/news/{symbol}
Get news articles for a specific stock.

## Market Data Endpoints

### GET /api/v1/market/summary
Get overall market summary and statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "market_summary": {
      "total_stocks": 1500,
      "advancing": 850,
      "declining": 450,
      "unchanged": 200,
      "total_volume": 125000000,
      "total_value": 5500000000000
    },
    "top_gainers": [
      {
        "symbol": "VCB",
        "change_percent": 5.2,
        "last_price": 86.0
      }
    ],
    "top_losers": [
      {
        "symbol": "ABC",
        "change_percent": -3.1,
        "last_price": 25.5
      }
    ],
    "most_active": [
      {
        "symbol": "VNM",
        "volume": 2500000,
        "last_price": 75.0
      }
    ]
  }
}
```

## Error Responses

### Standard Error Format
```json
{
  "success": false,
  "error": {
    "code": "STOCK_NOT_FOUND",
    "message": "Stock symbol not found",
    "details": "Symbol 'INVALID' does not exist in our database"
  },
  "timestamp": "2024-12-04T10:00:00Z",
  "request_id": "uuid-456"
}
```

### Common Error Codes
- `STOCK_NOT_FOUND` (404): Stock symbol not found
- `INVALID_PARAMETERS` (400): Invalid request parameters
- `UNAUTHORIZED` (401): Authentication required
- `FORBIDDEN` (403): Insufficient permissions
- `RATE_LIMIT_EXCEEDED` (429): Too many requests
- `INTERNAL_ERROR` (500): Server error

## Rate Limiting

### Limits
- **Free Tier**: 60 requests per minute
- **Premium Tier**: 600 requests per minute
- **Enterprise**: Custom limits

### Headers
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1701691200
```

## Pagination

### Parameters
- `limit`: Number of items per page (max: 1000)
- `offset`: Number of items to skip

### Response Headers
```
X-Total-Count: 1500
X-Page-Count: 15
Link: <https://api.example.com/stocks?offset=100&limit=100>; rel="next"
```