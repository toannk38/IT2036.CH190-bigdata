#!/bin/bash

echo "Running unit tests..."

cd ..

pytest -v -m unit \
    --tb=short \
    --color=yes

echo "✓ Unit tests completed"
