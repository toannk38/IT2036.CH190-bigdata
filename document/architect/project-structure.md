# Cấu trúc Project - Stock AI Backend System

## Tổng quan

Hệ thống AI gợi ý và cảnh báo cổ phiếu Việt Nam được thiết kế theo kiến trúc microservices với Docker containerization. Cấu trúc này hỗ trợ scalability, maintainability và development efficiency.

---

## 📁 Cấu trúc thư mục tổng thể

```
backend/
├── services/                    # Microservices
│   ├── data-collector/         # Thu thập dữ liệu vnstock
│   ├── kafka-consumer/         # Xử lý Kafka messages  
│   ├── ai-analysis/           # AI/ML analysis engine
│   ├── llm-analysis/          # LLM news analysis
│   ├── aggregation/           # Score aggregation service
│   ├── api/                   # REST API service
│   └── auth/                  # Authentication service
├── ml-training/               # ML Model Training
│   ├── data-preparation/      # Feature engineering, data cleaning
│   ├── model-training/        # Training scripts cho ARIMA, LSTM, etc.
│   ├── model-evaluation/      # Backtesting, performance metrics
│   ├── experiments/           # Jupyter notebooks, experiments
│   └── pipelines/            # Training pipelines
├── libs/                      # Shared libraries
│   ├── database/             # MongoDB connection & models
│   ├── kafka/                # Kafka utilities
│   ├── vnstock/              # vnstock wrapper
│   ├── ml/                   # ML utilities
│   └── common/               # Common utilities
├── models/                   # Trained ML models (artifacts)
│   ├── arima/               # ARIMA model files
│   ├── lstm/                # LSTM model files
│   ├── transformer/         # Transformer model files
│   ├── catboost/            # CatBoost model files
│   └── versions/            # Model versioning
├── infrastructure/           # Docker infrastructure
│   └── docker/              # Docker configs, docker-compose files
├── database/                # Database related
│   ├── migrations/         # MongoDB migrations
│   ├── schemas/            # Collection schemas
│   └── seeds/              # Initial data
├── config/                  # Configuration files
├── monitoring/             # Monitoring & logging
│   ├── prometheus/        # Prometheus configs
│   ├── grafana/           # Grafana dashboards
│   └── elk/               # ELK stack configs
├── scripts/                # Utility scripts
├── tests/                  # Test suites
├── document/              # Documentation
├── deployment/            # Deployment configs
├── .env.example           # Environment variables template
├── docker-compose.yml     # Main docker compose
├── docker-compose.dev.yml # Development environment
├── docker-compose.prod.yml # Production environment
└── README.md              # Project documentation
```

---

## 🏗️ Services Layer

### services/data-collector/
**Chức năng:** Thu thập dữ liệu từ vnstock library
```
data-collector/
├── src/
│   ├── collectors/
│   │   ├── price_collector.py     # Thu thập giá cổ phiếu
│   │   ├── news_collector.py      # Thu thập tin tức
│   │   └── base_collector.py      # Base collector class
│   ├── processors/
│   │   ├── data_validator.py      # Validation dữ liệu
│   │   ├── data_cleaner.py        # Làm sạch dữ liệu
│   │   └── data_normalizer.py     # Chuẩn hóa format
│   ├── producers/
│   │   └── kafka_producer.py      # Gửi dữ liệu tới Kafka
│   ├── config/
│   │   └── collector_config.py    # Configuration
│   └── main.py                    # Entry point
├── requirements.txt
├── Dockerfile
└── README.md
```

### services/kafka-consumer/
**Chức năng:** Consume messages từ Kafka và lưu vào MongoDB
```
kafka-consumer/
├── src/
│   ├── consumers/
│   │   ├── price_consumer.py      # Consumer giá cổ phiếu
│   │   ├── news_consumer.py       # Consumer tin tức
│   │   └── base_consumer.py       # Base consumer class
│   ├── processors/
│   │   ├── data_transformer.py    # Transform dữ liệu
│   │   └── data_validator.py      # Validate trước khi lưu
│   ├── storage/
│   │   └── mongodb_storage.py     # Lưu trữ MongoDB
│   └── main.py
├── requirements.txt
├── Dockerfile
└── README.md
```

