"""
Property-based tests for API Service.
Tests universal properties that should hold across all valid inputs.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from fastapi import HTTPException

from src.services.api_service import APIService


# Strategies for generating test data
@st.composite
def valid_symbol(draw):
    """Generate valid stock symbol (1-10 uppercase letters)."""
    return draw(st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu',))))


@st.composite
def price_data(draw):
    """Generate valid price data."""
    base_price = draw(st.floats(min_value=1000, max_value=100000))
    return {
        'symbol': draw(valid_symbol()),
        'timestamp': datetime.utcnow().isoformat(),
        'open': base_price,
        'close': draw(st.floats(min_value=base_price * 0.9, max_value=base_price * 1.1)),
        'high': draw(st.floats(min_value=base_price, max_value=base_price * 1.2)),
        'low': draw(st.floats(min_value=base_price * 0.8, max_value=base_price)),
        'volume': draw(st.integers(min_value=1000, max_value=10000000))
    }


@st.composite
def ai_analysis_data(draw):
    """Generate valid AI/ML analysis data."""
    return {
        'symbol': draw(valid_symbol()),
        'timestamp': datetime.utcnow().isoformat(),
        'technical_score': draw(st.floats(min_value=0.0, max_value=1.0)),
        'risk_score': draw(st.floats(min_value=0.0, max_value=1.0)),
        'trend_prediction': {
            'direction': draw(st.sampled_from(['up', 'down', 'neutral'])),
            'confidence': draw(st.floats(min_value=0.0, max_value=1.0)),
            'predicted_price': draw(st.floats(min_value=1000, max_value=100000))
        },
        'indicators': {
            'rsi': draw(st.floats(min_value=0, max_value=100)),
            'macd': draw(st.floats(min_value=-1000, max_value=1000))
        }
    }


@st.composite
def llm_analysis_data(draw):
    """Generate valid LLM analysis data."""
    return {
        'symbol': draw(valid_symbol()),
        'timestamp': datetime.utcnow().isoformat(),
        'sentiment': {
            'overall': draw(st.sampled_from(['positive', 'negative', 'neutral'])),
            'score': draw(st.floats(min_value=-1.0, max_value=1.0)),
            'confidence': draw(st.floats(min_value=0.0, max_value=1.0))
        },
        'summary': draw(st.text(min_size=10, max_size=200)),
        'influence_score': draw(st.floats(min_value=0.0, max_value=1.0)),
        'articles_analyzed': draw(st.integers(min_value=1, max_value=50))
    }


@st.composite
def final_score_data(draw):
    """Generate valid final score data."""
    return {
        'symbol': draw(valid_symbol()),
        'timestamp': datetime.utcnow().isoformat(),
        'final_score': draw(st.floats(min_value=0.0, max_value=100.0)),
        'recommendation': draw(st.sampled_from(['BUY', 'WATCH', 'RISK'])),
        'components': {
            'technical_score': draw(st.floats(min_value=0.0, max_value=1.0)),
            'risk_score': draw(st.floats(min_value=0.0, max_value=1.0)),
            'sentiment_score': draw(st.floats(min_value=0.0, max_value=1.0))
        },
        'alerts': [
            {
                'type': draw(st.sampled_from(['BUY', 'WATCH', 'RISK'])),
                'priority': draw(st.sampled_from(['high', 'medium', 'low'])),
                'message': draw(st.text(min_size=10, max_size=100))
            }
        ]
    }


@settings(max_examples=100)
@given(
    symbol=valid_symbol(),
    price=price_data(),
    ai_analysis=ai_analysis_data(),
    llm_analysis=llm_analysis_data(),
    final_score=final_score_data()
)
def test_property_24_stock_summary_response_completeness(
    symbol, price, ai_analysis, llm_analysis, final_score
):
    """
    **Feature: vietnam-stock-ai-backend, Property 24: Stock summary response completeness**
    
    For any valid stock symbol requested via API, the response should include current 
    price data, AI/ML scores, LLM sentiment, and final recommendation.
    
    **Validates: Requirements 7.1**
    """
    # Create mock MongoDB client
    mock_client = MagicMock()
    mock_db = MagicMock()
    
    # Ensure all data uses the same symbol
    price['symbol'] = symbol
    ai_analysis['symbol'] = symbol
    llm_analysis['symbol'] = symbol
    final_score['symbol'] = symbol
    
    # Create mock collections
    mock_symbols = MagicMock()
    mock_price = MagicMock()
    mock_ai = MagicMock()
    mock_llm = MagicMock()
    mock_final = MagicMock()
    
    # Setup find_one to return our test data
    mock_symbols.find_one = MagicMock(return_value={'symbol': symbol, 'active': True})
    mock_price.find_one = MagicMock(return_value=price)
    mock_ai.find_one = MagicMock(return_value=ai_analysis)
    mock_llm.find_one = MagicMock(return_value=llm_analysis)
    mock_final.find_one = MagicMock(return_value=final_score)
    
    # Setup database to return correct collections
    collections = {
        'symbols': mock_symbols,
        'price_history': mock_price,
        'ai_analysis': mock_ai,
        'llm_analysis': mock_llm,
        'final_scores': mock_final
    }
    mock_db.__getitem__ = MagicMock(side_effect=lambda name: collections.get(name, MagicMock()))
    mock_client.__getitem__ = MagicMock(return_value=mock_db)
    
    # Create API service
    api_service = APIService(mock_client)
    
    # Get stock summary
    summary = api_service.get_stock_summary(symbol)
    
    # Property: Response should not be None
    assert summary is not None, "Stock summary should not be None"
    
    # Property: Response should include symbol
    assert summary.symbol == symbol, \
        f"Summary symbol {summary.symbol} should match requested symbol {symbol}"
    
    # Property: Response should include current price data
    assert summary.current_price is not None, \
        "Summary should include current price data"
    assert summary.current_price.open == price['open'], \
        "Price data should match source"
    assert summary.current_price.close == price['close'], \
        "Price data should match source"
    assert summary.current_price.high == price['high'], \
        "Price data should match source"
    assert summary.current_price.low == price['low'], \
        "Price data should match source"
    assert summary.current_price.volume == price['volume'], \
        "Price data should match source"
    
    # Property: Response should include AI/ML analysis
    assert summary.ai_ml_analysis is not None, \
        "Summary should include AI/ML analysis"
    assert 'risk_score' in summary.ai_ml_analysis, \
        "AI/ML analysis should include risk_score"
    assert 'technical_score' in summary.ai_ml_analysis, \
        "AI/ML analysis should include technical_score"
    assert 'trend_prediction' in summary.ai_ml_analysis, \
        "AI/ML analysis should include trend_prediction"
    
    # Property: Response should include LLM analysis
    assert summary.llm_analysis is not None, \
        "Summary should include LLM analysis"
    assert 'sentiment' in summary.llm_analysis, \
        "LLM analysis should include sentiment"
    
    # Property: Response should include final score
    assert summary.final_score is not None, \
        "Summary should include final score"
    assert 0.0 <= summary.final_score <= 100.0, \
        f"Final score {summary.final_score} should be in range [0, 100]"
    
    # Property: Response should include recommendation
    assert summary.recommendation is not None, \
        "Summary should include recommendation"
    assert summary.recommendation in ['BUY', 'WATCH', 'RISK'], \
        f"Recommendation {summary.recommendation} should be one of BUY, WATCH, RISK"
    
    # Property: Response should include component scores
    assert summary.component_scores is not None, \
        "Summary should include component scores"
    assert hasattr(summary.component_scores, 'technical_score'), \
        "Component scores should include technical_score"
    assert hasattr(summary.component_scores, 'risk_score'), \
        "Component scores should include risk_score"
    assert hasattr(summary.component_scores, 'sentiment_score'), \
        "Component scores should include sentiment_score"
    
    # Property: Response should include alerts
    assert summary.alerts is not None, \
        "Summary should include alerts"
    assert isinstance(summary.alerts, list), \
        "Alerts should be a list"
    
    # Property: Response should include last_updated timestamp
    assert summary.last_updated is not None, \
        "Summary should include last_updated timestamp"


@settings(max_examples=100)
@given(
    num_alerts=st.integers(min_value=1, max_value=100),
    limit=st.integers(min_value=1, max_value=50),
    offset=st.integers(min_value=0, max_value=50)
)
def test_property_25_alert_list_sorting(num_alerts, limit, offset):
    """
    **Feature: vietnam-stock-ai-backend, Property 25: Alert list sorting**
    
    For any alert list returned by the API, alerts should be sorted first by priority 
    (high, medium, low) then by timestamp (most recent first).
    
    **Validates: Requirements 7.2**
    """
    # Create mock MongoDB client
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_final_scores = MagicMock()
    
    # Generate test alerts with random priorities and timestamps
    test_alerts = []
    priorities = ['high', 'medium', 'low']
    alert_types = ['BUY', 'WATCH', 'RISK']
    
    for i in range(num_alerts):
        # Generate timestamp with some variation
        timestamp = (datetime.utcnow() - timedelta(hours=i)).isoformat()
        priority = priorities[i % 3]
        alert_type = alert_types[i % 3]
        
        test_alerts.append({
            'symbol': f'SYM{i}',
            'timestamp': timestamp,
            'final_score': 50.0 + i,
            'recommendation': alert_type,
            'alerts': {
                'type': alert_type,
                'priority': priority,
                'message': f'Test alert {i}'
            }
        })
    
    # Mock the aggregation pipeline to return sorted alerts
    def mock_aggregate(pipeline):
        # Simulate the sorting behavior
        result = []
        for alert_doc in test_alerts:
            result.append({
                'symbol': alert_doc['symbol'],
                'timestamp': alert_doc['timestamp'],
                'final_score': alert_doc['final_score'],
                'recommendation': alert_doc['recommendation'],
                'alert': alert_doc['alerts']
            })
        
        # Sort by priority order then timestamp
        priority_order = {'high': 1, 'medium': 2, 'low': 3}
        result.sort(key=lambda x: (priority_order[x['alert']['priority']], x['timestamp']), reverse=True)
        result.sort(key=lambda x: priority_order[x['alert']['priority']])
        
        return result
    
    mock_final_scores.aggregate = mock_aggregate
    
    collections = {
        'final_scores': mock_final_scores
    }
    mock_db.__getitem__ = MagicMock(side_effect=lambda name: collections.get(name, MagicMock()))
    mock_client.__getitem__ = MagicMock(return_value=mock_db)
    
    # Create API service
    api_service = APIService(mock_client)
    
    # Get alerts
    response = api_service.get_alerts(limit=limit, offset=offset)
    
    # Property: Response should not be None
    assert response is not None, "Alert response should not be None"
    
    # Property: Response should have correct structure
    assert hasattr(response, 'alerts'), "Response should have alerts field"
    assert hasattr(response, 'total'), "Response should have total field"
    assert hasattr(response, 'page'), "Response should have page field"
    assert hasattr(response, 'page_size'), "Response should have page_size field"
    
    # Property: Alerts should be a list
    assert isinstance(response.alerts, list), "Alerts should be a list"
    
    # Property: Total should match number of generated alerts
    assert response.total == num_alerts, \
        f"Total {response.total} should match generated alerts {num_alerts}"
    
    # Property: Returned alerts should respect pagination
    expected_count = min(limit, max(0, num_alerts - offset))
    assert len(response.alerts) == expected_count, \
        f"Expected {expected_count} alerts, got {len(response.alerts)}"
    
    # Property: Alerts should be sorted by priority first
    if len(response.alerts) > 1:
        priority_order = {'high': 1, 'medium': 2, 'low': 3}
        for i in range(len(response.alerts) - 1):
            current_priority = priority_order[response.alerts[i]['priority']]
            next_priority = priority_order[response.alerts[i + 1]['priority']]
            
            # Current priority should be <= next priority (high comes first)
            assert current_priority <= next_priority, \
                f"Alert {i} priority {response.alerts[i]['priority']} should come before " \
                f"alert {i+1} priority {response.alerts[i+1]['priority']}"
            
            # If priorities are equal, timestamps should be in descending order (most recent first)
            if current_priority == next_priority:
                current_time = datetime.fromisoformat(response.alerts[i]['timestamp'])
                next_time = datetime.fromisoformat(response.alerts[i + 1]['timestamp'])
                assert current_time >= next_time, \
                    f"Alert {i} timestamp should be more recent than alert {i+1} for same priority"


@settings(max_examples=100)
@given(
    symbol=valid_symbol(),
    num_data_points=st.integers(min_value=1, max_value=50),
    days_range=st.integers(min_value=1, max_value=365)
)
def test_property_26_historical_data_date_range_filtering(symbol, num_data_points, days_range):
    """
    **Feature: vietnam-stock-ai-backend, Property 26: Historical data date range filtering**
    
    For any historical analysis request with start and end dates, all returned data 
    should have timestamps within the specified date range (inclusive).
    
    **Validates: Requirements 7.3**
    """
    # Create mock MongoDB client
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_symbols = MagicMock()
    mock_final_scores = MagicMock()
    
    # Setup symbol to exist
    mock_symbols.find_one = MagicMock(return_value={'symbol': symbol, 'active': True})
    
    # Generate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days_range)
    
    # Generate test data points within and outside the range
    test_data = []
    for i in range(num_data_points):
        # Generate timestamps within the range
        days_offset = (days_range * i) / num_data_points
        timestamp = start_date + timedelta(days=days_offset)
        
        test_data.append({
            'symbol': symbol,
            'timestamp': timestamp.isoformat(),
            'final_score': 50.0 + i,
            'recommendation': 'WATCH',
            'components': {
                'technical_score': 0.5,
                'risk_score': 0.3,
                'sentiment_score': 0.6
            }
        })
    
    # Mock find to return filtered data
    def mock_find(query, sort=None):
        # Filter by date range
        filtered = []
        for doc in test_data:
            doc_time = datetime.fromisoformat(doc['timestamp'])
            query_start = datetime.fromisoformat(query['timestamp']['$gte'])
            query_end = datetime.fromisoformat(query['timestamp']['$lte'])
            
            if query_start <= doc_time <= query_end:
                filtered.append(doc)
        
        return filtered
    
    mock_final_scores.find = mock_find
    
    collections = {
        'symbols': mock_symbols,
        'final_scores': mock_final_scores
    }
    mock_db.__getitem__ = MagicMock(side_effect=lambda name: collections.get(name, MagicMock()))
    mock_client.__getitem__ = MagicMock(return_value=mock_db)
    
    # Create API service
    api_service = APIService(mock_client)
    
    # Get historical analysis
    start_date_str = start_date.date().isoformat()
    end_date_str = end_date.date().isoformat()
    
    response = api_service.get_historical_analysis(symbol, start_date_str, end_date_str)
    
    # Property: Response should not be None
    assert response is not None, "Historical data response should not be None"
    
    # Property: Response should have correct structure
    assert response.symbol == symbol, "Response should have correct symbol"
    assert response.start_date == start_date_str, "Response should have correct start_date"
    assert response.end_date == end_date_str, "Response should have correct end_date"
    assert hasattr(response, 'data'), "Response should have data field"
    assert hasattr(response, 'total_points'), "Response should have total_points field"
    
    # Property: All returned data points should be within date range
    start_dt = datetime.fromisoformat(start_date_str)
    end_dt = datetime.fromisoformat(end_date_str)
    
    for point in response.data:
        point_time = datetime.fromisoformat(point.timestamp)
        
        assert start_dt <= point_time <= end_dt, \
            f"Data point timestamp {point.timestamp} should be within range " \
            f"[{start_date_str}, {end_date_str}]"
    
    # Property: Total points should match data length
    assert response.total_points == len(response.data), \
        f"Total points {response.total_points} should match data length {len(response.data)}"
    
    # Property: Each data point should have required fields
    for point in response.data:
        assert hasattr(point, 'timestamp'), "Data point should have timestamp"
        assert hasattr(point, 'final_score'), "Data point should have final_score"
        assert hasattr(point, 'recommendation'), "Data point should have recommendation"
        assert hasattr(point, 'components'), "Data point should have components"
        
        # Validate final score range
        assert 0.0 <= point.final_score <= 100.0, \
            f"Final score {point.final_score} should be in range [0, 100]"
        
        # Validate recommendation
        assert point.recommendation in ['BUY', 'WATCH', 'RISK'], \
            f"Recommendation {point.recommendation} should be one of BUY, WATCH, RISK"


@settings(max_examples=100)
@given(
    error_type=st.sampled_from(['invalid_symbol', 'invalid_date', 'invalid_params']),
    symbol=st.one_of(
        st.text(min_size=0, max_size=0),  # Empty symbol
        st.text(min_size=20, max_size=50),  # Too long symbol
        valid_symbol()  # Valid symbol (for other error types)
    )
)
def test_property_27_api_error_response_validity(error_type, symbol):
    """
    **Feature: vietnam-stock-ai-backend, Property 27: API error response validity**
    
    For any API request with invalid parameters, the response should include an 
    appropriate HTTP error code (4xx) and a descriptive error message.
    
    **Validates: Requirements 7.4**
    """
    # Create mock MongoDB client
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_symbols = MagicMock()
    mock_final_scores = MagicMock()
    
    # Setup different error scenarios
    if error_type == 'invalid_symbol':
        # Symbol doesn't exist in database
        mock_symbols.find_one = MagicMock(return_value=None)
    elif error_type == 'invalid_date':
        # Symbol exists but dates are invalid
        mock_symbols.find_one = MagicMock(return_value={'symbol': symbol, 'active': True})
    else:
        # Other parameter errors
        mock_symbols.find_one = MagicMock(return_value={'symbol': symbol, 'active': True})
    
    collections = {
        'symbols': mock_symbols,
        'final_scores': mock_final_scores
    }
    mock_db.__getitem__ = MagicMock(side_effect=lambda name: collections.get(name, MagicMock()))
    mock_client.__getitem__ = MagicMock(return_value=mock_db)
    
    # Create API service
    api_service = APIService(mock_client)
    
    # Test different error scenarios
    error_raised = False
    error_code = None
    error_message = None
    
    try:
        if error_type == 'invalid_symbol':
            # Try to get summary for non-existent symbol
            api_service.get_stock_summary(symbol)
        elif error_type == 'invalid_date':
            # Try to get historical data with invalid date format
            api_service.get_historical_analysis(symbol, 'invalid-date', '2024-01-01')
        else:
            # Try to get historical data with end_date before start_date
            api_service.get_historical_analysis(symbol, '2024-12-31', '2024-01-01')
    except HTTPException as e:
        error_raised = True
        error_code = e.status_code
        error_message = e.detail
    except Exception as e:
        # Other exceptions should also be caught
        error_raised = True
        error_code = 500
        error_message = str(e)
    
    # Property: An error should be raised for invalid input
    assert error_raised, \
        f"API should raise an error for {error_type}"
    
    # Property: Error code should be in 4xx range for client errors or 5xx for server errors
    assert error_code is not None, "Error should have a status code"
    assert 400 <= error_code < 600, \
        f"Error code {error_code} should be in range [400, 600)"
    
    # Property: Error message should be descriptive (not empty)
    assert error_message is not None, "Error should have a message"
    assert len(error_message) > 0, "Error message should not be empty"
    assert isinstance(error_message, str), "Error message should be a string"
    
    # Property: Client errors (invalid input) should return 4xx codes
    if error_type in ['invalid_symbol', 'invalid_date', 'invalid_params']:
        assert 400 <= error_code < 500, \
            f"Client error should return 4xx code, got {error_code}"
