import numpy as np
from typing import List, Dict, Any

class VolumeAnalysis:
    """Volume-based technical analysis features"""
    
    @staticmethod
    def volume_sma(volumes: List[float], period: int = 20) -> List[float]:
        """Volume Simple Moving Average"""
        if len(volumes) < period:
            return volumes[:]
        
        sma_values = []
        for i in range(len(volumes)):
            if i < period - 1:
                sma_values.append(volumes[i])
            else:
                window_avg = np.mean(volumes[i - period + 1:i + 1])
                sma_values.append(window_avg)
        
        return sma_values
    
    @staticmethod
    def volume_ratio(volumes: List[float], period: int = 20) -> List[float]:
        """Current volume vs average volume ratio"""
        vol_sma = VolumeAnalysis.volume_sma(volumes, period)
        
        ratios = []
        for i, (current_vol, avg_vol) in enumerate(zip(volumes, vol_sma)):
            if avg_vol > 0:
                ratios.append(current_vol / avg_vol)
            else:
                ratios.append(1.0)
        
        return ratios
    
    @staticmethod
    def obv(closes: List[float], volumes: List[float]) -> List[float]:
        """On-Balance Volume"""
        if len(closes) != len(volumes) or len(closes) < 2:
            return [0.0] * len(closes)
        
        obv_values = [0.0]
        
        for i in range(1, len(closes)):
            if closes[i] > closes[i-1]:
                obv_values.append(obv_values[-1] + volumes[i])
            elif closes[i] < closes[i-1]:
                obv_values.append(obv_values[-1] - volumes[i])
            else:
                obv_values.append(obv_values[-1])
        
        return obv_values
    
    @staticmethod
    def vwap(highs: List[float], lows: List[float], closes: List[float], 
             volumes: List[float]) -> List[float]:
        """Volume Weighted Average Price"""
        if not all(len(lst) == len(closes) for lst in [highs, lows, volumes]):
            return closes[:]
        
        vwap_values = []
        cumulative_volume = 0
        cumulative_pv = 0
        
        for i in range(len(closes)):
            typical_price = (highs[i] + lows[i] + closes[i]) / 3
            pv = typical_price * volumes[i]
            
            cumulative_pv += pv
            cumulative_volume += volumes[i]
            
            if cumulative_volume > 0:
                vwap_values.append(cumulative_pv / cumulative_volume)
            else:
                vwap_values.append(typical_price)
        
        return vwap_values
    
    @staticmethod
    def volume_oscillator(volumes: List[float], short_period: int = 5, 
                         long_period: int = 10) -> List[float]:
        """Volume Oscillator"""
        short_ma = VolumeAnalysis.volume_sma(volumes, short_period)
        long_ma = VolumeAnalysis.volume_sma(volumes, long_period)
        
        oscillator = []
        for short_val, long_val in zip(short_ma, long_ma):
            if long_val > 0:
                osc = ((short_val - long_val) / long_val) * 100
                oscillator.append(osc)
            else:
                oscillator.append(0.0)
        
        return oscillator
    
    @staticmethod
    def volume_spike_detection(volumes: List[float], threshold: float = 2.0, 
                              period: int = 20) -> List[bool]:
        """Detect volume spikes"""
        vol_sma = VolumeAnalysis.volume_sma(volumes, period)
        
        spikes = []
        for current_vol, avg_vol in zip(volumes, vol_sma):
            if avg_vol > 0:
                spike = current_vol > (avg_vol * threshold)
                spikes.append(spike)
            else:
                spikes.append(False)
        
        return spikes