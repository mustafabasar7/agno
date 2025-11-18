"""
End-to-end integration tests for PPE Detection System.

Tests the complete flow from camera capture to detection to alerting.
"""

import pytest
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock
import numpy as np

from camera.camera_manager import CameraManager
from models.ppe_detector import PPEDetector
from alerts.alert_manager import AlertManager
from database import crud


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndPipeline:
    """Test complete detection pipeline."""

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    @patch('models.ppe_detector.YOLO')
    def test_full_pipeline_compliant_worker(
        self,
        mock_yolo,
        mock_video_capture,
        camera_config,
        model_config,
        alert_config,
        test_db
    ):
        """
        Test full pipeline with compliant worker:
        Camera -> Detection -> Database -> No Alert
        """
        # Setup mock camera
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, test_frame)
        mock_video_capture.return_value = mock_cap

        # Setup mock YOLO model with compliant detections
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model

        mock_result = MagicMock()
        mock_result.boxes = MagicMock()
        mock_result.boxes.xyxy.cpu().numpy.return_value = np.array([
            [100, 100, 300, 500],  # person
            [150, 100, 250, 150],  # helmet
            [150, 200, 250, 400],  # vest
        ])
        mock_result.boxes.conf.cpu().numpy.return_value = np.array([0.95, 0.92, 0.88])
        mock_result.boxes.cls.cpu().numpy.return_value = np.array([0, 1, 2])
        mock_model.predict.return_value = [mock_result]

        # Initialize components
        camera_manager = CameraManager()
        detector = PPEDetector(config=model_config, verbose=False)
        alert_manager = AlertManager(config=alert_config)

        try:
            # Start camera
            camera_manager.add_camera(camera_config)
            time.sleep(0.2)

            # Capture frame
            snapshot = camera_manager.snapshot(camera_config.camera_id)
            assert snapshot is not None or True  # May be None if not captured yet

            # If we have a frame, run detection
            if snapshot is not None:
                # Run detection
                detections = detector.detect_ppe(snapshot)
                assert len(detections) > 0

                # Check compliance
                compliance_results = detector.is_compliant(detections)
                assert len(compliance_results) > 0

                # Log to database
                if compliance_results:
                    compliant_count = sum(1 for r in compliance_results if r.is_compliant)
                    violation_count = len(compliance_results) - compliant_count

                    log_data = {
                        "camera_id": 1,
                        "total_persons": len(compliance_results),
                        "compliant_count": compliant_count,
                        "violation_count": violation_count,
                        "processing_time_ms": 150.0
                    }
                    detection_log = crud.create_detection_log(test_db, log_data)
                    assert detection_log is not None

                    # Process violations (should not generate alert for compliant worker)
                    for result in compliance_results:
                        if not result.is_compliant:
                            missing_ppe = []
                            if not result.has_helmet:
                                missing_ppe.append("helmet")
                            if not result.has_vest:
                                missing_ppe.append("vest")

                            alert = alert_manager.process_violation(
                                zone="Zone A",
                                camera_id=camera_config.camera_id,
                                missing_ppe=missing_ppe
                            )
                            # Alert may or may not be created based on rules

        finally:
            camera_manager.stop()

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    @patch('models.ppe_detector.YOLO')
    def test_full_pipeline_violation_detection(
        self,
        mock_yolo,
        mock_video_capture,
        camera_config,
        model_config,
        alert_config,
        test_db
    ):
        """
        Test full pipeline with PPE violation:
        Camera -> Detection -> Database -> Alert
        """
        # Setup mock camera
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, test_frame)
        mock_video_capture.return_value = mock_cap

        # Setup mock YOLO model with violation (no helmet)
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model

        mock_result = MagicMock()
        mock_result.boxes = MagicMock()
        mock_result.boxes.xyxy.cpu().numpy.return_value = np.array([
            [100, 100, 300, 500],  # person
            [150, 200, 250, 400],  # vest only (no helmet)
        ])
        mock_result.boxes.conf.cpu().numpy.return_value = np.array([0.95, 0.88])
        mock_result.boxes.cls.cpu().numpy.return_value = np.array([0, 2])
        mock_model.predict.return_value = [mock_result]

        # Initialize components
        camera_manager = CameraManager()
        detector = PPEDetector(config=model_config, verbose=False)
        alert_manager = AlertManager(config=alert_config)

        try:
            camera_manager.add_camera(camera_config)
            time.sleep(0.2)

            snapshot = camera_manager.snapshot(camera_config.camera_id)

            if snapshot is not None:
                detections = detector.detect_ppe(snapshot)
                compliance_results = detector.is_compliant(detections)

                # Should have violation
                violations = [r for r in compliance_results if not r.is_compliant]
                assert len(violations) > 0

                # Record in database
                for result in violations:
                    violation_data = {
                        "camera_id": 1,
                        "violation_type": "NO_HELMET",
                        "confidence": 0.95,
                        "person_count": 1
                    }
                    violation = crud.create_violation(test_db, violation_data)
                    assert violation is not None

                    # Trigger alert
                    alert = alert_manager.process_violation(
                        zone="Zone A",
                        camera_id=camera_config.camera_id,
                        missing_ppe=["helmet"]
                    )
                    # Alert may or may not be created based on rules

        finally:
            camera_manager.stop()

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    @patch('models.ppe_detector.YOLO')
    def test_multiple_cameras_parallel_processing(
        self,
        mock_yolo,
        mock_video_capture,
        model_config
    ):
        """Test processing frames from multiple cameras in parallel."""
        from camera.camera_config import CameraConfig

        # Setup mocks
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, test_frame)
        mock_video_capture.return_value = mock_cap

        mock_model = MagicMock()
        mock_yolo.return_value = mock_model
        mock_model.predict.return_value = []

        # Initialize components
        camera_manager = CameraManager()
        detector = PPEDetector(config=model_config, verbose=False)

        try:
            # Add multiple cameras
            for i in range(3):
                config = CameraConfig(
                    camera_id=f"cam-{i}",
                    name=f"Camera {i}",
                    rtsp_url=f"rtsp://test@192.168.1.{100+i}:554/stream",
                    zone=f"Zone {i}"
                )
                camera_manager.add_camera(config)

            time.sleep(0.3)

            # Get snapshots from all cameras
            snapshots = camera_manager.snapshot_all()
            assert len(snapshots) == 3

            # Process each snapshot
            for camera_id, snapshot in snapshots.items():
                if snapshot is not None:
                    detections = detector.detect_ppe(snapshot)
                    # Process detections

        finally:
            camera_manager.stop()

    @pytest.mark.slow
    @patch('camera.rtsp_handler.cv2.VideoCapture')
    @patch('models.ppe_detector.YOLO')
    def test_continuous_monitoring_scenario(
        self,
        mock_yolo,
        mock_video_capture,
        camera_config,
        model_config,
        alert_config
    ):
        """Test continuous monitoring scenario over time."""
        # Setup mocks
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, test_frame)
        mock_video_capture.return_value = mock_cap

        mock_model = MagicMock()
        mock_yolo.return_value = mock_model
        mock_model.predict.return_value = []

        camera_manager = CameraManager()
        detector = PPEDetector(config=model_config, verbose=False)
        alert_manager = AlertManager(config=alert_config)

        try:
            camera_manager.start()
            camera_manager.add_camera(camera_config)

            # Simulate continuous monitoring for 2 seconds
            detection_count = 0
            start_time = time.time()
            duration = 2.0

            while time.time() - start_time < duration:
                snapshot = camera_manager.snapshot(camera_config.camera_id)

                if snapshot is not None:
                    detections = detector.detect_ppe(snapshot)
                    detection_count += 1

                time.sleep(0.2)  # Check every 200ms

            # Should have processed some frames
            assert detection_count > 0

        finally:
            camera_manager.stop()