### services/ai-analysis/
**Chức năng:** AI/ML analysis engine cho technical analysis
```
ai-analysis/
├── src/
│   ├── models/
│   │   ├── arima_model.py         # ARIMA implementation
│   │   ├── lstm_model.py          # LSTM implementation
│   │   ├── transformer_model.py   # Transformer implementation
│   │   ├── catboost_model.py      # CatBoost implementation
│   │   └── ensemble_model.py      # Model ensemble
│   ├── features/
│   │   ├── technical_indicators.py # RSI, MACD, Bollinger Bands
│   │   ├── pattern_detection.py   # Candlestick patterns
│   │   └── volume_analysis.py     # Volume indicators
│   ├── services/
│   │   ├── analysis_service.py    # Main analysis service
│   │   ├── prediction_service.py  # Prediction logic
│   │   └── scoring_service.py     # Technical scoring
│   ├── utils/
│   │   ├── data_loader.py         # Load data từ MongoDB
│   │   └── model_loader.py        # Load trained models
│   └── main.py
├── requirements.txt
├── Dockerfile
└── README.md
```

### services/llm-analysis/
**Chức năng:** LLM news analysis cho sentiment và insights
```
llm-analysis/
├── src/
│   ├── analyzers/
│   │   ├── sentiment_analyzer.py  # Sentiment analysis
│   │   ├── summary_analyzer.py    # News summarization
│   │   └── insight_extractor.py   # Key insights extraction
│   ├── llm/
│   │   ├── openai_client.py      # OpenAI API integration
│   │   ├── claude_client.py      # Claude API integration
│   │   └── prompt_templates.py   # Prompt engineering
│   ├── processors/
│   │   ├── text_preprocessor.py  # Text cleaning
│   │   ├── batch_processor.py    # Batch processing
│   │   └── result_validator.py   # Validate LLM outputs
│   └── main.py
├── requirements.txt
├── Dockerfile
└── README.md
```

### services/aggregation/
**Chức năng:** Tổng hợp điểm số và sinh alerts
```
aggregation/
├── src/
│   ├── aggregators/
│   │   ├── score_aggregator.py   # Tổng hợp điểm số
│   │   ├── weight_calculator.py  # Tính toán weights
│   │   └── risk_assessor.py      # Đánh giá rủi ro
│   ├── alerts/
│   │   ├── alert_generator.py    # Sinh alerts
│   │   ├── alert_rules.py        # Alert rules engine
│   │   └── notification_service.py # Send notifications
│   ├── scoring/
│   │   ├── technical_scorer.py   # Technical scoring
│   │   ├── sentiment_scorer.py   # Sentiment scoring
│   │   └── final_scorer.py       # Final score calculation
│   └── main.py
├── requirements.txt
├── Dockerfile
└── README.md
```

### services/api/
**Chức năng:** REST API service
```
api/
├── src/
│   ├── routes/
│   │   ├── stocks.py             # Stock information endpoints
│   │   ├── analysis.py           # Analysis endpoints
│   │   ├── alerts.py             # Alert endpoints
│   │   └── news.py               # News endpoints
│   ├── middleware/
│   │   ├── authentication.py     # Auth middleware
│   │   ├── rate_limiting.py      # Rate limiting
│   │   └── caching.py            # Cache middleware
│   ├── models/
│   │   ├── request_models.py     # API request schemas
│   │   └── response_models.py    # API response schemas
│   ├── services/
│   │   ├── stock_service.py      # Stock data service
│   │   ├── analysis_service.py   # Analysis data service
│   │   └── cache_service.py      # Caching service
│   └── main.py                   # FastAPI application
├── requirements.txt
├── Dockerfile
└── README.md
```

