

"""
Run from backend directory:
python -m pytest tests/services/data_collector/test_price_collector_simple.py -v

Or run directly:
cd /home/toannk/Desktop/project/bigdata/backend
python tests/services/data_collector/test_price_collector_simple.py
"""

def test_imports():
    """Test that all modules can be imported"""
    from libs.vnstock import VnstockClient, StockPrice, StockListing
    from services.data_collector.src.collectors import PriceCollector
    from services.data_collector.src.processors import DataValidator, DataNormalizer
    from services.data_collector.src.producers import StockKafkaProducer
    assert True

def test_validator():
    """Test data validator"""
    from services.data_collector.src.processors import DataValidator
    
    valid_data = {
        'symbol': 'VCB',
        'time': '2024-01-01',
        'open': 100.0,
        'high': 105.0,
        'low': 99.0,
        'close': 103.0,
        'volume': 1000000
    }
    assert DataValidator.validate_price_data(valid_data) is True
    
    invalid_data = {'symbol': 'VCB'}
    assert DataValidator.validate_price_data(invalid_data) is False

def test_normalizer():
    """Test data normalizer"""
    from datetime import datetime
    from libs.vnstock import StockPrice
    from services.data_collector.src.processors import DataNormalizer
    
    price = StockPrice(
        symbol='VCB',
        time=datetime(2024, 1, 1),
        open=100.0,
        high=105.0,
        low=99.0,
        close=103.0,
        volume=1000000
    )
    
    result = DataNormalizer.normalize_price_data(price)
    assert result['symbol'] == 'VCB'
    assert result['open'] == 100.0
    assert 'collected_at' in result

if __name__ == '__main__':
    print("Running tests...")
    test_imports()
    print("✓ Imports test passed")
    test_validator()
    print("✓ Validator test passed")
    test_normalizer()
    print("✓ Normalizer test passed")
    print("\nAll tests passed!")
