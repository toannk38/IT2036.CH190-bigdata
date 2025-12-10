"""
Property-based tests for AIMLEngine.

Tests universal properties that should hold across all valid executions.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pymongo import MongoClient

from src.engines.aiml_engine import AIMLEngine, AnalysisResult, TrendPrediction


# Hypothesis strategies for generating test data
price_strategy = st.floats(min_value=1000.0, max_value=1000000.0, allow_nan=False, allow_infinity=False)
volume_strategy = st.integers(min_value=0, max_value=100000000)

# Strategy for generating price series (list of prices)
price_series_strategy = st.lists(
    price_strategy,
    min_size=20,  # Minimum for technical analysis
    max_size=100
)


def create_price_dataframe(prices):
    """
    Create a DataFrame with price data from a list of close prices.
    
    Args:
        prices: List of close prices
        
    Returns:
        DataFrame with OHLCV data
    """
    n = len(prices)
    
    # Generate realistic OHLCV data based on close prices
    data = {
        'timestamp': pd.date_range(end=datetime.utcnow(), periods=n, freq='D'),
        'close': prices,
        'open': [p * np.random.uniform(0.98, 1.02) for p in prices],
        'high': [p * np.random.uniform(1.0, 1.05) for p in prices],
        'low': [p * np.random.uniform(0.95, 1.0) for p in prices],
        'volume': [np.random.randint(100000, 10000000) for _ in range(n)]
    }
    
    return pd.DataFrame(data)


def create_mock_mongo_client():
    """Create a mock MongoDB client."""
    mock_client = Mock(spec=MongoClient)
    mock_db = Mock()
    mock_price_collection = Mock()
    mock_analysis_collection = Mock()
    
    mock_db.__getitem__ = Mock(side_effect=lambda x: {
        'price_history': mock_price_collection,
        'ai_analysis': mock_analysis_collection
    }.get(x))
    
    mock_client.__getitem__ = Mock(return_value=mock_db)
    
    return mock_client


@given(prices=price_series_strategy)
@settings(max_examples=100, deadline=None)
def test_property_14_risk_score_validity(prices):
    """
    **Feature: vietnam-stock-ai-backend, Property 14: Risk score validity**
    **Validates: Requirements 4.3**
    
    For any price data analyzed by the AI/ML Engine, the calculated risk score 
    should be a valid number between 0 and 1
    
    This property verifies that:
    1. Risk score is always between 0.0 and 1.0 (inclusive)
    2. Risk score is a valid float (not NaN or infinity)
    3. Risk score calculation handles various price patterns
    """
    # Create price DataFrame
    price_data = create_price_dataframe(prices)
    
    # Create mock MongoDB client
    mock_mongo_client = create_mock_mongo_client()
    
    # Create engine
    engine = AIMLEngine(mock_mongo_client, database_name='test_db')
    
    # Calculate risk score
    risk_score = engine.calculate_risk_score(price_data)
    
    # Property verification: Risk score must be between 0 and 1
    assert isinstance(risk_score, float), \
        f"Risk score should be a float, but got {type(risk_score)}"
    
    assert not np.isnan(risk_score), \
        "Risk score should not be NaN"
    
    assert not np.isinf(risk_score), \
        "Risk score should not be infinity"
    
    assert 0.0 <= risk_score <= 1.0, \
        f"Risk score should be between 0.0 and 1.0, but got {risk_score}"


@given(prices=price_series_strategy)
@settings(max_examples=100, deadline=None)
def test_property_15_technical_score_validity(prices):
    """
    **Feature: vietnam-stock-ai-backend, Property 15: Technical score validity**
    **Validates: Requirements 4.4**
    
    For any price data analyzed by the AI/ML Engine, the calculated technical score 
    should be a valid number between 0 and 1
    
    This property verifies that:
    1. Technical score is always between 0.0 and 1.0 (inclusive)
    2. Technical score is a valid float (not NaN or infinity)
    3. Technical score calculation handles various price patterns
    """
    # Create price DataFrame
    price_data = create_price_dataframe(prices)
    
    # Create mock MongoDB client
    mock_mongo_client = create_mock_mongo_client()
    
    # Create engine
    engine = AIMLEngine(mock_mongo_client, database_name='test_db')
    
    # Calculate technical score
    technical_score = engine.calculate_technical_score(price_data)
    
    # Property verification: Technical score must be between 0 and 1
    assert isinstance(technical_score, float), \
        f"Technical score should be a float, but got {type(technical_score)}"
    
    assert not np.isnan(technical_score), \
        "Technical score should not be NaN"
    
    assert not np.isinf(technical_score), \
        "Technical score should not be infinity"
    
    assert 0.0 <= technical_score <= 1.0, \
        f"Technical score should be between 0.0 and 1.0, but got {technical_score}"


@given(
    symbol=st.text(
        alphabet=st.characters(whitelist_categories=('Lu',)),
        min_size=3,
        max_size=5
    ),
    prices=price_series_strategy
)
@settings(max_examples=100, deadline=None)
def test_property_16_aiml_results_storage_completeness(symbol, prices):
    """
    **Feature: vietnam-stock-ai-backend, Property 16: AI/ML results storage completeness**
    **Validates: Requirements 4.5**
    
    For any completed AI/ML analysis, the results stored in `ai_analysis` collection 
    should include timestamp, stock symbol, trend prediction, risk score, and technical score
    
    This property verifies that:
    1. All required fields are present in the stored result
    2. Field values are of the correct type
    3. The storage operation completes successfully
    """
    # Create price DataFrame
    price_data = create_price_dataframe(prices)
    
    # Create mock MongoDB client
    mock_mongo_client = create_mock_mongo_client()
    mock_db = mock_mongo_client['test_db']
    mock_analysis_collection = mock_db['ai_analysis']
    
    # Track what was inserted
    inserted_documents = []
    
    def mock_insert_one(document):
        inserted_documents.append(document)
        return Mock(inserted_id='mock_id')
    
    mock_analysis_collection.insert_one = Mock(side_effect=mock_insert_one)
    
    # Mock the price data retrieval to return our test data
    def mock_find(*args, **kwargs):
        # Convert DataFrame to list of dicts
        records = price_data.to_dict('records')
        for record in records:
            record['symbol'] = symbol
            record['timestamp'] = record['timestamp'].isoformat()
        return records
    
    mock_price_collection = mock_db['price_history']
    mock_price_collection.find = Mock(side_effect=mock_find)
    
    # Create engine
    engine = AIMLEngine(mock_mongo_client, database_name='test_db')
    
    # Perform analysis
    result = engine.analyze_stock(symbol, lookback_days=90)
    
    # Property verification: Result should be created
    assert result is not None, "Analysis should return a result"
    
    # Verify that a document was inserted
    assert len(inserted_documents) == 1, \
        f"Expected 1 document to be inserted, but got {len(inserted_documents)}"
    
    stored_doc = inserted_documents[0]
    
    # Verify all required fields are present
    required_fields = ['symbol', 'timestamp', 'trend_prediction', 'risk_score', 'technical_score', 'indicators']
    
    for field in required_fields:
        assert field in stored_doc, \
            f"Required field '{field}' is missing from stored document"
    
    # Verify field types and values
    assert stored_doc['symbol'] == symbol, \
        f"Expected symbol '{symbol}', but got '{stored_doc['symbol']}'"
    
    assert isinstance(stored_doc['timestamp'], str), \
        "Timestamp should be a string (ISO format)"
    
    assert isinstance(stored_doc['trend_prediction'], dict), \
        "Trend prediction should be a dictionary"
    
    # Verify trend prediction has required fields
    trend_fields = ['direction', 'confidence']
    for field in trend_fields:
        assert field in stored_doc['trend_prediction'], \
            f"Required field '{field}' is missing from trend_prediction"
    
    assert stored_doc['trend_prediction']['direction'] in ['up', 'down', 'neutral'], \
        f"Invalid trend direction: {stored_doc['trend_prediction']['direction']}"
    
    assert isinstance(stored_doc['risk_score'], float), \
        "Risk score should be a float"
    
    assert 0.0 <= stored_doc['risk_score'] <= 1.0, \
        f"Risk score should be between 0 and 1, but got {stored_doc['risk_score']}"
    
    assert isinstance(stored_doc['technical_score'], float), \
        "Technical score should be a float"
    
    assert 0.0 <= stored_doc['technical_score'] <= 1.0, \
        f"Technical score should be between 0 and 1, but got {stored_doc['technical_score']}"
    
    assert isinstance(stored_doc['indicators'], dict), \
        "Indicators should be a dictionary"
