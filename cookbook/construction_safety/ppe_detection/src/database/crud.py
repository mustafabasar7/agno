"""
CRUD operations for PPE detection database.

This module provides Create, Read, Update, Delete operations
for all database models with filtering, pagination, and statistics.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.exc import IntegrityError
import logging

from .models import Camera, Violation, DetectionLog, Zone, Alert, CameraStatus, ViolationType

logger = logging.getLogger(__name__)


# ============================================================================
# CAMERA CRUD OPERATIONS
# ============================================================================

def create_camera(db: Session, camera_data: Dict[str, Any]) -> Camera:
    """
    Create a new camera.

    Args:
        db: Database session.
        camera_data: Dictionary containing camera configuration.

    Returns:
        Created camera object.

    Example:
        camera = create_camera(db, {
            "name": "Camera-01",
            "rtsp_url": "rtsp://192.168.1.100:554/stream",
            "zone_id": 1,
            "status": "active"
        })
    """
    try:
        camera = Camera(**camera_data)
        db.add(camera)
        db.commit()
        db.refresh(camera)
        logger.info(f"Created camera: {camera.name} (ID: {camera.id})")
        return camera
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error creating camera: {e}")
        raise ValueError(f"Camera with name '{camera_data.get('name')}' already exists")


def get_camera(db: Session, camera_id: int) -> Optional[Camera]:
    """
    Get camera by ID.

    Args:
        db: Database session.
        camera_id: Camera ID.

    Returns:
        Camera object or None.
    """
    return db.query(Camera).filter(Camera.id == camera_id).first()


def get_camera_by_name(db: Session, name: str) -> Optional[Camera]:
    """
    Get camera by name.

    Args:
        db: Database session.
        name: Camera name.

    Returns:
        Camera object or None.
    """
    return db.query(Camera).filter(Camera.name == name).first()


def get_cameras(
    db: Session,
    active_only: bool = True,
    zone_id: Optional[int] = None,
    status: Optional[CameraStatus] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Camera]:
    """
    Get list of cameras with optional filtering.

    Args:
        db: Database session.
        active_only: Only return active cameras.
        zone_id: Filter by zone ID.
        status: Filter by camera status.
        skip: Number of records to skip (pagination).
        limit: Maximum number of records to return.

    Returns:
        List of camera objects.

    Example:
        cameras = get_cameras(db, active_only=True, zone_id=1, limit=10)
    """
    query = db.query(Camera)

    if active_only:
        query = query.filter(Camera.is_active == True)

    if zone_id is not None:
        query = query.filter(Camera.zone_id == zone_id)

    if status is not None:
        query = query.filter(Camera.status == status)

    return query.offset(skip).limit(limit).all()


def update_camera_status(
    db: Session,
    camera_id: int,
    status: CameraStatus,
    update_heartbeat: bool = True
) -> Optional[Camera]:
    """
    Update camera status.

    Args:
        db: Database session.
        camera_id: Camera ID.
        status: New camera status.
        update_heartbeat: Whether to update last_heartbeat timestamp.

    Returns:
        Updated camera object or None.

    Example:
        camera = update_camera_status(db, 1, CameraStatus.ACTIVE)
    """
    camera = get_camera(db, camera_id)
    if camera:
        camera.status = status
        if update_heartbeat:
            camera.last_heartbeat = datetime.utcnow()
        db.commit()
        db.refresh(camera)
        logger.info(f"Updated camera {camera_id} status to {status}")
    return camera


def update_camera(db: Session, camera_id: int, update_data: Dict[str, Any]) -> Optional[Camera]:
    """
    Update camera with arbitrary fields.

    Args:
        db: Database session.
        camera_id: Camera ID.
        update_data: Dictionary of fields to update.

    Returns:
        Updated camera object or None.
    """
    camera = get_camera(db, camera_id)
    if camera:
        for key, value in update_data.items():
            if hasattr(camera, key):
                setattr(camera, key, value)
        db.commit()
        db.refresh(camera)
        logger.info(f"Updated camera {camera_id}")
    return camera


def delete_camera(db: Session, camera_id: int) -> bool:
    """
    Delete camera by ID.

    Args:
        db: Database session.
        camera_id: Camera ID.

    Returns:
        True if deleted, False if not found.
    """
    camera = get_camera(db, camera_id)
    if camera:
        db.delete(camera)
        db.commit()
        logger.info(f"Deleted camera {camera_id}")
        return True
    return False


# ============================================================================
# VIOLATION CRUD OPERATIONS
# ============================================================================

def create_violation(db: Session, violation_data: Dict[str, Any]) -> Violation:
    """
    Create a new violation record.

    Args:
        db: Database session.
        violation_data: Dictionary containing violation data.

    Returns:
        Created violation object.

    Example:
        violation = create_violation(db, {
            "camera_id": 1,
            "image_path": "/data/violations/2024-01-01/violation_001.jpg",
            "violation_type": ViolationType.NO_HELMET,
            "confidence": 0.95,
            "person_count": 1,
            "severity": "high"
        })
    """
    violation = Violation(**violation_data)
    db.add(violation)
    db.commit()
    db.refresh(violation)
    logger.info(f"Created violation: {violation.id} (Type: {violation.violation_type})")
    return violation


def get_violation(db: Session, violation_id: int) -> Optional[Violation]:
    """
    Get violation by ID.

    Args:
        db: Database session.
        violation_id: Violation ID.

    Returns:
        Violation object or None.
    """
    return db.query(Violation).filter(Violation.id == violation_id).first()


def get_violations(
    db: Session,
    camera_id: Optional[int] = None,
    violation_type: Optional[ViolationType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    acknowledged: Optional[bool] = None,
    severity: Optional[str] = None,
    min_confidence: Optional[float] = None,
    skip: int = 0,
    limit: int = 100,
    order_by: str = "timestamp",
    order_desc: bool = True,
) -> Tuple[List[Violation], int]:
    """
    Get violations with comprehensive filtering and pagination.

    Args:
        db: Database session.
        camera_id: Filter by camera ID.
        violation_type: Filter by violation type.
        start_date: Filter violations after this date.
        end_date: Filter violations before this date.
        acknowledged: Filter by acknowledgment status.
        severity: Filter by severity level.
        min_confidence: Minimum confidence threshold.
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        order_by: Field to order by.
        order_desc: Order descending if True.

    Returns:
        Tuple of (list of violations, total count).

    Example:
        violations, total = get_violations(
            db,
            camera_id=1,
            start_date=datetime.now() - timedelta(days=7),
            acknowledged=False,
            limit=50
        )
    """
    query = db.query(Violation)

    # Apply filters
    if camera_id is not None:
        query = query.filter(Violation.camera_id == camera_id)

    if violation_type is not None:
        query = query.filter(Violation.violation_type == violation_type)

    if start_date is not None:
        query = query.filter(Violation.timestamp >= start_date)

    if end_date is not None:
        query = query.filter(Violation.timestamp <= end_date)

    if acknowledged is not None:
        query = query.filter(Violation.acknowledged == acknowledged)

    if severity is not None:
        query = query.filter(Violation.severity == severity)

    if min_confidence is not None:
        query = query.filter(Violation.confidence >= min_confidence)

    # Get total count before pagination
    total_count = query.count()

    # Apply ordering
    order_column = getattr(Violation, order_by, Violation.timestamp)
    if order_desc:
        query = query.order_by(desc(order_column))
    else:
        query = query.order_by(asc(order_column))

    # Apply pagination
    violations = query.offset(skip).limit(limit).all()

    return violations, total_count


def get_violation_stats(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    camera_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Get violation statistics for a time period.

    Args:
        db: Database session.
        start_date: Start of time period.
        end_date: End of time period.
        camera_id: Optional camera filter.

    Returns:
        Dictionary containing violation statistics.

    Example:
        stats = get_violation_stats(
            db,
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now()
        )
    """
    query = db.query(Violation)

    if start_date:
        query = query.filter(Violation.timestamp >= start_date)
    if end_date:
        query = query.filter(Violation.timestamp <= end_date)
    if camera_id:
        query = query.filter(Violation.camera_id == camera_id)

    # Total violations
    total_violations = query.count()

    # Violations by type
    violations_by_type = (
        query.with_entities(
            Violation.violation_type,
            func.count(Violation.id).label("count")
        )
        .group_by(Violation.violation_type)
        .all()
    )

    # Violations by severity
    violations_by_severity = (
        query.with_entities(
            Violation.severity,
            func.count(Violation.id).label("count")
        )
        .group_by(Violation.severity)
        .all()
    )

    # Average confidence
    avg_confidence = query.with_entities(
        func.avg(Violation.confidence)
    ).scalar() or 0

    # Acknowledged vs unacknowledged
    acknowledged_count = query.filter(Violation.acknowledged == True).count()
    unacknowledged_count = query.filter(Violation.acknowledged == False).count()

    # Violations by camera
    violations_by_camera = (
        query.join(Camera)
        .with_entities(
            Camera.id,
            Camera.name,
            func.count(Violation.id).label("count")
        )
        .group_by(Camera.id, Camera.name)
        .all()
    )

    return {
        "total_violations": total_violations,
        "violations_by_type": {str(vtype): count for vtype, count in violations_by_type},
        "violations_by_severity": {severity: count for severity, count in violations_by_severity},
        "average_confidence": float(avg_confidence),
        "acknowledged_count": acknowledged_count,
        "unacknowledged_count": unacknowledged_count,
        "violations_by_camera": [
            {"camera_id": cam_id, "camera_name": cam_name, "count": count}
            for cam_id, cam_name, count in violations_by_camera
        ],
    }


