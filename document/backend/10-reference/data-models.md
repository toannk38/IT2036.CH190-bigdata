# Data Models Reference

## Overview

This document describes all data models used in the Stock AI Backend System, based on the actual implementation in the codebase.

## Core Data Models

### StockPrice ✅

**Location**: `libs/vnstock/models.py`

```python
@dataclass
class StockPrice:
    symbol: str
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
```

**Description**: Represents a single price record for a stock at a specific time.

**Fields**:
- `symbol` (str): Stock symbol (e.g., "VCB", "VNM")
- `time` (datetime): Timestamp of the price record
- `open` (float): Opening price
- `high` (float): Highest price during the period
- `low` (float): Lowest price during the period  
- `close` (float): Closing price
- `volume` (int): Trading volume

**Usage Example**:
```python
price = StockPrice(
    symbol="VCB",
    time=datetime(2024, 12, 4, 9, 15),
    open=85.5,
    high=86.2,
    low=85.0,
    close=86.0,
    volume=1250000
)
```

### StockNews ✅

**Location**: `libs/vnstock/models.py`

```python
@dataclass
class StockNews:
    symbol: str
    title: str
    publish_date: datetime
    source: str
    url: Optional[str] = None
```

**Description**: Represents a news article related to a specific stock.

**Fields**:
- `symbol` (str): Related stock symbol
- `title` (str): News article title
- `publish_date` (datetime): Publication timestamp
- `source` (str): News source name
- `url` (Optional[str]): URL to full article (if available)

**Usage Example**:
```python
news = StockNews(
    symbol="VNM",
    title="VNM công bố kế hoạch tăng vốn điều lệ",
    publish_date=datetime(2024, 12, 4, 8, 30),
    source="VnExpress",
    url="https://vnexpress.net/..."
)
```

### StockListing ✅

**Location**: `libs/vnstock/models.py`

```python
@dataclass
class StockListing:
    symbol: str
    organ_name: str
    icb_name3: Optional[str] = None
    icb_name2: Optional[str] = None
    icb_name4: Optional[str] = None
```

**Description**: Represents basic information about a listed stock.

**Fields**:
- `symbol` (str): Stock trading symbol
- `organ_name` (str): Company name
- `icb_name3` (Optional[str]): ICB industry classification level 3
- `icb_name2` (Optional[str]): ICB industry classification level 2
- `icb_name4` (Optional[str]): ICB industry classification level 4

**Usage Example**:
```python
listing = StockListing(
    symbol="VCB",
    organ_name="Vietcombank",
    icb_name3="Banking",
    icb_name2="Finance",
    icb_name4="Banks"
)
```

## Data Processing Models

### Normalized Price Data ✅

**Location**: `services/data_collector/src/processors/data_normalizer.py`

**Format**: Dictionary representation used for Kafka messages

```python
{
    'symbol': str,           # Stock symbol
    'time': str,            # ISO format timestamp
    'open': float,          # Opening price
    'high': float,          # High price
    'low': float,           # Low price
    'close': float,         # Closing price
    'volume': int,          # Trading volume
    'collected_at': str     # Collection timestamp (ISO format)
}
```

**Example**:
```json
{
    "symbol": "VCB",
    "time": "2024-12-04T09:15:00+07:00",
    "open": 85.5,
    "high": 86.2,
    "low": 85.0,
    "close": 86.0,
    "volume": 1250000,
    "collected_at": "2024-12-04T09:15:30.123456"
}
```

**Normalization Rules**:
- Timestamps converted to ISO 8601 format
- Prices converted to float with proper precision
- Volume converted to integer
- Collection timestamp added for tracking

## Exception Models ✅

**Location**: `libs/vnstock/exceptions.py`

### VnstockError
```python
class VnstockError(Exception):
    """Base exception for vnstock wrapper"""
    pass
```

### RateLimitError
```python
class RateLimitError(VnstockError):
    """Raised when rate limit is exceeded"""
    pass
```

### DataNotFoundError
```python
class DataNotFoundError(VnstockError):
    """Raised when requested data is not found"""
    pass
```

**Usage**:
```python
try:
    prices = client.get_price_history("INVALID", "2024-01-01", "2024-01-02")
except DataNotFoundError:
    logger.warning("No data found for symbol")
except RateLimitError:
    logger.error("Rate limit exceeded")
except VnstockError as e:
    logger.error(f"General vnstock error: {e}")
```

## Validation Models

### Price Data Validation ✅

**Location**: `services/data_collector/src/processors/data_validator.py`

