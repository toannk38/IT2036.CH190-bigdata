import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional

class TechnicalIndicators:
    """Technical analysis indicators for stock price data"""
    
    @staticmethod
    def rsi(prices: List[float], period: int = 14) -> List[float]:
        """Relative Strength Index"""
        if len(prices) < period + 1:
            return [50.0] * len(prices)
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        rsi_values = [50.0] * period
        
        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            if avg_loss == 0:
                rsi_values.append(100.0)
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                rsi_values.append(rsi)
        
        return rsi_values
    
    @staticmethod
    def macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, List[float]]:
        """MACD (Moving Average Convergence Divergence)"""
        if len(prices) < slow:
            return {'macd': [0.0] * len(prices), 'signal': [0.0] * len(prices), 'histogram': [0.0] * len(prices)}
        
        # Calculate EMAs
        ema_fast = TechnicalIndicators._ema(prices, fast)
        ema_slow = TechnicalIndicators._ema(prices, slow)
        
        # MACD line
        macd_line = [fast_val - slow_val for fast_val, slow_val in zip(ema_fast, ema_slow)]
        
        # Signal line
        signal_line = TechnicalIndicators._ema(macd_line, signal)
        
        # Histogram
        histogram = [macd_val - signal_val for macd_val, signal_val in zip(macd_line, signal_line)]
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Dict[str, List[float]]:
        """Bollinger Bands"""
        if len(prices) < period:
            return {'upper': prices[:], 'middle': prices[:], 'lower': prices[:]}
        
        middle = TechnicalIndicators.sma(prices, period)
        
        upper = []
        lower = []
        
        for i in range(len(prices)):
            if i < period - 1:
                upper.append(prices[i])
                lower.append(prices[i])
            else:
                window = prices[i - period + 1:i + 1]
                std = np.std(window)
                upper.append(middle[i] + (std_dev * std))
                lower.append(middle[i] - (std_dev * std))
        
        return {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }
    
    @staticmethod
    def sma(prices: List[float], period: int) -> List[float]:
        """Simple Moving Average"""
        if len(prices) < period:
            return prices[:]
        
        sma_values = []
        for i in range(len(prices)):
            if i < period - 1:
                sma_values.append(prices[i])
            else:
                window_avg = np.mean(prices[i - period + 1:i + 1])
                sma_values.append(window_avg)
        
        return sma_values
    
    @staticmethod
    def ema(prices: List[float], period: int) -> List[float]:
        """Exponential Moving Average"""
        return TechnicalIndicators._ema(prices, period)
    
    @staticmethod
    def _ema(prices: List[float], period: int) -> List[float]:
        """Internal EMA calculation"""
        if len(prices) < period:
            return prices[:]
        
        multiplier = 2 / (period + 1)
        ema_values = [prices[0]]
        
        for i in range(1, len(prices)):
            ema = (prices[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
            ema_values.append(ema)
        
        return ema_values
    
    @staticmethod
    def stochastic(highs: List[float], lows: List[float], closes: List[float], 
                   k_period: int = 14, d_period: int = 3) -> Dict[str, List[float]]:
        """Stochastic Oscillator"""
        if len(closes) < k_period:
            return {'%K': [50.0] * len(closes), '%D': [50.0] * len(closes)}
        
        k_values = []
        
        for i in range(len(closes)):
            if i < k_period - 1:
                k_values.append(50.0)
            else:
                window_high = max(highs[i - k_period + 1:i + 1])
                window_low = min(lows[i - k_period + 1:i + 1])
                
                if window_high == window_low:
                    k_values.append(50.0)
                else:
                    k = ((closes[i] - window_low) / (window_high - window_low)) * 100
                    k_values.append(k)
        
        # %D is SMA of %K
        d_values = TechnicalIndicators.sma(k_values, d_period)
        
        return {'%K': k_values, '%D': d_values}
    
    @staticmethod
    def atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> List[float]:
        """Average True Range"""
        if len(closes) < 2:
            return [0.0] * len(closes)
        
        true_ranges = []
        
        for i in range(1, len(closes)):
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i-1])
            tr3 = abs(lows[i] - closes[i-1])
            true_ranges.append(max(tr1, tr2, tr3))
        
        # Prepend first value
        true_ranges.insert(0, highs[0] - lows[0])
        
        # Calculate ATR using EMA
        return TechnicalIndicators._ema(true_ranges, period)