#!/bin/bash

echo "Running all infrastructure tests..."

cd ..

pytest -v \
    --tb=short \
    --color=yes \
    --cov=. \
    --cov-report=html \
    --cov-report=term

echo "✓ All tests completed"
echo "Coverage report: htmlcov/index.html"
