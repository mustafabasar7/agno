"""
Production example for RTSP camera system integration with PPE detection

This example demonstrates a production-ready setup for Turkish construction sites
with multiple cameras, health monitoring, and integration points for PPE detection.
"""

import logging
import time
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from camera_manager import CameraManager
from config_loader import get_config_from_file


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ppe_detection/camera.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PPEDetectionCameraSystem:
    """
    Production-ready camera system for PPE detection in Turkish construction sites

    Features:
    - Automatic configuration loading
    - Health monitoring and reporting
    - Snapshot saving
    - Graceful shutdown
    - Integration hooks for PPE detection
    """

    def __init__(
        self,
        config_file: Optional[str] = None,
        snapshot_dir: str = '/var/ppe_detection/snapshots'
    ):
        """
        Initialize PPE detection camera system

        Args:
            config_file: Path to camera configuration file (optional)
            snapshot_dir: Directory to save snapshots
        """
        self.config_file = config_file
        self.snapshot_dir = Path(snapshot_dir)
        self.manager: Optional[CameraManager] = None
        self.running = False

        # Create snapshot directory
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("PPE Detection Camera System initialized")

    def start(self) -> bool:
        """
        Start the camera system

        Returns:
            True if started successfully, False otherwise
        """
        try:
            logger.info("Starting PPE Detection Camera System...")

            # Load camera configurations
            logger.info("Loading camera configurations...")
            configs = get_config_from_file(self.config_file)

            if not configs:
                logger.error("No camera configurations loaded!")
                return False

            logger.info(f"Loaded {len(configs)} camera configurations")

            # Create and start camera manager
            self.manager = CameraManager()
            self.manager.start()

            # Add all cameras
            for config in configs:
                success = self.manager.add_camera(config)
                if success:
                    logger.info(
                        f"Added camera: {config.name} ({config.zone}) - "
                        f"Enabled: {config.enabled}"
                    )
                else:
                    logger.error(f"Failed to add camera: {config.name}")

            # Wait for cameras to connect
            logger.info("Waiting for cameras to connect...")
            time.sleep(10)

            # Log initial health status
            health = self.manager.get_health_summary()
            logger.info(
                f"Camera system started: {health['active_cameras']}/{health['total_cameras']} "
                f"cameras active ({health['health_percentage']:.1f}%)"
            )

            self.running = True
            return True

        except Exception as e:
            logger.error(f"Failed to start camera system: {e}", exc_info=True)
            return False

    def stop(self) -> None:
        """Stop the camera system"""
        logger.info("Stopping PPE Detection Camera System...")

        self.running = False

        if self.manager:
            self.manager.stop()

        logger.info("Camera system stopped")

    def run(self, interval: float = 30.0) -> None:
        """
        Run the camera system main loop

        Args:
            interval: Interval between health checks (seconds)
        """
        if not self.running:
            logger.error("Camera system not started. Call start() first.")
            return

        logger.info(f"Camera system running. Health check interval: {interval}s")

        try:
            while self.running:
                # Perform health check
                self._health_check()

                # Capture snapshots (for demonstration)
                # In production, this would trigger PPE detection
                self._capture_snapshots()

                # Wait for next interval
                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
        finally:
            self.stop()

    def _health_check(self) -> None:
        """Perform health check on all cameras"""
        if not self.manager:
            return

        try:
            health = self.manager.get_health_summary()

            logger.info("="*80)
            logger.info("CAMERA HEALTH CHECK")
            logger.info("="*80)
            logger.info(f"Timestamp: {health['timestamp']}")
            logger.info(f"Total cameras: {health['total_cameras']}")
            logger.info(f"Active cameras: {health['active_cameras']}")
            logger.info(f"Inactive cameras: {health['inactive_cameras']}")
            logger.info(f"Health percentage: {health['health_percentage']:.1f}%")

            # Zone statistics
            logger.info("\nZone Statistics:")
            for zone, stats in health['zone_statistics'].items():
                logger.info(
                    f"  {zone}: {stats['active']}/{stats['total']} active "
                    f"({stats['active']/stats['total']*100:.0f}%)"
                )

            # Log unhealthy cameras
            statuses = self.manager.get_all_camera_status()
            unhealthy = [
                (cam_id, status)
                for cam_id, status in statuses.items()
                if not status['is_healthy']
            ]

            if unhealthy:
                logger.warning(f"\nUnhealthy Cameras ({len(unhealthy)}):")
                for cam_id, status in unhealthy:
                    logger.warning(
                        f"  {status['name']} ({cam_id}): "
                        f"Connected: {status['is_connected']}, "
                        f"Failures: {status['consecutive_failures']}, "
                        f"Error: {status['last_error']}"
                    )

            logger.info("="*80 + "\n")

        except Exception as e:
            logger.error(f"Error in health check: {e}", exc_info=True)

    def _capture_snapshots(self) -> None:
        """Capture snapshots from all active cameras"""
        if not self.manager:
            return

        try:
            # Get active cameras
            active_cameras = self.manager.get_all_active_cameras()

            if not active_cameras:
                logger.warning("No active cameras to capture snapshots")
                return

            logger.info(f"Capturing snapshots from {len(active_cameras)} active cameras...")

            # Create timestamp for this batch
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Capture snapshots
            snapshots = self.manager.snapshot_all()

            for camera_id, frame in snapshots.items():
                if frame is None:
                    continue

                # Get camera config for metadata
                config = self.manager.get_camera_config(camera_id)
                if not config:
                    continue

                # Save snapshot
                filename = f"{camera_id}_{timestamp}.jpg"
                filepath = self.snapshot_dir / filename

                # Add metadata overlay (optional)
                frame_with_overlay = self._add_metadata_overlay(
                    frame,
                    config.name,
                    config.zone,
                    timestamp
                )

                cv2.imwrite(str(filepath), frame_with_overlay)
                logger.info(f"Saved snapshot: {filename}")

                # TODO: Here you would call PPE detection on the frame
                # violations = detect_ppe_violations(frame, zone=config.zone)
                # if violations:
                #     handle_violations(violations, config)

        except Exception as e:
            logger.error(f"Error capturing snapshots: {e}", exc_info=True)

    def _add_metadata_overlay(
        self,
        frame: np.ndarray,
        camera_name: str,
        zone: str,
        timestamp: str
    ) -> np.ndarray:
        """
        Add metadata overlay to frame

        Args:
            frame: Input frame
            camera_name: Camera name
            zone: Zone name
            timestamp: Timestamp string

        Returns:
            Frame with overlay
        """
        frame_copy = frame.copy()

        # Add semi-transparent black background
        overlay = frame_copy.copy()
        cv2.rectangle(overlay, (10, 10), (500, 100), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame_copy, 0.4, 0, frame_copy)

        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(
            frame_copy,
            camera_name,
            (20, 35),
            font,
            0.7,
            (255, 255, 255),
            2
        )
        cv2.putText(
            frame_copy,
            f"Bolge: {zone}",
            (20, 60),
            font,
            0.6,
            (255, 255, 255),
            2
        )
        cv2.putText(
            frame_copy,
            timestamp,
            (20, 85),
            font,
            0.5,
            (255, 255, 255),
            1
        )

        return frame_copy

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}")
        self.running = False

    def get_camera_snapshot(self, camera_id: str) -> Optional[np.ndarray]:
        """
        Get snapshot from specific camera (API endpoint)

        Args:
            camera_id: Camera ID

        Returns:
            Frame or None
        """
        if not self.manager:
            return None
        return self.manager.snapshot(camera_id)

    def get_zone_snapshots(self, zone: str) -> dict:
        """
        Get snapshots from all cameras in a specific zone

        Args:
            zone: Zone name

        Returns:
            Dictionary mapping camera_id to frame
        """
        if not self.manager:
            return {}

        snapshots = {}
        for camera_id in self.manager.get_all_cameras():
            config = self.manager.get_camera_config(camera_id)
            if config and config.zone == zone:
                frame = self.manager.snapshot(camera_id)
                if frame is not None:
                    snapshots[camera_id] = frame

        return snapshots

    def get_system_status(self) -> dict:
        """
        Get overall system status (API endpoint)

        Returns:
            Status dictionary
        """
        if not self.manager:
            return {'status': 'stopped'}

        health = self.manager.get_health_summary()
        statuses = self.manager.get_all_camera_status()

        return {
            'status': 'running' if self.running else 'stopped',
            'health': health,
            'cameras': statuses,
            'snapshot_directory': str(self.snapshot_dir)
        }


