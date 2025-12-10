"""
Property-based tests for LLMEngine.

Tests universal properties that should hold across all valid executions.
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock
from datetime import datetime, timedelta
from pymongo import MongoClient

from src.engines.llm_engine import LLMEngine, NewsAnalysisResult, SentimentResult, LLMClient


# Hypothesis strategies for generating test data
text_strategy = st.text(min_size=10, max_size=1000)
article_title_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')),
    min_size=10,
    max_size=200
)
article_content_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')),
    min_size=50,
    max_size=2000
)


def create_mock_mongo_client():
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


@given(text=text_strategy)
@settings(max_examples=100, deadline=None)
def test_property_17_sentiment_classification_validity(text):
    """
    **Feature: vietnam-stock-ai-backend, Property 17: Sentiment classification validity**
    **Validates: Requirements 5.2**
    
    For any news article analyzed by the LLM Engine, the sentiment classification 
    should be one of: positive, negative, or neutral, and include a confidence score 
    between 0 and 1
    
    This property verifies that:
    1. Sentiment is one of the valid categories: 'positive', 'negative', or 'neutral'
    2. Score is between -1.0 and 1.0
    3. Confidence is between 0.0 and 1.0
    4. All values are valid (not NaN or infinity)
    """
    # Create mock MongoDB client
    mock_mongo_client = create_mock_mongo_client()
    
    # Create engine with mock LLM client
    engine = LLMEngine(mock_mongo_client, database_name='test_db')
    
    # Analyze sentiment
    sentiment_result = engine.analyze_sentiment(text)
    
    # Property verification: Sentiment classification must be valid
    assert isinstance(sentiment_result, SentimentResult), \
        f"Result should be a SentimentResult, but got {type(sentiment_result)}"
    
    # Verify sentiment is one of the valid categories
    valid_sentiments = ['positive', 'negative', 'neutral']
    assert sentiment_result.sentiment in valid_sentiments, \
        f"Sentiment should be one of {valid_sentiments}, but got '{sentiment_result.sentiment}'"
    
    # Verify score is between -1.0 and 1.0
    assert isinstance(sentiment_result.score, float), \
        f"Score should be a float, but got {type(sentiment_result.score)}"
    
    assert -1.0 <= sentiment_result.score <= 1.0, \
        f"Score should be between -1.0 and 1.0, but got {sentiment_result.score}"
    
    # Verify confidence is between 0.0 and 1.0
    assert isinstance(sentiment_result.confidence, float), \
        f"Confidence should be a float, but got {type(sentiment_result.confidence)}"
    
    assert 0.0 <= sentiment_result.confidence <= 1.0, \
        f"Confidence should be between 0.0 and 1.0, but got {sentiment_result.confidence}"



# Strategy for generating article sources
source_strategy = st.one_of(
    st.just('cafef.vn'),
    st.just('vnexpress.net'),
    st.just('vietstock.vn'),
    st.just('ndh.vn'),
    st.just('baodautu.vn'),
    st.text(alphabet=st.characters(whitelist_categories=('L', 'N')), min_size=5, max_size=30)
)


@given(
    title=article_title_strategy,
    content=article_content_strategy,
    source=source_strategy
)
@settings(max_examples=100, deadline=None)
def test_property_18_influence_score_validity(title, content, source):
    """
    **Feature: vietnam-stock-ai-backend, Property 18: Influence score validity**
    **Validates: Requirements 5.4**
    
    For any news article analyzed by the LLM Engine, the calculated influence score 
    should be a valid number between 0 and 1
    
    This property verifies that:
    1. Influence score is between 0.0 and 1.0 (inclusive)
    2. Influence score is a valid float (not NaN or infinity)
    3. Influence score calculation handles various sources
    """
    # Create mock MongoDB client
    mock_mongo_client = create_mock_mongo_client()
    
    # Create engine
    engine = LLMEngine(mock_mongo_client, database_name='test_db')
    
    # Create article document
    article = {
        'title': title,
        'content': content,
        'source': source,
        'published_at': datetime.utcnow().isoformat(),
        'symbol': 'TEST'
    }
    
    # Calculate influence score
    influence_score = engine.calculate_influence_score(article)
    
    # Property verification: Influence score must be between 0 and 1
    assert isinstance(influence_score, float), \
        f"Influence score should be a float, but got {type(influence_score)}"
    
    assert 0.0 <= influence_score <= 1.0, \
        f"Influence score should be between 0.0 and 1.0, but got {influence_score}"



# Strategy for generating stock symbols
symbol_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Lu',)),
    min_size=3,
    max_size=5
)

# Strategy for generating lists of articles
articles_list_strategy = st.lists(
    st.fixed_dictionaries({
        'title': article_title_strategy,
        'content': article_content_strategy,
        'source': source_strategy,
        'published_at': st.just(datetime.utcnow().isoformat()),
        'collected_at': st.just(datetime.utcnow().isoformat())
    }),
    min_size=1,
    max_size=10
)


@given(
    symbol=symbol_strategy,
    articles=articles_list_strategy
)
@settings(max_examples=100, deadline=None)
def test_property_19_llm_results_storage_completeness(symbol, articles):
    """
    **Feature: vietnam-stock-ai-backend, Property 19: LLM results storage completeness**
    **Validates: Requirements 5.2**
    
    For any completed LLM analysis, the results stored in `llm_analysis` collection 
    should include timestamp, stock symbol, sentiment classification, summary, and 
    influence score
    
    This property verifies that:
    1. All required fields are present in the stored result
    2. Field values are of the correct type
    3. The storage operation completes successfully
    """
    # Create mock MongoDB client
    mock_mongo_client = create_mock_mongo_client()
    mock_db = mock_mongo_client['test_db']
    mock_analysis_collection = mock_db['llm_analysis']
    
    # Track what was inserted
    inserted_documents = []
    
    def mock_insert_one(document):
        inserted_documents.append(document)
        return Mock(inserted_id='mock_id')
    
    mock_analysis_collection.insert_one = Mock(side_effect=mock_insert_one)
    
    # Mock the news retrieval to return our test articles
    def mock_find(*args, **kwargs):
        # Add symbol to each article
        for article in articles:
            article['symbol'] = symbol
        return articles
    
    mock_news_collection = mock_db['news']
    mock_news_collection.find = Mock(side_effect=mock_find)
    
    # Create mock LLM client to avoid real API calls
    from src.engines.llm_engine import LLMClient
    mock_llm_client = LLMClient(api_key=None, use_openai=False)
    
    # Create engine with mock LLM client
    engine = LLMEngine(mock_mongo_client, llm_client=mock_llm_client, database_name='test_db')
    
    # Perform analysis
    result = engine.analyze_news(symbol, lookback_days=7)
    
    # Property verification: Result should be created
    assert result is not None, "Analysis should return a result"
    
    # Verify that a document was inserted
    assert len(inserted_documents) == 1, \
        f"Expected 1 document to be inserted, but got {len(inserted_documents)}"
    
    stored_doc = inserted_documents[0]
    
    # Verify all required fields are present
    required_fields = ['symbol', 'timestamp', 'sentiment', 'summary', 'influence_score', 'articles_analyzed']
    
    for field in required_fields:
        assert field in stored_doc, \
            f"Required field '{field}' is missing from stored document"
    
    # Verify field types and values
    assert stored_doc['symbol'] == symbol, \
        f"Expected symbol '{symbol}', but got '{stored_doc['symbol']}'"
    
    assert isinstance(stored_doc['timestamp'], str), \
        "Timestamp should be a string (ISO format)"
    
    assert isinstance(stored_doc['sentiment'], dict), \
        "Sentiment should be a dictionary"
    
    # Verify sentiment has required fields
    sentiment_fields = ['sentiment', 'score', 'confidence']
    for field in sentiment_fields:
        assert field in stored_doc['sentiment'], \
            f"Required field '{field}' is missing from sentiment"
    
    assert stored_doc['sentiment']['sentiment'] in ['positive', 'negative', 'neutral'], \
        f"Invalid sentiment: {stored_doc['sentiment']['sentiment']}"
    
    assert -1.0 <= stored_doc['sentiment']['score'] <= 1.0, \
        f"Sentiment score should be between -1 and 1, but got {stored_doc['sentiment']['score']}"
    
    assert 0.0 <= stored_doc['sentiment']['confidence'] <= 1.0, \
        f"Confidence should be between 0 and 1, but got {stored_doc['sentiment']['confidence']}"
    
    assert isinstance(stored_doc['summary'], str), \
        "Summary should be a string"
    
    assert isinstance(stored_doc['influence_score'], float), \
        "Influence score should be a float"
    
    assert 0.0 <= stored_doc['influence_score'] <= 1.0, \
        f"Influence score should be between 0 and 1, but got {stored_doc['influence_score']}"
    
    assert isinstance(stored_doc['articles_analyzed'], int), \
        "Articles analyzed should be an integer"
    
    assert stored_doc['articles_analyzed'] == len(articles), \
        f"Expected {len(articles)} articles analyzed, but got {stored_doc['articles_analyzed']}"
