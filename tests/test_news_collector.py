"""
Unit tests for NewsCollector.

Tests specific functionality and edge cases.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from kafka import KafkaProducer
from kafka.errors import KafkaError
import pandas as pd
import json

from src.collectors.news_collector import NewsCollector, NewsData, CollectionResult
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
def news_collector(mock_kafka_producer, mock_vnstock_client, mock_symbol_manager):
    """Create a NewsCollector instance with mocked dependencies."""
    return NewsCollector(
        kafka_producer=mock_kafka_producer,
        vnstock_client=mock_vnstock_client,
        symbol_manager=mock_symbol_manager
    )


def test_news_collector_initialization(news_collector):
    """Test that NewsCollector initializes correctly."""
    assert news_collector.producer is not None
    assert news_collector.client is not None
    assert news_collector.symbol_manager is not None


def test_collect_with_valid_data(news_collector, mock_symbol_manager, mock_vnstock_client):
    """Test news data collection with valid data from vnstock."""
    # Setup
    test_symbols = ['VNM', 'VIC', 'HPG']
    mock_symbol_manager.get_active_symbols.return_value = test_symbols
    
    # Mock vnstock response
    def mock_stock_data(symbol, source):
        stock_mock = Mock()
        company_mock = Mock()
        df = pd.DataFrame({
            'title': [f'Breaking news about {symbol}', f'Another update on {symbol}'],
            'content': [f'Important content about {symbol}', f'More details on {symbol}'],
            'source': ['cafef.vn', 'vnexpress.net'],
            'published_date': ['2024-01-15T08:00:00Z', '2024-01-15T09:00:00Z']
        })
        company_mock.news.return_value = df
        stock_mock.company = company_mock
        return stock_mock
    
    mock_vnstock_client.stock = Mock(side_effect=mock_stock_data)
    
    # Execute
    result = news_collector.collect()
    
    # Assert
    assert result.success_count == 3
    assert result.failure_count == 0
    assert result.total_symbols == 3
    assert len(result.failed_symbols) == 0
    assert result.success is True


def test_collect_with_empty_symbols(news_collector, mock_symbol_manager):
    """Test collection when no active symbols are available."""
    # Setup
    mock_symbol_manager.get_active_symbols.return_value = []
    
    # Execute
    result = news_collector.collect()
    
    # Assert
    assert result.success_count == 0
    assert result.failure_count == 0
    assert result.total_symbols == 0
    assert result.success is True


def test_collect_with_vnstock_error(news_collector, mock_symbol_manager, mock_vnstock_client):
    """Test collection when vnstock raises an error."""
    # Setup
    test_symbols = ['VNM', 'VIC']
    mock_symbol_manager.get_active_symbols.return_value = test_symbols
    
    # Mock vnstock to raise an exception
    mock_vnstock_client.stock.side_effect = Exception("API error")
    
    # Execute
    result = news_collector.collect()
    
    # Assert
    assert result.success_count == 0
    assert result.failure_count == 2
    assert result.total_symbols == 2
    assert set(result.failed_symbols) == set(test_symbols)
    assert result.success is False


def test_collect_with_empty_dataframe(news_collector, mock_symbol_manager, mock_vnstock_client):
    """Test collection when vnstock returns empty DataFrame (no news)."""
    # Setup
    test_symbols = ['VNM']
    mock_symbol_manager.get_active_symbols.return_value = test_symbols
    
    # Mock vnstock to return empty DataFrame
    def mock_stock_data(symbol, source):
        stock_mock = Mock()
        company_mock = Mock()
        company_mock.news.return_value = pd.DataFrame()  # Empty DataFrame
        stock_mock.company = company_mock
        return stock_mock
    
    mock_vnstock_client.stock = Mock(side_effect=mock_stock_data)
    
    # Execute
    result = news_collector.collect()
    
    # Assert
    # No news is not a failure - some symbols may not have recent news
    assert result.success_count == 1
    assert result.failure_count == 0
    assert result.total_symbols == 1


def test_collect_with_none_dataframe(news_collector, mock_symbol_manager, mock_vnstock_client):
    """Test collection when vnstock returns None."""
    # Setup
    test_symbols = ['VNM']
    mock_symbol_manager.get_active_symbols.return_value = test_symbols
    
    # Mock vnstock to return None
    def mock_stock_data(symbol, source):
        stock_mock = Mock()
        company_mock = Mock()
        company_mock.news.return_value = None
        stock_mock.company = company_mock
        return stock_mock
    
    mock_vnstock_client.stock = Mock(side_effect=mock_stock_data)
    
    # Execute
    result = news_collector.collect()
    
    # Assert
    # No news is not a failure
    assert result.success_count == 1
    assert result.failure_count == 0
    assert result.total_symbols == 1


def test_publish_to_kafka_success(news_collector, mock_kafka_producer):
    """Test successful publishing to Kafka."""
    # Setup
    news_data = NewsData(
        symbol='VNM',
        title='Breaking news about VNM',
        content='Important content about VNM stock',
        source='cafef.vn',
        published_at='2024-01-15T08:00:00Z',
        collected_at='2024-01-15T08:05:00Z'
    )
    
    # Execute
    result = news_collector.publish_to_kafka(news_data)
    
    # Assert
    assert result is True
    assert mock_kafka_producer.send.called
    call_args = mock_kafka_producer.send.call_args
    assert call_args[0][0] == 'stock_news_raw'  # Topic name
    
    # Verify message content
    message = call_args[1]['value']
    data = json.loads(message.decode('utf-8'))
    assert data['symbol'] == 'VNM'
    assert data['title'] == 'Breaking news about VNM'
    assert data['content'] == 'Important content about VNM stock'
    assert data['source'] == 'cafef.vn'


def test_publish_to_kafka_with_custom_topic(news_collector, mock_kafka_producer):
    """Test publishing to a custom Kafka topic."""
    # Setup
    news_data = NewsData(
        symbol='VNM',
        title='Breaking news',
        content='Important content',
        source='cafef.vn',
        published_at='2024-01-15T08:00:00Z',
        collected_at='2024-01-15T08:05:00Z'
    )
    
    # Execute
    result = news_collector.publish_to_kafka(news_data, topic='custom_topic')
    
    # Assert
    assert result is True
    call_args = mock_kafka_producer.send.call_args
    assert call_args[0][0] == 'custom_topic'


def test_publish_to_kafka_failure(news_collector, mock_kafka_producer):
    """Test handling of Kafka publishing failure."""
    # Setup
    news_data = NewsData(
        symbol='VNM',
        title='Breaking news',
        content='Important content',
        source='cafef.vn',
        published_at='2024-01-15T08:00:00Z',
        collected_at='2024-01-15T08:05:00Z'
    )
    
    # Mock Kafka error
    mock_kafka_producer.send.side_effect = KafkaError("Connection failed")
    
    # Execute
    result = news_collector.publish_to_kafka(news_data)
    
    # Assert
    assert result is False


def test_collect_with_mixed_results(news_collector, mock_symbol_manager, mock_vnstock_client):
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
        company_mock = Mock()
        df = pd.DataFrame({
            'title': [f'News about {symbol}'],
            'content': [f'Content about {symbol}'],
            'source': ['cafef.vn'],
            'published_date': ['2024-01-15T08:00:00Z']
        })
        company_mock.news.return_value = df
        stock_mock.company = company_mock
        return stock_mock
    
    mock_vnstock_client.stock = Mock(side_effect=mock_stock_data)
    
    # Execute
    result = news_collector.collect()
    
    # Assert
    assert result.success_count == 2
    assert result.failure_count == 2
    assert result.total_symbols == 4
    assert len(result.failed_symbols) == 2
    assert result.success is False


def test_collect_with_kafka_publish_failure(news_collector, mock_symbol_manager, mock_vnstock_client, mock_kafka_producer):
    """Test collection when Kafka publishing fails."""
    # Setup
    test_symbols = ['VNM']
    mock_symbol_manager.get_active_symbols.return_value = test_symbols
    
    # Mock vnstock to return valid data
    def mock_stock_data(symbol, source):
        stock_mock = Mock()
        company_mock = Mock()
        df = pd.DataFrame({
            'title': [f'News about {symbol}'],
            'content': [f'Content about {symbol}'],
            'source': ['cafef.vn'],
            'published_date': ['2024-01-15T08:00:00Z']
        })
        company_mock.news.return_value = df
        stock_mock.company = company_mock
        return stock_mock
    
    mock_vnstock_client.stock = Mock(side_effect=mock_stock_data)
    
    # Mock Kafka to fail
    mock_kafka_producer.send.side_effect = KafkaError("Connection failed")
    
    # Execute
    result = news_collector.collect()
    
    # Assert
    assert result.success_count == 0
    assert result.failure_count == 1
    assert result.total_symbols == 1
    assert 'VNM' in result.failed_symbols


def test_news_data_to_dict():
    """Test NewsData conversion to dictionary."""
    news_data = NewsData(
        symbol='VNM',
        title='Breaking news about VNM',
        content='Important content about VNM stock',
        source='cafef.vn',
        published_at='2024-01-15T08:00:00Z',
        collected_at='2024-01-15T08:05:00Z'
    )
    
    data_dict = news_data.to_dict()
    
    assert data_dict['symbol'] == 'VNM'
    assert data_dict['title'] == 'Breaking news about VNM'
    assert data_dict['content'] == 'Important content about VNM stock'
    assert data_dict['source'] == 'cafef.vn'
    assert data_dict['published_at'] == '2024-01-15T08:00:00Z'
    assert data_dict['collected_at'] == '2024-01-15T08:05:00Z'


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


def test_collect_with_malformed_news_data(news_collector, mock_symbol_manager, mock_vnstock_client):
    """Test collection when news data has missing fields."""
    # Setup
    test_symbols = ['VNM']
    mock_symbol_manager.get_active_symbols.return_value = test_symbols
    
    # Mock vnstock to return data with missing fields
    def mock_stock_data(symbol, source):
        stock_mock = Mock()
        company_mock = Mock()
        df = pd.DataFrame({
            'title': ['News title'],
            # Missing 'content' field
            'source': ['cafef.vn'],
            # Missing 'published_date' field
        })
        company_mock.news.return_value = df
        stock_mock.company = company_mock
        return stock_mock
    
    mock_vnstock_client.stock = Mock(side_effect=mock_stock_data)
    
    # Execute
    result = news_collector.collect()
    
    # Assert - should handle missing fields gracefully
    assert result.success_count == 1
    assert result.failure_count == 0
    assert result.total_symbols == 1


def test_collect_with_multiple_articles_per_symbol(news_collector, mock_symbol_manager, mock_vnstock_client, mock_kafka_producer):
    """Test collection when a symbol has multiple news articles."""
    # Setup
    test_symbols = ['VNM']
    mock_symbol_manager.get_active_symbols.return_value = test_symbols
    
    # Mock vnstock to return multiple articles
    def mock_stock_data(symbol, source):
        stock_mock = Mock()
        company_mock = Mock()
        df = pd.DataFrame({
            'title': ['News 1', 'News 2', 'News 3'],
            'content': ['Content 1', 'Content 2', 'Content 3'],
            'source': ['cafef.vn', 'vnexpress.net', 'vietstock.vn'],
            'published_date': ['2024-01-15T08:00:00Z', '2024-01-15T09:00:00Z', '2024-01-15T10:00:00Z']
        })
        company_mock.news.return_value = df
        stock_mock.company = company_mock
        return stock_mock
    
    mock_vnstock_client.stock = Mock(side_effect=mock_stock_data)
    
    # Execute
    result = news_collector.collect()
    
    # Assert
    assert result.success_count == 1
    assert result.failure_count == 0
    assert result.total_symbols == 1
    
    # Verify that Kafka producer was called 3 times (once per article)
    assert mock_kafka_producer.send.call_count == 3
