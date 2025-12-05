# Vnstock Wrapper Library

Minimal wrapper around vnstock library with rate limiting, caching, and error handling.

## Features

- ✅ Rate limiting for API calls
- ✅ Response caching (TTL: 1 hour for listings, 5 min default)
- ✅ Structured data models
- ✅ Error handling with custom exceptions
- ✅ Retry logic built-in

## Usage

```python
from vnstock import VnstockClient

# Initialize client
client = VnstockClient(source='VCI', rate_limit=0.5)

# Get all stock symbols
symbols = client.get_all_symbols()

# Get price history
prices = client.get_price_history('VCB', '2024-01-01', '2024-01-31', interval='1D')

# Get news
news = client.get_news('VCB')
```

## Testing

```bash
pytest backend/tests/libs/test_vnstock.py -v
```
