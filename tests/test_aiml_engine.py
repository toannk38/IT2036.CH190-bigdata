"""
Unit tests for AIMLEngine.

Tests specific functionality and edge cases.
"""

import pytest
from unittest.mock import Mock, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pymongo import MongoClient

from src.engines.aiml_engine import AIMLEngine, AnalysisResult, TrendPrediction


@pytest.fixture
def mock_mongo_client():
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


@pytest.fixture
def aiml_engine(mock_mongo_client):
    """Create an AIMLEngine instance with mocked dependencies."""
    return AIMLEngine(mock_mongo_client, database_name='test_db')


def create_sample_price_data(num_days=90, base_price=50000):
    """
    Create sample price data for testing.
    
    Args:
        num_days: Number of days of data
        base_price: Base price for the stock
        
    Returns:
        DataFrame with OHLCV data
    """
    dates = pd.date_range(end=datetime.utcnow(), periods=num_days, freq='D')
    
    # Generate realistic price movements
    np.random.seed(42)  # For reproducibility
    returns = np.random.normal(0.001, 0.02, num_days)  # 0.1% mean, 2% std
    prices = base_price * np.exp(np.cumsum(returns))
    
    data = {
        'timestamp': dates,
        'close': prices,
        'open': prices * np.random.uniform(0.98, 1.02, num_days),
        'high': prices * np.random.uniform(1.0, 1.05, num_days),
        'low': prices * np.random.uniform(0.95, 1.0, num_days),
        'volume': np.random.randint(100000, 10000000, num_days)
    }
    
    return pd.DataFrame(data)


def test_aiml_engine_initialization(aiml_engine):
    """Test that AIMLEngine initializes correctly."""
    assert aiml_engine.db is not None
    assert aiml_engine.price_collection is not None
    assert aiml_engine.analysis_collection is not None


def test_calculate_trend_with_sufficient_data(aiml_engine):
    """Test trend calculation with sufficient historical data."""
    # Create sample data with upward trend
    price_data = create_sample_price_data(num_days=60, base_price=50000)
    
    # Add a clear upward trend
    price_data['close'] = price_data['close'] * np.linspace(1.0, 1.2, len(price_data))
    
    # Execute
    trend = aiml_engine.calculate_trend(price_data)
    
    # Assert
    assert isinstance(trend, TrendPrediction)
    assert trend.direction in ['up', 'down', 'neutral']
    assert 0.0 <= trend.confidence <= 1.0
    assert trend.predicted_price is None or isinstance(trend.predicted_price, float)


def test_calculate_trend_with_limited_data(aiml_engine):
    """Test trend calculation with limited data (less than 50 periods)."""
    # Create sample data with only 30 days
    price_data = create_sample_price_data(num_days=30, base_price=50000)
    
    # Execute
    trend = aiml_engine.calculate_trend(price_data)
    
    # Assert
    assert isinstance(trend, TrendPrediction)
    assert trend.direction in ['up', 'down', 'neutral']
    assert 0.0 <= trend.confidence <= 1.0


def test_calculate_trend_with_minimal_data(aiml_engine):
    """Test trend calculation with minimal data (less than 5 periods)."""
    # Create sample data with only 3 days
    price_data = create_sample_price_data(num_days=3, base_price=50000)
    
    # Execute
    trend = aiml_engine.calculate_trend(price_data)
    
    # Assert
    assert isinstance(trend, TrendPrediction)
    assert trend.direction == 'neutral'
    assert trend.confidence == 0.0


def test_calculate_risk_score_with_high_volatility(aiml_engine):
    """Test risk score calculation with high volatility data."""
    # Create sample data with high volatility
    price_data = create_sample_price_data(num_days=60, base_price=50000)
    
    # Add high volatility
    np.random.seed(42)
    price_data['close'] = price_data['close'] * (1 + np.random.normal(0, 0.1, len(price_data)))
    
    # Execute
    risk_score = aiml_engine.calculate_risk_score(price_data)
    
    # Assert
    assert isinstance(risk_score, float)
    assert 0.0 <= risk_score <= 1.0
    # High volatility should result in higher risk score
    assert risk_score > 0.3


def test_calculate_risk_score_with_low_volatility(aiml_engine):
    """Test risk score calculation with low volatility data."""
    # Create sample data with low volatility
    price_data = create_sample_price_data(num_days=60, base_price=50000)
    
    # Add low volatility (almost flat)
    price_data['close'] = 50000 + np.random.normal(0, 100, len(price_data))
    
    # Execute
    risk_score = aiml_engine.calculate_risk_score(price_data)
    
    # Assert
    assert isinstance(risk_score, float)
    assert 0.0 <= risk_score <= 1.0
    # Low volatility should result in lower risk score
    assert risk_score < 0.5


def test_calculate_risk_score_with_insufficient_data(aiml_engine):
    """Test risk score calculation with insufficient data."""
    # Create sample data with only 1 day
    price_data = create_sample_price_data(num_days=1, base_price=50000)
    
    # Execute
    risk_score = aiml_engine.calculate_risk_score(price_data)
    
    # Assert
    assert isinstance(risk_score, float)
    assert risk_score == 0.5  # Should return default medium risk


def test_calculate_technical_score_with_sufficient_data(aiml_engine):
    """Test technical score calculation with sufficient data."""
    # Create sample data
    price_data = create_sample_price_data(num_days=60, base_price=50000)
    
    # Execute
    technical_score = aiml_engine.calculate_technical_score(price_data)
    
    # Assert
    assert isinstance(technical_score, float)
    assert 0.0 <= technical_score <= 1.0