### services/auth/
**Chức năng:** Authentication và authorization service
```
auth/
├── src/
│   ├── auth/
│   │   ├── jwt_handler.py        # JWT token handling
│   │   ├── api_key_handler.py    # API key authentication
│   │   └── oauth_handler.py      # OAuth 2.0 handling
│   ├── models/
│   │   ├── user_model.py         # User data model
│   │   └── api_key_model.py      # API key model
│   ├── routes/
│   │   ├── login.py              # Login endpoints
│   │   ├── register.py           # Registration endpoints
│   │   └── api_keys.py           # API key management
│   └── main.py
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🤖 ML Training Layer

### ml-training/data-preparation/
**Chức năng:** Chuẩn bị dữ liệu cho training
```
data-preparation/
├── feature_engineering.py      # Technical indicators, patterns
├── data_cleaning.py           # Data validation, outlier removal
├── data_loader.py             # Load data từ MongoDB
├── feature_selection.py       # Feature importance analysis
├── data_splitter.py           # Train/test/validation split
└── config/
    └── feature_config.yml     # Feature engineering config
```

### ml-training/model-training/
**Chức năng:** Training các ML models
```
model-training/
├── arima/
│   ├── train_arima.py          # ARIMA model training
│   ├── hyperparameter_tuning.py
│   └── config/arima_config.yml
├── lstm/
│   ├── train_lstm.py           # LSTM model training
│   ├── model_architecture.py   # Network architecture
│   ├── data_preprocessing.py   # LSTM-specific preprocessing
│   └── config/lstm_config.yml
├── transformer/
│   ├── train_transformer.py    # Transformer model training
│   ├── attention_model.py      # Attention mechanisms
│   ├── positional_encoding.py  # Positional encoding
│   └── config/transformer_config.yml
├── catboost/
│   ├── train_catboost.py       # CatBoost model training
│   ├── feature_importance.py   # Feature analysis
│   └── config/catboost_config.yml
└── ensemble/
    ├── ensemble_trainer.py     # Ensemble model training
    ├── model_stacking.py       # Model stacking
    └── voting_classifier.py    # Voting methods
```

### ml-training/model-evaluation/
**Chức năng:** Backtesting, performance metrics, validation
```
model-evaluation/
├── backtesting/
│   ├── backtest_engine.py      # Backtesting engine
│   ├── strategy_tester.py      # Trading strategy testing
│   └── performance_analyzer.py # Performance analysis
├── metrics/
│   ├── regression_metrics.py   # Regression evaluation
│   ├── classification_metrics.py # Classification metrics
│   ├── trading_metrics.py      # Trading performance
│   └── risk_metrics.py         # Risk assessment
├── validation/
│   ├── cross_validator.py      # Cross-validation
│   ├── time_series_validator.py # Time series validation
│   └── walk_forward_validator.py # Walk-forward analysis
└── reports/
    ├── model_report_generator.py # Report generation
    ├── performance_dashboard.py  # Interactive dashboard
    └── comparison_report.py      # Model comparison
```

### ml-training/experiments/
**Chức năng:** Jupyter notebooks, experiments, research
```
experiments/
├── notebooks/
│   ├── data_exploration.ipynb  # Data analysis
│   ├── feature_analysis.ipynb  # Feature engineering
│   ├── model_comparison.ipynb  # Model comparison
│   └── strategy_research.ipynb # Trading strategies
├── research/
│   ├── market_regime_detection.py # Market regime analysis
│   ├── volatility_modeling.py     # Volatility models
│   └── correlation_analysis.py    # Correlation studies
└── prototypes/
    ├── new_indicators.py       # Experimental indicators
    ├── alternative_models.py   # New model architectures
    └── ensemble_experiments.py # Ensemble methods
```

### ml-training/pipelines/
**Chức năng:** Training pipelines và workflows
```
pipelines/
├── training_pipeline.py        # Main training orchestrator
├── data_pipeline.py            # Data processing pipeline
├── model_pipeline.py           # Model training pipeline
├── evaluation_pipeline.py      # Evaluation pipeline
├── deployment_pipeline.py      # Model deployment
├── schedulers/
│   ├── daily_retrain.py        # Daily retraining
│   ├── weekly_evaluation.py    # Weekly evaluation
│   └── monthly_backtest.py     # Monthly backtesting
└── config/
    └── pipeline_config.yml     # Pipeline configuration
