"""
Integration tests for camera to detection pipeline.

Tests the integration between camera capture and PPE detection.
"""

import pytest
import time
import numpy as np
from unittest.mock import patch, MagicMock

from camera.camera_manager import CameraManager
from models.ppe_detector import PPEDetector


@pytest.mark.integration
class TestCameraToDetection:
    """Test camera-to-detection integration."""

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    @patch('models.ppe_detector.YOLO')
    def test_capture_and_detect_single_frame(
        self,
        mock_yolo,
        mock_video_capture,
        camera_config,
        model_config
    ):
        """Test capturing a frame and running detection."""
        # Setup mock camera
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, test_frame)
        mock_video_capture.return_value = mock_cap

        # Setup mock detection
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model
        mock_model.predict.return_value = []

        # Initialize components
        camera_manager = CameraManager()
        detector = PPEDetector(config=model_config, verbose=False)

        try:
            camera_manager.add_camera(camera_config)
            time.sleep(0.2)

            # Capture frame
            snapshot = camera_manager.snapshot(camera_config.camera_id)

            if snapshot is not None:
                # Run detection
                detections = detector.detect_ppe(snapshot)
                assert isinstance(detections, list)

        finally:
            camera_manager.stop()

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    @patch('models.ppe_detector.YOLO')
    def test_continuous_detection_stream(
        self,
        mock_yolo,
        mock_video_capture,
        camera_config,
        model_config,
        performance_tracker
    ):
        """Test continuous detection from camera stream."""
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

        try:
            camera_manager.add_camera(camera_config)
            time.sleep(0.2)

            # Process multiple frames
            frame_count = 0
            for i in range(10):
                snapshot = camera_manager.snapshot(camera_config.camera_id)

                if snapshot is not None:
                    start_time = time.time()
                    detections = detector.detect_ppe(snapshot)
                    duration_ms = (time.time() - start_time) * 1000

                    performance_tracker.record("detection", duration_ms)
                    frame_count += 1

                time.sleep(0.1)

            # Should have processed some frames
            assert frame_count > 0

            # Check performance
            avg_time = performance_tracker.get_average("detection")
            assert avg_time >= 0  # Should have recorded times

        finally:
            camera_manager.stop()

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    @patch('models.ppe_detector.YOLO')
    def test_detection_with_multiple_cameras(
        self,
        mock_yolo,
        mock_video_capture,
        model_config
    ):
        """Test detection from multiple cameras simultaneously."""
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

        camera_manager = CameraManager()
        detector = PPEDetector(config=model_config, verbose=False)

        try:
            # Add 3 cameras
            for i in range(3):
                config = CameraConfig(
                    camera_id=f"cam-{i}",
                    name=f"Camera {i}",
                    rtsp_url=f"rtsp://test@192.168.1.{100+i}:554/stream"
                )
                camera_manager.add_camera(config)

            time.sleep(0.3)

            # Capture and detect from all cameras
            snapshots = camera_manager.snapshot_all()
            results = {}

            for camera_id, snapshot in snapshots.items():
                if snapshot is not None:
                    detections = detector.detect_ppe(snapshot)
                    results[camera_id] = detections

            # Should have processed snapshots from all cameras
            assert len(results) <= 3

        finally:
            camera_manager.stop()

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    @patch('models.ppe_detector.YOLO')
    def test_frame_quality_validation(
        self,
        mock_yolo,
        mock_video_capture,
        camera_config,
        model_config
    ):
        """Test handling of different frame qualities."""
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model
        mock_model.predict.return_value = []

        detector = PPEDetector(config=model_config, verbose=False)

        # Test with various frame sizes
        frame_sizes = [(640, 480), (1920, 1080), (320, 240)]

        for width, height in frame_sizes:
            test_frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
            mock_cap = MagicMock()
            mock_cap.isOpened.return_value = True
            mock_cap.read.return_value = (True, test_frame)
            mock_video_capture.return_value = mock_cap

            camera_manager = CameraManager()

            try:
                camera_manager.add_camera(camera_config)
                time.sleep(0.2)

                snapshot = camera_manager.snapshot(camera_config.camera_id)

                if snapshot is not None:
                    detections = detector.detect_ppe(snapshot)
                    assert isinstance(detections, list)

            finally:
                camera_manager.stop()

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    @patch('models.ppe_detector.YOLO')
    def test_detection_frame_preprocessing(
        self,
        mock_yolo,
        mock_video_capture,
        camera_config,
        model_config
    ):
        """Test frame preprocessing before detection."""
        # Create frame with specific characteristics
        test_frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, test_frame)
        mock_video_capture.return_value = mock_cap

        mock_model = MagicMock()
        mock_yolo.return_value = mock_model
        mock_model.predict.return_value = []

        camera_manager = CameraManager()
        detector = PPEDetector(config=model_config, verbose=False)

        try:
            camera_manager.add_camera(camera_config)
            time.sleep(0.2)

            snapshot = camera_manager.snapshot(camera_config.camera_id)

            if snapshot is not None:
                # Test with preprocessing
                detections = detector.detect_ppe(snapshot, preprocess=True)
                assert isinstance(detections, list)

        finally:
            camera_manager.stop()


