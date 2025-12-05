# Model Training Documentation

## Overview

Model training component handles training of multiple model types including ARIMA, LSTM, Transformers, and CatBoost with hyperparameter optimization and model versioning.

## Model Types

### 1. ARIMA Models
**Location**: `ml-training/model-training/arima/`

```python
class ARIMATrainer:
    def __init__(self, config):
        self.max_p, self.max_d, self.max_q = config['max_order']
        self.seasonal = config.get('seasonal', False)
    
    def train(self, data):
        # Auto-ARIMA for order selection
        model = auto_arima(
            data,
            max_p=self.max_p,
            max_d=self.max_d,
            max_q=self.max_q,
            seasonal=self.seasonal,
            stepwise=True,
            suppress_warnings=True
        )
        
        return model
```

**Configuration**: `arima/config/arima_config.yml`
```yaml
arima:
  max_order: [5, 1, 5]
  seasonal: false
  information_criterion: 'aic'
  stepwise: true
  seasonal_test: 'ocsb'
```

### 2. LSTM Models
**Location**: `ml-training/model-training/lstm/`

```python
class LSTMTrainer:
    def __init__(self, config):
        self.sequence_length = config['sequence_length']
        self.hidden_units = config['hidden_units']
        self.dropout_rate = config['dropout_rate']
    
    def build_model(self, input_shape):
        model = Sequential([
            LSTM(self.hidden_units[0], return_sequences=True, input_shape=input_shape),
            Dropout(self.dropout_rate),
            LSTM(self.hidden_units[1], return_sequences=False),
            Dropout(self.dropout_rate),
            Dense(1, activation='linear')
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return model
```

**Configuration**: `lstm/config/lstm_config.yml`
```yaml
lstm:
  sequence_length: 60
  hidden_units: [128, 64]
  dropout_rate: 0.2
  batch_size: 32
  epochs: 100
  early_stopping:
    patience: 10
    monitor: 'val_loss'
```

### 3. Transformer Models
**Location**: `ml-training/model-training/transformer/`

```python
class TransformerTrainer:
    def __init__(self, config):
        self.d_model = config['d_model']
        self.num_heads = config['num_heads']
        self.num_layers = config['num_layers']
    
    def build_model(self, input_shape):
        inputs = Input(shape=input_shape)
        
        # Positional encoding
        x = self.positional_encoding(inputs)
        
        # Transformer blocks
        for _ in range(self.num_layers):
            x = self.transformer_block(x)
        
        # Output layer
        x = GlobalAveragePooling1D()(x)
        outputs = Dense(1, activation='linear')(x)
        
        model = Model(inputs=inputs, outputs=outputs)
        return model
```

**Configuration**: `transformer/config/transformer_config.yml`
```yaml
transformer:
  d_model: 512
  num_heads: 8
  num_layers: 6
  dff: 2048
  dropout_rate: 0.1
  sequence_length: 60
```

### 4. CatBoost Models
**Location**: `ml-training/model-training/catboost/`

```python
class CatBoostTrainer:
    def __init__(self, config):
        self.iterations = config['iterations']
        self.learning_rate = config['learning_rate']
        self.depth = config['depth']
    
    def train(self, X_train, y_train, X_val, y_val):
        model = CatBoostRegressor(
            iterations=self.iterations,
            learning_rate=self.learning_rate,
            depth=self.depth,
            loss_function='RMSE',
            eval_metric='MAE',
            random_seed=42,
            verbose=False
        )
        
        model.fit(
            X_train, y_train,
            eval_set=(X_val, y_val),
            early_stopping_rounds=50,
            use_best_model=True
        )
        
        return model
```

**Configuration**: `catboost/config/catboost_config.yml`
```yaml
catboost:
  iterations: 1000
  learning_rate: 0.1
  depth: 6
  l2_leaf_reg: 3
  bootstrap_type: 'Bayesian'
  bagging_temperature: 1
  od_type: 'Iter'
  od_wait: 50
```

### 5. Ensemble Models
**Location**: `ml-training/model-training/ensemble/`

```python
class EnsembleTrainer:
    def __init__(self, base_models):
        self.base_models = base_models
        self.meta_model = None
    
    def train_stacking(self, X_train, y_train, X_val, y_val):
        # Generate base predictions
        base_predictions = []
        for model in self.base_models:
            pred = model.predict(X_val)
            base_predictions.append(pred)
        
        # Stack predictions
        stacked_features = np.column_stack(base_predictions)
        
        # Train meta-model
        self.meta_model = LinearRegression()
        self.meta_model.fit(stacked_features, y_val)
        
        return self
```

## Training Pipeline

