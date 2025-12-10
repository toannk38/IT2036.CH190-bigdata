"""
LLM Engine for qualitative stock analysis.
Performs sentiment analysis, news summarization, and influence scoring.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pymongo import MongoClient

from src.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class SentimentResult:
    """Sentiment analysis result for a single article."""
    sentiment: str  # 'positive', 'negative', or 'neutral'
    score: float  # -1.0 to 1.0 (negative to positive)
    confidence: float  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class NewsArticle:
    """News article data structure."""
    title: str
    content: str
    source: str
    published_at: str
    symbol: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class NewsAnalysisResult:
    """Complete LLM analysis result for a stock's news."""
    symbol: str
    timestamp: str
    sentiment: SentimentResult
    summary: str
    influence_score: float  # 0.0 to 1.0
    articles_analyzed: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        result = asdict(self)
        result['sentiment'] = self.sentiment.to_dict()
        return result


class LLMClient:
    """
    LLM client for sentiment analysis and summarization.
    Supports both OpenAI API and fallback keyword-based analysis.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = 'gpt-3.5-turbo', use_openai: bool = True):
        """
        Initialize LLM client.
        
        Args:
            api_key: OpenAI API key (optional, will try to load from config)
            model: OpenAI model to use (default: gpt-3.5-turbo)
            use_openai: Whether to use OpenAI API or fallback to keyword-based analysis
        """
        self.use_openai = use_openai and api_key is not None
        self.model = model
        
        if self.use_openai:
            try:
                import openai
                self.openai = openai
                self.client = openai.OpenAI(api_key=api_key)
                logger.info(f"LLMClient initialized with OpenAI API (model: {model})")
            except ImportError:
                logger.warning("OpenAI library not installed. Falling back to keyword-based analysis.")
                self.use_openai = False
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}. Falling back to keyword-based analysis.")
                self.use_openai = False
        else:
            logger.info("LLMClient initialized with keyword-based analysis")
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment, score, and confidence
        """
        if self.use_openai:
            return self._analyze_sentiment_openai(text)
        else:
            return self._analyze_sentiment_keywords(text)
    
    def _analyze_sentiment_openai(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment using OpenAI API.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment, score, and confidence
        """
        try:
            # Truncate text if too long (to avoid token limits)
            max_chars = 2000
            if len(text) > max_chars:
                text = text[:max_chars] + "..."
            
            prompt = f"""Analyze the sentiment of the following Vietnamese stock market news article.
Respond with a JSON object containing:
- sentiment: one of "positive", "negative", or "neutral"
- score: a number between -1.0 (very negative) and 1.0 (very positive)
- confidence: a number between 0.0 and 1.0 indicating confidence in the analysis

Article:
{text}

Response (JSON only):"""

            # Use max_completion_tokens for newer models, max_tokens for older ones
            completion_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a financial sentiment analysis expert. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
            
            # Try different token limit parameters based on model
            try:
                # Try max_completion_tokens first (newer API)
                completion_params["max_completion_tokens"] = 150
                response = self.client.chat.completions.create(**completion_params)
            except Exception as e:
                error_msg = str(e).lower()
                if "max_completion_tokens" in error_msg or "unexpected" in error_msg:
                    # Fallback to max_tokens for older models
                    del completion_params["max_completion_tokens"]
                    completion_params["max_tokens"] = 150
                    try:
                        response = self.client.chat.completions.create(**completion_params)
                    except Exception as e2:
                        # If still failing, try without token limits
                        logger.warning(f"Failed with max_tokens, trying without limits: {e2}")
                        del completion_params["max_tokens"]
                        response = self.client.chat.completions.create(**completion_params)
                else:
                    raise
            
            # Parse the response
            import json
            result_text = response.choices[0].message.content.strip()
            
            # Log the raw response for debugging
            logger.debug(f"OpenAI raw response: {result_text}")
            
            # Check if response is empty
            if not result_text:
                logger.warning("OpenAI returned empty response, falling back to keyword analysis")
                return self._analyze_sentiment_keywords(text)
            
            # Try to extract JSON from the response
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            # Try to parse JSON
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON response: {result_text[:200]}")
                logger.warning(f"JSON error: {e}")
                return self._analyze_sentiment_keywords(text)
            
            # Validate and normalize the result
            sentiment = result.get('sentiment', 'neutral').lower()
            if sentiment not in ['positive', 'negative', 'neutral']:
                sentiment = 'neutral'
            
            score = float(result.get('score', 0.0))
            score = max(-1.0, min(1.0, score))  # Clamp to [-1, 1]
            
            confidence = float(result.get('confidence', 0.5))
            confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
            
            return {
                'sentiment': sentiment,
                'score': score,
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"Error in OpenAI sentiment analysis: {e}", exc_info=True)
            # Fallback to keyword-based analysis
            return self._analyze_sentiment_keywords(text)
    
    def _analyze_sentiment_keywords(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment using keyword-based approach (fallback).
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment, score, and confidence
        """
        text_lower = text.lower()
        
        # Positive keywords
        positive_keywords = [
            'tăng', 'tăng trưởng', 'lợi nhuận', 'thành công', 'tốt', 'cao',
            'mạnh', 'khả quan', 'tích cực', 'phát triển', 'cải thiện',
            'increase', 'growth', 'profit', 'success', 'good', 'high',
            'strong', 'positive', 'improve', 'gain'
        ]
        
        # Negative keywords
        negative_keywords = [
            'giảm', 'lỗ', 'thất bại', 'xấu', 'thấp', 'yếu', 'khó khăn',
            'tiêu cực', 'suy giảm', 'rủi ro', 'lo ngại',
            'decrease', 'loss', 'fail', 'bad', 'low', 'weak', 'difficult',
            'negative', 'decline', 'risk', 'concern'
        ]
        
        # Count keyword occurrences
        positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
        negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
        
        total_count = positive_count + negative_count
        
        if total_count == 0:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.5
            }
        
        # Calculate sentiment score
        score = (positive_count - negative_count) / max(total_count, 1)
        
        # Determine sentiment category
        if score > 0.2:
            sentiment = 'positive'
        elif score < -0.2:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Calculate confidence based on keyword density
        confidence = min(total_count / 10.0, 1.0)
        
        return {
            'sentiment': sentiment,
            'score': score,
            'confidence': confidence
        }
    
    def generate_summary(self, texts: List[str]) -> str:
        """
        Generate summary of multiple texts.
        
        Args:
            texts: List of texts to summarize
            
        Returns:
            Summary text
        """
        if self.use_openai:
            return self._generate_summary_openai(texts)
        else:
            return self._generate_summary_simple(texts)
    
    def _generate_summary_openai(self, texts: List[str]) -> str:
        """
        Generate summary using OpenAI API.
        
        Args:
            texts: List of texts to summarize
            
        Returns:
            Summary text
        """
        try:
            if not texts:
                return "No news articles available for summary."
            
            # Combine texts with truncation
            max_chars = 3000
            combined_text = ""
            for i, text in enumerate(texts[:10], 1):  # Limit to 10 articles
                article_text = f"\n\nArticle {i}:\n{text[:300]}..."
                if len(combined_text) + len(article_text) > max_chars:
                    break
                combined_text += article_text
            
            prompt = f"""Summarize the following Vietnamese stock market news articles in 2-3 sentences. 
Focus on the key trends, events, and sentiment.
{combined_text}

Summary:"""

            # Use max_completion_tokens for newer models, max_tokens for older ones
            completion_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a financial news summarization expert. Provide concise, informative summaries."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5
            }
            
            # Try different token limit parameters based on model
            try:
                # Try max_completion_tokens first (newer API)
                completion_params["max_completion_tokens"] = 200
                response = self.client.chat.completions.create(**completion_params)
            except Exception as e:
                error_msg = str(e).lower()
                if "max_completion_tokens" in error_msg or "unexpected" in error_msg:
                    # Fallback to max_tokens for older models
                    del completion_params["max_completion_tokens"]
                    completion_params["max_tokens"] = 200
                    try:
                        response = self.client.chat.completions.create(**completion_params)
                    except Exception as e2:
                        # If still failing, try without token limits
                        logger.warning(f"Failed with max_tokens, trying without limits: {e2}")
                        del completion_params["max_tokens"]
                        response = self.client.chat.completions.create(**completion_params)
                else:
                    raise
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            logger.error(f"Error in OpenAI summary generation: {e}", exc_info=True)
            # Fallback to simple summary
            return self._generate_summary_simple(texts)
    
    def _generate_summary_simple(self, texts: List[str]) -> str:
        """
        Generate simple summary (fallback).
        
        Args:
            texts: List of texts to summarize
            
        Returns:
            Summary text
        """
        if not texts:
            return "No news articles available for summary."
        
        # Extract first sentence from each text as a simple summary
        sentences = []
        for text in texts[:5]:  # Limit to first 5 articles
            # Get first sentence (simplified)
            first_sentence = text.split('.')[0] if '.' in text else text[:100]
            sentences.append(first_sentence.strip())
        
        summary = ' | '.join(sentences)
        
        if len(texts) > 5:
            summary += f" ... and {len(texts) - 5} more articles."
        
        return summary


