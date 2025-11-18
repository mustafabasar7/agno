#!/bin/bash
# Build Docker images for PPE Detection application

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

echo -e "${GREEN}Building PPE Detection Docker Images${NC}"
echo "----------------------------------------"

# Parse arguments
BUILD_ENV=${1:-production}
NO_CACHE=${2:-false}

if [ "$BUILD_ENV" == "dev" ] || [ "$BUILD_ENV" == "development" ]; then
    echo -e "${YELLOW}Building development images...${NC}"
    DOCKERFILE="Dockerfile.dev"
    COMPOSE_FILE="docker-compose.yml -f docker-compose.dev.yml"
else
    echo -e "${YELLOW}Building production images...${NC}"
    DOCKERFILE="Dockerfile"
    COMPOSE_FILE="docker-compose.yml"
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Using .env.example${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}Created .env from .env.example${NC}"
    else
        echo -e "${RED}Error: .env.example not found. Please create it first.${NC}"
        exit 1
    fi
fi

# Build command
BUILD_CMD="docker-compose -f $COMPOSE_FILE build"

if [ "$NO_CACHE" == "true" ] || [ "$NO_CACHE" == "--no-cache" ]; then
    BUILD_CMD="$BUILD_CMD --no-cache"
    echo -e "${YELLOW}Building without cache...${NC}"
fi

# Add parallel build if supported
BUILD_CMD="$BUILD_CMD --parallel"

echo ""
echo -e "${GREEN}Running: $BUILD_CMD${NC}"
echo ""

# Execute build
eval $BUILD_CMD

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Build completed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "  - Start services: ./scripts/docker/start.sh"
    echo "  - View logs: ./scripts/docker/logs.sh"
    echo ""
else
    echo ""
    echo -e "${RED}✗ Build failed!${NC}"
    exit 1
fi
