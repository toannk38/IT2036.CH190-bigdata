#!/bin/bash

echo "Setting up test environment..."

# Check if infrastructure is running
cd ../../../../infrastructure

if ! docker-compose ps | grep -q "Up"; then
    echo "Starting infrastructure services..."
    docker-compose up -d
    echo "Waiting for services to be ready..."
    sleep 30
fi

# Install test dependencies
cd ../backend/tests/infrastructure
pip install -r requirements.txt

echo "✓ Test environment setup complete"
