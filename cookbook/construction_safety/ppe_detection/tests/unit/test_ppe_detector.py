"""
Unit tests for PPE Detector.

Tests the core detection logic, compliance checking, and visualization.
"""

import pytest
import numpy as np
import cv2
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from models.ppe_detector import PPEDetector, Detection, ComplianceResult
from models.model_config import ModelConfig


@pytest.mark.unit
class TestDetection:
    """Test Detection dataclass functionality."""

    def test_detection_creation(self):
        """Test creating a Detection object."""
        detection = Detection(
            bbox=(100, 100, 200, 300),
            confidence=0.95,
            class_id=0,
            class_name="person"
        )

        assert detection.bbox == (100, 100, 200, 300)
        assert detection.confidence == 0.95
        assert detection.class_id == 0
        assert detection.class_name == "person"

    def test_detection_center(self):
        """Test Detection center property."""
        detection = Detection(
            bbox=(100, 100, 200, 300),
            confidence=0.95,
            class_id=0,
            class_name="person"
        )

        center = detection.center
        assert center == (150, 200)

    def test_detection_area(self):
        """Test Detection area property."""
        detection = Detection(
            bbox=(100, 100, 200, 300),
            confidence=0.95,
            class_id=0,
            class_name="person"
        )

        area = detection.area
        assert area == (200 - 100) * (300 - 100)  # 100 * 200 = 20000

    def test_detection_iou_no_overlap(self):
        """Test IoU calculation with no overlap."""
        det1 = Detection(bbox=(0, 0, 100, 100), confidence=0.9, class_id=0, class_name="person")
        det2 = Detection(bbox=(200, 200, 300, 300), confidence=0.9, class_id=0, class_name="person")

        iou = det1.iou(det2)
        assert iou == 0.0

    def test_detection_iou_partial_overlap(self):
        """Test IoU calculation with partial overlap."""
        det1 = Detection(bbox=(0, 0, 100, 100), confidence=0.9, class_id=0, class_name="person")
        det2 = Detection(bbox=(50, 50, 150, 150), confidence=0.9, class_id=0, class_name="person")

        iou = det1.iou(det2)
        # Intersection: 50x50 = 2500
        # Union: 10000 + 10000 - 2500 = 17500
        # IoU = 2500 / 17500 = 0.142857...
        assert 0.14 <= iou <= 0.15

    def test_detection_iou_complete_overlap(self):
        """Test IoU calculation with complete overlap."""
        det1 = Detection(bbox=(0, 0, 100, 100), confidence=0.9, class_id=0, class_name="person")
        det2 = Detection(bbox=(0, 0, 100, 100), confidence=0.9, class_id=0, class_name="person")

        iou = det1.iou(det2)
        assert iou == 1.0

    def test_detection_distance(self):
        """Test distance calculation between detections."""
        det1 = Detection(bbox=(0, 0, 100, 100), confidence=0.9, class_id=0, class_name="person")
        det2 = Detection(bbox=(300, 400, 400, 500), confidence=0.9, class_id=1, class_name="helmet")

        distance = det1.distance_to(det2)
        # Center of det1: (50, 50)
        # Center of det2: (350, 450)
        # Distance = sqrt((350-50)^2 + (450-50)^2) = sqrt(90000 + 160000) = sqrt(250000) = 500
        assert abs(distance - 500.0) < 1.0