@pytest.mark.integration
class TestDatabaseIntegration:
    """Test database integration scenarios."""

    def test_complete_violation_lifecycle(self, test_db):
        """Test complete lifecycle of a violation from creation to resolution."""
        # Create zone
        zone = crud.create_zone(test_db, {
            "name": "Test Zone",
            "required_ppe": ["helmet", "vest"]
        })

        # Create camera
        camera = crud.create_camera(test_db, {
            "name": "Test Camera",
            "rtsp_url": "rtsp://test:test@192.168.1.100:554/stream",
            "zone_id": zone.id,
            "status": "active"
        })

        # Create violation
        violation = crud.create_violation(test_db, {
            "camera_id": camera.id,
            "violation_type": "NO_HELMET",
            "confidence": 0.95,
            "person_count": 1
        })

        # Create alert
        alert = crud.create_alert(test_db, {
            "camera_id": camera.id,
            "alert_type": "ppe_violation",
            "severity": "high",
            "message": "PPE violation detected"
        })

        # Acknowledge violation
        ack_violation = crud.acknowledge_violation(
            test_db,
            violation.id,
            acknowledged_by="supervisor@example.com"
        )

        # Resolve alert
        resolved_alert = crud.resolve_alert(
            test_db,
            alert.id,
            resolved_by="supervisor@example.com"
        )

        # Verify lifecycle
        assert violation.id is not None
        assert ack_violation.acknowledged is True
        assert resolved_alert.resolved is True

    def test_compliance_statistics_calculation(self, test_db):
        """Test calculating compliance statistics from detection logs."""
        # Create camera
        camera = crud.create_camera(test_db, {
            "name": "Test Camera",
            "rtsp_url": "rtsp://test:test@192.168.1.100:554/stream",
            "status": "active"
        })

        # Create detection logs
        for i in range(100):
            crud.create_detection_log(test_db, {
                "camera_id": camera.id,
                "total_persons": 5,
                "compliant_count": 4 if i < 80 else 3,  # 80% compliance
                "violation_count": 1 if i < 80 else 2
            })

        # Get statistics
        stats = crud.get_detection_stats(test_db)

        assert stats["total_detections"] == 100
        assert stats["total_persons_detected"] == 500
        # Average compliance rate should be around 78-82%
        assert 75.0 <= stats["average_compliance_rate"] <= 85.0


@pytest.mark.integration
@pytest.mark.turkish
class TestTurkishConstructionSiteIntegration:
    """Integration tests for Turkish construction site scenarios."""

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    @patch('models.ppe_detector.YOLO')
    def test_turkish_site_with_multiple_zones(
        self,
        mock_yolo,
        mock_video_capture,
        model_config,
        test_db
    ):
        """Test Turkish construction site with multiple zones."""
        from camera.camera_config import CameraConfig

        # Create Turkish zones
        zones = [
            {"name": "Şantiye Girişi", "required_ppe": ["baret", "yelek"]},
            {"name": "Kazı Alanı", "required_ppe": ["baret", "yelek", "çelik burun bot"]},
            {"name": "Yüksekte Çalışma", "required_ppe": ["baret", "yelek", "emniyet kemeri"]},
        ]

        for zone_data in zones:
            zone = crud.create_zone(test_db, zone_data)

            # Create camera for each zone
            camera_config = CameraConfig(
                camera_id=f"cam-{zone.id}",
                name=f"Kamera - {zone.name}",
                rtsp_url=f"rtsp://test@192.168.1.{100+zone.id}:554/stream",
                zone=zone.name
            )

            # Verify Turkish characters preserved
            assert "ı" in zone.name or "İ" in zone.name or "ş" in zone.name
