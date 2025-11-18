"""
Database package for PPE detection system.

This package provides database models, connection management,
and CRUD operations for the PPE detection application.
"""

from .models import (
    Base,
    Camera,
    Violation,
    DetectionLog,
    Zone,
    Alert,
    CameraStatus,
    ViolationType,
)

from .database import (
    Database,
    AsyncDatabase,
    DatabaseConfig,
    db,
    async_db,
    get_db,
    get_async_db,
    init_db,
    init_async_db,
)

from .crud import (
    # Camera operations
    create_camera,
    get_camera,
    get_camera_by_name,
    get_cameras,
    update_camera_status,
    update_camera,
    delete_camera,
    # Violation operations
    create_violation,
    get_violation,
    get_violations,
    get_violation_stats,
    acknowledge_violation,
    # Detection log operations
    create_detection_log,
    get_detection_logs,
    get_detection_stats,
    # Zone operations
    create_zone,
    get_zone,
    get_zones,
    update_zone,
    delete_zone,
    # Alert operations
    create_alert,
    get_alerts,
    resolve_alert,
)

__all__ = [
    # Models
    "Base",
    "Camera",
    "Violation",
    "DetectionLog",
    "Zone",
    "Alert",
    "CameraStatus",
    "ViolationType",
    # Database
    "Database",
    "AsyncDatabase",
    "DatabaseConfig",
    "db",
    "async_db",
    "get_db",
    "get_async_db",
    "init_db",
    "init_async_db",
    # CRUD - Camera
    "create_camera",
    "get_camera",
    "get_camera_by_name",
    "get_cameras",
    "update_camera_status",
    "update_camera",
    "delete_camera",
    # CRUD - Violation
    "create_violation",
    "get_violation",
    "get_violations",
    "get_violation_stats",
    "acknowledge_violation",
    # CRUD - Detection Log
    "create_detection_log",
    "get_detection_logs",
    "get_detection_stats",
    # CRUD - Zone
    "create_zone",
    "get_zone",
    "get_zones",
    "update_zone",
    "delete_zone",
    # CRUD - Alert
    "create_alert",
    "get_alerts",
    "resolve_alert",
]

__version__ = "1.0.0"
