#!/bin/bash

echo "Running integration tests..."

cd ..

pytest -v -m integration \
    --tb=short \
    --color=yes

echo "✓ Integration tests completed"