def acknowledge_violation(
    db: Session,
    violation_id: int,
    acknowledged_by: str,
    notes: Optional[str] = None
) -> Optional[Violation]:
    """
    Acknowledge a violation.

    Args:
        db: Database session.
        violation_id: Violation ID.
        acknowledged_by: User who acknowledged.
        notes: Optional acknowledgment notes.

    Returns:
        Updated violation or None.
    """
    violation = get_violation(db, violation_id)
    if violation:
        violation.acknowledged = True
        violation.acknowledged_by = acknowledged_by
        violation.acknowledged_at = datetime.utcnow()
        if notes:
            violation.notes = notes
        db.commit()
        db.refresh(violation)
        logger.info(f"Acknowledged violation {violation_id} by {acknowledged_by}")
    return violation


# ============================================================================
# DETECTION LOG CRUD OPERATIONS
# ============================================================================

def create_detection_log(db: Session, log_data: Dict[str, Any]) -> DetectionLog:
    """
    Create a new detection log entry.

    Args:
        db: Database session.
        log_data: Dictionary containing detection log data.

    Returns:
        Created detection log object.

    Example:
        log = create_detection_log(db, {
            "camera_id": 1,
            "total_persons": 5,
            "compliant_count": 4,
            "violation_count": 1,
            "compliance_rate": 80.0,
            "processing_time_ms": 150.5
        })
    """
    # Calculate compliance rate if not provided
    if "compliance_rate" not in log_data and log_data.get("total_persons", 0) > 0:
        log_data["compliance_rate"] = (
            log_data.get("compliant_count", 0) / log_data["total_persons"] * 100
        )

    log = DetectionLog(**log_data)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_detection_logs(
    db: Session,
    camera_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[DetectionLog]:
    """
    Get detection logs with filtering.

    Args:
        db: Database session.
        camera_id: Filter by camera ID.
        start_date: Filter logs after this date.
        end_date: Filter logs before this date.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        List of detection log objects.
    """
    query = db.query(DetectionLog)

    if camera_id is not None:
        query = query.filter(DetectionLog.camera_id == camera_id)

    if start_date is not None:
        query = query.filter(DetectionLog.timestamp >= start_date)

    if end_date is not None:
        query = query.filter(DetectionLog.timestamp <= end_date)

    return query.order_by(desc(DetectionLog.timestamp)).offset(skip).limit(limit).all()


def get_detection_stats(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    camera_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Get detection statistics.

    Args:
        db: Database session.
        start_date: Start of time period.
        end_date: End of time period.
        camera_id: Optional camera filter.

    Returns:
        Dictionary containing detection statistics.
    """
    query = db.query(DetectionLog)

    if start_date:
        query = query.filter(DetectionLog.timestamp >= start_date)
    if end_date:
        query = query.filter(DetectionLog.timestamp <= end_date)
    if camera_id:
        query = query.filter(DetectionLog.camera_id == camera_id)

    total_logs = query.count()

    # Aggregate statistics
    stats = query.with_entities(
        func.sum(DetectionLog.total_persons).label("total_persons"),
        func.sum(DetectionLog.compliant_count).label("compliant_count"),
        func.sum(DetectionLog.violation_count).label("violation_count"),
        func.avg(DetectionLog.compliance_rate).label("avg_compliance_rate"),
        func.avg(DetectionLog.processing_time_ms).label("avg_processing_time"),
    ).first()

    return {
        "total_detections": total_logs,
        "total_persons_detected": int(stats.total_persons or 0),
        "total_compliant": int(stats.compliant_count or 0),
        "total_violations": int(stats.violation_count or 0),
        "average_compliance_rate": float(stats.avg_compliance_rate or 0),
        "average_processing_time_ms": float(stats.avg_processing_time or 0),
    }


# ============================================================================
# ZONE CRUD OPERATIONS
# ============================================================================

def create_zone(db: Session, zone_data: Dict[str, Any]) -> Zone:
    """
    Create a new zone.

    Args:
        db: Database session.
        zone_data: Dictionary containing zone data.

    Returns:
        Created zone object.

    Example:
        zone = create_zone(db, {
            "name": "Construction Area A",
            "description": "Main construction zone",
            "required_ppe": ["helmet", "vest", "boots"]
        })
    """
    try:
        zone = Zone(**zone_data)
        db.add(zone)
        db.commit()
        db.refresh(zone)
        logger.info(f"Created zone: {zone.name} (ID: {zone.id})")
        return zone
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error creating zone: {e}")
        raise ValueError(f"Zone with name '{zone_data.get('name')}' already exists")


def get_zone(db: Session, zone_id: int) -> Optional[Zone]:
    """Get zone by ID."""
    return db.query(Zone).filter(Zone.id == zone_id).first()


def get_zones(db: Session, skip: int = 0, limit: int = 100) -> List[Zone]:
    """Get all zones with pagination."""
    return db.query(Zone).offset(skip).limit(limit).all()


def update_zone(db: Session, zone_id: int, update_data: Dict[str, Any]) -> Optional[Zone]:
    """Update zone with arbitrary fields."""
    zone = get_zone(db, zone_id)
    if zone:
        for key, value in update_data.items():
            if hasattr(zone, key):
                setattr(zone, key, value)
        db.commit()
        db.refresh(zone)
        logger.info(f"Updated zone {zone_id}")
    return zone


def delete_zone(db: Session, zone_id: int) -> bool:
    """Delete zone by ID."""
    zone = get_zone(db, zone_id)
    if zone:
        db.delete(zone)
        db.commit()
        logger.info(f"Deleted zone {zone_id}")
        return True
    return False


# ============================================================================
# ALERT CRUD OPERATIONS
# ============================================================================

def create_alert(db: Session, alert_data: Dict[str, Any]) -> Alert:
    """Create a new alert."""
    alert = Alert(**alert_data)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    logger.info(f"Created alert: {alert.id} (Type: {alert.alert_type})")
    return alert


def get_alerts(
    db: Session,
    camera_id: Optional[int] = None,
    resolved: Optional[bool] = None,
    severity: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Alert]:
    """Get alerts with filtering."""
    query = db.query(Alert)

    if camera_id is not None:
        query = query.filter(Alert.camera_id == camera_id)
    if resolved is not None:
        query = query.filter(Alert.resolved == resolved)
    if severity is not None:
        query = query.filter(Alert.severity == severity)

    return query.order_by(desc(Alert.timestamp)).offset(skip).limit(limit).all()


def resolve_alert(
    db: Session,
    alert_id: int,
    resolved_by: str
) -> Optional[Alert]:
    """Resolve an alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert:
        alert.resolved = True
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = resolved_by
        db.commit()
        db.refresh(alert)
        logger.info(f"Resolved alert {alert_id} by {resolved_by}")
    return alert