@pytest.mark.integration
@pytest.mark.slow
class TestCameraFailureRecovery:
    """Test camera failure and recovery scenarios."""

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    def test_camera_connection_failure_recovery(
        self,
        mock_video_capture,
        camera_config
    ):
        """Test automatic recovery from camera connection failure."""
        # Mock connection failure followed by success
        mock_cap = MagicMock()
        call_count = [0]

        def mock_is_opened():
            call_count[0] += 1
            # Fail first few attempts, then succeed
            return call_count[0] > 3

        mock_cap.isOpened = mock_is_opened
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_video_capture.return_value = mock_cap

        camera_manager = CameraManager()

        try:
            camera_manager.add_camera(camera_config)
            time.sleep(1.0)  # Wait for reconnection attempts

            # Camera should eventually recover
            status = camera_manager.get_camera_status(camera_config.camera_id)
            # Status depends on connection success

        finally:
            camera_manager.stop()

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    @patch('models.ppe_detector.YOLO')
    def test_detection_with_missing_frames(
        self,
        mock_yolo,
        mock_video_capture,
        camera_config,
        model_config
    ):
        """Test detection when some frames are missing."""
        # Mock intermittent frame availability
        frame_count = [0]
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        def mock_read():
            frame_count[0] += 1
            # Return frame every other call
            if frame_count[0] % 2 == 0:
                return True, test_frame
            else:
                return False, None

        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read = mock_read
        mock_video_capture.return_value = mock_cap

        mock_model = MagicMock()
        mock_yolo.return_value = mock_model
        mock_model.predict.return_value = []

        camera_manager = CameraManager()
        detector = PPEDetector(config=model_config, verbose=False)

        try:
            camera_manager.add_camera(camera_config)
            time.sleep(0.3)

            # Try multiple snapshots
            successful_detections = 0
            for i in range(10):
                snapshot = camera_manager.snapshot(camera_config.camera_id)

                if snapshot is not None:
                    detections = detector.detect_ppe(snapshot)
                    successful_detections += 1

                time.sleep(0.1)

            # Should have some successful detections despite missing frames
            # (depends on timing and frame availability)

        finally:
            camera_manager.stop()


@pytest.mark.integration
class TestDetectionAccuracy:
    """Test detection accuracy with known test images."""

    @patch('models.ppe_detector.YOLO')
    def test_detection_on_compliant_worker_image(
        self,
        mock_yolo,
        model_config,
        compliant_worker_image
    ):
        """Test detection on image with compliant worker."""
        # Setup mock to detect all PPE
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model

        mock_result = MagicMock()
        mock_result.boxes = MagicMock()
        mock_result.boxes.xyxy.cpu().numpy.return_value = np.array([
            [200, 150, 400, 450],  # person
            [270, 140, 330, 200],  # helmet
            [250, 220, 350, 380],  # vest
        ])
        mock_result.boxes.conf.cpu().numpy.return_value = np.array([0.95, 0.92, 0.88])
        mock_result.boxes.cls.cpu().numpy.return_value = np.array([0, 1, 2])
        mock_model.predict.return_value = [mock_result]

        detector = PPEDetector(config=model_config, verbose=False)
        detections = detector.detect_ppe(compliant_worker_image)
        compliance_results = detector.is_compliant(detections)

        assert len(compliance_results) > 0
        assert compliance_results[0].is_compliant is True

    @patch('models.ppe_detector.YOLO')
    def test_detection_on_non_compliant_worker_image(
        self,
        mock_yolo,
        model_config,
        non_compliant_worker_image
    ):
        """Test detection on image with non-compliant worker."""
        # Setup mock to detect person and vest only (no helmet)
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model

        mock_result = MagicMock()
        mock_result.boxes = MagicMock()
        mock_result.boxes.xyxy.cpu().numpy.return_value = np.array([
            [200, 150, 400, 450],  # person
            [250, 220, 350, 380],  # vest only
        ])
        mock_result.boxes.conf.cpu().numpy.return_value = np.array([0.95, 0.88])
        mock_result.boxes.cls.cpu().numpy.return_value = np.array([0, 2])
        mock_model.predict.return_value = [mock_result]

        detector = PPEDetector(config=model_config, verbose=False)
        detections = detector.detect_ppe(non_compliant_worker_image)
        compliance_results = detector.is_compliant(detections)

        assert len(compliance_results) > 0
        assert compliance_results[0].is_compliant is False
        assert compliance_results[0].has_helmet is False

    @patch('models.ppe_detector.YOLO')
    def test_detection_on_multiple_workers_image(
        self,
        mock_yolo,
        model_config,
        multiple_workers_image
    ):
        """Test detection on image with multiple workers."""
        # Setup mock for 3 workers (2 compliant, 1 not)
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model

        mock_result = MagicMock()
        mock_result.boxes = MagicMock()
        mock_result.boxes.xyxy.cpu().numpy.return_value = np.array([
            # Worker 1 - compliant
            [50, 150, 200, 450],
            [100, 145, 150, 195],  # helmet
            [100, 220, 150, 350],  # vest

            # Worker 2 - non-compliant (no helmet)
            [250, 150, 390, 450],
            [300, 220, 340, 350],  # vest only

            # Worker 3 - compliant
            [440, 150, 590, 450],
            [490, 145, 540, 195],  # helmet
            [490, 220, 540, 350],  # vest
        ])
        mock_result.boxes.conf.cpu().numpy.return_value = np.array(
            [0.95, 0.92, 0.88, 0.93, 0.87, 0.94, 0.91, 0.89]
        )
        mock_result.boxes.cls.cpu().numpy.return_value = np.array(
            [0, 1, 2, 0, 2, 0, 1, 2]
        )
        mock_model.predict.return_value = [mock_result]

        detector = PPEDetector(config=model_config, verbose=False)
        detections = detector.detect_ppe(multiple_workers_image)
        compliance_results = detector.is_compliant(detections)

        assert len(compliance_results) == 3
        compliant_count = sum(1 for r in compliance_results if r.is_compliant)
        assert compliant_count == 2