def test_calculate_technical_score_with_insufficient_data(aiml_engine):
    """Test technical score calculation with insufficient data."""
    # Create sample data with only 10 days (less than 26 needed for MACD)
    price_data = create_sample_price_data(num_days=10, base_price=50000)
    
    # Execute
    technical_score = aiml_engine.calculate_technical_score(price_data)
    
    # Assert
    assert isinstance(technical_score, float)
    assert technical_score == 0.5  # Should return default neutral score


def test_calculate_technical_score_with_oversold_rsi(aiml_engine):
    """Test technical score with oversold RSI condition."""
    # Create sample data with downward trend (oversold)
    price_data = create_sample_price_data(num_days=60, base_price=50000)
    
    # Create strong downward trend to get low RSI
    price_data['close'] = price_data['close'] * np.linspace(1.0, 0.7, len(price_data))
    
    # Execute
    technical_score = aiml_engine.calculate_technical_score(price_data)
    
    # Assert
    assert isinstance(technical_score, float)
    assert 0.0 <= technical_score <= 1.0


def test_analyze_stock_with_valid_data(aiml_engine, mock_mongo_client):
    """Test complete stock analysis with valid data."""
    # Setup
    symbol = 'VNM'
    price_data = create_sample_price_data(num_days=90, base_price=50000)
    
    # Convert to list of dicts for MongoDB mock
    records = price_data.to_dict('records')
    for record in records:
        record['symbol'] = symbol
        record['timestamp'] = record['timestamp'].isoformat()
    
    # Mock MongoDB query
    mock_db = mock_mongo_client['test_db']
    mock_price_collection = mock_db['price_history']
    mock_price_collection.find.return_value = records
    
    mock_analysis_collection = mock_db['ai_analysis']
    mock_analysis_collection.insert_one.return_value = Mock(inserted_id='mock_id')
    
    # Execute
    result = aiml_engine.analyze_stock(symbol, lookback_days=90)
    
    # Assert
    assert result is not None
    assert isinstance(result, AnalysisResult)
    assert result.symbol == symbol
    assert isinstance(result.timestamp, str)
    assert isinstance(result.trend_prediction, TrendPrediction)
    assert 0.0 <= result.risk_score <= 1.0
    assert 0.0 <= result.technical_score <= 1.0
    assert isinstance(result.indicators, dict)
    
    # Verify MongoDB insert was called
    assert mock_analysis_collection.insert_one.called


def test_analyze_stock_with_insufficient_data(aiml_engine, mock_mongo_client):
    """Test stock analysis with insufficient historical data."""
    # Setup
    symbol = 'VNM'
    price_data = create_sample_price_data(num_days=5, base_price=50000)  # Too little data
    
    # Convert to list of dicts for MongoDB mock
    records = price_data.to_dict('records')
    for record in records:
        record['symbol'] = symbol
        record['timestamp'] = record['timestamp'].isoformat()
    
    # Mock MongoDB query
    mock_db = mock_mongo_client['test_db']
    mock_price_collection = mock_db['price_history']
    mock_price_collection.find.return_value = records
    
    # Execute
    result = aiml_engine.analyze_stock(symbol, lookback_days=90)
    
    # Assert
    assert result is None  # Should return None for insufficient data


def test_analyze_stock_with_no_data(aiml_engine, mock_mongo_client):
    """Test stock analysis when no historical data is available."""
    # Setup
    symbol = 'VNM'
    
    # Mock MongoDB query to return empty list
    mock_db = mock_mongo_client['test_db']
    mock_price_collection = mock_db['price_history']
    mock_price_collection.find.return_value = []
    
    # Execute
    result = aiml_engine.analyze_stock(symbol, lookback_days=90)
    
    # Assert
    assert result is None  # Should return None for no data


def test_calculate_indicators(aiml_engine):
    """Test calculation of technical indicators."""
    # Create sample data
    price_data = create_sample_price_data(num_days=60, base_price=50000)
    
    # Execute
    indicators = aiml_engine._calculate_indicators(price_data)
    
    # Assert
    assert isinstance(indicators, dict)
    # Should have at least some indicators
    assert len(indicators) > 0
    
    # Check for expected indicators
    if 'rsi' in indicators:
        assert isinstance(indicators['rsi'], float)
        assert 0 <= indicators['rsi'] <= 100
    
    if 'macd' in indicators:
        assert isinstance(indicators['macd'], float)
    
    if 'moving_avg_20' in indicators:
        assert isinstance(indicators['moving_avg_20'], float)
        assert indicators['moving_avg_20'] > 0


def test_store_result(aiml_engine, mock_mongo_client):
    """Test storing analysis result in MongoDB."""
    # Setup
    trend = TrendPrediction(direction='up', confidence=0.75, predicted_price=55000.0)
    result = AnalysisResult(
        symbol='VNM',
        timestamp=datetime.utcnow().isoformat(),
        trend_prediction=trend,
        risk_score=0.35,
        technical_score=0.72,
        indicators={'rsi': 65.0, 'macd': 1250.0}
    )
    
    # Mock MongoDB insert
    mock_db = mock_mongo_client['test_db']
    mock_analysis_collection = mock_db['ai_analysis']
    mock_analysis_collection.insert_one.return_value = Mock(inserted_id='mock_id')
    
    # Execute
    success = aiml_engine._store_result(result)
    
    # Assert
    assert success is True
    assert mock_analysis_collection.insert_one.called
    
    # Verify the document structure
    call_args = mock_analysis_collection.insert_one.call_args
    document = call_args[0][0]
    
    assert document['symbol'] == 'VNM'
    assert 'timestamp' in document
    assert 'trend_prediction' in document
    assert document['risk_score'] == 0.35
    assert document['technical_score'] == 0.72
    assert 'indicators' in document
