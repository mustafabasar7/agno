# PPE Detection System - Setup Guide

Complete installation and configuration guide for the PPE Detection System.

## Table of Contents

- [System Requirements](#system-requirements)
- [Hardware Recommendations](#hardware-recommendations)
- [Installation Methods](#installation-methods)
- [Docker Installation](#docker-installation)
- [Local Python Installation](#local-python-installation)
- [Camera Configuration](#camera-configuration)
- [Network Setup for RTSP](#network-setup-for-rtsp)
- [Database Setup](#database-setup)
- [Environment Configuration](#environment-configuration)
- [Model Setup](#model-setup)
- [First Run](#first-run)
- [Verification](#verification)

---

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|------------|
| **CPU** | 4 cores (2.0 GHz+) |
| **RAM** | 8 GB |
| **Storage** | 50 GB available space |
| **OS** | Ubuntu 20.04+, macOS 11+, Windows 10+ |
| **Python** | 3.9, 3.10, 3.11, or 3.12 |
| **Docker** | 20.10+ (if using Docker) |
| **Network** | 100 Mbps+ |

### Recommended for Production

| Component | Specification |
|-----------|--------------|
| **CPU** | 8+ cores (Intel Xeon or AMD EPYC) |
| **RAM** | 16-32 GB |
| **Storage** | 200+ GB SSD (NVMe preferred) |
| **GPU** | NVIDIA GPU with 6+ GB VRAM (optional) |
| **OS** | Ubuntu 22.04 LTS Server |
| **Network** | 1 Gbps+ with dedicated VLAN for cameras |

### GPU Requirements (Optional)

For GPU acceleration:
- **NVIDIA GPU**: GTX 1660 Ti or better
- **VRAM**: 6 GB minimum, 8+ GB recommended
- **CUDA**: 11.8 or newer
- **cuDNN**: 8.6 or newer
- **Drivers**: Latest NVIDIA drivers

---

## Hardware Recommendations

### Server Configuration

#### Small Deployment (1-5 cameras)
```
CPU: 4-core Intel i5 or AMD Ryzen 5
RAM: 8-16 GB
Storage: 128 GB SSD
Network: 100 Mbps
Estimated Cost: $500-800
```

#### Medium Deployment (5-15 cameras)
```
CPU: 8-core Intel i7 or AMD Ryzen 7
RAM: 16-32 GB
Storage: 512 GB NVMe SSD
GPU: NVIDIA GTX 1660 Ti (optional)
Network: 1 Gbps
Estimated Cost: $1,200-2,000
```

#### Large Deployment (15+ cameras)
```
CPU: 16+ core Intel Xeon or AMD EPYC
RAM: 32-64 GB
Storage: 1 TB+ NVMe SSD RAID
GPU: NVIDIA RTX 3060 or better
Network: 10 Gbps with dedicated camera VLAN
Estimated Cost: $3,000-5,000
```

### Storage Calculations

**Per Camera Storage Requirements:**
- Image storage: ~500 MB/day (1 detection/5 sec)
- Video retention: ~10 GB/day (if recording)
- Database: ~100 MB/day

**Example for 10 cameras, 30-day retention:**
- Images: 10 × 500 MB × 30 = 150 GB
- Videos: 10 × 10 GB × 30 = 3 TB (optional)
- Database: 10 × 100 MB × 30 = 30 GB
- **Total: ~180 GB** (without video) or **~3.2 TB** (with video)

---

## Installation Methods

Choose the installation method that best fits your needs:

| Method | Best For | Difficulty | Production Ready |
|--------|----------|------------|------------------|
| **Docker** | Most users, production | Easy | ✅ Yes |
| **Docker Compose** | Development, testing | Easy | ✅ Yes |
| **Local Python** | Development, testing | Medium | ⚠️ Requires setup |
| **Kubernetes** | Large scale, cloud | Hard | ✅ Yes |

---

## Docker Installation

**Recommended for most users.**

### Prerequisites

Install Docker and Docker Compose:

#### Ubuntu/Debian
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

#### macOS
```bash
# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop

# Verify installation
docker --version
docker compose version
```

#### Windows
```powershell
# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop

# Verify installation in PowerShell
docker --version
docker compose version
```

### Installation Steps

1. **Clone the Repository**

```bash
git clone <repository-url>
cd ppe_detection
```

2. **Setup Environment**

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env  # or use your preferred editor
```

3. **Configure Essential Settings**

Edit `.env` and set these minimum values:

```bash
# Database credentials
DB_PASSWORD=your_secure_db_password_here

# Redis password
REDIS_PASSWORD=your_secure_redis_password_here

# Application secret
SECRET_KEY=your_secret_key_here_change_this_in_production

# API key
API_KEY=your_api_key_here

# Camera URLs (comma-separated)
CAMERA_URLS=rtsp://camera1_url,rtsp://camera2_url
```

4. **Generate Secure Keys**

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate API_KEY
openssl rand -hex 16
```

5. **Build and Start Services**

```bash
# Using Makefile (recommended)
make install
make start

# Or using docker-compose directly
docker-compose build
docker-compose up -d
```

6. **Check Service Status**

```bash
# Using Makefile
make ps

# Or docker-compose
docker-compose ps

# Expected output:
# NAME                    STATUS              PORTS
# ppe_detection_app       Up (healthy)        0.0.0.0:8000->8000/tcp
# ppe_detection_db        Up (healthy)        0.0.0.0:5432->5432/tcp
# ppe_detection_redis     Up (healthy)        0.0.0.0:6379->6379/tcp
# ppe_detection_celery    Up
# ppe_detection_nginx     Up (healthy)        0.0.0.0:80->80/tcp
```

7. **View Logs**

```bash
# All services
make logs

# Specific service
make logs-app
make logs-db

# Follow logs in real-time
docker-compose logs -f app
```

---

## Local Python Installation

**For development and testing.**

### Prerequisites

1. **Python 3.9+**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3-pip

# macOS
brew install python@3.11

# Windows
# Download from: https://www.python.org/downloads/
```

2. **PostgreSQL**

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql@16

# Windows
# Download from: https://www.postgresql.org/download/windows/
```

3. **Redis**

```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Windows
# Download from: https://redis.io/download
```

### Installation Steps

1. **Clone Repository**

```bash
git clone <repository-url>
cd ppe_detection
```

2. **Create Virtual Environment**

```bash
# Create venv
python3 -m venv venv

# Activate venv
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

3. **Install Dependencies**

```bash
# Install core dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -e ".[dev]"
```

4. **Setup Environment**

```bash
cp .env.example .env
nano .env
```

5. **Setup Database**

```bash
# Create database
sudo -u postgres psql
CREATE DATABASE ppe_detection;
CREATE USER ppe_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ppe_detection TO ppe_user;
\q

# Run migrations
python -m src.database.migrate
```

6. **Setup Redis**

```bash
# Start Redis
redis-server

# Or as service
sudo systemctl start redis
sudo systemctl enable redis
```

7. **Download Model**

```bash
# Create model directory
mkdir -p data/models

# Download YOLO model (example)
wget -O data/models/ppe_detection.pt https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

8. **Run Application**

```bash
# Development mode with auto-reload
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
python run_api.py
```

---

## Camera Configuration

### Supported Camera Types

- **IP Cameras**: Any camera with RTSP/RTMP support
- **USB Cameras**: Local USB webcams (0, 1, 2, etc.)
- **File Sources**: Video files for testing

### RTSP URL Formats

Different camera brands use different URL formats:

#### Generic RTSP Format
```
rtsp://username:password@ip_address:port/stream_path
```

#### Common Camera Brands

**Hikvision:**
```
rtsp://admin:password@192.168.1.64:554/Streaming/Channels/101
```

**Dahua:**
```
rtsp://admin:password@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0
```

**Axis:**
```
rtsp://root:password@192.168.1.100/axis-media/media.amp
```

**Onvif Standard:**
```
rtsp://username:password@192.168.1.100:554/onvif1
```

**Reolink:**
```
rtsp://admin:password@192.168.1.100:554/h264Preview_01_main
```

### Finding Your Camera's RTSP URL

1. **Check Camera Documentation**: Look for RTSP stream path
2. **Use ONVIF Device Manager**:
   - Download from https://sourceforge.net/projects/onvifdm/
   - Scan network for cameras
   - View stream URLs

3. **Test with VLC Media Player**:
   ```
   vlc rtsp://username:password@camera_ip:554/stream
   ```

### Adding Cameras via API

```bash
# Add camera using curl
curl -X POST "http://localhost:8000/api/cameras" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Main Entrance Camera",
    "rtsp_url": "rtsp://admin:password@192.168.1.100:554/stream",
    "location": "Main Entrance",
    "zone": "Zone A",
    "detection_interval": 5,
    "confidence_threshold": 0.7,
    "required_ppe": ["helmet", "vest"]
  }'
```

### Camera Configuration via Environment

```bash
# .env file
CAMERA_URLS=rtsp://admin:pass@192.168.1.100:554/stream1,rtsp://admin:pass@192.168.1.101:554/stream1

# Advanced camera settings
CAMERA_RECONNECT_DELAY=5        # Seconds to wait before reconnecting
CAMERA_MAX_RETRIES=3            # Max reconnection attempts
CAMERA_TIMEOUT=10               # Connection timeout in seconds
FRAME_PROCESSING_INTERVAL=1     # Process every N seconds
CAMERA_WIDTH=1920              # Video width
CAMERA_HEIGHT=1080             # Video height
CAMERA_FPS=30                  # Frames per second
```

---

## Network Setup for RTSP

### Network Architecture

```
┌─────────────────┐
│  Internet       │
└────────┬────────┘
         │
┌────────┴────────┐
│  Router/Gateway │
└────────┬────────┘
         │
    ┌────┴────┐
    │  Switch │
    └────┬────┘
         │
    ─────┼─────────────
    │    │    │    │
┌───┴──┐┌┴──┐┌┴──┐┌┴────┐
│Cam 1 ││Cam││Cam││ PPE  │
│      ││ 2 ││ 3 ││ App  │
└──────┘└───┘└───┘└─────┘
```

### Network Requirements

1. **VLAN Segmentation** (Recommended)
   - Separate VLAN for cameras
   - Prevents camera internet access
   - Reduces network congestion

2. **Bandwidth Calculation**
   - Per camera: 2-4 Mbps (H.264) or 4-8 Mbps (H.265)
   - 10 cameras: 20-80 Mbps
   - Add 50% buffer: 30-120 Mbps

3. **Network Switch**
   - Gigabit ethernet minimum
   - PoE+ for camera power (optional)
   - Managed switch for VLAN support

### Firewall Configuration

**Required Ports:**

| Port | Protocol | Service | Direction |
|------|----------|---------|-----------|
| 8000 | TCP | API Server | Inbound |
| 554 | TCP | RTSP | Outbound to cameras |
| 5432 | TCP | PostgreSQL | Internal only |
| 6379 | TCP | Redis | Internal only |
| 80/443 | TCP | HTTP/HTTPS | Inbound (optional) |

**Firewall Rules Example (UFW):**

```bash
# Allow API access
sudo ufw allow 8000/tcp

# Allow RTSP to camera subnet
sudo ufw allow out to 192.168.1.0/24 port 554

# Allow HTTP/HTTPS (if using Nginx)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### Static IP Assignment

Assign static IPs to cameras to ensure consistent connectivity:

```bash
# Example: /etc/dhcp/dhcpd.conf
host camera-entrance {
    hardware ethernet 00:11:22:33:44:55;
    fixed-address 192.168.1.100;
}

host camera-zone-a {
    hardware ethernet 00:11:22:33:44:66;
    fixed-address 192.168.1.101;
}
```

---

## Database Setup

### PostgreSQL Configuration

#### Using Docker (Included)

Database is automatically configured when using Docker Compose.

#### Manual PostgreSQL Setup

1. **Install PostgreSQL**

```bash
sudo apt-get install postgresql-16
```

2. **Create Database and User**

```bash
sudo -u postgres psql

CREATE DATABASE ppe_detection;
CREATE USER ppe_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE ppe_detection TO ppe_user;

# For PostgreSQL 15+
\c ppe_detection
GRANT ALL ON SCHEMA public TO ppe_user;
\q
```

3. **Configure PostgreSQL**

Edit `/etc/postgresql/16/main/postgresql.conf`:

```ini
# Connection Settings
listen_addresses = 'localhost'  # or '*' for network access
max_connections = 100

# Memory Settings (adjust based on available RAM)
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
work_mem = 4MB

# Logging
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d.log'
log_min_duration_statement = 1000  # Log slow queries (>1s)
```

Edit `/etc/postgresql/16/main/pg_hba.conf`:

```
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             postgres                                peer
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

4. **Restart PostgreSQL**

```bash
sudo systemctl restart postgresql
```

### Database Migrations

```bash
# Run all migrations
python -m alembic upgrade head

# Create new migration
python -m alembic revision --autogenerate -m "Description"

# Rollback one migration
python -m alembic downgrade -1
```

### Database Backup

```bash
# Manual backup
pg_dump -U ppe_user ppe_detection | gzip > backup_$(date +%Y%m%d).sql.gz

# Automated daily backup (crontab)
0 2 * * * pg_dump -U ppe_user ppe_detection | gzip > /backup/ppe_$(date +\%Y\%m\%d).sql.gz
```

---

## Environment Configuration

### Complete .env Configuration

```bash
# ==============================================================================
# APPLICATION SETTINGS
# ==============================================================================
APP_ENV=production                    # production, development, staging
APP_PORT=8000
LOG_LEVEL=info                        # debug, info, warning, error
DEBUG=false

# ==============================================================================
# SECURITY
# ==============================================================================
SECRET_KEY=your_secret_key_here_change_this_in_production
API_KEY=your_api_key_here

# ==============================================================================
# DATABASE CONFIGURATION
# ==============================================================================
DB_NAME=ppe_detection
DB_USER=postgres
DB_PASSWORD=your_secure_db_password_here
DB_HOST=db                            # 'db' for Docker, 'localhost' for local
DB_PORT=5432
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# ==============================================================================
# REDIS CONFIGURATION
# ==============================================================================
REDIS_PASSWORD=your_secure_redis_password_here
REDIS_HOST=redis                      # 'redis' for Docker, 'localhost' for local
REDIS_PORT=6379
REDIS_DB=0

# ==============================================================================
# PPE DETECTION SETTINGS
# ==============================================================================
DETECTION_CONFIDENCE_THRESHOLD=0.5    # Minimum confidence (0.0 - 1.0)
DETECTION_IOU_THRESHOLD=0.45          # NMS threshold (0.0 - 1.0)
MODEL_PATH=/app/data/models/ppe_detection.pt
DETECTION_CLASSES=person,hardhat,safety_vest,no_hardhat,no_vest

# ==============================================================================
# CAMERA CONFIGURATION
# ==============================================================================
CAMERA_URLS=rtsp://admin:password@192.168.1.100:554/stream1
CAMERA_RECONNECT_DELAY=5
CAMERA_MAX_RETRIES=3
CAMERA_TIMEOUT=10
FRAME_PROCESSING_INTERVAL=1
CAMERA_WIDTH=1920
CAMERA_HEIGHT=1080
CAMERA_FPS=30

# ==============================================================================
# MONITORING & ALERTS
# ==============================================================================
ENABLE_MONITORING=true
ENABLE_ALERTS=true
ALERT_VIOLATION_COUNT_THRESHOLD=3
ALERT_COOLDOWN_SECONDS=300

# Email Alerts
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_email_password
ALERT_EMAIL_FROM=alerts@ppe-detection.local
ALERT_EMAIL_TO=safety@company.com

# ==============================================================================
# PERFORMANCE TUNING
# ==============================================================================
WORKERS_COUNT=2
WORKER_TIMEOUT=120
BATCH_SIZE=8
USE_GPU=false
GPU_DEVICE_ID=0
```

---

## Model Setup

### Download Pre-trained Model

```bash
# Create model directory
mkdir -p data/models

# Option 1: Download YOLOv8 base model
wget -O data/models/yolov8n.pt \
  https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

# Option 2: Download custom PPE model (if available)
# wget -O data/models/ppe_detection.pt https://your-model-url/ppe_detection.pt

# Verify model file
ls -lh data/models/
```

### GPU Support (Optional)

For NVIDIA GPU acceleration:

```bash
# Install NVIDIA drivers
sudo apt-get install nvidia-driver-535

# Install CUDA toolkit
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/12.3.0/local_installers/cuda-repo-ubuntu2204-12-3-local_12.3.0-545.23.06-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2204-12-3-local_12.3.0-545.23.06-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2204-12-3-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get install cuda

# Install PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Enable GPU in .env
echo "USE_GPU=true" >> .env
echo "GPU_DEVICE_ID=0" >> .env

# Verify GPU
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

---

## First Run

### Start Services

```bash
# Using Docker (recommended)
make start

# Or docker-compose
docker-compose up -d

# Wait for services to be healthy
make health

# View startup logs
make logs-app
```

### Initialize Database

```bash
# Run migrations
docker-compose exec app python -m alembic upgrade head

# Or if using local installation
python -m alembic upgrade head
```

### Add First Camera

```bash
curl -X POST "http://localhost:8000/api/cameras" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Camera",
    "rtsp_url": "rtsp://admin:password@192.168.1.100:554/stream",
    "location": "Main Entrance",
    "zone": "Zone A",
    "detection_interval": 5,
    "confidence_threshold": 0.7,
    "required_ppe": ["helmet", "vest"]
  }'
```

---

## Verification

### Health Checks

```bash
# Check API health
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime_seconds": 123.45,
  "database_connected": true,
  "model_loaded": true,
  "active_cameras": 1
}
```

### Test Detection

```bash
# Test with sample image
curl -X POST "http://localhost:8000/api/detect" \
  -F "file=@test_image.jpg" \
  -F "confidence_threshold=0.5"
```

### View API Documentation

Open in browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Monitor Logs

```bash
# Real-time logs
make logs

# App logs only
make logs-app

# Database logs
make logs-db
```

### Check System Resources

```bash
# Container resource usage
docker stats

# Disk usage
df -h

# Memory usage
free -h
```

---

## Next Steps

1. **Configure Cameras**: Add all your cameras via API or config file
2. **Setup Alerts**: Configure email, SMS, or webhook notifications
3. **Customize Detection**: Adjust confidence thresholds per camera/zone
4. **Enable Monitoring**: Start Prometheus and Grafana for metrics
5. **Schedule Backups**: Setup automated database backups
6. **SSL/TLS**: Configure HTTPS for production (see [DEPLOYMENT.md](./DEPLOYMENT.md))
7. **Load Testing**: Test with expected camera load
8. **Documentation**: Read [USER_GUIDE.md](./USER_GUIDE.md) for daily operations

---

## Troubleshooting Setup Issues

See [README.md - Troubleshooting](./README.md#troubleshooting) section for common issues and solutions.

For deployment to production environments, see [DEPLOYMENT.md](./DEPLOYMENT.md).
