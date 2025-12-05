# Experiments Documentation

## Overview

The experiments component provides research environment with Jupyter notebooks, prototyping capabilities, and research tools for exploring new models, features, and trading strategies.

## Structure

### 1. Notebooks
**Location**: `ml-training/experiments/notebooks/`

Interactive Jupyter notebooks for data exploration, model development, and research analysis.

#### Data Exploration Notebook
**File**: `data_exploration.ipynb`

```python
# Key sections in the notebook:

# 1. Data Loading and Overview
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load stock data
data = load_stock_data(['VCB', 'VIC', 'VHM'], start_date='2020-01-01')

# Basic statistics
data.describe()
data.info()

# 2. Price Analysis
# Price trends over time
plt.figure(figsize=(15, 8))
for symbol in data['symbol'].unique():
    symbol_data = data[data['symbol'] == symbol]
    plt.plot(symbol_data['time'], symbol_data['close'], label=symbol)
plt.legend()
plt.title('Stock Price Trends')

# 3. Volume Analysis
# Volume patterns
data.groupby('symbol')['volume'].describe()

# Volume vs Price correlation
correlation_matrix = data[['close', 'volume', 'high', 'low']].corr()
sns.heatmap(correlation_matrix, annot=True)

# 4. Return Analysis
# Calculate returns
data['returns'] = data.groupby('symbol')['close'].pct_change()

# Return distribution
plt.figure(figsize=(12, 6))
data['returns'].hist(bins=50, alpha=0.7)
plt.title('Return Distribution')

# 5. Volatility Analysis
# Rolling volatility
data['volatility'] = data.groupby('symbol')['returns'].rolling(20).std()

# Volatility clustering
plt.figure(figsize=(15, 6))
plt.plot(data['time'], data['volatility'])
plt.title('Volatility Over Time')
```

#### Feature Analysis Notebook
**File**: `feature_analysis.ipynb`

```python
# Feature engineering and analysis

# 1. Technical Indicators
from ta import add_all_ta_features

# Add all technical indicators
data_with_features = add_all_ta_features(
    data, open="open", high="high", low="low", close="close", volume="volume"
)

# 2. Feature Correlation Analysis
# Calculate correlation matrix
feature_columns = [col for col in data_with_features.columns if col.startswith('ta_')]
correlation_matrix = data_with_features[feature_columns].corr()

# Plot correlation heatmap
plt.figure(figsize=(20, 16))
sns.heatmap(correlation_matrix, annot=False, cmap='coolwarm', center=0)
plt.title('Technical Indicators Correlation Matrix')

# 3. Feature Importance Analysis
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import SelectKBest, f_regression

# Prepare target variable (next day return)
data_with_features['target'] = data_with_features.groupby('symbol')['returns'].shift(-1)

# Feature importance using Random Forest
rf = RandomForestRegressor(n_estimators=100, random_state=42)
X = data_with_features[feature_columns].fillna(0)
y = data_with_features['target'].fillna(0)

rf.fit(X, y)
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': rf.feature_importances_
}).sort_values('importance', ascending=False)

# Plot top 20 features
plt.figure(figsize=(12, 8))
sns.barplot(data=feature_importance.head(20), x='importance', y='feature')
plt.title('Top 20 Most Important Features')

# 4. Statistical Tests
from scipy.stats import pearsonr, spearmanr

# Test feature-target relationships
statistical_tests = []
for feature in feature_columns:
    if data_with_features[feature].notna().sum() > 100:
        pearson_corr, pearson_p = pearsonr(
            data_with_features[feature].fillna(0), 
            data_with_features['target'].fillna(0)
        )
        statistical_tests.append({
            'feature': feature,
            'pearson_correlation': pearson_corr,
            'p_value': pearson_p,
            'significant': pearson_p < 0.05
        })

statistical_df = pd.DataFrame(statistical_tests)
significant_features = statistical_df[statistical_df['significant']].sort_values(
    'pearson_correlation', key=abs, ascending=False
)
```

#### Model Comparison Notebook
**File**: `model_comparison.ipynb`