```

---

## 📚 Shared Libraries Layer

### libs/database/
**Chức năng:** Database connections và models
```
database/
├── connection.py              # MongoDB connection
├── models/
│   ├── stock_model.py        # Stock data model
│   ├── price_model.py        # Price history model
│   ├── news_model.py         # News model
│   ├── analysis_model.py     # Analysis results model
│   └── alert_model.py        # Alert model
├── repositories/
│   ├── stock_repository.py   # Stock data access
│   ├── price_repository.py   # Price data access
│   └── news_repository.py    # News data access
└── migrations/
    └── migration_runner.py   # Migration utilities
```

### libs/kafka/
**Chức năng:** Kafka utilities
```
kafka/
├── producer.py               # Kafka producer wrapper
├── consumer.py               # Kafka consumer wrapper
├── config.py                 # Kafka configuration
└── serializers/
    ├── json_serializer.py    # JSON serialization
    └── avro_serializer.py    # Avro serialization
```

### libs/vnstock/
**Chức năng:** vnstock API wrapper
```
vnstock/
├── client.py                 # vnstock client wrapper
├── data_models.py           # Data model definitions
├── rate_limiter.py          # API rate limiting
└── cache.py                 # Response caching
```

### libs/ml/
**Chức năng:** ML utilities
```
ml/
├── feature_engineering/
│   ├── technical_indicators.py # Technical analysis functions
│   ├── pattern_detection.py   # Pattern recognition
│   └── volume_analysis.py     # Volume indicators
├── model_utils/
│   ├── model_loader.py       # Load/save models
│   ├── model_validator.py    # Model validation
│   └── ensemble_utils.py     # Ensemble utilities
└── evaluation/
    ├── metrics.py            # Performance metrics
    └── backtesting.py        # Backtesting utilities
```

### libs/common/
**Chức năng:** Common utilities
```
common/
├── logging.py               # Structured logging
├── config.py               # Configuration management
├── exceptions.py           # Custom exceptions
├── decorators.py          # Common decorators
├── validators.py          # Data validation utilities
└── utils.py               # Miscellaneous utilities
```

---

## 🗄️ Models Storage

### models/
**Chức năng:** Lưu trữ trained models
```
models/
├── arima/
│   ├── v1.0/
│   │   ├── model.pkl         # Trained ARIMA model
│   │   ├── metadata.json     # Model metadata
│   │   └── performance.json  # Performance metrics
│   └── v1.1/
├── lstm/
│   ├── v1.0/
│   │   ├── model.h5         # Keras model
│   │   ├── weights.h5       # Model weights
│   │   ├── scaler.pkl       # Data scaler
│   │   └── config.json      # Model configuration
│   └── v1.1/
├── transformer/
│   ├── v1.0/
│   │   ├── pytorch_model.bin # PyTorch model
│   │   ├── config.json      # Model config
│   │   └── tokenizer.json   # Tokenizer config
│   └── v1.1/
├── catboost/
│   ├── v1.0/
│   │   ├── model.cbm        # CatBoost model
│   │   ├── features.json    # Feature names
│   │   └── importance.json  # Feature importance
│   └── v1.1/
└── versions/
    ├── model_registry.json  # Model version registry
    └── deployment_config.json # Deployment configurations
```

---

## 🐳 Infrastructure Layer

### infrastructure/docker/
**Chức năng:** Docker containerization
```
docker/
├── dockerfiles/
│   ├── Dockerfile.api        # API service dockerfile
│   ├── Dockerfile.collector  # Data collector dockerfile
│   ├── Dockerfile.ai        # AI analysis dockerfile
│   └── Dockerfile.llm       # LLM analysis dockerfile
├── compose/
│   ├── docker-compose.yml    # Main compose file
│   ├── docker-compose.dev.yml # Development environment
│   ├── docker-compose.prod.yml # Production environment
│   └── docker-compose.monitoring.yml # Monitoring stack
├── configs/
│   ├── nginx/              # Nginx configurations
│   ├── prometheus/         # Prometheus configs
│   └── grafana/           # Grafana configs
└── scripts/
    ├── build.sh            # Build all images
    ├── deploy.sh           # Deploy services
    └── cleanup.sh          # Cleanup unused images
