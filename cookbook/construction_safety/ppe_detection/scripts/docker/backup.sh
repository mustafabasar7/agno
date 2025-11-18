#!/bin/bash
# Backup script for PPE Detection application data

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

# Configuration
BACKUP_DIR="${1:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="ppe_detection_backup_${TIMESTAMP}"

echo -e "${GREEN}PPE Detection Backup Script${NC}"
echo "========================================"
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR/$BACKUP_NAME"

echo -e "${YELLOW}Backing up to: $BACKUP_DIR/$BACKUP_NAME${NC}"
echo ""

# Backup database
echo -e "${BLUE}[1/4] Backing up PostgreSQL database...${NC}"
docker-compose exec -T db pg_dump -U postgres ppe_detection | gzip > "$BACKUP_DIR/$BACKUP_NAME/database.sql.gz"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database backup completed${NC}"
else
    echo -e "${RED}✗ Database backup failed${NC}"
    exit 1
fi

# Backup Redis data
echo -e "${BLUE}[2/4] Backing up Redis data...${NC}"
docker-compose exec -T redis redis-cli --raw SAVE
docker cp ppe_detection_redis:/data/dump.rdb "$BACKUP_DIR/$BACKUP_NAME/redis_dump.rdb"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Redis backup completed${NC}"
else
    echo -e "${YELLOW}⚠ Redis backup failed (non-critical)${NC}"
fi

# Backup application data
echo -e "${BLUE}[3/4] Backing up application data...${NC}"
tar -czf "$BACKUP_DIR/$BACKUP_NAME/data.tar.gz" ./data 2>/dev/null || true
if [ -f "$BACKUP_DIR/$BACKUP_NAME/data.tar.gz" ]; then
    echo -e "${GREEN}✓ Application data backup completed${NC}"
else
    echo -e "${YELLOW}⚠ No application data to backup${NC}"
fi

# Backup configuration
echo -e "${BLUE}[4/4] Backing up configuration...${NC}"
cp .env "$BACKUP_DIR/$BACKUP_NAME/.env.backup" 2>/dev/null || true
cp -r config "$BACKUP_DIR/$BACKUP_NAME/config" 2>/dev/null || true
echo -e "${GREEN}✓ Configuration backup completed${NC}"

# Create backup info file
cat > "$BACKUP_DIR/$BACKUP_NAME/backup_info.txt" << EOF
Backup Information
==================
Backup Name: $BACKUP_NAME
Timestamp: $(date)
Hostname: $(hostname)
Docker Version: $(docker --version)
Docker Compose Version: $(docker-compose --version)

Contents:
- database.sql.gz: PostgreSQL database dump
- redis_dump.rdb: Redis data dump
- data.tar.gz: Application data (videos, images, models)
- .env.backup: Environment configuration
- config/: Configuration files
EOF

# Calculate backup size
BACKUP_SIZE=$(du -sh "$BACKUP_DIR/$BACKUP_NAME" | cut -f1)

echo ""
echo -e "${GREEN}========================================"
echo "✓ Backup completed successfully!"
echo "========================================${NC}"
echo ""
echo "Backup location: $BACKUP_DIR/$BACKUP_NAME"
echo "Backup size: $BACKUP_SIZE"
echo ""
echo "To restore this backup, use:"
echo "  ./scripts/docker/restore.sh $BACKUP_DIR/$BACKUP_NAME"
echo ""
