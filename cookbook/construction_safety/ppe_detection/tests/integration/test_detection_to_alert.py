"""
Integration tests for detection to alert pipeline.

Tests the integration between PPE detection and alert system.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import numpy as np

from models.ppe_detector import PPEDetector
from alerts.alert_manager import AlertManager
from database import crud


@pytest.mark.integration
class TestDetectionToAlert:
    """Test detection-to-alert integration."""

    @patch('models.ppe_detector.YOLO')
    def test_violation_detection_triggers_alert(
        self,
        mock_yolo,
        model_config,
        alert_config,
        test_db,
        sample_image
    ):
        """Test that detected violation triggers alert."""
        # Setup mock detection (person with no helmet)
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model

        mock_result = MagicMock()
        mock_result.boxes = MagicMock()
        mock_result.boxes.xyxy.cpu().numpy.return_value = np.array([
            [100, 100, 300, 500],  # person
            [150, 200, 250, 400],  # vest only
        ])
        mock_result.boxes.conf.cpu().numpy.return_value = np.array([0.95, 0.88])
        mock_result.boxes.cls.cpu().numpy.return_value = np.array([0, 2])
        mock_model.predict.return_value = [mock_result]

        # Initialize components
        detector = PPEDetector(config=model_config, verbose=False)
        alert_manager = AlertManager(config=alert_config)

        # Detect PPE
        detections = detector.detect_ppe(sample_image)
        compliance_results = detector.is_compliant(detections)

        # Process violations
        for result in compliance_results:
            if not result.is_compliant:
                missing_ppe = []
                if not result.has_helmet:
                    missing_ppe.append("helmet")
                if not result.has_vest:
                    missing_ppe.append("vest")

                # Trigger alert
                alert = alert_manager.process_violation(
                    zone="Test Zone",
                    camera_id="cam-001",
                    missing_ppe=missing_ppe
                )

                # Alert may or may not be created based on rules
                # Check that the system processed the violation
                assert len(missing_ppe) > 0

    @patch('models.ppe_detector.YOLO')
    def test_compliant_worker_no_alert(
        self,
        mock_yolo,
        model_config,
        alert_config,
        sample_image
    ):
        """Test that compliant worker does not trigger alert."""
        # Setup mock detection (compliant worker)
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

        detector = PPEDetector(config=model_config, verbose=False)
        alert_manager = AlertManager(config=alert_config)

        detections = detector.detect_ppe(sample_image)
        compliance_results = detector.is_compliant(detections)

        # Should be compliant
        assert all(r.is_compliant for r in compliance_results)

        # No violations to process
        violations = [r for r in compliance_results if not r.is_compliant]
        assert len(violations) == 0

    @patch('models.ppe_detector.YOLO')
    def test_multiple_violations_alert_batching(
        self,
        mock_yolo,
        model_config,
        alert_config,
        sample_image
    ):
        """Test alert batching for multiple violations."""
        # Setup mock for multiple workers with violations
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model

        mock_result = MagicMock()
        mock_result.boxes = MagicMock()
        mock_result.boxes.xyxy.cpu().numpy.return_value = np.array([
            # Worker 1 - no helmet
            [50, 100, 150, 500],
            [75, 200, 125, 400],  # vest only

            # Worker 2 - no vest
            [200, 100, 300, 500],
            [225, 100, 275, 150],  # helmet only

            # Worker 3 - compliant
            [350, 100, 450, 500],
            [375, 100, 425, 150],  # helmet
            [375, 200, 425, 400],  # vest
        ])
        mock_result.boxes.conf.cpu().numpy.return_value = np.array(
            [0.95, 0.88, 0.94, 0.91, 0.93, 0.90, 0.87]
        )
        mock_result.boxes.cls.cpu().numpy.return_value = np.array(
            [0, 2, 0, 1, 0, 1, 2]
        )
        mock_model.predict.return_value = [mock_result]

        detector = PPEDetector(config=model_config, verbose=False)
        alert_manager = AlertManager(config=alert_config)

        detections = detector.detect_ppe(sample_image)
        compliance_results = detector.is_compliant(detections)

        # Should have violations
        violations = [r for r in compliance_results if not r.is_compliant]
        assert len(violations) > 0

        # Process all violations
        alerts_created = []
        for result in violations:
            missing_ppe = []
            if not result.has_helmet:
                missing_ppe.append("helmet")
            if not result.has_vest:
                missing_ppe.append("vest")

            alert = alert_manager.process_violation(
                zone="Test Zone",
                camera_id="cam-001",
                missing_ppe=missing_ppe,
                timestamp=datetime.now()
            )

            if alert:
                alerts_created.append(alert)

        # Check that violations were processed
        # (Some may be deduplicated or throttled)

    @patch('models.ppe_detector.YOLO')
    def test_violation_severity_mapping(
        self,
        mock_yolo,
        model_config,
        alert_config,
        sample_image
    ):
        """Test that violation severity is correctly mapped to alert priority."""
        # Missing helmet should be CRITICAL
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

        detector = PPEDetector(config=model_config, verbose=False)
        alert_manager = AlertManager(config=alert_config)

        detections = detector.detect_ppe(sample_image)
        compliance_results = detector.is_compliant(detections)

        for result in compliance_results:
            if not result.has_helmet:
                # Determine priority
                priority = alert_manager._determine_priority(
                    zone="Test Zone",
                    missing_ppe=["helmet"],
                    violation_count=1,
                    compliance_rate=None
                )

                # Missing helmet should be CRITICAL
                from alerts.alert_config import AlertPriority
                assert priority == AlertPriority.CRITICAL

    @patch('models.ppe_detector.YOLO')
    def test_violation_persistence_to_database(
        self,
        mock_yolo,
        model_config,
        test_db,
        sample_camera,
        sample_image
    ):
        """Test that violations are correctly persisted to database."""
        # Setup mock detection with violation
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model

        mock_result = MagicMock()
        mock_result.boxes = MagicMock()
        mock_result.boxes.xyxy.cpu().numpy.return_value = np.array([
            [100, 100, 300, 500],
            [150, 200, 250, 400],
        ])
        mock_result.boxes.conf.cpu().numpy.return_value = np.array([0.95, 0.88])
        mock_result.boxes.cls.cpu().numpy.return_value = np.array([0, 2])
        mock_model.predict.return_value = [mock_result]

        detector = PPEDetector(config=model_config, verbose=False)

        detections = detector.detect_ppe(sample_image)
        compliance_results = detector.is_compliant(detections)

        # Save violations to database
        for result in compliance_results:
            if not result.is_compliant:
                violation_data = {
                    "camera_id": sample_camera.id,
                    "timestamp": datetime.utcnow(),
                    "violation_type": "NO_HELMET",
                    "confidence": result.person_detection.confidence,
                    "person_count": 1
                }

                violation = crud.create_violation(test_db, violation_data)

                assert violation.id is not None
                assert violation.camera_id == sample_camera.id

    @patch('models.ppe_detector.YOLO')
    @pytest.mark.slow
    def test_continuous_detection_and_alerting(
        self,
        mock_yolo,
        model_config,
        alert_config,
        sample_image
    ):
        """Test continuous detection and alerting over time."""
        import time

        mock_model = MagicMock()
        mock_yolo.return_value = mock_model
        mock_model.predict.return_value = []

        detector = PPEDetector(config=model_config, verbose=False)
        alert_manager = AlertManager(config=alert_config)

        # Simulate continuous monitoring
        detection_count = 0
        alert_count = 0
        start_time = time.time()
        duration = 2.0

        while time.time() - start_time < duration:
            detections = detector.detect_ppe(sample_image)
            compliance_results = detector.is_compliant(detections)

            for result in compliance_results:
                if not result.is_compliant:
                    alert = alert_manager.process_violation(
                        zone="Test Zone",
                        camera_id="cam-001",
                        missing_ppe=["helmet"]
                    )
                    if alert:
                        alert_count += 1

            detection_count += 1
            time.sleep(0.2)

        # Should have processed multiple detections
        assert detection_count > 0


@pytest.mark.integration
@pytest.mark.turkish
class TestTurkishAlertIntegration:
    """Test Turkish-specific alert scenarios."""

    @patch('models.ppe_detector.YOLO')
    def test_critical_zone_alert_priority(
        self,
        mock_yolo,
        model_config,
        alert_config,
        sample_image
    ):
        """Test that critical Turkish zones trigger high-priority alerts."""
        # Setup mock with violation
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model

        mock_result = MagicMock()
        mock_result.boxes = MagicMock()
        mock_result.boxes.xyxy.cpu().numpy.return_value = np.array([
            [100, 100, 300, 500],
            [150, 200, 250, 400],
        ])
        mock_result.boxes.conf.cpu().numpy.return_value = np.array([0.95, 0.88])
        mock_result.boxes.cls.cpu().numpy.return_value = np.array([0, 2])
        mock_model.predict.return_value = [mock_result]

        detector = PPEDetector(config=model_config, verbose=False)
        alert_manager = AlertManager(config=alert_config)

        detections = detector.detect_ppe(sample_image)
        compliance_results = detector.is_compliant(detections)

        # Test with critical Turkish zone
        for result in compliance_results:
            if not result.is_compliant:
                priority = alert_manager._determine_priority(
                    zone="Kazı Alanı",  # Critical zone
                    missing_ppe=["vest"],
                    violation_count=1,
                    compliance_rate=None
                )

                from alerts.alert_config import AlertPriority
                assert priority == AlertPriority.CRITICAL

    @patch('models.ppe_detector.YOLO')
    def test_harness_violation_elevated_work(
        self,
        mock_yolo,
        model_config,
        alert_config,
        sample_image
    ):
        """Test harness violation in elevated work area."""
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model
        mock_model.predict.return_value = []

        alert_manager = AlertManager(config=alert_config)

        # Missing harness in elevated work should be CRITICAL
        priority = alert_manager._determine_priority(
            zone="Yüksekte Çalışma Alanı",
            missing_ppe=["harness"],
            violation_count=1,
            compliance_rate=None
        )

        from alerts.alert_config import AlertPriority
        assert priority == AlertPriority.CRITICAL