```python
# Compare different model architectures

# 1. Model Setup
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
import tensorflow as tf

models = {
    'Linear Regression': LinearRegression(),
    'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
    'XGBoost': XGBRegressor(n_estimators=100, random_state=42),
}

# 2. Data Preparation
# Split data
train_size = int(0.8 * len(data_with_features))
train_data = data_with_features[:train_size]
test_data = data_with_features[train_size:]

X_train = train_data[selected_features].fillna(0)
y_train = train_data['target'].fillna(0)
X_test = test_data[selected_features].fillna(0)
y_test = test_data['target'].fillna(0)

# 3. Model Training and Evaluation
results = {}

for model_name, model in models.items():
    # Train model
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    results[model_name] = {
        'MSE': mse,
        'RMSE': np.sqrt(mse),
        'R²': r2,
        'predictions': y_pred
    }

# 4. Results Visualization
results_df = pd.DataFrame(results).T
print(results_df)

# Plot predictions vs actual
fig, axes = plt.subplots(2, 2, figsize=(15, 12))
axes = axes.ravel()

for i, (model_name, result) in enumerate(results.items()):
    ax = axes[i]
    ax.scatter(y_test, result['predictions'], alpha=0.5)
    ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    ax.set_xlabel('Actual Returns')
    ax.set_ylabel('Predicted Returns')
    ax.set_title(f'{model_name} (R² = {result["R²"]:.3f})')

plt.tight_layout()
```

### 2. Research
**Location**: `ml-training/experiments/research/`

Advanced research modules for specialized analysis and new technique development.

#### Market Regime Detection
**File**: `market_regime_detection.py`

```python
class MarketRegimeDetector:
    def __init__(self):
        self.regimes = ['Bull', 'Bear', 'Sideways', 'High Volatility']
    
    def detect_regimes_hmm(self, returns):
        """Hidden Markov Model for regime detection"""
        from hmmlearn import hmm
        
        # Prepare features
        features = np.column_stack([
            returns,
            np.abs(returns),  # Volatility proxy
            returns.rolling(20).mean(),  # Trend
            returns.rolling(20).std()   # Volatility
        ])
        
        # Fit HMM
        model = hmm.GaussianHMM(n_components=4, covariance_type="full")
        model.fit(features)
        
        # Predict regimes
        regimes = model.predict(features)
        
        return regimes, model
    
    def detect_regimes_threshold(self, returns, volatility_threshold=0.02):
        """Threshold-based regime detection"""
        rolling_return = returns.rolling(20).mean()
        rolling_volatility = returns.rolling(20).std()
        
        regimes = []
        for ret, vol in zip(rolling_return, rolling_volatility):
            if vol > volatility_threshold:
                regime = 'High Volatility'
            elif ret > 0.001:  # 0.1% daily return threshold
                regime = 'Bull'
            elif ret < -0.001:
                regime = 'Bear'
            else:
                regime = 'Sideways'
            regimes.append(regime)
        
        return regimes
    
    def analyze_regime_performance(self, returns, regimes):
        """Analyze model performance by regime"""
        regime_stats = {}
        
        for regime in self.regimes:
            regime_mask = np.array(regimes) == regime
            if regime_mask.sum() > 0:
                regime_returns = returns[regime_mask]
                regime_stats[regime] = {
                    'count': regime_mask.sum(),
                    'mean_return': regime_returns.mean(),
                    'volatility': regime_returns.std(),
                    'sharpe': regime_returns.mean() / regime_returns.std() if regime_returns.std() > 0 else 0
                }
        
        return regime_stats
```

#### Volatility Modeling
**File**: `volatility_modeling.py`

