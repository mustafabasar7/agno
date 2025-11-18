"""Initial schema for PPE detection system

Revision ID: 001
Revises:
Create Date: 2024-11-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database schema."""

    # Create zones table
    op.create_table(
        'zones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('required_ppe', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_zones_id'), 'zones', ['id'], unique=False)
    op.create_index(op.f('ix_zones_name'), 'zones', ['name'], unique=True)

    # Create cameras table
    op.create_table(
        'cameras',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('rtsp_url', sa.String(length=500), nullable=False),
        sa.Column('zone_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'ERROR', 'MAINTENANCE',
                                     name='camerastatus'), nullable=False),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('fps', sa.Integer(), nullable=True),
        sa.Column('resolution', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_heartbeat', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['zone_id'], ['zones.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cameras_id'), 'cameras', ['id'], unique=False)
    op.create_index(op.f('ix_cameras_name'), 'cameras', ['name'], unique=True)
    op.create_index(op.f('ix_cameras_status'), 'cameras', ['status'], unique=False)
    op.create_index(op.f('ix_cameras_zone_id'), 'cameras', ['zone_id'], unique=False)

    # Create violations table
    op.create_table(
        'violations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('camera_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('image_path', sa.String(length=500), nullable=False),
        sa.Column('violation_type', sa.Enum('NO_HELMET', 'NO_VEST', 'NO_GLOVES',
                                             'NO_BOOTS', 'NO_GOGGLES', 'MULTIPLE',
                                             name='violationtype'), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('person_count', sa.Integer(), nullable=True),
        sa.Column('bounding_boxes', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('severity', sa.String(length=20), nullable=True),
        sa.Column('acknowledged', sa.Boolean(), nullable=False),
        sa.Column('acknowledged_by', sa.String(length=100), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['camera_id'], ['cameras.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_violations_id'), 'violations', ['id'], unique=False)
    op.create_index(op.f('ix_violations_camera_id'), 'violations', ['camera_id'], unique=False)
    op.create_index(op.f('ix_violations_timestamp'), 'violations', ['timestamp'], unique=False)
    op.create_index(op.f('ix_violations_violation_type'), 'violations', ['violation_type'], unique=False)
    op.create_index('idx_violation_camera_timestamp', 'violations', ['camera_id', 'timestamp'], unique=False)
    op.create_index('idx_violation_type_timestamp', 'violations', ['violation_type', 'timestamp'], unique=False)
    op.create_index('idx_violation_timestamp_acknowledged', 'violations', ['timestamp', 'acknowledged'], unique=False)

    # Create detection_logs table
    op.create_table(
        'detection_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('camera_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('total_persons', sa.Integer(), nullable=False),
        sa.Column('compliant_count', sa.Integer(), nullable=False),
        sa.Column('violation_count', sa.Integer(), nullable=False),
        sa.Column('compliance_rate', sa.Float(), nullable=True),
        sa.Column('processing_time_ms', sa.Float(), nullable=True),
        sa.Column('frame_id', sa.String(length=100), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['camera_id'], ['cameras.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_detection_logs_id'), 'detection_logs', ['id'], unique=False)
    op.create_index(op.f('ix_detection_logs_camera_id'), 'detection_logs', ['camera_id'], unique=False)
    op.create_index(op.f('ix_detection_logs_timestamp'), 'detection_logs', ['timestamp'], unique=False)
    op.create_index('idx_detectionlog_camera_timestamp', 'detection_logs', ['camera_id', 'timestamp'], unique=False)
    op.create_index('idx_detectionlog_timestamp', 'detection_logs', ['timestamp'], unique=False)

    # Create alerts table
    op.create_table(
        'alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('camera_id', sa.Integer(), nullable=False),
        sa.Column('violation_id', sa.Integer(), nullable=True),
        sa.Column('alert_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('resolved', sa.Boolean(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by', sa.String(length=100), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['camera_id'], ['cameras.id'], ),
        sa.ForeignKeyConstraint(['violation_id'], ['violations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alerts_id'), 'alerts', ['id'], unique=False)
    op.create_index(op.f('ix_alerts_camera_id'), 'alerts', ['camera_id'], unique=False)
    op.create_index(op.f('ix_alerts_timestamp'), 'alerts', ['timestamp'], unique=False)
    op.create_index(op.f('ix_alerts_alert_type'), 'alerts', ['alert_type'], unique=False)
    op.create_index('idx_alert_timestamp_resolved', 'alerts', ['timestamp', 'resolved'], unique=False)
    op.create_index('idx_alert_severity_resolved', 'alerts', ['severity', 'resolved'], unique=False)


def downgrade() -> None:
    """Drop all tables."""

    op.drop_index('idx_alert_severity_resolved', table_name='alerts')
    op.drop_index('idx_alert_timestamp_resolved', table_name='alerts')
    op.drop_index(op.f('ix_alerts_alert_type'), table_name='alerts')
    op.drop_index(op.f('ix_alerts_timestamp'), table_name='alerts')
    op.drop_index(op.f('ix_alerts_camera_id'), table_name='alerts')
    op.drop_index(op.f('ix_alerts_id'), table_name='alerts')
    op.drop_table('alerts')

    op.drop_index('idx_detectionlog_timestamp', table_name='detection_logs')
    op.drop_index('idx_detectionlog_camera_timestamp', table_name='detection_logs')
    op.drop_index(op.f('ix_detection_logs_timestamp'), table_name='detection_logs')
    op.drop_index(op.f('ix_detection_logs_camera_id'), table_name='detection_logs')
    op.drop_index(op.f('ix_detection_logs_id'), table_name='detection_logs')
    op.drop_table('detection_logs')

    op.drop_index('idx_violation_timestamp_acknowledged', table_name='violations')
    op.drop_index('idx_violation_type_timestamp', table_name='violations')
    op.drop_index('idx_violation_camera_timestamp', table_name='violations')
    op.drop_index(op.f('ix_violations_violation_type'), table_name='violations')
    op.drop_index(op.f('ix_violations_timestamp'), table_name='violations')
    op.drop_index(op.f('ix_violations_camera_id'), table_name='violations')
    op.drop_index(op.f('ix_violations_id'), table_name='violations')
    op.drop_table('violations')

    op.drop_index(op.f('ix_cameras_zone_id'), table_name='cameras')
    op.drop_index(op.f('ix_cameras_status'), table_name='cameras')
    op.drop_index(op.f('ix_cameras_name'), table_name='cameras')
    op.drop_index(op.f('ix_cameras_id'), table_name='cameras')
    op.drop_table('cameras')

    op.drop_index(op.f('ix_zones_name'), table_name='zones')
    op.drop_index(op.f('ix_zones_id'), table_name='zones')
    op.drop_table('zones')
