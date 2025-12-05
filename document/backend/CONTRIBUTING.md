# Contributing Guidelines

## Development Workflow

### Git Workflow
1. **Branch Naming**: `feature/phase-X-component-name` or `fix/issue-description`
2. **Commits**: Follow conventional commits format
3. **Pull Requests**: Required for all changes

### Code Standards
- **Python**: Follow PEP 8, use black formatter
- **Testing**: Minimum 80% coverage required
- **Documentation**: Update docs for all new features

### Development Setup
```bash
# Clone and setup
git clone <repository>
cd backend
pip install -r requirements.txt

# Run tests before committing
pytest tests/

# Format code
black src/
```

### Review Process
1. All PRs require review
2. Tests must pass
3. Documentation must be updated
4. Follow established patterns from `libs/vnstock` and `services/data_collector`