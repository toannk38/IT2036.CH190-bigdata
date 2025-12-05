# Database Design

## Overview

Database architecture using MongoDB as primary storage and Redis for caching, designed to support the data models established in the existing code.

## MongoDB Schema Design

### Collections Overview

Based on the architecture plan and existing data models:

```javascript
// Database: stock_ai
Collections:
├── stocks           // Stock metadata and current info
├── price_history    // Historical price data  
├── news            // News articles
├── ai_analysis     // AI/ML analysis results
├── llm_analysis    // LLM sentiment analysis
└── final_scores    // Aggregated scores and recommendations
```

### 1. stocks Collection

**Purpose**: Store stock metadata and current information
**Based on**: `StockListing` model from `libs/vnstock/models.py`

```javascript
{
  "_id": ObjectId("..."),
  "symbol": "VCB",                    // From StockListing.symbol
  "organ_name": "Vietcombank",        // From StockListing.organ_name  
  "company_name": "Vietcombank",      // Extended field
  "exchange": "HOSE",                 // Extended field
  "industry": "Banking",              // From StockListing.icb_name3
  "icb_name2": "Finance",            // From StockListing.icb_name2
  "icb_name4": "Banks",              // From StockListing.icb_name4
  "last_price": 86.0,               // Current price
  "last_update": ISODate("2024-12-04T09:15:00Z"),
  "market_cap": 850000000000,        // Market capitalization
  "outstanding_shares": 3500000000,   // Number of shares
  "status": "active",                // Trading status
  "created_at": ISODate("2024-01-01T00:00:00Z"),
  "updated_at": ISODate("2024-12-04T09:15:00Z")
}
```

**Indexes**:
```javascript
db.stocks.createIndex({ "symbol": 1 }, { unique: true })
db.stocks.createIndex({ "exchange": 1, "industry": 1 })
db.stocks.createIndex({ "last_update": -1 })
db.stocks.createIndex({ "market_cap": -1 })
```

### 2. price_history Collection

**Purpose**: Store historical price data
**Based on**: Normalized data from `DataNormalizer.normalize_price_data()`

```javascript
{
  "_id": ObjectId("..."),
  "symbol": "VCB",                   // From normalized data
  "timestamp": ISODate("2024-12-04T09:15:00Z"), // From normalized time
  "open": 85.5,                      // From normalized open
  "high": 86.2,                      // From normalized high
  "low": 85.0,                       // From normalized low
  "close": 86.0,                     // From normalized close
  "volume": 1250000,                 // From normalized volume
  "value": 107250000000,             // Trading value (calculated)
  "change": 0.5,                     // Price change
  "change_percent": 0.58,            // Percentage change
  "source": "vnstock",               // Data source
  "collected_at": ISODate("2024-12-04T09:15:30Z"), // From normalized collected_at
  "created_at": ISODate("2024-12-04T09:15:30Z")
}
```

**Indexes**:
```javascript
db.price_history.createIndex({ "symbol": 1, "timestamp": -1 })
db.price_history.createIndex({ "timestamp": -1 })
db.price_history.createIndex({ "symbol": 1, "timestamp": 1 }, 
  { expireAfterSeconds: 7776000 }) // 90 days TTL
```

### 3. news Collection

**Purpose**: Store news articles
**Based on**: `StockNews` model and planned news normalization

```javascript
{
  "_id": ObjectId("..."),
  "news_id": "hash_abc123",          // MD5 hash for deduplication
  "symbol": "VCB",                   // From StockNews.symbol
  "title": "VCB công bố kế hoạch tăng vốn", // From StockNews.title
  "content": "Nội dung tin tức đầy đủ...",   // Full article content
  "summary": "Tóm tắt ngắn gọn...",          // Auto-generated summary
  "source": "VnExpress",             // From StockNews.source
  "source_url": "https://...",       // From StockNews.url
  "published_at": ISODate("2024-12-04T08:30:00Z"), // From StockNews.publish_date
  "collected_at": ISODate("2024-12-04T09:00:00Z"),  // Collection timestamp
  "category": "corporate_action",     // News category
  "tags": ["tăng vốn", "cổ phiếu"],  // Extracted tags
  "language": "vi",                   // Language detection
  "sentiment": null,                  // Will be populated by LLM analysis
  "impact_score": null,              // Will be populated by LLM analysis
  "processed": false,                // Processing status
  "created_at": ISODate("2024-12-04T09:00:30Z"),
  "updated_at": ISODate("2024-12-04T09:00:30Z")
}
```

