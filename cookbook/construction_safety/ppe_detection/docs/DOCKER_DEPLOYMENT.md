# Docker Deployment Guide for PPE Detection System

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Configuration](#configuration)
5. [Deployment Options](#deployment-options)
6. [Production Deployment](#production-deployment)
7. [Development Setup](#development-setup)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)
10. [Hardware Requirements](#hardware-requirements)

## Overview

This PPE Detection application is containerized using Docker and Docker Compose, providing:

- **Multi-stage builds** for optimized image sizes
- **Non-root user** execution for security
- **Health checks** for all services
- **Resource limits** appropriate for construction site hardware
- **Horizontal scalability** for multiple cameras
- **Monitoring** with Prometheus and Grafana
- **Development tools** for easier debugging

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Nginx (Reverse Proxy)                │
│                            Port 80/443                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
┌───────▼────────┐                   ┌────────▼────────┐
│   FastAPI App  │◄──────────────────┤  Celery Worker  │
│   Port 8000    │                   │  (Background)   │
└───────┬────────┘                   └────────┬────────┘
        │                                     │
        ├─────────────────┬───────────────────┤
        │                 │                   │
┌───────▼────────┐ ┌──────▼──────┐   ┌───────▼────────┐
│   PostgreSQL   │ │    Redis    │   │   Prometheus   │
│   Port 5432    │ │  Port 6379  │   │   Port 9090    │
└────────────────┘ └─────────────┘   └────────────────┘
```

## Prerequisites

### Required Software

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: For cloning the repository

### Installation

#### Linux (Ubuntu/Debian)
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Add user to docker group (optional, requires logout)
sudo usermod -aG docker $USER
```

#### macOS
```bash
# Install Docker Desktop
brew install --cask docker
```

#### Windows
Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)

### Verify Installation
```bash
docker --version
docker-compose --version
```

## Quick Start

### 1. Clone Repository (if not already done)
```bash
cd /home/user/agno/cookbook/construction_safety/ppe_detection
```

### 2. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit with your settings
nano .env  # or vim, vi, etc.
```

**Required configurations:**
- `AGNO_API_KEY`: Your Agno API key
- `SECRET_KEY`: Generate with `openssl rand -hex 32`
- `DB_PASSWORD`: Secure database password
- `REDIS_PASSWORD`: Secure Redis password
- `CAMERA_URLS`: Your RTSP camera URLs

### 3. Build and Start Services
```bash
# Build images
./scripts/docker/build.sh

# Start services
./scripts/docker/start.sh
```

### 4. Verify Deployment
```bash
# Check service status
docker-compose ps

# View logs
./scripts/docker/logs.sh

# Access the API
curl http://localhost:8000/health
```

### 5. Access Services
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Configuration

### Environment Variables

The `.env` file contains all configuration. Key sections:

#### Application Settings
```env
APP_ENV=production
APP_PORT=8000
LOG_LEVEL=info
DEBUG=false
```

#### Security
```env
SECRET_KEY=your_secret_key_here  # Generate with: openssl rand -hex 32
API_KEY=your_api_key_here
```

#### Database
```env
DB_NAME=ppe_detection
DB_USER=postgres
DB_PASSWORD=secure_password_here
DB_PORT=5432
```

#### Camera Configuration
```env
# Multiple cameras (comma-separated)
CAMERA_URLS=rtsp://admin:pass@192.168.1.100:554/stream1,rtsp://admin:pass@192.168.1.101:554/stream1

CAMERA_RECONNECT_DELAY=5
FRAME_PROCESSING_INTERVAL=1
```

#### Detection Settings
```env
DETECTION_CONFIDENCE_THRESHOLD=0.5
DETECTION_IOU_THRESHOLD=0.45
```

#### Agno AI
```env
AGNO_API_KEY=your_agno_api_key
AGNO_MODEL=gpt-4o
```

## Deployment Options

### Production Deployment

Production deployment with optimized settings and security:

```bash
# Build production images
./scripts/docker/build.sh production

# Start production services
./scripts/docker/start.sh production

# With monitoring enabled
./scripts/docker/start.sh production -d monitoring
```

#### Production Features:
- Multi-stage builds for smaller images
- Non-root user execution
- Resource limits enforced
- Health checks enabled
- Nginx reverse proxy
- SSL/TLS support (when configured)

### Development Deployment

Development setup with hot-reload and debugging tools:

```bash
# Build development images
./scripts/docker/build.sh dev

# Start development services
./scripts/docker/start.sh dev

# With development tools (PGAdmin, Redis Commander, etc.)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --profile dev-tools up -d
```

#### Development Features:
- Source code mounted for hot-reload
- Debug mode enabled
- Lower detection thresholds for testing
- PGAdmin for database management
- Redis Commander for cache inspection
- Flower for Celery task monitoring
- Mailhog for email testing

#### Development Tools Access:
- **PGAdmin**: http://localhost:5050
- **Redis Commander**: http://localhost:8081
- **Flower (Celery)**: http://localhost:5555
- **Mailhog**: http://localhost:8025

## Service Details

### FastAPI Application

**Container**: `ppe_detection_app`

**Ports**: 8000 (HTTP), 5678 (Debugger in dev)

**Environment**: See `.env` file

**Resource Limits**:
- CPU: 2.0 cores (limit), 1.0 core (reservation)
- Memory: 4GB (limit), 2GB (reservation)

**Health Check**:
```bash
curl http://localhost:8000/health
```

### PostgreSQL Database

**Container**: `ppe_detection_db`

**Port**: 5432

**Credentials**: From `.env` file

**Data Volume**: `postgres_data`

**Backup**:
```bash
./scripts/docker/backup.sh
```

**Resource Limits**:
- CPU: 1.0 core (limit), 0.5 core (reservation)
- Memory: 1GB (limit), 512MB (reservation)

### Redis Cache

**Container**: `ppe_detection_redis`

**Port**: 6379

**Password**: From `.env` file

**Data Volume**: `redis_data`

**Resource Limits**:
- CPU: 0.5 core (limit), 0.25 core (reservation)
- Memory: 512MB (limit), 256MB (reservation)

### Celery Worker

**Container**: `ppe_detection_celery`

**Purpose**: Background task processing

**Concurrency**: 2 workers (configurable)

**Resource Limits**:
- CPU: 1.5 cores (limit), 0.5 core (reservation)
- Memory: 3GB (limit), 1GB (reservation)

### Nginx Reverse Proxy

**Container**: `ppe_detection_nginx`

**Ports**: 80 (HTTP), 443 (HTTPS)

**Configuration**: `config/nginx.conf`

**Features**:
- Load balancing
- Rate limiting
- Gzip compression
- WebSocket support
- SSL/TLS termination (when configured)

## Monitoring & Maintenance

### Monitoring Stack (Optional)

Enable with `--profile monitoring`:

```bash
docker-compose --profile monitoring up -d prometheus grafana
```

**Services**:
- **Prometheus**: http://localhost:9090 - Metrics collection
- **Grafana**: http://localhost:3000 - Visualization

**Default Credentials** (Change in production):
- Username: `admin`
- Password: `admin`

### Viewing Logs

```bash
# All services
./scripts/docker/logs.sh

# Specific service
./scripts/docker/logs.sh app

# Last 200 lines without following
./scripts/docker/logs.sh app --no-follow 200
```

### Backup & Restore

#### Create Backup
```bash
./scripts/docker/backup.sh [backup_directory]

# Example
./scripts/docker/backup.sh ./backups
```

Backs up:
- PostgreSQL database
- Redis data
- Application data (videos, images, models)
- Configuration files

#### Restore from Backup
```bash
./scripts/docker/restore.sh <backup_directory>

# Example
./scripts/docker/restore.sh ./backups/ppe_detection_backup_20250118_120000
```

### Database Management

#### Access Database
```bash
docker-compose exec db psql -U postgres ppe_detection
```

#### Run Migrations
```bash
docker-compose exec app alembic upgrade head
```

#### Create Migration
```bash
docker-compose exec app alembic revision --autogenerate -m "description"
```

### Scaling Services

Scale the FastAPI application:
```bash
docker-compose up -d --scale app=3
```

Scale Celery workers:
```bash
docker-compose up -d --scale celery_worker=3
```

### Updating the Application

```bash
# Pull latest code
git pull origin main

# Rebuild images
./scripts/docker/build.sh production --no-cache

# Restart services
docker-compose down
./scripts/docker/start.sh production
```

## Hardware Requirements

### Minimum Requirements (Single Camera)

- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 50GB SSD
- **Network**: 10 Mbps upload

### Recommended Requirements (2-4 Cameras)

- **CPU**: 8 cores (Intel i7 or AMD Ryzen 7)
- **RAM**: 16GB
- **Storage**: 256GB SSD
- **GPU**: NVIDIA GPU with 4GB VRAM (optional, for acceleration)
- **Network**: 100 Mbps LAN

### Production Requirements (5+ Cameras)

- **CPU**: 16+ cores (Intel Xeon or AMD EPYC)
- **RAM**: 32GB+
- **Storage**: 512GB NVMe SSD
- **GPU**: NVIDIA GPU with 8GB+ VRAM
- **Network**: 1 Gbps LAN

### Storage Calculations

**Video Storage**:
- Per camera: ~10 GB/day (with 7-day retention)
- 4 cameras: ~280 GB/week
- Adjust `VIDEO_RETENTION_DAYS` in `.env`

**Database**:
- ~1 GB per month for metadata
- Regular backups recommended

## Troubleshooting

### Services Won't Start

**Check logs**:
```bash
./scripts/docker/logs.sh
```

**Check service status**:
```bash
docker-compose ps
```

**Common issues**:

1. **Port already in use**:
   ```bash
   # Check what's using the port
   sudo netstat -tulpn | grep :8000

   # Change port in .env
   APP_PORT=8001
   ```

2. **Permission denied**:
   ```bash
   # Fix permissions
   sudo chown -R $USER:$USER ./data ./logs
   ```

3. **Out of memory**:
   ```bash
   # Reduce worker count in .env
   WORKERS_COUNT=1
   CELERY_WORKER_CONCURRENCY=1
   ```

### Database Connection Issues

```bash
# Check database is running
docker-compose ps db

# Check database logs
./scripts/docker/logs.sh db

# Test connection
docker-compose exec db psql -U postgres -d ppe_detection -c "SELECT 1"
```

### Camera Connection Issues

**Check camera URLs**:
```bash
# Test RTSP stream
ffmpeg -i "rtsp://admin:password@192.168.1.100:554/stream1" -frames:v 1 test.jpg
```

**Common issues**:
- Incorrect credentials
- Camera not accessible from Docker network
- Firewall blocking RTSP port (554)

**Solution for network issues**:
```bash
# Use host network mode (less secure)
docker-compose up -d --network host
```

### High CPU/Memory Usage

**Check resource usage**:
```bash
docker stats
```

**Reduce resource usage**:

1. **Decrease frame processing**:
   ```env
   FRAME_PROCESSING_INTERVAL=2  # Process every 2 seconds
   FRAME_SKIP_COUNT=1           # Skip every other frame
   ```

2. **Lower detection resolution**:
   ```env
   CAMERA_WIDTH=1280
   CAMERA_HEIGHT=720
   ```

3. **Reduce workers**:
   ```env
   WORKERS_COUNT=1
   CELERY_WORKER_CONCURRENCY=1
   ```

### Container Keeps Restarting

**Check container logs**:
```bash
docker logs ppe_detection_app --tail 100
```

**Common causes**:
- Missing environment variables
- Database not ready (wait for health check)
- Insufficient resources
- Application error

**Debug in interactive mode**:
```bash
docker-compose run --rm app bash
```

### Clean Reinstall

```bash
# Stop all services
./scripts/docker/stop.sh

# Remove all volumes (WARNING: deletes all data)
./scripts/docker/stop.sh --volumes

# Remove all images
docker-compose down --rmi all

# Rebuild from scratch
./scripts/docker/build.sh production --no-cache
./scripts/docker/start.sh production
```

## Security Best Practices

### 1. Change Default Credentials

Update in `.env`:
```env
DB_PASSWORD=<strong-password>
REDIS_PASSWORD=<strong-password>
SECRET_KEY=<generated-secret>
GRAFANA_PASSWORD=<strong-password>
```

### 2. Enable SSL/TLS

Uncomment HTTPS section in `config/nginx.conf` and provide certificates:

```bash
mkdir -p config/ssl
# Copy your certificates
cp /path/to/cert.pem config/ssl/
cp /path/to/key.pem config/ssl/
```

### 3. Network Security

Use Docker networks to isolate services:
```bash
# Already configured in docker-compose.yml
# Services communicate via internal network
```

### 4. Regular Updates

```bash
# Update base images
docker-compose pull

# Rebuild application
./scripts/docker/build.sh production --no-cache
```

### 5. Backup Regularly

Set up automated backups:
```bash
# Add to crontab
0 2 * * * /home/user/agno/cookbook/construction_safety/ppe_detection/scripts/docker/backup.sh /backups
```

## Advanced Configuration

### GPU Support

To enable GPU acceleration:

1. **Install NVIDIA Docker runtime**:
   ```bash
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

   sudo apt-get update
   sudo apt-get install -y nvidia-docker2
   sudo systemctl restart docker
   ```

2. **Update docker-compose.yml**:
   ```yaml
   services:
     app:
       deploy:
         resources:
           reservations:
             devices:
               - driver: nvidia
                 count: 1
                 capabilities: [gpu]
   ```

3. **Set in .env**:
   ```env
   USE_GPU=true
   GPU_DEVICE_ID=0
   ```

### Custom SSL Certificates

1. **Place certificates**:
   ```bash
   mkdir -p config/ssl
   cp your-cert.pem config/ssl/cert.pem
   cp your-key.pem config/ssl/key.pem
   ```

2. **Update nginx.conf**:
   Uncomment the HTTPS server block

3. **Restart Nginx**:
   ```bash
   docker-compose restart nginx
   ```

### Multi-Site Deployment

For multiple construction sites:

1. **Clone configuration**:
   ```bash
   cp .env .env.site1
   cp .env .env.site2
   ```

2. **Update ports and names**:
   ```env
   # .env.site1
   APP_PORT=8001
   COMPOSE_PROJECT_NAME=ppe_site1

   # .env.site2
   APP_PORT=8002
   COMPOSE_PROJECT_NAME=ppe_site2
   ```

3. **Deploy separately**:
   ```bash
   docker-compose --env-file .env.site1 up -d
   docker-compose --env-file .env.site2 up -d
   ```

## Support and Resources

### Useful Commands Cheat Sheet

```bash
# Build
./scripts/docker/build.sh [production|dev] [--no-cache]

# Start
./scripts/docker/start.sh [production|dev] [-d|--detach] [profile]

# Stop
./scripts/docker/stop.sh [--volumes]

# Logs
./scripts/docker/logs.sh [service] [-f|--no-follow] [lines]

# Backup
./scripts/docker/backup.sh [backup_dir]

# Restore
./scripts/docker/restore.sh <backup_dir>

# Status
docker-compose ps

# Resource usage
docker stats

# Execute command in container
docker-compose exec <service> <command>

# Access shell
docker-compose exec app bash
```

### Log Locations

- **Application**: `./logs/app.log`
- **Nginx**: Docker volume `nginx_logs`
- **Docker**: `docker-compose logs`

### Getting Help

For issues or questions:

1. Check logs: `./scripts/docker/logs.sh`
2. Review this documentation
3. Check Docker and Docker Compose documentation
4. Contact support team

## License

Copyright (c) 2025 PPE Detection System
