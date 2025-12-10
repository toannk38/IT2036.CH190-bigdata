# Implementation Plan

- [ ] 1. Set up project structure and core infrastructure
  - Create directory structure for collectors, consumers, engines, services, and DAGs
  - Set up Docker Compose configuration with Kafka, MongoDB, and Airflow standalone
  - Configure environment variables and .env file template
  - Create requirements.txt with core dependencies (kafka-python, pymongo, vnstock, fastapi, apache-airflow)
  - _Requirements: 10.1_

- [-] 2. Implement Symbol Manager
- [x] 2.1 Create SymbolManager class with MongoDB integration
  - Implement `__init__` with MongoDB client connection
  - Implement `load_symbols_from_json()` to parse JSON and upsert to MongoDB
  - Implement `get_active_symbols()` to query active symbols
  - Implement `update_symbol()` for metadata updates
  - _Requirements: 2.1, 2.2, 2.4, 2.5_

- [x] 2.2 Write property test for symbol upsert idempotence
  - **Property 3: Symbol upsert idempotence**
  - **Validates: Requirements 2.4**

- [x] 2.3 Write property test for active symbols retrieval
  - **Property 4: Active symbols retrieval**
  - **Validates: Requirements 2.5**

- [x] 2.4 Write unit tests for SymbolManager
  - Test JSON parsing and loading
  - Test symbol retrieval with different filters
  - Test error handling for invalid JSON
  - _Requirements: 2.1, 2.2, 2.5_

- [x] 3. Implement Price Collector
- [x] 3.1 Create PriceCollector class with vnstock integration
  - Implement `__init__` with Kafka producer, vnstock client, and SymbolManager
  - Implement `collect()` to fetch prices for all active symbols
  - Implement `publish_to_kafka()` to send data to stock_prices_raw topic
  - Add error handling and logging for failed symbol collections
  - _Requirements: 1.2, 1.3, 1.6_

- [x] 3.2 Write property test for symbol-based price collection
  - **Property 5: Symbol-based price collection**
  - **Validates: Requirements 1.2**

- [x] 3.3 Write property test for price data Kafka publishing
  - **Property 6: Price data Kafka publishing**
  - **Validates: Requirements 1.3**

- [x] 3.4 Write unit tests for PriceCollector
  - Test price data collection with mocked vnstock
  - Test Kafka publishing with mocked producer
  - Test error handling for network failures
  - _Requirements: 1.2, 1.3, 1.6_

- [x] 4. Implement News Collector
- [x] 4.1 Create NewsCollector class with vnstock integration
  - Implement `__init__` with Kafka producer, vnstock client, and SymbolManager
  - Implement `collect()` to fetch news for all active symbols
  - Implement `publish_to_kafka()` to send data to stock_news_raw topic
  - Add error handling and logging for failed symbol collections
  - _Requirements: 3.1, 3.2, 3.3, 3.6_

- [x] 4.2 Write property test for symbol-based news collection
  - **Property 9: Symbol-based news collection**
  - **Validates: Requirements 3.2**

- [x] 4.3 Write property test for news data Kafka publishing
  - **Property 10: News data Kafka publishing**
  - **Validates: Requirements 3.3**

- [x] 4.4 Write unit tests for NewsCollector
  - Test news collection with mocked vnstock
  - Test Kafka publishing with mocked producer
  - Test error handling for API failures
  - _Requirements: 3.1, 3.2, 3.3, 3.6_

- [x] 5. Implement Kafka Consumer
- [x] 5.1 Create KafkaDataConsumer class
  - Implement `__init__` with Kafka consumer and MongoDB client
  - Implement `consume_and_store()` for continuous message processing
  - Implement `validate_message()` for schema validation
  - Add offset management and error recovery
  - _Requirements: 1.4, 3.4, 8.1, 8.2, 8.3_

- [x] 5.2 Write property test for price data round-trip preservation
  - **Property 7: Price data round-trip preservation**
  - **Validates: Requirements 1.4**

- [x] 5.3 Write property test for price data completeness
  - **Property 8: Price data completeness**
  - **Validates: Requirements 1.5**

