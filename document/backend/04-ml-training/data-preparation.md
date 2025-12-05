# Data Preparation Documentation

## Overview

Data preparation is the foundation of the ML pipeline, handling feature engineering, data cleaning, and preprocessing for all model types.

## Components

### 1. Feature Engineering
**Location**: `ml-training/data-preparation/feature_engineering.py`

```python
class FeatureEngineer:
    def __init__(self):
        self.technical_indicators = TechnicalIndicators()
        self.pattern_detector = PatternDetector()
    
    def engineer_features(self, price_data):
        features = {}
        
        # Price-based features
        features.update(self._price_features(price_data))
        
        # Technical indicators
        features.update(self.technical_indicators.calculate_all(price_data))
        
        # Pattern features
        features.update(self.pattern_detector.detect_patterns(price_data))
        
        return features
```

**Generated Features**:
- **Price Features**: Returns, volatility, price ratios
- **Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages
- **Volume Features**: Volume indicators, OBV, VPT
- **Pattern Features**: Candlestick patterns, support/resistance

### 2. Data Cleaning
**Location**: `ml-training/data-preparation/data_cleaning.py`

```python
class DataCleaner:
    def clean_price_data(self, raw_data):
        # Remove duplicates
        data = self._remove_duplicates(raw_data)
        
        # Handle missing values
        data = self._handle_missing_values(data)
        
        # Remove outliers
        data = self._remove_outliers(data)
        
        # Validate data integrity
        data = self._validate_data(data)
        
        return data
```

**Cleaning Steps**:
- **Duplicate Removal**: Remove duplicate timestamps
- **Missing Value Handling**: Forward fill, interpolation
- **Outlier Detection**: Statistical and business rule-based
- **Data Validation**: Price consistency, volume validation

### 3. Data Loader
**Location**: `ml-training/data-preparation/data_loader.py`

```python
class DataLoader:
    def __init__(self, mongodb_uri, database_name):
        self.client = MongoClient(mongodb_uri)
        self.db = self.client[database_name]
    
    def load_price_data(self, symbol, start_date, end_date):
        collection = self.db.stock_prices
        query = {
            'symbol': symbol,
            'time': {'$gte': start_date, '$lte': end_date}
        }
        return list(collection.find(query).sort('time', 1))
```

### 4. Feature Selection
**Location**: `ml-training/data-preparation/feature_selection.py`

```python
class FeatureSelector:
    def select_features(self, features, target, method='importance'):
        if method == 'importance':
            return self._importance_based_selection(features, target)
        elif method == 'correlation':
            return self._correlation_based_selection(features, target)
        elif method == 'recursive':
            return self._recursive_feature_elimination(features, target)
```

### 5. Data Splitter
**Location**: `ml-training/data-preparation/data_splitter.py`

```python
class DataSplitter:
    def time_series_split(self, data, train_ratio=0.7, val_ratio=0.2):
        n = len(data)
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))
        
        train_data = data[:train_end]
        val_data = data[train_end:val_end]
        test_data = data[val_end:]
        
        return train_data, val_data, test_data
```

## Configuration

### Feature Configuration
**Location**: `ml-training/data-preparation/config/feature_config.yml`

```yaml
technical_indicators:
  rsi:
    periods: [14, 30]
  macd:
    fast: 12
    slow: 26
    signal: 9
  bollinger_bands:
    period: 20
    std: 2
  moving_averages:
    periods: [5, 10, 20, 50, 200]

volume_indicators:
  obv: true
  vpt: true
  volume_sma: [10, 20]

pattern_detection:
  candlestick_patterns: true
  support_resistance: true
  trend_lines: true

data_cleaning:
  outlier_threshold: 3.0
  missing_value_method: 'forward_fill'
  min_data_points: 100
```

## Data Models

### Feature Schema
```python
@dataclass
class FeatureSet:
    symbol: str
    timestamp: datetime
    
    # Price features
    returns_1d: float
    returns_5d: float
    returns_20d: float
    volatility_20d: float
    high_low_ratio: float
    
    # Technical indicators
    rsi_14: float
    macd: float
    macd_signal: float
    bb_upper: float
    bb_lower: float
    sma_20: float
    
    # Volume features
    volume_sma_10: float
    obv: float
    vpt: float
    
    # Pattern features
    is_doji: bool
    is_hammer: bool
    support_level: Optional[float]
    resistance_level: Optional[float]
    
    # Target
    target_return: Optional[float]
```

## Processing Pipeline

### Daily Feature Generation
```python
def daily_feature_pipeline():
    # 1. Load raw data
    loader = DataLoader(MONGODB_URI, DATABASE_NAME)
    raw_data = loader.load_recent_data(days=1000)
    
    # 2. Clean data
    cleaner = DataCleaner()
    clean_data = cleaner.clean_price_data(raw_data)
    
    # 3. Engineer features
    engineer = FeatureEngineer()
    features = engineer.engineer_features(clean_data)
    
    # 4. Select features
    selector = FeatureSelector()
    selected_features = selector.select_features(features)
    
    # 5. Save to feature store
    save_features(selected_features)
    
    return selected_features
```

## Quality Checks

### Data Quality Metrics
- **Completeness**: Percentage of non-null values
- **Consistency**: Data format and range validation
- **Accuracy**: Business rule validation
- **Timeliness**: Data freshness checks

### Feature Quality Metrics
- **Feature Importance**: Statistical significance
- **Feature Stability**: Consistency over time
- **Feature Correlation**: Multicollinearity detection
- **Feature Distribution**: Statistical properties