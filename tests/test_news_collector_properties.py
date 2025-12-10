"""
Property-based tests for NewsCollector.

Tests universal properties that should hold across all valid executions.
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, MagicMock, patch
from kafka import KafkaProducer
import pandas as pd

from src.collectors.news_collector import NewsCollector, NewsData, CollectionResult
from src.services.symbol_manager import SymbolManager


# Hypothesis strategies for generating test data
symbol_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Lu',)),  # Uppercase letters
    min_size=3,
    max_size=5
)

symbols_list_strategy = st.lists(
    symbol_strategy,
    min_size=1,
    max_size=20,
    unique=True
)

news_title_strategy = st.text(min_size=10, max_size=200)
news_content_strategy = st.text(min_size=50, max_size=1000)
news_source_strategy = st.sampled_from(['cafef.vn', 'vnexpress.net', 'vietstock.vn', 'ndh.vn'])


def create_mock_kafka_producer():
    """Create a mock Kafka producer."""
    producer = Mock(spec=KafkaProducer)
    future = Mock()
    future.get.return_value = Mock(partition=0, offset=0)
    producer.send.return_value = future
    return producer


def create_mock_vnstock_client():
    """Create a mock vnstock client."""
    client = Mock()
    return client


def create_mock_symbol_manager():
    """Create a mock SymbolManager."""
    manager = Mock(spec=SymbolManager)
    return manager


@given(symbols=symbols_list_strategy)
@settings(max_examples=100, deadline=None)
def test_property_9_symbol_based_news_collection(symbols):
    """
    **Feature: vietnam-stock-ai-backend, Property 9: Symbol-based news collection**
    **Validates: Requirements 3.2**
    
    For any news collection run, news data should be collected for all symbols 
    returned by get_active_symbols()
    
    This property verifies that:
    1. The collector attempts to fetch news for every active symbol
    2. The number of collection attempts equals the number of active symbols
    """
    # Create fresh mocks for each test iteration
    mock_kafka_producer = create_mock_kafka_producer()
    mock_vnstock_client = create_mock_vnstock_client()
    mock_symbol_manager = create_mock_symbol_manager()
    
    # Setup: Configure mock symbol manager to return the generated symbols
    mock_symbol_manager.get_active_symbols.return_value = symbols
    
    # Setup: Configure mock vnstock client to return valid news data
    def mock_stock_data(symbol, source):
        """Mock stock data factory."""
        stock_mock = Mock()
        company_mock = Mock()
        
        # Create a DataFrame with news data
        df = pd.DataFrame({
            'title': ['Breaking news about ' + symbol],
            'content': ['This is important news content about ' + symbol],
            'source': ['cafef.vn'],
            'published_date': ['2024-01-15T08:00:00Z']
        })
        
        company_mock.news.return_value = df
        stock_mock.company = company_mock
        return stock_mock
    
    mock_vnstock_client.stock = Mock(side_effect=mock_stock_data)
    
    # Create collector
    collector = NewsCollector(
        kafka_producer=mock_kafka_producer,
        vnstock_client=mock_vnstock_client,
        symbol_manager=mock_symbol_manager
    )
    
    # Execute collection
    result = collector.collect()
    
    # Property verification: All symbols should be processed
    # The total number of attempts (success + failure) should equal the number of symbols
    assert result.total_symbols == len(symbols), \
        f"Expected {len(symbols)} symbols to be processed, but got {result.total_symbols}"
    
    assert result.success_count + result.failure_count == len(symbols), \
        f"Sum of successes ({result.success_count}) and failures ({result.failure_count}) " \
        f"should equal total symbols ({len(symbols)})"
    
    # Verify that vnstock client was called for each symbol
    assert mock_vnstock_client.stock.call_count == len(symbols), \
        f"vnstock client should be called once per symbol ({len(symbols)} times), " \
        f"but was called {mock_vnstock_client.stock.call_count} times"


@given(
    symbols=symbols_list_strategy,
    news_data=st.lists(
        st.tuples(news_title_strategy, news_content_strategy, news_source_strategy),
        min_size=1,
        max_size=20
    )
)
@settings(max_examples=100, deadline=None)
def test_property_10_news_data_kafka_publishing(symbols, news_data):
    """
    **Feature: vietnam-stock-ai-backend, Property 10: News data Kafka publishing**
    **Validates: Requirements 3.3**
    
    For any successfully retrieved news articles, the articles should be published to 
    the Kafka topic `stock_news_raw`
    
    This property verifies that:
    1. All successfully collected news articles are published to Kafka
    2. The Kafka producer is called for each article
    3. The correct topic name is used
    """
    # Create fresh mocks for each test iteration
    mock_kafka_producer = create_mock_kafka_producer()
    mock_vnstock_client = create_mock_vnstock_client()
    mock_symbol_manager = create_mock_symbol_manager()
    
    # Setup: Configure mock symbol manager to return the generated symbols
    # Limit to the number of news data tuples we have
    test_symbols = symbols[:len(news_data)]
    mock_symbol_manager.get_active_symbols.return_value = test_symbols
    
    # Setup: Configure mock vnstock client to return valid news data
    news_index = [0]  # Use list to allow mutation in nested function
    
    def mock_stock_data(symbol, source):
        """Mock stock data factory that returns different news for each call."""
        stock_mock = Mock()
        company_mock = Mock()
        
        # Get the news tuple for this symbol
        idx = news_index[0]
        if idx < len(news_data):
            title, content, src = news_data[idx]
            news_index[0] += 1
        else:
            title = 'Default news title'
            content = 'Default news content'
            src = 'cafef.vn'
        
        # Create a DataFrame with news data
        df = pd.DataFrame({
            'title': [title],
            'content': [content],
            'source': [src],
            'published_date': ['2024-01-15T08:00:00Z']
        })
        
        company_mock.news.return_value = df
        stock_mock.company = company_mock
        return stock_mock
    
    mock_vnstock_client.stock = Mock(side_effect=mock_stock_data)
    
    # Create collector
    collector = NewsCollector(
        kafka_producer=mock_kafka_producer,
        vnstock_client=mock_vnstock_client,
        symbol_manager=mock_symbol_manager
    )
    
    # Execute collection
    result = collector.collect()
    
    # Property verification: All successfully collected news should be published to Kafka
    # Since our mock always returns valid data (1 article per symbol), all collections should succeed
    assert result.success_count == len(test_symbols), \
        f"Expected {len(test_symbols)} successful collections, but got {result.success_count}"
    
    # Verify that Kafka producer was called for each article
    # Each symbol has 1 article, so we expect len(test_symbols) calls
    assert mock_kafka_producer.send.call_count == len(test_symbols), \
        f"Kafka producer should be called once per article ({len(test_symbols)} times), " \
        f"but was called {mock_kafka_producer.send.call_count} times"
    
    # Verify that all calls used the correct topic
    for call in mock_kafka_producer.send.call_args_list:
        args, kwargs = call
        # First positional argument should be the topic name
        assert args[0] == 'stock_news_raw', \
            f"Expected topic 'stock_news_raw', but got '{args[0]}'"
