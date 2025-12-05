# API Usage Examples

## Authentication Examples

### JWT Token Authentication

#### Login and Get Token
```bash
# Login request
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "password123"
  }'

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwidXNlcl9pZCI6IjEyMyIsInJvbGUiOiJwcmVtaXVtIiwiZXhwIjoxNzAxNjkzNjAwfQ.signature",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "username": "user@example.com",
    "role": "premium"
  }
}
```

#### Using JWT Token
```bash
# Store token in variable
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Use token in API calls
curl -X GET "http://localhost:8000/api/v1/stocks/VCB/summary" \
  -H "Authorization: Bearer $TOKEN"
```

### API Key Authentication

#### Generate API Key
```bash
# Generate API key (requires JWT token)
curl -X POST "http://localhost:8000/api/v1/auth/api-keys" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Trading Bot",
    "description": "Automated trading application"
  }'

# Response
{
  "api_key": "<your_api_key_here>",
  "name": "My Trading Bot",
  "created_at": "2024-12-04T10:00:00Z",
  "permissions": ["read:stocks", "read:analysis", "write:alerts"]
}
```

#### Using API Key
```bash
# Store API key
API_KEY="<your_api_key_here>"

# Use API key in requests
curl -X GET "http://localhost:8000/api/v1/stocks/VCB" \
  -H "Authorization: Bearer $API_KEY"
```

## Stock Data Examples

### Get Stock List
```bash
# Get all stocks with pagination
curl "http://localhost:8000/api/v1/stocks?limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN"

# Filter by exchange
curl "http://localhost:8000/api/v1/stocks?exchange=HOSE&limit=50" \
  -H "Authorization: Bearer $TOKEN"

# Response
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
        "change_percent": 2.5,
        "volume": 1250000
      },
      {
        "symbol": "VNM",
        "company_name": "Vinamilk",
        "exchange": "HOSE", 
        "industry": "Food & Beverage",
        "last_price": 75.0,
        "change_percent": -1.2,
        "volume": 890000
      }
    ],
    "total": 1500,
    "limit": 10,
    "offset": 0
  }
}
```

### Get Stock Details
```bash
# Get detailed stock information
curl "http://localhost:8000/api/v1/stocks/VCB" \
  -H "Authorization: Bearer $TOKEN"

# Response
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
    "avg_volume_30d": 1100000,
    "last_updated": "2024-12-04T09:15:00Z",
    "trading_status": "active"
  }
}
```

### Get Stock Summary with AI Scores
```bash
# Get comprehensive stock summary
curl "http://localhost:8000/api/v1/stocks/VCB/summary" \
  -H "Authorization: Bearer $TOKEN"

# Response
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
    "scores": {
      "technical_score": 0.7,
      "sentiment_score": 0.8,
      "risk_score": 0.3
    },
    "targets": {
      "target_price": 92.0,
      "stop_loss": 82.0,
      "time_horizon": "30_days"
    },
    "last_analysis": "2024-12-04T10:00:00Z"
  }
}
```

### Get Price History
```bash
# Get 30 days of daily prices
curl "http://localhost:8000/api/v1/stocks/VCB/prices?start_date=2024-11-04&end_date=2024-12-04&interval=1D" \
  -H "Authorization: Bearer $TOKEN"

# Get intraday prices (1 hour intervals)
curl "http://localhost:8000/api/v1/stocks/VCB/prices?start_date=2024-12-04&interval=1H" \
  -H "Authorization: Bearer $TOKEN"

# Response
{
  "success": true,
  "data": {
    "symbol": "VCB",
    "interval": "1D",
    "prices": [
      {
        "timestamp": "2024-12-04T00:00:00Z",
        "open": 85.5,
        "high": 86.2,
        "low": 85.0,
        "close": 86.0,
        "volume": 1250000,
        "value": 107250000000
      },
      {
        "timestamp": "2024-12-03T00:00:00Z",
        "open": 84.0,
        "high": 85.8,
        "low": 83.5,
        "close": 85.5,
        "volume": 980000,
        "value": 83790000000
      }
    ],
    "count": 30,
    "start_date": "2024-11-04",
    "end_date": "2024-12-04"
  }
}
```

## Analysis Examples

