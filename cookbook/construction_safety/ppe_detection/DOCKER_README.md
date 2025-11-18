# PPE Detection - Docker Quick Start

[![Docker](https://img.shields.io/badge/Docker-20.10%2B-blue.svg)](https://www.docker.com/)
[![Docker Compose](https://img.shields.io/badge/Docker%20Compose-2.0%2B-blue.svg)](https://docs.docker.com/compose/)

Complete Docker setup for the PPE Detection system with production-ready configuration.

## Quick Start (3 Steps)

### 1. Setup Environment
```bash
# Copy environment template
cp .env.example .env

# Edit configuration (required!)
nano .env  # Update AGNO_API_KEY, CAMERA_URLS, passwords, etc.
```

### 2. Build and Start
```bash
# Using helper scripts
./scripts/docker/build.sh
./scripts/docker/start.sh

# OR using Make
make install
make start

# OR using docker-compose directly
docker-compose up -d
```

### 3. Verify
```bash
# Check status
docker-compose ps

# Access the API
curl http://localhost:8000/health

# View documentation
open http://localhost:8000/docs
```

## Services Overview

| Service | Port | Purpose |
|---------|------|---------|
| FastAPI App | 8000 | Main API and detection engine |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache and message broker |
| Celery Worker | - | Background task processing |
| Nginx | 80, 443 | Reverse proxy |
| Prometheus | 9090 | Metrics (optional) |
| Grafana | 3000 | Monitoring UI (optional) |

## Common Commands

### Using Make (Recommended)
```bash
# View all available commands
make help

# Development
make install-dev          # First-time dev setup
make start-dev           # Start dev environment
make logs-app            # View app logs
make db-shell            # Access database

# Production
make install             # First-time production setup
make start-prod          # Start production
make backup              # Backup all data
make scale-app REPLICAS=3  # Scale application

# Maintenance
make restart             # Restart all services
make clean               # Clean up containers
make update              # Update and rebuild
```

### Using Scripts
```bash
# Build
./scripts/docker/build.sh [production|dev]

# Start/Stop
./scripts/docker/start.sh [production|dev]
./scripts/docker/stop.sh

# Logs
./scripts/docker/logs.sh [service]

# Backup/Restore
./scripts/docker/backup.sh
./scripts/docker/restore.sh <backup_dir>
```

### Using Docker Compose
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f [service]

# Stop services
docker-compose down

# Restart service
docker-compose restart [service]
```

## Configuration

### Required Environment Variables

Edit `.env` file with:

```bash
# Agno AI (Required)
AGNO_API_KEY=your_agno_api_key_here

# Security (Required - generate new values!)
SECRET_KEY=$(openssl rand -hex 32)
DB_PASSWORD=your_secure_db_password
REDIS_PASSWORD=your_secure_redis_password

# Cameras (Required)
CAMERA_URLS=rtsp://user:pass@192.168.1.100:554/stream1,rtsp://user:pass@192.168.1.101:554/stream2

# Detection Settings (Optional)
DETECTION_CONFIDENCE_THRESHOLD=0.5
DETECTION_IOU_THRESHOLD=0.45
```

See `.env.example` for all available options.

## Deployment Modes

### Production
Optimized for security and performance:
```bash
make start-prod
# OR
./scripts/docker/start.sh production
```

Features:
- Multi-stage builds
- Non-root user
- Resource limits
- Health checks
- Nginx reverse proxy

### Development
With hot-reload and debugging:
```bash
make start-dev
# OR
./scripts/docker/start.sh dev
```

Features:
- Source code mounted
- Debug mode enabled
- Development tools included
- Lower detection thresholds

### With Monitoring
Enable Prometheus and Grafana:
```bash
make start-monitoring
# OR
docker-compose --profile monitoring up -d
```

Access:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

### Development Tools
PGAdmin, Redis Commander, Flower, Mailhog:
```bash
make start-dev-tools
# OR
docker-compose --profile dev-tools up -d
```

Access:
- PGAdmin: http://localhost:5050
- Redis Commander: http://localhost:8081
- Flower: http://localhost:5555
- Mailhog: http://localhost:8025

## Accessing Services

### API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# API documentation (Swagger)
open http://localhost:8000/docs

# Alternative docs (ReDoc)
open http://localhost:8000/redoc

# Example detection request
curl -X POST http://localhost:8000/api/v1/detect \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"camera_id": "cam_1"}'
```

### Database Access
```bash
# Using Make
make db-shell

# Using Docker Compose
docker-compose exec db psql -U postgres ppe_detection

# Using PGAdmin (dev mode)
open http://localhost:5050
```

### Redis Access
```bash
# CLI
docker-compose exec redis redis-cli

# With password
docker-compose exec redis redis-cli -a your_redis_password

# Redis Commander (dev mode)
open http://localhost:8081
```

## Maintenance

### View Logs
```bash
# All services
make logs

# Specific service
make logs-app
make logs-db

# Follow logs
docker-compose logs -f app
```

### Backup
```bash
# Create backup
make backup
# OR
./scripts/docker/backup.sh

# Creates backup in ./backups/ppe_detection_backup_TIMESTAMP/
```

### Restore
```bash
# Restore from backup
make restore BACKUP_DIR=./backups/ppe_detection_backup_20250118_120000
# OR
./scripts/docker/restore.sh ./backups/ppe_detection_backup_20250118_120000
```

### Database Migrations
```bash
# Run migrations
make db-migrate

# Create new migration
make db-migrate-create

# Manual
docker-compose exec app alembic upgrade head
```

### Scaling
```bash
# Scale application
make scale-app REPLICAS=3

# Scale Celery workers
make scale-celery REPLICAS=2

# Manual
docker-compose up -d --scale app=3
```

### Updates
```bash
# Pull latest changes and rebuild
make update

# Manual
git pull
./scripts/docker/build.sh production --no-cache
docker-compose restart
```

## Troubleshooting

### Services won't start
```bash
# Check service status
docker-compose ps

# View errors
docker-compose logs

# Check resources
docker stats
```

### Port conflicts
```bash
# Change ports in .env
APP_PORT=8001
DB_PORT=5433
```

### Reset everything
```bash
# Stop and remove all
make clean-all

# Rebuild from scratch
make build-no-cache
make start
```

### Camera connection issues
```bash
# Test camera stream
ffmpeg -i "rtsp://user:pass@192.168.1.100:554/stream" -frames:v 1 test.jpg

# Check camera logs
make logs-app
```

### Database issues
```bash
# Check database
make db-shell

# Reset database (WARNING: deletes data)
docker-compose down -v
docker-compose up -d db
```

## Hardware Requirements

### Minimum (1-2 cameras)
- CPU: 4 cores
- RAM: 8GB
- Storage: 50GB SSD
- Network: 10 Mbps

### Recommended (2-4 cameras)
- CPU: 8 cores
- RAM: 16GB
- Storage: 256GB SSD
- Network: 100 Mbps

### Production (5+ cameras)
- CPU: 16+ cores
- RAM: 32GB+
- Storage: 512GB NVMe SSD
- GPU: NVIDIA GPU with 8GB+ VRAM
- Network: 1 Gbps

## File Structure

```
ppe_detection/
├── Dockerfile                 # Production Dockerfile
├── Dockerfile.dev            # Development Dockerfile
├── docker-compose.yml        # Production compose file
├── docker-compose.dev.yml    # Development compose file
├── .dockerignore             # Files to exclude from build
├── .env.example              # Environment template
├── Makefile                  # Helper commands
├── config/
│   ├── nginx.conf           # Nginx configuration
│   └── prometheus.yml       # Prometheus configuration
├── scripts/
│   ├── docker/
│   │   ├── build.sh         # Build script
│   │   ├── start.sh         # Start script
│   │   ├── stop.sh          # Stop script
│   │   ├── logs.sh          # Logs script
│   │   ├── backup.sh        # Backup script
│   │   └── restore.sh       # Restore script
│   ├── init-db.sql          # Database init script
│   └── init-db-dev.sql      # Dev database init
├── docs/
│   └── DOCKER_DEPLOYMENT.md # Complete documentation
└── src/                      # Application source code
```

## Security Checklist

Before deploying to production:

- [ ] Change default passwords in `.env`
- [ ] Generate new `SECRET_KEY`
- [ ] Set strong `DB_PASSWORD`
- [ ] Set strong `REDIS_PASSWORD`
- [ ] Update `API_KEY`
- [ ] Configure SSL/TLS certificates
- [ ] Review and restrict CORS settings
- [ ] Enable firewall rules
- [ ] Set up regular backups
- [ ] Review resource limits
- [ ] Enable monitoring
- [ ] Change Grafana admin password
- [ ] Restrict database access
- [ ] Use strong camera passwords

## Additional Resources

- **Full Documentation**: [docs/DOCKER_DEPLOYMENT.md](docs/DOCKER_DEPLOYMENT.md)
- **Docker Documentation**: https://docs.docker.com/
- **Docker Compose Documentation**: https://docs.docker.com/compose/
- **Agno Documentation**: https://agno.dev/

## Support

For issues or questions:

1. Check logs: `make logs`
2. Review [DOCKER_DEPLOYMENT.md](docs/DOCKER_DEPLOYMENT.md)
3. Check Docker documentation
4. Contact support team

## License

Copyright (c) 2025 PPE Detection System
