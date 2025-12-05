# Training Pipelines Documentation

## Overview

Training pipelines provide automated, orchestrated workflows for the complete ML lifecycle from data preparation to model deployment. They ensure reproducible, scalable, and maintainable ML operations.

## Pipeline Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Data Pipeline   │───►│ Model Pipeline   │───►│ Evaluation      │
│ (ETL + Features)│    │ (Training)       │    │ Pipeline        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Feature Store   │    │ Model Registry   │    │ Deployment      │
│ (Processed)     │    │ (Artifacts)      │    │ Pipeline        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Core Pipelines

### 1. Training Pipeline
**Location**: `ml-training/pipelines/training_pipeline.py`

Main orchestrator that coordinates all training activities.

```python
class TrainingPipeline:
    def __init__(self, config):
        self.config = config
        self.data_pipeline = DataPipeline(config['data'])
        self.model_pipeline = ModelPipeline(config['models'])
        self.evaluation_pipeline = EvaluationPipeline(config['evaluation'])
        self.deployment_pipeline = DeploymentPipeline(config['deployment'])
    
    def run_full_pipeline(self, symbols=None, retrain_all=False):
        """Run complete training pipeline"""
        try:
            # 1. Data Pipeline
            logger.info("Starting data pipeline...")
            feature_data = self.data_pipeline.run(symbols)
            
            # 2. Model Pipeline
            logger.info("Starting model training...")
            trained_models = self.model_pipeline.run(feature_data, retrain_all)
            
            # 3. Evaluation Pipeline
            logger.info("Starting model evaluation...")
            evaluation_results = self.evaluation_pipeline.run(trained_models, feature_data)
            
            # 4. Model Selection
            best_models = self.select_best_models(evaluation_results)
            
            # 5. Deployment Pipeline
            logger.info("Starting deployment...")
            deployment_results = self.deployment_pipeline.run(best_models)
            
            # 6. Generate Report
            report = self.generate_pipeline_report(
                feature_data, trained_models, evaluation_results, deployment_results
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            self.handle_pipeline_failure(e)
            raise
    
    def select_best_models(self, evaluation_results):
        """Select best performing models for deployment"""
        best_models = {}
        
        for model_type in evaluation_results:
            models = evaluation_results[model_type]
            
            # Rank by composite score
            best_model = max(models.items(), 
                           key=lambda x: self.calculate_composite_score(x[1]))
            
            best_models[model_type] = best_model
        
        return best_models
    
    def calculate_composite_score(self, evaluation_result):
        """Calculate composite score for model ranking"""
        weights = self.config['model_selection']['weights']
        
        score = (
            weights['r2'] * evaluation_result['metrics']['r2'] +
            weights['sharpe'] * max(0, evaluation_result['backtest']['sharpe_ratio']) +
            weights['drawdown'] * (1 - abs(evaluation_result['backtest']['max_drawdown']))
        )
        
        return score
```

### 2. Data Pipeline
**Location**: `ml-training/pipelines/data_pipeline.py`

Handles data extraction, transformation, and feature engineering.

```python
class DataPipeline:
    def __init__(self, config):
        self.config = config
        self.data_loader = DataLoader(config['mongodb'])
        self.feature_engineer = FeatureEngineer(config['features'])
        self.data_cleaner = DataCleaner(config['cleaning'])
        self.feature_selector = FeatureSelector(config['selection'])
    
    def run(self, symbols=None):
        """Execute data pipeline"""
        # 1. Load raw data
        raw_data = self.load_raw_data(symbols)
        
        # 2. Clean data
        clean_data = self.clean_data(raw_data)
        
        # 3. Engineer features
        feature_data = self.engineer_features(clean_data)
        
        # 4. Select features
        selected_data = self.select_features(feature_data)
        
        # 5. Split data
        train_val_test = self.split_data(selected_data)
        
        # 6. Save to feature store
        self.save_to_feature_store(train_val_test)
        
        return train_val_test
    
    def load_raw_data(self, symbols):
        """Load raw price data from MongoDB"""
        if symbols is None:
            symbols = self.get_all_symbols()
        
        data = {}
        for symbol in symbols:
            symbol_data = self.data_loader.load_price_data(
                symbol=symbol,
                start_date=self.config['start_date'],
                end_date=self.config['end_date']
            )
            data[symbol] = symbol_data
        
        return data
    
    def engineer_features(self, clean_data):
        """Engineer features for all symbols"""
        feature_data = {}
        
        for symbol, data in clean_data.items():
            features = self.feature_engineer.engineer_features(data)
            feature_data[symbol] = features
        
        return feature_data
    
    def save_to_feature_store(self, processed_data):
        """Save processed features to feature store"""
        feature_store_path = self.config['feature_store_path']
        
        for split_name, split_data in processed_data.items():
            for symbol, data in split_data.items():
                file_path = os.path.join(
                    feature_store_path, 
                    f"{symbol}_{split_name}_features.parquet"
                )
                data.to_parquet(file_path)
```