**Validation Rules**:
```python
def validate_price_data(data: Dict[str, Any]) -> bool:
    # Required fields check
    required_fields = ['symbol', 'time', 'open', 'high', 'low', 'close', 'volume']
    
    # Business logic validation
    # 1. High >= Low
    # 2. Volume >= 0
    # 3. All price fields are numeric
```

**Validation Response**: Boolean (True/False)

## Configuration Models

### Collection Results ✅

**Location**: `services/data_collector/src/collectors/price_collector.py`

**Format**: Dictionary returned by collection methods

```python
{
    'success': int,        # Number of successfully processed symbols
    'failed': int,         # Number of failed symbols  
    'total_records': int   # Total number of records collected
}
```

**Example**:
```python
results = {
    'success': 150,
    'failed': 5,
    'total_records': 3000
}
```

## Planned Data Models 📋

### MongoDB Collections (Phase 1.2)

#### stocks Collection
```javascript
{
  "_id": ObjectId("..."),
  "symbol": "VNM",
  "company_name": "Vinamilk", 
  "exchange": "HOSE",
  "industry": "Food & Beverage",
  "last_price": 86.0,
  "last_update": ISODate("2024-12-04T09:15:00Z"),
  "market_cap": 85000000000000,
  "outstanding_shares": 1700000000,
  "created_at": ISODate("2024-01-01T00:00:00Z"),
  "updated_at": ISODate("2024-12-04T09:15:00Z")
}
```

#### price_history Collection
```javascript
{
  "_id": ObjectId("..."),
  "symbol": "VNM",
  "timestamp": ISODate("2024-12-04T09:15:00Z"),
  "open": 85.5,
  "high": 86.2,
  "low": 85.0,
  "close": 86.0,
  "volume": 1250000,
  "value": 107250000000,
  "change": 0.5,
  "change_percent": 0.58,
  "source": "vnstock",
  "created_at": ISODate("2024-12-04T09:15:30Z")
}
```

#### news Collection
```javascript
{
  "_id": ObjectId("..."),
  "news_id": "hash_abc123",
  "symbol": "VNM", 
  "title": "VNM công bố kế hoạch tăng vốn điều lệ",
  "content": "Nội dung tin tức đầy đủ...",
  "summary": "Tóm tắt ngắn gọn...",
  "source_url": "https://...",
  "published_at": ISODate("2024-12-04T08:30:00Z"),
  "collected_at": ISODate("2024-12-04T09:00:00Z"),
  "category": "corporate_action",
  "tags": ["tăng vốn", "cổ phiếu"],
  "sentiment": null,
  "impact_score": null,
  "processed": false,
  "source": "vnstock"
}
```

## Data Type Conventions

### Timestamps
- **Input**: Python datetime objects
- **Storage**: ISO 8601 strings in JSON, ISODate in MongoDB
- **Timezone**: UTC for storage, local timezone for display

### Prices
- **Type**: float
- **Precision**: 2 decimal places for VND
- **Validation**: Must be positive numbers

### Volume
- **Type**: int
- **Validation**: Must be non-negative
- **Unit**: Number of shares

### Symbols
- **Type**: str
- **Format**: Uppercase (e.g., "VCB", "VNM")
- **Validation**: 3-4 character codes

## Data Relationships

### Current Implementation ✅
```
StockListing (1) ──── (N) StockPrice
     │
     └──── (N) StockNews
```

### Planned Relationships 📋
```
stocks (1) ──── (N) price_history
   │
   ├──── (N) news
   │
   ├──── (N) ai_analysis
   │
   ├──── (N) llm_analysis
   │
   └──── (N) final_scores
```

## Serialization

### JSON Serialization ✅
```python
# Kafka producer serialization
value_serializer=lambda v: json.dumps(v).encode('utf-8')
key_serializer=lambda k: k.encode('utf-8') if k else None
```

### Custom Serializers (Planned)
- Avro for schema evolution
- Protocol Buffers for performance
- MessagePack for compact representation

## Data Quality Rules

### Implemented ✅
1. **Required Fields**: All mandatory fields must be present
2. **Price Logic**: High >= Low, all prices > 0
3. **Volume Logic**: Volume >= 0
4. **Type Safety**: Proper type conversion and validation

### Planned 📋
1. **Outlier Detection**: Statistical anomaly detection
2. **Consistency Checks**: Cross-field validation
3. **Temporal Validation**: Timestamp sequence validation
4. **Business Rules**: Market hours, trading halts, etc.