### Technical Analysis
```bash
# Get technical analysis for a stock
curl "http://localhost:8000/api/v1/stocks/VCB/analysis/technical" \
  -H "Authorization: Bearer $TOKEN"

# Response
{
  "success": true,
  "data": {
    "symbol": "VCB",
    "analysis_date": "2024-12-04T10:00:00Z",
    "technical_indicators": {
      "rsi_14": 65.5,
      "macd": 0.8,
      "macd_signal": 0.6,
      "macd_histogram": 0.2,
      "bollinger_upper": 87.5,
      "bollinger_middle": 85.0,
      "bollinger_lower": 82.5,
      "bollinger_position": 0.7,
      "sma_20": 84.2,
      "ema_12": 85.1,
      "volume_sma_ratio": 1.2,
      "atr_14": 2.1
    },
    "patterns": {
      "hammer": false,
      "doji": true,
      "bullish_engulfing": false,
      "bearish_engulfing": false,
      "shooting_star": false
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
    },
    "signals": {
      "rsi_signal": "neutral",
      "macd_signal": "bullish",
      "bollinger_signal": "bullish"
    }
  }
}
```

### Sentiment Analysis
```bash
# Get news sentiment analysis
curl "http://localhost:8000/api/v1/stocks/VCB/analysis/sentiment" \
  -H "Authorization: Bearer $TOKEN"

# Response
{
  "success": true,
  "data": {
    "symbol": "VCB",
    "analysis_date": "2024-12-04T10:30:00Z",
    "overall_sentiment": {
      "sentiment": "positive",
      "confidence": 0.85,
      "impact_score": 0.7,
      "trend": "improving"
    },
    "recent_news": [
      {
        "news_id": "hash_abc123",
        "title": "VCB reports strong Q4 earnings",
        "sentiment": "positive",
        "confidence": 0.9,
        "impact_score": 0.8,
        "published_at": "2024-12-04T08:30:00Z",
        "source": "VnExpress"
      },
      {
        "news_id": "hash_def456", 
        "title": "Banking sector outlook remains positive",
        "sentiment": "positive",
        "confidence": 0.7,
        "impact_score": 0.5,
        "published_at": "2024-12-03T14:20:00Z",
        "source": "CafeF"
      }
    ],
    "key_insights": [
      "Strong earnings growth reported",
      "Positive market outlook for banking sector",
      "Expansion plans announced for 2025"
    ],
    "sentiment_history": {
      "7_days": 0.6,
      "30_days": 0.5,
      "90_days": 0.4
    }
  }
}
```

### Combined Analysis
```bash
# Get combined technical and sentiment analysis
curl "http://localhost:8000/api/v1/stocks/VCB/analysis/combined" \
  -H "Authorization: Bearer $TOKEN"

# Response
{
  "success": true,
  "data": {
    "symbol": "VCB",
    "analysis_date": "2024-12-04T11:00:00Z",
    "scores": {
      "technical_score": 0.8,
      "sentiment_score": 0.7,
      "final_score": 0.75,
      "confidence": 0.72,
      "risk_score": 0.3
    },
    "recommendation": {
      "action": "BUY",
      "strength": "strong",
      "target_price": 92.0,
      "stop_loss": 82.0,
      "time_horizon": "medium_term",
      "position_size": "moderate"
    },
    "summary": "Strong technical indicators combined with positive sentiment suggest bullish outlook",
    "key_factors": [
      "RSI showing momentum without being overbought",
      "MACD bullish crossover confirmed",
      "Positive earnings news driving sentiment",
      "Volume supporting price movement"
    ],
    "risks": [
      "General market volatility",
      "Banking sector regulatory changes"
    ]
  }
}
```

## Alert Examples

### Get Active Alerts
```bash
# Get all active alerts
curl "http://localhost:8000/api/v1/alerts" \
  -H "Authorization: Bearer $TOKEN"

# Filter alerts by symbol
curl "http://localhost:8000/api/v1/alerts?symbol=VCB" \
  -H "Authorization: Bearer $TOKEN"

# Filter by alert type and priority
curl "http://localhost:8000/api/v1/alerts?type=buy_signal&priority=high" \
  -H "Authorization: Bearer $TOKEN"

# Response
{
  "success": true,
  "data": {
    "alerts": [
      {
        "alert_id": "uuid-789",
        "symbol": "VCB",
        "alert_type": "buy_signal",
        "priority": "high",
        "message": "Strong technical and sentiment alignment detected",
        "created_at": "2024-12-04T11:00:00Z",
        "data": {
          "final_score": 0.85,
          "recommendation": "BUY",
          "target_price": 92.0,
          "confidence": 0.8
        },
        "status": "active"
      }
    ],
    "count": 1,
    "total_active": 15
  }
}
```

### Subscribe to Alerts
```bash
# Subscribe to buy/sell signals for specific stocks
curl -X POST "http://localhost:8000/api/v1/alerts/subscribe" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["VCB", "VNM", "VIC"],
    "alert_types": ["buy_signal", "sell_signal"],
    "min_score": 0.7,
    "min_confidence": 0.6,
    "notification_methods": ["email", "webhook"],
    "webhook_url": "https://myapp.com/webhooks/alerts"
  }'

# Response
{
  "success": true,
  "data": {
    "subscription_id": "sub_abc123",
    "symbols": ["VCB", "VNM", "VIC"],
    "alert_types": ["buy_signal", "sell_signal"],
    "filters": {
      "min_score": 0.7,
      "min_confidence": 0.6
    },
    "created_at": "2024-12-04T11:00:00Z",
    "status": "active"
  }
}
```

