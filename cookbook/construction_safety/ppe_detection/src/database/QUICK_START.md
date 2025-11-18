# Database Layer - Quick Start Guide

Complete guide to get started with the PPE Detection database layer in under 5 minutes.

## Installation

```bash
# Navigate to database directory
cd /home/user/agno/cookbook/construction_safety/ppe_detection/src/database

# Install dependencies
pip install -r requirements.txt
```

## Setup (SQLite - Development)

### Option 1: Using Python (Recommended)

```bash
# Run the migration helper
python migrate.py init
```

### Option 2: Using Alembic Directly

```bash
# Apply migrations
alembic upgrade head
```

### Option 3: From Python Code

```python
from database import init_db

# Initialize and create tables
db = init_db(create_tables=True)
```

## Setup (PostgreSQL - Production)

### 1. Create PostgreSQL Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE ppe_detection;
CREATE USER ppe_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE ppe_detection TO ppe_user;
\q
```

### 2. Configure Environment

```bash
# Create .env file
cp .env.example .env

# Edit .env
export DATABASE_URL=postgresql://ppe_user:secure_password@localhost:5432/ppe_detection
```

### 3. Run Migrations

```bash
# Apply migrations
python migrate.py init
```

## Migration Commands

### Using migrate.py (Recommended)

```bash
# Initialize new database
python migrate.py init

# Upgrade to latest version
python migrate.py upgrade

# Downgrade one version
python migrate.py downgrade

# Show current version
python migrate.py current

# Show migration history
python migrate.py history

# Create new migration (auto-generated from model changes)
python migrate.py create "Add new field"

# Create empty migration template
python migrate.py empty "Custom migration"

# Mark database as specific version without running migrations
python migrate.py stamp head

# Reset database (WARNING: deletes all data!)
python migrate.py reset
```

### Using Alembic Directly

```bash
# Navigate to database directory first
cd /home/user/agno/cookbook/construction_safety/ppe_detection/src/database

# Upgrade to latest
alembic upgrade head

# Upgrade to specific version
alembic upgrade 001

# Downgrade one version
alembic downgrade -1

# Downgrade to base (empty database)
alembic downgrade base

# Show current version with details
alembic current -v

# Show full migration history
alembic history --verbose

# Create auto-generated migration
alembic revision --autogenerate -m "Description"

# Create empty migration
alembic revision -m "Description"

# Show SQL without executing
alembic upgrade head --sql

# Generate offline migration script
alembic upgrade head --sql > migration.sql
```

## Example Queries

### Basic Setup

```python
from database import init_db, create_zone, create_camera, create_violation
from database.models import CameraStatus, ViolationType

# Initialize database
db = init_db(create_tables=True)
```

### Create Records

```python
with db.session_scope() as session:
    # Create a zone
    zone = create_zone(session, {
        "name": "Construction Area",
        "description": "Main construction zone",
        "required_ppe": ["helmet", "vest", "boots"]
    })
    print(f"Created zone: {zone.id}")

    # Create a camera
    camera = create_camera(session, {
        "name": "CAM-01",
        "rtsp_url": "rtsp://192.168.1.100:554/stream",
        "zone_id": zone.id,
        "status": CameraStatus.ACTIVE,
        "location": "North Entrance"
    })
    print(f"Created camera: {camera.id}")

    # Create a violation
    violation = create_violation(session, {
        "camera_id": camera.id,
        "image_path": "/data/violations/2024/11/18/001.jpg",
        "violation_type": ViolationType.NO_HELMET,
        "confidence": 0.95,
        "severity": "high",
        "person_count": 1
    })
    print(f"Created violation: {violation.id}")
```

### Query Records

```python
from database import get_cameras, get_violations, get_violation_stats
from datetime import datetime, timedelta

with db.session_scope() as session:
    # Get all active cameras
    cameras = get_cameras(session, active_only=True)
    for camera in cameras:
        print(f"{camera.name}: {camera.status.value}")

    # Get recent violations
    violations, total = get_violations(
        session,
        start_date=datetime.now() - timedelta(days=7),
        acknowledged=False,
        limit=10
    )
    print(f"Found {total} unacknowledged violations")

    # Get statistics
    stats = get_violation_stats(
        session,
        start_date=datetime.now() - timedelta(days=30)
    )
    print(f"Total violations: {stats['total_violations']}")
    print(f"Average confidence: {stats['average_confidence']:.2f}")
```

### Update Records

```python
from database import update_camera_status, acknowledge_violation

with db.session_scope() as session:
    # Update camera status
    camera = update_camera_status(
        session,
        camera_id=1,
        status=CameraStatus.ACTIVE
    )

    # Acknowledge violation
    violation = acknowledge_violation(
        session,
        violation_id=1,
        acknowledged_by="supervisor@example.com",
        notes="Worker warned and retrained"
    )
