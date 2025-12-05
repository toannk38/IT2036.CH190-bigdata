import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class PatternResult:
    pattern_name: str
    confidence: float
    signal: str  # 'bullish', 'bearish', 'neutral'
    description: str

class PatternDetection:
    """Candlestick and chart pattern detection"""
    
    @staticmethod
    def detect_candlestick_patterns(opens: List[float], highs: List[float], 
                                   lows: List[float], closes: List[float]) -> List[PatternResult]:
        """Detect candlestick patterns"""
        if len(opens) < 3:
            return []
        
        patterns = []
        
        # Get last few candles for pattern detection
        for i in range(2, min(len(opens), 10)):
            # Doji pattern
            doji = PatternDetection._detect_doji(opens[-i], highs[-i], lows[-i], closes[-i])
            if doji:
                patterns.append(doji)
            
            # Hammer pattern
            if i >= 1:
                hammer = PatternDetection._detect_hammer(opens[-i], highs[-i], lows[-i], closes[-i])
                if hammer:
                    patterns.append(hammer)
            
            # Engulfing pattern (needs 2 candles)
            if i >= 2:
                engulfing = PatternDetection._detect_engulfing(
                    opens[-i-1:], highs[-i-1:], lows[-i-1:], closes[-i-1:]
                )
                if engulfing:
                    patterns.append(engulfing)
        
        return patterns
    
    @staticmethod
    def _detect_doji(open_price: float, high: float, low: float, close: float) -> PatternResult:
        """Detect Doji candlestick pattern"""
        body_size = abs(close - open_price)
        total_range = high - low
        
        if total_range == 0:
            return None
        
        body_ratio = body_size / total_range
        
        if body_ratio < 0.1:  # Very small body
            confidence = 1.0 - body_ratio * 10  # Higher confidence for smaller body
            return PatternResult(
                pattern_name="Doji",
                confidence=confidence,
                signal="neutral",
                description="Indecision in the market, potential reversal"
            )
        
        return None
    
    @staticmethod
    def _detect_hammer(open_price: float, high: float, low: float, close: float) -> PatternResult:
        """Detect Hammer candlestick pattern"""
        body_size = abs(close - open_price)
        total_range = high - low
        lower_shadow = min(open_price, close) - low
        upper_shadow = high - max(open_price, close)
        
        if total_range == 0:
            return None
        
        # Hammer criteria: long lower shadow, small body, small upper shadow
        if (lower_shadow > body_size * 2 and 
            upper_shadow < body_size and 
            body_size / total_range < 0.3):
            
            confidence = min(0.9, lower_shadow / total_range)
            signal = "bullish" if close > open_price else "bearish"
            
            return PatternResult(
                pattern_name="Hammer",
                confidence=confidence,
                signal=signal,
                description="Potential reversal pattern with long lower shadow"
            )
        
        return None
    
    @staticmethod
    def _detect_engulfing(opens: List[float], highs: List[float], 
                         lows: List[float], closes: List[float]) -> PatternResult:
        """Detect Engulfing pattern (2 candles)"""
        if len(opens) < 2:
            return None
        
        # Previous candle
        prev_open, prev_close = opens[-2], closes[-2]
        # Current candle
        curr_open, curr_close = opens[-1], closes[-1]
        
        prev_bullish = prev_close > prev_open
        curr_bullish = curr_close > curr_open
        
        # Bullish engulfing
        if not prev_bullish and curr_bullish:
            if curr_open < prev_close and curr_close > prev_open:
                confidence = min(0.9, abs(curr_close - curr_open) / abs(prev_close - prev_open))
                return PatternResult(
                    pattern_name="Bullish Engulfing",
                    confidence=confidence,
                    signal="bullish",
                    description="Bullish reversal pattern"
                )
        
        # Bearish engulfing
        if prev_bullish and not curr_bullish:
            if curr_open > prev_close and curr_close < prev_open:
                confidence = min(0.9, abs(curr_close - curr_open) / abs(prev_close - prev_open))
                return PatternResult(
                    pattern_name="Bearish Engulfing",
                    confidence=confidence,
                    signal="bearish",
                    description="Bearish reversal pattern"
                )
        
        return None
    
    @staticmethod
    def detect_chart_patterns(prices: List[float], period: int = 20) -> List[PatternResult]:
        """Detect chart patterns like support/resistance, trends"""
        if len(prices) < period:
            return []
        
        patterns = []
        
        # Support and resistance levels
        support_resistance = PatternDetection._detect_support_resistance(prices[-period:])
        if support_resistance:
            patterns.extend(support_resistance)
        
        # Trend detection
        trend = PatternDetection._detect_trend(prices[-period:])
        if trend:
            patterns.append(trend)
        
        return patterns
    
    @staticmethod
    def _detect_support_resistance(prices: List[float]) -> List[PatternResult]:
        """Detect support and resistance levels"""
        if len(prices) < 10:
            return []
        
        patterns = []
        current_price = prices[-1]
        
        # Find local minima (support) and maxima (resistance)
        minima = []
        maxima = []
        
        for i in range(2, len(prices) - 2):
            # Local minimum
            if (prices[i] < prices[i-1] and prices[i] < prices[i+1] and
                prices[i] < prices[i-2] and prices[i] < prices[i+2]):
                minima.append(prices[i])
            
            # Local maximum
            if (prices[i] > prices[i-1] and prices[i] > prices[i+1] and
                prices[i] > prices[i-2] and prices[i] > prices[i+2]):
                maxima.append(prices[i])
        
        # Check if current price is near support/resistance
        tolerance = np.std(prices) * 0.5
        
        for support in minima:
            if abs(current_price - support) < tolerance:
                confidence = 1.0 - (abs(current_price - support) / tolerance)
                patterns.append(PatternResult(
                    pattern_name="Support Level",
                    confidence=confidence,
                    signal="bullish",
                    description=f"Price near support level at {support:.2f}"
                ))
        
        for resistance in maxima:
            if abs(current_price - resistance) < tolerance:
                confidence = 1.0 - (abs(current_price - resistance) / tolerance)
                patterns.append(PatternResult(
                    pattern_name="Resistance Level",
                    confidence=confidence,
                    signal="bearish",
                    description=f"Price near resistance level at {resistance:.2f}"
                ))
        
        return patterns
    
    @staticmethod
    def _detect_trend(prices: List[float]) -> PatternResult:
        """Detect overall trend direction"""
        if len(prices) < 5:
            return None
        
        # Linear regression to find trend
        x = np.arange(len(prices))
        y = np.array(prices)
        
        slope, intercept = np.polyfit(x, y, 1)
        
        # Calculate R-squared for trend strength
        y_pred = slope * x + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Normalize slope by price level
        normalized_slope = slope / np.mean(prices) if np.mean(prices) > 0 else 0
        
        if abs(normalized_slope) > 0.01 and r_squared > 0.5:  # Significant trend
            if normalized_slope > 0:
                signal = "bullish"
                pattern_name = "Uptrend"
                description = "Strong upward trend detected"
            else:
                signal = "bearish"
                pattern_name = "Downtrend"
                description = "Strong downward trend detected"
            
            confidence = min(0.9, r_squared)
            
            return PatternResult(
                pattern_name=pattern_name,
                confidence=confidence,
                signal=signal,
                description=description
            )
        
        return None