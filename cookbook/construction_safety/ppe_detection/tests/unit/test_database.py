"""
Unit tests for Database CRUD operations.

Tests all database operations including camera, violation, detection log,
zone, and alert management.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from database import crud
from database.models import CameraStatus, ViolationType


@pytest.mark.unit
@pytest.mark.database
class TestCameraCRUD:
    """Test Camera CRUD operations."""

    def test_create_camera(self, test_db, sample_zone):
        """Test creating a camera."""
        camera_data = {
            "name": "Camera-01",
            "rtsp_url": "rtsp://admin:pass@192.168.1.100:554/stream",
            "location": "Entrance",
            "zone_id": sample_zone.id,
            "status": CameraStatus.ACTIVE,
            "is_active": True,
            "fps": 15.0,
            "resolution": "1920x1080"
        }

        camera = crud.create_camera(test_db, camera_data)

        assert camera.id is not None
        assert camera.name == "Camera-01"
        assert camera.status == CameraStatus.ACTIVE

    def test_create_duplicate_camera(self, test_db, sample_zone):
        """Test creating duplicate camera (should fail)."""
        camera_data = {
            "name": "Camera-Duplicate",
            "rtsp_url": "rtsp://admin:pass@192.168.1.100:554/stream",
            "zone_id": sample_zone.id,
            "status": CameraStatus.ACTIVE
        }

        crud.create_camera(test_db, camera_data)

        # Try to create duplicate
        with pytest.raises(ValueError):
            crud.create_camera(test_db, camera_data)

    def test_get_camera(self, test_db, sample_camera):
        """Test getting camera by ID."""
        camera = crud.get_camera(test_db, sample_camera.id)

        assert camera is not None
        assert camera.id == sample_camera.id
        assert camera.name == sample_camera.name

    def test_get_camera_by_name(self, test_db, sample_camera):
        """Test getting camera by name."""
        camera = crud.get_camera_by_name(test_db, sample_camera.name)

        assert camera is not None
        assert camera.name == sample_camera.name

    def test_get_cameras(self, test_db, sample_zone):
        """Test getting list of cameras."""
        # Create multiple cameras
        for i in range(5):
            camera_data = {
                "name": f"Camera-{i}",
                "rtsp_url": f"rtsp://admin:pass@192.168.1.{100+i}:554/stream",
                "zone_id": sample_zone.id,
                "status": CameraStatus.ACTIVE if i < 3 else CameraStatus.INACTIVE,
                "is_active": i < 4
            }
            crud.create_camera(test_db, camera_data)

        # Get all cameras
        cameras = crud.get_cameras(test_db, active_only=False)
        assert len(cameras) >= 5

        # Get only active cameras
        active_cameras = crud.get_cameras(test_db, active_only=True)
        assert all(c.is_active for c in active_cameras)

    def test_update_camera_status(self, test_db, sample_camera):
        """Test updating camera status."""
        updated_camera = crud.update_camera_status(
            test_db,
            sample_camera.id,
            CameraStatus.INACTIVE
        )

        assert updated_camera.status == CameraStatus.INACTIVE
        assert updated_camera.last_heartbeat is not None

    def test_update_camera(self, test_db, sample_camera):
        """Test updating camera fields."""
        update_data = {
            "location": "New Location",
            "fps": 30.0
        }

        updated_camera = crud.update_camera(
            test_db,
            sample_camera.id,
            update_data
        )

        assert updated_camera.location == "New Location"
        assert updated_camera.fps == 30.0

    def test_delete_camera(self, test_db, sample_camera):
        """Test deleting a camera."""
        result = crud.delete_camera(test_db, sample_camera.id)

        assert result is True

        # Verify deletion
        camera = crud.get_camera(test_db, sample_camera.id)
        assert camera is None


@pytest.mark.unit
@pytest.mark.database
class TestViolationCRUD:
    """Test Violation CRUD operations."""

    def test_create_violation(self, test_db, sample_camera):
        """Test creating a violation."""
        violation_data = {
            "camera_id": sample_camera.id,
            "timestamp": datetime.utcnow(),
            "violation_type": ViolationType.NO_HELMET,
            "image_path": "/data/violations/test.jpg",
            "confidence": 0.95,
            "person_count": 1,
            "severity": "high"
        }

        violation = crud.create_violation(test_db, violation_data)

        assert violation.id is not None
        assert violation.violation_type == ViolationType.NO_HELMET
        assert violation.confidence == 0.95

    def test_get_violation(self, test_db, sample_camera):
        """Test getting violation by ID."""
        violation_data = {
            "camera_id": sample_camera.id,
            "violation_type": ViolationType.NO_VEST,
            "confidence": 0.90
        }

        created = crud.create_violation(test_db, violation_data)
        violation = crud.get_violation(test_db, created.id)

        assert violation is not None
        assert violation.id == created.id

    def test_get_violations_with_filters(self, test_db, sample_camera):
        """Test getting violations with filters."""
        # Create multiple violations
        for i in range(10):
            violation_data = {
                "camera_id": sample_camera.id,
                "timestamp": datetime.utcnow() - timedelta(hours=i),
                "violation_type": ViolationType.NO_HELMET if i % 2 == 0 else ViolationType.NO_VEST,
                "confidence": 0.85 + (i * 0.01),
                "acknowledged": i > 5
            }
            crud.create_violation(test_db, violation_data)

        # Filter by type
        violations, total = crud.get_violations(
            test_db,
            violation_type=ViolationType.NO_HELMET,
            limit=100
        )

        assert all(v.violation_type == ViolationType.NO_HELMET for v in violations)

        # Filter by acknowledged status
        unack_violations, total = crud.get_violations(
            test_db,
            acknowledged=False,
            limit=100
        )

        assert all(v.acknowledged is False for v in unack_violations)

    def test_get_violations_pagination(self, test_db, sample_camera):
        """Test violation pagination."""
        # Create violations
        for i in range(20):
            violation_data = {
                "camera_id": sample_camera.id,
                "violation_type": ViolationType.NO_HELMET,
                "confidence": 0.9
            }
            crud.create_violation(test_db, violation_data)

        # Get first page
        page1, total = crud.get_violations(test_db, skip=0, limit=10)
        assert len(page1) == 10

        # Get second page
        page2, total = crud.get_violations(test_db, skip=10, limit=10)
        assert len(page2) == 10

        # Pages should not overlap
        page1_ids = {v.id for v in page1}
        page2_ids = {v.id for v in page2}
        assert len(page1_ids.intersection(page2_ids)) == 0

    def test_get_violation_stats(self, test_db, sample_camera):
        """Test getting violation statistics."""
        # Create various violations
        for i in range(15):
            violation_data = {
                "camera_id": sample_camera.id,
                "timestamp": datetime.utcnow(),
                "violation_type": ViolationType.NO_HELMET if i < 10 else ViolationType.NO_VEST,
                "confidence": 0.85 + (i * 0.01),
                "severity": "high" if i < 5 else "medium"
            }
            crud.create_violation(test_db, violation_data)

        stats = crud.get_violation_stats(test_db)

        assert stats["total_violations"] >= 15
        assert "violations_by_type" in stats
        assert "violations_by_severity" in stats
        assert "average_confidence" in stats

    def test_acknowledge_violation(self, test_db, sample_camera):
        """Test acknowledging a violation."""
        violation_data = {
            "camera_id": sample_camera.id,
            "violation_type": ViolationType.NO_HELMET,
            "confidence": 0.9,
            "acknowledged": False
        }

        violation = crud.create_violation(test_db, violation_data)

        # Acknowledge
        ack_violation = crud.acknowledge_violation(
            test_db,
            violation.id,
            acknowledged_by="supervisor@example.com",
            notes="Worker warned"
        )

        assert ack_violation.acknowledged is True
        assert ack_violation.acknowledged_by == "supervisor@example.com"
        assert ack_violation.notes == "Worker warned"


@pytest.mark.unit
@pytest.mark.database
class TestDetectionLogCRUD:
    """Test Detection Log CRUD operations."""

    def test_create_detection_log(self, test_db, sample_camera):
        """Test creating a detection log."""
        log_data = {
            "camera_id": sample_camera.id,
            "timestamp": datetime.utcnow(),
            "total_persons": 5,
            "compliant_count": 4,
            "violation_count": 1,
            "processing_time_ms": 150.5
        }

        log = crud.create_detection_log(test_db, log_data)

        assert log.id is not None
        assert log.total_persons == 5
        assert log.compliance_rate == 80.0  # Calculated automatically

    def test_get_detection_logs(self, test_db, sample_camera):
        """Test getting detection logs."""
        # Create logs
        for i in range(10):
            log_data = {
                "camera_id": sample_camera.id,
                "timestamp": datetime.utcnow() - timedelta(minutes=i),
                "total_persons": 3 + i,
                "compliant_count": 2 + i,
                "violation_count": 1
            }
            crud.create_detection_log(test_db, log_data)

        logs = crud.get_detection_logs(test_db, limit=100)

        assert len(logs) >= 10

    def test_get_detection_stats(self, test_db, sample_camera):
        """Test getting detection statistics."""
        # Create logs
        for i in range(20):
            log_data = {
                "camera_id": sample_camera.id,
                "total_persons": 5,
                "compliant_count": 4,
                "violation_count": 1,
                "processing_time_ms": 100.0 + i
            }
            crud.create_detection_log(test_db, log_data)

        stats = crud.get_detection_stats(test_db)

        assert stats["total_detections"] >= 20
        assert stats["total_persons_detected"] >= 100
        assert "average_compliance_rate" in stats
        assert "average_processing_time_ms" in stats


@pytest.mark.unit
@pytest.mark.database
class TestZoneCRUD:
    """Test Zone CRUD operations."""

    def test_create_zone(self, test_db):
        """Test creating a zone."""
        zone_data = {
            "name": "Construction Area A",
            "description": "Main construction zone",
            "required_ppe": ["helmet", "vest", "boots"]
        }

        zone = crud.create_zone(test_db, zone_data)

        assert zone.id is not None
        assert zone.name == "Construction Area A"
        assert "helmet" in zone.required_ppe

    def test_create_duplicate_zone(self, test_db):
        """Test creating duplicate zone."""
        zone_data = {
            "name": "Duplicate Zone",
            "required_ppe": ["helmet"]
        }

        crud.create_zone(test_db, zone_data)

        with pytest.raises(ValueError):
            crud.create_zone(test_db, zone_data)

    def test_get_zone(self, test_db, sample_zone):
        """Test getting zone by ID."""
        zone = crud.get_zone(test_db, sample_zone.id)

        assert zone is not None
        assert zone.id == sample_zone.id

    def test_get_zones(self, test_db):
        """Test getting all zones."""
        # Create multiple zones
        for i in range(5):
            zone_data = {
                "name": f"Zone {i}",
                "required_ppe": ["helmet", "vest"]
            }
            crud.create_zone(test_db, zone_data)

        zones = crud.get_zones(test_db)

        assert len(zones) >= 5

    def test_update_zone(self, test_db, sample_zone):
        """Test updating zone."""
        update_data = {
            "description": "Updated description",
            "required_ppe": ["helmet", "vest", "boots", "gloves"]
        }

        updated_zone = crud.update_zone(test_db, sample_zone.id, update_data)

        assert updated_zone.description == "Updated description"
        assert len(updated_zone.required_ppe) == 4

    def test_delete_zone(self, test_db, sample_zone):
        """Test deleting zone."""
        result = crud.delete_zone(test_db, sample_zone.id)

        assert result is True

        zone = crud.get_zone(test_db, sample_zone.id)
        assert zone is None


@pytest.mark.unit
@pytest.mark.database
class TestAlertCRUD:
    """Test Alert CRUD operations."""

    def test_create_alert(self, test_db, sample_camera):
        """Test creating an alert."""
        alert_data = {
            "camera_id": sample_camera.id,
            "timestamp": datetime.utcnow(),
            "alert_type": "ppe_violation",
            "severity": "high",
            "message": "Worker without helmet detected",
            "resolved": False
        }

        alert = crud.create_alert(test_db, alert_data)

        assert alert.id is not None
        assert alert.severity == "high"
        assert alert.resolved is False

    def test_get_alerts(self, test_db, sample_camera):
        """Test getting alerts with filters."""
        # Create alerts
        for i in range(10):
            alert_data = {
                "camera_id": sample_camera.id,
                "alert_type": "ppe_violation",
                "severity": "high" if i < 5 else "medium",
                "resolved": i > 6
            }
            crud.create_alert(test_db, alert_data)

        # Get unresolved alerts
        unresolved = crud.get_alerts(test_db, resolved=False)
        assert all(a.resolved is False for a in unresolved)

        # Get high severity alerts
        high_severity = crud.get_alerts(test_db, severity="high")
        assert all(a.severity == "high" for a in high_severity)

    def test_resolve_alert(self, test_db, sample_camera):
        """Test resolving an alert."""
        alert_data = {
            "camera_id": sample_camera.id,
            "alert_type": "ppe_violation",
            "severity": "high",
            "resolved": False
        }

        alert = crud.create_alert(test_db, alert_data)

        # Resolve
        resolved_alert = crud.resolve_alert(
            test_db,
            alert.id,
            resolved_by="supervisor@example.com"
        )

        assert resolved_alert.resolved is True
        assert resolved_alert.resolved_by == "supervisor@example.com"
        assert resolved_alert.resolved_at is not None


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.turkish
class TestTurkishDataHandling:
    """Test handling of Turkish characters in database."""

    def test_turkish_zone_names(self, test_db):
        """Test zone names with Turkish characters."""
        zone_data = {
            "name": "Kazı Alanı",
            "description": "Ana kazı bölgesi - İşçi güvenliği öncelikli",
            "required_ppe": ["baret", "yelek", "iş ayakkabısı"]
        }

        zone = crud.create_zone(test_db, zone_data)

        assert zone.name == "Kazı Alanı"
        assert "İşçi" in zone.description
        assert "baret" in zone.required_ppe

    def test_turkish_camera_locations(self, test_db, sample_zone):
        """Test camera locations with Turkish characters."""
        camera_data = {
            "name": "Kamera-01",
            "rtsp_url": "rtsp://test:test@192.168.1.100:554/stream",
            "location": "Şantiye Girişi",
            "zone_id": sample_zone.id,
            "status": CameraStatus.ACTIVE
        }

        camera = crud.create_camera(test_db, camera_data)

        assert camera.location == "Şantiye Girişi"

    def test_turkish_alert_messages(self, test_db, sample_camera):
        """Test alerts with Turkish messages."""
        alert_data = {
            "camera_id": sample_camera.id,
            "alert_type": "ppe_ihlali",
            "severity": "yüksek",
            "message": "İşçi baretsiz tespit edildi - Acil müdahale gerekli",
            "resolved": False
        }

        alert = crud.create_alert(test_db, alert_data)

        assert "İşçi" in alert.message
        assert "baretsiz" in alert.message
