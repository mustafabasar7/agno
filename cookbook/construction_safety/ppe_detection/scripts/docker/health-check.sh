#!/bin/bash
# Health check script for PPE Detection services

set -e

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

echo -e "${GREEN}PPE Detection System Health Check${NC}"
echo "=========================================="
echo ""

# Check if Docker is running
echo -e "${BLUE}[1/7] Checking Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Docker is running${NC}"
fi

# Check if Docker Compose is available
echo -e "${BLUE}[2/7] Checking Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose is not installed${NC}"
    exit 1
else
    COMPOSE_VERSION=$(docker-compose version --short)
    echo -e "${GREEN}✓ Docker Compose is available (v${COMPOSE_VERSION})${NC}"
fi

# Check if .env file exists
echo -e "${BLUE}[3/7] Checking configuration...${NC}"
if [ ! -f .env ]; then
    echo -e "${RED}✗ .env file not found${NC}"
    echo "  Run: cp .env.example .env"
    exit 1
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Check if services are running
echo -e "${BLUE}[4/7] Checking services status...${NC}"
SERVICES=$(docker-compose ps --services 2>/dev/null | wc -l)
RUNNING=$(docker-compose ps --filter "status=running" --services 2>/dev/null | wc -l)

if [ $SERVICES -eq 0 ]; then
    echo -e "${YELLOW}⚠ No services defined${NC}"
elif [ $RUNNING -eq 0 ]; then
    echo -e "${RED}✗ No services running${NC}"
    echo "  Run: ./scripts/docker/start.sh"
else
    echo -e "${GREEN}✓ $RUNNING/$SERVICES services running${NC}"
fi

# Check individual service health
echo -e "${BLUE}[5/7] Checking service health...${NC}"

check_service_health() {
    local service=$1
    local health=$(docker inspect --format='{{.State.Health.Status}}' ppe_detection_$service 2>/dev/null)

    if [ -z "$health" ]; then
        # No health check defined, check if running
        local status=$(docker inspect --format='{{.State.Status}}' ppe_detection_$service 2>/dev/null)
        if [ "$status" == "running" ]; then
            echo -e "  ${GREEN}✓${NC} $service: running"
        else
            echo -e "  ${RED}✗${NC} $service: $status"
        fi
    elif [ "$health" == "healthy" ]; then
        echo -e "  ${GREEN}✓${NC} $service: healthy"
    elif [ "$health" == "starting" ]; then
        echo -e "  ${YELLOW}⚠${NC} $service: starting"
    else
        echo -e "  ${RED}✗${NC} $service: $health"
    fi
}

check_service_health "app"
check_service_health "db"
check_service_health "redis"
check_service_health "celery"
check_service_health "nginx"

# Check API endpoint
echo -e "${BLUE}[6/7] Checking API endpoint...${NC}"
if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    RESPONSE=$(curl -s http://localhost:8000/health)
    echo -e "${GREEN}✓ API is responding${NC}"
    echo "  Response: $RESPONSE"
else
    echo -e "${RED}✗ API is not responding${NC}"
    echo "  Check: curl http://localhost:8000/health"
fi

# Check resource usage
echo -e "${BLUE}[7/7] Checking resource usage...${NC}"
CONTAINERS=$(docker ps --filter "name=ppe_detection" --format "{{.Names}}")

if [ -z "$CONTAINERS" ]; then
    echo -e "${YELLOW}⚠ No containers running${NC}"
else
    # Get stats (non-streaming)
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" --filter "name=ppe_detection" 2>/dev/null | head -10
fi

echo ""
echo "=========================================="

# Overall status
OVERALL_STATUS=0
if [ $RUNNING -eq 0 ]; then
    OVERALL_STATUS=1
    echo -e "${RED}Status: UNHEALTHY - Services not running${NC}"
elif ! curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    OVERALL_STATUS=1
    echo -e "${YELLOW}Status: DEGRADED - API not responding${NC}"
else
    echo -e "${GREEN}Status: HEALTHY${NC}"
fi

echo ""
echo "Useful commands:"
echo "  - View logs: ./scripts/docker/logs.sh"
echo "  - Restart: docker-compose restart"
echo "  - Full status: docker-compose ps"
echo ""

exit $OVERALL_STATUS
