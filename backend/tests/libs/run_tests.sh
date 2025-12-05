#!/bin/bash
# Install test dependencies
pip install pytest pytest-mock

# Run tests
pytest test_vnstock.py -v --tb=short
