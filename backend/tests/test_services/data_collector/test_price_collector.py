import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from libs.vnstock import StockPrice, StockListing
from libs.vnstock.exceptions import DataNotFoundError

from services.data_collector.src.collectors import PriceCollector
from services.data_collector.src.processors import DataValidator, DataNormalizer

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

class TestDataValidator:
    def test_validate_valid_data(self):
        data = {
            'symbol': 'VCB',
            'time': '2024-01-01',
            'open': 100.0,
            'high': 105.0,
            'low': 99.0,
            'close': 103.0,
            'volume': 1000000
        }
        assert DataValidator.validate_price_data(data) is True
    
    def test_validate_missing_field(self):
        data = {'symbol': 'VCB', 'open': 100.0}
        assert DataValidator.validate_price_data(data) is False
    
    def test_validate_invalid_high_low(self):
        data = {
            'symbol': 'VCB',
            'time': '2024-01-01',
            'open': 100.0,
            'high': 99.0,
            'low': 105.0,
            'close': 103.0,
            'volume': 1000000
        }
        assert DataValidator.validate_price_data(data) is False

class TestDataNormalizer:
    def test_normalize_price_data(self, sample_price):
        result = DataNormalizer.normalize_price_data(sample_price)
        
        assert result['symbol'] == 'VCB'
        assert result['open'] == 100.0
        assert result['high'] == 105.0
        assert result['low'] == 99.0
        assert result['close'] == 103.0
        assert result['volume'] == 1000000
        assert 'collected_at' in result

class TestPriceCollector:
    def test_collect_symbol_prices_success(self, price_collector, mock_vnstock_client, 
                                          mock_kafka_producer, sample_price):
        mock_vnstock_client.get_price_history.return_value = [sample_price]
        
        count = price_collector.collect_symbol_prices('VCB', '2024-01-01', '2024-01-02')
        
        assert count == 1
        assert mock_kafka_producer.send_price_data.call_count == 1
    
    def test_collect_symbol_prices_not_found(self, price_collector, mock_vnstock_client):
        mock_vnstock_client.get_price_history.side_effect = DataNotFoundError("Not found")
        
        count = price_collector.collect_symbol_prices('INVALID', '2024-01-01', '2024-01-02')
        
        assert count == 0
    
    def test_collect_all_symbols(self, price_collector, mock_vnstock_client, sample_price):
        mock_vnstock_client.get_all_symbols.return_value = [
            StockListing(symbol='VCB', organ_name='Vietcombank'),
            StockListing(symbol='VIC', organ_name='Vingroup')
        ]
        mock_vnstock_client.get_price_history.return_value = [sample_price]
        
        results = price_collector.collect_all_symbols(days=1)
        
        assert results['success'] == 2
        assert results['failed'] == 0
        assert results['total_records'] == 2
