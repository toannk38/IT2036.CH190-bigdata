# Infrastructure Documentation

## Overview

Infrastructure setup and configuration for the Stock AI Backend System.

## Documents

- **[docker-compose.md](docker-compose.md)** - Docker services configuration
- **[mongodb.md](mongodb.md)** - Database setup and management
- **[kafka.md](kafka.md)** - Message queue setup
- **[redis.md](redis.md)** - Caching setup
- **[monitoring.md](monitoring.md)** - Prometheus and Grafana
- **[networking.md](networking.md)** - Service communication

## Infrastructure Components

### Core Services 📋
- **MongoDB**: Primary database for data storage
- **Apache Kafka**: Message queue for data pipeline
- **Redis**: Caching layer for performance
- **Zookeeper**: Kafka coordination service

### Monitoring Stack 📋
- **Prometheus**: Metrics collection
- **Grafana**: Visualization and dashboards
- **Elasticsearch**: Log aggregation
- **Kibana**: Log analysis interface

### Networking
- **NGINX**: Reverse proxy and load balancer
- **Docker Networks**: Service isolation and communication

## Quick Start

### Development Environment
```bash
# Start core infrastructure
docker-compose -f docker-compose.dev.yml up -d mongodb kafka redis

# Verify services
docker-compose ps

# Check logs
docker-compose logs -f
```

### Production Environment
```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose up -d --scale api=3 --scale kafka-consumer=2
```

## Service Dependencies

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   MongoDB   │    │    Kafka    │    │    Redis    │
└─────────────┘    └─────────────┘    └─────────────┘
       ▲                   ▲                   ▲
       │                   │                   │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Data Services│    │ Processing  │    │ API Services│
└─────────────┘    └─────────────┘    └─────────────┘
```

## Health Checks

### Service Status
```bash
# Check all services
./scripts/health-check.sh

# Individual service checks
curl http://localhost:8081/health  # API health
curl http://localhost:9092         # Kafka health
```

## Troubleshooting

### Common Issues
1. **Port Conflicts**: Check for conflicting services
2. **Memory Issues**: Ensure sufficient RAM allocation
3. **Network Issues**: Verify Docker network configuration
4. **Permission Issues**: Check file permissions and user access