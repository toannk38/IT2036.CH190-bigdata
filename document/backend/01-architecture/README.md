# Architecture Documentation

## Overview

System architecture documentation for the Stock AI Backend System.

## Documents

- **[system-design.md](system-design.md)** - High-level system architecture ✅
- **[data-flow.md](data-flow.md)** - Data pipeline architecture
- **[microservices.md](microservices.md)** - Microservices design
- **[database-design.md](database-design.md)** - MongoDB and Redis schemas
- **[kafka-topics.md](kafka-topics.md)** - Message queue configuration
- **[adr/](adr/)** - Architecture Decision Records

## Architecture Principles

### 1. Microservices Architecture
- Single responsibility per service
- Kafka-based communication
- Independent deployment and scaling

### 2. Event-Driven Design
- Asynchronous processing
- Decoupled components
- Real-time data flow

### 3. Data-Centric Approach
- MongoDB primary storage
- Redis caching layer
- Structured validation

## Implementation Status

### ✅ Implemented
- vnstock API integration
- Price data collection
- Data validation/normalization
- Testing framework

### 📋 Planned
- Infrastructure setup
- AI/ML analysis
- API layer