```

---

## 🗃️ Database Layer

### database/
**Chức năng:** Database schemas và migrations
```
database/
├── migrations/
│   ├── 001_initial_schema.py     # Initial collections
│   ├── 002_add_indexes.py        # Database indexes
│   ├── 003_add_analysis_collections.py
│   └── migration_runner.py       # Run migrations
├── schemas/
│   ├── stocks_schema.json        # Stock collection schema
│   ├── price_history_schema.json # Price history schema
│   ├── news_schema.json          # News collection schema
│   ├── ai_analysis_schema.json   # AI analysis schema
│   └── alerts_schema.json        # Alerts schema
└── seeds/
    ├── stock_list.json          # Initial stock list
    ├── industries.json          # Industry classifications
    └── seed_runner.py           # Load initial data
```

---

## ⚙️ Configuration Layer

### config/
**Chức năng:** Configuration management
```
config/
├── environments/
│   ├── development.yml       # Development config
│   ├── staging.yml          # Staging config
│   └── production.yml       # Production config
├── services/
│   ├── api_config.yml       # API service config
│   ├── collector_config.yml # Data collector config
│   ├── ai_config.yml        # AI analysis config
│   └── llm_config.yml       # LLM analysis config
├── database/
│   └── mongodb_config.yml   # MongoDB configuration
├── kafka/
│   └── kafka_config.yml     # Kafka configuration
└── monitoring/
    ├── prometheus_config.yml # Prometheus config
    └── grafana_config.yml   # Grafana config
```

---

## 📊 Monitoring Layer

### monitoring/
**Chức năng:** System monitoring và logging

#### monitoring/prometheus/
```
prometheus/
├── prometheus.yml           # Main Prometheus config
├── alert_rules/
│   ├── system_alerts.yml   # System-level alerts
│   ├── api_alerts.yml      # API performance alerts
│   ├── ml_alerts.yml       # ML model alerts
│   └── business_alerts.yml # Business metric alerts
└── targets/
    └── service_discovery.yml # Service discovery config
```

#### monitoring/grafana/
```
grafana/
├── dashboards/
│   ├── system_overview.json    # System health dashboard
│   ├── api_performance.json    # API metrics dashboard
│   ├── ml_monitoring.json      # ML model performance
│   ├── business_metrics.json   # Business KPIs
│   └── alert_dashboard.json    # Alert management
├── datasources/
│   ├── prometheus.yml         # Prometheus datasource
│   └── elasticsearch.yml      # Elasticsearch datasource
└── provisioning/
    ├── dashboards.yml         # Dashboard provisioning
    └── datasources.yml        # Datasource provisioning
```

#### monitoring/elk/
```
elk/
├── elasticsearch/
│   ├── elasticsearch.yml      # Elasticsearch config
│   └── index_templates/       # Index templates
├── logstash/
│   ├── logstash.conf         # Logstash pipeline config
│   ├── patterns/             # Custom log patterns
│   └── filters/              # Log filtering rules
└── kibana/
    ├── kibana.yml            # Kibana configuration
    └── dashboards/           # Log analysis dashboards
