"""
AI/ML Engine for quantitative stock analysis.
Performs time-series analysis, risk assessment, and technical indicator calculations.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np
from pymongo import MongoClient
from ta.trend import MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

from src.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class TrendPrediction:
    """Trend prediction result."""
    direction: str  # 'up', 'down', or 'neutral'
    confidence: float  # 0.0 to 1.0
    predicted_price: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class AnalysisResult:
    """Complete AI/ML analysis result for a stock."""
    symbol: str
    timestamp: str
    trend_prediction: TrendPrediction
    risk_score: float  # 0.0 to 1.0
    technical_score: float  # 0.0 to 1.0
    indicators: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        result = asdict(self)
        result['trend_prediction'] = self.trend_prediction.to_dict()
        return result


class AIMLEngine:
    """
    AI/ML Engine for quantitative stock analysis.
    
    Responsibilities:
    - Retrieve historical price data from MongoDB
    - Calculate trend predictions using time-series analysis
    - Calculate risk scores based on volatility
    - Calculate technical scores using indicators (RSI, MACD, etc.)
    - Store analysis results in MongoDB
    """
    
    def __init__(self, mongo_client: MongoClient, database_name: str = 'vietnam_stock_ai'):
        """
        Initialize AIMLEngine.
        
        Args:
            mongo_client: MongoDB client instance
            database_name: Name of the database to use
        """
        self.db = mongo_client[database_name]
        self.price_collection = self.db['price_history']
        self.analysis_collection = self.db['ai_analysis']
        
        logger.info("AIMLEngine initialized")
    
    def analyze_stock(self, symbol: str, lookback_days: int = 90) -> Optional[AnalysisResult]:
        """
        Perform quantitative analysis on stock.
        
        Args:
            symbol: Stock symbol code
            lookback_days: Number of days of historical data to analyze
            
        Returns:
            AnalysisResult with scores and predictions, or None if insufficient data
        """
        logger.info(f"Starting AI/ML analysis for {symbol}")
        
        try:
            # Retrieve historical price data
            price_data = self._retrieve_price_data(symbol, lookback_days)
            
            if price_data is None or len(price_data) < 20:
                logger.warning(
                    f"Insufficient price data for analysis",
                    context={'symbol': symbol, 'data_points': len(price_data) if price_data is not None else 0}
                )
                return None
            
            # Calculate trend prediction
            trend = self.calculate_trend(price_data)
            
            # Calculate risk score
            risk_score = self.calculate_risk_score(price_data)
            
            # Calculate technical score
            technical_score = self.calculate_technical_score(price_data)
            
            # Calculate technical indicators for storage
            indicators = self._calculate_indicators(price_data)
            
            # Create analysis result
            result = AnalysisResult(
                symbol=symbol,
                timestamp=datetime.utcnow().isoformat(),
                trend_prediction=trend,
                risk_score=risk_score,
                technical_score=technical_score,
                indicators=indicators
            )
            
            # Store result in MongoDB
            self._store_result(result)
            
            logger.info(
                f"AI/ML analysis completed for {symbol}",
                context={
                    'trend': trend.direction,
                    'risk_score': risk_score,
                    'technical_score': technical_score
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(
                f"Error during AI/ML analysis",
                context={'symbol': symbol, 'error': str(e)},
                exc_info=True
            )
            return None
    
    def _retrieve_price_data(self, symbol: str, lookback_days: int) -> Optional[pd.DataFrame]:
        """
        Retrieve historical price data from MongoDB.
        
        Args:
            symbol: Stock symbol code
            lookback_days: Number of days to look back
            
        Returns:
            DataFrame with price data or None if no data found
        """
        try:
            # Calculate start date
            start_date = datetime.utcnow() - timedelta(days=lookback_days)
            
            # Query MongoDB
            cursor = self.price_collection.find(
                {
                    'symbol': symbol,
                    'timestamp': {'$gte': start_date.isoformat()}
                },
                sort=[('timestamp', 1)]
            )
            
            # Convert to DataFrame
            data = list(cursor)
            
            if not data:
                logger.warning(f"No price data found for {symbol}")
                return None
            
            df = pd.DataFrame(data)
            
            # Ensure required columns exist
            required_cols = ['timestamp', 'open', 'close', 'high', 'low', 'volume']
            if not all(col in df.columns for col in required_cols):
                logger.error(f"Missing required columns in price data for {symbol}")
                return None
            
            # Convert timestamp to datetime - handle mixed timezone formats
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
            # Convert to timezone-naive UTC for consistent sorting
            df['timestamp'] = df['timestamp'].dt.tz_localize(None)
            df = df.sort_values('timestamp')
            
            return df
            
        except Exception as e:
            logger.error(
                f"Error retrieving price data",
                context={'symbol': symbol, 'error': str(e)},
                exc_info=True
            )
            return None
    
    def calculate_trend(self, price_data: pd.DataFrame) -> TrendPrediction:
        """
        Calculate trend using time-series analysis.
        
        Uses simple moving average crossover strategy:
        - Short-term MA (20 periods) vs Long-term MA (50 periods)
        - Uptrend: short MA > long MA
        - Downtrend: short MA < long MA
        
        Args:
            price_data: DataFrame with price history
            
        Returns:
            TrendPrediction with direction and confidence
        """
        try:
            if len(price_data) < 50:
                # Not enough data for 50-period MA, use simpler approach
                return self._calculate_simple_trend(price_data)
            
            # Calculate moving averages
            price_data = price_data.copy()
            price_data['ma_20'] = price_data['close'].rolling(window=20).mean()
            price_data['ma_50'] = price_data['close'].rolling(window=50).mean()
            
            # Get latest values
            latest = price_data.iloc[-1]
            ma_20 = latest['ma_20']
            ma_50 = latest['ma_50']
            current_price = latest['close']
            
            # Determine trend direction
            if pd.isna(ma_20) or pd.isna(ma_50):
                return self._calculate_simple_trend(price_data)
            
            # Calculate confidence based on separation between MAs
            separation = abs(ma_20 - ma_50) / ma_50
            confidence = min(separation * 10, 1.0)  # Scale to 0-1
            
            if ma_20 > ma_50:
                direction = 'up'
                # Predict price based on trend continuation
                predicted_price = current_price * (1 + separation * 0.5)
            elif ma_20 < ma_50:
                direction = 'down'
                predicted_price = current_price * (1 - separation * 0.5)
            else:
                direction = 'neutral'
                predicted_price = current_price
            
            return TrendPrediction(
                direction=direction,
                confidence=float(confidence),
                predicted_price=float(predicted_price)
            )
            
        except Exception as e:
            logger.error(f"Error calculating trend: {str(e)}", exc_info=True)
            # Return neutral trend on error
            return TrendPrediction(
                direction='neutral',
                confidence=0.0,
                predicted_price=None
            )
    
    def _calculate_simple_trend(self, price_data: pd.DataFrame) -> TrendPrediction:
        """
        Calculate simple trend for limited data.
        
        Args:
            price_data: DataFrame with price history
            
        Returns:
            TrendPrediction based on recent price movement
        """
        if len(price_data) < 5:
            return TrendPrediction(direction='neutral', confidence=0.0, predicted_price=None)
        
        # Compare recent average to older average
        recent_avg = price_data['close'].tail(5).mean()
        older_avg = price_data['close'].head(5).mean()
        current_price = price_data['close'].iloc[-1]
        
        change_pct = (recent_avg - older_avg) / older_avg
        confidence = min(abs(change_pct) * 5, 1.0)
        
        if change_pct > 0.02:
            direction = 'up'
            predicted_price = current_price * (1 + change_pct)
        elif change_pct < -0.02:
            direction = 'down'
            predicted_price = current_price * (1 + change_pct)
        else:
            direction = 'neutral'
            predicted_price = current_price
        
        return TrendPrediction(
            direction=direction,
            confidence=float(confidence),
            predicted_price=float(predicted_price)
        )
    
    def calculate_risk_score(self, price_data: pd.DataFrame) -> float:
        """
        Calculate risk score based on volatility.
        
        Uses standard deviation of returns as volatility measure.
        Higher volatility = higher risk.
        
        Args:
            price_data: DataFrame with price history
            
        Returns:
            Risk score between 0.0 (low risk) and 1.0 (high risk)
        """
        try:
            if len(price_data) < 2:
                return 0.5  # Default medium risk for insufficient data
            
            # Calculate daily returns
            price_data = price_data.copy()
            price_data['returns'] = price_data['close'].pct_change()
            
            # Calculate volatility (standard deviation of returns)
            volatility = price_data['returns'].std()
            
            if pd.isna(volatility):
                return 0.5
            
            # Normalize volatility to 0-1 scale
            # Typical stock volatility ranges from 0% to 10% daily
            # We'll map 0-5% to 0-1 risk score
            risk_score = min(volatility / 0.05, 1.0)
            
            return float(risk_score)
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {str(e)}", exc_info=True)
            return 0.5  # Default medium risk on error
    
    def calculate_technical_score(self, price_data: pd.DataFrame) -> float:
        """
        Calculate technical score using indicators (RSI, MACD, etc.).
        
        Combines multiple technical indicators:
        - RSI (Relative Strength Index): 30-70 is neutral, <30 oversold, >70 overbought
        - MACD: Positive signal = bullish, negative = bearish
        - Bollinger Bands: Price position relative to bands
        
        Args:
            price_data: DataFrame with price history
            
        Returns:
            Technical score between 0.0 (bearish) and 1.0 (bullish)
        """
        try:
            if len(price_data) < 26:  # MACD needs at least 26 periods
                return 0.5  # Default neutral score for insufficient data
            
            price_data = price_data.copy()
            scores = []
            
            # RSI Score (14-period)
            if len(price_data) >= 14:
                rsi_indicator = RSIIndicator(close=price_data['close'], window=14)
                rsi = rsi_indicator.rsi().iloc[-1]
                
                if not pd.isna(rsi):
                    # Convert RSI to 0-1 score
                    # RSI < 30: oversold (bullish) = high score
                    # RSI > 70: overbought (bearish) = low score
                    # RSI 30-70: neutral = medium score
                    if rsi < 30:
                        rsi_score = 0.7 + (30 - rsi) / 30 * 0.3  # 0.7-1.0
                    elif rsi > 70:
                        rsi_score = 0.3 - (rsi - 70) / 30 * 0.3  # 0.0-0.3
                    else:
                        rsi_score = 0.3 + (rsi - 30) / 40 * 0.4  # 0.3-0.7
                    
                    scores.append(rsi_score)
            
            # MACD Score
            if len(price_data) >= 26:
                macd_indicator = MACD(close=price_data['close'])
                macd_line = macd_indicator.macd().iloc[-1]
                signal_line = macd_indicator.macd_signal().iloc[-1]
                
                if not pd.isna(macd_line) and not pd.isna(signal_line):
                    # MACD above signal = bullish
                    macd_diff = macd_line - signal_line
                    # Normalize to 0-1 (assuming typical diff range of -10 to +10)
                    macd_score = 0.5 + np.tanh(macd_diff / 5) * 0.5
                    scores.append(macd_score)
            
            # Bollinger Bands Score
            if len(price_data) >= 20:
                bb_indicator = BollingerBands(close=price_data['close'], window=20, window_dev=2)
                current_price = price_data['close'].iloc[-1]
                bb_high = bb_indicator.bollinger_hband().iloc[-1]
                bb_low = bb_indicator.bollinger_lband().iloc[-1]
                bb_mid = bb_indicator.bollinger_mavg().iloc[-1]
                
                if not any(pd.isna([bb_high, bb_low, bb_mid])):
                    # Position within bands
                    if bb_high != bb_low:
                        bb_position = (current_price - bb_low) / (bb_high - bb_low)
                        # Near lower band = oversold = bullish
                        # Near upper band = overbought = bearish
                        bb_score = 1.0 - bb_position
                        scores.append(bb_score)
            
            # Calculate average score
            if scores:
                technical_score = np.mean(scores)
                return float(np.clip(technical_score, 0.0, 1.0))
            else:
                return 0.5  # Default neutral score
                
        except Exception as e:
            logger.error(f"Error calculating technical score: {str(e)}", exc_info=True)
            return 0.5  # Default neutral score on error
    
    def _calculate_indicators(self, price_data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate technical indicators for storage.
        
        Args:
            price_data: DataFrame with price history
            
        Returns:
            Dictionary of indicator values
        """
        indicators = {}
        
        try:
            # RSI
            if len(price_data) >= 14:
                rsi_indicator = RSIIndicator(close=price_data['close'], window=14)
                rsi = rsi_indicator.rsi().iloc[-1]
                if not pd.isna(rsi):
                    indicators['rsi'] = float(rsi)
            
            # MACD
            if len(price_data) >= 26:
                macd_indicator = MACD(close=price_data['close'])
                macd = macd_indicator.macd().iloc[-1]
                if not pd.isna(macd):
                    indicators['macd'] = float(macd)
            
            # Moving averages
            if len(price_data) >= 20:
                ma_20 = price_data['close'].rolling(window=20).mean().iloc[-1]
                if not pd.isna(ma_20):
                    indicators['moving_avg_20'] = float(ma_20)
            
            if len(price_data) >= 50:
                ma_50 = price_data['close'].rolling(window=50).mean().iloc[-1]
                if not pd.isna(ma_50):
                    indicators['moving_avg_50'] = float(ma_50)
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {str(e)}", exc_info=True)
        
        return indicators
    
    def _store_result(self, result: AnalysisResult) -> bool:
        """
        Store analysis result in MongoDB.
        
        Args:
            result: AnalysisResult to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            document = result.to_dict()
            self.analysis_collection.insert_one(document)
            
            logger.debug(
                f"Stored AI/ML analysis result",
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
