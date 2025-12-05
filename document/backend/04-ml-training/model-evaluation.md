# Model Evaluation Documentation

## Overview

Model evaluation provides comprehensive assessment of trained models through backtesting, performance metrics, and validation strategies to ensure model quality and trading viability.

## Components

### 1. Backtesting Engine
**Location**: `ml-training/model-evaluation/backtesting/backtest_engine.py`

```python
class BacktestEngine:
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
        self.commission = 0.001  # 0.1% commission
    
    def run_backtest(self, model, test_data, strategy='simple'):
        portfolio = Portfolio(self.initial_capital)
        results = []
        
        for i, row in test_data.iterrows():
            # Get prediction
            prediction = model.predict(row.features)
            
            # Generate signal
            signal = self.generate_signal(prediction, strategy)
            
            # Execute trade
            if signal != 'HOLD':
                trade_result = portfolio.execute_trade(
                    symbol=row.symbol,
                    signal=signal,
                    price=row.close,
                    timestamp=row.timestamp
                )
                results.append(trade_result)
        
        return BacktestResults(portfolio, results)
```

### 2. Strategy Tester
**Location**: `ml-training/model-evaluation/backtesting/strategy_tester.py`

```python
class StrategyTester:
    def __init__(self):
        self.strategies = {
            'simple': SimpleStrategy(),
            'threshold': ThresholdStrategy(),
            'momentum': MomentumStrategy(),
            'mean_reversion': MeanReversionStrategy()
        }
    
    def test_strategy(self, model, data, strategy_name):
        strategy = self.strategies[strategy_name]
        
        # Generate signals
        signals = strategy.generate_signals(model, data)
        
        # Calculate returns
        returns = self.calculate_strategy_returns(signals, data)
        
        # Performance metrics
        metrics = self.calculate_performance_metrics(returns)
        
        return StrategyResults(signals, returns, metrics)
```

### 3. Performance Analyzer
**Location**: `ml-training/model-evaluation/backtesting/performance_analyzer.py`

```python
class PerformanceAnalyzer:
    def analyze_performance(self, backtest_results):
        returns = backtest_results.returns
        
        metrics = {
            # Return metrics
            'total_return': self.total_return(returns),
            'annualized_return': self.annualized_return(returns),
            'volatility': self.volatility(returns),
            
            # Risk metrics
            'sharpe_ratio': self.sharpe_ratio(returns),
            'max_drawdown': self.max_drawdown(returns),
            'calmar_ratio': self.calmar_ratio(returns),
            
            # Trading metrics
            'win_rate': self.win_rate(backtest_results.trades),
            'profit_factor': self.profit_factor(backtest_results.trades),
            'avg_trade_return': self.avg_trade_return(backtest_results.trades)
        }
        
        return metrics
```

## Metrics

### 1. Regression Metrics
**Location**: `ml-training/model-evaluation/metrics/regression_metrics.py`

```python
class RegressionMetrics:
    @staticmethod
    def calculate_all(y_true, y_pred):
        return {
            'mae': mean_absolute_error(y_true, y_pred),
            'mse': mean_squared_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mape': mean_absolute_percentage_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred),
            'directional_accuracy': directional_accuracy(y_true, y_pred)
        }
    
    @staticmethod
    def directional_accuracy(y_true, y_pred):
        """Calculate percentage of correct direction predictions"""
        true_direction = np.sign(np.diff(y_true))
        pred_direction = np.sign(np.diff(y_pred))
        return np.mean(true_direction == pred_direction)
```

### 2. Trading Metrics
**Location**: `ml-training/model-evaluation/metrics/trading_metrics.py`

```python
class TradingMetrics:
    @staticmethod
    def sharpe_ratio(returns, risk_free_rate=0.02):
        """Calculate Sharpe ratio"""
        excess_returns = returns - risk_free_rate / 252
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
    
    @staticmethod
    def max_drawdown(returns):
        """Calculate maximum drawdown"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    @staticmethod
    def calmar_ratio(returns):
        """Calculate Calmar ratio"""
        annual_return = (1 + returns).prod() ** (252 / len(returns)) - 1
        max_dd = abs(TradingMetrics.max_drawdown(returns))
        return annual_return / max_dd if max_dd != 0 else 0
```

### 3. Risk Metrics
**Location**: `ml-training/model-evaluation/metrics/risk_metrics.py`

