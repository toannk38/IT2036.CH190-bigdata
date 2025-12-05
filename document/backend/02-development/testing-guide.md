# Testing Guide

## Overview

This guide covers the testing strategy and practices for the Stock AI Backend System, based on the implemented testing framework.

**Testing Status**: ✅ **IMPLEMENTED** for core components

## Testing Framework

### Technology Stack ✅
- **Framework**: pytest
- **Mocking**: unittest.mock
- **Fixtures**: pytest fixtures
- **Coverage**: pytest-cov (planned)

### Configuration ✅
**Location**: `pytest.ini`

```ini
[pytest]
pythonpath = .
addopts = --tb=short
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

## Test Structure

### Directory Layout ✅
```
tests/
├── libs/
│   └── test_vnstock.py              # vnstock library tests
├── test_services/
│   └── data_collector/
│       ├── test_price_collector.py  # Price collector tests
│       └── test_price_collector_simple.py
├── infrastructure/                   # Infrastructure tests
│   ├── unit/                        # Unit tests for infrastructure
│   ├── integration/                 # Integration tests
│   ├── health/                      # Health check tests
│   └── fixtures/                    # Test data fixtures
└── conftest.py                      # Global pytest configuration
```

## Unit Tests

### vnstock Library Tests ✅
**Location**: `tests/libs/test_vnstock.py`

#### Test Coverage
```python
class TestVnstockClient:
    def test_init(self, client)                    # Client initialization
    def test_get_all_symbols(self, client, ...)   # Symbol listing
    def test_get_price_history(self, client, ...)  # Price data retrieval
    def test_get_price_history_empty(self, client) # Empty data handling
    def test_get_news(self, client, ...)          # News data retrieval
    def test_get_news_empty(self, client)         # Empty news handling
    def test_rate_limit(self, client)             # Rate limiting

class TestCache:
    def test_cache_works(self, client, ...)       # Caching mechanism
```

#### Test Fixtures
```python
@pytest.fixture
def client():
    return VnstockClient(source='VCI', rate_limit=0.1)

@pytest.fixture
def mock_listing_df():
    return pd.DataFrame({
        'symbol': ['VCB', 'VIC'],
        'organ_name': ['Vietcombank', 'Vingroup']
    })

@pytest.fixture
def mock_price_df():
    return pd.DataFrame({
        'time': ['2024-01-01', '2024-01-02'],
        'open': [100.0, 101.0],
        'high': [105.0, 106.0],
        'low': [99.0, 100.0],
        'close': [103.0, 104.0],
        'volume': [1000000, 1100000]
    })
```

#### Mocking Strategy
```python
# Mock vnstock library calls
with patch('vnstock.vnstock_client.vnstock_lib') as mock_vnstock:
    mock_listing = Mock()
    mock_listing.all_symbols.return_value = mock_listing_df
    mock_vnstock.Listing.return_value = mock_listing
    
    result = client.get_all_symbols()
    
    assert len(result) == 2
    assert isinstance(result[0], StockListing)
```

### Data Collector Tests ✅
**Location**: `tests/test_services/data_collector/test_price_collector.py`

#### Test Coverage
```python
class TestDataValidator:
    def test_validate_valid_data(self)         # Valid data validation
    def test_validate_missing_field(self)      # Missing field handling
    def test_validate_invalid_high_low(self)   # Business logic validation

class TestDataNormalizer:
    def test_normalize_price_data(self, sample_price)  # Data normalization

class TestPriceCollector:
    def test_collect_symbol_prices_success(self, ...)     # Successful collection
    def test_collect_symbol_prices_not_found(self, ...)  # Data not found handling
    def test_collect_all_symbols(self, ...)              # Bulk collection
```

#### Mock Services
```python
@pytest.fixture
def mock_vnstock_client():
    return Mock()

@pytest.fixture
def mock_kafka_producer():
    producer = Mock()
    producer.send_price_data = Mock()
    return producer

@pytest.fixture
def price_collector(mock_vnstock_client, mock_kafka_producer):
    return PriceCollector(mock_vnstock_client, mock_kafka_producer, 'test_topic')
```

## Integration Tests

### Infrastructure Tests ✅
**Location**: `tests/infrastructure/`

#### Database Integration
```python
# tests/infrastructure/integration/test_cache_database.py
# tests/infrastructure/integration/test_data_pipeline.py
```

#### Service Health Tests
```python
# tests/infrastructure/health/test_connectivity.py
# tests/infrastructure/health/test_services_health.py
# tests/infrastructure/health/test_resource_limits.py
```

#### Unit Infrastructure Tests
```python
# tests/infrastructure/unit/test_mongodb.py
# tests/infrastructure/unit/test_kafka.py
# tests/infrastructure/unit/test_redis.py
# tests/infrastructure/unit/test_elasticsearch.py
```

## Test Data & Fixtures

### Stock Data Fixtures ✅
**Location**: `tests/infrastructure/fixtures/`

```python
# tests/infrastructure/fixtures/stock_companies.py
# tests/infrastructure/fixtures/stock_prices.py
# tests/infrastructure/fixtures/stock_news.py
```

### Sample Data
```python
@pytest.fixture
def sample_price():
    return StockPrice(
        symbol='VCB',
        time=datetime(2024, 1, 1),
        open=100.0,
        high=105.0,
        low=99.0,
        close=103.0,
        volume=1000000
    )