### 3. Model Pipeline
**Location**: `ml-training/pipelines/model_pipeline.py`

Orchestrates training of multiple model types with hyperparameter optimization.

```python
class ModelPipeline:
    def __init__(self, config):
        self.config = config
        self.model_trainers = self.initialize_trainers()
        self.hyperopt = HyperparameterOptimizer(config['optimization'])
        self.model_registry = ModelRegistry(config['registry_path'])
    
    def run(self, feature_data, retrain_all=False):
        """Execute model training pipeline"""
        trained_models = {}
        
        for model_type in self.config['model_types']:
            logger.info(f"Training {model_type} models...")
            
            # Check if retraining is needed
            if not retrain_all and self.should_skip_training(model_type):
                logger.info(f"Skipping {model_type} - recent model exists")
                continue
            
            # Hyperparameter optimization
            if self.config['optimization']['enabled']:
                best_params = self.hyperopt.optimize(model_type, feature_data)
            else:
                best_params = self.config['models'][model_type]['default_params']
            
            # Train models for each symbol
            symbol_models = {}
            for symbol in feature_data['train'].keys():
                symbol_data = self.prepare_symbol_data(feature_data, symbol)
                
                # Train model
                trainer = self.model_trainers[model_type]
                trainer.update_params(best_params)
                
                model = trainer.train(symbol_data)
                
                # Save model
                model_path = self.model_registry.save_model(
                    model, f"{model_type}_{symbol}", 
                    {'params': best_params, 'symbol': symbol}
                )
                
                symbol_models[symbol] = {
                    'model': model,
                    'path': model_path,
                    'params': best_params
                }
            
            trained_models[model_type] = symbol_models
        
        return trained_models
    
    def should_skip_training(self, model_type):
        """Check if model training should be skipped"""
        last_training = self.model_registry.get_last_training_time(model_type)
        if last_training is None:
            return False
        
        hours_since_training = (datetime.now() - last_training).total_seconds() / 3600
        min_hours = self.config['retraining']['min_hours_between']
        
        return hours_since_training < min_hours
```

### 4. Evaluation Pipeline
**Location**: `ml-training/pipelines/evaluation_pipeline.py`

Comprehensive model evaluation with backtesting and performance analysis.

```python
class EvaluationPipeline:
    def __init__(self, config):
        self.config = config
        self.backtest_engine = BacktestEngine(config['backtesting'])
        self.performance_analyzer = PerformanceAnalyzer()
        self.cross_validator = CrossValidator(config['cross_validation'])
    
    def run(self, trained_models, feature_data):
        """Execute evaluation pipeline"""
        evaluation_results = {}
        
        for model_type, symbol_models in trained_models.items():
            logger.info(f"Evaluating {model_type} models...")
            
            model_results = {}
            for symbol, model_info in symbol_models.items():
                # Prepare test data
                test_data = feature_data['test'][symbol]
                
                # Run evaluation
                symbol_results = self.evaluate_model(
                    model_info['model'], test_data, symbol
                )
                
                model_results[symbol] = symbol_results
            
            evaluation_results[model_type] = model_results
        
        # Generate comparison report
        self.generate_comparison_report(evaluation_results)
        
        return evaluation_results
    
    def evaluate_model(self, model, test_data, symbol):
        """Comprehensive model evaluation"""
        # 1. Prediction metrics
        predictions = model.predict(test_data.drop('target', axis=1))
        metrics = self.calculate_prediction_metrics(test_data['target'], predictions)
        
        # 2. Backtesting
        backtest_results = self.backtest_engine.run_backtest(
            model, test_data, symbol
        )
        
        # 3. Performance analysis
        performance_metrics = self.performance_analyzer.analyze_performance(
            backtest_results
        )
        
        # 4. Cross-validation
        cv_scores = self.cross_validator.time_series_cv(test_data, model)
        
        # 5. Risk analysis
        risk_metrics = self.calculate_risk_metrics(backtest_results.returns)
        
        return {
            'metrics': metrics,
            'backtest': backtest_results,
            'performance': performance_metrics,
            'cv_scores': cv_scores,
            'risk': risk_metrics,
            'predictions': predictions
        }
```