@pytest.mark.unit
class TestComplianceResult:
    """Test ComplianceResult dataclass functionality."""

    def test_compliance_result_compliant(self):
        """Test compliant worker status."""
        person = Detection(bbox=(100, 100, 300, 500), confidence=0.9, class_id=0, class_name="person")
        helmet = Detection(bbox=(150, 100, 250, 150), confidence=0.85, class_id=1, class_name="helmet")
        vest = Detection(bbox=(150, 200, 250, 400), confidence=0.88, class_id=2, class_name="vest")

        result = ComplianceResult(
            person_detection=person,
            has_helmet=True,
            has_vest=True,
            is_compliant=True,
            helmet_detection=helmet,
            vest_detection=vest,
            confidence_score=0.865
        )

        assert result.is_compliant is True
        assert result.compliance_status == "COMPLIANT"

    def test_compliance_result_missing_helmet(self):
        """Test worker missing helmet."""
        person = Detection(bbox=(100, 100, 300, 500), confidence=0.9, class_id=0, class_name="person")
        vest = Detection(bbox=(150, 200, 250, 400), confidence=0.88, class_id=2, class_name="vest")

        result = ComplianceResult(
            person_detection=person,
            has_helmet=False,
            has_vest=True,
            is_compliant=False,
            vest_detection=vest
        )

        assert result.is_compliant is False
        assert result.compliance_status == "MISSING HELMET"

    def test_compliance_result_missing_vest(self):
        """Test worker missing vest."""
        person = Detection(bbox=(100, 100, 300, 500), confidence=0.9, class_id=0, class_name="person")
        helmet = Detection(bbox=(150, 100, 250, 150), confidence=0.85, class_id=1, class_name="helmet")

        result = ComplianceResult(
            person_detection=person,
            has_helmet=True,
            has_vest=False,
            is_compliant=False,
            helmet_detection=helmet
        )

        assert result.is_compliant is False
        assert result.compliance_status == "MISSING VEST"

    def test_compliance_result_missing_both(self):
        """Test worker missing both helmet and vest."""
        person = Detection(bbox=(100, 100, 300, 500), confidence=0.9, class_id=0, class_name="person")

        result = ComplianceResult(
            person_detection=person,
            has_helmet=False,
            has_vest=False,
            is_compliant=False
        )

        assert result.is_compliant is False
        assert result.compliance_status == "MISSING HELMET & VEST"