def main():
    """Main entry point for production deployment"""
    logger.info("="*80)
    logger.info("PPE Detection Camera System - Production Deployment")
    logger.info("İnşaat Şantiyesi Güvenlik Kamera Sistemi")
    logger.info("="*80)

    # Create camera system
    system = PPEDetectionCameraSystem(
        config_file='camera_config.yaml',  # Will auto-discover if not found
        snapshot_dir='/var/ppe_detection/snapshots'
    )

    # Start system
    if not system.start():
        logger.error("Failed to start camera system")
        sys.exit(1)

    # Run main loop
    try:
        logger.info("Camera system running. Press Ctrl+C to stop.")
        system.run(interval=30.0)  # Health check every 30 seconds
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
    finally:
        system.stop()

    logger.info("Camera system shutdown complete")


# Example API integration (Flask/FastAPI)
def example_api_integration():
    """
    Example showing how to integrate with Flask/FastAPI

    This is pseudocode showing the integration pattern
    """
    # Initialize once at startup
    camera_system = PPEDetectionCameraSystem()
    camera_system.start()

    # Flask example
    """
    from flask import Flask, jsonify, send_file
    app = Flask(__name__)

    @app.route('/api/cameras/status')
    def get_status():
        return jsonify(camera_system.get_system_status())

    @app.route('/api/cameras/<camera_id>/snapshot')
    def get_snapshot(camera_id):
        frame = camera_system.get_camera_snapshot(camera_id)
        if frame is None:
            return jsonify({'error': 'Camera not found or inactive'}), 404

        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        return send_file(
            io.BytesIO(buffer),
            mimetype='image/jpeg'
        )

    @app.route('/api/zones/<zone>/snapshots')
    def get_zone_snapshots(zone):
        snapshots = camera_system.get_zone_snapshots(zone)
        return jsonify({
            'zone': zone,
            'camera_count': len(snapshots),
            'cameras': list(snapshots.keys())
        })
    """

    # FastAPI example
    """
    from fastapi import FastAPI
    from fastapi.responses import StreamingResponse

    app = FastAPI()

    @app.get("/api/cameras/status")
    async def get_status():
        return camera_system.get_system_status()

    @app.get("/api/cameras/{camera_id}/snapshot")
    async def get_snapshot(camera_id: str):
        frame = camera_system.get_camera_snapshot(camera_id)
        if frame is None:
            return {"error": "Camera not found"}

        _, buffer = cv2.imencode('.jpg', frame)
        return StreamingResponse(
            io.BytesIO(buffer),
            media_type="image/jpeg"
        )
    """


if __name__ == "__main__":
    main()