### 5. Deployment Pipeline
**Location**: `ml-training/pipelines/deployment_pipeline.py`

Handles model deployment to production environment.

```python
class DeploymentPipeline:
    def __init__(self, config):
        self.config = config
        self.model_registry = ModelRegistry(config['registry_path'])
        self.deployment_manager = DeploymentManager(config['deployment'])
    
    def run(self, best_models):
        """Execute deployment pipeline"""
        deployment_results = {}
        
        for model_type, model_info in best_models.items():
            logger.info(f"Deploying {model_type} models...")
            
            # Prepare deployment package
            deployment_package = self.prepare_deployment_package(
                model_type, model_info
            )
            
            # Deploy to staging
            staging_result = self.deploy_to_staging(deployment_package)
            
            # Run deployment tests
            test_results = self.run_deployment_tests(staging_result)
            
            # Deploy to production if tests pass
            if test_results['passed']:
                production_result = self.deploy_to_production(deployment_package)
                deployment_results[model_type] = production_result
            else:
                logger.error(f"Deployment tests failed for {model_type}")
                deployment_results[model_type] = {'status': 'failed', 'tests': test_results}
        
        return deployment_results
    
    def prepare_deployment_package(self, model_type, model_info):
        """Prepare model deployment package"""
        package = {
            'model_type': model_type,
            'models': {},
            'metadata': {},
            'dependencies': self.get_model_dependencies(model_type)
        }
        
        for symbol, symbol_model in model_info[1].items():
            # Load model
            model = self.model_registry.load_model(
                f"{model_type}_{symbol}", 
                version='latest'
            )
            
            # Serialize model
            serialized_model = self.serialize_model(model, model_type)
            
            package['models'][symbol] = serialized_model
            package['metadata'][symbol] = symbol_model['params']
        
        return package
    
    def deploy_to_production(self, deployment_package):
        """Deploy models to production environment"""
        # Update model serving infrastructure
        serving_config = self.generate_serving_config(deployment_package)
        
        # Deploy via Kubernetes or Docker
        deployment_result = self.deployment_manager.deploy(
            deployment_package, serving_config
        )
        
        # Update model registry
        self.model_registry.mark_as_production(
            deployment_package['model_type']
        )
        
        return deployment_result
```

## Schedulers

### 1. Daily Retrain
**Location**: `ml-training/pipelines/schedulers/daily_retrain.py`

```python
class DailyRetrainScheduler:
    def __init__(self, config):
        self.config = config
        self.training_pipeline = TrainingPipeline(config['pipeline'])
    
    def run_daily_retrain(self):
        """Run daily retraining process"""
        # Check if retraining is needed
        if not self.should_retrain():
            logger.info("Daily retrain not needed")
            return
        
        # Get symbols that need retraining
        symbols_to_retrain = self.get_symbols_for_retraining()
        
        # Run incremental training
        results = self.training_pipeline.run_incremental_training(
            symbols=symbols_to_retrain
        )
        
        # Send notifications
        self.send_retraining_notification(results)
        
        return results
    
    def should_retrain(self):
        """Determine if retraining is needed"""
        # Check data freshness
        latest_data_time = self.get_latest_data_timestamp()
        hours_since_data = (datetime.now() - latest_data_time).total_seconds() / 3600
        
        if hours_since_data > self.config['max_data_age_hours']:
            return False
        
        # Check model performance degradation
        current_performance = self.get_current_model_performance()
        performance_threshold = self.config['performance_threshold']
        
        return current_performance < performance_threshold
```

