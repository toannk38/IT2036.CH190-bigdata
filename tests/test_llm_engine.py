"""
Unit tests for LLMEngine.

Tests specific functionality and edge cases.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta
from pymongo import MongoClient

from src.engines.llm_engine import (
    LLMEngine, NewsAnalysisResult, SentimentResult, LLMClient, NewsArticle
)


@pytest.fixture
def mock_mongo_client():
    """Create a mock MongoDB client."""
    mock_client = Mock(spec=MongoClient)
    mock_db = Mock()
    mock_news_collection = Mock()
    mock_analysis_collection = Mock()
    
    mock_db.__getitem__ = Mock(side_effect=lambda x: {
        'news': mock_news_collection,
        'llm_analysis': mock_analysis_collection
    }.get(x))
    
    mock_client.__getitem__ = Mock(return_value=mock_db)
    
    return mock_client


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    mock_client = Mock(spec=LLMClient)
    
    # Default sentiment analysis response
    mock_client.analyze_sentiment.return_value = {
        'sentiment': 'positive',
        'score': 0.5,
        'confidence': 0.8
    }
    
    # Default summary generation response
    mock_client.generate_summary.return_value = "Test summary of articles."
    
    return mock_client


@pytest.fixture
def llm_engine(mock_mongo_client, mock_llm_client):
    """Create an LLMEngine instance with mocked dependencies."""
    return LLMEngine(mock_mongo_client, llm_client=mock_llm_client, database_name='test_db')


def create_sample_articles(num_articles=5, symbol='VNM'):
    """
    Create sample news articles for testing.
    
    Args:
        num_articles: Number of articles to create
        symbol: Stock symbol
        
    Returns:
        List of article dictionaries
    """
    articles = []
    base_time = datetime.utcnow()
    
    for i in range(num_articles):
        article = {
            'symbol': symbol,
            'title': f'Test Article {i+1} about {symbol}',
            'content': f'This is the content of test article {i+1}. It contains information about the stock.',
            'source': 'cafef.vn',
            'published_at': (base_time - timedelta(hours=i)).isoformat(),
            'collected_at': (base_time - timedelta(hours=i) + timedelta(minutes=5)).isoformat()
        }
        articles.append(article)
    
    return articles


def test_llm_engine_initialization(llm_engine):
    """Test that LLMEngine initializes correctly."""
    assert llm_engine.db is not None
    assert llm_engine.news_collection is not None
    assert llm_engine.analysis_collection is not None
    assert llm_engine.llm is not None


def test_llm_engine_initialization_with_default_client(mock_mongo_client):
    """Test that LLMEngine creates default LLM client if none provided."""
    engine = LLMEngine(mock_mongo_client, database_name='test_db')
    
    assert engine.llm is not None
    assert isinstance(engine.llm, LLMClient)


def test_analyze_sentiment_with_positive_text(llm_engine, mock_llm_client):
    """Test sentiment analysis with positive text."""
    # Setup
    text = "The company reported strong growth and increased profits."
    mock_llm_client.analyze_sentiment.return_value = {
        'sentiment': 'positive',
        'score': 0.7,
        'confidence': 0.85
    }
    
    # Execute
    result = llm_engine.analyze_sentiment(text)
    
    # Assert
    assert isinstance(result, SentimentResult)
    assert result.sentiment == 'positive'
    assert result.score == 0.7
    assert result.confidence == 0.85
    assert mock_llm_client.analyze_sentiment.called


def test_analyze_sentiment_with_negative_text(llm_engine, mock_llm_client):
    """Test sentiment analysis with negative text."""
    # Setup
    text = "The company faces significant losses and declining revenue."
    mock_llm_client.analyze_sentiment.return_value = {
        'sentiment': 'negative',
        'score': -0.6,
        'confidence': 0.9
    }
    
    # Execute
    result = llm_engine.analyze_sentiment(text)
    
    # Assert
    assert isinstance(result, SentimentResult)
    assert result.sentiment == 'negative'
    assert result.score == -0.6
    assert result.confidence == 0.9


def test_analyze_sentiment_with_neutral_text(llm_engine, mock_llm_client):
    """Test sentiment analysis with neutral text."""
    # Setup
    text = "The company held its annual meeting yesterday."
    mock_llm_client.analyze_sentiment.return_value = {
        'sentiment': 'neutral',
        'score': 0.0,
        'confidence': 0.6
    }
    
    # Execute
    result = llm_engine.analyze_sentiment(text)
    
    # Assert
    assert isinstance(result, SentimentResult)
    assert result.sentiment == 'neutral'
    assert result.score == 0.0
    assert result.confidence == 0.6


def test_generate_summary_with_multiple_articles(llm_engine, mock_llm_client):
    """Test summary generation with multiple articles."""
    # Setup
    articles = [
        "Article 1 content about stock performance.",
        "Article 2 content about company earnings.",
        "Article 3 content about market trends."
    ]
    expected_summary = "Summary of all articles discussing stock performance and earnings."
    mock_llm_client.generate_summary.return_value = expected_summary
    
    # Execute
    summary = llm_engine.generate_summary(articles)
    
    # Assert
    assert isinstance(summary, str)
    assert summary == expected_summary
    assert mock_llm_client.generate_summary.called


def test_generate_summary_with_empty_list(llm_engine, mock_llm_client):
    """Test summary generation with empty article list."""
    # Setup
    articles = []
    mock_llm_client.generate_summary.return_value = "No news articles available for summary."
    
    # Execute
    summary = llm_engine.generate_summary(articles)
    
    # Assert
    assert isinstance(summary, str)
    assert "No news" in summary or "available" in summary


def test_calculate_influence_score_with_known_source(llm_engine):
    """Test influence score calculation with known credible source."""
    # Setup
    article = {
        'title': 'Test Article',
        'content': 'Test content',
        'source': 'vnexpress.net',
        'published_at': datetime.utcnow().isoformat()
    }
    
    # Execute
    influence_score = llm_engine.calculate_influence_score(article)
    
    # Assert
    assert isinstance(influence_score, float)
    assert 0.0 <= influence_score <= 1.0
    # vnexpress.net should have high credibility (0.95)
    assert influence_score == 0.95


def test_calculate_influence_score_with_unknown_source(llm_engine):
    """Test influence score calculation with unknown source."""
    # Setup
    article = {
        'title': 'Test Article',
        'content': 'Test content',
        'source': 'unknown-source.com',
        'published_at': datetime.utcnow().isoformat()
    }
    
    # Execute
    influence_score = llm_engine.calculate_influence_score(article)
    
    # Assert
    assert isinstance(influence_score, float)
    assert 0.0 <= influence_score <= 1.0
    # Unknown source should get default credibility (0.7)
    assert influence_score == 0.7


def test_calculate_influence_score_with_various_sources(llm_engine):
    """Test influence score calculation with various known sources."""
    sources_and_expected = [
        ('cafef.vn', 0.9),
        ('vietstock.vn', 0.9),
        ('ndh.vn', 0.85),
        ('baodautu.vn', 0.8),
    ]
    
    for source, expected_score in sources_and_expected:
        article = {
            'title': 'Test Article',
            'content': 'Test content',
            'source': source,
            'published_at': datetime.utcnow().isoformat()
        }
        
        influence_score = llm_engine.calculate_influence_score(article)
        
        assert influence_score == expected_score, \
            f"Expected {expected_score} for {source}, but got {influence_score}"


def test_analyze_news_with_valid_articles(llm_engine, mock_mongo_client, mock_llm_client):
    """Test complete news analysis with valid articles."""
    # Setup
    symbol = 'VNM'
    articles = create_sample_articles(num_articles=5, symbol=symbol)
    
    # Mock MongoDB query
    mock_db = mock_mongo_client['test_db']
    mock_news_collection = mock_db['news']
    mock_news_collection.find.return_value = articles
    
    mock_analysis_collection = mock_db['llm_analysis']
    mock_analysis_collection.insert_one.return_value = Mock(inserted_id='mock_id')
    
    # Mock LLM responses
    mock_llm_client.analyze_sentiment.return_value = {
        'sentiment': 'positive',
        'score': 0.6,
        'confidence': 0.8
    }
    mock_llm_client.generate_summary.return_value = "Summary of news articles."
    
    # Execute
    result = llm_engine.analyze_news(symbol, lookback_days=7)
    
    # Assert
    assert result is not None
    assert isinstance(result, NewsAnalysisResult)
    assert result.symbol == symbol
    assert isinstance(result.timestamp, str)
    assert isinstance(result.sentiment, SentimentResult)
    assert result.sentiment.sentiment in ['positive', 'negative', 'neutral']
    assert -1.0 <= result.sentiment.score <= 1.0
    assert 0.0 <= result.sentiment.confidence <= 1.0
    assert isinstance(result.summary, str)
    assert 0.0 <= result.influence_score <= 1.0
    assert result.articles_analyzed == 5
    
    # Verify MongoDB insert was called
    assert mock_analysis_collection.insert_one.called


def test_analyze_news_with_no_articles(llm_engine, mock_mongo_client):
    """Test news analysis when no articles are available."""
    # Setup
    symbol = 'VNM'
    
    # Mock MongoDB query to return empty list
    mock_db = mock_mongo_client['test_db']
    mock_news_collection = mock_db['news']
    mock_news_collection.find.return_value = []
    
    # Execute
    result = llm_engine.analyze_news(symbol, lookback_days=7)
    
    # Assert
    assert result is None  # Should return None for no articles


def test_analyze_news_with_single_article(llm_engine, mock_mongo_client, mock_llm_client):
    """Test news analysis with only one article."""
    # Setup
    symbol = 'VNM'
    articles = create_sample_articles(num_articles=1, symbol=symbol)
    
    # Mock MongoDB query
    mock_db = mock_mongo_client['test_db']
    mock_news_collection = mock_db['news']
    mock_news_collection.find.return_value = articles
    
    mock_analysis_collection = mock_db['llm_analysis']
    mock_analysis_collection.insert_one.return_value = Mock(inserted_id='mock_id')
    
    # Execute
    result = llm_engine.analyze_news(symbol, lookback_days=7)
    
    # Assert
    assert result is not None
    assert result.articles_analyzed == 1


def test_store_result(llm_engine, mock_mongo_client):
    """Test storing analysis result in MongoDB."""
    # Setup
    sentiment = SentimentResult(sentiment='positive', score=0.6, confidence=0.8)
    result = NewsAnalysisResult(
        symbol='VNM',
        timestamp=datetime.utcnow().isoformat(),
        sentiment=sentiment,
        summary='Test summary of news articles.',
        influence_score=0.85,
        articles_analyzed=5
    )
    
    # Mock MongoDB insert
    mock_db = mock_mongo_client['test_db']
    mock_analysis_collection = mock_db['llm_analysis']
    mock_analysis_collection.insert_one.return_value = Mock(inserted_id='mock_id')
    
    # Execute
    success = llm_engine._store_result(result)
    
    # Assert
    assert success is True
    assert mock_analysis_collection.insert_one.called
    
    # Verify the document structure
    call_args = mock_analysis_collection.insert_one.call_args
    document = call_args[0][0]
    
    assert document['symbol'] == 'VNM'
    assert 'timestamp' in document
    assert 'sentiment' in document
    assert document['sentiment']['sentiment'] == 'positive'
    assert document['summary'] == 'Test summary of news articles.'
    assert document['influence_score'] == 0.85
    assert document['articles_analyzed'] == 5


def test_llm_client_analyze_sentiment_with_positive_keywords():
    """Test LLMClient sentiment analysis with positive keywords."""
    client = LLMClient()
    
    text = "The company reported strong growth and increased profits with positive outlook."
    result = client.analyze_sentiment(text)
    
    assert result['sentiment'] in ['positive', 'negative', 'neutral']
    assert -1.0 <= result['score'] <= 1.0
    assert 0.0 <= result['confidence'] <= 1.0
    # Should detect positive sentiment
    assert result['sentiment'] == 'positive'


def test_llm_client_analyze_sentiment_with_negative_keywords():
    """Test LLMClient sentiment analysis with negative keywords."""
    client = LLMClient()
    
    text = "The company faces significant losses and declining revenue with high risk."
    result = client.analyze_sentiment(text)
    
    assert result['sentiment'] in ['positive', 'negative', 'neutral']
    assert -1.0 <= result['score'] <= 1.0
    assert 0.0 <= result['confidence'] <= 1.0
    # Should detect negative sentiment
    assert result['sentiment'] == 'negative'


def test_llm_client_analyze_sentiment_with_neutral_text():
    """Test LLMClient sentiment analysis with neutral text."""
    client = LLMClient()
    
    text = "The company held its annual meeting yesterday at the headquarters."
    result = client.analyze_sentiment(text)
    
    assert result['sentiment'] in ['positive', 'negative', 'neutral']
    assert -1.0 <= result['score'] <= 1.0
    assert 0.0 <= result['confidence'] <= 1.0


def test_llm_client_generate_summary_with_articles():
    """Test LLMClient summary generation."""
    client = LLMClient()
    
    texts = [
        "Article 1 about stock performance.",
        "Article 2 about company earnings.",
        "Article 3 about market trends."
    ]
    
    summary = client.generate_summary(texts)
    
    assert isinstance(summary, str)
    assert len(summary) > 0


def test_llm_client_generate_summary_with_empty_list():
    """Test LLMClient summary generation with empty list."""
    client = LLMClient()
    
    texts = []
    summary = client.generate_summary(texts)
    
    assert isinstance(summary, str)
    assert "No news" in summary


def test_aggregate_sentiment_with_multiple_results(llm_engine):
    """Test sentiment aggregation with multiple results."""
    # Setup
    sentiment_results = [
        SentimentResult(sentiment='positive', score=0.7, confidence=0.8),
        SentimentResult(sentiment='positive', score=0.5, confidence=0.7),
        SentimentResult(sentiment='neutral', score=0.1, confidence=0.6),
    ]
    influence_scores = [0.9, 0.8, 0.7]
    
    # Execute
    aggregated = llm_engine._aggregate_sentiment(sentiment_results, influence_scores)
    
    # Assert
    assert isinstance(aggregated, SentimentResult)
    assert aggregated.sentiment in ['positive', 'negative', 'neutral']
    assert -1.0 <= aggregated.score <= 1.0
    assert 0.0 <= aggregated.confidence <= 1.0


def test_aggregate_sentiment_with_empty_list(llm_engine):
    """Test sentiment aggregation with empty list."""
    # Setup
    sentiment_results = []
    influence_scores = []
    
    # Execute
    aggregated = llm_engine._aggregate_sentiment(sentiment_results, influence_scores)
    
    # Assert
    assert isinstance(aggregated, SentimentResult)
    assert aggregated.sentiment == 'neutral'
    assert aggregated.score == 0.0
    assert aggregated.confidence == 0.0


def test_aggregate_sentiment_with_mixed_sentiments(llm_engine):
    """Test sentiment aggregation with mixed positive and negative sentiments."""
    # Setup
    sentiment_results = [
        SentimentResult(sentiment='positive', score=0.8, confidence=0.9),
        SentimentResult(sentiment='negative', score=-0.6, confidence=0.8),
        SentimentResult(sentiment='positive', score=0.4, confidence=0.7),
    ]
    influence_scores = [0.9, 0.8, 0.7]
    
    # Execute
    aggregated = llm_engine._aggregate_sentiment(sentiment_results, influence_scores)
    
    # Assert
    assert isinstance(aggregated, SentimentResult)
    assert aggregated.sentiment in ['positive', 'negative', 'neutral']
    # The result should be influenced by the weights
    assert -1.0 <= aggregated.score <= 1.0
    assert 0.0 <= aggregated.confidence <= 1.0
