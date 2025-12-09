.PHONY: help setup start stop restart logs clean test

help:
	@echo "Vietnam Stock AI Backend - Makefile Commands"
	@echo ""
	@echo "setup          - Setup environment and install dependencies"
	@echo "start          - Start all services"
	@echo "stop           - Stop all services"
	@echo "restart        - Restart all services"
	@echo "logs           - View logs from all services"
	@echo "logs-service   - View logs from specific service (make logs-service SERVICE=api)"
	@echo "init-kafka     - Initialize Kafka topics"
	@echo "load-symbols   - Load symbols from JSON (make load-symbols FILE=data/symbols.json)"
	@echo "test           - Run all tests"
	@echo "test-unit      - Run unit tests only"
	@echo "test-property  - Run property-based tests only"
	@echo "clean          - Clean up containers and volumes"
	@echo "shell-api      - Open shell in API container"
	@echo "shell-airflow  - Open shell in Airflow container"

setup:
	@echo "Setting up environment..."
	cp -n .env.template .env || true
	pip install -r requirements.txt
	@echo "Setup complete! Edit .env file with your configuration."

start:
	@echo "Starting all services..."
	docker-compose up -d
	@echo "Services started. Waiting for health checks..."
	sleep 10
	@echo "Access Airflow at http://localhost:8080 (admin/admin)"
	@echo "Access API docs at http://localhost:8000/docs"

stop:
	@echo "Stopping all services..."
	docker-compose down

restart:
	@echo "Restarting all services..."
	docker-compose restart

logs:
	docker-compose logs -f

logs-service:
	docker-compose logs -f $(SERVICE)

init-kafka:
	@echo "Initializing Kafka topics..."
	chmod +x scripts/create_kafka_topics.sh
	./scripts/create_kafka_topics.sh

load-symbols:
	@echo "Loading symbols from $(FILE)..."
	python scripts/load_symbols.py $(FILE)

test:
	pytest tests/ -v

test-unit:
	pytest tests/ -v -m "not property"

test-property:
	pytest tests/ -v -k "property"

clean:
	@echo "Cleaning up..."
	docker-compose down -v
	rm -rf __pycache__ .pytest_cache .hypothesis
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete!"

shell-api:
	docker exec -it api-service /bin/bash

shell-airflow:
	docker exec -it airflow /bin/bash

shell-consumer:
	docker exec -it kafka-consumer /bin/bash
