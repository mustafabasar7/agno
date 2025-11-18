#!/bin/bash
# Start Docker services for PPE Detection application

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

echo -e "${GREEN}Starting PPE Detection Services${NC}"
echo "----------------------------------------"

# Parse arguments
ENV=${1:-production}
DETACHED=${2:--d}
PROFILE=${3:-}

# Determine compose files
if [ "$ENV" == "dev" ] || [ "$ENV" == "development" ]; then
    echo -e "${YELLOW}Starting in DEVELOPMENT mode${NC}"
    COMPOSE_FILES="-f docker-compose.yml -f docker-compose.dev.yml"
else
    echo -e "${YELLOW}Starting in PRODUCTION mode${NC}"
    COMPOSE_FILES="-f docker-compose.yml"
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please run: cp .env.example .env"
    echo "Then edit .env with your configuration"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check required environment variables
REQUIRED_VARS=("DB_PASSWORD" "REDIS_PASSWORD" "SECRET_KEY")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo -e "${RED}Error: Missing required environment variables:${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    echo ""
    echo "Please configure these in your .env file"
    exit 1
fi

# Build command
START_CMD="docker-compose $COMPOSE_FILES"

# Add profile if specified
if [ ! -z "$PROFILE" ]; then
    START_CMD="$START_CMD --profile $PROFILE"
    echo -e "${BLUE}Using profile: $PROFILE${NC}"
fi

# Add detached mode
if [ "$DETACHED" == "-d" ] || [ "$DETACHED" == "--detach" ]; then
    START_CMD="$START_CMD up -d"
    DETACHED_MODE=true
else
    START_CMD="$START_CMD up"
    DETACHED_MODE=false
fi

echo ""
echo -e "${GREEN}Running: $START_CMD${NC}"
echo ""

# Execute start
eval $START_CMD

if [ $? -eq 0 ]; then
    if [ "$DETACHED_MODE" == true ]; then
        echo ""
        echo -e "${GREEN}✓ Services started successfully!${NC}"
        echo ""
        echo "Service endpoints:"
        echo "  - API: http://localhost:${APP_PORT:-8000}"
        echo "  - API Docs: http://localhost:${APP_PORT:-8000}/docs"
        echo "  - Nginx: http://localhost:${NGINX_HTTP_PORT:-80}"

        if [ "$ENV" == "dev" ] || [ "$ENV" == "development" ]; then
            echo ""
            echo "Development tools (use --profile dev-tools):"
            echo "  - PGAdmin: http://localhost:5050"
            echo "  - Redis Commander: http://localhost:8081"
            echo "  - Flower: http://localhost:5555"
            echo "  - Mailhog: http://localhost:8025"
        fi

        if [ ! -z "$PROFILE" ] && [ "$PROFILE" == "monitoring" ]; then
            echo ""
            echo "Monitoring tools:"
            echo "  - Prometheus: http://localhost:${PROMETHEUS_PORT:-9090}"
            echo "  - Grafana: http://localhost:${GRAFANA_PORT:-3000}"
        fi

        echo ""
        echo "Useful commands:"
        echo "  - View logs: ./scripts/docker/logs.sh"
        echo "  - Stop services: ./scripts/docker/stop.sh"
        echo "  - View status: docker-compose ps"
        echo ""
    fi
else
    echo ""
    echo -e "${RED}✗ Failed to start services!${NC}"
    exit 1
fi
