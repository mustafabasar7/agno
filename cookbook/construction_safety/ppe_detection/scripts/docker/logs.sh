#!/bin/bash
# View logs for PPE Detection Docker services

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

# Parse arguments
SERVICE=${1:-}
FOLLOW=${2:--f}
TAIL=${3:-100}

# Determine compose files
COMPOSE_FILES="-f docker-compose.yml -f docker-compose.dev.yml"

echo -e "${GREEN}PPE Detection Service Logs${NC}"
echo "----------------------------------------"

# Build command
if [ -z "$SERVICE" ]; then
    echo -e "${YELLOW}Showing logs for all services${NC}"
    LOGS_CMD="docker-compose $COMPOSE_FILES logs"
else
    echo -e "${YELLOW}Showing logs for: $SERVICE${NC}"
    LOGS_CMD="docker-compose $COMPOSE_FILES logs $SERVICE"
fi

# Add follow flag
if [ "$FOLLOW" == "-f" ] || [ "$FOLLOW" == "--follow" ]; then
    LOGS_CMD="$LOGS_CMD -f"
fi

# Add tail
LOGS_CMD="$LOGS_CMD --tail=$TAIL"

echo ""
echo -e "${BLUE}Available services:${NC}"
echo "  - app (FastAPI application)"
echo "  - db (PostgreSQL)"
echo "  - redis (Redis cache)"
echo "  - celery_worker (Background tasks)"
echo "  - nginx (Reverse proxy)"
echo "  - prometheus (Monitoring)"
echo "  - grafana (Visualization)"
echo ""
echo -e "${BLUE}Usage:${NC}"
echo "  ./scripts/docker/logs.sh [service] [follow] [lines]"
echo ""
echo -e "${BLUE}Examples:${NC}"
echo "  ./scripts/docker/logs.sh              # All services, follow, last 100 lines"
echo "  ./scripts/docker/logs.sh app          # App service, follow, last 100 lines"
echo "  ./scripts/docker/logs.sh app -f 200   # App service, follow, last 200 lines"
echo "  ./scripts/docker/logs.sh app --no-follow 50   # App service, no follow, last 50 lines"
echo ""
echo -e "${GREEN}Running: $LOGS_CMD${NC}"
echo -e "${YELLOW}Press Ctrl+C to exit${NC}"
echo "----------------------------------------"
echo ""

# Execute logs
eval $LOGS_CMD
