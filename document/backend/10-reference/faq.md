# Frequently Asked Questions

## General Questions

### Q: What is the Stock AI Backend System?
**A:** A comprehensive AI-powered system for analyzing Vietnamese stock market data, providing technical analysis, sentiment analysis of news, and generating investment recommendations.

### Q: What data sources does the system use?
**A:** The primary data source is the vnstock library, which provides access to Vietnamese stock exchanges (HOSE, HNX, UPCOM). The system also integrates with OpenAI for news sentiment analysis.

### Q: What programming language is the system built in?
**A:** The system is built primarily in Python 3.9+, using frameworks like FastAPI for APIs, Kafka for messaging, and MongoDB for data storage.

## Technical Questions

### Q: How does the data collection work?
**A:** The data collector service uses the vnstock library to fetch stock prices and news data, validates and normalizes the data, then publishes it to Kafka topics for downstream processing.

### Q: What is the system architecture?
**A:** The system follows a microservices architecture with:
- Data Collector Service (✅ implemented)
- Kafka Consumer Service (📋 planned)
- AI Analysis Service (📋 planned)
- LLM Analysis Service (📋 planned)
- Aggregation Service (📋 planned)
- API Service (📋 planned)

### Q: How is data stored?
**A:** Data is stored in MongoDB with the following collections:
- `stocks`: Stock metadata
- `price_history`: Historical price data
- `news`: News articles
- `ai_analysis`: Technical analysis results
- `llm_analysis`: Sentiment analysis results
- `final_scores`: Aggregated recommendations

### Q: What caching strategy is used?
**A:** Multi-layer caching:
- L1: In-memory caching in vnstock client (✅ implemented)
- L2: Redis for application-level caching (📋 planned)
- L3: MongoDB for persistent storage

## Development Questions

### Q: How do I set up the development environment?
**A:** 
1. Install Python 3.9+, Docker, and Git
2. Clone the repository
3. Create virtual environment: `python -m venv venv`
4. Install dependencies: `pip install -r requirements.txt`
5. Run tests: `pytest tests/`

### Q: What testing framework is used?
**A:** The system uses pytest for unit and integration testing, with comprehensive test coverage for implemented components.

### Q: How do I run the existing services?
**A:** Currently implemented services:
```bash
# Run data collector (requires Kafka setup)
cd services/data_collector
python -m src.main

# Run tests
pytest tests/libs/test_vnstock.py
pytest tests/test_services/data_collector/
```

### Q: What code style guidelines are followed?
**A:** 
- **Formatting**: Black for Python code formatting
- **Linting**: Flake8 for code quality
- **Type Hints**: Type annotations where applicable
- **Documentation**: Docstrings for all public functions

## Configuration Questions

### Q: What environment variables are required?
**A:** Key environment variables:
```bash
# Required for data collection
VNSTOCK_SOURCE=VCI
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Required for LLM analysis (when implemented)
OPENAI_API_KEY=your-key-here

# Required for database (when implemented)
MONGODB_URI=mongodb://localhost:27017
```

### Q: How do I configure rate limiting?
**A:** Rate limiting is configured via environment variables:
```bash
VNSTOCK_RATE_LIMIT=0.5  # Seconds between vnstock API calls
LLM_RATE_LIMIT=1.0      # Requests per second for LLM API
```

### Q: Can I use different data sources?
**A:** Yes, vnstock supports multiple sources:
- `VCI`: Viet Capital Securities (default)
- `TCBS`: Techcom Securities  
- `SSI`: Saigon Securities Inc

Set via: `VNSTOCK_SOURCE=TCBS`

## Operational Questions

### Q: How do I monitor the system?
**A:** Monitoring is planned with:
- Prometheus for metrics collection
- Grafana for dashboards
- ELK stack for log analysis
- Health check endpoints for service status

### Q: What happens if vnstock API is unavailable?
**A:** The system implements error handling:
- Rate limiting prevents API abuse
- Caching reduces dependency on external APIs
- Custom exceptions handle different error types
- Retry logic with exponential backoff

### Q: How is data quality ensured?
**A:** Data quality measures include:
- Validation rules in `DataValidator` (✅ implemented)
- Business logic checks (high >= low, volume >= 0)
- Data normalization in `DataNormalizer` (✅ implemented)
- Error logging and monitoring

## Performance Questions

### Q: How many stocks can the system handle?
**A:** The system is designed to handle:
- 1000+ stocks processed per minute
- Horizontal scaling via Kafka partitioning
- Parallel processing across multiple consumers

### Q: What are the performance targets?
**A:** Target performance metrics:
- **Throughput**: 1000+ stocks/minute
- **Latency**: < 10 seconds end-to-end
- **Availability**: 99.9% uptime
- **Data Quality**: > 95% accuracy

### Q: How does caching improve performance?
**A:** Caching reduces:
- API calls to vnstock (1-hour cache for symbols)
- Database queries (Redis caching)
- Computation overhead (cached analysis results)

## Troubleshooting

### Q: Why am I getting rate limit errors?
**A:** Rate limit solutions:
1. Increase `VNSTOCK_RATE_LIMIT` value
2. Check vnstock API status
3. Verify no other processes are using the API
4. Monitor API usage patterns

### Q: How do I debug Kafka connection issues?
**A:** Kafka troubleshooting:
1. Verify `KAFKA_BOOTSTRAP_SERVERS` configuration
2. Check Kafka cluster health: `docker-compose ps`
3. Review Kafka logs: `docker-compose logs kafka`
4. Test connectivity: `telnet localhost 9092`

### Q: What if tests are failing?
**A:** Test troubleshooting:
1. Ensure virtual environment is activated
2. Install test dependencies: `pip install pytest`
3. Check Python version: `python --version` (should be 3.9+)
4. Run specific test: `pytest tests/libs/test_vnstock.py -v`

### Q: How do I handle memory issues?
**A:** Memory optimization:
1. Reduce `PRICE_HISTORY_DAYS` for data collection
2. Implement batch processing for large datasets
3. Monitor memory usage: `docker stats`
4. Increase Docker memory allocation

## Future Development

### Q: What features are planned next?
**A:** Development roadmap:
1. **Phase 1**: Infrastructure setup (Docker, MongoDB, Kafka)
2. **Phase 2**: AI/ML analysis engine
3. **Phase 3**: LLM news analysis
4. **Phase 4**: API layer and aggregation service

### Q: How can I contribute to the project?
**A:** Contribution guidelines:
1. Follow the established code patterns from `libs/vnstock` and `services/data_collector`
2. Write comprehensive tests for new features
3. Update documentation for changes
4. Follow the Git workflow with feature branches and pull requests

### Q: Will the system support other markets?
**A:** Currently focused on Vietnamese markets, but the architecture is designed to be extensible for other markets by:
- Adding new data source adapters
- Extending the vnstock wrapper pattern
- Configuring market-specific analysis parameters

### Q: How will real-time features work?
**A:** Real-time capabilities will include:
- WebSocket connections for live price updates
- Real-time alert generation
- Streaming analysis results
- Live dashboard updates

## Security Questions

### Q: How are API keys secured?
**A:** Security measures:
- Environment variables for sensitive configuration
- No hardcoded secrets in code
- Planned encryption for production secrets
- Regular key rotation procedures

### Q: What authentication will the API use?
**A:** Planned authentication methods:
- JWT tokens for user sessions
- API keys for service-to-service communication
- OAuth 2.0 for third-party integrations
- Role-based access control (RBAC)

### Q: How is data privacy handled?
**A:** Privacy considerations:
- No personal user data stored
- Public market data only
- Compliance with data protection regulations
- Audit logging for data access