@pytest.mark.unit
@pytest.mark.model
class TestPPEDetector:
    """Test PPEDetector class."""

    @patch('models.ppe_detector.YOLO')
    def test_detector_initialization(self, mock_yolo, model_config):
        """Test detector initialization."""
        detector = PPEDetector(config=model_config, verbose=False)

        assert detector.config == model_config
        assert detector.stats["total_detections"] == 0
        assert detector.stats["total_frames_processed"] == 0

    @patch('models.ppe_detector.YOLO')
    def test_detector_invalid_config(self, mock_yolo):
        """Test detector with invalid configuration."""
        config = ModelConfig(
            confidence_threshold=1.5,  # Invalid: > 1.0
            nms_threshold=0.5
        )

        with pytest.raises(ValueError):
            PPEDetector(config=config, verbose=False)

    def test_preprocess_image(self, model_config, sample_image):
        """Test image preprocessing."""
        with patch('models.ppe_detector.YOLO'):
            detector = PPEDetector(config=model_config, verbose=False)

            # Test resize
            resized = detector.preprocess_image(sample_image, target_size=(320, 320))
            assert resized.shape == (320, 320, 3)

    @patch('models.ppe_detector.YOLO')
    def test_detect_ppe_with_mock_results(self, mock_yolo, model_config, sample_image):
        """Test PPE detection with mocked model results."""
        # Mock YOLO model and results
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model

        # Mock detection results
        mock_result = MagicMock()
        mock_result.boxes = MagicMock()
        mock_result.boxes.xyxy.cpu().numpy.return_value = np.array([
            [100, 100, 200, 300],  # person
            [110, 100, 150, 130],  # helmet
        ])
        mock_result.boxes.conf.cpu().numpy.return_value = np.array([0.95, 0.88])
        mock_result.boxes.cls.cpu().numpy.return_value = np.array([0, 1])

        mock_model.predict.return_value = [mock_result]

        detector = PPEDetector(config=model_config, verbose=False)
        detections = detector.detect_ppe(sample_image)

        assert len(detections) == 2
        assert detections[0].class_name == "person"
        assert detections[1].class_name == "helmet"
        assert detector.stats["total_frames_processed"] == 1

    @patch('models.ppe_detector.YOLO')
    def test_detect_ppe_from_file_path(self, mock_yolo, model_config, tmp_path):
        """Test detection from file path."""
        # Create test image file
        img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        img_path = tmp_path / "test.jpg"
        cv2.imwrite(str(img_path), img)

        # Mock model
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model
        mock_model.predict.return_value = []

        detector = PPEDetector(config=model_config, verbose=False)
        detections = detector.detect_ppe(str(img_path))

        assert isinstance(detections, list)

    @patch('models.ppe_detector.YOLO')
    def test_detect_ppe_invalid_image(self, mock_yolo, model_config):
        """Test detection with invalid image."""
        detector = PPEDetector(config=model_config, verbose=False)

        with pytest.raises(ValueError):
            detector.detect_ppe("/nonexistent/image.jpg")

    @patch('models.ppe_detector.YOLO')
    def test_is_compliant_single_compliant_worker(self, mock_yolo, model_config):
        """Test compliance check with single compliant worker."""
        detector = PPEDetector(config=model_config, verbose=False)

        detections = [
            Detection(bbox=(100, 100, 300, 500), confidence=0.95, class_id=0, class_name="person"),
            Detection(bbox=(150, 100, 250, 150), confidence=0.88, class_id=1, class_name="helmet"),
            Detection(bbox=(150, 200, 250, 400), confidence=0.85, class_id=2, class_name="vest"),
        ]

        results = detector.is_compliant(detections)

        assert len(results) == 1
        assert results[0].is_compliant is True
        assert results[0].has_helmet is True
        assert results[0].has_vest is True

    @patch('models.ppe_detector.YOLO')
    def test_is_compliant_non_compliant_worker(self, mock_yolo, model_config):
        """Test compliance check with non-compliant worker (missing helmet)."""
        detector = PPEDetector(config=model_config, verbose=False)

        detections = [
            Detection(bbox=(100, 100, 300, 500), confidence=0.95, class_id=0, class_name="person"),
            Detection(bbox=(150, 200, 250, 400), confidence=0.85, class_id=2, class_name="vest"),
        ]

        results = detector.is_compliant(detections)

        assert len(results) == 1
        assert results[0].is_compliant is False
        assert results[0].has_helmet is False
        assert results[0].has_vest is True

    @patch('models.ppe_detector.YOLO')
    def test_is_compliant_multiple_workers(self, mock_yolo, model_config):
        """Test compliance check with multiple workers."""
        detector = PPEDetector(config=model_config, verbose=False)

        detections = [
            # Worker 1 - compliant
            Detection(bbox=(50, 100, 150, 500), confidence=0.95, class_id=0, class_name="person"),
            Detection(bbox=(75, 100, 125, 150), confidence=0.88, class_id=1, class_name="helmet"),
            Detection(bbox=(75, 200, 125, 400), confidence=0.85, class_id=2, class_name="vest"),
            # Worker 2 - non-compliant (no helmet)
            Detection(bbox=(300, 100, 400, 500), confidence=0.92, class_id=0, class_name="person"),
            Detection(bbox=(325, 200, 375, 400), confidence=0.83, class_id=2, class_name="vest"),
        ]

        results = detector.is_compliant(detections)

        assert len(results) == 2
        assert results[0].is_compliant is True
        assert results[1].is_compliant is False

    @patch('models.ppe_detector.YOLO')
    def test_visualize_detections(self, mock_yolo, model_config, sample_image):
        """Test detection visualization."""
        detector = PPEDetector(config=model_config, verbose=False)

        detections = [
            Detection(bbox=(100, 100, 200, 200), confidence=0.95, class_id=0, class_name="person"),
        ]

        output = detector.visualize_detections(sample_image, detections)

        assert output.shape == sample_image.shape
        assert not np.array_equal(output, sample_image)  # Image should be modified

    @patch('models.ppe_detector.YOLO')
    def test_visualize_compliance(self, mock_yolo, model_config, sample_image):
        """Test compliance visualization."""
        detector = PPEDetector(config=model_config, verbose=False)

        person = Detection(bbox=(100, 100, 300, 500), confidence=0.95, class_id=0, class_name="person")
        compliance_results = [
            ComplianceResult(
                person_detection=person,
                has_helmet=True,
                has_vest=True,
                is_compliant=True
            )
        ]

        output = detector.visualize_compliance(sample_image, compliance_results)

        assert output.shape == sample_image.shape
        assert not np.array_equal(output, sample_image)

    @patch('models.ppe_detector.YOLO')
    def test_get_statistics(self, mock_yolo, model_config):
        """Test statistics retrieval."""
        detector = PPEDetector(config=model_config, verbose=False)

        # Simulate some processing
        detector.stats["total_persons_detected"] = 10
        detector.stats["total_compliant"] = 8
        detector.stats["total_non_compliant"] = 2

        stats = detector.get_statistics()

        assert stats["total_persons_detected"] == 10
        assert stats["compliance_rate"] == 0.8

    @patch('models.ppe_detector.YOLO')
    def test_reset_statistics(self, mock_yolo, model_config):
        """Test statistics reset."""
        detector = PPEDetector(config=model_config, verbose=False)

        # Set some stats
        detector.stats["total_detections"] = 100
        detector.stats["total_frames_processed"] = 50

        # Reset
        detector.reset_statistics()

        assert detector.stats["total_detections"] == 0
        assert detector.stats["total_frames_processed"] == 0


