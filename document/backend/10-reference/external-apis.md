# External APIs Reference

## vnstock API ✅

### Overview
Primary data source for Vietnamese stock market information, accessed through the vnstock Python library.

### Integration ✅
**Location**: `libs/vnstock/vnstock_client.py`

```python
class VnstockClient:
    def __init__(self, source: str = 'VCI', rate_limit: float = 0.5):
        self.source = source
        self.rate_limit = rate_limit
```

### Available Methods ✅

#### get_all_symbols()
```python
@cached(ttl=3600)
def get_all_symbols(self) -> List[StockListing]:
    """Get all available stock symbols with company information"""
```

**Returns**: List of StockListing objects
**Cache**: 1 hour TTL
**Rate Limit**: Applied automatically

#### get_price_history()
```python
def get_price_history(self, symbol: str, start: str, end: str, 
                     interval: str = '1D') -> List[StockPrice]:
    """Get historical price data for a symbol"""
```

**Parameters**:
- `symbol`: Stock symbol (e.g., "VCB", "VNM")
- `start`: Start date in YYYY-MM-DD format
- `end`: End date in YYYY-MM-DD format  
- `interval`: Data interval ("1D", "1H", "5m")

**Returns**: List of StockPrice objects

#### get_news()
```python
def get_news(self, symbol: str) -> List[StockNews]:
    """Get news articles for a specific symbol"""
```

**Parameters**:
- `symbol`: Stock symbol

**Returns**: List of StockNews objects

### Data Sources
- **VCI**: Viet Capital Securities (default)
- **TCBS**: Techcom Securities
- **SSI**: Saigon Securities Inc

### Rate Limiting ✅
```python
def _rate_limit_check(self):
    elapsed = time.time() - self._last_call
    if elapsed < self.rate_limit:
        time.sleep(self.rate_limit - elapsed)
    self._last_call = time.time()
```

**Default**: 0.5 seconds between calls
**Configurable**: Via VNSTOCK_RATE_LIMIT environment variable

### Error Handling ✅
```python
# Custom exceptions
class VnstockError(Exception): pass
class RateLimitError(VnstockError): pass  
class DataNotFoundError(VnstockError): pass
```

### Usage Examples ✅
```python
# Initialize client
client = VnstockClient(source='VCI', rate_limit=0.5)

# Get all symbols
symbols = client.get_all_symbols()
print(f"Found {len(symbols)} symbols")

# Get price history
prices = client.get_price_history('VCB', '2024-01-01', '2024-12-04')
print(f"Retrieved {len(prices)} price records")

# Get news
news = client.get_news('VCB')
print(f"Found {len(news)} news articles")
```

## OpenAI API 📋

### Overview
Large Language Model API for news sentiment analysis and insight extraction.

### Planned Integration
**Location**: `services/llm_analysis/src/llm/openai_client.py`

```python
class OpenAIClient:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.rate_limiter = RateLimiter(requests_per_minute=60)
```

### Planned Methods

#### analyze_sentiment()
```python
def analyze_sentiment(self, text: str) -> dict:
    """Analyze sentiment of Vietnamese news text"""
    
    prompt = """
    Analyze the sentiment of this Vietnamese stock news article.
    Return JSON with: sentiment (positive/negative/neutral), 
    confidence (0-1), impact_score (0-1), key_insights (list).
    
    Article: {text}
    """
    
    response = self.client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt.format(text=text)}],
        temperature=0.1
    )
    
    return json.loads(response.choices[0].message.content)
```

#### extract_insights()
```python
def extract_insights(self, text: str) -> List[str]:
    """Extract key business insights from news text"""
```

### Configuration
```python
# Environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
OPENAI_RATE_LIMIT = float(os.getenv('OPENAI_RATE_LIMIT', '60'))  # per minute
```

### Rate Limiting 📋
- **Default**: 60 requests per minute
- **Implementation**: Token bucket algorithm
- **Backoff**: Exponential backoff on rate limit errors

### Cost Management 📋
```python
class CostTracker:
    def __init__(self):
        self.total_tokens = 0
        self.total_cost = 0.0
    
    def track_usage(self, prompt_tokens: int, completion_tokens: int):
        # GPT-4 pricing (as of 2024)
        prompt_cost = prompt_tokens * 0.00003  # $0.03 per 1K tokens
        completion_cost = completion_tokens * 0.00006  # $0.06 per 1K tokens
        
        self.total_tokens += prompt_tokens + completion_tokens
        self.total_cost += prompt_cost + completion_cost
```

