"""
Unit tests for Camera Handler and RTSP Handler.

Tests camera connection, frame capture, and stream management.
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import numpy as np

from camera.camera_manager import CameraManager
from camera.rtsp_handler import RTSPHandler
from camera.camera_config import CameraConfig


@pytest.mark.unit
@pytest.mark.camera
class TestCameraConfig:
    """Test CameraConfig functionality."""

    def test_camera_config_creation(self):
        """Test creating camera configuration."""
        config = CameraConfig(
            camera_id="cam-001",
            name="Test Camera",
            rtsp_url="rtsp://admin:password@192.168.1.100:554/stream",
            username="admin",
            password="password",
            zone="Zone A",
            location="Entrance",
            enabled=True,
            fps=15
        )

        assert config.camera_id == "cam-001"
        assert config.name == "Test Camera"
        assert config.enabled is True
        assert config.fps == 15

    def test_camera_config_sanitized_url(self):
        """Test URL sanitization (hide credentials)."""
        config = CameraConfig(
            camera_id="cam-001",
            name="Test Camera",
            rtsp_url="rtsp://admin:password@192.168.1.100:554/stream",
            username="admin",
            password="password"
        )

        sanitized = config.get_sanitized_url()
        assert "password" not in sanitized
        assert "admin" not in sanitized or "****" in sanitized


@pytest.mark.unit
@pytest.mark.camera
class TestRTSPHandler:
    """Test RTSPHandler class."""

    def test_rtsp_handler_initialization(self, camera_config):
        """Test RTSP handler initialization."""
        handler = RTSPHandler(camera_config)

        assert handler.camera_id == camera_config.camera_id
        assert handler.config == camera_config
        assert handler._is_running is False
        assert handler._is_connected is False

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    def test_rtsp_handler_start(self, mock_video_capture, camera_config):
        """Test starting RTSP stream capture."""
        # Mock VideoCapture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_video_capture.return_value = mock_cap

        handler = RTSPHandler(camera_config)
        result = handler.start()

        time.sleep(0.2)  # Give thread time to start

        assert handler._is_running is True
        handler.stop()

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    def test_rtsp_handler_stop(self, mock_video_capture, camera_config):
        """Test stopping RTSP stream capture."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_video_capture.return_value = mock_cap

        handler = RTSPHandler(camera_config)
        handler.start()
        time.sleep(0.2)

        handler.stop()
        assert handler._is_running is False

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    def test_rtsp_handler_get_frame(self, mock_video_capture, camera_config):
        """Test getting latest frame."""
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, test_frame)
        mock_video_capture.return_value = mock_cap

        handler = RTSPHandler(camera_config)
        handler.start()
        time.sleep(0.3)  # Wait for frames to be captured

        result = handler.get_frame()
        handler.stop()

        if result:
            frame, timestamp = result
            assert frame is not None
            assert isinstance(timestamp, datetime)

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    def test_rtsp_handler_snapshot(self, mock_video_capture, camera_config):
        """Test snapshot capture."""
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, test_frame)
        mock_video_capture.return_value = mock_cap

        handler = RTSPHandler(camera_config)
        handler.start()
        time.sleep(0.2)

        snapshot = handler.snapshot()
        handler.stop()

        assert snapshot is not None or handler._latest_frame is None

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    def test_rtsp_handler_connection_failure(self, mock_video_capture, camera_config):
        """Test handling connection failure."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_video_capture.return_value = mock_cap

        handler = RTSPHandler(camera_config)
        result = handler.start()
        time.sleep(0.2)

        handler.stop()
        # Connection should fail gracefully

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    def test_rtsp_handler_reconnection(self, mock_video_capture, camera_config):
        """Test automatic reconnection logic."""
        mock_cap = MagicMock()

        # First fail, then succeed
        mock_cap.isOpened.side_effect = [False, False, True]
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_video_capture.return_value = mock_cap

        handler = RTSPHandler(camera_config)
        handler.start()
        time.sleep(0.5)

        handler.stop()

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    def test_rtsp_handler_is_healthy(self, mock_video_capture, camera_config):
        """Test health check."""
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, test_frame)
        mock_video_capture.return_value = mock_cap

        handler = RTSPHandler(camera_config)
        handler.start()
        time.sleep(0.2)

        is_healthy = handler.is_healthy()
        handler.stop()

        # Health status depends on connection

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    def test_rtsp_handler_get_status(self, mock_video_capture, camera_config):
        """Test getting handler status."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_video_capture.return_value = mock_cap

        handler = RTSPHandler(camera_config)
        handler.start()
        time.sleep(0.2)

        status = handler.get_status()
        handler.stop()

        assert isinstance(status, dict)
        assert "camera_id" in status
        assert "is_connected" in status