**Indexes**:
```javascript
db.news.createIndex({ "news_id": 1 }, { unique: true })
db.news.createIndex({ "symbol": 1, "published_at": -1 })
db.news.createIndex({ "processed": 1, "published_at": -1 })
db.news.createIndex({ "published_at": -1 })
db.news.createIndex({ "category": 1, "symbol": 1 })
```

### 4. ai_analysis Collection

**Purpose**: Store AI/ML technical analysis results

```javascript
{
  "_id": ObjectId("..."),
  "symbol": "VCB",
  "analysis_date": ISODate("2024-12-04T10:00:00Z"),
  "data_period": {
    "start_date": ISODate("2024-11-04T00:00:00Z"),
    "end_date": ISODate("2024-12-04T00:00:00Z"),
    "days": 30
  },
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
    "trend_direction": "bullish",      // bullish/bearish/neutral
    "confidence": 0.75,               // 0-1 confidence score
    "risk_score": 0.3,                // 0-1 risk assessment
    "technical_score": 0.8,           // 0-1 technical strength
    "price_target": {
      "1_day": 86.5,
      "5_day": 88.0,
      "30_day": 92.0
    }
  },
  "model_versions": {
    "arima": "v1.0",
    "lstm": "v1.2",
    "transformer": "v1.1",
    "catboost": "v2.0"
  },
  "created_at": ISODate("2024-12-04T10:00:00Z")
}
```

**Indexes**:
```javascript
db.ai_analysis.createIndex({ "symbol": 1, "analysis_date": -1 })
db.ai_analysis.createIndex({ "analysis_date": -1 })
db.ai_analysis.createIndex({ "predictions.technical_score": -1 })
```

### 5. llm_analysis Collection

**Purpose**: Store LLM news sentiment analysis results

```javascript
{
  "_id": ObjectId("..."),
  "news_id": "hash_abc123",          // Reference to news collection
  "symbol": "VCB",
  "analysis_date": ISODate("2024-12-04T10:30:00Z"),
  "sentiment": {
    "sentiment": "positive",          // positive/negative/neutral
    "confidence": 0.85,              // 0-1 confidence score
    "impact_score": 0.7,             // 0-1 market impact assessment
    "urgency": "medium"              // low/medium/high
  },
  "insights": [
    "Strong Q4 earnings report",
    "Positive market outlook",
    "Expansion plans announced"
  ],
  "summary": "Company reports strong Q4 results with 15% revenue growth...",
  "key_entities": [
    "Q4 earnings",
    "revenue growth", 
    "market expansion"
  ],
  "risk_factors": [
    "Market volatility",
    "Regulatory changes"
  ],
  "llm_metadata": {
    "model": "gpt-4",
    "version": "2024-11-01",
    "tokens_used": 1250,
    "processing_time": 2.3
  },
  "created_at": ISODate("2024-12-04T10:30:00Z")
}
```

**Indexes**:
```javascript
db.llm_analysis.createIndex({ "news_id": 1 }, { unique: true })
db.llm_analysis.createIndex({ "symbol": 1, "analysis_date": -1 })
db.llm_analysis.createIndex({ "sentiment.sentiment": 1, "symbol": 1 })
db.llm_analysis.createIndex({ "sentiment.impact_score": -1 })
```

### 6. final_scores Collection

**Purpose**: Store aggregated final scores and recommendations