- [x] 5.4 Write property test for news data round-trip preservation
  - **Property 11: News data round-trip preservation**
  - **Validates: Requirements 3.4**

- [x] 5.5 Write property test for news data completeness
  - **Property 12: News data completeness**
  - **Validates: Requirements 3.5**

- [x] 5.6 Write unit tests for KafkaDataConsumer
  - Test message consumption and storage
  - Test schema validation
  - Test offset recovery after failure
  - _Requirements: 1.4, 3.4, 8.3_

- [x] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [-] 7. Implement AI/ML Engine
- [x] 7.1 Create AIMLEngine class with analysis functions
  - Implement `__init__` with MongoDB client and model loading
  - Implement `analyze_stock()` to orchestrate analysis
  - Implement `calculate_trend()` using time-series analysis
  - Implement `calculate_risk_score()` based on volatility
  - Implement `calculate_technical_score()` using RSI, MACD indicators
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 7.2 Write property test for risk score validity
  - **Property 14: Risk score validity**
  - **Validates: Requirements 4.3**

- [x] 7.3 Write property test for technical score validity
  - **Property 15: Technical score validity**
  - **Validates: Requirements 4.4**

- [x] 7.4 Write property test for AI/ML results storage completeness
  - **Property 16: AI/ML results storage completeness**
  - **Validates: Requirements 4.5**

- [x] 7.5 Write unit tests for AIMLEngine
  - Test trend calculation with sample price data
  - Test risk score calculation
  - Test technical indicators calculation
  - _Requirements: 4.2, 4.3, 4.4_

- [ ] 8. Implement LLM Engine
- [x] 8.1 Create LLMEngine class with sentiment analysis
  - Implement `__init__` with MongoDB client and LLM client
  - Implement `analyze_news()` to process news articles
  - Implement `analyze_sentiment()` for single article sentiment
  - Implement `generate_summary()` for multiple articles
  - Implement `calculate_influence_score()` based on source credibility
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 8.2 Write property test for sentiment classification validity
  - **Property 17: Sentiment classification validity**
  - **Validates: Requirements 5.2**

- [x] 8.3 Write property test for influence score validity
  - **Property 18: Influence score validity**
  - **Validates: Requirements 5.4**

- [x] 8.4 Write property test for LLM results storage completeness
  - **Property 19: LLM results storage completeness**
  - **Validates: Requirements 5.5**

- [x] 8.5 Write unit tests for LLMEngine
  - Test sentiment analysis with mocked LLM
  - Test summary generation
  - Test influence score calculation
  - _Requirements: 5.2, 5.3, 5.4_

- [x] 9. Implement Aggregation Service
- [x] 9.1 Create AggregationService class
  - Implement `__init__` with MongoDB client and weight configuration
  - Implement `aggregate()` to combine AI/ML and LLM results
  - Implement `calculate_final_score()` with weighted formula
  - Implement `generate_alerts()` based on score thresholds
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 9.2 Write property test for final score range validity
  - **Property 21: Final score range validity**
  - **Validates: Requirements 6.3**

- [x] 9.3 Write property test for alert generation consistency
  - **Property 22: Alert generation consistency**
  - **Validates: Requirements 6.4**

- [x] 9.4 Write property test for final scores storage completeness
  - **Property 23: Final scores storage completeness**
  - **Validates: Requirements 6.5**

- [x] 9.5 Write unit tests for AggregationService
  - Test weighted score calculation
  - Test alert generation for different score ranges
  - Test data retrieval and aggregation
  - _Requirements: 6.2, 6.3, 6.4_

- [x] 10. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [-] 11. Implement API Service
- [x] 11.1 Create FastAPI application with endpoints
  - Implement `get_stock_summary()` endpoint for comprehensive stock data
  - Implement `get_alerts()` endpoint with sorting and pagination
  - Implement `get_historical_analysis()` endpoint with date filtering
  - Add input validation and error handling
  - Add response models and documentation
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 11.2 Write property test for stock summary response completeness
  - **Property 24: Stock summary response completeness**
  - **Validates: Requirements 7.1**

