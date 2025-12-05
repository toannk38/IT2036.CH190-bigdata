import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
import os

# Add libs to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../libs'))

from ml.feature_engineering.technical_indicators import TechnicalIndicators
from ml.feature_engineering.volume_analysis import VolumeAnalysis

logger = logging.getLogger(__name__)

class FeatureCalculator:
    """Calculate technical features from price data"""
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
        self.volume_analyzer = VolumeAnalysis()
    
    def calculate_features(self, price_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate all technical features from price data"""
        if len(price_data) < 30:  # Need minimum data for calculations
            return self._empty_features()
        
        # Extract price arrays
        closes = [float(p['close']) for p in price_data]
        opens = [float(p['open']) for p in price_data]
        highs = [float(p['high']) for p in price_data]
        lows = [float(p['low']) for p in price_data]
        volumes = [float(p['volume']) for p in price_data]
        
        features = {}
        
        try:
            # Price-based indicators
            features['rsi'] = self.indicators.rsi(closes)[-1]
            features['rsi_14'] = self.indicators.rsi(closes, 14)[-1]
            features['rsi_7'] = self.indicators.rsi(closes, 7)[-1]
            
            # MACD
            macd_data = self.indicators.macd(closes)
            features['macd'] = macd_data['macd'][-1]
            features['macd_signal'] = macd_data['signal'][-1]
            features['macd_histogram'] = macd_data['histogram'][-1]
            
            # Bollinger Bands
            bb_data = self.indicators.bollinger_bands(closes)
            features['bb_upper'] = bb_data['upper'][-1]
            features['bb_middle'] = bb_data['middle'][-1]
            features['bb_lower'] = bb_data['lower'][-1]
            features['bb_position'] = (closes[-1] - bb_data['lower'][-1]) / (bb_data['upper'][-1] - bb_data['lower'][-1])
            
            # Moving Averages
            features['sma_5'] = self.indicators.sma(closes, 5)[-1]
            features['sma_10'] = self.indicators.sma(closes, 10)[-1]
            features['sma_20'] = self.indicators.sma(closes, 20)[-1]
            features['sma_50'] = self.indicators.sma(closes, 50)[-1] if len(closes) >= 50 else closes[-1]
            
            features['ema_5'] = self.indicators.ema(closes, 5)[-1]
            features['ema_10'] = self.indicators.ema(closes, 10)[-1]
            features['ema_20'] = self.indicators.ema(closes, 20)[-1]
            
            # Price position relative to MAs
            features['price_vs_sma20'] = closes[-1] / features['sma_20'] - 1
            features['price_vs_ema20'] = closes[-1] / features['ema_20'] - 1
            
            # Stochastic
            stoch_data = self.indicators.stochastic(highs, lows, closes)
            features['stoch_k'] = stoch_data['%K'][-1]
            features['stoch_d'] = stoch_data['%D'][-1]
            
            # ATR
            atr_values = self.indicators.atr(highs, lows, closes)
            features['atr'] = atr_values[-1]
            features['atr_ratio'] = atr_values[-1] / closes[-1] if closes[-1] > 0 else 0
            
            # Volume features
            features['volume_sma'] = self.volume_analyzer.volume_sma(volumes, 20)[-1]
            features['volume_ratio'] = self.volume_analyzer.volume_ratio(volumes, 20)[-1]
            
            obv_values = self.volume_analyzer.obv(closes, volumes)
            features['obv'] = obv_values[-1]
            
            vwap_values = self.volume_analyzer.vwap(highs, lows, closes, volumes)
            features['vwap'] = vwap_values[-1]
            features['price_vs_vwap'] = closes[-1] / vwap_values[-1] - 1
            
            vol_osc = self.volume_analyzer.volume_oscillator(volumes)
            features['volume_oscillator'] = vol_osc[-1]
            
            # Price momentum
            features['price_change_1d'] = (closes[-1] / closes[-2] - 1) if len(closes) >= 2 else 0
            features['price_change_5d'] = (closes[-1] / closes[-6] - 1) if len(closes) >= 6 else 0
            features['price_change_10d'] = (closes[-1] / closes[-11] - 1) if len(closes) >= 11 else 0
            
            # Volatility
            returns = [(closes[i] / closes[i-1] - 1) for i in range(1, len(closes))]
            features['volatility_10d'] = self._calculate_volatility(returns[-10:]) if len(returns) >= 10 else 0
            features['volatility_20d'] = self._calculate_volatility(returns[-20:]) if len(returns) >= 20 else 0
            
            # Trend strength
            features['trend_strength'] = self._calculate_trend_strength(closes[-20:]) if len(closes) >= 20 else 0
            
            logger.info(f"Calculated {len(features)} features for {len(price_data)} data points")
            
        except Exception as e:
            logger.error(f"Error calculating features: {e}")
            return self._empty_features()
        
        return features
    
    def _calculate_volatility(self, returns: List[float]) -> float:
        """Calculate volatility from returns"""
        if len(returns) < 2:
            return 0.0
        
        import numpy as np
        return float(np.std(returns) * np.sqrt(252))  # Annualized volatility
    
    def _calculate_trend_strength(self, prices: List[float]) -> float:
        """Calculate trend strength using linear regression slope"""
        if len(prices) < 5:
            return 0.0
        
        import numpy as np
        x = np.arange(len(prices))
        y = np.array(prices)
        
        # Linear regression
        slope, _ = np.polyfit(x, y, 1)
        
        # Normalize by price level
        return slope / np.mean(prices) if np.mean(prices) > 0 else 0.0
    
    def _empty_features(self) -> Dict[str, Any]:
        """Return empty features dict"""
        return {
            'rsi': 50.0,
            'rsi_14': 50.0,
            'rsi_7': 50.0,
            'macd': 0.0,
            'macd_signal': 0.0,
            'macd_histogram': 0.0,
            'bb_upper': 0.0,
            'bb_middle': 0.0,
            'bb_lower': 0.0,
            'bb_position': 0.5,
            'sma_5': 0.0,
            'sma_10': 0.0,
            'sma_20': 0.0,
            'sma_50': 0.0,
            'ema_5': 0.0,
            'ema_10': 0.0,
            'ema_20': 0.0,
            'price_vs_sma20': 0.0,
            'price_vs_ema20': 0.0,
            'stoch_k': 50.0,
            'stoch_d': 50.0,
            'atr': 0.0,
            'atr_ratio': 0.0,
            'volume_sma': 0.0,
            'volume_ratio': 1.0,
            'obv': 0.0,
            'vwap': 0.0,
            'price_vs_vwap': 0.0,
            'volume_oscillator': 0.0,
            'price_change_1d': 0.0,
            'price_change_5d': 0.0,
            'price_change_10d': 0.0,
            'volatility_10d': 0.0,
            'volatility_20d': 0.0,
            'trend_strength': 0.0
        }