### 2. Weekly Evaluation
**Location**: `ml-training/pipelines/schedulers/weekly_evaluation.py`

```python
class WeeklyEvaluationScheduler:
    def __init__(self, config):
        self.config = config
        self.evaluation_pipeline = EvaluationPipeline(config['evaluation'])
    
    def run_weekly_evaluation(self):
        """Run comprehensive weekly model evaluation"""
        # Load all production models
        production_models = self.load_production_models()
        
        # Get evaluation data (last week)
        evaluation_data = self.get_weekly_evaluation_data()
        
        # Run comprehensive evaluation
        results = self.evaluation_pipeline.run(production_models, evaluation_data)
        
        # Generate weekly report
        report = self.generate_weekly_report(results)
        
        # Check for model degradation
        degraded_models = self.check_model_degradation(results)
        
        if degraded_models:
            self.trigger_model_retraining(degraded_models)
        
        return report
```

## Configuration

### Pipeline Configuration
**Location**: `ml-training/pipelines/config/pipeline_config.yml`

```yaml
pipeline:
  data:
    mongodb:
      uri: "mongodb://localhost:27017"
      database: "stock_ai"
    start_date: "2020-01-01"
    feature_store_path: "/app/features"
    
  models:
    model_types: ['arima', 'lstm', 'transformer', 'catboost']
    registry_path: "/app/models"
    retraining:
      min_hours_between: 24
      performance_threshold: 0.7
    
  optimization:
    enabled: true
    n_trials: 50
    timeout: 1800
    
  evaluation:
    backtesting:
      initial_capital: 100000
      commission: 0.001
    cross_validation:
      cv_folds: 5
      
  deployment:
    staging_endpoint: "http://staging-api:8000"
    production_endpoint: "http://prod-api:8000"
    
  scheduling:
    daily_retrain:
      enabled: true
      time: "02:00"
      max_data_age_hours: 48
    weekly_evaluation:
      enabled: true
      day: "sunday"
      time: "01:00"

model_selection:
  weights:
    r2: 0.3
    sharpe: 0.4
    drawdown: 0.3
```

## Monitoring and Logging

### Pipeline Monitoring
```python
class PipelineMonitor:
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alerting = AlertingSystem()
    
    def monitor_pipeline_execution(self, pipeline_name, execution_id):
        """Monitor pipeline execution"""
        start_time = time.time()
        
        try:
            # Monitor resource usage
            self.monitor_resources(execution_id)
            
            # Track pipeline progress
            self.track_progress(pipeline_name, execution_id)
            
            # Check for anomalies
            self.detect_anomalies(pipeline_name)
            
        except Exception as e:
            self.alerting.send_alert(
                f"Pipeline monitoring failed: {e}",
                severity="high"
            )
    
    def track_pipeline_metrics(self, pipeline_name, metrics):
        """Track pipeline performance metrics"""
        self.metrics_collector.record_metrics(
            pipeline_name, metrics, timestamp=datetime.now()
        )
```

## Usage Examples

### Running Complete Pipeline
```bash
# Run full training pipeline
python -m ml-training.pipelines.training_pipeline --config config/pipeline_config.yml

# Run specific pipeline components
python -m ml-training.pipelines.data_pipeline --symbols VCB,VIC,VHM
python -m ml-training.pipelines.model_pipeline --model-type lstm --retrain

# Schedule automated runs
python -m ml-training.pipelines.schedulers.daily_retrain
```

### Pipeline API
```python
# Programmatic pipeline execution
from ml_training.pipelines import TrainingPipeline

config = load_config('pipeline_config.yml')
pipeline = TrainingPipeline(config)

# Run full pipeline
results = pipeline.run_full_pipeline(symbols=['VCB', 'VIC'])

# Run incremental update
results = pipeline.run_incremental_training(symbols=['VHM'])
```