```

### Advanced Queries

```python
from database import get_violations
from datetime import datetime, timedelta

with db.session_scope() as session:
    # Get high-severity violations from last week
    violations, total = get_violations(
        session,
        start_date=datetime.now() - timedelta(days=7),
        severity="high",
        min_confidence=0.9,
        acknowledged=False,
        order_by="timestamp",
        order_desc=True,
        skip=0,
        limit=50
    )

    # Process violations
    for v in violations:
        print(f"[{v.timestamp}] {v.violation_type.value}")
        print(f"  Camera: {v.camera.name}")
        print(f"  Confidence: {v.confidence:.2%}")
        print(f"  Severity: {v.severity}")
```

## Complete Example Script

Save this as `test_database.py`:

```python
from database import (
    init_db,
    create_zone,
    create_camera,
    create_violation,
    get_cameras,
    get_violations,
    get_violation_stats,
    CameraStatus,
    ViolationType
)
from datetime import datetime, timedelta

def main():
    # Initialize database
    print("Initializing database...")
    db = init_db(create_tables=True)

    with db.session_scope() as session:
        # Create zone
        zone = create_zone(session, {
            "name": "Test Zone",
            "required_ppe": ["helmet", "vest"]
        })
        print(f"✓ Created zone: {zone.name}")

        # Create camera
        camera = create_camera(session, {
            "name": "TEST-CAM-01",
            "rtsp_url": "rtsp://test",
            "zone_id": zone.id,
            "status": CameraStatus.ACTIVE
        })
        print(f"✓ Created camera: {camera.name}")

        # Create violation
        violation = create_violation(session, {
            "camera_id": camera.id,
            "image_path": "/data/test.jpg",
            "violation_type": ViolationType.NO_HELMET,
            "confidence": 0.95
        })
        print(f"✓ Created violation: ID {violation.id}")

        # Query cameras
        cameras = get_cameras(session)
        print(f"✓ Found {len(cameras)} cameras")

        # Query violations
        violations, total = get_violations(session)
        print(f"✓ Found {total} violations")

        # Get statistics
        stats = get_violation_stats(session)
        print(f"✓ Statistics: {stats['total_violations']} total violations")

    print("\n✓ All tests passed!")
    db.close()

if __name__ == "__main__":
    main()
```

Run with:

```bash
python test_database.py
```

## Run Full Examples

```bash
# Run all examples
python examples.py
```

This will:
1. Initialize database
2. Create sample zones, cameras, and violations
3. Demonstrate all CRUD operations
4. Show filtering and pagination
5. Display statistics

## Testing

### Unit Tests

```python
import pytest
from database import Database, DatabaseConfig, create_camera

@pytest.fixture
def test_db():
    config = DatabaseConfig(database_url="sqlite:///:memory:")
    db = Database(config)
    db.initialize()
    db.create_tables()
    yield db
    db.close()

def test_camera_creation(test_db):
    with test_db.session_scope() as session:
        camera = create_camera(session, {
            "name": "Test Camera",
            "rtsp_url": "rtsp://test",
            "status": "active"
        })
        assert camera.id is not None
```

### Integration Tests

```bash
# Run pytest
pytest -v
```

## Common Issues

### Issue: Module not found

```bash
# Install dependencies
pip install -r requirements.txt
```

### Issue: Database locked (SQLite)

```bash
# Close all connections
# Or delete the database file and reinitialize
rm data/ppe_detection.db
python migrate.py init
```

### Issue: Migration conflicts

```bash
# Check current version
alembic current

# Reset to head
alembic stamp head
```

### Issue: Foreign key constraint errors

```bash
# For SQLite, ensure foreign keys are enabled (automatic in our setup)
# For PostgreSQL, check constraint definitions
```

## Performance Tips

1. **Use indexes**: Already configured for common queries
2. **Use pagination**: Always specify `limit` for large datasets
3. **Use connection pooling**: Automatic for PostgreSQL
4. **Batch operations**: Use transactions for multiple writes
5. **Filter at database**: Use query parameters instead of filtering in Python

## Next Steps

1. Read the [Full README](README.md) for detailed documentation
2. Review [Migration Guide](MIGRATIONS.md) for advanced migrations
3. Explore [examples.py](examples.py) for more usage patterns
4. Check [models.py](models.py) to understand the schema
5. Review [crud.py](crud.py) for available operations

## Support

For issues or questions:
1. Check the README.md and MIGRATIONS.md
2. Review examples.py for usage patterns
3. Check Alembic and SQLAlchemy documentation
