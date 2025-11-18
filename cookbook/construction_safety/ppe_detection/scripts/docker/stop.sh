#!/bin/bash
# Stop Docker services for PPE Detection application

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo -e "${GREEN}Stopping PPE Detection Services${NC}"
echo "----------------------------------------"

# Parse arguments
REMOVE_VOLUMES=${1:-false}
REMOVE_ORPHANS=${2:-true}

# Determine compose files (stop all)
COMPOSE_FILES="-f docker-compose.yml -f docker-compose.dev.yml"

# Build command
STOP_CMD="docker-compose $COMPOSE_FILES down"

if [ "$REMOVE_ORPHANS" == "true" ]; then
    STOP_CMD="$STOP_CMD --remove-orphans"
fi

if [ "$REMOVE_VOLUMES" == "true" ] || [ "$REMOVE_VOLUMES" == "-v" ] || [ "$REMOVE_VOLUMES" == "--volumes" ]; then
    echo -e "${YELLOW}Warning: This will remove all volumes (databases, caches, etc.)${NC}"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        STOP_CMD="$STOP_CMD -v"
    else
        echo "Skipping volume removal"
    fi
fi

echo ""
echo -e "${GREEN}Running: $STOP_CMD${NC}"
echo ""

# Execute stop
eval $STOP_CMD

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Services stopped successfully!${NC}"
    echo ""

    # Show remaining containers
    RUNNING=$(docker ps -a --filter "name=ppe_detection" --format "{{.Names}}" | wc -l)
    if [ $RUNNING -gt 0 ]; then
        echo -e "${YELLOW}Remaining containers:${NC}"
        docker ps -a --filter "name=ppe_detection" --format "table {{.Names}}\t{{.Status}}"
        echo ""
    fi

    # Show remaining volumes
    VOLUMES=$(docker volume ls --filter "name=ppe_detection" --format "{{.Name}}" | wc -l)
    if [ $VOLUMES -gt 0 ]; then
        echo -e "${YELLOW}Remaining volumes:${NC}"
        docker volume ls --filter "name=ppe_detection"
        echo ""
        echo "To remove volumes: ./scripts/docker/stop.sh --volumes"
        echo ""
    fi
else
    echo ""
    echo -e "${RED}✗ Failed to stop services!${NC}"
    exit 1
fi
