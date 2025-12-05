# Development Documentation

## Overview

Development setup and guidelines for the Stock AI Backend System.

## Documents

- **[environment-setup.md](environment-setup.md)** - Local development environment
- **[docker-guide.md](docker-guide.md)** - Docker development workflow
- **[coding-standards.md](coding-standards.md)** - Code style and conventions
- **[git-workflow.md](git-workflow.md)** - Branching and commit guidelines
- **[testing-guide.md](testing-guide.md)** - Testing strategy and practices ✅
- **[debugging.md](debugging.md)** - Common issues and solutions

## Quick Start

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- Git

### Setup
```bash
# Clone repository
git clone <repository-url>
cd backend

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Start development environment (when ready)
docker-compose -f docker-compose.dev.yml up -d
```

## Development Standards

### Code Quality
- **Formatting**: Use black for Python code formatting
- **Linting**: Use flake8 for code linting
- **Type Hints**: Use type annotations where applicable
- **Testing**: Minimum 80% test coverage required

### Git Workflow
- **Branching**: Feature branches from main
- **Commits**: Conventional commit format
- **Reviews**: All changes require pull request review

### Documentation
- Update documentation for all new features
- Include docstrings for all public functions
- Maintain README files for each service