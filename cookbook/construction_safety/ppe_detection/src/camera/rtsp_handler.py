"""RTSP stream handler for capturing frames from IP cameras"""

import cv2
import threading
import time
import logging
from typing import Optional, Tuple
from datetime import datetime
import numpy as np

from .camera_config import CameraConfig


logger = logging.getLogger(__name__)


class RTSPHandler:
    """
    Handles RTSP stream connection and frame capture for a single camera.

    Features:
    - Automatic reconnection on connection loss
    - Thread-safe frame access
    - Configurable capture intervals
    - Memory efficient (stores only latest frame)
    - Connection health monitoring
    """

    def __init__(self, config: CameraConfig):
        """
        Initialize RTSP handler

        Args:
            config: Camera configuration
        """
        self.config = config
        self.camera_id = config.camera_id

        # Connection state
        self._capture: Optional[cv2.VideoCapture] = None
        self._is_running = False
        self._is_connected = False
        self._capture_thread: Optional[threading.Thread] = None

        # Frame storage (thread-safe)
        self._frame_lock = threading.Lock()
        self._latest_frame: Optional[np.ndarray] = None
        self._latest_timestamp: Optional[datetime] = None

        # Connection monitoring
        self._consecutive_failures = 0
        self._last_connection_attempt: Optional[datetime] = None
        self._connection_start_time: Optional[datetime] = None
        self._total_frames_captured = 0
        self._last_error: Optional[str] = None

        logger.info(f"Initialized RTSP handler for camera: {self.camera_id}")

    def start(self) -> bool:
        """
        Start capturing frames from the RTSP stream

        Returns:
            True if started successfully, False otherwise
        """
        if self._is_running:
            logger.warning(f"Camera {self.camera_id} is already running")
            return True

        logger.info(f"Starting camera {self.camera_id}: {self.config.get_sanitized_url()}")

        self._is_running = True
        self._capture_thread = threading.Thread(
            target=self._capture_loop,
            name=f"RTSP-{self.camera_id}",
            daemon=True
        )
        self._capture_thread.start()

        # Wait a moment to check if connection succeeds
        time.sleep(0.5)

        return self._is_connected

    def stop(self) -> None:
        """Stop capturing frames and release resources"""
        logger.info(f"Stopping camera {self.camera_id}")

        self._is_running = False

        if self._capture_thread and self._capture_thread.is_alive():
            self._capture_thread.join(timeout=5.0)

        self._release_capture()

        logger.info(f"Camera {self.camera_id} stopped. Total frames captured: {self._total_frames_captured}")

    def get_frame(self) -> Optional[Tuple[np.ndarray, datetime]]:
        """
        Get the latest captured frame (thread-safe)

        Returns:
            Tuple of (frame, timestamp) or None if no frame available
        """
        with self._frame_lock:
            if self._latest_frame is not None:
                return self._latest_frame.copy(), self._latest_timestamp
            return None

    def snapshot(self) -> Optional[np.ndarray]:
        """
        Get the latest frame as a snapshot

        Returns:
            Frame as numpy array or None if no frame available
        """
        result = self.get_frame()
        if result:
            return result[0]
        return None

    def is_healthy(self) -> bool:
        """
        Check if camera connection is healthy

        Returns:
            True if connected and capturing frames, False otherwise
        """
        if not self._is_running or not self._is_connected:
            return False

        # Check if we have a recent frame (within last 30 seconds)
        if self._latest_timestamp:
            age = (datetime.now() - self._latest_timestamp).total_seconds()
            return age < 30

        return False

    def get_status(self) -> dict:
        """
        Get detailed status information

        Returns:
            Dictionary with status information
        """
        uptime = None
        if self._connection_start_time:
            uptime = (datetime.now() - self._connection_start_time).total_seconds()

        frame_age = None
        if self._latest_timestamp:
            frame_age = (datetime.now() - self._latest_timestamp).total_seconds()

        return {
            'camera_id': self.camera_id,
            'name': self.config.name,
            'zone': self.config.zone,
            'is_running': self._is_running,
            'is_connected': self._is_connected,
            'is_healthy': self.is_healthy(),
            'total_frames_captured': self._total_frames_captured,
            'consecutive_failures': self._consecutive_failures,
            'uptime_seconds': uptime,
            'last_frame_age_seconds': frame_age,
            'last_error': self._last_error,
            'rtsp_url': self.config.get_sanitized_url()
        }

    def _capture_loop(self) -> None:
        """Main capture loop (runs in separate thread)"""
        logger.info(f"Capture loop started for camera {self.camera_id}")

        while self._is_running:
            try:
                # Connect to stream if not connected
                if not self._is_connected:
                    self._connect()

                # Capture frame if connected
                if self._is_connected:
                    self._capture_frame()

                # Wait for next capture interval
                time.sleep(self.config.capture_interval)

            except Exception as e:
                logger.error(f"Error in capture loop for camera {self.camera_id}: {e}", exc_info=True)
                self._last_error = str(e)
                self._handle_error()

        logger.info(f"Capture loop ended for camera {self.camera_id}")

    def _connect(self) -> bool:
        """
        Establish connection to RTSP stream

        Returns:
            True if connection successful, False otherwise
        """
        # Check if we should attempt reconnection
        if self._last_connection_attempt:
            time_since_last = (datetime.now() - self._last_connection_attempt).total_seconds()
            if time_since_last < self.config.reconnect_interval:
                return False

        # Check if max reconnect attempts exceeded
        if self._consecutive_failures >= self.config.max_reconnect_attempts:
            if self._consecutive_failures == self.config.max_reconnect_attempts:
                logger.error(
                    f"Camera {self.camera_id} exceeded max reconnection attempts "
                    f"({self.config.max_reconnect_attempts}). Will retry in next cycle."
                )
                self._consecutive_failures += 1  # Increment to avoid repeated logging
            return False

        self._last_connection_attempt = datetime.now()

        try:
            logger.info(f"Connecting to camera {self.camera_id}: {self.config.get_sanitized_url()}")

            # Create VideoCapture object
            self._capture = cv2.VideoCapture(self.config.rtsp_url)

            # Set buffer size to minimize latency
            self._capture.set(cv2.CAP_PROP_BUFFERSIZE, self.config.buffer_size)

            # Set FPS if specified
            if self.config.fps:
                self._capture.set(cv2.CAP_PROP_FPS, self.config.fps)

            # Check if opened successfully
            if not self._capture.isOpened():
                raise ConnectionError(f"Failed to open RTSP stream for camera {self.camera_id}")

            # Try to read one frame to verify connection
            ret, frame = self._capture.read()
            if not ret or frame is None:
                raise ConnectionError(f"Failed to read initial frame from camera {self.camera_id}")

            self._is_connected = True
            self._consecutive_failures = 0
            self._connection_start_time = datetime.now()
            self._last_error = None

            logger.info(f"Successfully connected to camera {self.camera_id}")

            # Store the initial frame
            self._store_frame(frame)

            return True

        except Exception as e:
            logger.error(f"Failed to connect to camera {self.camera_id}: {e}")
            self._last_error = str(e)
            self._consecutive_failures += 1
            self._release_capture()
            return False

    def _capture_frame(self) -> bool:
        """
        Capture a single frame from the stream

        Returns:
            True if frame captured successfully, False otherwise
        """
        if not self._capture or not self._is_connected:
            return False

        try:
            # Read frame
            ret, frame = self._capture.read()

            if not ret or frame is None:
                logger.warning(f"Failed to read frame from camera {self.camera_id}")
                self._handle_error()
                return False

            # Resize if configured
            if self.config.frame_width and self.config.frame_height:
                frame = cv2.resize(frame, (self.config.frame_width, self.config.frame_height))

            # Store frame
            self._store_frame(frame)

            # Reset failure counter on success
            self._consecutive_failures = 0
            self._last_error = None

            return True

        except Exception as e:
            logger.error(f"Error capturing frame from camera {self.camera_id}: {e}")
            self._last_error = str(e)
            self._handle_error()
            return False

    def _store_frame(self, frame: np.ndarray) -> None:
        """
        Store frame in thread-safe manner

        Args:
            frame: Frame to store
        """
        with self._frame_lock:
            self._latest_frame = frame
            self._latest_timestamp = datetime.now()
            self._total_frames_captured += 1

    def _handle_error(self) -> None:
        """Handle capture error by disconnecting and preparing for reconnection"""
        self._consecutive_failures += 1
        self._is_connected = False
        self._release_capture()

    def _release_capture(self) -> None:
        """Release VideoCapture resources"""
        if self._capture:
            try:
                self._capture.release()
            except Exception as e:
                logger.error(f"Error releasing capture for camera {self.camera_id}: {e}")
            finally:
                self._capture = None
                self._is_connected = False

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()

    def __repr__(self) -> str:
        """String representation"""
        status = "connected" if self._is_connected else "disconnected"
        return f"RTSPHandler(camera_id={self.camera_id}, status={status})"