```python
class VolatilityModeler:
    def __init__(self):
        self.models = {}
    
    def fit_garch(self, returns):
        """Fit GARCH model for volatility forecasting"""
        from arch import arch_model
        
        # Fit GARCH(1,1) model
        model = arch_model(returns * 100, vol='Garch', p=1, q=1)
        fitted_model = model.fit(disp='off')
        
        self.models['garch'] = fitted_model
        return fitted_model
    
    def fit_egarch(self, returns):
        """Fit EGARCH model (asymmetric volatility)"""
        from arch import arch_model
        
        model = arch_model(returns * 100, vol='EGARCH', p=1, o=1, q=1)
        fitted_model = model.fit(disp='off')
        
        self.models['egarch'] = fitted_model
        return fitted_model
    
    def forecast_volatility(self, model_name, horizon=5):
        """Forecast volatility using fitted model"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not fitted")
        
        model = self.models[model_name]
        forecast = model.forecast(horizon=horizon)
        
        return forecast.variance.iloc[-1] / 10000  # Convert back to decimal
    
    def compare_volatility_models(self, returns):
        """Compare different volatility models"""
        models = ['garch', 'egarch']
        results = {}
        
        for model_name in models:
            if model_name == 'garch':
                fitted_model = self.fit_garch(returns)
            elif model_name == 'egarch':
                fitted_model = self.fit_egarch(returns)
            
            results[model_name] = {
                'aic': fitted_model.aic,
                'bic': fitted_model.bic,
                'log_likelihood': fitted_model.loglikelihood
            }
        
        return results
```

### 3. Prototypes
**Location**: `ml-training/experiments/prototypes/`

Experimental implementations of new indicators, models, and ensemble methods.

#### New Indicators
**File**: `new_indicators.py`

```python
class ExperimentalIndicators:
    @staticmethod
    def adaptive_rsi(prices, window=14, alpha=0.1):
        """Adaptive RSI that adjusts to market volatility"""
        returns = prices.pct_change()
        volatility = returns.rolling(window).std()
        
        # Adjust window based on volatility
        adaptive_window = window * (1 + alpha * volatility / volatility.mean())
        adaptive_window = adaptive_window.fillna(window).astype(int)
        
        rsi_values = []
        for i, w in enumerate(adaptive_window):
            if i >= w:
                price_slice = prices.iloc[i-w:i+1]
                delta = price_slice.diff()
                gain = delta.where(delta > 0, 0).mean()
                loss = -delta.where(delta < 0, 0).mean()
                rs = gain / loss if loss != 0 else 0
                rsi = 100 - (100 / (1 + rs))
                rsi_values.append(rsi)
            else:
                rsi_values.append(np.nan)
        
        return pd.Series(rsi_values, index=prices.index)
    
    @staticmethod
    def fractal_dimension(prices, window=20):
        """Calculate fractal dimension for trend strength"""
        def hurst_exponent(ts):
            """Calculate Hurst exponent"""
            lags = range(2, min(len(ts)//2, 20))
            tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
            poly = np.polyfit(np.log(lags), np.log(tau), 1)
            return poly[0] * 2.0
        
        fractal_dims = []
        for i in range(len(prices)):
            if i >= window:
                price_window = prices.iloc[i-window:i]
                hurst = hurst_exponent(price_window.values)
                fractal_dim = 2 - hurst
                fractal_dims.append(fractal_dim)
            else:
                fractal_dims.append(np.nan)
        
        return pd.Series(fractal_dims, index=prices.index)
    
    @staticmethod
    def market_microstructure_indicator(prices, volumes, window=20):
        """Indicator based on market microstructure theory"""
        # Price impact measure
        returns = prices.pct_change()
        volume_impact = returns / np.log(volumes + 1)
        
        # Rolling correlation between returns and volume
        rolling_corr = returns.rolling(window).corr(volumes.rolling(window).mean())
        
        # Combine measures
        microstructure_score = (volume_impact.rolling(window).mean() + 
                              rolling_corr) / 2
        
        return microstructure_score
```

#### Alternative Models
**File**: `alternative_models.py`

