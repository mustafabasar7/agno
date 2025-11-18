"""
SQLAlchemy models for PPE detection system.

This module defines the database schema including cameras, violations,
detection logs, and zones.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
    Text,
    JSON,
    Index,
    Enum as SQLEnum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class CameraStatus(str, enum.Enum):
    """Camera status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class ViolationType(str, enum.Enum):
    """PPE violation types."""
    NO_HELMET = "no_helmet"
    NO_VEST = "no_vest"
    NO_GLOVES = "no_gloves"
    NO_BOOTS = "no_boots"
    NO_GOGGLES = "no_goggles"
    MULTIPLE = "multiple"


class Zone(Base):
    """
    Zone model representing different areas in the construction site.

    Each zone can have different PPE requirements.
    """
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    required_ppe = Column(JSON, nullable=False)  # List of required PPE items
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cameras = relationship("Camera", back_populates="zone", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Zone(id={self.id}, name='{self.name}')>"


class Camera(Base):
    """
    Camera model representing video surveillance cameras.

    Each camera is assigned to a zone and monitors PPE compliance.
    """
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    rtsp_url = Column(String(500), nullable=False)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=True, index=True)
    status = Column(
        SQLEnum(CameraStatus),
        default=CameraStatus.INACTIVE,
        nullable=False,
        index=True
    )
    location = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    fps = Column(Integer, default=30)
    resolution = Column(String(20), default="1920x1080")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_heartbeat = Column(DateTime, nullable=True)

    # Relationships
    zone = relationship("Zone", back_populates="cameras")
    violations = relationship("Violation", back_populates="camera", cascade="all, delete-orphan")
    detection_logs = relationship("DetectionLog", back_populates="camera", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Camera(id={self.id}, name='{self.name}', status='{self.status}')>"


class Violation(Base):
    """
    Violation model for recording PPE violations detected by cameras.

    Stores information about each violation including image evidence,
    confidence scores, and metadata.
    """
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    image_path = Column(String(500), nullable=False)
    violation_type = Column(
        SQLEnum(ViolationType),
        nullable=False,
        index=True
    )
    confidence = Column(Float, nullable=False)
    person_count = Column(Integer, default=1)
    bounding_boxes = Column(JSON, nullable=True)  # Store detection coordinates
    metadata = Column(JSON, nullable=True)  # Additional violation details
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    camera = relationship("Camera", back_populates="violations")

    # Indexes for common queries
    __table_args__ = (
        Index('idx_violation_camera_timestamp', 'camera_id', 'timestamp'),
        Index('idx_violation_type_timestamp', 'violation_type', 'timestamp'),
        Index('idx_violation_timestamp_acknowledged', 'timestamp', 'acknowledged'),
    )

    def __repr__(self):
        return f"<Violation(id={self.id}, type='{self.violation_type}', camera_id={self.camera_id})>"


class DetectionLog(Base):
    """
    Detection log model for tracking overall detection statistics.

    Records aggregate statistics for each detection cycle including
    total persons detected, compliant count, and violations.
    """
    __tablename__ = "detection_logs"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    total_persons = Column(Integer, default=0, nullable=False)
    compliant_count = Column(Integer, default=0, nullable=False)
    violation_count = Column(Integer, default=0, nullable=False)
    compliance_rate = Column(Float, nullable=True)  # Percentage
    processing_time_ms = Column(Float, nullable=True)  # Detection processing time
    frame_id = Column(String(100), nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional detection metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    camera = relationship("Camera", back_populates="detection_logs")

    # Indexes for time-series queries
    __table_args__ = (
        Index('idx_detectionlog_camera_timestamp', 'camera_id', 'timestamp'),
        Index('idx_detectionlog_timestamp', 'timestamp'),
    )

    def __repr__(self):
        return f"<DetectionLog(id={self.id}, camera_id={self.camera_id}, persons={self.total_persons})>"


class Alert(Base):
    """
    Alert model for critical violations that require immediate attention.

    Generated when violations exceed certain thresholds or critical PPE
    requirements are not met.
    """
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False, index=True)
    violation_id = Column(Integer, ForeignKey("violations.id"), nullable=True)
    alert_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), default="medium", nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    resolved = Column(Boolean, default=False, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(100), nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    camera = relationship("Camera")
    violation = relationship("Violation")

    # Indexes
    __table_args__ = (
        Index('idx_alert_timestamp_resolved', 'timestamp', 'resolved'),
        Index('idx_alert_severity_resolved', 'severity', 'resolved'),
    )

    def __repr__(self):
        return f"<Alert(id={self.id}, type='{self.alert_type}', severity='{self.severity}')>"
