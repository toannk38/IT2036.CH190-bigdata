import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import statistics
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    is_valid: bool
    score: float  # 0.0 to 1.0
    issues: List[str]
    warnings: List[str]

class DataQualityValidator:
    def __init__(self):
        self.price_thresholds = {
            'max_daily_change': 0.15,  # 15% max daily change
            'min_volume': 1000,
            'max_price': 1000000,  # VND
            'min_price': 1000      # VND
        }
    
    def validate_price_data(self, price_data: Dict[str, Any], 
                          historical_data: Optional[List[Dict]] = None) -> ValidationResult:
        """Validate price data quality"""
        issues = []
        warnings = []
        score = 1.0
        
        # Basic field validation
        if not self._validate_price_fields(price_data):
            issues.append("Missing required price fields")
            score -= 0.3
        
        # Price range validation
        if not self._validate_price_ranges(price_data):
            issues.append("Price values outside acceptable range")
            score -= 0.2
        
        # OHLC consistency
        if not self._validate_ohlc_consistency(price_data):
            issues.append("OHLC values inconsistent")
            score -= 0.2
        
        # Historical comparison
        if historical_data:
            change_valid, change_warning = self._validate_price_change(price_data, historical_data)
            if not change_valid:
                issues.append("Extreme price change detected")
                score -= 0.2
            if change_warning:
                warnings.append("Unusual price movement")
                score -= 0.1
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            score=max(0.0, score),
            issues=issues,
            warnings=warnings
        )
    
    def validate_news_data(self, news_data: Dict[str, Any]) -> ValidationResult:
        """Validate news data quality"""
        issues = []
        warnings = []
        score = 1.0
        
        # Content quality checks
        if not self._validate_news_content(news_data):
            issues.append("Poor news content quality")
            score -= 0.3
        
        # Duplicate detection
        if self._is_duplicate_news(news_data):
            warnings.append("Potential duplicate news")
            score -= 0.1
        
        # Language detection
        if not self._validate_language(news_data.get('content', '')):
            warnings.append("Non-Vietnamese content detected")
            score -= 0.05
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            score=max(0.0, score),
            issues=issues,
            warnings=warnings
        )
    
    def _validate_price_fields(self, data: Dict[str, Any]) -> bool:
        required_fields = ['symbol', 'time', 'open', 'high', 'low', 'close', 'volume']
        return all(field in data and data[field] is not None for field in required_fields)
    
    def _validate_price_ranges(self, data: Dict[str, Any]) -> bool:
        try:
            price_fields = ['open', 'high', 'low', 'close']
            for field in price_fields:
                price = float(data[field])
                if not (self.price_thresholds['min_price'] <= price <= self.price_thresholds['max_price']):
                    return False
            
            volume = int(data['volume'])
            return volume >= self.price_thresholds['min_volume']
        except (ValueError, KeyError):
            return False
    
    def _validate_ohlc_consistency(self, data: Dict[str, Any]) -> bool:
        try:
            open_price = float(data['open'])
            high = float(data['high'])
            low = float(data['low'])
            close = float(data['close'])
            
            # High should be >= max(open, close) and low should be <= min(open, close)
            return (high >= max(open_price, close) and 
                   low <= min(open_price, close) and
                   high >= low)
        except (ValueError, KeyError):
            return False
    
    def _validate_price_change(self, current: Dict[str, Any], 
                             historical: List[Dict]) -> tuple[bool, bool]:
        if not historical:
            return True, False
        
        try:
            current_close = float(current['close'])
            last_close = float(historical[-1]['close'])
            
            change_pct = abs(current_close - last_close) / last_close
            
            # Extreme change (invalid)
            if change_pct > self.price_thresholds['max_daily_change']:
                return False, False
            
            # Unusual change (warning)
            if change_pct > self.price_thresholds['max_daily_change'] * 0.7:
                return True, True
            
            return True, False
        except (ValueError, KeyError, ZeroDivisionError):
            return False, False
    
    def _validate_news_content(self, data: Dict[str, Any]) -> bool:
        content = data.get('content', '')
        title = data.get('title', '')
        
        # Minimum content length
        if len(content) < 50 or len(title) < 10:
            return False
        
        # Check for spam patterns
        spam_indicators = ['click here', 'buy now', '!!!', 'URGENT']
        content_lower = content.lower()
        if any(indicator in content_lower for indicator in spam_indicators):
            return False
        
        return True
    
    def _is_duplicate_news(self, data: Dict[str, Any]) -> bool:
        # Simple duplicate detection based on title similarity
        # In production, this would check against existing news in database
        return False
    
    def _validate_language(self, text: str) -> bool:
        # Simple Vietnamese text detection
        vietnamese_chars = 'àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ'
        return any(char in text.lower() for char in vietnamese_chars)