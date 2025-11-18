# PPE Detection System - Deployment Guide

Comprehensive deployment guide for various environments.

## Table of Contents

- [Deployment Overview](#deployment-overview)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Cloud Deployment](#cloud-deployment)
  - [AWS Deployment](#aws-deployment)
  - [Azure Deployment](#azure-deployment)
  - [Google Cloud Platform](#google-cloud-platform)
- [On-Premise Deployment](#on-premise-deployment)
- [SSL/TLS Setup](#ssltls-setup)
- [Reverse Proxy Configuration](#reverse-proxy-configuration)
- [High Availability Setup](#high-availability-setup)
- [Monitoring Setup](#monitoring-setup)
- [Backup and Recovery](#backup-and-recovery)
- [Security Hardening](#security-hardening)
- [Performance Tuning](#performance-tuning)
- [Troubleshooting](#troubleshooting)

---

## Deployment Overview

### Deployment Options

| Deployment Type | Best For | Complexity | Cost | Scalability |
|----------------|----------|------------|------|-------------|
| **Docker Single Host** | Small sites, testing | Low | Low | Limited |
| **Docker Swarm** | Medium sites | Medium | Low | Medium |
| **Kubernetes** | Large sites, multi-site | High | Medium | High |
| **AWS ECS/EKS** | Cloud-first | Medium | Variable | High |
| **Azure AKS** | Azure ecosystem | Medium | Variable | High |
| **GCP GKE** | GCP ecosystem | Medium | Variable | High |
| **On-Premise VM** | Air-gapped, compliance | Medium | High (upfront) | Medium |

### Pre-Deployment Checklist

- [ ] Server/VM provisioned with required resources
- [ ] Domain name configured (if using SSL)
- [ ] SSL certificates obtained (Let's Encrypt, commercial, or self-signed)
- [ ] Database backup strategy defined
- [ ] Firewall rules configured
- [ ] Camera network accessible from deployment server
- [ ] `.env` file configured with production values
- [ ] Model files downloaded and available
- [ ] Monitoring and alerting configured
- [ ] Backup and restore procedures tested
- [ ] Documentation reviewed

---

## Docker Deployment

### Single Host Docker Deployment

**Best for:** 1-10 cameras, single site

#### Prerequisites

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get install docker-compose-plugin
```

#### Deployment Steps

1. **Clone Repository**

```bash
git clone <repository-url>
cd ppe_detection
```

2. **Configure Environment**

```bash
cp .env.example .env
nano .env
```

**Essential Production Settings:**

```bash
# Application
APP_ENV=production
LOG_LEVEL=info
DEBUG=false

# Security - MUST CHANGE
SECRET_KEY=$(openssl rand -hex 32)
API_KEY=$(openssl rand -hex 16)

# Database - STRONG PASSWORDS
DB_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)

# Cameras
CAMERA_URLS=rtsp://cam1,rtsp://cam2,rtsp://cam3

# Monitoring
ENABLE_MONITORING=true
ENABLE_ALERTS=true

# Email alerts
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@company.com
SMTP_PASSWORD=your_email_app_password
ALERT_EMAIL_TO=safety@company.com

# Performance
WORKERS_COUNT=4  # Adjust based on CPU cores
USE_GPU=true     # If GPU available
```

3. **Build and Start**

```bash
# Build images
make build-prod

# Start services
make start

# Check status
make ps

# View logs
make logs
```

4. **Initialize Database**

```bash
# Run migrations
docker-compose exec app python -m alembic upgrade head
```

5. **Verify Deployment**

```bash
# Health check
curl http://localhost:8000/health

# Interactive API docs
open http://localhost:8000/docs
```

#### Production Optimizations

**docker-compose.prod.yml:**

```yaml
version: '3.8'

services:
  app:
    restart: always
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
        reservations:
          cpus: '2.0'
          memory: 4G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  db:
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    command: postgres -c max_connections=200 -c shared_buffers=256MB

  redis:
    restart: always
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD} --maxmemory 1gb --maxmemory-policy allkeys-lru

  nginx:
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx-prod.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - letsencrypt:/etc/letsencrypt:ro
```

---

## Kubernetes Deployment

**Best for:** 15+ cameras, multi-site, high availability

### Prerequisites

- Kubernetes cluster (v1.24+)
- kubectl configured
- Helm 3.x installed
- Persistent volume provisioner
- Ingress controller (Nginx or Traefik)

### Deployment Files

**namespace.yaml:**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ppe-detection
  labels:
    name: ppe-detection
    environment: production
```

**configmap.yaml:**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ppe-config
  namespace: ppe-detection
data:
  APP_ENV: "production"
  LOG_LEVEL: "info"
  DETECTION_CONFIDENCE_THRESHOLD: "0.5"
  DETECTION_IOU_THRESHOLD: "0.45"
  ENABLE_MONITORING: "true"
  ENABLE_ALERTS: "true"
```

**secrets.yaml:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ppe-secrets
  namespace: ppe-detection
type: Opaque
stringData:
  DB_PASSWORD: "your_secure_password"
  REDIS_PASSWORD: "your_redis_password"
  SECRET_KEY: "your_secret_key"
  API_KEY: "your_api_key"
  SMTP_PASSWORD: "your_smtp_password"
```

**postgresql.yaml:**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: ppe-detection
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
  storageClassName: standard
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: ppe-detection
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:16-alpine
        ports:
        - containerPort: 5432
          name: postgres
        env:
        - name: POSTGRES_DB
          value: ppe_detection
        - name: POSTGRES_USER
          value: postgres
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: ppe-secrets
              key: DB_PASSWORD
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 50Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: ppe-detection
spec:
  ports:
  - port: 5432
    targetPort: 5432
  selector:
    app: postgres
  clusterIP: None
```

**redis.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: ppe-detection
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        command: ["redis-server"]
        args:
          - "--requirepass"
          - "$(REDIS_PASSWORD)"
          - "--appendonly"
          - "yes"
        env:
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: ppe-secrets
              key: REDIS_PASSWORD
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: ppe-detection
spec:
  ports:
  - port: 6379
    targetPort: 6379
  selector:
    app: redis
```

**app-deployment.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ppe-app
  namespace: ppe-detection
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ppe-app
  template:
    metadata:
      labels:
        app: ppe-app
    spec:
      containers:
      - name: app
        image: your-registry/ppe-detection:latest
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: DATABASE_URL
          value: "postgresql://postgres:$(DB_PASSWORD)@postgres:5432/ppe_detection"
        - name: REDIS_URL
          value: "redis://:$(REDIS_PASSWORD)@redis:6379/0"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: ppe-secrets
              key: DB_PASSWORD
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: ppe-secrets
              key: REDIS_PASSWORD
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: ppe-secrets
              key: SECRET_KEY
        envFrom:
        - configMapRef:
            name: ppe-config
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        volumeMounts:
        - name: data
          mountPath: /app/data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: app-data-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: ppe-app
  namespace: ppe-detection
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: ppe-app
```

**ingress.yaml:**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ppe-ingress
  namespace: ppe-detection
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - ppe.yourdomain.com
    secretName: ppe-tls
  rules:
  - host: ppe.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ppe-app
            port:
              number: 8000
```

**hpa.yaml (Horizontal Pod Autoscaler):**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ppe-app-hpa
  namespace: ppe-detection
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ppe-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets (replace with actual values)
kubectl create secret generic ppe-secrets \
  --from-literal=DB_PASSWORD=$(openssl rand -base64 32) \
  --from-literal=REDIS_PASSWORD=$(openssl rand -base64 32) \
  --from-literal=SECRET_KEY=$(openssl rand -hex 32) \
  --from-literal=API_KEY=$(openssl rand -hex 16) \
  -n ppe-detection

# Create config
kubectl apply -f k8s/configmap.yaml

# Deploy database
kubectl apply -f k8s/postgresql.yaml

# Deploy Redis
kubectl apply -f k8s/redis.yaml

# Wait for DB and Redis
kubectl wait --for=condition=ready pod -l app=postgres -n ppe-detection --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n ppe-detection --timeout=300s

# Deploy application
kubectl apply -f k8s/app-deployment.yaml

# Deploy ingress
kubectl apply -f k8s/ingress.yaml

# Deploy HPA
kubectl apply -f k8s/hpa.yaml

# Check status
kubectl get pods -n ppe-detection
kubectl get services -n ppe-detection
kubectl get ingress -n ppe-detection

# View logs
kubectl logs -f deployment/ppe-app -n ppe-detection
```

---

## Cloud Deployment

### AWS Deployment

#### Option 1: ECS Fargate

**Task Definition:**

```json
{
  "family": "ppe-detection",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "containerDefinitions": [
    {
      "name": "ppe-app",
      "image": "your-ecr-repo/ppe-detection:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "APP_ENV",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DB_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:db-password"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ppe-detection",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ppe"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

**Terraform Configuration:**

```hcl
# main.tf
provider "aws" {
  region = "us-east-1"
}

# VPC
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "ppe-detection-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = false

  tags = {
    Environment = "production"
    Project     = "ppe-detection"
  }
}

# RDS PostgreSQL
resource "aws_db_instance" "postgres" {
  identifier        = "ppe-detection-db"
  engine            = "postgres"
  engine_version    = "16.1"
  instance_class    = "db.t3.medium"
  allocated_storage = 100

  db_name  = "ppe_detection"
  username = "postgres"
  password = random_password.db_password.result

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.default.name

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "mon:04:00-mon:05:00"

  multi_az               = true
  storage_encrypted      = true
  skip_final_snapshot    = false
  final_snapshot_identifier = "ppe-detection-final-snapshot"

  tags = {
    Environment = "production"
    Project     = "ppe-detection"
  }
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "ppe-detection-redis"
  engine               = "redis"
  node_type            = "cache.t3.medium"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  engine_version       = "7.0"
  port                 = 6379

  subnet_group_name  = aws_elasticache_subnet_group.default.name
  security_group_ids = [aws_security_group.redis.id]

  snapshot_retention_limit = 5
  snapshot_window          = "03:00-05:00"

  tags = {
    Environment = "production"
    Project     = "ppe-detection"
  }
}

# Application Load Balancer
resource "aws_lb" "app" {
  name               = "ppe-detection-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = module.vpc.public_subnets

  enable_deletion_protection = true

  tags = {
    Environment = "production"
    Project     = "ppe-detection"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "ppe-detection-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Environment = "production"
    Project     = "ppe-detection"
  }
}

# ECS Service
resource "aws_ecs_service" "app" {
  name            = "ppe-app"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 3
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "ppe-app"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.app]
}

# Auto Scaling
resource "aws_appautoscaling_target" "ecs_target" {
  max_capacity       = 10
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.app.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "ecs_policy_cpu" {
  name               = "cpu-auto-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}
```

**Deploy to AWS:**

```bash
# Build and push Docker image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t ppe-detection .
docker tag ppe-detection:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/ppe-detection:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/ppe-detection:latest

# Deploy with Terraform
cd terraform
terraform init
terraform plan
terraform apply

# Check deployment
aws ecs list-services --cluster ppe-detection-cluster
aws ecs describe-services --cluster ppe-detection-cluster --services ppe-app
```

---

### Azure Deployment

#### Azure Container Instances

```bash
# Create resource group
az group create --name ppe-detection-rg --location eastus

# Create Azure Container Registry
az acr create --resource-group ppe-detection-rg \
  --name ppedetectionacr --sku Basic

# Build and push image
az acr build --registry ppedetectionacr \
  --image ppe-detection:latest .

# Create Azure Database for PostgreSQL
az postgres flexible-server create \
  --resource-group ppe-detection-rg \
  --name ppe-detection-db \
  --location eastus \
  --admin-user postgres \
  --admin-password <secure-password> \
  --sku-name Standard_D2s_v3 \
  --tier GeneralPurpose \
  --version 16 \
  --storage-size 128

# Create Azure Cache for Redis
az redis create \
  --resource-group ppe-detection-rg \
  --name ppe-detection-redis \
  --location eastus \
  --sku Basic \
  --vm-size c0

# Deploy container
az container create \
  --resource-group ppe-detection-rg \
  --name ppe-app \
  --image ppedetectionacr.azurecr.io/ppe-detection:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8000 \
  --dns-name-label ppe-detection \
  --environment-variables \
    APP_ENV=production \
    DATABASE_URL="postgresql://postgres:<password>@ppe-detection-db.postgres.database.azure.com:5432/ppe_detection" \
    REDIS_URL="redis://:<password>@ppe-detection-redis.redis.cache.windows.net:6380?ssl=true"
```

---

## SSL/TLS Setup

### Let's Encrypt with Certbot

```bash
# Install Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d ppe.yourdomain.com -d www.ppe.yourdomain.com

# Auto-renewal (add to crontab)
0 12 * * * /usr/bin/certbot renew --quiet
```

### Nginx SSL Configuration

**config/nginx-ssl.conf:**

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name ppe.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name ppe.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/ppe.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ppe.yourdomain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;

    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Proxy to app
    location / {
        proxy_pass http://app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Increase upload size for detection images
    client_max_body_size 10M;
}
```

---

## Backup and Recovery

### Automated Backup Script

**scripts/backup.sh:**

```bash
#!/bin/bash
set -e

BACKUP_DIR="/backup/ppe_detection"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="ppe_backup_${TIMESTAMP}"

mkdir -p "$BACKUP_DIR/$BACKUP_NAME"

# Backup PostgreSQL
echo "Backing up database..."
docker-compose exec -T db pg_dump -U postgres ppe_detection | \
  gzip > "$BACKUP_DIR/$BACKUP_NAME/database.sql.gz"

# Backup Redis
echo "Backing up Redis..."
docker-compose exec -T redis redis-cli --rdb /data/dump.rdb save
docker cp ppe_detection_redis:/data/dump.rdb "$BACKUP_DIR/$BACKUP_NAME/redis.rdb"

# Backup application data
echo "Backing up application data..."
tar -czf "$BACKUP_DIR/$BACKUP_NAME/app_data.tar.gz" \
  -C ./data detections models

# Backup configuration
echo "Backing up configuration..."
cp .env "$BACKUP_DIR/$BACKUP_NAME/env.backup"
cp docker-compose.yml "$BACKUP_DIR/$BACKUP_NAME/"

# Create backup manifest
cat > "$BACKUP_DIR/$BACKUP_NAME/manifest.json" <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "version": "$(docker-compose exec -T app python -c 'import sys; print(sys.version)')",
  "databases": ["postgresql", "redis"],
  "files": ["database.sql.gz", "redis.rdb", "app_data.tar.gz", "env.backup", "docker-compose.yml"]
}
EOF

# Compress entire backup
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"

echo "Backup completed: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"

# Cleanup old backups (keep last 30 days)
find "$BACKUP_DIR" -name "ppe_backup_*.tar.gz" -mtime +30 -delete
```

### Automated Backup with Cron

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/scripts/backup.sh >> /var/log/ppe_backup.log 2>&1
```

### Restore from Backup

**scripts/restore.sh:**

```bash
#!/bin/bash
set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <backup_file.tar.gz>"
  exit 1
fi

BACKUP_FILE="$1"
RESTORE_DIR="/tmp/ppe_restore_$$"

mkdir -p "$RESTORE_DIR"
tar -xzf "$BACKUP_FILE" -C "$RESTORE_DIR"

BACKUP_NAME=$(basename "$BACKUP_FILE" .tar.gz)
BACKUP_PATH="$RESTORE_DIR/$BACKUP_NAME"

# Stop services
echo "Stopping services..."
docker-compose down

# Restore database
echo "Restoring database..."
gunzip < "$BACKUP_PATH/database.sql.gz" | \
  docker-compose exec -T db psql -U postgres ppe_detection

# Restore Redis
echo "Restoring Redis..."
docker cp "$BACKUP_PATH/redis.rdb" ppe_detection_redis:/data/dump.rdb
docker-compose restart redis

# Restore application data
echo "Restoring application data..."
tar -xzf "$BACKUP_PATH/app_data.tar.gz" -C ./data

# Restore configuration (review before overwriting)
echo "Configuration backup available at: $BACKUP_PATH/env.backup"

# Start services
echo "Starting services..."
docker-compose up -d

echo "Restore completed!"
echo "Please verify the restoration and review configuration at: $BACKUP_PATH/env.backup"

# Cleanup
rm -rf "$RESTORE_DIR"
```

---

## Monitoring Setup

### Prometheus + Grafana

**config/prometheus.yml:**

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'ppe-app'
    static_configs:
      - targets: ['app:8000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

**Start Monitoring Stack:**

```bash
# Start with monitoring profile
docker-compose --profile monitoring up -d

# Access Grafana
open http://localhost:3000
# Default: admin/admin

# Import PPE Detection dashboard
# Dashboard ID: Create custom or import from dashboards/grafana/
```

---

## Performance Tuning

### Database Optimization

```sql
-- Create indexes for common queries
CREATE INDEX idx_violations_camera_timestamp
  ON violations(camera_id, timestamp DESC);

CREATE INDEX idx_violations_timestamp_acknowledged
  ON violations(timestamp DESC, acknowledged);

CREATE INDEX idx_detectionlog_camera_timestamp
  ON detection_logs(camera_id, timestamp DESC);

-- Analyze tables
ANALYZE violations;
ANALYZE detection_logs;
ANALYZE cameras;

-- Vacuum old data
VACUUM ANALYZE violations;
```

### Application Tuning

```bash
# .env optimizations

# Increase workers for more throughput
WORKERS_COUNT=8  # 2 × CPU cores

# Database connection pool
DB_POOL_SIZE=40
DB_MAX_OVERFLOW=20

# Redis optimizations
REDIS_MAX_CONNECTIONS=50

# Enable GPU processing
USE_GPU=true
GPU_DEVICE_ID=0

# Batch processing
BATCH_SIZE=16
MAX_BATCH_WAIT_TIME=5

# Cache settings
CACHE_TTL=300
```

---

For additional deployment scenarios, security hardening, and troubleshooting, see:
- [SETUP.md](./SETUP.md) - Initial setup and configuration
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [README.md](./README.md) - General documentation

**Deployment Support:**
- 📧 Email: deployment@ppe-detection.local
- 💬 Slack: #deployment-help
- 📖 Wiki: https://wiki.ppe-detection.local/deployment
