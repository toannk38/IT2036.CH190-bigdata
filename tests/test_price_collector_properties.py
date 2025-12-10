"""
Property-based tests for PriceCollector.

Tests universal properties that should hold across all valid executions.
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, MagicMock, patch
from kafka import KafkaProducer
import pandas as pd

from src.collectors.price_collector import PriceCollector, PriceData, CollectionResult
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

price_strategy = st.floats(min_value=1000, max_value=1000000, allow_nan=False, allow_infinity=False)
volume_strategy = st.integers(min_value=0, max_value=100000000)


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
def test_property_5_symbol_based_price_collection(symbols):
    """
    **Feature: vietnam-stock-ai-backend, Property 5: Symbol-based price collection**
    **Validates: Requirements 1.2**
    
    For any price collection run, price data should be collected for all symbols 
    returned by get_active_symbols()
    
    This property verifies that:
    1. The collector attempts to fetch data for every active symbol
    2. The number of collection attempts equals the number of active symbols
    """
    # Create fresh mocks for each test iteration
    mock_kafka_producer = create_mock_kafka_producer()
    mock_vnstock_client = create_mock_vnstock_client()
    mock_symbol_manager = create_mock_symbol_manager()
    
    # Setup: Configure mock symbol manager to return the generated symbols
    mock_symbol_manager.get_active_symbols.return_value = symbols
    
    # Setup: Configure mock vnstock client to return valid price data
    def mock_stock_data(symbol, source):
        """Mock stock data factory."""
        stock_mock = Mock()
        quote_mock = Mock()
        
        # Create a DataFrame with price data
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
    
    # Create collector
    collector = PriceCollector(
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
    prices=st.lists(
        st.tuples(price_strategy, price_strategy, price_strategy, price_strategy, volume_strategy),
        min_size=1,
        max_size=20
    )
)
@settings(max_examples=100, deadline=None)
def test_property_6_price_data_kafka_publishing(symbols, prices):
    """
    **Feature: vietnam-stock-ai-backend, Property 6: Price data Kafka publishing**
    **Validates: Requirements 1.3**
    
    For any successfully retrieved price data, the data should be published to 
    the Kafka topic `stock_prices_raw`
    
    This property verifies that:
    1. All successfully collected price data is published to Kafka
    2. The Kafka producer is called for each successful data collection
    3. The correct topic name is used
    """
    # Create fresh mocks for each test iteration
    mock_kafka_producer = create_mock_kafka_producer()
    mock_vnstock_client = create_mock_vnstock_client()
    mock_symbol_manager = create_mock_symbol_manager()
    
    # Setup: Configure mock symbol manager to return the generated symbols
    # Limit to the number of price tuples we have
    test_symbols = symbols[:len(prices)]
    mock_symbol_manager.get_active_symbols.return_value = test_symbols
    
    # Setup: Configure mock vnstock client to return valid price data
    price_index = [0]  # Use list to allow mutation in nested function
    
    def mock_stock_data(symbol, source):
        """Mock stock data factory that returns different prices for each call."""
        stock_mock = Mock()
        quote_mock = Mock()
        
        # Get the price tuple for this symbol
        idx = price_index[0]
        if idx < len(prices):
            open_price, close_price, high_price, low_price, vol = prices[idx]
            price_index[0] += 1
        else:
            open_price, close_price, high_price, low_price, vol = 50000.0, 51000.0, 52000.0, 49000.0, 1000000
        
        # Create a DataFrame with price data
        df = pd.DataFrame({
            'open': [open_price],
            'close': [close_price],
            'high': [high_price],
            'low': [low_price],
            'volume': [vol]
        })
        
        quote_mock.history.return_value = df
        stock_mock.quote = quote_mock
        return stock_mock
    
    mock_vnstock_client.stock = Mock(side_effect=mock_stock_data)
    
    # Create collector
    collector = PriceCollector(
        kafka_producer=mock_kafka_producer,
        vnstock_client=mock_vnstock_client,
        symbol_manager=mock_symbol_manager
    )
    
    # Execute collection
    result = collector.collect()
    
    # Property verification: All successfully collected data should be published to Kafka
    # Since our mock always returns valid data, all collections should succeed
    assert result.success_count == len(test_symbols), \
        f"Expected {len(test_symbols)} successful collections, but got {result.success_count}"
    
    # Verify that Kafka producer was called for each successful collection
    assert mock_kafka_producer.send.call_count == len(test_symbols), \
        f"Kafka producer should be called once per successful collection ({len(test_symbols)} times), " \
        f"but was called {mock_kafka_producer.send.call_count} times"
    
    # Verify that all calls used the correct topic
    for call in mock_kafka_producer.send.call_args_list:
        args, kwargs = call
        # First positional argument should be the topic name
        assert args[0] == 'stock_prices_raw', \
            f"Expected topic 'stock_prices_raw', but got '{args[0]}'"