```javascript
{
  "_id": ObjectId("..."),
  "symbol": "VCB",
  "score_date": ISODate("2024-12-04T11:00:00Z"),
  "scores": {
    "technical_score": 0.8,          // From ai_analysis
    "sentiment_score": 0.7,          // From llm_analysis
    "final_score": 0.75,             // Weighted combination
    "confidence": 0.72               // Minimum of component confidences
  },
  "recommendation": {
    "action": "BUY",                 // BUY/SELL/WATCH
    "strength": "strong",            // weak/moderate/strong
    "time_horizon": "short_term",    // short_term/medium_term/long_term
    "target_price": 92.0,
    "stop_loss": 82.0
  },
  "weights": {
    "technical": 0.6,               // Weight for technical analysis
    "sentiment": 0.4                // Weight for sentiment analysis
  },
  "alerts": [
    {
      "type": "buy_signal",
      "priority": "high",
      "message": "Strong technical and sentiment alignment",
      "created_at": ISODate("2024-12-04T11:00:00Z")
    }
  ],
  "metadata": {
    "ai_analysis_id": ObjectId("..."),
    "llm_analysis_ids": [ObjectId("..."), ObjectId("...")],
    "news_count": 3,
    "data_quality": 0.95
  },
  "created_at": ISODate("2024-12-04T11:00:00Z")
}
```

**Indexes**:
```javascript
db.final_scores.createIndex({ "symbol": 1, "score_date": -1 })
db.final_scores.createIndex({ "scores.final_score": -1 })
db.final_scores.createIndex({ "recommendation.action": 1, "scores.final_score": -1 })
db.final_scores.createIndex({ "score_date": -1 })
```

## Redis Caching Strategy

### Cache Keys Pattern
```
stock_ai:{type}:{identifier}:{ttl}
```

### Cache Types

#### 1. API Response Caching
```redis
# Stock summary cache (5 minutes)
stock_ai:summary:VCB:300 → JSON summary data

# Analysis results cache (15 minutes)  
stock_ai:analysis:VCB:900 → JSON analysis data

# Stock list cache (1 hour)
stock_ai:stocks:all:3600 → JSON stock list
```

#### 2. Session Caching
```redis
# User sessions (24 hours)
stock_ai:session:{user_id}:86400 → Session data

# API rate limiting (1 minute)
stock_ai:ratelimit:{api_key}:60 → Request count
```

#### 3. Computed Results Caching
```redis
# Technical indicators cache (30 minutes)
stock_ai:indicators:VCB:1800 → Computed indicators

# News sentiment cache (2 hours)
stock_ai:sentiment:VCB:7200 → Aggregated sentiment
```

## Data Retention Policies

### MongoDB TTL Indexes
```javascript
// Price history: 90 days retention
db.price_history.createIndex(
  { "created_at": 1 }, 
  { expireAfterSeconds: 7776000 }
)

// News: 1 year retention
db.news.createIndex(
  { "created_at": 1 }, 
  { expireAfterSeconds: 31536000 }
)

// Analysis results: 6 months retention
db.ai_analysis.createIndex(
  { "created_at": 1 }, 
  { expireAfterSeconds: 15552000 }
)
```

### Archive Strategy
- **Hot Data**: Last 30 days in primary collections
- **Warm Data**: 30-90 days with reduced indexes
- **Cold Data**: >90 days archived to separate collections

## Database Performance Optimization

### Sharding Strategy
```javascript
// Shard by symbol for even distribution
sh.shardCollection("stock_ai.price_history", { "symbol": 1, "timestamp": 1 })
sh.shardCollection("stock_ai.news", { "symbol": 1, "published_at": 1 })
```

### Read Preferences
- **Primary**: Write operations, real-time data
- **Secondary**: Analytics queries, reporting
- **Nearest**: Geographically distributed reads

### Connection Pooling
```python
# MongoDB connection configuration
client = MongoClient(
    host=MONGODB_URI,
    maxPoolSize=50,
    minPoolSize=10,
    maxIdleTimeMS=30000,
    serverSelectionTimeoutMS=5000
)
```

## Data Consistency

### Write Concerns
```python
# Critical data (prices, scores)
write_concern = WriteConcern(w="majority", j=True)

# Non-critical data (logs, metrics)
write_concern = WriteConcern(w=1, j=False)
```

### Read Concerns
```python
# Real-time data
read_concern = ReadConcern("majority")

# Analytics data
read_concern = ReadConcern("local")
```

## Backup and Recovery

### Backup Strategy
- **Full Backup**: Daily at 2 AM UTC
- **Incremental**: Every 6 hours
- **Point-in-Time**: Oplog replay capability
- **Cross-Region**: Replicated to secondary datacenter

### Recovery Procedures
1. **Data Corruption**: Restore from latest backup
2. **Partial Loss**: Replay oplog from last checkpoint
3. **Complete Loss**: Full restore + data reconciliation