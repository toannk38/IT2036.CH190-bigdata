from typing import Dict, Any

class DataValidator:
    @staticmethod
    def validate_price_data(data: Dict[str, Any]) -> bool:
        required_fields = ['symbol', 'time', 'open', 'high', 'low', 'close', 'volume']
        if not all(field in data for field in required_fields):
            return False
        
        if data['high'] < data['low']:
            return False
        
        if data['volume'] < 0:
            return False
        
        return True
