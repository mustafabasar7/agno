# PPE Detection Database Layer

This module provides a complete database layer for the PPE (Personal Protective Equipment) detection system, including models, CRUD operations, and database migrations.

## Features

- **SQLAlchemy ORM Models**: Camera, Violation, DetectionLog, Zone, Alert
- **Database Support**: SQLite (development) and PostgreSQL (production)
- **Connection Pooling**: Optimized connection management
- **Async Support**: Full async/await support with asyncio
- **Migrations**: Alembic-based database migrations
- **CRUD Operations**: Comprehensive Create, Read, Update, Delete operations
- **Performance Indexes**: Optimized indexes for common queries

## Project Structure

```
database/
├── __init__.py              # Package exports
├── models.py                # SQLAlchemy models
├── database.py              # Database connection management
├── crud.py                  # CRUD operations
├── alembic.ini             # Alembic configuration
├── migrations/             # Database migrations
│   ├── env.py             # Migration environment
│   ├── script.py.mako     # Migration template
│   └── versions/          # Migration versions
│       └── 20241118_0000_initial_schema.py
└── README.md              # This file
```

## Installation

Install required dependencies:

```bash
# For SQLite (development)
pip install sqlalchemy alembic

# For PostgreSQL (production)
pip install sqlalchemy alembic psycopg2-binary

# For async support
pip install aiosqlite asyncpg
```

## Configuration

### Environment Variables

Configure the database using environment variables:

```bash
# SQLite (default)
export DB_TYPE=sqlite
export DB_PATH=./data/ppe_detection.db

# PostgreSQL
export DB_TYPE=postgresql
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=postgres
export DB_PASSWORD=your_password
export DB_NAME=ppe_detection

# Or use a full DATABASE_URL
export DATABASE_URL=postgresql://user:password@localhost:5432/ppe_detection
```

## Quick Start

### 1. Initialize Database

```python
from database import init_db

# Initialize with default configuration (SQLite)
db = init_db()

# Or specify a custom database URL
db = init_db("postgresql://user:pass@localhost/ppe_detection")
```

### 2. Create Tables

```python
# Using the database instance
db.create_tables()

# Or during initialization
db = init_db(create_tables=True)
```

### 3. Basic CRUD Operations

```python
from database import db, create_camera, create_violation, get_cameras
from database.models import CameraStatus, ViolationType

# Use session scope for transactions
with db.session_scope() as session:
    # Create a zone
    zone = create_zone(session, {
        "name": "Construction Area A",
        "description": "Main construction zone",
        "required_ppe": ["helmet", "vest", "boots"]
    })

    # Create a camera
    camera = create_camera(session, {
        "name": "Camera-01",
        "rtsp_url": "rtsp://192.168.1.100:554/stream",
        "zone_id": zone.id,
        "status": CameraStatus.ACTIVE
    })

    # Create a violation
    violation = create_violation(session, {
        "camera_id": camera.id,
        "image_path": "/data/violations/violation_001.jpg",
        "violation_type": ViolationType.NO_HELMET,
        "confidence": 0.95,
        "severity": "high"
    })

# Get all active cameras
cameras = get_cameras(db.get_session(), active_only=True)
for camera in cameras:
    print(f"{camera.name}: {camera.status}")
```

### 4. Query with Filters

```python
from datetime import datetime, timedelta
from database import get_violations, get_violation_stats

with db.session_scope() as session:
    # Get recent violations
    violations, total = get_violations(
        session,
        camera_id=1,
        start_date=datetime.now() - timedelta(days=7),
        acknowledged=False,
        limit=50
    )

    # Get statistics
    stats = get_violation_stats(
        session,
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now()
    )
    print(f"Total violations: {stats['total_violations']}")
    print(f"Average confidence: {stats['average_confidence']:.2f}")
```

## Database Migrations

### Initialize Migrations

From the database directory:

```bash
cd /home/user/agno/cookbook/construction_safety/ppe_detection/src/database
```

### Apply Migrations

```bash
# Run all pending migrations
alembic upgrade head

# Run specific migration
alembic upgrade 001

# Rollback one migration
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

### Create New Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new column to camera table"

# Create empty migration
alembic revision -m "Custom migration"
```

### Common Migration Commands

```bash
# Upgrade to latest
alembic upgrade head

# Downgrade to base
alembic downgrade base

# Show SQL without executing
alembic upgrade head --sql

# Offline SQL generation
alembic upgrade head --sql > migration.sql
```

## Async Usage

For async applications (e.g., FastAPI with async endpoints):