```python
class AlternativeModels:
    def __init__(self):
        self.models = {}
    
    def wavelet_lstm(self, data, wavelet='db4', levels=3):
        """LSTM with wavelet decomposition preprocessing"""
        import pywt
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import LSTM, Dense, Dropout
        
        # Wavelet decomposition
        coeffs = pywt.wavedec(data, wavelet, level=levels)
        
        # Reconstruct approximation and details
        approx = pywt.waverec([coeffs[0]] + [None]*levels, wavelet)
        details = []
        for i in range(1, levels+1):
            detail_coeffs = [None]*(levels+1)
            detail_coeffs[i] = coeffs[i]
            detail = pywt.waverec(detail_coeffs, wavelet)
            details.append(detail)
        
        # Combine components
        combined_features = np.column_stack([approx[:len(data)]] + 
                                          [d[:len(data)] for d in details])
        
        # Build LSTM model
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(combined_features.shape[1], 1)),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mse')
        return model, combined_features
    
    def attention_transformer(self, sequence_length=60, d_model=64):
        """Transformer model with attention mechanism"""
        import tensorflow as tf
        from tensorflow.keras.layers import MultiHeadAttention, LayerNormalization
        
        class TransformerBlock(tf.keras.layers.Layer):
            def __init__(self, d_model, num_heads, dff, rate=0.1):
                super(TransformerBlock, self).__init__()
                self.att = MultiHeadAttention(num_heads=num_heads, key_dim=d_model)
                self.ffn = tf.keras.Sequential([
                    Dense(dff, activation='relu'),
                    Dense(d_model)
                ])
                self.layernorm1 = LayerNormalization(epsilon=1e-6)
                self.layernorm2 = LayerNormalization(epsilon=1e-6)
                self.dropout1 = Dropout(rate)
                self.dropout2 = Dropout(rate)
            
            def call(self, x, training):
                attn_output = self.att(x, x)
                attn_output = self.dropout1(attn_output, training=training)
                out1 = self.layernorm1(x + attn_output)
                
                ffn_output = self.ffn(out1)
                ffn_output = self.dropout2(ffn_output, training=training)
                return self.layernorm2(out1 + ffn_output)
        
        # Build model
        inputs = Input(shape=(sequence_length, d_model))
        x = TransformerBlock(d_model, num_heads=4, dff=128)(inputs)
        x = GlobalAveragePooling1D()(x)
        outputs = Dense(1)(x)
        
        model = Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        
        return model
    
    def quantum_inspired_model(self, n_qubits=4):
        """Quantum-inspired neural network"""
        # Simplified quantum-inspired approach using rotation gates
        class QuantumLayer(tf.keras.layers.Layer):
            def __init__(self, n_qubits):
                super(QuantumLayer, self).__init__()
                self.n_qubits = n_qubits
                self.theta = self.add_weight(
                    shape=(n_qubits,), 
                    initializer='random_normal',
                    trainable=True
                )
            
            def call(self, inputs):
                # Simulate quantum rotation gates
                rotated = tf.cos(self.theta) * inputs + tf.sin(self.theta) * tf.roll(inputs, 1, axis=-1)
                return rotated
        
        model = Sequential([
            Dense(n_qubits, activation='tanh'),
            QuantumLayer(n_qubits),
            Dense(n_qubits//2, activation='relu'),
            Dense(1)
        ])
        
        return model
```

## Configuration

### Experiment Configuration
**Location**: `ml-training/experiments/config/experiment_config.yml`

```yaml
experiments:
  notebooks:
    jupyter_port: 8888
    kernel: python3
    extensions: ['plotly', 'seaborn', 'ta-lib']
  
  research:
    data_sources: ['mongodb', 'csv', 'api']
    cache_results: true
    parallel_processing: true
    
  prototypes:
    auto_save: true
    version_control: true
    testing_framework: 'pytest'
    
  visualization:
    backend: 'plotly'
    interactive: true
    save_format: ['png', 'html']
```

## Usage Guidelines

### Setting Up Experiments
```bash
# Start Jupyter notebook server
cd ml-training/experiments/notebooks
jupyter notebook --port=8888 --no-browser

# Run research scripts
cd ml-training/experiments/research
python market_regime_detection.py

# Test prototypes
cd ml-training/experiments/prototypes
pytest test_new_indicators.py
```

### Best Practices
1. **Version Control**: Use git for tracking experiment changes
2. **Documentation**: Document all experiments and findings
3. **Reproducibility**: Set random seeds and save configurations
4. **Validation**: Always validate new approaches on out-of-sample data
5. **Collaboration**: Share notebooks and findings with team members