- [x] 11.3 Write property test for alert list sorting
  - **Property 25: Alert list sorting**
  - **Validates: Requirements 7.2**

- [x] 11.4 Write property test for historical data date range filtering
  - **Property 26: Historical data date range filtering**
  - **Validates: Requirements 7.3**

- [ ] 11.5 Write property test for API error response validity
  - **Property 27: API error response validity**
  - **Validates: Requirements 7.4**

- [ ] 11.6 Write unit tests for API endpoints
  - Test each endpoint with valid inputs
  - Test error handling with invalid inputs
  - Test response format and status codes
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 12. Implement Airflow DAGs
- [ ] 12.1 Create Price Collection DAG
  - Define DAG with 5-minute schedule (*/5 * * * *)
  - Create PythonOperator for price collection task
  - Configure retry policy and error handling
  - Add logging and monitoring
  - _Requirements: 11.2, 11.4_

- [ ] 12.2 Create News Collection DAG
  - Define DAG with 30-minute schedule (*/30 * * * *)
  - Create PythonOperator for news collection task
  - Configure retry policy and error handling
  - Add logging and monitoring
  - _Requirements: 11.3, 11.4_

- [ ] 12.3 Create Analysis Pipeline DAG
  - Define DAG with hourly schedule (@hourly)
  - Create PythonOperators for AI/ML and LLM analysis (parallel)
  - Create PythonOperator for aggregation (after both analyses)
  - Configure task dependencies and retry policy
  - Add logging and monitoring
  - _Requirements: 12.1, 12.3, 12.4, 12.5_

- [ ] 12.4 Write property test for aggregation triggering after dual analysis
  - **Property 35: Aggregation triggering after dual analysis**
  - **Validates: Requirements 12.3**

- [ ] 12.5 Write integration tests for DAG execution
  - Test DAG parsing and validation
  - Test task execution order
  - Test retry behavior on failures
  - _Requirements: 11.4, 12.3, 12.4_

- [ ] 13. Implement error handling and logging
- [ ] 13.1 Create centralized logging configuration
  - Set up structured logging with JSON format
  - Configure log levels for different components
  - Add context information (component name, timestamp)
  - _Requirements: 13.1, 13.4_

- [ ] 13.2 Add error handling utilities
  - Implement retry with exponential backoff decorator
  - Implement circuit breaker for external API calls
  - Add dead letter queue handling for Kafka
  - _Requirements: 1.6, 3.6, 9.5, 13.2_

- [ ] 13.3 Write property test for error logging completeness
  - **Property 38: Error logging completeness**
  - **Validates: Requirements 13.1**

- [ ] 13.4 Write property test for database retry with exponential backoff
  - **Property 31: Database retry with exponential backoff**
  - **Validates: Requirements 9.5**

- [ ] 13.5 Write unit tests for error handling
  - Test retry logic with different failure scenarios
  - Test circuit breaker state transitions
  - Test logging output format
  - _Requirements: 13.1, 13.2, 13.3_

- [ ] 14. Create Docker Compose configuration
- [ ] 14.1 Write docker-compose.yml
  - Configure Zookeeper and Kafka services
  - Configure MongoDB service with volume
  - Configure Airflow standalone service
  - Configure Kafka consumer service
  - Configure API service
  - Set up Docker networks and dependencies
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [ ] 14.2 Create Dockerfiles for each service
  - Create Dockerfile for Airflow with DAGs
  - Create Dockerfile for Kafka consumer
  - Create Dockerfile for API service
  - Optimize image sizes and layers
  - _Requirements: 10.1_

- [ ] 14.3 Create initialization scripts
  - Create script to load symbols from JSON to MongoDB
  - Create script to initialize MongoDB indexes
  - Create script to create Kafka topics
  - _Requirements: 2.3, 9.1_

- [ ] 15. Final Checkpoint - Integration testing
  - Ensure all tests pass, ask the user if questions arise.
  - Test end-to-end data flow from collection to API
  - Verify DAG execution and scheduling
  - Test error recovery and retry mechanisms
