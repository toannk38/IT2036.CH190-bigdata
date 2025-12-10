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
