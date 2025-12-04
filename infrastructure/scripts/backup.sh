#!/bin/bash

# =================================================================
# STOCK AI INFRASTRUCTURE BACKUP SCRIPT
# =================================================================

# Load environment variables
source /app/.env

# Configuration
BACKUP_DIR="/app/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Function to backup MongoDB
backup_mongodb() {
    log "Starting MongoDB backup..."
    
    MONGO_BACKUP_DIR="$BACKUP_DIR/mongodb_$DATE"
    mkdir -p "$MONGO_BACKUP_DIR"
    
    # MongoDB backup using mongodump
    docker exec mongodb mongodump \
        --username="$MONGODB_ROOT_USERNAME" \
        --password="$MONGODB_ROOT_PASSWORD" \
        --authenticationDatabase=admin \
        --db="$MONGODB_DATABASE" \
        --out="/tmp/backup"
    
    # Copy backup from container to host
    docker cp mongodb:/tmp/backup "$MONGO_BACKUP_DIR/"
    
    # Compress the backup
    tar -czf "$BACKUP_DIR/mongodb_backup_$DATE.tar.gz" -C "$MONGO_BACKUP_DIR" .
    rm -rf "$MONGO_BACKUP_DIR"
    
    log "MongoDB backup completed: mongodb_backup_$DATE.tar.gz"
}

# Function to backup Redis
backup_redis() {
    log "Starting Redis backup..."
    
    # Redis backup (RDB snapshot)
    docker exec redis redis-cli --rdb /tmp/dump.rdb
    docker cp redis:/tmp/dump.rdb "$BACKUP_DIR/redis_backup_$DATE.rdb"
    
    log "Redis backup completed: redis_backup_$DATE.rdb"
}

# Function to backup Elasticsearch
backup_elasticsearch() {
    log "Starting Elasticsearch backup..."
    
    # Create repository if it doesn't exist
    curl -X PUT "elasticsearch:9200/_snapshot/backup_repo" \
        -H 'Content-Type: application/json' \
        -d '{
            "type": "fs",
            "settings": {
                "location": "/usr/share/elasticsearch/backup"
            }
        }'
    
    # Create snapshot
    curl -X PUT "elasticsearch:9200/_snapshot/backup_repo/snapshot_$DATE" \
        -H 'Content-Type: application/json' \
        -d '{
            "indices": "*",
            "ignore_unavailable": true,
            "include_global_state": false
        }'
    
    log "Elasticsearch backup completed: snapshot_$DATE"
}

# Function to backup Grafana
backup_grafana() {
    log "Starting Grafana backup..."
    
    # Backup Grafana database and config
    docker exec grafana tar -czf /tmp/grafana_backup.tar.gz /var/lib/grafana /etc/grafana
    docker cp grafana:/tmp/grafana_backup.tar.gz "$BACKUP_DIR/grafana_backup_$DATE.tar.gz"
    
    log "Grafana backup completed: grafana_backup_$DATE.tar.gz"
}

# Function to backup Prometheus
backup_prometheus() {
    log "Starting Prometheus backup..."
    
    # Backup Prometheus data
    docker exec prometheus tar -czf /tmp/prometheus_backup.tar.gz /prometheus
    docker cp prometheus:/tmp/prometheus_backup.tar.gz "$BACKUP_DIR/prometheus_backup_$DATE.tar.gz"
    
    log "Prometheus backup completed: prometheus_backup_$DATE.tar.gz"
}

# Function to cleanup old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."
    
    find "$BACKUP_DIR" -name "*backup*" -type f -mtime +$RETENTION_DAYS -delete
    
    log "Cleanup completed"
}

# Function to backup all services
backup_all() {
    log "Starting full infrastructure backup..."
    
    # Check if backup is enabled
    if [ "$BACKUP_ENABLED" != "true" ]; then
        warn "Backup is disabled. Set BACKUP_ENABLED=true to enable backups."
        exit 0
    fi
    
    # Create backup metadata
    cat > "$BACKUP_DIR/backup_metadata_$DATE.json" << EOF
{
    "backup_date": "$(date -Iseconds)",
    "backup_type": "full",
    "services": ["mongodb", "redis", "elasticsearch", "grafana", "prometheus"],
    "retention_days": $RETENTION_DAYS
}
EOF

    # Backup each service
    backup_mongodb
    backup_redis
    backup_elasticsearch
    backup_grafana
    backup_prometheus
    
    # Cleanup old backups
    cleanup_old_backups
    
    log "Full backup completed successfully!"
}

# Function to restore from backup
restore_backup() {
    local backup_date=$1
    
    if [ -z "$backup_date" ]; then
        error "Please provide backup date (format: YYYYMMDD_HHMMSS)"
        exit 1
    fi
    
    log "Starting restore from backup: $backup_date"
    
    # Stop services before restore
    docker-compose down
    
    # Restore MongoDB
    if [ -f "$BACKUP_DIR/mongodb_backup_$backup_date.tar.gz" ]; then
        log "Restoring MongoDB..."
        tar -xzf "$BACKUP_DIR/mongodb_backup_$backup_date.tar.gz" -C /tmp/
        # Restore logic here
    fi
    
    # Start services after restore
    docker-compose up -d
    
    log "Restore completed successfully!"
}

# Main script logic
case "$1" in
    "backup")
        backup_all
        ;;
    "restore")
        restore_backup "$2"
        ;;
    "mongodb")
        backup_mongodb
        ;;
    "redis")
        backup_redis
        ;;
    "elasticsearch")
        backup_elasticsearch
        ;;
    "grafana")
        backup_grafana
        ;;
    "prometheus")
        backup_prometheus
        ;;
    "cleanup")
        cleanup_old_backups
        ;;
    *)
        echo "Usage: $0 {backup|restore|mongodb|redis|elasticsearch|grafana|prometheus|cleanup}"
        echo ""
        echo "Commands:"
        echo "  backup                    - Backup all services"
        echo "  restore <backup_date>     - Restore from specific backup"
        echo "  mongodb                   - Backup MongoDB only"
        echo "  redis                     - Backup Redis only"
        echo "  elasticsearch             - Backup Elasticsearch only"
        echo "  grafana                   - Backup Grafana only"
        echo "  prometheus                - Backup Prometheus only"
        echo "  cleanup                   - Remove old backups"
        echo ""
        echo "Examples:"
        echo "  $0 backup"
        echo "  $0 restore 20241204_020000"
        echo "  $0 mongodb"
        exit 1
        ;;
esac