### Main Training Orchestrator
**Location**: `ml-training/model-training/training_orchestrator.py`

```python
class TrainingOrchestrator:
    def __init__(self):
        self.trainers = {
            'arima': ARIMATrainer(arima_config),
            'lstm': LSTMTrainer(lstm_config),
            'transformer': TransformerTrainer(transformer_config),
            'catboost': CatBoostTrainer(catboost_config)
        }
    
    def train_all_models(self, data):
        trained_models = {}
        
        for model_name, trainer in self.trainers.items():
            print(f"Training {model_name} model...")
            
            # Prepare data for specific model
            model_data = self.prepare_data_for_model(data, model_name)
            
            # Train model
            model = trainer.train(model_data)
            
            # Validate model
            validation_results = self.validate_model(model, model_data)
            
            # Save model
            model_path = self.save_model(model, model_name, validation_results)
            
            trained_models[model_name] = {
                'model': model,
                'path': model_path,
                'validation': validation_results
            }
        
        return trained_models
```

## Hyperparameter Optimization

### Optuna Integration
```python
class HyperparameterOptimizer:
    def __init__(self, model_type):
        self.model_type = model_type
    
    def optimize_lstm(self, trial, data):
        # Suggest hyperparameters
        hidden_units_1 = trial.suggest_int('hidden_units_1', 32, 256)
        hidden_units_2 = trial.suggest_int('hidden_units_2', 16, 128)
        dropout_rate = trial.suggest_float('dropout_rate', 0.1, 0.5)
        learning_rate = trial.suggest_float('learning_rate', 1e-4, 1e-2, log=True)
        
        # Build and train model
        config = {
            'hidden_units': [hidden_units_1, hidden_units_2],
            'dropout_rate': dropout_rate,
            'learning_rate': learning_rate
        }
        
        trainer = LSTMTrainer(config)
        model = trainer.train(data)
        
        # Return validation score
        return model.evaluate(data['X_val'], data['y_val'])[0]  # Return loss
    
    def run_optimization(self, data, n_trials=100):
        study = optuna.create_study(direction='minimize')
        study.optimize(
            lambda trial: self.optimize_lstm(trial, data),
            n_trials=n_trials
        )
        
        return study.best_params
```

## Model Versioning

### Model Registry
```python
class ModelRegistry:
    def __init__(self, registry_path):
        self.registry_path = registry_path
    
    def save_model(self, model, model_name, metadata):
        # Generate version
        version = self.generate_version()
        
        # Create model directory
        model_dir = os.path.join(self.registry_path, model_name, version)
        os.makedirs(model_dir, exist_ok=True)
        
        # Save model artifacts
        if model_name in ['lstm', 'transformer']:
            model.save(os.path.join(model_dir, 'model.h5'))
        elif model_name == 'catboost':
            model.save_model(os.path.join(model_dir, 'model.cbm'))
        elif model_name == 'arima':
            joblib.dump(model, os.path.join(model_dir, 'model.pkl'))
        
        # Save metadata
        metadata_path = os.path.join(model_dir, 'metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        return model_dir
    
    def load_model(self, model_name, version='latest'):
        if version == 'latest':
            version = self.get_latest_version(model_name)
        
        model_dir = os.path.join(self.registry_path, model_name, version)
        
        # Load model based on type
        if model_name in ['lstm', 'transformer']:
            from tensorflow.keras.models import load_model
            return load_model(os.path.join(model_dir, 'model.h5'))
        elif model_name == 'catboost':
            from catboost import CatBoostRegressor
            model = CatBoostRegressor()
            model.load_model(os.path.join(model_dir, 'model.cbm'))
            return model
        elif model_name == 'arima':
            return joblib.load(os.path.join(model_dir, 'model.pkl'))
```

## Training Configuration

### Global Training Config
**Location**: `ml-training/model-training/config/training_config.yml`

```yaml
training:
  data:
    train_ratio: 0.7
    val_ratio: 0.2
    test_ratio: 0.1
    min_samples: 1000
  
  optimization:
    n_trials: 100
    timeout: 3600  # 1 hour
    pruner: 'median'
  
  validation:
    cv_folds: 5
    scoring: ['mse', 'mae', 'r2']
  
  model_registry:
    path: '/app/models'
    versioning: 'timestamp'
    max_versions: 10
```

## Monitoring

### Training Metrics
- **Loss Curves**: Training and validation loss
- **Convergence**: Model convergence tracking
- **Overfitting**: Early stopping and regularization
- **Resource Usage**: GPU/CPU utilization

### Model Performance
- **Validation Scores**: Cross-validation results
- **Feature Importance**: Model interpretability
- **Prediction Quality**: Distribution analysis
- **Stability**: Performance consistency