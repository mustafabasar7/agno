# Database Migrations Guide

This guide explains how to manage database migrations for the PPE Detection system.

## Quick Reference

```bash
# Navigate to database directory
cd /home/user/agno/cookbook/construction_safety/ppe_detection/src/database

# Initialize new database
python migrate.py init

# Apply all pending migrations
python migrate.py upgrade

# Rollback one migration
python migrate.py downgrade

# Show current version
python migrate.py current

# View migration history
python migrate.py history

# Create new migration
python migrate.py create "Add new field to camera"

# Reset database (WARNING: deletes all data)
python migrate.py reset
```

## Using Alembic Directly

If you prefer to use Alembic directly:

```bash
# All commands must be run from the database directory
cd /home/user/agno/cookbook/construction_safety/ppe_detection/src/database

# Upgrade to latest
alembic upgrade head

# Upgrade to specific version
alembic upgrade 001

# Downgrade one version
alembic downgrade -1

# Downgrade to base
alembic downgrade base

# Show current version
alembic current

# Show migration history
alembic history --verbose

# Create new auto-generated migration
alembic revision --autogenerate -m "Add new column"

# Create empty migration template
alembic revision -m "Custom migration"

# Show SQL without executing
alembic upgrade head --sql

# Generate offline SQL script
alembic upgrade head --sql > migration.sql
```

## Migration Workflow

### 1. Development Setup

```bash
# Clone repository
git clone <repo-url>
cd cookbook/construction_safety/ppe_detection/src/database

# Install dependencies
pip install -r requirements.txt

# Configure database
cp .env.example .env
# Edit .env with your settings

# Initialize database
python migrate.py init
```

### 2. Making Model Changes

When you modify models in `models.py`:

```bash
# Create auto-generated migration
python migrate.py create "Description of changes"

# Review the generated migration in migrations/versions/
# Edit if necessary

# Apply the migration
python migrate.py upgrade

# Test the changes
python examples.py
```

### 3. Sharing Migrations

```bash
# Commit migration files to git
git add migrations/versions/*.py
git commit -m "Add migration for new camera fields"
git push

# Other developers pull and apply
git pull
python migrate.py upgrade
```

### 4. Production Deployment

```bash
# On production server
cd /path/to/ppe_detection/src/database

# Backup database first!
pg_dump ppe_detection > backup_$(date +%Y%m%d_%H%M%S).sql

# Apply migrations
python migrate.py upgrade

# Verify
python migrate.py current
```

## Migration Examples

### Example 1: Add Column to Existing Table

```python
# In models.py, add new field
class Camera(Base):
    # ... existing fields ...
    location_coordinates = Column(String(100), nullable=True)

# Create migration
$ python migrate.py create "Add location coordinates to camera"

# Generated migration (edit if needed)
def upgrade():
    op.add_column('cameras',
        sa.Column('location_coordinates', sa.String(100), nullable=True)
    )

def downgrade():
    op.drop_column('cameras', 'location_coordinates')

# Apply
$ python migrate.py upgrade
```

### Example 2: Modify Column Type

```python
# migrations/versions/xxx_change_confidence_precision.py
def upgrade():
    # PostgreSQL
    op.alter_column('violations', 'confidence',
        type_=sa.Numeric(precision=5, scale=4),
        existing_type=sa.Float()
    )

def downgrade():
    op.alter_column('violations', 'confidence',
        type_=sa.Float(),
        existing_type=sa.Numeric(precision=5, scale=4)
    )
```

### Example 3: Add Index

```python
def upgrade():
    op.create_index(
        'idx_camera_zone_status',
        'cameras',
        ['zone_id', 'status'],
        unique=False
    )

def downgrade():
    op.drop_index('idx_camera_zone_status', table_name='cameras')
```

### Example 4: Data Migration

