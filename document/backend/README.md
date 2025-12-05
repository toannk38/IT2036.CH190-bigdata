# Stock AI Backend System - Technical Documentation

## Project Overview

A comprehensive AI-powered stock analysis and recommendation system for Vietnamese stock market, built with microservices architecture using Python, MongoDB, Kafka, and machine learning models.

## System Status

### ✅ **Completed Components**
- **Phase 0**: Project Foundation - Complete
- **Phase 2.1**: vnstock Integration Library - Complete  
- **Phase 2.2**: Price Data Collector Service - Complete
- **Phase 9.1**: Unit Testing Framework - Complete

### 🚧 **In Progress**
- **Phase 1**: Infrastructure Setup (Docker, Kafka, MongoDB)

### 📋 **Pending**
- News Data Collector
- AI/ML Analysis Engine
- LLM News Analysis
- API Layer

## Architecture Overview

The system follows a microservices architecture with the following layers:

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA SOURCES LAYER                           │
│                   ┌──────────────────┐                          │
│                   │  vnstock Library │                          │
│                   └────────┬─────────┘                          │
└────────────────────────────┼─────────────────────────────────────┘
                             │
┌────────────────────────────┼─────────────────────────────────────┐
│               DATA PIPELINE LAYER                                │
│  ┌────────────────┐        │        ┌────────────────┐          │
│  │ Price Collector│◄───────┴───────►│ News Collector │          │
│  └───────┬────────┘                 └───────┬────────┘          │
│          │                                  │                   │
│          │         ┌──────────────────┐     │                   │
│          └────────►│   Apache Kafka   │◄────┘                   │
│                    │  - stock_prices  │                         │
│                    │  - stock_news    │                         │
│                    └────────┬─────────┘                         │
└─────────────────────────────┼─────────────────────────────────────┘
                              │
┌─────────────────────────────┼─────────────────────────────────────┐
│                    STORAGE LAYER                                 │
│                    ┌────────▼─────────┐                          │
│                    │     MongoDB      │                          │
│                    │  - stocks        │                          │
│                    │  - price_history │                          │
│                    │  - news          │                          │
│                    │  - ai_analysis   │                          │
│                    │  - final_scores  │                          │
│                    └──────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- Git

### Development Setup

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Tests**
   ```bash
   pytest tests/
   ```

4. **Start Services** (When infrastructure is ready)
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

## Documentation Structure

- **[01-architecture/](01-architecture/)** - System design and architecture decisions
- **[02-development/](02-development/)** - Development setup and guidelines  
- **[03-services/](03-services/)** - Individual service documentation
- **[04-infrastructure/](04-infrastructure/)** - Infrastructure setup and configuration
- **[10-reference/](10-reference/)** - API references and data models

## Key Technologies

- **Backend**: Python 3.9+, FastAPI
- **Message Queue**: Apache Kafka
- **Database**: MongoDB
- **Caching**: Redis  
- **ML/AI**: TensorFlow, PyTorch, scikit-learn
- **Containerization**: Docker, Docker Compose
- **Testing**: pytest
- **Monitoring**: Prometheus, Grafana

## Current Implementation Status

Based on code analysis, the following components are implemented:

### libs/vnstock/ ✅
- Complete vnstock API wrapper with rate limiting
- Data models: StockPrice, StockNews, StockListing
- Error handling: VnstockError, RateLimitError, DataNotFoundError
- Caching mechanism for API responses

### services/data_collector/ ✅  
- Price collection service with Kafka integration
- Data validation and normalization
- Comprehensive error handling and logging
- Configurable collection intervals

### tests/ ✅
- Unit tests for vnstock library
- Integration tests for data collector
- Test fixtures and mock services
- pytest configuration

## Next Steps

1. **Complete Infrastructure Setup** (Phase 1)
   - Docker Compose configuration
   - MongoDB, Kafka, Redis containers
   - Network configuration

2. **Implement News Collector** (Phase 2.3)
3. **Build AI/ML Analysis Engine** (Phase 3)
4. **Develop API Layer** (Phase 6)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and workflow.

## License

[License information]