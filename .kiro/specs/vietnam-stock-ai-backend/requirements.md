# Requirements Document

## Introduction

Hệ thống Backend AI Cổ phiếu Việt Nam là một nền tảng phân tích cổ phiếu tự động sử dụng kiến trúc microservices và data-driven. Hệ thống thu thập dữ liệu giá cổ phiếu và tin tức từ thị trường Việt Nam, thực hiện phân tích định lượng (AI/ML) và định tính (LLM), sau đó tổng hợp để đưa ra các khuyến nghị đầu tư thông minh. Hệ thống sử dụng Kafka làm trung tâm streaming dữ liệu, MongoDB để lưu trữ, và cung cấp REST API cho các ứng dụng frontend.

## Glossary

- **System**: Hệ thống Backend AI Cổ phiếu Việt Nam
- **Data Pipeline**: Thành phần thu thập và xử lý dữ liệu thô từ các nguồn bên ngoài
- **Price Collector**: Module thu thập dữ liệu giá cổ phiếu
- **News Collector**: Module thu thập tin tức liên quan đến cổ phiếu
- **Kafka**: Nền tảng streaming phân tán để truyền tải dữ liệu giữa các thành phần
- **MongoDB**: Cơ sở dữ liệu NoSQL để lưu trữ dữ liệu
- **AI/ML Engine**: Module phân tích định lượng sử dụng machine learning
- **LLM Engine**: Module phân tích định tính sử dụng Large Language Model
- **Aggregation Service**: Dịch vụ tổng hợp kết quả từ AI/ML và LLM
- **API Service**: Dịch vụ cung cấp REST API cho client
- **vnstock**: Thư viện Python để truy cập dữ liệu thị trường chứng khoán Việt Nam
- **Technical Score**: Điểm đánh giá kỹ thuật dựa trên các chỉ số kỹ thuật
- **Sentiment Score**: Điểm đánh giá tâm lý thị trường từ tin tức
- **Final Recommendation Score**: Điểm khuyến nghị cuối cùng sau khi tổng hợp
- **Alert**: Cảnh báo tự động về cơ hội hoặc rủi ro đầu tư
- **Airflow**: Nền tảng quản lý và điều phối workflow, scheduling các task ETL và phân tích
- **DAG**: Directed Acyclic Graph - đồ thị định nghĩa workflow và dependencies giữa các task trong Airflow
- **Task**: Đơn vị công việc trong Airflow DAG (ví dụ: thu thập dữ liệu, phân tích, tổng hợp)
- **Symbol**: Mã cổ phiếu (ví dụ: VNM, VIC, HPG)
- **Symbols Collection**: MongoDB collection chứa danh sách các mã cổ phiếu cần theo dõi với thông tin chi tiết
- **ICB**: Industry Classification Benchmark - hệ thống phân loại ngành công nghiệp

## Requirements

### Requirement 1

**User Story:** As a system administrator, I want the system to manage a list of stock symbols and collect price data for those symbols, so that I can track specific stocks of interest.

#### Acceptance Criteria

1. WHEN the System initializes, THE System SHALL load stock symbols from MongoDB collection named symbols
2. WHEN the Price Collector runs on schedule, THE System SHALL retrieve stock price data for all symbols in the symbols collection using vnstock library
3. WHEN price data is retrieved successfully, THE System SHALL publish the data to Kafka topic named stock_prices_raw
4. WHEN price data is published to Kafka, THE System SHALL consume the data and store it in MongoDB collection named price_history with all original fields preserved
5. WHEN storing price data, THE System SHALL include timestamp, symbol, open price, close price, high price, low price, and volume
6. IF the data retrieval fails for a symbol, THEN THE System SHALL log the error and continue with the next symbol

### Requirement 2

**User Story:** As a system administrator, I want to manage a database of stock symbols with their metadata, so that I can control which stocks to track and analyze.

#### Acceptance Criteria

