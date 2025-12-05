# Reference Documentation

## Overview

Technical reference documentation for the Stock AI Backend System.

## Documents

- **[glossary.md](glossary.md)** - Terms and definitions
- **[external-apis.md](external-apis.md)** - vnstock and other APIs
- **[data-models.md](data-models.md)** - Data structures and schemas ✅
- **[configuration-reference.md](configuration-reference.md)** - All config options
- **[faq.md](faq.md)** - Frequently asked questions

## Quick Reference

### Data Models ✅
- **StockPrice**: Price data structure
- **StockNews**: News article structure  
- **StockListing**: Stock metadata structure

### API Endpoints 📋
- `/api/v1/stocks/{symbol}/summary`
- `/api/v1/stocks/{symbol}/analysis`
- `/api/v1/alerts/list`

### Configuration
- Environment variables for all services
- Docker Compose configuration
- Database connection settings

### External Dependencies
- **vnstock**: Vietnamese stock data API
- **OpenAI**: LLM analysis service
- **MongoDB**: Primary database
- **Kafka**: Message queue system