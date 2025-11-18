# PPE Detection System - Architecture Documentation

Comprehensive system architecture and design decisions.

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Diagram](#architecture-diagram)
- [Component Descriptions](#component-descriptions)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Design Decisions](#design-decisions)
- [Scalability Considerations](#scalability-considerations)
- [Security Architecture](#security-architecture)
- [Database Schema](#database-schema)
- [API Architecture](#api-architecture)
- [Detection Pipeline](#detection-pipeline)
- [Alert System](#alert-system)

---

## System Overview

The PPE Detection System is a microservices-based application designed to provide real-time personal protective equipment compliance monitoring for construction sites using computer vision and AI.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  Web Dashboard  │  Mobile App  │  External Systems (API)        │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway (Nginx)                         │
│                   Load Balancing │ SSL/TLS                       │
└─────────────────────────────────────────────────────────────────┘
                               │
           ┌───────────────────┼───────────────────┐
           ▼                   ▼                   ▼
┌──────────────────┐  ┌────────────────┐  ┌──────────────────┐
│   FastAPI App    │  │  FastAPI App   │  │   FastAPI App    │
│   (Instance 1)   │  │  (Instance 2)  │  │   (Instance 3)   │
└──────────────────┘  └────────────────┘  └──────────────────┘
           │                   │                   │
           └───────────────────┼───────────────────┘
                               │
           ┌───────────────────┼───────────────────┐
           ▼                   ▼                   ▼
┌──────────────────┐  ┌────────────────┐  ┌──────────────────┐
│   PostgreSQL     │  │     Redis      │  │  Celery Workers  │
│   (Database)     │  │ (Cache/Queue)  │  │  (Background)    │
└──────────────────┘  └────────────────┘  └──────────────────┘
           │                                        │
           ▼                                        ▼
┌──────────────────┐                     ┌──────────────────┐
│  Storage Layer   │                     │  Camera Streams  │
│  (Images/Videos) │                     │  (RTSP/RTMP)     │
└──────────────────┘                     └──────────────────┘
```

### Key Characteristics

- **Stateless Application Layer**: Enables horizontal scaling
- **Event-Driven Architecture**: Asynchronous processing with Celery
- **API-First Design**: RESTful API with WebSocket support
- **Containerized**: Docker containers for easy deployment
- **Cloud-Native**: Designed for cloud and on-premise deployment
- **Highly Available**: No single point of failure

---

## Architecture Diagram

### Detailed System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                            External Layer                               │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                 │
│  │   Camera 1  │   │   Camera 2  │   │   Camera N  │                 │
│  │ (RTSP/RTMP) │   │ (RTSP/RTMP) │   │ (RTSP/RTMP) │                 │
│  └─────────────┘   └─────────────┘   └─────────────┘                 │
│          │                 │                 │                          │
└──────────┼─────────────────┼─────────────────┼──────────────────────────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────────────┐
│                     Ingress Layer (Nginx)                               │
├────────────────────────────┼────────────────────────────────────────────┤
│  • SSL Termination         │                                            │
│  • Load Balancing          │  ┌──────────────────────┐                 │
│  • Rate Limiting           ├─▶│   API Gateway        │                 │
│  • Request Routing         │  │   (Nginx/Traefik)    │                 │
│                            │  └──────────────────────┘                 │
└────────────────────────────┼────────────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────────────┐
│                     Application Layer                                   │
├────────────────────────────┼────────────────────────────────────────────┤
│                             │                                            │
│  ┌──────────────────────────┼──────────────────────────────┐            │
│  │         FastAPI Application (Stateless)                 │            │
│  ├─────────────────────────────────────────────────────────┤            │
│  │                                                          │            │
│  │  ┌────────────────┐  ┌────────────────┐  ┌──────────┐ │            │
│  │  │ API Endpoints  │  │  WebSocket     │  │  Health  │ │            │
│  │  │  /cameras      │  │  /ws/live      │  │  /health │ │            │
│  │  │  /detect       │  │                │  │          │ │            │
│  │  │  /violations   │  └────────────────┘  └──────────┘ │            │
│  │  │  /stats        │                                    │            │
│  │  └────────────────┘                                    │            │
│  │                                                          │            │
│  │  ┌────────────────────────────────────────────────┐    │            │
│  │  │           Business Logic Layer                  │    │            │
│  │  ├────────────────────────────────────────────────┤    │            │
│  │  │                                                 │    │            │
│  │  │  ┌──────────────┐  ┌───────────────────────┐  │    │            │
│  │  │  │   Camera     │  │   Detection Service   │  │    │            │
│  │  │  │   Manager    │  │   - YOLO Model        │  │    │            │
│  │  │  │              │  │   - Person Detection  │  │    │            │
│  │  │  └──────────────┘  │   - PPE Detection     │  │    │            │
│  │  │                    │   - Compliance Check  │  │    │            │
│  │  │  ┌──────────────┐  └───────────────────────┘  │    │            │
│  │  │  │   Alert      │                              │    │            │
│  │  │  │   Manager    │  ┌───────────────────────┐  │    │            │
│  │  │  │              │  │   Storage Manager     │  │    │            │
│  │  │  └──────────────┘  │   - Image Storage     │  │    │            │
│  │  │                    │   - Path Management   │  │    │            │
│  │  │  ┌──────────────┐  └───────────────────────┘  │    │            │
│  │  │  │ Notification │                              │    │            │
│  │  │  │   Service    │  ┌───────────────────────┐  │    │            │
│  │  │  │ - Email      │  │   Analytics Service   │  │    │            │
│  │  │  │ - SMS        │  │   - Statistics        │  │    │            │
│  │  │  │ - Telegram   │  │   - Reporting         │  │    │            │
│  │  │  │ - Webhook    │  │   - Trends            │  │    │            │
│  │  │  └──────────────┘  └───────────────────────┘  │    │            │
│  │  │                                                 │    │            │
│  │  └─────────────────────────────────────────────────┘    │            │
│  │                                                          │            │
│  │  ┌────────────────────────────────────────────────┐    │            │
│  │  │             Data Access Layer                   │    │            │
│  │  ├────────────────────────────────────────────────┤    │            │
│  │  │  SQLAlchemy ORM  │  Redis Client  │ S3 Client  │    │            │
│  │  └────────────────────────────────────────────────┘    │            │
│  │                                                          │            │
│  └──────────────────────────────────────────────────────────┘            │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────┐           │
│  │         Celery Workers (Async Processing)                │           │
│  ├──────────────────────────────────────────────────────────┤           │
│  │  • Video Frame Processing                                │           │
│  │  • Batch Detection                                       │           │
│  │  • Report Generation                                     │           │
│  │  • Notification Dispatch                                 │           │
│  └──────────────────────────────────────────────────────────┘           │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────────────┐
│                       Data Layer                                        │
├────────────────────────────┼────────────────────────────────────────────┤
│                             │                                            │
│  ┌────────────────────┐    │    ┌────────────────────┐                 │
│  │   PostgreSQL       │◀───┼───▶│      Redis         │                 │
│  ├────────────────────┤    │    ├────────────────────┤                 │
│  │ • Cameras          │    │    │ • Session Cache    │                 │
│  │ • Violations       │    │    │ • Query Cache      │                 │
│  │ • Detection Logs   │    │    │ • Celery Queue     │                 │
│  │ • Zones            │    │    │ • Real-time State  │                 │
│  │ • Alerts           │    │    └────────────────────┘                 │
│  └────────────────────┘    │                                            │
│                             │                                            │
│  ┌────────────────────┐    │    ┌────────────────────┐                 │
│  │  File Storage      │◀───┼───▶│  Model Storage     │                 │
│  ├────────────────────┤    │    ├────────────────────┤                 │
│  │ • Detection Images │    │    │ • YOLO Models      │                 │
│  │ • Video Clips      │    │    │ • Optimized Models │                 │
│  │ • Reports          │    │    │ • TensorRT         │                 │
│  └────────────────────┘    │    └────────────────────┘                 │
│                             │                                            │
└────────────────────────────┼────────────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────────────┐
│                   Monitoring & Observability                            │
├────────────────────────────┼────────────────────────────────────────────┤
│                             │                                            │
│  ┌────────────────┐   ┌────┴────────┐   ┌────────────────┐            │
│  │  Prometheus    │◀──│   Metrics   │──▶│    Grafana     │            │
│  │  (Metrics)     │   │  Exporter   │   │  (Dashboards)  │            │
│  └────────────────┘   └─────────────┘   └────────────────┘            │
│                                                                          │
│  ┌────────────────┐   ┌─────────────┐   ┌────────────────┐            │
│  │  ELK Stack     │◀──│    Logs     │──▶│  Alertmanager  │            │
│  │  (Logs)        │   │             │   │  (Alerts)      │            │
│  └────────────────┘   └─────────────┘   └────────────────┘            │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Component Descriptions

### 1. API Gateway (Nginx)

**Purpose**: Entry point for all external requests

**Responsibilities**:
- SSL/TLS termination
- Load balancing across app instances
- Rate limiting
- Request routing
- Static file serving
- WebSocket proxying

**Configuration**:
```nginx
upstream app {
    least_conn;
    server app1:8000 weight=1;
    server app2:8000 weight=1;
    server app3:8000 weight=1;
}

server {
    listen 443 ssl http2;

    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws/ {
        proxy_pass http://app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 2. FastAPI Application

**Purpose**: Core application logic and API endpoints

**Key Modules**:
- **API Endpoints** (`src/api/endpoints.py`): RESTful API routes
- **Schemas** (`src/api/schemas.py`): Request/response validation
- **Dependencies** (`src/api/dependencies.py`): Dependency injection

**Design Patterns**:
- **Dependency Injection**: Database sessions, settings
- **Repository Pattern**: Database access abstraction
- **Service Layer**: Business logic separation

### 3. Detection Engine

**Purpose**: Computer vision and PPE detection

**Components**:
- **PPE Detector** (`src/models/ppe_detector.py`): YOLO-based detection
- **Model Optimizer** (`src/models/optimization/`): Model optimization
- **Inference Engine**: Batched inference processing

**Detection Pipeline**:
```python
Image/Frame → Preprocessing → YOLO Detection →
Person Detection → PPE Matching → Compliance Check →
Violation Recording → Alert Generation
```

**Models Used**:
- YOLOv8n/s/m for object detection
- Custom trained on construction PPE dataset
- TensorRT optimization for GPU inference

### 4. Camera Manager

**Purpose**: Manage camera streams and frame capture

**Features**:
- RTSP stream handling
- Automatic reconnection
- Frame buffering
- Multi-camera support
- Health monitoring

**Stream Processing**:
```python
RTSP Stream → Frame Capture → Frame Buffer →
Detection Queue → Processing → Result Storage
```

### 5. Alert Manager

**Purpose**: Manage violation alerts and notifications

**Features**:
- Alert rule engine
- De-duplication
- Throttling
- Escalation
- Multi-channel notifications

**Alert Flow**:
```python
Violation Detected → Rule Matching → Deduplication →
Throttle Check → Channel Selection → Notification Dispatch
```

**Supported Channels**:
- Email (SMTP)
- SMS (Twilio, AWS SNS)
- Telegram
- Webhook
- WebSocket (real-time)

### 6. Database Layer

**Purpose**: Persistent data storage

**PostgreSQL Tables**:
- `cameras` - Camera configurations
- `zones` - Site zone definitions
- `violations` - Violation records
- `detection_logs` - Detection history
- `alerts` - Alert records

**Optimizations**:
- Indexes on timestamp and camera_id
- Partitioning on timestamp (for large datasets)
- Connection pooling (20-40 connections)
- Read replicas (for reporting)

### 7. Cache Layer (Redis)

**Purpose**: High-speed caching and queuing

**Use Cases**:
- Session management
- Query result caching
- Celery task queue
- Real-time state (WebSocket)
- Rate limiting counters

**Cache Strategy**:
- TTL-based expiration (5-30 minutes)
- LRU eviction policy
- Separate databases for different purposes

### 8. Celery Workers

**Purpose**: Asynchronous background processing

**Tasks**:
- Video frame processing
- Batch detection
- Report generation
- Scheduled cleanups
- Email notifications
- Data aggregation

**Queue Configuration**:
```python
# High priority queue
detection_queue = Queue('detection', priority=10)

# Normal priority queue
notification_queue = Queue('notifications', priority=5)

# Low priority queue
reporting_queue = Queue('reports', priority=1)
```

### 9. Storage Layer

**Purpose**: File and object storage

**Storage Types**:
- **Local Storage**: Development and small deployments
- **NFS/SMB**: Shared storage for multi-instance
- **Object Storage**: S3, Azure Blob, GCS for cloud

**Organization**:
```
/data/
├── detections/
│   ├── 2024/
│   │   ├── 11/
│   │   │   ├── 18/
│   │   │   │   ├── det_20241118_123456.jpg
│   ├── thumbnails/
├── models/
│   ├── ppe_detection.pt
│   ├── ppe_detection_optimized.engine
├── videos/
│   ├── camera_1/
│   │   ├── 20241118_120000.mp4
└── reports/
    ├── daily/
    ├── weekly/
    └── monthly/
```

---

## Data Flow

### Detection Flow

```
┌─────────────────┐
│  Camera Stream  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Frame Capture   │ ◀── Every N seconds (configurable)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Frame Buffer   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ YOLO Detection  │ ◀── GPU/CPU inference
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Person Detection│ ◀── Filter person bboxes
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PPE Matching   │ ◀── Match PPE to persons
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Compliance Check │ ◀── Check required PPE
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
         ▼                 ▼
┌─────────────────┐  ┌──────────────┐
│ Save Detection  │  │Save Violation│
│   (All Cases)   │  │(If violated) │
└─────────────────┘  └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │Alert Manager │
                     └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │ Notification │
                     │   Dispatch   │
                     └──────────────┘
```

### API Request Flow

```
Client Request
    │
    ▼
Nginx (SSL, Load Balance)
    │
    ▼
FastAPI App
    │
    ├─▶ Request Validation (Pydantic)
    │
    ├─▶ Dependency Injection
    │   ├─ Database Session
    │   ├─ Settings
    │   └─ App State
    │
    ├─▶ Business Logic
    │   ├─ Service Layer
    │   └─ Repository Layer
    │
    ├─▶ Data Access
    │   ├─ PostgreSQL
    │   └─ Redis Cache
    │
    ├─▶ Response Formation
    │   └─ Pydantic Schema
    │
    ▼
Response to Client
```

---

## Technology Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.9-3.12 | Core language |
| **FastAPI** | 0.104+ | Web framework |
| **Uvicorn** | 0.24+ | ASGI server |
| **SQLAlchemy** | 2.0+ | ORM |
| **Alembic** | 1.13+ | Migrations |
| **Pydantic** | 2.0+ | Validation |
| **Celery** | 5.3+ | Task queue |

### Computer Vision & ML

| Technology | Version | Purpose |
|------------|---------|---------|
| **Ultralytics** | 8.0+ | YOLO models |
| **PyTorch** | 2.0+ | ML framework |
| **OpenCV** | 4.8+ | Image processing |
| **NumPy** | 1.24+ | Numerical computing |
| **Pillow** | 10.0+ | Image manipulation |

### Infrastructure

| Technology | Version | Purpose |
|------------|---------|---------|
| **PostgreSQL** | 16 | Primary database |
| **Redis** | 7 | Cache & queue |
| **Docker** | 20.10+ | Containerization |
| **Nginx** | 1.24+ | Reverse proxy |
| **Prometheus** | Latest | Metrics |
| **Grafana** | Latest | Visualization |

---

## Design Decisions

### 1. Why FastAPI?

**Decision**: Use FastAPI over Flask/Django

**Rationale**:
- **High Performance**: ASGI async support
- **Auto Documentation**: OpenAPI/Swagger built-in
- **Type Safety**: Pydantic validation
- **Modern**: Async/await, type hints
- **WebSocket**: Native support

**Trade-offs**:
- Smaller ecosystem than Django
- Newer (less mature)

### 2. Why PostgreSQL?

**Decision**: PostgreSQL over MySQL/MongoDB

**Rationale**:
- **ACID Compliance**: Data integrity
- **JSON Support**: Flexible metadata storage
- **Performance**: Excellent indexing
- **Extensions**: PostGIS, TimescaleDB ready
- **Scalability**: Proven at scale

### 3. Why YOLO?

**Decision**: YOLO over Faster R-CNN/SSD

**Rationale**:
- **Speed**: Real-time detection (30+ FPS)
- **Accuracy**: 95%+ on PPE detection
- **Community**: Active development
- **Flexibility**: Easy to train/fine-tune
- **Deployment**: Exportable to TensorRT, ONNX

### 4. Why Docker?

**Decision**: Container-based deployment

**Rationale**:
- **Consistency**: Same env everywhere
- **Scalability**: Easy horizontal scaling
- **Isolation**: Service independence
- **Portability**: Cloud-agnostic
- **DevOps**: CI/CD friendly

### 5. Stateless Application Design

**Decision**: Stateless app instances

**Rationale**:
- **Scalability**: Horizontal scaling
- **Reliability**: No single point of failure
- **Load Balancing**: Simple round-robin
- **Deployment**: Zero-downtime updates

**Implementation**:
- Session in Redis, not memory
- No in-memory caching
- Shared file storage (NFS/S3)

---

## Scalability Considerations

### Horizontal Scaling

**Application Layer**:
```bash
# Scale to 10 instances
docker-compose up -d --scale app=10
```

**Celery Workers**:
```bash
# Scale workers
docker-compose up -d --scale celery_worker=5
```

### Vertical Scaling

**Database**:
- Increase `shared_buffers`
- Increase `effective_cache_size`
- More CPU/RAM

**Application**:
- Increase worker count
- Larger batch sizes
- GPU acceleration

### Database Scaling

**Read Replicas**:
```python
# Write to primary
engine_write = create_engine(WRITE_DATABASE_URL)

# Read from replica
engine_read = create_engine(READ_DATABASE_URL)
```

**Partitioning**:
```sql
-- Partition violations by month
CREATE TABLE violations_2024_11 PARTITION OF violations
FOR VALUES FROM ('2024-11-01') TO ('2024-12-01');
```

### Caching Strategy

**Multi-Level Cache**:
1. **L1**: Application memory (10s TTL)
2. **L2**: Redis (5min TTL)
3. **L3**: Database query cache

**Cache Invalidation**:
- Time-based (TTL)
- Event-based (on write)

---

## Security Architecture

### Authentication & Authorization

**Current** (v0.1.0): No auth (MVP)

**Planned** (v0.2.0):
- API Key authentication
- JWT tokens
- Role-based access control (RBAC)

**Future** (v0.3.0):
- OAuth 2.0
- LDAP/AD integration
- SSO support

### Data Security

**At Rest**:
- Database encryption (PostgreSQL)
- Encrypted volumes (LUKS)
- Secrets management (Vault, AWS Secrets)

**In Transit**:
- TLS 1.2/1.3 only
- Strong cipher suites
- Certificate pinning

**Application**:
- Input validation (Pydantic)
- SQL injection prevention (ORM)
- XSS protection (headers)
- CSRF tokens

### Network Security

**Firewall Rules**:
- Minimal open ports
- Camera VLAN isolation
- Database not exposed

**DMZ Architecture**:
```
Internet → Firewall → DMZ (Nginx) →
Internal Network (App) →
Secure Network (Database)
```

---

## Database Schema

### ERD (Entity Relationship Diagram)

```
┌─────────────────┐
│     zones       │
├─────────────────┤
│ id (PK)         │
│ name            │
│ description     │
│ required_ppe    │─┐
│ created_at      │ │
│ updated_at      │ │
└─────────────────┘ │
                    │
         ┌──────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐        1:N        ┌─────────────────┐
│    cameras      │◀───────────────────│   violations    │
├─────────────────┤                    ├─────────────────┤
│ id (PK)         │                    │ id (PK)         │
│ name            │                    │ camera_id (FK)  │
│ rtsp_url        │                    │ timestamp       │
│ zone_id (FK)    │                    │ image_path      │
│ status          │                    │ violation_type  │
│ location        │                    │ confidence      │
│ is_active       │                    │ person_count    │
│ created_at      │                    │ bounding_boxes  │
│ updated_at      │                    │ acknowledged    │
│ last_heartbeat  │                    │ acknowledged_by │
└─────────────────┘                    │ acknowledged_at │
         │                             │ notes           │
         │                             │ created_at      │
         │                             └─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐        1:N        ┌─────────────────┐
│ detection_logs  │                    │     alerts      │
├─────────────────┤                    ├─────────────────┤
│ id (PK)         │                    │ id (PK)         │
│ camera_id (FK)  │                    │ camera_id (FK)  │
│ timestamp       │                    │ violation_id    │
│ total_persons   │                    │ alert_type      │
│ compliant_count │                    │ severity        │
│ violation_count │                    │ title           │
│ compliance_rate │                    │ message         │
│ processing_time │                    │ timestamp       │
│ frame_id        │                    │ resolved        │
│ metadata        │                    │ resolved_at     │
│ created_at      │                    │ resolved_by     │
└─────────────────┘                    │ metadata        │
                                       └─────────────────┘
```

For detailed schema, see [src/database/models.py](../src/database/models.py).

---

## API Architecture

### REST API Design

**Principles**:
- RESTful resources
- HTTP verbs (GET, POST, PUT, DELETE)
- Consistent naming (/resource/{id})
- Versioning ready (/api/v1/)

**Response Format**:
```json
{
  "id": 1,
  "name": "Resource",
  "created_at": "2024-11-18T12:34:56",
  "updated_at": "2024-11-18T12:34:56"
}
```

**Error Format**:
```json
{
  "error": "Error message",
  "detail": "Detailed description",
  "timestamp": "2024-11-18T12:34:56",
  "path": "/api/endpoint"
}
```

### WebSocket Architecture

**Purpose**: Real-time updates

**Flow**:
```python
Client → WS Connect → Subscribe to Camera →
Receive Detection Events → Display Updates
```

**Message Format**:
```json
{
  "type": "detection",
  "camera_id": 1,
  "data": {...},
  "timestamp": "2024-11-18T12:34:56"
}
```

---

## Detection Pipeline

### Pipeline Stages

```python
# 1. Frame Acquisition
frame = camera.read()

# 2. Preprocessing
frame = resize(frame, (640, 640))
frame = normalize(frame)

# 3. Inference
results = model.predict(frame)

# 4. Post-processing
persons = filter_class(results, 'person')
helmets = filter_class(results, 'helmet')
vests = filter_class(results, 'vest')

# 5. PPE Matching
for person in persons:
    has_helmet = check_ppe_near(person, helmets)
    has_vest = check_ppe_near(person, vests)

# 6. Compliance Check
is_compliant = has_helmet and has_vest

# 7. Violation Recording
if not is_compliant:
    save_violation(person, missing_ppe)

# 8. Alert Generation
if violation_count > threshold:
    trigger_alert(camera, violations)
```

### Performance Optimization

**Batching**:
```python
# Process multiple frames in batch
batch = collect_frames(batch_size=8)
results = model.predict_batch(batch)
```

**GPU Acceleration**:
```python
# Use CUDA for inference
model = YOLO('ppe_detection.pt').to('cuda')
```

**Model Optimization**:
```python
# Export to TensorRT for 3-5x speedup
model.export(format='engine')  # TensorRT
```

---

## Alert System

### Alert Rule Engine

**Rules**:
- Missing critical PPE (helmet)
- Multiple violations in timeframe
- Zone-specific requirements
- Repeat offenders

**Example Rule**:
```python
if violation.missing_ppe.contains('helmet'):
    priority = 'high'
    channels = ['email', 'sms', 'telegram']
elif violation_count > 3 in last_hour:
    priority = 'medium'
    channels = ['email', 'telegram']
```

### De-duplication

**Fingerprinting**:
```python
fingerprint = hash(f"{zone}:{camera}:{missing_ppe}")

if fingerprint in recent_alerts:
    suppress_duplicate()
else:
    send_alert()
    recent_alerts.add(fingerprint, ttl=300)
```

### Throttling

**Limits**:
- Max 60 alerts/hour per camera
- Max 100 alerts/hour system-wide
- Cooldown period: 5 minutes

---

For more details on implementation, see:
- [API Documentation](./API.md)
- [Setup Guide](./SETUP.md)
- [Deployment Guide](./DEPLOYMENT.md)
