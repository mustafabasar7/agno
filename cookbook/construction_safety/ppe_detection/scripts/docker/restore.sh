#!/bin/bash
# Restore script for PPE Detection application data

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

# Check arguments
if [ -z "$1" ]; then
    echo -e "${RED}Error: Backup directory not specified${NC}"
    echo ""
    echo "Usage: $0 <backup_directory>"
    echo ""
    echo "Example: $0 ./backups/ppe_detection_backup_20250118_120000"
    exit 1
fi

BACKUP_DIR="$1"

if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}Error: Backup directory not found: $BACKUP_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}PPE Detection Restore Script${NC}"
echo "========================================"
echo ""
echo -e "${YELLOW}Restoring from: $BACKUP_DIR${NC}"
echo ""

# Show backup info
if [ -f "$BACKUP_DIR/backup_info.txt" ]; then
    cat "$BACKUP_DIR/backup_info.txt"
    echo ""
fi

# Confirmation
echo -e "${RED}WARNING: This will replace all current data!${NC}"
read -p "Are you sure you want to continue? (yes/no) " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Restore cancelled"
    exit 0
fi

# Ensure services are running
echo -e "${BLUE}Starting services if not running...${NC}"
docker-compose up -d db redis
sleep 5

# Restore database
if [ -f "$BACKUP_DIR/database.sql.gz" ]; then
    echo -e "${BLUE}[1/4] Restoring PostgreSQL database...${NC}"

    # Drop existing connections
    docker-compose exec -T db psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'ppe_detection' AND pid <> pg_backend_pid();"

    # Drop and recreate database
    docker-compose exec -T db psql -U postgres -c "DROP DATABASE IF EXISTS ppe_detection;"
    docker-compose exec -T db psql -U postgres -c "CREATE DATABASE ppe_detection;"

    # Restore dump
    gunzip -c "$BACKUP_DIR/database.sql.gz" | docker-compose exec -T db psql -U postgres ppe_detection

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Database restore completed${NC}"
    else
        echo -e "${RED}✗ Database restore failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ No database backup found${NC}"
fi

# Restore Redis data
if [ -f "$BACKUP_DIR/redis_dump.rdb" ]; then
    echo -e "${BLUE}[2/4] Restoring Redis data...${NC}"

    docker-compose stop redis
    docker cp "$BACKUP_DIR/redis_dump.rdb" ppe_detection_redis:/data/dump.rdb
    docker-compose start redis
    sleep 3

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Redis restore completed${NC}"
    else
        echo -e "${YELLOW}⚠ Redis restore failed (non-critical)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ No Redis backup found${NC}"
fi

# Restore application data
if [ -f "$BACKUP_DIR/data.tar.gz" ]; then
    echo -e "${BLUE}[3/4] Restoring application data...${NC}"

    # Backup current data
    if [ -d "./data" ]; then
        mv ./data "./data.backup.$(date +%Y%m%d_%H%M%S)"
    fi

    tar -xzf "$BACKUP_DIR/data.tar.gz"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Application data restore completed${NC}"
    else
        echo -e "${YELLOW}⚠ Application data restore failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠ No application data backup found${NC}"
fi

# Restore configuration
if [ -f "$BACKUP_DIR/.env.backup" ]; then
    echo -e "${BLUE}[4/4] Restoring configuration...${NC}"

    if [ -f ".env" ]; then
        mv .env ".env.backup.$(date +%Y%m%d_%H%M%S)"
    fi

    cp "$BACKUP_DIR/.env.backup" .env
    echo -e "${GREEN}✓ Configuration restore completed${NC}"
else
    echo -e "${YELLOW}⚠ No configuration backup found${NC}"
fi

# Restart all services
echo ""
echo -e "${BLUE}Restarting all services...${NC}"
docker-compose restart

echo ""
echo -e "${GREEN}========================================"
echo "✓ Restore completed successfully!"
echo "========================================${NC}"
echo ""
echo "Services are restarting. Check logs with:"
echo "  ./scripts/docker/logs.sh"
echo ""
