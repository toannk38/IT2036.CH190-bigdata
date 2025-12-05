import os

# Monitoring Configuration
MONITORING_PORT = int(os.getenv('MONITORING_PORT', '8081'))

# Quality Thresholds
QUALITY_THRESHOLDS = {
    'min_quality_score': float(os.getenv('MIN_QUALITY_SCORE', '0.8')),
    'max_outlier_rate': float(os.getenv('MAX_OUTLIER_RATE', '0.05')),
    'max_invalid_rate': float(os.getenv('MAX_INVALID_RATE', '0.1'))
}

# Price Validation Thresholds
PRICE_THRESHOLDS = {
    'max_daily_change': float(os.getenv('MAX_DAILY_CHANGE', '0.15')),
    'min_volume': int(os.getenv('MIN_VOLUME', '1000')),
    'max_price': int(os.getenv('MAX_PRICE', '1000000')),
    'min_price': int(os.getenv('MIN_PRICE', '1000'))
}

# Outlier Detection Settings
OUTLIER_SETTINGS = {
    'z_score_threshold': float(os.getenv('Z_SCORE_THRESHOLD', '3.0')),
    'iqr_multiplier': float(os.getenv('IQR_MULTIPLIER', '1.5'))
}