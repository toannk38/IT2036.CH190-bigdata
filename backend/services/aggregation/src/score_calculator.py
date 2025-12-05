import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import asyncio
import aiohttp

@dataclass
class TechnicalScore:
    rsi_score: float
    macd_score: float
    bollinger_score: float
    volume_score: float
    pattern_score: float
    trend_score: float
    overall_technical: float
    confidence: float

@dataclass
class SentimentScore:
    news_sentiment: float
    sentiment_confidence: float
    news_impact: float
    market_sentiment: float
    overall_sentiment: float
    confidence: float

@dataclass
class FinalScore:
    stock_symbol: str
    technical_score: float
    sentiment_score: float
    risk_score: float
    final_score: float
    recommendation: str
    confidence: float
    timestamp: datetime
    components: Dict[str, Any]

class ScoreCalculator:
    """Calculate comprehensive stock scores from technical and sentiment analysis"""
    
    def __init__(self, ai_analysis_url: str = "http://localhost:8003", 
                 llm_analysis_url: str = "http://localhost:8004"):
        self.ai_analysis_url = ai_analysis_url
        self.llm_analysis_url = llm_analysis_url
        
        # Scoring weights (will be optimized dynamically)
        self.weights = {
            'technical': {
                'rsi': 0.20,
                'macd': 0.25,
                'bollinger': 0.15,
                'volume': 0.15,
                'pattern': 0.15,
                'trend': 0.10
            },
            'sentiment': {
                'news_sentiment': 0.40,
                'news_impact': 0.30,
                'market_sentiment': 0.30
            },
            'final': {
                'technical': 0.60,
                'sentiment': 0.25,
                'risk': 0.15
            }
        }
        
        # Score thresholds
        self.thresholds = {
            'buy': 0.75,
            'hold': 0.50,
            'sell': 0.25
        }
    
    async def get_technical_analysis(self, stock_symbol: str) -> Dict[str, Any]:
        """Fetch technical analysis from AI Analysis Service"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.ai_analysis_url}/predict/{stock_symbol}") as response:
                    if response.status == 200:
                        return await response.json()
                    return {}
            except Exception:
                return {}
    
    async def get_sentiment_analysis(self, stock_symbol: str) -> Dict[str, Any]:
        """Fetch latest sentiment analysis from LLM Analysis Service"""
        async with aiohttp.ClientSession() as session:
            try:
                # Get recent news analysis for the stock
                async with session.get(f"{self.llm_analysis_url}/analyze/recent/{stock_symbol}") as response:
                    if response.status == 200:
                        return await response.json()
                    return {}
            except Exception:
                return {}
    
    def calculate_technical_score(self, technical_data: Dict[str, Any]) -> TechnicalScore:
        """Calculate technical analysis score"""
        if not technical_data:
            return TechnicalScore(0, 0, 0, 0, 0, 0, 0, 0)
        
        features = technical_data.get('features', {})
        predictions = technical_data.get('predictions', {})
        
        # RSI Score (0-1, inverted for oversold/overbought)
        rsi = features.get('rsi', 50)
        if rsi < 30:  # Oversold - bullish
            rsi_score = 0.8 + (30 - rsi) / 30 * 0.2
        elif rsi > 70:  # Overbought - bearish
            rsi_score = 0.2 - (rsi - 70) / 30 * 0.2
        else:  # Neutral zone
            rsi_score = 0.5 + (50 - abs(rsi - 50)) / 50 * 0.3
        
        # MACD Score
        macd = features.get('macd', 0)
        macd_signal = features.get('macd_signal', 0)
        macd_diff = macd - macd_signal
        macd_score = 0.5 + np.tanh(macd_diff * 10) * 0.5  # Normalize to 0-1
        
        # Bollinger Bands Score
        bb_position = features.get('bb_position', 0.5)  # Position within bands
        if bb_position < 0.2:  # Near lower band - oversold
            bollinger_score = 0.8
        elif bb_position > 0.8:  # Near upper band - overbought
            bollinger_score = 0.2
        else:
            bollinger_score = 0.5
        
        # Volume Score
        volume_ratio = features.get('volume_ratio', 1.0)
        volume_score = min(1.0, max(0.0, 0.3 + volume_ratio * 0.4))
        
        # Pattern Score
        patterns = features.get('patterns', [])
        pattern_score = 0.5
        for pattern in patterns:
            if pattern.get('signal') == 'bullish':
                pattern_score += pattern.get('confidence', 0) * 0.3
            elif pattern.get('signal') == 'bearish':
                pattern_score -= pattern.get('confidence', 0) * 0.3
        pattern_score = max(0, min(1, pattern_score))
        
        # Trend Score
        trend = predictions.get('trend_direction', 0)
        trend_confidence = predictions.get('confidence', 0.5)
        trend_score = 0.5 + trend * trend_confidence * 0.5
        
        # Calculate overall technical score
        weights = self.weights['technical']
        overall_technical = (
            rsi_score * weights['rsi'] +
            macd_score * weights['macd'] +
            bollinger_score * weights['bollinger'] +
            volume_score * weights['volume'] +
            pattern_score * weights['pattern'] +
            trend_score * weights['trend']
        )
        
        # Calculate confidence based on data quality
        confidence = min(1.0, len([x for x in [rsi, macd, bb_position] if x is not None]) / 3)
        
        return TechnicalScore(
            rsi_score=rsi_score,
            macd_score=macd_score,
            bollinger_score=bollinger_score,
            volume_score=volume_score,
            pattern_score=pattern_score,
            trend_score=trend_score,
            overall_technical=overall_technical,
            confidence=confidence
        )
    
    def calculate_sentiment_score(self, sentiment_data: Dict[str, Any]) -> SentimentScore:
        """Calculate sentiment analysis score"""
        if not sentiment_data:
            return SentimentScore(0.5, 0, 0.5, 0.5, 0.5, 0)
        
        # News sentiment score
        sentiment_results = sentiment_data.get('sentiment_results', [])
        if sentiment_results:
            sentiments = []
            confidences = []
            impacts = []
            
            for result in sentiment_results[-5:]:  # Last 5 news items
                sentiment = result.get('result', {}).get('sentiment', 'NEUTRAL')
                confidence = result.get('confidence', 0)
                impact = result.get('result', {}).get('market_impact', 'LOW')
                
                # Convert sentiment to score
                if sentiment == 'POSITIVE':
                    sent_score = 0.8
                elif sentiment == 'NEGATIVE':
                    sent_score = 0.2
                else:
                    sent_score = 0.5
                
                # Weight by confidence
                sentiments.append(sent_score * confidence)
                confidences.append(confidence)
                
                # Convert impact to score
                impact_score = {'HIGH': 0.9, 'MEDIUM': 0.6, 'LOW': 0.3}.get(impact, 0.3)
                impacts.append(impact_score)
            
            news_sentiment = np.mean(sentiments) if sentiments else 0.5
            sentiment_confidence = np.mean(confidences) if confidences else 0
            news_impact = np.mean(impacts) if impacts else 0.5
        else:
            news_sentiment = 0.5
            sentiment_confidence = 0
            news_impact = 0.5
        
        # Market sentiment (placeholder - would come from broader market analysis)
        market_sentiment = 0.5
        
        # Calculate overall sentiment score
        weights = self.weights['sentiment']
        overall_sentiment = (
            news_sentiment * weights['news_sentiment'] +
            news_impact * weights['news_impact'] +
            market_sentiment * weights['market_sentiment']
        )
        
        return SentimentScore(
            news_sentiment=news_sentiment,
            sentiment_confidence=sentiment_confidence,
            news_impact=news_impact,
            market_sentiment=market_sentiment,
            overall_sentiment=overall_sentiment,
            confidence=sentiment_confidence
        )
    
    def calculate_risk_score(self, technical_score: TechnicalScore, 
                           sentiment_score: SentimentScore, 
                           stock_data: Dict[str, Any]) -> float:
        """Calculate risk assessment score"""
        risk_factors = []
        
        # Volatility risk
        volatility = stock_data.get('volatility', 0.2)
        volatility_risk = min(1.0, volatility * 5)  # Normalize
        risk_factors.append(volatility_risk * 0.3)
        
        # Technical risk (extreme values indicate higher risk)
        tech_risk = 0
        if technical_score.rsi_score < 0.2 or technical_score.rsi_score > 0.8:
            tech_risk += 0.3
        if technical_score.bollinger_score < 0.3 or technical_score.bollinger_score > 0.7:
            tech_risk += 0.2
        risk_factors.append(tech_risk * 0.3)
        
        # Sentiment risk (low confidence or conflicting signals)
        sent_risk = 0
        if sentiment_score.confidence < 0.5:
            sent_risk += 0.4
        if abs(sentiment_score.overall_sentiment - 0.5) > 0.3:
            sent_risk += 0.2
        risk_factors.append(sent_risk * 0.2)
        
        # Market cap risk (smaller caps are riskier)
        market_cap = stock_data.get('market_cap', 1000000000)  # Default 1B
        if market_cap < 100000000:  # < 100M
            cap_risk = 0.8
        elif market_cap < 1000000000:  # < 1B
            cap_risk = 0.5
        else:
            cap_risk = 0.2
        risk_factors.append(cap_risk * 0.2)
        
        return sum(risk_factors)
    
    def generate_recommendation(self, final_score: float, confidence: float) -> str:
        """Generate investment recommendation"""
        if confidence < 0.4:
            return "WATCH"
        
        if final_score >= self.thresholds['buy']:
            return "BUY"
        elif final_score >= self.thresholds['hold']:
            return "HOLD"
        elif final_score >= self.thresholds['sell']:
            return "SELL"
        else:
            return "STRONG_SELL"
    
    async def calculate_comprehensive_score(self, stock_symbol: str, 
                                          stock_data: Dict[str, Any] = None) -> FinalScore:
        """Calculate comprehensive final score for a stock"""
        # Fetch analysis data
        technical_data, sentiment_data = await asyncio.gather(
            self.get_technical_analysis(stock_symbol),
            self.get_sentiment_analysis(stock_symbol),
            return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(technical_data, Exception):
            technical_data = {}
        if isinstance(sentiment_data, Exception):
            sentiment_data = {}
        
        # Calculate component scores
        technical_score = self.calculate_technical_score(technical_data)
        sentiment_score = self.calculate_sentiment_score(sentiment_data)
        
        # Calculate risk score
        if not stock_data:
            stock_data = {}
        risk_score = self.calculate_risk_score(technical_score, sentiment_score, stock_data)
        
        # Calculate final score
        weights = self.weights['final']
        final_score_value = (
            technical_score.overall_technical * weights['technical'] +
            sentiment_score.overall_sentiment * weights['sentiment'] +
            (1 - risk_score) * weights['risk']  # Lower risk = higher score
        )
        
        # Calculate overall confidence
        confidence = (
            technical_score.confidence * weights['technical'] +
            sentiment_score.confidence * weights['sentiment'] +
            0.7 * weights['risk']  # Risk calculation has moderate confidence
        )
        
        # Generate recommendation
        recommendation = self.generate_recommendation(final_score_value, confidence)
        
        # Compile components for transparency
        components = {
            'technical': {
                'rsi': technical_score.rsi_score,
                'macd': technical_score.macd_score,
                'bollinger': technical_score.bollinger_score,
                'volume': technical_score.volume_score,
                'pattern': technical_score.pattern_score,
                'trend': technical_score.trend_score,
                'overall': technical_score.overall_technical,
                'confidence': technical_score.confidence
            },
            'sentiment': {
                'news_sentiment': sentiment_score.news_sentiment,
                'news_impact': sentiment_score.news_impact,
                'market_sentiment': sentiment_score.market_sentiment,
                'overall': sentiment_score.overall_sentiment,
                'confidence': sentiment_score.confidence
            },
            'risk': {
                'score': risk_score,
                'level': 'HIGH' if risk_score > 0.7 else 'MEDIUM' if risk_score > 0.4 else 'LOW'
            },
            'weights': self.weights
        }
        
        return FinalScore(
            stock_symbol=stock_symbol,
            technical_score=technical_score.overall_technical,
            sentiment_score=sentiment_score.overall_sentiment,
            risk_score=risk_score,
            final_score=final_score_value,
            recommendation=recommendation,
            confidence=confidence,
            timestamp=datetime.now(),
            components=components
        )
    
    def update_weights(self, new_weights: Dict[str, Any]):
        """Update scoring weights (for optimization)"""
        self.weights.update(new_weights)
    
    def get_score_explanation(self, final_score: FinalScore) -> Dict[str, Any]:
        """Generate human-readable explanation of the score"""
        components = final_score.components
        
        explanation = {
            'overall_assessment': f"Score: {final_score.final_score:.2f} - {final_score.recommendation}",
            'confidence_level': f"{final_score.confidence:.1%}",
            'technical_analysis': {
                'score': f"{final_score.technical_score:.2f}",
                'key_factors': [],
                'strength': 'Strong' if final_score.technical_score > 0.7 else 'Moderate' if final_score.technical_score > 0.4 else 'Weak'
            },
            'sentiment_analysis': {
                'score': f"{final_score.sentiment_score:.2f}",
                'news_sentiment': 'Positive' if components['sentiment']['news_sentiment'] > 0.6 else 'Negative' if components['sentiment']['news_sentiment'] < 0.4 else 'Neutral',
                'strength': 'Strong' if final_score.sentiment_score > 0.7 else 'Moderate' if final_score.sentiment_score > 0.4 else 'Weak'
            },
            'risk_assessment': {
                'level': components['risk']['level'],
                'score': f"{final_score.risk_score:.2f}",
                'impact': 'High impact on final score' if final_score.risk_score > 0.6 else 'Moderate impact' if final_score.risk_score > 0.3 else 'Low impact'
            }
        }
        
        # Add key technical factors
        tech = components['technical']
        if tech['rsi'] > 0.7:
            explanation['technical_analysis']['key_factors'].append('Strong RSI signal')
        if tech['macd'] > 0.7:
            explanation['technical_analysis']['key_factors'].append('Bullish MACD crossover')
        if tech['trend'] > 0.7:
            explanation['technical_analysis']['key_factors'].append('Strong upward trend')
        
        return explanation