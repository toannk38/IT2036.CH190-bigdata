# Environment Setup

## Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows with WSL2
- **Python**: 3.9 or higher
- **Docker**: 20.10+ with Docker Compose
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Storage**: 20GB free space

### Required Tools
```bash
# Python and pip
python3 --version  # Should be 3.9+
pip3 --version

# Docker
docker --version
docker-compose --version

# Git
git --version
```

## Python Environment Setup

### Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Development Dependencies
```bash
# Install development tools
pip install black flake8 mypy pytest pytest-cov

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

## IDE Configuration

### VSCode Settings
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests/"]
}
```

### PyCharm Configuration
- Set Python interpreter to virtual environment
- Enable pytest as test runner
- Configure black as code formatter
- Enable flake8 for linting

## Environment Variables

### Development Configuration
```bash
# Copy example environment file
cp .env.example .env

# Edit with your settings
vim .env
```

### Required Variables
```bash
# vnstock Configuration
VNSTOCK_SOURCE=VCI
VNSTOCK_RATE_LIMIT=0.5

# Kafka Configuration (when infrastructure is ready)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_PRICE_TOPIC=stock_prices_raw

# MongoDB Configuration (when infrastructure is ready)
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=stock_ai

# Redis Configuration (when infrastructure is ready)
REDIS_URL=redis://localhost:6379

# Logging
LOG_LEVEL=INFO
```

## Verification

### Test Installation
```bash
# Run unit tests
pytest tests/libs/test_vnstock.py -v

# Run data collector tests
pytest tests/test_services/data_collector/ -v

# Check code formatting
black --check src/

# Run linting
flake8 src/
```

### Import Tests
```python
# Test vnstock library
from libs.vnstock import VnstockClient
client = VnstockClient()
symbols = client.get_all_symbols()
print(f"Found {len(symbols)} symbols")

# Test data collector
from services.data_collector.src.collectors import PriceCollector
print("Data collector imports successfully")
```