```python
class RiskMetrics:
    @staticmethod
    def value_at_risk(returns, confidence_level=0.05):
        """Calculate Value at Risk"""
        return np.percentile(returns, confidence_level * 100)
    
    @staticmethod
    def expected_shortfall(returns, confidence_level=0.05):
        """Calculate Expected Shortfall (Conditional VaR)"""
        var = RiskMetrics.value_at_risk(returns, confidence_level)
        return returns[returns <= var].mean()
    
    @staticmethod
    def beta(returns, market_returns):
        """Calculate beta relative to market"""
        covariance = np.cov(returns, market_returns)[0][1]
        market_variance = np.var(market_returns)
        return covariance / market_variance
```

## Validation

### 1. Cross Validator
**Location**: `ml-training/model-evaluation/validation/cross_validator.py`

```python
class CrossValidator:
    def __init__(self, cv_folds=5):
        self.cv_folds = cv_folds
    
    def time_series_cv(self, data, model_trainer):
        """Time series cross-validation with expanding window"""
        n_samples = len(data)
        fold_size = n_samples // self.cv_folds
        
        cv_scores = []
        
        for i in range(self.cv_folds):
            # Expanding window: use all data up to current fold
            train_end = (i + 1) * fold_size
            val_start = train_end
            val_end = min(val_start + fold_size, n_samples)
            
            train_data = data[:train_end]
            val_data = data[val_start:val_end]
            
            # Train model
            model = model_trainer.train(train_data)
            
            # Evaluate
            predictions = model.predict(val_data.features)
            score = mean_squared_error(val_data.target, predictions)
            cv_scores.append(score)
        
        return cv_scores
```

### 2. Walk Forward Validator
**Location**: `ml-training/model-evaluation/validation/walk_forward_validator.py`

```python
class WalkForwardValidator:
    def __init__(self, train_window=252, test_window=21):
        self.train_window = train_window  # 1 year
        self.test_window = test_window    # 1 month
    
    def validate(self, data, model_trainer):
        """Walk-forward validation for time series"""
        results = []
        
        for i in range(self.train_window, len(data) - self.test_window, self.test_window):
            # Define windows
            train_start = i - self.train_window
            train_end = i
            test_start = i
            test_end = i + self.test_window
            
            # Split data
            train_data = data[train_start:train_end]
            test_data = data[test_start:test_end]
            
            # Train model
            model = model_trainer.train(train_data)
            
            # Test model
            predictions = model.predict(test_data.features)
            
            # Calculate metrics
            metrics = RegressionMetrics.calculate_all(test_data.target, predictions)
            
            results.append({
                'period': f"{test_data.index[0]} to {test_data.index[-1]}",
                'metrics': metrics,
                'predictions': predictions,
                'actual': test_data.target.values
            })
        
        return results
```

## Reports

### 1. Model Report Generator
**Location**: `ml-training/model-evaluation/reports/model_report_generator.py`

```python
class ModelReportGenerator:
    def generate_comprehensive_report(self, model_name, evaluation_results):
        report = {
            'model_info': {
                'name': model_name,
                'evaluation_date': datetime.now().isoformat(),
                'data_period': evaluation_results['data_period']
            },
            'performance_metrics': evaluation_results['metrics'],
            'backtesting_results': evaluation_results['backtest'],
            'cross_validation': evaluation_results['cv_results'],
            'feature_importance': evaluation_results.get('feature_importance', {}),
            'risk_analysis': evaluation_results['risk_metrics'],
            'recommendations': self.generate_recommendations(evaluation_results)
        }
        
        return report
    
    def generate_recommendations(self, results):
        recommendations = []
        
        # Performance-based recommendations
        if results['metrics']['r2'] < 0.3:
            recommendations.append("Low R² score suggests poor model fit. Consider feature engineering or different model architecture.")
        
        if results['backtest']['sharpe_ratio'] < 1.0:
            recommendations.append("Low Sharpe ratio indicates poor risk-adjusted returns. Review trading strategy.")
        
        if results['backtest']['max_drawdown'] < -0.2:
            recommendations.append("High maximum drawdown suggests high risk. Implement risk management measures.")
        
        return recommendations
```

### 2. Performance Dashboard
**Location**: `ml-training/model-evaluation/reports/performance_dashboard.py`