@pytest.mark.unit
@pytest.mark.turkish
class TestTurkishConstructionScenarios:
    """Test scenarios specific to Turkish construction sites."""

    @patch('models.ppe_detector.YOLO')
    def test_multiple_workers_turkish_site(self, mock_yolo, model_config):
        """Test detection with multiple workers on Turkish construction site."""
        detector = PPEDetector(config=model_config, verbose=False)

        # Simulate 5 workers with varying compliance
        detections = [
            # Worker 1 - Compliant (baret + yelek)
            Detection(bbox=(50, 100, 100, 400), confidence=0.95, class_id=0, class_name="person"),
            Detection(bbox=(60, 100, 90, 140), confidence=0.92, class_id=1, class_name="helmet"),
            Detection(bbox=(55, 200, 95, 350), confidence=0.88, class_id=2, class_name="vest"),

            # Worker 2 - Missing helmet (only yelek)
            Detection(bbox=(150, 100, 200, 400), confidence=0.93, class_id=0, class_name="person"),
            Detection(bbox=(155, 200, 195, 350), confidence=0.85, class_id=2, class_name="vest"),

            # Worker 3 - Compliant
            Detection(bbox=(250, 100, 300, 400), confidence=0.94, class_id=0, class_name="person"),
            Detection(bbox=(260, 100, 290, 140), confidence=0.90, class_id=1, class_name="helmet"),
            Detection(bbox=(255, 200, 295, 350), confidence=0.87, class_id=2, class_name="vest"),

            # Worker 4 - Missing both
            Detection(bbox=(350, 100, 400, 400), confidence=0.91, class_id=0, class_name="person"),

            # Worker 5 - Compliant
            Detection(bbox=(450, 100, 500, 400), confidence=0.96, class_id=0, class_name="person"),
            Detection(bbox=(460, 100, 490, 140), confidence=0.91, class_id=1, class_name="helmet"),
            Detection(bbox=(455, 200, 495, 350), confidence=0.89, class_id=2, class_name="vest"),
        ]

        results = detector.is_compliant(detections)

        assert len(results) == 5
        compliant_count = sum(1 for r in results if r.is_compliant)
        assert compliant_count == 3  # Workers 1, 3, 5

    @patch('models.ppe_detector.YOLO')
    def test_partial_ppe_scenarios(self, mock_yolo, model_config):
        """Test partial PPE scenarios (helmet but no vest, or vice versa)."""
        detector = PPEDetector(config=model_config, verbose=False)

        # Test: helmet only
        detections_helmet_only = [
            Detection(bbox=(100, 100, 200, 400), confidence=0.95, class_id=0, class_name="person"),
            Detection(bbox=(120, 100, 180, 140), confidence=0.90, class_id=1, class_name="helmet"),
        ]

        results = detector.is_compliant(detections_helmet_only)
        assert len(results) == 1
        assert results[0].has_helmet is True
        assert results[0].has_vest is False
        assert results[0].is_compliant is False

        # Test: vest only
        detections_vest_only = [
            Detection(bbox=(100, 100, 200, 400), confidence=0.95, class_id=0, class_name="person"),
            Detection(bbox=(110, 200, 190, 350), confidence=0.88, class_id=2, class_name="vest"),
        ]

        results = detector.is_compliant(detections_vest_only)
        assert len(results) == 1
        assert results[0].has_helmet is False
        assert results[0].has_vest is True
        assert results[0].is_compliant is False
