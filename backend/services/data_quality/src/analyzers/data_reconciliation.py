import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ReconciliationResult:
    symbol: str
    expected_count: int
    actual_count: int
    missing_count: int
    duplicate_count: int
    data_gaps: List[str]
    quality_score: float

class DataReconciliation:
    def __init__(self):
        self.expected_trading_hours = {
            'start': '09:00',
            'end': '15:00'
        }
    
    def reconcile_price_data(self, symbol: str, date: datetime, 
                           collected_data: List[Dict[str, Any]]) -> ReconciliationResult:
        """Reconcile price data for completeness"""
        
        # Expected data points (assuming 1-minute intervals during trading hours)
        expected_count = self._calculate_expected_data_points(date)
        actual_count = len(collected_data)
        
        # Find duplicates
        timestamps = [data['time'] for data in collected_data]
        duplicate_count = len(timestamps) - len(set(timestamps))
        
        # Find gaps
        data_gaps = self._find_data_gaps(collected_data, date)
        
        # Calculate missing count
        missing_count = max(0, expected_count - actual_count + duplicate_count)
        
        # Quality score based on completeness
        completeness_ratio = actual_count / expected_count if expected_count > 0 else 0
        gap_penalty = len(data_gaps) * 0.1
        duplicate_penalty = duplicate_count * 0.05
        
        quality_score = max(0.0, completeness_ratio - gap_penalty - duplicate_penalty)
        
        return ReconciliationResult(
            symbol=symbol,
            expected_count=expected_count,
            actual_count=actual_count,
            missing_count=missing_count,
            duplicate_count=duplicate_count,
            data_gaps=data_gaps,
            quality_score=min(1.0, quality_score)
        )
    
    def reconcile_news_data(self, symbol: str, date: datetime,
                          collected_news: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Reconcile news data for duplicates and quality"""
        
        # Check for duplicates by title similarity
        duplicates = self._find_duplicate_news(collected_news)
        
        # Check for content quality
        low_quality_count = sum(1 for news in collected_news 
                               if len(news.get('content', '')) < 100)
        
        # Calculate quality metrics
        total_count = len(collected_news)
        duplicate_rate = len(duplicates) / total_count if total_count > 0 else 0
        low_quality_rate = low_quality_count / total_count if total_count > 0 else 0
        
        quality_score = 1.0 - (duplicate_rate * 0.5) - (low_quality_rate * 0.3)
        
        return {
            'symbol': symbol,
            'date': date.isoformat(),
            'total_news': total_count,
            'duplicates': len(duplicates),
            'low_quality': low_quality_count,
            'duplicate_rate': duplicate_rate,
            'low_quality_rate': low_quality_rate,
            'quality_score': max(0.0, quality_score)
        }
    
    def _calculate_expected_data_points(self, date: datetime) -> int:
        """Calculate expected number of data points for a trading day"""
        # Skip weekends
        if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return 0
        
        # Trading hours: 9:00 - 15:00 (6 hours = 360 minutes)
        # Assuming 1-minute intervals
        return 360
    
    def _find_data_gaps(self, data: List[Dict[str, Any]], date: datetime) -> List[str]:
        """Find gaps in time series data"""
        if not data:
            return ['No data available']
        
        gaps = []
        sorted_data = sorted(data, key=lambda x: x['time'])
        
        # Check for gaps larger than 5 minutes
        for i in range(1, len(sorted_data)):
            prev_time = datetime.fromisoformat(sorted_data[i-1]['time'].replace('Z', '+00:00'))
            curr_time = datetime.fromisoformat(sorted_data[i]['time'].replace('Z', '+00:00'))
            
            gap_duration = (curr_time - prev_time).total_seconds() / 60  # minutes
            
            if gap_duration > 5:  # Gap larger than 5 minutes
                gaps.append(f"Gap from {prev_time.strftime('%H:%M')} to {curr_time.strftime('%H:%M')} ({gap_duration:.1f} min)")
        
        return gaps
    
    def _find_duplicate_news(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find duplicate news based on title similarity"""
        duplicates = []
        seen_titles = set()
        
        for news in news_list:
            title = news.get('title', '').lower().strip()
            
            # Simple duplicate detection - exact title match
            if title in seen_titles:
                duplicates.append(news)
            else:
                seen_titles.add(title)
        
        return duplicates