# Stock AI Infrastructure Makefile

.DEFAULT_GOAL := help
.PHONY: help start stop restart status logs clean backup dev prod setup

# Colors
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

help: ## Show this help message
	@echo "Stock AI Infrastructure Management"
	@echo "================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make dev          # Start development environment"
	@echo "  make prod         # Start production environment"
	@echo "  make logs         # Show logs from all services"
	@echo "  make backup       # Create backup"

setup: ## Initial setup - create directories and set permissions
	@echo "$(GREEN)Setting up infrastructure directories...$(RESET)"
	@mkdir -p docker_volumes/{mongodb,redis,kafka,zookeeper,elasticsearch,prometheus,grafana,nginx/logs}
	@mkdir -p docker_backups
	@chmod +x scripts/*.sh
	@sudo chown -R $$USER:$$USER docker_volumes/
	@chmod -R 755 docker_volumes/
	@echo "$(GREEN)Setup completed!$(RESET)"

dev: ## Start development environment
	@echo "$(GREEN)Starting development environment...$(RESET)"
	@./scripts/manage.sh start development

prod: ## Start production environment
	@echo "$(GREEN)Starting production environment...$(RESET)"
	@./scripts/manage.sh start production

start: dev ## Alias for dev (start development environment)

stop: ## Stop all services
	@echo "$(YELLOW)Stopping all services...$(RESET)"
	@./scripts/manage.sh stop

restart: ## Restart all services (development)
	@echo "$(YELLOW)Restarting services...$(RESET)"
	@./scripts/manage.sh restart development

restart-prod: ## Restart all services (production)
	@echo "$(YELLOW)Restarting production services...$(RESET)"
	@./scripts/manage.sh restart production

status: ## Show service status
	@./scripts/manage.sh status

logs: ## Show logs from all services
	@docker-compose logs -f

logs-mongodb: ## Show MongoDB logs
	@docker-compose logs -f mongodb

logs-redis: ## Show Redis logs
	@docker-compose logs -f redis

logs-kafka: ## Show Kafka logs
	@docker-compose logs -f kafka

logs-nginx: ## Show Nginx logs
	@docker-compose logs -f nginx

logs-prometheus: ## Show Prometheus logs
	@docker-compose logs -f prometheus

logs-grafana: ## Show Grafana logs
	@docker-compose logs -f grafana

logs-elasticsearch: ## Show Elasticsearch logs
	@docker-compose logs -f elasticsearch

logs-kibana: ## Show Kibana logs
	@docker-compose logs -f kibana

backup: ## Create backup of all data
	@echo "$(GREEN)Creating backup...$(RESET)"
	@./scripts/manage.sh backup

backup-list: ## List available backups
	@./scripts/backup.sh list

clean: ## Remove all containers and volumes (DESTRUCTIVE!)
	@echo "$(RED)WARNING: This will delete all data!$(RESET)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo ""; \
		echo "$(RED)Cleaning up...$(RESET)"; \
		./scripts/manage.sh clean; \
	else \
		echo ""; \
		echo "$(GREEN)Cleanup cancelled$(RESET)"; \
	fi

ps: ## Show running containers
	@docker-compose ps

top: ## Show container resource usage
	@docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.PIDs}}"

health: ## Check health of all services
	@echo "$(GREEN)Checking service health...$(RESET)"
	@echo ""
	@echo "MongoDB:"
	@docker-compose exec mongodb mongosh --eval "db.runCommand('ping')" --quiet 2>/dev/null || echo "❌ MongoDB not responding"
	@echo ""
	@echo "Redis:"
	@docker-compose exec redis redis-cli -a $${REDIS_PASSWORD:-redis123} ping 2>/dev/null || echo "❌ Redis not responding"
	@echo ""
	@echo "Kafka:"
	@docker-compose exec kafka kafka-broker-api-versions.sh --bootstrap-server localhost:9093 >/dev/null 2>&1 && echo "✅ Kafka OK" || echo "❌ Kafka not responding"
	@echo ""
	@echo "Elasticsearch:"
	@curl -s -o /dev/null -w "Elasticsearch: %{http_code}\n" http://localhost:9200/_cluster/health || echo "❌ Elasticsearch not responding"
	@echo ""

init-kafka: ## Initialize Kafka topics
	@echo "$(GREEN)Initializing Kafka topics...$(RESET)"
	@docker-compose exec kafka kafka-topics.sh --create --bootstrap-server localhost:9093 --topic stock_prices_raw --partitions 3 --replication-factor 1 --if-not-exists
	@docker-compose exec kafka kafka-topics.sh --create --bootstrap-server localhost:9093 --topic stock_news_raw --partitions 3 --replication-factor 1 --if-not-exists
	@docker-compose exec kafka kafka-topics.sh --create --bootstrap-server localhost:9093 --topic ai_analysis_results --partitions 2 --replication-factor 1 --if-not-exists
	@docker-compose exec kafka kafka-topics.sh --create --bootstrap-server localhost:9093 --topic llm_analysis_results --partitions 2 --replication-factor 1 --if-not-exists
	@docker-compose exec kafka kafka-topics.sh --create --bootstrap-server localhost:9093 --topic stock_alerts --partitions 2 --replication-factor 1 --if-not-exists
	@echo "$(GREEN)Kafka topics initialized!$(RESET)"

kafka-topics: ## List Kafka topics
	@docker-compose exec kafka kafka-topics.sh --bootstrap-server localhost:9093 --list

shell-mongodb: ## Open MongoDB shell
	@docker-compose exec mongodb mongosh -u admin -p $${MONGODB_ROOT_PASSWORD:-admin123} --authenticationDatabase admin

shell-redis: ## Open Redis CLI
	@docker-compose exec redis redis-cli -a $${REDIS_PASSWORD:-redis123}

update-images: ## Pull latest Docker images
	@echo "$(GREEN)Pulling latest images...$(RESET)"
	@docker-compose pull

rebuild: ## Rebuild and restart services
	@echo "$(YELLOW)Rebuilding services...$(RESET)"
	@docker-compose down
	@docker-compose build --no-cache
	@docker-compose up -d

# Quick access URLs
urls: ## Show service URLs
	@echo "$(GREEN)Service Access URLs:$(RESET)"
	@echo "================================="
	@echo "📊 Grafana:      http://localhost:3000 (admin/StockAI@Grafana2024)"
	@echo "📈 Prometheus:   http://localhost:9090"
	@echo "📋 Kibana:       http://localhost:5601"
	@echo "📬 Kafka UI:     http://localhost:8080"
	@echo "🔍 Elasticsearch: http://localhost:9200"
	@echo ""
	@echo "$(YELLOW)Database Connections:$(RESET)"
	@echo "🗄️  MongoDB:     mongodb://admin:StockAI@MongoDB2024@localhost:27017/stock_ai"
	@echo "⚡ Redis:       redis://:StockAI@Redis2024@localhost:6379/0"
	@echo "📡 Kafka:       localhost:9092"

# Development helpers
dev-reset: ## Reset development environment (clean + setup + start)
	@echo "$(YELLOW)Resetting development environment...$(RESET)"
	@$(MAKE) clean
	@$(MAKE) setup
	@$(MAKE) dev

monitoring: ## Open monitoring dashboards
	@echo "$(GREEN)Opening monitoring dashboards...$(RESET)"
	@which xdg-open >/dev/null && xdg-open http://localhost:3000 || open http://localhost:3000 || echo "Please open http://localhost:3000 manually"