## Claude API 📋

### Overview
Alternative LLM API for backup and comparison with OpenAI.

### Planned Integration
```python
class ClaudeClient:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
```

## External Data Sources 📋

### Yahoo Finance (Backup)
```python
# Potential backup data source
import yfinance as yf

def get_backup_data(symbol: str):
    # Convert VN symbol to Yahoo format
    yahoo_symbol = f"{symbol}.VN"
    ticker = yf.Ticker(yahoo_symbol)
    return ticker.history(period="1mo")
```

### Alpha Vantage (Alternative)
```python
# Alternative financial data API
class AlphaVantageClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
```

## API Monitoring 📋

### Health Checks
```python
async def check_external_apis():
    results = {}
    
    # Check vnstock availability
    try:
        client = VnstockClient()
        symbols = client.get_all_symbols()
        results['vnstock'] = {
            'status': 'healthy',
            'symbols_count': len(symbols),
            'response_time': '< 1s'
        }
    except Exception as e:
        results['vnstock'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # Check OpenAI API
    try:
        openai_client = OpenAIClient(api_key=OPENAI_API_KEY)
        test_response = openai_client.test_connection()
        results['openai'] = {
            'status': 'healthy',
            'model': 'gpt-4',
            'rate_limit_remaining': test_response.get('rate_limit_remaining')
        }
    except Exception as e:
        results['openai'] = {
            'status': 'unhealthy', 
            'error': str(e)
        }
    
    return results
```

### Usage Metrics
```python
# Track API usage and costs
class APIMetrics:
    def __init__(self):
        self.metrics = {
            'vnstock': {
                'requests_today': 0,
                'errors_today': 0,
                'avg_response_time': 0.0
            },
            'openai': {
                'requests_today': 0,
                'tokens_used_today': 0,
                'cost_today': 0.0
            }
        }
    
    def record_vnstock_call(self, response_time: float, success: bool):
        self.metrics['vnstock']['requests_today'] += 1
        if not success:
            self.metrics['vnstock']['errors_today'] += 1
        
        # Update average response time
        current_avg = self.metrics['vnstock']['avg_response_time']
        total_requests = self.metrics['vnstock']['requests_today']
        new_avg = ((current_avg * (total_requests - 1)) + response_time) / total_requests
        self.metrics['vnstock']['avg_response_time'] = new_avg
```

## Error Handling Strategies

### Retry Logic ✅
```python
# From vnstock client implementation
def _handle_error(self, e: Exception, context: str):
    if isinstance(e, (RateLimitError, DataNotFoundError, VnstockError)):
        raise
    if "rate limit" in str(e).lower():
        raise RateLimitError(f"Rate limit exceeded: {context}")
    elif "not found" in str(e).lower():
        raise DataNotFoundError(f"Data not found: {context}")
    raise VnstockError(f"Error in {context}: {str(e)}")
```

### Fallback Strategies 📋
```python
class DataSourceFallback:
    def __init__(self):
        self.primary = VnstockClient()
        self.backup = YahooFinanceClient()
    
    def get_price_data(self, symbol: str, start: str, end: str):
        try:
            return self.primary.get_price_history(symbol, start, end)
        except Exception as e:
            logger.warning(f"Primary source failed: {e}, trying backup")
            return self.backup.get_price_history(symbol, start, end)
```

## Security Considerations

### API Key Management
```python
# Secure API key handling
import os
from cryptography.fernet import Fernet

class SecureAPIKeys:
    def __init__(self):
        self.cipher = Fernet(os.getenv('ENCRYPTION_KEY'))
    
    def get_openai_key(self):
        encrypted_key = os.getenv('OPENAI_API_KEY_ENCRYPTED')
        return self.cipher.decrypt(encrypted_key.encode()).decode()
```

### Request Validation
```python
# Validate and sanitize API requests
def validate_symbol(symbol: str) -> bool:
    # Only allow alphanumeric symbols, 3-4 characters
    return symbol.isalnum() and 3 <= len(symbol) <= 4

def sanitize_date(date_str: str) -> str:
    # Validate date format YYYY-MM-DD
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}")
```