class LLMEngine:
    """
    LLM Engine for qualitative stock analysis.
    
    Responsibilities:
    - Retrieve news articles from MongoDB
    - Analyze sentiment of news articles
    - Generate summaries of multiple articles
    - Calculate influence scores based on source credibility
    - Store analysis results in MongoDB
    """
    
    # Source credibility scores (0.0 to 1.0)
    SOURCE_CREDIBILITY = {
        'cafef.vn': 0.9,
        'vnexpress.net': 0.95,
        'vietstock.vn': 0.9,
        'ndh.vn': 0.85,
        'baodautu.vn': 0.8,
        'default': 0.7
    }
    
    def __init__(self, mongo_client: MongoClient, llm_client: Optional[LLMClient] = None,
                 database_name: str = 'vietnam_stock_ai', api_key: Optional[str] = None,
                 model: str = 'gpt-3.5-turbo', use_openai: bool = True):
        """
        Initialize LLMEngine.
        
        Args:
            mongo_client: MongoDB client instance
            llm_client: LLM client for sentiment analysis (optional, creates default if None)
            database_name: Name of the database to use
            api_key: OpenAI API key (optional, will try to load from config)
            model: OpenAI model to use (default: gpt-3.5-turbo)
            use_openai: Whether to use OpenAI API or fallback to keyword-based analysis
        """
        self.db = mongo_client[database_name]
        self.news_collection = self.db['news']
        self.analysis_collection = self.db['llm_analysis']
        
        if llm_client is not None:
            self.llm = llm_client
        else:
            # Create LLM client with provided or config settings
            if api_key is None:
                from src.config import config
                api_key = config.OPENAI_API_KEY
                model = config.OPENAI_MODEL
            
            self.llm = LLMClient(api_key=api_key, model=model, use_openai=use_openai)
        
        logger.info("LLMEngine initialized")
    
    def analyze_news(self, symbol: str, lookback_days: int = 7) -> Optional[NewsAnalysisResult]:
        """
        Perform qualitative analysis on news articles.
        
        Args:
            symbol: Stock symbol code
            lookback_days: Number of days of news to analyze
            
        Returns:
            NewsAnalysisResult with sentiment and summaries, or None if no news found
        """
        logger.info(f"Starting LLM analysis for {symbol}")
        
        try:
            # Retrieve news articles
            articles = self._retrieve_news_articles(symbol, lookback_days)
            
            if not articles:
                logger.warning(
                    f"No news articles found for analysis",
                    context={'symbol': symbol}
                )
                return None
            
            # Analyze sentiment for each article
            sentiment_results = []
            influence_scores = []
            article_texts = []
            
            for article in articles:
                # Analyze sentiment
                sentiment = self.analyze_sentiment(article['title'] + ' ' + article['content'])
                sentiment_results.append(sentiment)
                
                # Calculate influence score
                influence = self.calculate_influence_score(article)
                influence_scores.append(influence)
                
                # Collect text for summary
                article_texts.append(article['title'] + '. ' + article['content'])
            
            # Calculate overall sentiment
            overall_sentiment = self._aggregate_sentiment(sentiment_results, influence_scores)
            
            # Generate summary
            summary = self.generate_summary(article_texts)
            
            # Calculate overall influence score
            overall_influence = sum(influence_scores) / len(influence_scores) if influence_scores else 0.0
            
            # Create analysis result
            result = NewsAnalysisResult(
                symbol=symbol,
                timestamp=datetime.utcnow().isoformat(),
                sentiment=overall_sentiment,
                summary=summary,
                influence_score=overall_influence,
                articles_analyzed=len(articles)
            )
            
            # Store result in MongoDB
            self._store_result(result)
            
            logger.info(
                f"LLM analysis completed for {symbol}",
                context={
                    'sentiment': overall_sentiment.sentiment,
                    'score': overall_sentiment.score,
                    'articles_analyzed': len(articles)
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(
                f"Error during LLM analysis",
                context={'symbol': symbol, 'error': str(e)},
                exc_info=True
            )
            return None
    
    def _retrieve_news_articles(self, symbol: str, lookback_days: int) -> List[Dict[str, Any]]:
        """
        Retrieve news articles from MongoDB.
        
        Args:
            symbol: Stock symbol code
            lookback_days: Number of days to look back
            
        Returns:
            List of news article documents
        """
        try:
            # Calculate start date
            start_date = datetime.utcnow() - timedelta(days=lookback_days)
            
            # Query MongoDB
            cursor = self.news_collection.find(
                {
                    'symbol': symbol,
                    'collected_at': {'$gte': start_date.isoformat()}
                },
                sort=[('collected_at', -1)]  # Most recent first
            )
            
            articles = list(cursor)
            
            logger.debug(
                f"Retrieved {len(articles)} news articles",
                context={'symbol': symbol}
            )
            
            return articles
            
        except Exception as e:
            logger.error(
                f"Error retrieving news articles",
                context={'symbol': symbol, 'error': str(e)},
                exc_info=True
            )
            return []
    
    def analyze_sentiment(self, text: str) -> SentimentResult:
        """
        Analyze sentiment of single article.
        
        Args:
            text: Article text (title + content)
            
        Returns:
            SentimentResult with classification and confidence
        """
        try:
            # Call LLM for sentiment analysis
            result = self.llm.analyze_sentiment(text)
            
            return SentimentResult(
                sentiment=result['sentiment'],
                score=result['score'],
                confidence=result['confidence']
            )
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}", exc_info=True)
            # Return neutral sentiment on error
            return SentimentResult(
                sentiment='neutral',
                score=0.0,
                confidence=0.0
            )
    
    def generate_summary(self, articles: List[str]) -> str:
        """
        Generate summary of multiple articles.
        
        Args:
            articles: List of article texts
            
        Returns:
            Summary text
        """
        try:
            # Call LLM for summary generation
            summary = self.llm.generate_summary(articles)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}", exc_info=True)
            return "Unable to generate summary due to error."
    
    def calculate_influence_score(self, article: Dict[str, Any]) -> float:
        """
        Calculate influence score based on source credibility.
        
        Args:
            article: News article document with 'source' field
            
        Returns:
            Influence score between 0.0 and 1.0
        """
        try:
            source = article.get('source', '').lower()
            
            # Look up credibility score
            for known_source, credibility in self.SOURCE_CREDIBILITY.items():
                if known_source in source:
                    return credibility
            
            # Return default credibility for unknown sources
            return self.SOURCE_CREDIBILITY['default']
            
        except Exception as e:
            logger.error(f"Error calculating influence score: {str(e)}", exc_info=True)
            return 0.5  # Default medium influence on error
    
    def _aggregate_sentiment(self, sentiment_results: List[SentimentResult],
                            influence_scores: List[float]) -> SentimentResult:
        """
        Aggregate multiple sentiment results into overall sentiment.
        
        Args:
            sentiment_results: List of individual sentiment results
            influence_scores: List of influence scores for weighting
            
        Returns:
            Aggregated SentimentResult
        """
        if not sentiment_results:
            return SentimentResult(sentiment='neutral', score=0.0, confidence=0.0)
        
        # Calculate weighted average score
        total_weight = sum(influence_scores)
        if total_weight == 0:
            weighted_score = sum(s.score for s in sentiment_results) / len(sentiment_results)
            weighted_confidence = sum(s.confidence for s in sentiment_results) / len(sentiment_results)
        else:
            weighted_score = sum(
                s.score * w for s, w in zip(sentiment_results, influence_scores)
            ) / total_weight
            
            weighted_confidence = sum(
                s.confidence * w for s, w in zip(sentiment_results, influence_scores)
            ) / total_weight
        
        # Determine overall sentiment category
        if weighted_score > 0.2:
            sentiment = 'positive'
        elif weighted_score < -0.2:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return SentimentResult(
            sentiment=sentiment,
            score=weighted_score,
            confidence=weighted_confidence
        )
    
    def _store_result(self, result: NewsAnalysisResult) -> bool:
        """
        Store analysis result in MongoDB.
        
        Args:
            result: NewsAnalysisResult to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            document = result.to_dict()
            self.analysis_collection.insert_one(document)
            
            logger.debug(
                f"Stored LLM analysis result",
                context={'symbol': result.symbol}
            )
            
            return True
            
        except Exception as e:
            logger.error(
                f"Error storing analysis result",
                context={'symbol': result.symbol, 'error': str(e)},
                exc_info=True
            )
            return False
