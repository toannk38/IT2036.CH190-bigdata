"""
Unit tests for AggregationService.
Tests specific functionality with concrete examples.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from src.services.aggregation_service import AggregationService, Alert, FinalScore


@pytest.fixture
def mock_mongo_client():
    """Create a mock MongoDB client."""
    mock_client = MagicMock()
    mock_db = MagicMock()
    
    # Create mock collections
    mock_ai_collection = MagicMock()
    mock_llm_collection = MagicMock()
    mock_final_collection = MagicMock()
    
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
    
    return mock_client, mock_ai_collection, mock_llm_collection, mock_final_collection


def test_weighted_score_calculation_high_technical():
    """
    Test weighted score calculation with high technical score.
    Requirements: 6.2, 6.3
    """
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    
    service = AggregationService(mock_client)
    
    # High technical, low risk, neutral sentiment
    ai_result = {
        'technical_score': 0.9,
        'risk_score': 0.2,
        'trend_prediction': {'direction': 'up', 'confidence': 0.8}
    }
    llm_result = {
        'sentiment': {
            'sentiment': 'neutral',
            'score': 0.0,  # -1 to 1 range
            'confidence': 0.7
        }
    }
    
    final_score = service.calculate_final_score(ai_result, llm_result)
    
    # Expected: (0.9 * 0.4 + 0.8 * 0.3 + 0.5 * 0.3) * 100
    # = (0.36 + 0.24 + 0.15) * 100 = 75
    assert 70 <= final_score <= 80, f"Expected score around 75, got {final_score}"


def test_weighted_score_calculation_high_risk():
    """
    Test weighted score calculation with high risk.
    Requirements: 6.2, 6.3
    """
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    
    service = AggregationService(mock_client)
    
    # Low technical, high risk, negative sentiment
    ai_result = {
        'technical_score': 0.3,
        'risk_score': 0.8,
        'trend_prediction': {'direction': 'down', 'confidence': 0.7}
    }
    llm_result = {
        'sentiment': {
            'sentiment': 'negative',
            'score': -0.6,  # -1 to 1 range
            'confidence': 0.8
        }
    }
    
    final_score = service.calculate_final_score(ai_result, llm_result)
    
    # Expected: (0.3 * 0.4 + 0.2 * 0.3 + 0.2 * 0.3) * 100
    # = (0.12 + 0.06 + 0.06) * 100 = 24
    assert 20 <= final_score <= 30, f"Expected score around 24, got {final_score}"


def test_weighted_score_calculation_positive_sentiment():
    """
    Test weighted score calculation with positive sentiment.
    Requirements: 6.2, 6.3
    """
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    
    service = AggregationService(mock_client)
    
    # Medium technical, low risk, positive sentiment
    ai_result = {
        'technical_score': 0.6,
        'risk_score': 0.3,
        'trend_prediction': {'direction': 'up', 'confidence': 0.6}
    }
    llm_result = {
        'sentiment': {
            'sentiment': 'positive',
            'score': 0.8,  # -1 to 1 range
            'confidence': 0.9
        }
    }
    
    final_score = service.calculate_final_score(ai_result, llm_result)
    
    # Expected: (0.6 * 0.4 + 0.7 * 0.3 + 0.9 * 0.3) * 100
    # = (0.24 + 0.21 + 0.27) * 100 = 72
    assert 68 <= final_score <= 76, f"Expected score around 72, got {final_score}"


def test_alert_generation_buy_signal():
    """
    Test alert generation for BUY signal (score > 70).
    Requirements: 6.4
    """
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    
    service = AggregationService(mock_client)
    
    alerts = service.generate_alerts(75.0, 'VNM')
    
    assert len(alerts) == 1
    assert alerts[0].type == 'BUY'
    assert alerts[0].priority == 'high'
    assert 'VNM' in alerts[0].message
    assert '75' in alerts[0].message


def test_alert_generation_watch_signal():
    """
    Test alert generation for WATCH signal (40 <= score <= 70).
    Requirements: 6.4
    """
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    
    service = AggregationService(mock_client)
    
    # Test lower boundary
    alerts = service.generate_alerts(40.0, 'VIC')
    assert len(alerts) == 1
    assert alerts[0].type == 'WATCH'
    assert alerts[0].priority == 'medium'
    
    # Test middle
    alerts = service.generate_alerts(55.0, 'HPG')
    assert len(alerts) == 1
    assert alerts[0].type == 'WATCH'
    assert alerts[0].priority == 'medium'
    
    # Test upper boundary
    alerts = service.generate_alerts(70.0, 'TCB')
    assert len(alerts) == 1
    assert alerts[0].type == 'WATCH'
    assert alerts[0].priority == 'medium'


def test_alert_generation_risk_signal():
    """
    Test alert generation for RISK signal (score < 40).
    Requirements: 6.4
    """
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    
    service = AggregationService(mock_client)
    
    alerts = service.generate_alerts(25.0, 'ABC')
    
    assert len(alerts) == 1
    assert alerts[0].type == 'RISK'
    assert alerts[0].priority == 'high'
    assert 'ABC' in alerts[0].message
    assert '25' in alerts[0].message


def test_data_retrieval_and_aggregation(mock_mongo_client):
    """
    Test complete data retrieval and aggregation flow.
    Requirements: 6.1, 6.2, 6.3, 6.4
    """
    mock_client, mock_ai_coll, mock_llm_coll, mock_final_coll = mock_mongo_client
    
    # Setup test data
    ai_result = {
        'symbol': 'VNM',
        'timestamp': datetime.utcnow().isoformat(),
        'technical_score': 0.75,
        'risk_score': 0.35,
        'trend_prediction': {'direction': 'up', 'confidence': 0.8},
        'indicators': {'rsi': 65, 'macd': 1250}
    }
    
    llm_result = {
        'symbol': 'VNM',
        'timestamp': datetime.utcnow().isoformat(),
        'sentiment': {
            'sentiment': 'positive',
            'score': 0.6,
            'confidence': 0.85
        },
        'summary': 'Positive outlook for the company',
        'influence_score': 0.7,
        'articles_analyzed': 5
    }
    
    mock_ai_coll.find_one.return_value = ai_result
    mock_llm_coll.find_one.return_value = llm_result
    
    # Create service and aggregate
    service = AggregationService(mock_client)
    result = service.aggregate('VNM')
    
    # Verify result
    assert result is not None
    assert result.symbol == 'VNM'
    assert 0 <= result.final_score <= 100
    assert result.recommendation in ['BUY', 'WATCH', 'RISK']
    assert len(result.alerts) > 0
    
    # Verify components
    assert 'technical_score' in result.components
    assert 'risk_score' in result.components
    assert 'sentiment_score' in result.components
    
    # Verify storage was called
    assert mock_final_coll.insert_one.called


def test_aggregation_missing_ai_data(mock_mongo_client):
    """
    Test aggregation when AI/ML data is missing.
    Requirements: 6.1
    """
    mock_client, mock_ai_coll, mock_llm_coll, mock_final_coll = mock_mongo_client
    
    # No AI data available
    mock_ai_coll.find_one.return_value = None
    mock_llm_coll.find_one.return_value = {'symbol': 'VNM', 'sentiment': {}}
    
    service = AggregationService(mock_client)
    result = service.aggregate('VNM')
    
    # Should return None when data is missing
    assert result is None
    assert not mock_final_coll.insert_one.called


def test_aggregation_missing_llm_data(mock_mongo_client):
    """
    Test aggregation when LLM data is missing.
    Requirements: 6.1
    """
    mock_client, mock_ai_coll, mock_llm_coll, mock_final_coll = mock_mongo_client
    
    # No LLM data available
    mock_ai_coll.find_one.return_value = {'symbol': 'VNM', 'technical_score': 0.5}
    mock_llm_coll.find_one.return_value = None
    
    service = AggregationService(mock_client)
    result = service.aggregate('VNM')
    
    # Should return None when data is missing
    assert result is None
    assert not mock_final_coll.insert_one.called


def test_custom_weights():
    """
    Test aggregation with custom weights.
    Requirements: 6.2
    """
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    
    # Custom weights favoring sentiment
    custom_weights = {
        'technical': 0.2,
        'risk': 0.2,
        'sentiment': 0.6
    }
    
    service = AggregationService(mock_client, weights=custom_weights)
    
    ai_result = {
        'technical_score': 0.5,
        'risk_score': 0.5,
    }
    llm_result = {
        'sentiment': {
            'score': 0.8,  # Very positive
            'confidence': 0.9
        }
    }
    
    final_score = service.calculate_final_score(ai_result, llm_result)
    
    # With high sentiment weight, score should be high
    # (0.5 * 0.2 + 0.5 * 0.2 + 0.9 * 0.6) * 100 = 74
    assert 70 <= final_score <= 78, f"Expected score around 74, got {final_score}"


def test_sentiment_score_normalization():
    """
    Test that sentiment scores are properly normalized from -1..1 to 0..1 range.
    Requirements: 6.2
    """
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    
    service = AggregationService(mock_client)
    
    # Test negative sentiment
    assert service._normalize_sentiment_score(-1.0) == 0.0
    assert service._normalize_sentiment_score(-0.5) == 0.25
    assert service._normalize_sentiment_score(0.0) == 0.5
    assert service._normalize_sentiment_score(0.5) == 0.75
    assert service._normalize_sentiment_score(1.0) == 1.0


def test_recommendation_determination():
    """
    Test recommendation category determination.
    Requirements: 6.3
    """
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    
    service = AggregationService(mock_client)
    
    # Test BUY recommendation
    assert service._determine_recommendation(75.0) == 'BUY'
    assert service._determine_recommendation(100.0) == 'BUY'
    
    # Test WATCH recommendation
    assert service._determine_recommendation(40.0) == 'WATCH'
    assert service._determine_recommendation(55.0) == 'WATCH'
    assert service._determine_recommendation(70.0) == 'WATCH'
    
    # Test RISK recommendation
    assert service._determine_recommendation(0.0) == 'RISK'
    assert service._determine_recommendation(25.0) == 'RISK'
    assert service._determine_recommendation(39.9) == 'RISK'


def test_final_score_to_dict():
    """
    Test FinalScore serialization to dictionary.
    Requirements: 6.5
    """
    alerts = [
        Alert(type='BUY', priority='high', message='Test alert')
    ]
    
    final_score = FinalScore(
        symbol='VNM',
        timestamp='2024-01-15T10:00:00Z',
        final_score=75.5,
        recommendation='BUY',
        components={'technical_score': 0.8, 'risk_score': 0.3, 'sentiment_score': 0.7},
        alerts=alerts
    )
    
    result_dict = final_score.to_dict()
    
    assert result_dict['symbol'] == 'VNM'
    assert result_dict['final_score'] == 75.5
    assert result_dict['recommendation'] == 'BUY'
    assert 'components' in result_dict
    assert 'alerts' in result_dict
    assert len(result_dict['alerts']) == 1
    assert result_dict['alerts'][0]['type'] == 'BUY'
