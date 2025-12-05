import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error
import pandas as pd

@dataclass
class OptimizationResult:
    optimal_weights: Dict[str, Any]
    performance_metrics: Dict[str, float]
    backtest_results: Dict[str, Any]
    improvement: float
    timestamp: datetime

@dataclass
class PerformanceMetrics:
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    sharpe_ratio: float
    max_drawdown: float
    total_return: float

class WeightOptimizer:
    """Dynamic weight optimization using machine learning and backtesting"""
    
    def __init__(self, score_calculator):
        self.score_calculator = score_calculator
        self.optimization_history = []
        
        # Optimization parameters
        self.lookback_days = 90
        self.min_samples = 50
        self.optimization_frequency = 7  # days
        
        # Performance tracking
        self.baseline_weights = score_calculator.weights.copy()
        self.current_performance = None
        
    async def collect_historical_data(self, stock_symbols: List[str], 
                                    days: int = 90) -> pd.DataFrame:
        """Collect historical data for optimization"""
        data = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        for symbol in stock_symbols:
            # This would typically fetch from your database
            # For now, we'll simulate the data structure
            sample_data = {
                'symbol': symbol,
                'date': end_date,
                'technical_score': np.random.uniform(0.2, 0.8),
                'sentiment_score': np.random.uniform(0.2, 0.8),
                'risk_score': np.random.uniform(0.1, 0.7),
                'actual_return': np.random.uniform(-0.1, 0.1),  # 1-day return
                'price_change': np.random.uniform(-0.05, 0.05)
            }
            data.append(sample_data)
        
        return pd.DataFrame(data)
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and targets for ML optimization"""
        # Features: component scores and their interactions
        features = []
        targets = []
        
        for _, row in df.iterrows():
            feature_vector = [
                row['technical_score'],
                row['sentiment_score'],
                row['risk_score'],
                row['technical_score'] * row['sentiment_score'],  # Interaction
                row['technical_score'] * (1 - row['risk_score']),  # Risk-adjusted technical
                row['sentiment_score'] * (1 - row['risk_score']),  # Risk-adjusted sentiment
                abs(row['technical_score'] - row['sentiment_score']),  # Divergence
            ]
            features.append(feature_vector)
            targets.append(row['actual_return'])
        
        return np.array(features), np.array(targets)
    
    def optimize_weights_ml(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Use machine learning to optimize weights"""
        # Time series cross-validation
        tscv = TimeSeriesSplit(n_splits=5)
        
        best_weights = None
        best_score = float('-inf')
        
        # Grid search over weight combinations
        weight_combinations = [
            {'technical': 0.7, 'sentiment': 0.2, 'risk': 0.1},
            {'technical': 0.6, 'sentiment': 0.25, 'risk': 0.15},
            {'technical': 0.5, 'sentiment': 0.35, 'risk': 0.15},
            {'technical': 0.65, 'sentiment': 0.3, 'risk': 0.05},
            {'technical': 0.55, 'sentiment': 0.3, 'risk': 0.15},
        ]
        
        for weights in weight_combinations:
            scores = []
            
            for train_idx, test_idx in tscv.split(X):
                X_train, X_test = X[train_idx], X[test_idx]
                y_train, y_test = y[train_idx], y[test_idx]
                
                # Calculate weighted scores
                weighted_scores = self._calculate_weighted_scores(X_test, weights)
                
                # Evaluate correlation with actual returns
                correlation = np.corrcoef(weighted_scores, y_test)[0, 1]
                if not np.isnan(correlation):
                    scores.append(correlation)
            
            avg_score = np.mean(scores) if scores else 0
            if avg_score > best_score:
                best_score = avg_score
                best_weights = weights
        
        return best_weights or self.baseline_weights['final']
    
    def _calculate_weighted_scores(self, X: np.ndarray, weights: Dict[str, float]) -> np.ndarray:
        """Calculate weighted scores for given weights"""
        technical_scores = X[:, 0]
        sentiment_scores = X[:, 1]
        risk_scores = X[:, 2]
        
        weighted_scores = (
            technical_scores * weights['technical'] +
            sentiment_scores * weights['sentiment'] +
            (1 - risk_scores) * weights['risk']
        )
        
        return weighted_scores
    
    def backtest_weights(self, df: pd.DataFrame, weights: Dict[str, Any]) -> Dict[str, Any]:
        """Backtest weight performance"""
        # Simulate trading based on scores
        df = df.copy()
        df['predicted_score'] = (
            df['technical_score'] * weights['technical'] +
            df['sentiment_score'] * weights['sentiment'] +
            (1 - df['risk_score']) * weights['risk']
        )
        
        # Generate trading signals
        df['signal'] = 0
        df.loc[df['predicted_score'] > 0.7, 'signal'] = 1  # Buy
        df.loc[df['predicted_score'] < 0.3, 'signal'] = -1  # Sell
        
        # Calculate returns
        df['strategy_return'] = df['signal'].shift(1) * df['actual_return']
        df['cumulative_return'] = (1 + df['strategy_return']).cumprod()
        
        # Performance metrics
        total_return = df['cumulative_return'].iloc[-1] - 1
        volatility = df['strategy_return'].std() * np.sqrt(252)  # Annualized
        sharpe_ratio = (df['strategy_return'].mean() * 252) / volatility if volatility > 0 else 0
        
        # Max drawdown
        rolling_max = df['cumulative_return'].expanding().max()
        drawdown = (df['cumulative_return'] - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        # Accuracy metrics
        correct_predictions = ((df['signal'] > 0) & (df['actual_return'] > 0)) | \
                            ((df['signal'] < 0) & (df['actual_return'] < 0))
        accuracy = correct_predictions.sum() / len(df)
        
        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'accuracy': accuracy,
            'volatility': volatility,
            'num_trades': (df['signal'] != 0).sum()
        }
    
    async def optimize_weights(self, stock_symbols: List[str]) -> OptimizationResult:
        """Main weight optimization function"""
        # Collect historical data
        df = await self.collect_historical_data(stock_symbols, self.lookback_days)
        
        if len(df) < self.min_samples:
            raise ValueError(f"Insufficient data: {len(df)} < {self.min_samples}")
        
        # Prepare ML features
        X, y = self.prepare_features(df)
        
        # Optimize weights using ML
        optimal_final_weights = self.optimize_weights_ml(X, y)
        
        # Optimize sub-component weights (technical indicators)
        optimal_technical_weights = self._optimize_technical_weights(df)
        optimal_sentiment_weights = self._optimize_sentiment_weights(df)
        
        # Combine all optimal weights
        optimal_weights = {
            'technical': optimal_technical_weights,
            'sentiment': optimal_sentiment_weights,
            'final': optimal_final_weights
        }
        
        # Backtest performance
        backtest_results = self.backtest_weights(df, optimal_final_weights)
        baseline_results = self.backtest_weights(df, self.baseline_weights['final'])
        
        # Calculate improvement
        improvement = (backtest_results['sharpe_ratio'] - baseline_results['sharpe_ratio']) / \
                     abs(baseline_results['sharpe_ratio']) if baseline_results['sharpe_ratio'] != 0 else 0
        
        # Performance metrics
        performance_metrics = {
            'optimization_accuracy': backtest_results['accuracy'],
            'sharpe_improvement': improvement,
            'return_improvement': backtest_results['total_return'] - baseline_results['total_return'],
            'risk_reduction': baseline_results['max_drawdown'] - backtest_results['max_drawdown']
        }
        
        result = OptimizationResult(
            optimal_weights=optimal_weights,
            performance_metrics=performance_metrics,
            backtest_results=backtest_results,
            improvement=improvement,
            timestamp=datetime.now()
        )
        
        # Store in history
        self.optimization_history.append(result)
        
        return result
    
    def _optimize_technical_weights(self, df: pd.DataFrame) -> Dict[str, float]:
        """Optimize technical indicator weights"""
        # Simplified optimization - in practice, you'd have individual indicator data
        base_weights = self.baseline_weights['technical'].copy()
        
        # Adjust based on recent performance (placeholder logic)
        adjustments = {
            'rsi': np.random.uniform(0.9, 1.1),
            'macd': np.random.uniform(0.9, 1.1),
            'bollinger': np.random.uniform(0.9, 1.1),
            'volume': np.random.uniform(0.9, 1.1),
            'pattern': np.random.uniform(0.9, 1.1),
            'trend': np.random.uniform(0.9, 1.1)
        }
        
        # Apply adjustments and normalize
        for key in base_weights:
            base_weights[key] *= adjustments.get(key, 1.0)
        
        # Normalize to sum to 1
        total = sum(base_weights.values())
        return {k: v/total for k, v in base_weights.items()}
    
    def _optimize_sentiment_weights(self, df: pd.DataFrame) -> Dict[str, float]:
        """Optimize sentiment component weights"""
        base_weights = self.baseline_weights['sentiment'].copy()
        
        # Adjust based on sentiment effectiveness (placeholder)
        adjustments = {
            'news_sentiment': np.random.uniform(0.9, 1.1),
            'news_impact': np.random.uniform(0.9, 1.1),
            'market_sentiment': np.random.uniform(0.9, 1.1)
        }
        
        for key in base_weights:
            base_weights[key] *= adjustments.get(key, 1.0)
        
        # Normalize
        total = sum(base_weights.values())
        return {k: v/total for k, v in base_weights.items()}
    
    def should_reoptimize(self) -> bool:
        """Check if weights should be reoptimized"""
        if not self.optimization_history:
            return True
        
        last_optimization = self.optimization_history[-1].timestamp
        days_since = (datetime.now() - last_optimization).days
        
        return days_since >= self.optimization_frequency
    
    async def auto_optimize(self, stock_symbols: List[str]) -> Optional[OptimizationResult]:
        """Automatically optimize weights if needed"""
        if self.should_reoptimize():
            try:
                result = await self.optimize_weights(stock_symbols)
                
                # Apply weights if improvement is significant
                if result.improvement > 0.05:  # 5% improvement threshold
                    self.score_calculator.update_weights(result.optimal_weights)
                    return result
            except Exception as e:
                print(f"Optimization failed: {e}")
        
        return None
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get summary of optimization history"""
        if not self.optimization_history:
            return {'message': 'No optimization history available'}
        
        recent = self.optimization_history[-5:]  # Last 5 optimizations
        
        return {
            'total_optimizations': len(self.optimization_history),
            'recent_improvements': [r.improvement for r in recent],
            'avg_improvement': np.mean([r.improvement for r in recent]),
            'last_optimization': self.optimization_history[-1].timestamp,
            'current_weights': self.score_calculator.weights,
            'baseline_weights': self.baseline_weights
        }