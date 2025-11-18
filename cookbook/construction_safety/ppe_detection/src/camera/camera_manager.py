"""Camera manager for handling multiple RTSP camera streams"""

import logging
import threading
from typing import Dict, List, Optional
from datetime import datetime
import time

import numpy as np

from .camera_config import CameraConfig
from .rtsp_handler import RTSPHandler


logger = logging.getLogger(__name__)


class CameraManager:
    """
    Manages multiple RTSP camera connections

    Features:
    - Add/remove cameras dynamically
    - Health monitoring of all cameras
    - Thread-safe camera access
    - Snapshot capture from multiple cameras
    - Automatic reconnection handling
    """

    def __init__(self):
        """Initialize camera manager"""
        self._cameras: Dict[str, RTSPHandler] = {}
        self._configs: Dict[str, CameraConfig] = {}
        self._lock = threading.RLock()
        self._is_running = False
        self._health_check_thread: Optional[threading.Thread] = None
        self._health_check_interval = 10.0  # seconds

        logger.info("Camera manager initialized")

    def start(self) -> None:
        """Start the camera manager and health monitoring"""
        if self._is_running:
            logger.warning("Camera manager is already running")
            return

        logger.info("Starting camera manager")
        self._is_running = True

        # Start health monitoring thread
        self._health_check_thread = threading.Thread(
            target=self._health_check_loop,
            name="CameraHealthCheck",
            daemon=True
        )
        self._health_check_thread.start()

        logger.info("Camera manager started")

    def stop(self) -> None:
        """Stop the camera manager and all cameras"""
        logger.info("Stopping camera manager")
        self._is_running = False

        # Stop health check thread
        if self._health_check_thread and self._health_check_thread.is_alive():
            self._health_check_thread.join(timeout=5.0)

        # Stop all cameras
        with self._lock:
            camera_ids = list(self._cameras.keys())

        for camera_id in camera_ids:
            self.remove_camera(camera_id)

        logger.info("Camera manager stopped")

    def add_camera(self, config: CameraConfig) -> bool:
        """
        Add a new camera

        Args:
            config: Camera configuration

        Returns:
            True if camera added successfully, False otherwise
        """
        camera_id = config.camera_id

        with self._lock:
            # Check if camera already exists
            if camera_id in self._cameras:
                logger.warning(f"Camera {camera_id} already exists. Remove it first to update.")
                return False

            try:
                # Create RTSP handler
                handler = RTSPHandler(config)

                # Start the handler if enabled
                if config.enabled:
                    success = handler.start()
                    if not success:
                        logger.warning(
                            f"Camera {camera_id} added but failed to connect. "
                            "Will retry automatically."
                        )

                # Store camera and config
                self._cameras[camera_id] = handler
                self._configs[camera_id] = config

                logger.info(f"Camera {camera_id} added successfully")
                return True

            except Exception as e:
                logger.error(f"Failed to add camera {camera_id}: {e}", exc_info=True)
                return False

    def remove_camera(self, camera_id: str) -> bool:
        """
        Remove a camera

        Args:
            camera_id: ID of camera to remove

        Returns:
            True if camera removed successfully, False otherwise
        """
        with self._lock:
            if camera_id not in self._cameras:
                logger.warning(f"Camera {camera_id} not found")
                return False

            try:
                # Stop and remove handler
                handler = self._cameras[camera_id]
                handler.stop()

                del self._cameras[camera_id]
                del self._configs[camera_id]

                logger.info(f"Camera {camera_id} removed successfully")
                return True

            except Exception as e:
                logger.error(f"Failed to remove camera {camera_id}: {e}", exc_info=True)
                return False

    def snapshot(self, camera_id: str) -> Optional[np.ndarray]:
        """
        Get latest frame from a specific camera

        Args:
            camera_id: ID of camera

        Returns:
            Frame as numpy array or None if not available
        """
        with self._lock:
            if camera_id not in self._cameras:
                logger.warning(f"Camera {camera_id} not found")
                return None

            handler = self._cameras[camera_id]
            return handler.snapshot()

    def snapshot_all(self) -> Dict[str, Optional[np.ndarray]]:
        """
        Get latest frames from all cameras

        Returns:
            Dictionary mapping camera_id to frame (or None if not available)
        """
        with self._lock:
            camera_ids = list(self._cameras.keys())

        snapshots = {}
        for camera_id in camera_ids:
            snapshots[camera_id] = self.snapshot(camera_id)

        return snapshots

    def get_all_active_cameras(self) -> List[str]:
        """
        Get list of all active (connected) cameras

        Returns:
            List of camera IDs that are currently connected
        """
        with self._lock:
            return [
                camera_id
                for camera_id, handler in self._cameras.items()
                if handler.is_healthy()
            ]

    def get_all_cameras(self) -> List[str]:
        """
        Get list of all cameras (active and inactive)

        Returns:
            List of all camera IDs
        """
        with self._lock:
            return list(self._cameras.keys())

    def get_camera_status(self, camera_id: str) -> Optional[dict]:
        """
        Get status information for a specific camera

        Args:
            camera_id: ID of camera

        Returns:
            Status dictionary or None if camera not found
        """
        with self._lock:
            if camera_id not in self._cameras:
                return None

            handler = self._cameras[camera_id]
            return handler.get_status()

    def get_all_camera_status(self) -> Dict[str, dict]:
        """
        Get status information for all cameras

        Returns:
            Dictionary mapping camera_id to status dictionary
        """
        with self._lock:
            camera_ids = list(self._cameras.keys())

        statuses = {}
        for camera_id in camera_ids:
            status = self.get_camera_status(camera_id)
            if status:
                statuses[camera_id] = status

        return statuses

    def get_camera_config(self, camera_id: str) -> Optional[CameraConfig]:
        """
        Get configuration for a specific camera

        Args:
            camera_id: ID of camera

        Returns:
            Camera configuration or None if not found
        """
        with self._lock:
            return self._configs.get(camera_id)

    def update_camera_config(self, camera_id: str, config: CameraConfig) -> bool:
        """
        Update camera configuration

        Note: This will restart the camera with new configuration

        Args:
            camera_id: ID of camera to update
            config: New configuration

        Returns:
            True if updated successfully, False otherwise
        """
        if config.camera_id != camera_id:
            logger.error("Config camera_id must match the camera_id parameter")
            return False

        # Remove old camera
        if not self.remove_camera(camera_id):
            logger.error(f"Failed to remove camera {camera_id} for update")
            return False

        # Add with new config
        if not self.add_camera(config):
            logger.error(f"Failed to add camera {camera_id} with new config")
            return False

        logger.info(f"Camera {camera_id} configuration updated successfully")
        return True

    def enable_camera(self, camera_id: str) -> bool:
        """
        Enable a camera (start capturing)

        Args:
            camera_id: ID of camera to enable

        Returns:
            True if enabled successfully, False otherwise
        """
        with self._lock:
            if camera_id not in self._cameras:
                logger.warning(f"Camera {camera_id} not found")
                return False

            handler = self._cameras[camera_id]
            config = self._configs[camera_id]

            if config.enabled:
                logger.info(f"Camera {camera_id} is already enabled")
                return True

            config.enabled = True
            return handler.start()

    def disable_camera(self, camera_id: str) -> bool:
        """
        Disable a camera (stop capturing)

        Args:
            camera_id: ID of camera to disable

        Returns:
            True if disabled successfully, False otherwise
        """
        with self._lock:
            if camera_id not in self._cameras:
                logger.warning(f"Camera {camera_id} not found")
                return False

            handler = self._cameras[camera_id]
            config = self._configs[camera_id]

            if not config.enabled:
                logger.info(f"Camera {camera_id} is already disabled")
                return True

            config.enabled = False
            handler.stop()
            return True

    def get_health_summary(self) -> dict:
        """
        Get overall health summary of all cameras

        Returns:
            Dictionary with health statistics
        """
        with self._lock:
            total = len(self._cameras)
            active = len([h for h in self._cameras.values() if h.is_healthy()])
            inactive = total - active

            # Get per-zone statistics
            zone_stats = {}
            for camera_id, handler in self._cameras.items():
                config = self._configs[camera_id]
                zone = config.zone

                if zone not in zone_stats:
                    zone_stats[zone] = {'total': 0, 'active': 0, 'inactive': 0}

                zone_stats[zone]['total'] += 1
                if handler.is_healthy():
                    zone_stats[zone]['active'] += 1
                else:
                    zone_stats[zone]['inactive'] += 1

        return {
            'total_cameras': total,
            'active_cameras': active,
            'inactive_cameras': inactive,
            'health_percentage': (active / total * 100) if total > 0 else 0,
            'zone_statistics': zone_stats,
            'timestamp': datetime.now().isoformat()
        }

    def _health_check_loop(self) -> None:
        """Health monitoring loop (runs in separate thread)"""
        logger.info("Health check loop started")

        while self._is_running:
            try:
                # Get health summary
                summary = self.get_health_summary()

                # Log health status
                logger.info(
                    f"Camera health: {summary['active_cameras']}/{summary['total_cameras']} active "
                    f"({summary['health_percentage']:.1f}%)"
                )

                # Log unhealthy cameras
                with self._lock:
                    for camera_id, handler in self._cameras.items():
                        if not handler.is_healthy():
                            config = self._configs[camera_id]
                            if config.enabled:
                                logger.warning(
                                    f"Camera {camera_id} ({config.name}) is unhealthy - "
                                    f"attempting reconnection"
                                )

                # Wait for next check
                time.sleep(self._health_check_interval)

            except Exception as e:
                logger.error(f"Error in health check loop: {e}", exc_info=True)
                time.sleep(self._health_check_interval)

        logger.info("Health check loop ended")

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()

    def __repr__(self) -> str:
        """String representation"""
        summary = self.get_health_summary()
        return (
            f"CameraManager(total={summary['total_cameras']}, "
            f"active={summary['active_cameras']}, "
            f"health={summary['health_percentage']:.1f}%)"
        )
