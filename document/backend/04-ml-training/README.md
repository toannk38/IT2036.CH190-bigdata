# ML Training Documentation

## Overview

The ML Training layer handles the complete machine learning pipeline from data preparation to model deployment. It supports multiple model types including ARIMA, LSTM, Transformers, and CatBoost for stock price prediction and technical analysis.

**Status**: 🔄 **PLANNED**

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MongoDB       │───►│ Data Preparation │───►│ Feature Store   │
│ (Raw Price Data)│    │   & Engineering  │    │   (Features)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Experiments   │◄───│ Model Training   │◄───│ Model Registry  │
│  (Notebooks)    │    │   & Tuning       │    │  (Artifacts)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Research      │    │ Model Evaluation │    │   Production    │
│   & Analysis    │    │  & Backtesting   │    │   Deployment    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Directory Structure

```
ml-training/
├── data-preparation/           # Feature engineering & data cleaning
│   ├── feature_engineering.py  # Technical indicators, patterns
│   ├── data_cleaning.py        # Data validation, outlier removal
│   ├── data_loader.py          # Load data from MongoDB
│   ├── feature_selection.py    # Feature importance analysis
│   ├── data_splitter.py        # Train/test/validation split
│   ├── preprocessors/
│   │   ├── price_preprocessor.py
│   │   ├── volume_preprocessor.py
│   │   └── news_preprocessor.py
│   └── config/
│       └── feature_config.yml
├── model-training/             # Training scripts
│   ├── arima/
│   │   ├── train_arima.py
│   │   ├── hyperparameter_tuning.py
│   │   └── config/arima_config.yml
│   ├── lstm/
│   │   ├── train_lstm.py
│   │   ├── model_architecture.py
│   │   ├── data_preprocessing.py
│   │   └── config/lstm_config.yml
│   ├── transformer/
│   │   ├── train_transformer.py
│   │   ├── attention_model.py
│   │   ├── positional_encoding.py
│   │   └── config/transformer_config.yml
│   ├── catboost/
│   │   ├── train_catboost.py
│   │   ├── feature_importance.py
│   │   └── config/catboost_config.yml
│   └── ensemble/
│       ├── ensemble_trainer.py
│       ├── model_stacking.py
│       └── voting_classifier.py
├── model-evaluation/           # Backtesting & metrics
│   ├── backtesting/
│   │   ├── backtest_engine.py
│   │   ├── strategy_tester.py
│   │   └── performance_analyzer.py
│   ├── metrics/
│   │   ├── regression_metrics.py
│   │   ├── classification_metrics.py
│   │   ├── trading_metrics.py
│   │   └── risk_metrics.py
│   ├── validation/
│   │   ├── cross_validator.py
│   │   ├── time_series_validator.py
│   │   └── walk_forward_validator.py
│   └── reports/
│       ├── model_report_generator.py
│       ├── performance_dashboard.py
│       └── comparison_report.py
├── experiments/                # Research & notebooks
│   ├── notebooks/
│   │   ├── data_exploration.ipynb
│   │   ├── feature_analysis.ipynb
│   │   ├── model_comparison.ipynb
│   │   └── strategy_research.ipynb
│   ├── research/
│   │   ├── market_regime_detection.py
│   │   ├── volatility_modeling.py
│   │   └── correlation_analysis.py
│   └── prototypes/
│       ├── new_indicators.py
│       ├── alternative_models.py
│       └── ensemble_experiments.py
└── pipelines/                  # Training pipelines
    ├── training_pipeline.py    # Main training orchestrator
    ├── data_pipeline.py        # Data processing pipeline
    ├── model_pipeline.py       # Model training pipeline
    ├── evaluation_pipeline.py  # Evaluation pipeline
    ├── deployment_pipeline.py  # Model deployment pipeline
    ├── schedulers/
    │   ├── daily_retrain.py
    │   ├── weekly_evaluation.py
    │   └── monthly_backtest.py
    └── config/
        └── pipeline_config.yml
```

## Configuration

### Environment Variables
```python
# Data Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=stock_ai
FEATURE_STORE_PATH=/app/features
MODEL_REGISTRY_PATH=/app/models

# Training Configuration
TRAINING_DATA_DAYS=1000
VALIDATION_SPLIT=0.2
TEST_SPLIT=0.1
RANDOM_SEED=42

# Model Configuration
ARIMA_MAX_ORDER=(5,1,5)
LSTM_SEQUENCE_LENGTH=60
TRANSFORMER_D_MODEL=512
CATBOOST_ITERATIONS=1000

# Compute Configuration
USE_GPU=true
N_JOBS=4
BATCH_SIZE=32
```

## Model Types

### 1. ARIMA Models
**Purpose**: Time series forecasting with trend and seasonality
**Features**:
- Auto-ARIMA for order selection
- Seasonal decomposition
- Residual analysis
- Confidence intervals

### 2. LSTM Models
**Purpose**: Deep learning for sequential pattern recognition
**Features**:
- Multi-layer LSTM architecture
- Dropout regularization
- Attention mechanisms
- Bidirectional processing

### 3. Transformer Models
**Purpose**: Attention-based sequence modeling
**Features**:
- Multi-head attention
- Positional encoding
- Layer normalization
- Residual connections

### 4. CatBoost Models
**Purpose**: Gradient boosting for feature-rich predictions
**Features**:
- Categorical feature handling
- Feature importance analysis
- Cross-validation
- Hyperparameter optimization

### 5. Ensemble Models
**Purpose**: Combining multiple models for better performance
**Features**:
- Voting classifiers
- Model stacking
- Dynamic weighting
- Confidence-based selection

## Feature Engineering

### Technical Indicators
```python
# Price-based features
- Returns (1d, 5d, 20d)
- Volatility (rolling std)
- Price ratios (high/low, close/open)

# Technical indicators
- RSI (14, 30 periods)
- MACD (12, 26, 9)
- Bollinger Bands (20, 2)
- Moving Averages (5, 10, 20, 50, 200)
- Stochastic Oscillator
- Williams %R
- ATR (Average True Range)

# Volume indicators
- Volume SMA
- Volume Rate of Change
- On-Balance Volume (OBV)
- Volume Price Trend (VPT)

# Pattern features
- Candlestick patterns (doji, hammer, etc.)
- Support/resistance levels
- Trend lines
- Chart patterns
```

## Evaluation Metrics

### Regression Metrics
- **MAE**: Mean Absolute Error
- **RMSE**: Root Mean Square Error
- **MAPE**: Mean Absolute Percentage Error
- **R²**: Coefficient of Determination
- **Directional Accuracy**: Prediction direction correctness

### Trading Metrics
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Gross profit / Gross loss
- **Calmar Ratio**: Annual return / Maximum drawdown

## Tools and Technologies

### Core Libraries
- **pandas**: Data manipulation
- **numpy**: Numerical computing
- **scikit-learn**: Machine learning
- **tensorflow/keras**: Deep learning
- **catboost**: Gradient boosting
- **statsmodels**: Statistical models

### Specialized Libraries
- **ta-lib**: Technical analysis
- **arch**: GARCH models
- **pmdarima**: Auto-ARIMA
- **optuna**: Hyperparameter optimization
- **mlflow**: Experiment tracking