```python
class PerformanceDashboard:
    def create_dashboard(self, evaluation_results):
        """Create interactive dashboard with plotly"""
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=[
                'Cumulative Returns', 'Drawdown',
                'Prediction vs Actual', 'Residuals',
                'Feature Importance', 'Risk Metrics'
            ]
        )
        
        # Cumulative returns plot
        self.add_returns_plot(fig, evaluation_results['backtest'], row=1, col=1)
        
        # Drawdown plot
        self.add_drawdown_plot(fig, evaluation_results['backtest'], row=1, col=2)
        
        # Prediction scatter plot
        self.add_prediction_plot(fig, evaluation_results['predictions'], row=2, col=1)
        
        # Residuals plot
        self.add_residuals_plot(fig, evaluation_results['residuals'], row=2, col=2)
        
        # Feature importance
        self.add_feature_importance(fig, evaluation_results['feature_importance'], row=3, col=1)
        
        # Risk metrics
        self.add_risk_metrics(fig, evaluation_results['risk_metrics'], row=3, col=2)
        
        return fig
```

### 3. Comparison Report
**Location**: `ml-training/model-evaluation/reports/comparison_report.py`

```python
class ComparisonReport:
    def compare_models(self, model_results):
        """Compare multiple models across various metrics"""
        comparison_data = []
        
        for model_name, results in model_results.items():
            comparison_data.append({
                'Model': model_name,
                'R²': results['metrics']['r2'],
                'RMSE': results['metrics']['rmse'],
                'Sharpe Ratio': results['backtest']['sharpe_ratio'],
                'Max Drawdown': results['backtest']['max_drawdown'],
                'Win Rate': results['backtest']['win_rate'],
                'Total Return': results['backtest']['total_return']
            })
        
        df = pd.DataFrame(comparison_data)
        
        # Rank models
        df['Overall Rank'] = self.calculate_overall_rank(df)
        
        return df.sort_values('Overall Rank')
    
    def calculate_overall_rank(self, df):
        """Calculate overall ranking based on multiple metrics"""
        # Normalize metrics (higher is better)
        normalized = df.copy()
        
        # Metrics where higher is better
        positive_metrics = ['R²', 'Sharpe Ratio', 'Win Rate', 'Total Return']
        for metric in positive_metrics:
            normalized[f'{metric}_norm'] = (df[metric] - df[metric].min()) / (df[metric].max() - df[metric].min())
        
        # Metrics where lower is better (invert)
        negative_metrics = ['RMSE', 'Max Drawdown']
        for metric in negative_metrics:
            normalized[f'{metric}_norm'] = 1 - (df[metric] - df[metric].min()) / (df[metric].max() - df[metric].min())
        
        # Calculate weighted average
        weights = {
            'R²_norm': 0.2,
            'RMSE_norm': 0.2,
            'Sharpe Ratio_norm': 0.25,
            'Max Drawdown_norm': 0.15,
            'Win Rate_norm': 0.1,
            'Total Return_norm': 0.1
        }
        
        overall_score = sum(normalized[metric] * weight for metric, weight in weights.items())
        return overall_score.rank(ascending=False)
```

## Configuration

### Evaluation Configuration
**Location**: `ml-training/model-evaluation/config/evaluation_config.yml`

```yaml
evaluation:
  backtesting:
    initial_capital: 100000
    commission: 0.001
    slippage: 0.0005
    
  validation:
    cv_folds: 5
    walk_forward:
      train_window: 252
      test_window: 21
    
  metrics:
    regression: ['mae', 'mse', 'rmse', 'mape', 'r2']
    trading: ['sharpe_ratio', 'max_drawdown', 'calmar_ratio', 'win_rate']
    risk: ['var_95', 'expected_shortfall', 'beta']
    
  reporting:
    generate_plots: true
    save_predictions: true
    comparison_metrics: ['r2', 'sharpe_ratio', 'max_drawdown']
```

## Usage Examples

### Complete Model Evaluation
```python
def evaluate_model_complete(model, test_data):
    # Initialize evaluators
    backtest_engine = BacktestEngine()
    performance_analyzer = PerformanceAnalyzer()
    cross_validator = CrossValidator()
    
    # Run backtesting
    backtest_results = backtest_engine.run_backtest(model, test_data)
    
    # Analyze performance
    performance_metrics = performance_analyzer.analyze_performance(backtest_results)
    
    # Cross-validation
    cv_scores = cross_validator.time_series_cv(test_data, model)
    
    # Generate report
    report_generator = ModelReportGenerator()
    report = report_generator.generate_comprehensive_report(
        model_name='LSTM',
        evaluation_results={
            'metrics': performance_metrics,
            'backtest': backtest_results,
            'cv_results': cv_scores
        }
    )
    
    return report
```