"""
Property-based tests for AggregationService.
Tests universal properties that should hold across all valid inputs.
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import MagicMock
from datetime import datetime

from src.services.aggregation_service import AggregationService


# Strategies for generating test data
@st.composite
def ai_analysis_result(draw):
    """Generate valid AI/ML analysis result."""
    return {
        'symbol': draw(st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu',)))),
        'timestamp': datetime.utcnow().isoformat(),
        'technical_score': draw(st.floats(min_value=0.0, max_value=1.0)),
        'risk_score': draw(st.floats(min_value=0.0, max_value=1.0)),
        'trend_prediction': {
            'direction': draw(st.sampled_from(['up', 'down', 'neutral'])),
            'confidence': draw(st.floats(min_value=0.0, max_value=1.0))
        },
        'indicators': {}
    }


@st.composite
def llm_analysis_result(draw):
    """Generate valid LLM analysis result."""
    return {
        'symbol': draw(st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu',)))),
        'timestamp': datetime.utcnow().isoformat(),
        'sentiment': {
            'sentiment': draw(st.sampled_from(['positive', 'negative', 'neutral'])),
            'score': draw(st.floats(min_value=-1.0, max_value=1.0)),
            'confidence': draw(st.floats(min_value=0.0, max_value=1.0))
        },
        'summary': draw(st.text(min_size=10, max_size=200)),
        'influence_score': draw(st.floats(min_value=0.0, max_value=1.0)),
        'articles_analyzed': draw(st.integers(min_value=1, max_value=50))
    }


@settings(max_examples=100)
@given(ai_result=ai_analysis_result(), llm_result=llm_analysis_result())
def test_property_21_final_score_range_validity(ai_result, llm_result):
    """
    **Feature: vietnam-stock-ai-backend, Property 21: Final score range validity**
    
    For any aggregated analysis results, the calculated final recommendation score 
    should be between 0 and 100.
    
    **Validates: Requirements 6.3**
    """
    # Create mock MongoDB client
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    
    # Create service
    service = AggregationService(mock_client)
    
    # Calculate final score
    final_score = service.calculate_final_score(ai_result, llm_result)
    
    # Property: Final score must be between 0 and 100
    assert 0.0 <= final_score <= 100.0, \
        f"Final score {final_score} is outside valid range [0, 100]"
    
    # Additional check: score should be a valid float
    assert isinstance(final_score, float), \
        f"Final score should be float, got {type(final_score)}"


@settings(max_examples=100)
@given(
    ai_result=ai_analysis_result(),
    llm_result=llm_analysis_result(),
    weights=st.fixed_dictionaries({
        'technical': st.floats(min_value=0.0, max_value=1.0),
        'risk': st.floats(min_value=0.0, max_value=1.0),
        'sentiment': st.floats(min_value=0.0, max_value=1.0)
    })
)
def test_property_21_final_score_with_custom_weights(ai_result, llm_result, weights):
    """
    **Feature: vietnam-stock-ai-backend, Property 21: Final score range validity**
    
    For any aggregated analysis results with custom weights, the calculated final 
    recommendation score should be between 0 and 100.
    
    **Validates: Requirements 6.3**
    """
    # Create mock MongoDB client
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    
    # Create service with custom weights
    service = AggregationService(mock_client, weights=weights)
    
    # Calculate final score
    final_score = service.calculate_final_score(ai_result, llm_result)
    
    # Property: Final score must be between 0 and 100 regardless of weights
    assert 0.0 <= final_score <= 100.0, \
        f"Final score {final_score} with weights {weights} is outside valid range [0, 100]"


@settings(max_examples=100)
@given(final_score=st.floats(min_value=0.0, max_value=100.0))
def test_property_22_alert_generation_consistency(final_score):
    """
    **Feature: vietnam-stock-ai-backend, Property 22: Alert generation consistency**
    
    For any final score calculated, if the score is above 70, an alert of type BUY 
    should be generated; if between 40-70, type WATCH; if below 40, type RISK.
    
    **Validates: Requirements 6.4**
    """
    # Create mock MongoDB client
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    
    # Create service
    service = AggregationService(mock_client)
    
    # Generate alerts
    alerts = service.generate_alerts(final_score, 'TEST')
    
    # Property: Exactly one alert should be generated
    assert len(alerts) == 1, \
        f"Expected exactly 1 alert, got {len(alerts)}"
    
    alert = alerts[0]
    
    # Property: Alert type should match score threshold
    if final_score > 70:
        assert alert.type == 'BUY', \
            f"Score {final_score} > 70 should generate BUY alert, got {alert.type}"
        assert alert.priority == 'high', \
            f"BUY alert should have high priority, got {alert.priority}"
    elif final_score >= 40:
        assert alert.type == 'WATCH', \
            f"Score {final_score} in [40, 70] should generate WATCH alert, got {alert.type}"
        assert alert.priority == 'medium', \
            f"WATCH alert should have medium priority, got {alert.priority}"
    else:
        assert alert.type == 'RISK', \
            f"Score {final_score} < 40 should generate RISK alert, got {alert.type}"
        assert alert.priority == 'high', \
            f"RISK alert should have high priority, got {alert.priority}"
    
    # Property: Alert message should contain the symbol
    assert 'TEST' in alert.message, \
        f"Alert message should contain symbol 'TEST', got: {alert.message}"
    
    # Property: Alert message should contain the score
    assert str(round(final_score, 1)) in alert.message or str(int(final_score)) in alert.message, \
        f"Alert message should contain score {final_score}, got: {alert.message}"


@settings(max_examples=100)
@given(
    symbol=st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu',))),
    ai_result=ai_analysis_result(),
    llm_result=llm_analysis_result()
)
def test_property_23_final_scores_storage_completeness(symbol, ai_result, llm_result):
    """
    **Feature: vietnam-stock-ai-backend, Property 23: Final scores storage completeness**
    
    For any completed aggregation, the results stored in final_scores collection 
    should include timestamp, stock symbol, final score, recommendation, component 
    scores, and alerts.
    
    **Validates: Requirements 6.5**
    """
    # Create mock MongoDB client with proper collection structure
    mock_client = MagicMock()
    mock_db = MagicMock()
    
    # Create mock collections
    mock_ai_collection = MagicMock()
    mock_llm_collection = MagicMock()
    mock_final_collection = MagicMock()
    
    # Override symbol in test data to match
    ai_result['symbol'] = symbol
    llm_result['symbol'] = symbol
    
    # Setup find_one to return our test data
    mock_ai_collection.find_one = MagicMock(return_value=ai_result)
    mock_llm_collection.find_one = MagicMock(return_value=llm_result)
    mock_final_collection.insert_one = MagicMock()
    
    # Setup database to return correct collections
    def get_collection(self, name):
        if name == 'ai_analysis':
            return mock_ai_collection
        elif name == 'llm_analysis':
            return mock_llm_collection
        elif name == 'final_scores':
            return mock_final_collection
        return MagicMock()
    
    mock_db.__getitem__ = get_collection
    mock_client.__getitem__.return_value = mock_db
    
    # Create service
    service = AggregationService(mock_client)
    
    # Perform aggregation
    result = service.aggregate(symbol)
    
    # Property: Result should not be None
    assert result is not None, "Aggregation should return a result"
    
    # Property: Result should have all required fields
    assert hasattr(result, 'timestamp'), "Result should have timestamp"
    assert hasattr(result, 'symbol'), "Result should have symbol"
    assert hasattr(result, 'final_score'), "Result should have final_score"
    assert hasattr(result, 'recommendation'), "Result should have recommendation"
    assert hasattr(result, 'components'), "Result should have components"
    assert hasattr(result, 'alerts'), "Result should have alerts"
    
    # Property: Symbol should match
    assert result.symbol == symbol, \
        f"Result symbol {result.symbol} should match input symbol {symbol}"
    
    # Property: Final score should be valid
    assert 0.0 <= result.final_score <= 100.0, \
        f"Final score {result.final_score} should be in range [0, 100]"
    
    # Property: Recommendation should be valid
    assert result.recommendation in ['BUY', 'WATCH', 'RISK'], \
        f"Recommendation {result.recommendation} should be one of BUY, WATCH, RISK"
    
    # Property: Components should contain all required scores
    assert 'technical_score' in result.components, \
        "Components should include technical_score"
    assert 'risk_score' in result.components, \
        "Components should include risk_score"
    assert 'sentiment_score' in result.components, \
        "Components should include sentiment_score"
    
    # Property: Alerts should be a list
    assert isinstance(result.alerts, list), \
        f"Alerts should be a list, got {type(result.alerts)}"
    
    # Property: At least one alert should be generated
    assert len(result.alerts) > 0, \
        "At least one alert should be generated"
    
    # Property: Storage method should be called
    assert mock_final_collection.insert_one.called, \
        "Result should be stored in final_scores collection"