```

---

## 🧪 Testing Layer

### tests/
**Chức năng:** Test suites cho tất cả components
```
tests/
├── unit/                    # Unit tests
│   ├── services/           # Service layer tests
│   ├── libs/               # Library tests
│   └── ml_training/        # ML training tests
├── integration/            # Integration tests
│   ├── api_tests/         # API endpoint tests
│   ├── database_tests/    # Database integration tests
│   └── kafka_tests/       # Kafka integration tests
├── e2e/                   # End-to-end tests
│   ├── workflow_tests/    # Complete workflow tests
│   └── performance_tests/ # Performance testing
├── fixtures/              # Test data fixtures
│   ├── sample_data/       # Sample stock data
│   └── mock_responses/    # Mock API responses
├── utils/                 # Test utilities
│   ├── test_helpers.py    # Common test functions
│   └── mock_services.py   # Mock external services
└── conftest.py           # Pytest configuration
```

---

## 🚀 Deployment Layer

### deployment/
**Chức năng:** Deployment configurations và scripts
```
deployment/
├── environments/
│   ├── development/
│   │   ├── .env.dev         # Development environment vars
│   │   └── docker-compose.override.yml
│   ├── staging/
│   │   ├── .env.staging     # Staging environment vars
│   │   └── docker-compose.override.yml
│   └── production/
│       ├── .env.prod        # Production environment vars
│       └── docker-compose.override.yml
├── scripts/
│   ├── deploy.sh           # Deployment script
│   ├── rollback.sh         # Rollback script
│   ├── health_check.sh     # Health check script
│   └── backup.sh           # Backup script
├── secrets/
│   ├── secrets.example     # Example secrets file
│   └── .gitkeep           # Keep directory in git
└── ci-cd/
    ├── github-actions/     # GitHub Actions workflows
    └── jenkins/           # Jenkins pipeline scripts
```

---

## 🔧 Utility Scripts

### scripts/
**Chức năng:** Utility và maintenance scripts
```
scripts/
├── setup/
│   ├── install_dependencies.sh  # Install system dependencies
│   ├── setup_database.sh       # Setup MongoDB
│   └── init_project.sh         # Initialize project
├── maintenance/
│   ├── cleanup_logs.sh         # Clean old logs
│   ├── backup_database.sh      # Backup MongoDB
│   ├── update_models.sh        # Update ML models
│   └── health_check.sh         # System health check
├── data/
│   ├── import_stock_list.py    # Import initial stock list
│   ├── backfill_data.py       # Backfill historical data
│   └── data_quality_check.py  # Data quality validation
└── development/
    ├── generate_test_data.py   # Generate test data
    ├── reset_database.sh      # Reset development database
    └── start_dev_env.sh       # Start development environment
```

---

## 📝 Root Level Files

### Core Files
```
backend/
├── .env.example              # Environment variables template
├── .gitignore               # Git ignore rules
├── docker-compose.yml       # Main docker compose
├── docker-compose.dev.yml   # Development environment
├── docker-compose.prod.yml  # Production environment
├── requirements.txt         # Python dependencies (if shared)
├── Makefile                # Common development commands
├── README.md               # Project documentation
├── LICENSE                 # Project license
└── CHANGELOG.md            # Version changelog
```

### Makefile Example
```makefile
# Development commands
.PHONY: dev up down build test clean

dev:
	docker-compose -f docker-compose.dev.yml up -d

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

test:
	docker-compose exec api pytest tests/

clean:
	docker-compose down -v --remove-orphans
	docker system prune -f
```

---

## 🎯 Benefits của cấu trúc này

### 1. **Modularity**
- Mỗi service độc lập, có thể develop/deploy riêng biệt
- Shared libraries tránh code duplication
- Clear separation of concerns

### 2. **Scalability**
- Microservices có thể scale independently
- Docker containerization dễ dàng horizontal scaling
- Model versioning hỗ trợ A/B testing

### 3. **Maintainability**
- Cấu trúc rõ ràng, dễ navigate
- Consistent naming conventions
- Comprehensive documentation

### 4. **Development Efficiency**
- Separate ML training pipeline
- Comprehensive testing structure
- Environment-specific configurations

### 5. **Production Ready**
- Monitoring và logging infrastructure
- Deployment automation
- Health checks và backup strategies

---

## 🚀 Getting Started

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Setup environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

3. **Start development environment**
   ```bash
   make dev
   # hoặc
   docker-compose -f docker-compose.dev.yml up -d
   ```

4. **Initialize database**
   ```bash
   ./scripts/setup/setup_database.sh
   ```

5. **Run tests**
   ```bash
   make test
   ```

Cấu trúc này cung cấp foundation mạnh mẽ cho việc phát triển hệ thống AI gợi ý cổ phiếu với khả năng mở rộng và bảo trì tốt.