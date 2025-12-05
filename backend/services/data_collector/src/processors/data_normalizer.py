from typing import Dict, Any
from datetime import datetime

class DataNormalizer:
    @staticmethod
    def normalize_price_data(price_data) -> Dict[str, Any]:
        return {
            'symbol': price_data.symbol,
            'time': price_data.time.isoformat() if isinstance(price_data.time, datetime) else price_data.time,
            'open': float(price_data.open),
            'high': float(price_data.high),
            'low': float(price_data.low),
            'close': float(price_data.close),
            'volume': int(price_data.volume),
            'collected_at': datetime.utcnow().isoformat()
        }