1. WHEN the System starts, THE System SHALL create a MongoDB collection named symbols if it does not exist
2. WHEN storing symbol data, THE System SHALL include symbol code, organ_name, icb_name2, icb_name3, icb_name4, com_type_code, and icb_code fields
3. WHEN loading symbols from JSON file, THE System SHALL parse the file and insert all symbols into the symbols collection
4. WHEN a symbol already exists in the collection, THE System SHALL update the existing record with new metadata
5. WHEN querying symbols for data collection, THE System SHALL retrieve all active symbols from the symbols collection

### Requirement 3

**User Story:** As a system administrator, I want the system to collect news articles for tracked stocks, so that I can perform sentiment analysis on market news.

#### Acceptance Criteria

1. WHEN the News Collector runs on schedule, THE System SHALL retrieve the list of symbols from the symbols collection
2. WHEN collecting news, THE System SHALL retrieve news articles for all symbols in the symbols collection using vnstock library
3. WHEN news articles are retrieved successfully, THE System SHALL publish the articles to Kafka topic named stock_news_raw
4. WHEN news data is published to Kafka, THE System SHALL consume the data and store it in MongoDB collection named news with all original fields preserved
5. WHEN storing news data, THE System SHALL include timestamp, title, content, source, and related stock symbols
6. IF the news retrieval fails for a symbol, THEN THE System SHALL log the error and continue with the next symbol

### Requirement 4

**User Story:** As a data analyst, I want the system to perform quantitative analysis on historical price data, so that I can identify trends and technical patterns.

#### Acceptance Criteria

1. WHEN the AI/ML Engine receives a request for analysis, THE System SHALL retrieve historical price data from price_history collection
2. WHEN analyzing price data, THE System SHALL calculate trend prediction using time-series analysis
3. WHEN analyzing price data, THE System SHALL calculate risk score based on volatility and historical patterns
4. WHEN analyzing price data, THE System SHALL calculate technical score based on technical indicators
5. WHEN analysis is complete, THE System SHALL store results in MongoDB collection named ai_analysis with timestamp and stock symbol

### Requirement 5

**User Story:** As a data analyst, I want the system to perform qualitative analysis on news articles, so that I can understand market sentiment and news impact.

#### Acceptance Criteria

1. WHEN the LLM Engine receives news articles for a stock, THE System SHALL analyze sentiment of each article
2. WHEN analyzing sentiment, THE System SHALL classify sentiment as positive, negative, or neutral with confidence score
3. WHEN analyzing news content, THE System SHALL generate a summary of key points
4. WHEN analyzing news impact, THE System SHALL calculate influence score based on source credibility and content relevance
5. WHEN analysis is complete, THE System SHALL store results in MongoDB collection named llm_analysis with timestamp and stock symbol

### Requirement 6

**User Story:** As an investment advisor, I want the system to aggregate AI/ML and LLM analysis results, so that I can get comprehensive investment recommendations.

#### Acceptance Criteria

1. WHEN the Aggregation Service receives analysis results, THE System SHALL retrieve both ai_analysis and llm_analysis for the specified stock
2. WHEN aggregating results, THE System SHALL combine technical score, risk score, and sentiment score using weighted formula
3. WHEN calculating final score, THE System SHALL generate a final recommendation score between 0 and 100
4. WHEN final score indicates opportunity or risk, THE System SHALL generate alerts with type BUY, WATCH, or RISK
5. WHEN aggregation is complete, THE System SHALL store results in MongoDB collection named final_scores with timestamp

### Requirement 7

**User Story:** As a frontend developer, I want to access stock analysis data through REST API, so that I can display information on the dashboard.

#### Acceptance Criteria

1. WHEN a client requests stock summary, THE API Service SHALL return aggregated data including price, scores, and recommendations
2. WHEN a client requests alert list, THE API Service SHALL return active alerts sorted by priority and timestamp
3. WHEN a client requests historical analysis, THE API Service SHALL return time-series data for specified date range
4. WHEN API receives invalid parameters, THE System SHALL return appropriate HTTP error codes with descriptive messages
5. WHEN API processes requests, THE System SHALL respond within 2 seconds for 95% of requests

