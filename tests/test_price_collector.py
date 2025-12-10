"""
Unit tests for PriceCollector.

Tests specific functionality and edge cases.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from kafka import KafkaProducer
from kafka.errors import KafkaError
import pandas as pd
import json

from src.collectors.price_collector import PriceCollector, PriceData, CollectionResult
from src.services.symbol_manager import SymbolManager


@pytest.fixture
def mock_kafka_producer():
    """Create a mock Kafka producer."""
    producer = Mock(spec=KafkaProducer)
    future = Mock()
    future.get.return_value = Mock(partition=0, offset=0)
    producer.send.return_value = future
    return producer


@pytest.fixture
def mock_vnstock_client():
    """Create a mock vnstock client."""
    client = Mock()
    return client


@pytest.fixture
def mock_symbol_manager():
    """Create a mock SymbolManager."""
    manager = Mock(spec=SymbolManager)
    return manager


@pytest.fixture
def price_collector(mock_kafka_producer, mock_vnstock_client, mock_symbol_manager):
    """Create a PriceCollector instance with mocked dependencies."""
    return PriceCollector(
        kafka_producer=mock_kafka_producer,
        vnstock_client=mock_vnstock_client,
        symbol_manager=mock_symbol_manager
    )


def test_price_collector_initialization(price_collector):
    """Test that PriceCollector initializes correctly."""
    assert price_collector.producer is not None
    assert price_collector.client is not None
    assert price_collector.symbol_manager is not None


def test_collect_with_valid_data(price_collector, mock_symbol_manager, mock_vnstock_client):
    """Test price data collection with valid data from vnstock."""
    # Setup
    test_symbols = ['VNM', 'VIC', 'HPG']
    mock_symbol_manager.get_active_symbols.return_value = test_symbols
    
    # Mock vnstock response
    def mock_stock_data(symbol, source):
        stock_mock = Mock()
        quote_mock = Mock()
        df = pd.DataFrame({
            'open': [50000.0],
            'close': [51000.0],
            'high': [52000.0],
            'low': [49000.0],
            'volume': [1000000]
        })
        quote_mock.history.return_value = df
        stock_mock.quote = quote_mock
        return stock_mock
    
    mock_vnstock_client.stock = Mock(side_effect=mock_stock_data)
    
    # Execute
    result = price_collector.collect()
    
    # Assert
    assert result.success_count == 3
    assert result.failure_count == 0
    assert result.total_symbols == 3
    assert len(result.failed_symbols) == 0
    assert result.success is True


def test_collect_with_empty_symbols(price_collector, mock_symbol_manager):
    """Test collection when no active symbols are available."""
    # Setup
    mock_symbol_manager.get_active_symbols.return_value = []
    
    # Execute
    result = price_collector.collect()
    
    # Assert
    assert result.success_count == 0
    assert result.failure_count == 0
    assert result.total_symbols == 0
    assert result.success is True


def test_collect_with_vnstock_error(price_collector, mock_symbol_manager, mock_vnstock_client):
    """Test collection when vnstock raises an error."""
    # Setup
    test_symbols = ['VNM', 'VIC']
    mock_symbol_manager.get_active_symbols.return_value = test_symbols
    
    # Mock vnstock to raise an exception
    mock_vnstock_client.stock.side_effect = Exception("Network error")
    
    # Execute
    result = price_collector.collect()
    
    # Assert
    assert result.success_count == 0
    assert result.failure_count == 2
    assert result.total_symbols == 2
    assert set(result.failed_symbols) == set(test_symbols)
    assert result.success is False


def test_collect_with_empty_dataframe(price_collector, mock_symbol_manager, mock_vnstock_client):
    """Test collection when vnstock returns empty DataFrame."""
    # Setup
    test_symbols = ['VNM']
    mock_symbol_manager.get_active_symbols.return_value = test_symbols
    
    # Mock vnstock to return empty DataFrame
    def mock_stock_data(symbol, source):
        stock_mock = Mock()
        quote_mock = Mock()
        quote_mock.history.return_value = pd.DataFrame()  # Empty DataFrame
        stock_mock.quote = quote_mock
        return stock_mock
    
    mock_vnstock_client.stock = Mock(side_effect=mock_stock_data)
    
    # Execute
    result = price_collector.collect()
    
    # Assert
    assert result.success_count == 0
    assert result.failure_count == 1
    assert result.total_symbols == 1
    assert 'VNM' in result.failed_symbols


def test_publish_to_kafka_success(price_collector, mock_kafka_producer):
    """Test successful publishing to Kafka."""
    # Setup
    price_data = PriceData(
        symbol='VNM',
        timestamp='2024-01-15T10:00:00Z',
        open=50000.0,
        close=51000.0,
        high=52000.0,
        low=49000.0,
        volume=1000000
    )
    
    # Execute
    result = price_collector.publish_to_kafka(price_data)
    
    # Assert
    assert result is True
    assert mock_kafka_producer.send.called
    call_args = mock_kafka_producer.send.call_args
    assert call_args[0][0] == 'stock_prices_raw'  # Topic name
    
    # Verify message content
    message = call_args[1]['value']
    data = json.loads(message.decode('utf-8'))
    assert data['symbol'] == 'VNM'
    assert data['open'] == 50000.0
    assert data['close'] == 51000.0


def test_publish_to_kafka_with_custom_topic(price_collector, mock_kafka_producer):
    """Test publishing to a custom Kafka topic."""
    # Setup
    price_data = PriceData(
        symbol='VNM',
        timestamp='2024-01-15T10:00:00Z',
        open=50000.0,
        close=51000.0,
        high=52000.0,
        low=49000.0,
        volume=1000000
    )
    
    # Execute
    result = price_collector.publish_to_kafka(price_data, topic='custom_topic')
    
    # Assert
    assert result is True
    call_args = mock_kafka_producer.send.call_args
    assert call_args[0][0] == 'custom_topic'


def test_publish_to_kafka_failure(price_collector, mock_kafka_producer):
    """Test handling of Kafka publishing failure."""
    # Setup
    price_data = PriceData(
        symbol='VNM',
        timestamp='2024-01-15T10:00:00Z',
        open=50000.0,
        close=51000.0,
        high=52000.0,
        low=49000.0,
        volume=1000000
    )
    
    # Mock Kafka error
    mock_kafka_producer.send.side_effect = KafkaError("Connection failed")
    
    # Execute
    result = price_collector.publish_to_kafka(price_data)
    
    # Assert
    assert result is False


def test_collect_with_mixed_results(price_collector, mock_symbol_manager, mock_vnstock_client):
    """Test collection with some symbols succeeding and others failing."""
    # Setup
    test_symbols = ['VNM', 'VIC', 'HPG', 'TCB']
    mock_symbol_manager.get_active_symbols.return_value = test_symbols
    
    # Mock vnstock to succeed for some symbols and fail for others
    call_count = [0]
    
    def mock_stock_data(symbol, source):
        call_count[0] += 1
        if call_count[0] % 2 == 0:  # Fail every other symbol
            raise Exception("API error")
        
        stock_mock = Mock()
        quote_mock = Mock()
        df = pd.DataFrame({
            'open': [50000.0],
            'close': [51000.0],
            'high': [52000.0],
            'low': [49000.0],
            'volume': [1000000]
        })
        quote_mock.history.return_value = df
        stock_mock.quote = quote_mock
        return stock_mock
    
    mock_vnstock_client.stock = Mock(side_effect=mock_stock_data)
    
    # Execute
    result = price_collector.collect()
    
    # Assert
    assert result.success_count == 2
    assert result.failure_count == 2
    assert result.total_symbols == 4
    assert len(result.failed_symbols) == 2
    assert result.success is False


def test_price_data_to_dict():
    """Test PriceData conversion to dictionary."""
    price_data = PriceData(
        symbol='VNM',
        timestamp='2024-01-15T10:00:00Z',
        open=50000.0,
        close=51000.0,
        high=52000.0,
        low=49000.0,
        volume=1000000
    )
    
    data_dict = price_data.to_dict()
    
    assert data_dict['symbol'] == 'VNM'
    assert data_dict['timestamp'] == '2024-01-15T10:00:00Z'
    assert data_dict['open'] == 50000.0
    assert data_dict['close'] == 51000.0
    assert data_dict['high'] == 52000.0
    assert data_dict['low'] == 49000.0
    assert data_dict['volume'] == 1000000


def test_collection_result_success_property():
    """Test CollectionResult success property."""
    # Success case
    result_success = CollectionResult(
        success_count=5,
        failure_count=0,
        total_symbols=5,
        failed_symbols=[]
    )
    assert result_success.success is True
    
    # Failure case
    result_failure = CollectionResult(
        success_count=3,
        failure_count=2,
        total_symbols=5,
        failed_symbols=['VIC', 'HPG']
    )
    assert result_failure.success is False