## News Examples

### Get Latest News
```bash
# Get latest market news
curl "http://localhost:8000/api/v1/news?limit=10" \
  -H "Authorization: Bearer $TOKEN"

# Get news for specific stock
curl "http://localhost:8000/api/v1/news?symbol=VCB&limit=5" \
  -H "Authorization: Bearer $TOKEN"

# Filter by category
curl "http://localhost:8000/api/v1/news?category=earnings&limit=20" \
  -H "Authorization: Bearer $TOKEN"

# Response
{
  "success": true,
  "data": {
    "news": [
      {
        "news_id": "hash_abc123",
        "symbol": "VCB",
        "title": "VCB announces Q4 dividend payment",
        "summary": "Vietcombank announces quarterly dividend of 1,500 VND per share...",
        "content": "Full article content here...",
        "published_at": "2024-12-04T08:30:00Z",
        "source": "VnExpress",
        "category": "corporate_action",
        "sentiment": "positive",
        "impact_score": 0.7,
        "url": "https://vnexpress.net/..."
      }
    ],
    "count": 10,
    "total_available": 150
  }
}
```

## Market Data Examples

### Market Summary
```bash
# Get overall market summary
curl "http://localhost:8000/api/v1/market/summary" \
  -H "Authorization: Bearer $TOKEN"

# Response
{
  "success": true,
  "data": {
    "market_summary": {
      "date": "2024-12-04",
      "total_stocks": 1500,
      "advancing": 850,
      "declining": 450,
      "unchanged": 200,
      "total_volume": 125000000,
      "total_value": 5500000000000,
      "market_trend": "bullish"
    },
    "indices": {
      "vn_index": {
        "value": 1250.5,
        "change": 15.2,
        "change_percent": 1.23
      },
      "hnx_index": {
        "value": 245.8,
        "change": -2.1,
        "change_percent": -0.85
      }
    },
    "top_gainers": [
      {
        "symbol": "VCB",
        "change_percent": 5.2,
        "last_price": 86.0,
        "volume": 1250000
      }
    ],
    "top_losers": [
      {
        "symbol": "ABC",
        "change_percent": -3.1,
        "last_price": 25.5,
        "volume": 890000
      }
    ],
    "most_active": [
      {
        "symbol": "VNM",
        "volume": 2500000,
        "last_price": 75.0,
        "value": 187500000000
      }
    ]
  }
}
```

## Error Handling Examples

### Common Error Responses
```bash
# Stock not found
curl "http://localhost:8000/api/v1/stocks/INVALID" \
  -H "Authorization: Bearer $TOKEN"

# Response (404)
{
  "success": false,
  "error": {
    "code": "STOCK_NOT_FOUND",
    "message": "Stock symbol not found",
    "details": "Symbol 'INVALID' does not exist in our database"
  },
  "timestamp": "2024-12-04T10:00:00Z",
  "request_id": "req_abc123"
}

# Unauthorized access
curl "http://localhost:8000/api/v1/stocks/VCB"
# No Authorization header

# Response (401)
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required",
    "details": "Missing or invalid authorization header"
  },
  "timestamp": "2024-12-04T10:00:00Z",
  "request_id": "req_def456"
}

# Rate limit exceeded
# Response (429)
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests",
    "details": "Rate limit of 60 requests per minute exceeded"
  },
  "timestamp": "2024-12-04T10:00:00Z",
  "request_id": "req_ghi789",
  "retry_after": 45
}
```

## Batch Operations Examples

### Multiple Stock Analysis
```bash
# Get analysis for multiple stocks
curl -X POST "http://localhost:8000/api/v1/stocks/batch/analysis" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["VCB", "VNM", "VIC", "MSN"],
    "analysis_types": ["technical", "sentiment"],
    "include_scores": true
  }'

# Response
{
  "success": true,
  "data": {
    "results": [
      {
        "symbol": "VCB",
        "technical_score": 0.8,
        "sentiment_score": 0.7,
        "final_score": 0.75,
        "recommendation": "BUY"
      },
      {
        "symbol": "VNM", 
        "technical_score": 0.6,
        "sentiment_score": 0.5,
        "final_score": 0.55,
        "recommendation": "WATCH"
      }
    ],
    "processed": 4,
    "failed": 0
  }
}
```