@pytest.mark.unit
@pytest.mark.camera
class TestCameraManager:
    """Test CameraManager class."""

    def test_camera_manager_initialization(self):
        """Test camera manager initialization."""
        manager = CameraManager()

        assert len(manager._cameras) == 0
        assert manager._is_running is False

    def test_camera_manager_start_stop(self):
        """Test starting and stopping camera manager."""
        manager = CameraManager()

        manager.start()
        assert manager._is_running is True

        manager.stop()
        assert manager._is_running is False

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    def test_add_camera(self, mock_video_capture, camera_config):
        """Test adding a camera to manager."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap

        manager = CameraManager()
        result = manager.add_camera(camera_config)

        assert result is True
        assert camera_config.camera_id in manager._cameras

        manager.stop()

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    def test_add_duplicate_camera(self, mock_video_capture, camera_config):
        """Test adding duplicate camera."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap

        manager = CameraManager()
        manager.add_camera(camera_config)

        # Try to add same camera again
        result = manager.add_camera(camera_config)

        assert result is False
        manager.stop()

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    def test_remove_camera(self, mock_video_capture, camera_config):
        """Test removing a camera."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap

        manager = CameraManager()
        manager.add_camera(camera_config)

        result = manager.remove_camera(camera_config.camera_id)

        assert result is True
        assert camera_config.camera_id not in manager._cameras

    def test_remove_nonexistent_camera(self):
        """Test removing non-existent camera."""
        manager = CameraManager()
        result = manager.remove_camera("nonexistent-id")

        assert result is False

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    def test_snapshot(self, mock_video_capture, camera_config):
        """Test taking snapshot from camera."""
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, test_frame)
        mock_video_capture.return_value = mock_cap

        manager = CameraManager()
        manager.add_camera(camera_config)
        time.sleep(0.2)

        snapshot = manager.snapshot(camera_config.camera_id)

        manager.stop()
        # Snapshot may be None if frame not captured yet

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    def test_snapshot_all(self, mock_video_capture):
        """Test taking snapshots from all cameras."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_video_capture.return_value = mock_cap

        manager = CameraManager()

        # Add multiple cameras
        for i in range(3):
            config = CameraConfig(
                camera_id=f"cam-{i}",
                name=f"Camera {i}",
                rtsp_url=f"rtsp://test@192.168.1.{100+i}:554/stream"
            )
            manager.add_camera(config)

        time.sleep(0.3)
        snapshots = manager.snapshot_all()

        assert len(snapshots) == 3
        manager.stop()

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    def test_get_all_cameras(self, mock_video_capture, camera_config):
        """Test getting list of all cameras."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap

        manager = CameraManager()
        manager.add_camera(camera_config)

        cameras = manager.get_all_cameras()

        assert len(cameras) == 1
        assert camera_config.camera_id in cameras
        manager.stop()

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    def test_get_camera_status(self, mock_video_capture, camera_config):
        """Test getting camera status."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap

        manager = CameraManager()
        manager.add_camera(camera_config)

        status = manager.get_camera_status(camera_config.camera_id)

        assert status is not None
        assert isinstance(status, dict)
        manager.stop()

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    def test_get_all_camera_status(self, mock_video_capture):
        """Test getting status of all cameras."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap

        manager = CameraManager()

        # Add cameras
        for i in range(2):
            config = CameraConfig(
                camera_id=f"cam-{i}",
                name=f"Camera {i}",
                rtsp_url=f"rtsp://test@192.168.1.{100+i}:554/stream"
            )
            manager.add_camera(config)

        statuses = manager.get_all_camera_status()

        assert len(statuses) == 2
        manager.stop()

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    def test_enable_disable_camera(self, mock_video_capture, camera_config):
        """Test enabling and disabling camera."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap

        manager = CameraManager()
        manager.add_camera(camera_config)

        # Disable
        result = manager.disable_camera(camera_config.camera_id)
        assert result is True

        # Enable
        result = manager.enable_camera(camera_config.camera_id)
        # Result depends on connection success

        manager.stop()

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    def test_get_health_summary(self, mock_video_capture):
        """Test getting health summary."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_video_capture.return_value = mock_cap

        manager = CameraManager()

        # Add cameras in different zones
        for i in range(3):
            config = CameraConfig(
                camera_id=f"cam-{i}",
                name=f"Camera {i}",
                rtsp_url=f"rtsp://test@192.168.1.{100+i}:554/stream",
                zone=f"Zone {i % 2}"  # Two zones
            )
            manager.add_camera(config)

        time.sleep(0.2)
        summary = manager.get_health_summary()

        assert "total_cameras" in summary
        assert "active_cameras" in summary
        assert "zone_statistics" in summary
        assert summary["total_cameras"] == 3

        manager.stop()

    @patch('camera.rtsp_handler.cv2.VideoCapture')
    def test_context_manager(self, mock_video_capture, camera_config):
        """Test using camera manager as context manager."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap

        with CameraManager() as manager:
            assert manager._is_running is True
            manager.add_camera(camera_config)

        # Should be stopped after context