```

## Test Execution

### Running Tests ✅

#### All Tests
```bash
pytest tests/
```

#### Specific Test Modules
```bash
# vnstock library tests
pytest tests/libs/test_vnstock.py

# Data collector tests
pytest tests/test_services/data_collector/

# Infrastructure tests
pytest tests/infrastructure/
```

#### Test Scripts ✅
**Location**: `tests/infrastructure/scripts/`

```bash
# Run all tests
./tests/infrastructure/scripts/run_all_tests.sh

# Run unit tests only
./tests/infrastructure/scripts/run_unit_tests.sh

# Run integration tests only
./tests/infrastructure/scripts/run_integration_tests.sh
```

### Test Environment Setup ✅
```bash
# Setup test environment
./tests/infrastructure/scripts/setup_test_env.sh
```

## Test Utilities

### Helper Functions ✅
**Location**: `tests/infrastructure/utils/`

```python
# tests/infrastructure/utils/cleanup_helpers.py
# tests/infrastructure/utils/data_loader.py
# tests/infrastructure/utils/docker_helpers.py
# tests/infrastructure/utils/wait_for_services.py
```

### Docker Test Helpers
```python
# Example from docker_helpers.py
def wait_for_service(service_name, port, timeout=30):
    """Wait for a Docker service to be ready"""
    pass

def cleanup_test_containers():
    """Clean up test containers after tests"""
    pass
```

## Testing Best Practices

### 1. Test Isolation ✅
- Each test is independent
- Mock external dependencies
- Clean up after tests

### 2. Descriptive Test Names ✅
```python
def test_get_price_history_empty(self, client):
    """Test handling of empty price history response"""
    
def test_validate_invalid_high_low(self):
    """Test validation fails when high < low"""
```

### 3. Comprehensive Mocking ✅
```python
# Mock external API calls
with patch('vnstock.vnstock_client.vnstock_lib') as mock_vnstock:
    # Setup mock behavior
    mock_quote = Mock()
    mock_quote.history.return_value = pd.DataFrame()
    mock_vnstock.Quote.return_value = mock_quote
    
    # Test exception handling
    with pytest.raises(DataNotFoundError):
        client.get_price_history('INVALID', '2024-01-01', '2024-01-02')
```

### 4. Edge Case Testing ✅
- Empty data responses
- Network failures
- Invalid input data
- Rate limiting scenarios

## Test Coverage

### Current Coverage ✅
- **vnstock Library**: Comprehensive unit tests
- **Data Collector**: Core functionality tested
- **Data Validation**: Business logic validation
- **Error Handling**: Exception scenarios covered

### Coverage Goals 📋
- **Unit Tests**: > 90% code coverage
- **Integration Tests**: All service interactions
- **End-to-End Tests**: Complete workflows

## Performance Testing

### Load Testing (Planned) 📋
```python
def test_collection_performance():
    """Test collection performance under load"""
    # Measure collection time for large datasets
    # Verify memory usage stays within limits
    # Test concurrent collection scenarios
```

### Stress Testing (Planned) 📋
- High-volume data collection
- Kafka throughput testing
- Database performance under load
- Memory leak detection

## Continuous Integration

### Test Automation (Planned) 📋
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ --cov=src/
```

## Debugging Tests

### Test Debugging ✅
```python
# Use pytest debugging features
pytest tests/libs/test_vnstock.py -v -s  # Verbose output
pytest tests/libs/test_vnstock.py --pdb  # Drop into debugger on failure
```

### Logging in Tests
```python
import logging
logging.basicConfig(level=logging.DEBUG)

def test_with_logging():
    logger = logging.getLogger(__name__)
    logger.debug("Test debug information")
```

## Test Data Management

### Test Database (Planned) 📋
- Separate test database instance
- Test data seeding and cleanup
- Isolated test environments

### Mock Data Generation
```python
def generate_mock_price_data(symbol, days=30):
    """Generate realistic mock price data for testing"""
    base_price = 100.0
    prices = []
    
    for i in range(days):
        # Generate realistic OHLCV data
        pass
    
    return prices
```

## Common Testing Patterns

### 1. Arrange-Act-Assert ✅
```python
def test_normalize_price_data(self, sample_price):
    # Arrange
    normalizer = DataNormalizer()
    
    # Act
    result = normalizer.normalize_price_data(sample_price)
    
    # Assert
    assert result['symbol'] == 'VCB'
    assert result['open'] == 100.0
```

### 2. Exception Testing ✅
```python
def test_get_price_history_empty(self, client):
    with patch('vnstock.vnstock_client.vnstock_lib') as mock_vnstock:
        mock_quote = Mock()
        mock_quote.history.return_value = pd.DataFrame()
        mock_vnstock.Quote.return_value = mock_quote
        
        with pytest.raises(DataNotFoundError):
            client.get_price_history('INVALID', '2024-01-01', '2024-01-02')
```

### 3. Parameterized Tests (Planned) 📋
```python
@pytest.mark.parametrize("symbol,expected", [
    ("VCB", True),
    ("VNM", True),
    ("INVALID", False)
])
def test_symbol_validation(symbol, expected):
    result = validate_symbol(symbol)
    assert result == expected
```

## Test Maintenance

### Regular Tasks
1. **Update Test Data**: Keep test fixtures current
2. **Review Coverage**: Identify untested code paths
3. **Performance Monitoring**: Track test execution time
4. **Dependency Updates**: Keep test dependencies current

### Test Refactoring
- Extract common test utilities
- Consolidate similar test cases
- Improve test readability
- Optimize test performance