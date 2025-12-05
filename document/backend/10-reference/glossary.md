# Glossary

## Technical Terms

### **API (Application Programming Interface)**
Interface for communication between software components. In this system, includes REST APIs for external access and internal service APIs.

### **Aggregation Service**
Microservice responsible for combining AI analysis and LLM sentiment results to generate final stock scores and recommendations.

### **Circuit Breaker**
Design pattern that prevents cascading failures by temporarily disabling failing services and allowing them to recover.

### **Data Collector Service** ✅
Implemented microservice that collects stock price and news data from vnstock API and publishes to Kafka topics.

### **Dead Letter Queue (DLQ)**
Kafka topic for messages that failed processing after multiple retry attempts, allowing for manual review and recovery.

### **ETL (Extract, Transform, Load)**
Data processing pattern used in the data pipeline to collect, normalize, and store stock market data.

## Stock Market Terms

### **HOSE (Ho Chi Minh Stock Exchange)**
Main stock exchange in Vietnam where large-cap stocks are traded.

### **HNX (Hanoi Stock Exchange)**
Secondary stock exchange in Vietnam for mid-cap stocks.

### **OHLCV**
Standard price data format: Open, High, Low, Close, Volume for a specific time period.

### **RSI (Relative Strength Index)**
Technical indicator measuring price momentum, ranging from 0-100, used to identify overbought/oversold conditions.

### **MACD (Moving Average Convergence Divergence)**
Technical indicator showing relationship between two moving averages, used for trend analysis.

### **Bollinger Bands**
Technical indicator consisting of moving average with upper/lower bands based on standard deviation.

### **Sentiment Analysis**
Process of analyzing news text to determine positive, negative, or neutral market sentiment toward a stock.

## System Components

### **vnstock Library** ✅
Python library providing access to Vietnamese stock market data, wrapped by our custom client for rate limiting and caching.

### **Kafka Topics**
Named channels for message passing:
- `stock_prices_raw`: Raw price data from collectors
- `stock_news_raw`: Raw news data from collectors
- `analysis_triggers`: Trigger messages for analysis jobs

### **MongoDB Collections**
Database collections storing different data types:
- `stocks`: Stock metadata and current information
- `price_history`: Historical price data
- `news`: News articles and content
- `ai_analysis`: Technical analysis results
- `final_scores`: Aggregated scores and recommendations

### **Redis Cache**
In-memory data store used for caching API responses and session management.

## Data Processing Terms

### **Data Normalization** ✅
Process of converting raw data into standardized format, implemented in `DataNormalizer.normalize_price_data()`.

### **Data Validation** ✅
Process of checking data integrity and business rules, implemented in `DataValidator.validate_price_data()`.

### **Rate Limiting** ✅
Mechanism to control API call frequency, implemented in vnstock client to prevent API abuse.

### **TTL (Time To Live)**
Cache expiration time, determining how long data remains valid before refresh.

### **Partitioning**
Kafka strategy for distributing messages across multiple partitions for parallel processing.

## Architecture Patterns

### **Microservices Architecture**
Design pattern where application is composed of small, independent services communicating via APIs.

### **Event-Driven Architecture**
Design pattern where services communicate through events (messages) rather than direct calls.

### **Producer-Consumer Pattern** ✅
Messaging pattern where producers send messages to queues and consumers process them asynchronously.

### **Repository Pattern**
Data access pattern that encapsulates database operations behind a consistent interface.

## Development Terms

### **Docker Compose** ✅
Tool for defining and running multi-container Docker applications, used for local development environment.

### **pytest** ✅
Python testing framework used for unit and integration tests in the system.

### **Black** 
Python code formatter ensuring consistent code style across the project.

### **Flake8**
Python linting tool for code quality and style checking.

### **ADR (Architecture Decision Record)**
Document capturing important architectural decisions and their rationale.

## Monitoring Terms

### **Prometheus**
Monitoring system for collecting and storing metrics from services.

### **Grafana**
Visualization platform for creating dashboards from Prometheus metrics.

### **Health Check**
Endpoint or mechanism to verify service availability and proper functioning.

### **SLA (Service Level Agreement)**
Commitment to specific performance metrics like uptime, response time, and availability.

## Acronyms

- **AI**: Artificial Intelligence
- **API**: Application Programming Interface
- **CPU**: Central Processing Unit
- **CRUD**: Create, Read, Update, Delete
- **DLQ**: Dead Letter Queue
- **ETL**: Extract, Transform, Load
- **HTTP**: Hypertext Transfer Protocol
- **JSON**: JavaScript Object Notation
- **JWT**: JSON Web Token
- **LLM**: Large Language Model
- **ML**: Machine Learning
- **OHLCV**: Open, High, Low, Close, Volume
- **RAM**: Random Access Memory
- **REST**: Representational State Transfer
- **SLA**: Service Level Agreement
- **SQL**: Structured Query Language
- **SSL**: Secure Sockets Layer
- **TTL**: Time To Live
- **UUID**: Universally Unique Identifier
- **VCI**: Viet Capital Securities (vnstock data source)
- **WSL**: Windows Subsystem for Linux