```python
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

def upgrade():
    # Add new column
    op.add_column('cameras', sa.Column('is_ptz', sa.Boolean(), nullable=True))

    # Migrate existing data
    cameras = table('cameras',
        column('is_ptz', sa.Boolean()),
        column('name', sa.String())
    )

    op.execute(
        cameras.update().
        where(cameras.c.name.like('PTZ%')).
        values({'is_ptz': True})
    )

    # Set default for remaining
    op.execute(
        cameras.update().
        where(cameras.c.is_ptz.is_(None)).
        values({'is_ptz': False})
    )

    # Make column non-nullable
    op.alter_column('cameras', 'is_ptz', nullable=False)

def downgrade():
    op.drop_column('cameras', 'is_ptz')
```

## Troubleshooting

### Issue: "Can't locate revision identified by 'xxx'"

```bash
# Check current version
alembic current

# If empty or wrong, stamp with correct version
alembic stamp head

# Or reset to base
alembic stamp base
alembic upgrade head
```

### Issue: "Target database is not up to date"

```bash
# Check pending migrations
alembic history

# Apply all pending
alembic upgrade head
```

### Issue: Migration conflicts after merge

```bash
# Check for multiple head revisions
alembic heads

# If multiple heads, create merge migration
alembic merge -m "Merge heads" head1 head2
```

### Issue: Need to rollback in production

```bash
# Backup first!
pg_dump ppe_detection > backup.sql

# Rollback one version
alembic downgrade -1

# Or rollback to specific version
alembic downgrade abc123

# Verify
alembic current
```

### Issue: SQLite locked database

```bash
# Check for running processes
lsof data/ppe_detection.db

# Kill processes if necessary
kill -9 <PID>

# Or use the migration tool which handles locks better
python migrate.py upgrade
```

## Best Practices

1. **Always backup before migrations in production**
   ```bash
   pg_dump dbname > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Test migrations on copy of production data**
   ```bash
   # Restore backup to test database
   createdb ppe_detection_test
   psql ppe_detection_test < backup.sql

   # Test migration
   DATABASE_URL=postgresql://user:pass@localhost/ppe_detection_test
   python migrate.py upgrade
   ```

3. **Review auto-generated migrations**
   - Alembic may not detect all changes
   - Check column types, constraints, indexes
   - Add data migrations if needed

4. **Write reversible migrations**
   - Always implement `downgrade()`
   - Test rollback scenarios
   - Document destructive changes

5. **Keep migrations small and focused**
   - One logical change per migration
   - Easier to review and rollback
   - Better for team collaboration

6. **Use transactions**
   ```python
   # Migrations run in transactions by default
   # But be aware of DDL limitations in some databases
   ```

7. **Version control**
   - Commit migrations with code changes
   - Never modify existing migrations in production
   - Create new migration to fix issues

## Environment-Specific Migrations

### SQLite to PostgreSQL Migration

```bash
# Export SQLite data
sqlite3 data/ppe_detection.db .dump > sqlite_dump.sql

# Convert to PostgreSQL (may need manual editing)
# Then import to PostgreSQL
psql ppe_detection < converted_dump.sql

# Stamp with current version
DATABASE_URL=postgresql://... alembic stamp head
```

### Multiple Environments

```bash
# Development (SQLite)
export DATABASE_URL=sqlite:///./data/dev.db
python migrate.py upgrade

# Staging (PostgreSQL)
export DATABASE_URL=postgresql://user:pass@staging/ppe_detection
python migrate.py upgrade

# Production (PostgreSQL)
export DATABASE_URL=postgresql://user:pass@prod/ppe_detection
python migrate.py upgrade
```

## Migration Checklist

Before deploying migrations to production:

- [ ] Tested on development database
- [ ] Tested on staging database with production-like data
- [ ] Reviewed migration SQL
- [ ] Verified downgrade path works
- [ ] Database backup created
- [ ] Estimated migration time
- [ ] Planned for rollback if needed
- [ ] Notified team of deployment
- [ ] Prepared monitoring for migration progress

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