### Requirement 8

**User Story:** As a system administrator, I want the system to use Kafka as central data hub, so that I can ensure reliable and scalable data streaming between components.

#### Acceptance Criteria

1. WHEN any component publishes data to Kafka, THE System SHALL ensure message delivery with at-least-once guarantee
2. WHEN consumers read from Kafka topics, THE System SHALL process messages in order within each partition
3. WHEN a consumer fails, THE System SHALL resume processing from last committed offset
4. WHEN Kafka topics are created, THE System SHALL configure appropriate retention policies based on data type
5. WHEN message volume increases, THE System SHALL scale consumers horizontally without data loss

### Requirement 9

**User Story:** As a system administrator, I want to store all data in MongoDB, so that I can have flexible schema and efficient querying for analysis.

#### Acceptance Criteria

1. WHEN the System stores data in MongoDB, THE System SHALL create appropriate indexes for query optimization
2. WHEN querying historical data, THE System SHALL use time-based indexes for efficient retrieval
3. WHEN storing analysis results, THE System SHALL maintain referential integrity between collections using stock symbols
4. WHEN data volume grows, THE System SHALL support data archival for records older than specified retention period
5. WHEN database operations fail, THE System SHALL implement retry logic with exponential backoff

### Requirement 10

**User Story:** As a DevOps engineer, I want to deploy the system using Docker Compose, so that I can easily manage and orchestrate all microservices.

#### Acceptance Criteria

1. WHEN deploying the system, THE System SHALL start all services using Docker Compose configuration
2. WHEN services start, THE System SHALL ensure proper startup order with health checks and dependencies
3. WHEN managing secrets, THE System SHALL use Docker secrets or Vault for sensitive configuration
4. WHEN services communicate, THE System SHALL use Docker network for internal service discovery
5. WHEN updating services, THE System SHALL support rolling updates without complete system downtime

### Requirement 11

**User Story:** As a data engineer, I want to use Apache Airflow in standalone mode to orchestrate and schedule data pipelines, so that I can manage workflows simply without external database dependencies.

#### Acceptance Criteria

1. WHEN deploying Airflow, THE System SHALL run in standalone mode using SQLite as the metadata database
2. WHEN scheduling price data collection, THE System SHALL configure a dedicated DAG to trigger Price Collector every 5 minutes
3. WHEN scheduling news data collection, THE System SHALL configure a dedicated DAG to trigger News Collector every 30 minutes
4. WHEN a task fails in Airflow, THE System SHALL retry the task according to configured retry policy and log failure details
5. WHEN monitoring workflows, THE System SHALL provide Airflow web UI showing task status, execution history, and logs

### Requirement 12

**User Story:** As a data engineer, I want separate DAGs for data collection and analysis workflows, so that I can run them independently with different schedules.

#### Acceptance Criteria

1. WHEN creating the price collection DAG, THE System SHALL define a simple task that collects price data and publishes to Kafka every 5 minutes
2. WHEN creating the news collection DAG, THE System SHALL define a simple task that collects news data and publishes to Kafka every 30 minutes
3. WHEN creating the analysis DAG, THE System SHALL define tasks for AI/ML analysis, LLM analysis, and aggregation that run on a separate schedule
4. WHEN any task in a workflow fails, THE System SHALL log the error and continue with the next scheduled run
5. WHEN workflows execute, THE System SHALL record execution metadata in SQLite database

### Requirement 13

**User Story:** As a system administrator, I want comprehensive error handling and logging, so that I can monitor system health and troubleshoot issues effectively.

#### Acceptance Criteria

1. WHEN any component encounters an error, THE System SHALL log error details with timestamp, component name, and stack trace
2. WHEN critical errors occur, THE System SHALL send notifications to administrators through configured channels
3. WHEN processing data, THE System SHALL validate input data and reject invalid records with descriptive error messages
4. WHEN services start, THE System SHALL log startup status and configuration details
5. WHEN system metrics exceed thresholds, THE System SHALL generate alerts for monitoring systems
