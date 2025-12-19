"""
Aggregation Service for combining AI/ML and LLM analysis results.
Generates final investment recommendations and alerts.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pymongo import MongoClient

from src.logging_config import get_logger
from src.utils.time_utils import current_epoch

logger = get_logger(__name__)


@dataclass
class Alert:
    """Investment alert."""
    type: str  # 'BUY', 'WATCH', or 'RISK'
    priority: str  # 'high', 'medium', or 'low'
    message: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class FinalScore:
    """Final aggregated score and recommendation."""
    symbol: str
    timestamp: float  # Changed to float for epoch timestamp
    final_score: float  # 0-100
    recommendation: str  # 'BUY', 'WATCH', or 'RISK'
    components: Dict[str, float]  # Individual component scores
    alerts: List[Alert]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        result = asdict(self)
        result['alerts'] = [alert.to_dict() for alert in self.alerts]
        return result


class AggregationService:
    """
    Aggregation Service for combining AI/ML and LLM analysis results.
    
    Responsibilities:
    - Retrieve AI/ML and LLM analysis results from MongoDB
    - Combine technical score, risk score, and sentiment score using weighted formula
    - Generate final recommendation score (0-100)
    - Generate alerts based on score thresholds
    - Store final scores in MongoDB
    """
    
    def __init__(self, mongo_client: MongoClient, database_name: str = 'vietnam_stock_ai',
                 weights: Optional[Dict[str, float]] = None):
        """
        Initialize AggregationService.
        
        Args:
            mongo_client: MongoDB client instance
            database_name: Name of the database to use
            weights: Custom weights for score components (optional)
                    Default: {'technical': 0.4, 'risk': 0.3, 'sentiment': 0.3}
        """
        self.db = mongo_client[database_name]
        self.ai_analysis_collection = self.db['ai_analysis']
        self.llm_analysis_collection = self.db['llm_analysis']
        self.final_scores_collection = self.db['final_scores']
        
        # Set weights with defaults
        self.weights = weights if weights is not None else {
            'technical': 0.4,
            'risk': 0.3,
            'sentiment': 0.3
        }
        
        logger.info(
            "AggregationService initialized",
            context={'weights': self.weights}
        )
    
    def aggregate(self, symbol: str) -> Optional[FinalScore]:
        """
        Aggregate AI/ML and LLM results for a stock.
        
        Args:
            symbol: Stock symbol code
            
        Returns:
            FinalScore with recommendation and alerts, or None if data not available
        """
        logger.info(f"Starting aggregation for {symbol}")
        
        try:
            # Retrieve latest AI/ML analysis
            ai_result = self._get_latest_ai_analysis(symbol)
            if ai_result is None:
                logger.warning(
                    f"No AI/ML analysis found for aggregation",
                    context={'symbol': symbol}
                )
                return None
            
            # Retrieve latest LLM analysis
            llm_result = self._get_latest_llm_analysis(symbol)
            if llm_result is None:
                logger.warning(
                    f"No LLM analysis found for aggregation",
                    context={'symbol': symbol}
                )
                return None
            
            # Calculate final score
            final_score = self.calculate_final_score(ai_result, llm_result)
            
            # Determine recommendation
            recommendation = self._determine_recommendation(final_score)
            
            # Generate alerts
            alerts = self.generate_alerts(final_score, symbol)
            
            # Extract component scores
            components = {
                'technical_score': ai_result['technical_score'],
                'risk_score': ai_result['risk_score'],
                'sentiment_score': self._normalize_sentiment_score(llm_result['sentiment']['score'])
            }
            
            # Create final score object
            result = FinalScore(
                symbol=symbol,
                timestamp=current_epoch(),  # Use epoch timestamp
                final_score=final_score,
                recommendation=recommendation,
                components=components,
                alerts=alerts
            )
            
            # Store result in MongoDB
            self._store_result(result)
            
            logger.info(
                f"Aggregation completed for {symbol}",
                context={
                    'final_score': final_score,
                    'recommendation': recommendation,
                    'alerts_count': len(alerts)
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(
                f"Error during aggregation",
                context={'symbol': symbol, 'error': str(e)},
                exc_info=True
            )
            return None
    
    def calculate_final_score(self, ai_result: Dict[str, Any], 
                             llm_result: Dict[str, Any]) -> float:
        """
        Calculate weighted final score from AI/ML and LLM results.
        
        Formula:
        final_score = (technical_score * w_tech + 
                      (1 - risk_score) * w_risk + 
                      sentiment_score * w_sent) * 100
        
        Args:
            ai_result: AI/ML analysis result document
            llm_result: LLM analysis result document
            
        Returns:
            Final score between 0 and 100
        """
        try:
            # Extract scores
            technical_score = ai_result['technical_score']
            risk_score = ai_result['risk_score']
            sentiment_score = self._normalize_sentiment_score(llm_result['sentiment']['score'])
            
            # Calculate weighted score
            # Note: We invert risk_score because lower risk is better
            weighted_score = (
                technical_score * self.weights['technical'] +
                (1.0 - risk_score) * self.weights['risk'] +
                sentiment_score * self.weights['sentiment']
            )
            
            # Scale to 0-100
            final_score = weighted_score * 100
            
            # Ensure within bounds
            final_score = max(0.0, min(100.0, final_score))
            
            return float(final_score)
            
        except Exception as e:
            logger.error(f"Error calculating final score: {str(e)}", exc_info=True)
            return 50.0  # Default neutral score on error
    
    def generate_alerts(self, final_score: float, symbol: str) -> List[Alert]:
        """
        Generate alerts based on score thresholds.
        
        Thresholds:
        - Score > 70: BUY alert (high priority)
        - Score 40-70: WATCH alert (medium priority)
        - Score < 40: RISK alert (high priority)
        
        Args:
            final_score: Final recommendation score (0-100)
            symbol: Stock symbol code
            
        Returns:
            List of Alert objects
        """
        alerts = []
        
        try:
            if final_score > 70:
                alerts.append(Alert(
                    type='BUY',
                    priority='high',
                    message=f"Strong buy signal detected for {symbol}. Score: {final_score:.1f}"
                ))
            elif final_score >= 40:
                alerts.append(Alert(
                    type='WATCH',
                    priority='medium',
                    message=f"Watch signal for {symbol}. Score: {final_score:.1f}"
                ))
            else:
                alerts.append(Alert(
                    type='RISK',
                    priority='high',
                    message=f"Risk alert for {symbol}. Score: {final_score:.1f}"
                ))
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error generating alerts: {str(e)}", exc_info=True)
            return []
    
    def _get_latest_ai_analysis(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve latest AI/ML analysis for a symbol.
        
        Args:
            symbol: Stock symbol code
            
        Returns:
            AI/ML analysis document or None if not found
        """
        try:
            result = self.ai_analysis_collection.find_one(
                {'symbol': symbol},
                sort=[('timestamp', -1)]  # Most recent first
            )
            
            if result:
                logger.debug(f"Retrieved AI/ML analysis for {symbol}")
            
            return result
            
        except Exception as e:
            logger.error(
                f"Error retrieving AI/ML analysis",
                context={'symbol': symbol, 'error': str(e)},
                exc_info=True
            )
            return None
    
    def _get_latest_llm_analysis(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve latest LLM analysis for a symbol.
        
        Args:
            symbol: Stock symbol code
            
        Returns:
            LLM analysis document or None if not found
        """
        try:
            result = self.llm_analysis_collection.find_one(
                {'symbol': symbol},
                sort=[('timestamp', -1)]  # Most recent first
            )
            
            if result:
                logger.debug(f"Retrieved LLM analysis for {symbol}")
            
            return result
            
        except Exception as e:
            logger.error(
                f"Error retrieving LLM analysis",
                context={'symbol': symbol, 'error': str(e)},
                exc_info=True
            )
            return None
    
    def _normalize_sentiment_score(self, sentiment_score: float) -> float:
        """
        Normalize sentiment score from -1.0 to 1.0 range to 0.0 to 1.0 range.
        
        Args:
            sentiment_score: Sentiment score from -1.0 (negative) to 1.0 (positive)
            
        Returns:
            Normalized score from 0.0 to 1.0
        """
        return (sentiment_score + 1.0) / 2.0
    
    def _determine_recommendation(self, final_score: float) -> str:
        """
        Determine recommendation category based on final score.
        
        Args:
            final_score: Final score (0-100)
            
        Returns:
            Recommendation string: 'BUY', 'WATCH', or 'RISK'
        """
        if final_score > 70:
            return 'BUY'
        elif final_score >= 40:
            return 'WATCH'
        else:
            return 'RISK'
    
    def _store_result(self, result: FinalScore) -> bool:
        """
        Store final score result in MongoDB.
        
        Args:
            result: FinalScore to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            document = result.to_dict()
            self.final_scores_collection.insert_one(document)
            
            logger.debug(
                f"Stored final score result",
                context={'symbol': result.symbol}
            )
            
            return True
            
        except Exception as e:
            logger.error(
                f"Error storing final score result",
                context={'symbol': result.symbol, 'error': str(e)},
                exc_info=True
            )
            return False