```python
from database import init_async_db, AsyncDatabase
import asyncio

async def main():
    # Initialize async database
    db = await init_async_db(create_tables=True)

    # Get async session
    async with db.SessionLocal() as session:
        # Perform async operations
        result = await session.execute(
            select(Camera).where(Camera.is_active == True)
        )
        cameras = result.scalars().all()

    # Close connections
    await db.close()

asyncio.run(main())
```

## Model Reference

### Camera
- **id**: Primary key
- **name**: Camera name (unique)
- **rtsp_url**: RTSP stream URL
- **zone_id**: Foreign key to Zone
- **status**: ACTIVE, INACTIVE, ERROR, MAINTENANCE
- **location**: Physical location
- **is_active**: Boolean flag
- **last_heartbeat**: Last connection timestamp

### Violation
- **id**: Primary key
- **camera_id**: Foreign key to Camera
- **timestamp**: When violation occurred
- **image_path**: Path to violation image
- **violation_type**: Type of PPE violation
- **confidence**: Detection confidence (0-1)
- **severity**: low, medium, high, critical
- **acknowledged**: Whether violation was reviewed
- **bounding_boxes**: JSON with detection coordinates
- **metadata**: Additional violation data

### DetectionLog
- **id**: Primary key
- **camera_id**: Foreign key to Camera
- **timestamp**: Detection timestamp
- **total_persons**: Total people detected
- **compliant_count**: People with proper PPE
- **violation_count**: People without proper PPE
- **compliance_rate**: Percentage (0-100)
- **processing_time_ms**: Detection processing time

### Zone
- **id**: Primary key
- **name**: Zone name (unique)
- **description**: Zone description
- **required_ppe**: JSON list of required PPE items

## Performance Optimization

### Indexes

The schema includes optimized indexes for:

- **Timestamp queries**: Fast time-based filtering
- **Camera lookups**: Efficient camera-based queries
- **Violation type filtering**: Quick violation categorization
- **Composite indexes**: Multi-column query optimization

### Connection Pooling

PostgreSQL configuration includes:
- Pool size: 5 permanent connections
- Max overflow: 10 additional connections
- Pool timeout: 30 seconds
- Connection recycling: 1 hour
- Pre-ping: Connection health checks

### Query Tips

```python
# Use pagination for large datasets
violations, total = get_violations(session, skip=0, limit=100)

# Filter at database level
cameras = get_cameras(session, active_only=True, zone_id=1)

# Use date ranges for time-series data
stats = get_violation_stats(
    session,
    start_date=datetime.now() - timedelta(days=7)
)
```

## Testing

```python
import pytest
from database import Database, DatabaseConfig

@pytest.fixture
def test_db():
    """Create test database."""
    config = DatabaseConfig(database_url="sqlite:///:memory:")
    db = Database(config)
    db.initialize()
    db.create_tables()
    yield db
    db.close()

def test_create_camera(test_db):
    """Test camera creation."""
    with test_db.session_scope() as session:
        camera = create_camera(session, {
            "name": "Test-Camera",
            "rtsp_url": "rtsp://test",
            "status": CameraStatus.ACTIVE
        })
        assert camera.id is not None
        assert camera.name == "Test-Camera"
```

## Troubleshooting

### SQLite Foreign Key Errors

Ensure foreign keys are enabled:
```python
# This is handled automatically by database.py
PRAGMA foreign_keys=ON
```

### PostgreSQL Connection Issues

Check connection parameters:
```bash
# Test connection
psql -h localhost -U postgres -d ppe_detection

# Check if database exists
psql -U postgres -c "\l"
```

### Migration Conflicts

```bash
# Check current version
alembic current

# Show pending migrations
alembic history

# Force set version
alembic stamp head
```

## Example Queries

### Get Violations by Camera and Date Range

```python
from datetime import datetime, timedelta

with db.session_scope() as session:
    violations, total = get_violations(
        session,
        camera_id=1,
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now(),
        violation_type=ViolationType.NO_HELMET,
        min_confidence=0.8,
        acknowledged=False,
        limit=100
    )
```

### Get Statistics Dashboard

```python
with db.session_scope() as session:
    # Violation statistics
    violation_stats = get_violation_stats(
        session,
        start_date=datetime.now() - timedelta(days=30)
    )

    # Detection statistics
    detection_stats = get_detection_stats(
        session,
        start_date=datetime.now() - timedelta(days=30)
    )

    print(f"Total Violations: {violation_stats['total_violations']}")
    print(f"Compliance Rate: {detection_stats['average_compliance_rate']:.2f}%")
```

### Update Camera Status

```python
from database import update_camera_status
from database.models import CameraStatus

with db.session_scope() as session:
    camera = update_camera_status(
        session,
        camera_id=1,
        status=CameraStatus.ACTIVE,
        update_heartbeat=True
    )
```

## License

This database layer is part of the PPE Detection system.
