#!/bin/bash

# Stock AI Infrastructure Start Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f "$ENV_FILE" ]; then
        print_error ".env file not found. Please create it from .env.example"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p docker_volumes/{mongodb,redis,kafka,zookeeper,elasticsearch,prometheus,grafana}
    mkdir -p docker_volumes/nginx/{logs,ssl}
    
    # Set proper permissions
    chmod 755 docker_volumes/*
    sudo chown -R $USER:$USER docker_volumes/
    
    print_success "Directories created"
}

# Function to start infrastructure
start_infrastructure() {
    local environment=${1:-development}
    
    print_status "Starting Stock AI infrastructure in $environment mode..."
    
    if [ "$environment" = "development" ]; then
        docker-compose -f $COMPOSE_FILE -f docker-compose.dev.yml up -d
    elif [ "$environment" = "production" ]; then
        docker-compose -f $COMPOSE_FILE -f docker-compose.prod.yml up -d
    else
        docker-compose -f $COMPOSE_FILE up -d
    fi
    
    print_success "Infrastructure started"
}

# Function to wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    local services=(
        "mongodb:27017"
        "redis:6379"
        "elasticsearch:9200"
        "kafka:9093"
        "prometheus:9090"
        "grafana:3000"
        "kibana:5601"
    )
    
    for service in "${services[@]}"; do
        local name=${service%:*}
        local port=${service#*:}
        
        print_status "Waiting for $name to be ready..."
        
        for i in {1..60}; do
            if docker-compose exec $name nc -z localhost $port 2>/dev/null; then
                print_success "$name is ready"
                break
            fi
            
            if [ $i -eq 60 ]; then
                print_warning "$name did not become ready within 60 seconds"
            fi
            
            sleep 1
        done
    done
}

# Function to show service status
show_status() {
    print_status "Service Status:"
    echo ""
    docker-compose ps
    echo ""
    
    print_status "Access URLs:"
    echo "  - Grafana:     http://localhost:3000 (admin/admin123)"
    echo "  - Prometheus:  http://localhost:9090"
    echo "  - Kibana:      http://localhost:5601"
    echo "  - Kafka UI:    http://localhost:8080"
    echo "  - API Gateway: http://localhost:80"
    echo ""
}

# Function to initialize Kafka topics
init_kafka_topics() {
    print_status "Initializing Kafka topics..."
    
    local topics=(
        "stock_prices_raw:3:1"
        "stock_news_raw:3:1"
        "ai_analysis_results:2:1"
        "llm_analysis_results:2:1"
        "stock_alerts:2:1"
    )
    
    for topic_config in "${topics[@]}"; do
        local topic_name=${topic_config%%:*}
        local partitions=${topic_config%:*}
        partitions=${partitions#*:}
        local replication=${topic_config##*:}
        
        print_status "Creating topic: $topic_name"
        
        docker-compose exec kafka kafka-topics.sh \
            --create \
            --bootstrap-server localhost:9093 \
            --topic $topic_name \
            --partitions $partitions \
            --replication-factor $replication \
            --if-not-exists
    done
    
    print_success "Kafka topics initialized"
}

# Function to show logs
show_logs() {
    local service=$1
    if [ -z "$service" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f $service
    fi
}

# Main script logic
case "${1:-start}" in
    "start")
        environment=${2:-development}
        check_prerequisites
        create_directories
        start_infrastructure $environment
        wait_for_services
        init_kafka_topics
        show_status
        ;;
    
    "stop")
        print_status "Stopping infrastructure..."
        docker-compose down
        print_success "Infrastructure stopped"
        ;;
    
    "restart")
        environment=${2:-development}
        print_status "Restarting infrastructure..."
        docker-compose down
        start_infrastructure $environment
        wait_for_services
        show_status
        ;;
    
    "status")
        show_status
        ;;
    
    "logs")
        show_logs $2
        ;;
    
    "clean")
        print_warning "This will remove all containers, volumes, and data!"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Cleaning up..."
            docker-compose down -v --remove-orphans
            docker system prune -f
            print_success "Cleanup completed"
        else
            print_status "Cleanup cancelled"
        fi
        ;;
    
    "backup")
        print_status "Creating backup..."
        cd "$(dirname "$0")"
        ./backup.sh
        cd - > /dev/null
        ;;
    
    "help"|*)
        echo "Stock AI Infrastructure Management Script"
        echo ""
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  start [env]     Start infrastructure (env: development|production)"
        echo "  stop            Stop infrastructure"
        echo "  restart [env]   Restart infrastructure"
        echo "  status          Show service status"
        echo "  logs [service]  Show logs (optionally for specific service)"
        echo "  clean           Remove all containers and volumes (DESTRUCTIVE)"
        echo "  backup          Create backup of data"
        echo "  help            Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 start development"
        echo "  $0 logs mongodb"
        echo "  $0 status"
        ;;
esac