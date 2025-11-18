"""
Test script for RTSP camera stream handler

This script provides basic tests and validation for the camera system.
Use this to verify your camera connections before deploying to production.
"""

import logging
import time
import cv2
from datetime import datetime

from camera_config import CameraConfig, build_rtsp_url, RTSP_URL_TEMPLATES
from camera_manager import CameraManager
from rtsp_handler import RTSPHandler


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_camera_config():
    """Test camera configuration validation"""
    print("\n" + "="*80)
    print("TEST 1: Camera Configuration Validation")
    print("="*80)

    # Test valid configuration
    try:
        config = CameraConfig(
            camera_id="test_001",
            rtsp_url="rtsp://admin:12345@192.168.1.100:554/stream",
            name="Test Camera",
            zone="Test Zone"
        )
        logger.info("✓ Valid configuration created successfully")
        logger.info(f"  Camera ID: {config.camera_id}")
        logger.info(f"  Name: {config.name}")
        logger.info(f"  Zone: {config.zone}")
        logger.info(f"  Sanitized URL: {config.get_sanitized_url()}")
    except Exception as e:
        logger.error(f"✗ Failed to create valid configuration: {e}")
        return False

    # Test invalid configurations
    invalid_configs = [
        {"camera_id": "", "rtsp_url": "rtsp://test", "name": "Test", "zone": "Zone"},
        {"camera_id": "test", "rtsp_url": "", "name": "Test", "zone": "Zone"},
        {"camera_id": "test", "rtsp_url": "http://invalid", "name": "Test", "zone": "Zone"},
        {"camera_id": "test", "rtsp_url": "rtsp://test", "name": "", "zone": "Zone"},
    ]

    for i, invalid in enumerate(invalid_configs, 1):
        try:
            CameraConfig(**invalid)
            logger.error(f"✗ Invalid config {i} should have failed but didn't")
            return False
        except ValueError:
            logger.info(f"✓ Invalid config {i} correctly rejected")

    # Test configuration serialization
    config_dict = config.to_dict()
    config_restored = CameraConfig.from_dict(config_dict)
    if config_restored.camera_id == config.camera_id:
        logger.info("✓ Configuration serialization works correctly")
    else:
        logger.error("✗ Configuration serialization failed")
        return False

    logger.info("\n✓ All configuration tests passed!\n")
    return True


def test_rtsp_url_builder():
    """Test RTSP URL builder for different camera types"""
    print("\n" + "="*80)
    print("TEST 2: RTSP URL Builder")
    print("="*80)

    test_cases = [
        {
            'type': 'hikvision',
            'expected_pattern': 'rtsp://admin:pass123@192.168.1.100:554/Streaming/Channels/1'
        },
        {
            'type': 'dahua',
            'expected_pattern': 'rtsp://admin:pass123@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0'
        },
        {
            'type': 'axis',
            'expected_pattern': 'rtsp://admin:pass123@192.168.1.100:554/axis-media/media.amp'
        },
        {
            'type': 'onvif',
            'expected_pattern': 'rtsp://admin:pass123@192.168.1.100:554/onvif1'
        },
    ]

    for case in test_cases:
        url = build_rtsp_url(
            camera_type=case['type'],
            ip='192.168.1.100',
            username='admin',
            password='pass123',
            channel=1
        )
        if url == case['expected_pattern']:
            logger.info(f"✓ {case['type']} URL: {url}")
        else:
            logger.error(f"✗ {case['type']} URL mismatch")
            logger.error(f"  Expected: {case['expected_pattern']}")
            logger.error(f"  Got: {url}")
            return False

    # Test available templates
    logger.info(f"\n✓ Available camera types: {list(RTSP_URL_TEMPLATES.keys())}")
    logger.info("✓ All URL builder tests passed!\n")
    return True


def test_single_camera_connection(rtsp_url: str = None):
    """
    Test single camera connection

    Args:
        rtsp_url: RTSP URL to test (optional, uses demo URL if not provided)
    """
    print("\n" + "="*80)
    print("TEST 3: Single Camera Connection")
    print("="*80)

    if rtsp_url is None:
        logger.warning("No RTSP URL provided - using demo URL (will fail)")
        rtsp_url = "rtsp://admin:12345@192.168.1.100:554/stream"

    config = CameraConfig(
        camera_id="test_single_001",
        rtsp_url=rtsp_url,
        name="Test Single Camera",
        zone="Test Zone",
        capture_interval=2.0,
        connection_timeout=5.0,
        max_reconnect_attempts=2
    )

    logger.info(f"Testing camera: {config.get_sanitized_url()}")

    handler = RTSPHandler(config)
    logger.info("✓ RTSPHandler created")

    # Start handler
    success = handler.start()
    logger.info(f"Connection attempt: {'✓ Success' if success else '✗ Failed'}")

    # Wait for frames
    time.sleep(5)

    # Check status
    status = handler.get_status()
    logger.info("\nCamera Status:")
    logger.info(f"  Running: {status['is_running']}")
    logger.info(f"  Connected: {status['is_connected']}")
    logger.info(f"  Healthy: {status['is_healthy']}")
    logger.info(f"  Frames captured: {status['total_frames_captured']}")
    logger.info(f"  Consecutive failures: {status['consecutive_failures']}")

    # Try to get frame
    frame = handler.snapshot()
    if frame is not None:
        logger.info(f"✓ Frame captured: {frame.shape}")
        logger.info(f"  Resolution: {frame.shape[1]}x{frame.shape[0]}")
        logger.info(f"  Channels: {frame.shape[2]}")
    else:
        logger.warning("✗ No frame available")

    # Stop handler
    handler.stop()
    logger.info("✓ Handler stopped\n")

    return success


def test_camera_manager():
    """Test camera manager with multiple mock cameras"""
    print("\n" + "="*80)
    print("TEST 4: Camera Manager")
    print("="*80)

    manager = CameraManager()
    logger.info("✓ CameraManager created")

    # Start manager
    manager.start()
    logger.info("✓ Manager started")

    # Add test cameras
    cameras = [
        {
            'id': 'test_cam_001',
            'name': 'Test Camera 1',
            'zone': 'Zone A',
            'url': 'rtsp://admin:12345@192.168.1.100:554/stream1'
        },
        {
            'id': 'test_cam_002',
            'name': 'Test Camera 2',
            'zone': 'Zone B',
            'url': 'rtsp://admin:12345@192.168.1.101:554/stream1'
        },
    ]

    for cam in cameras:
        config = CameraConfig(
            camera_id=cam['id'],
            rtsp_url=cam['url'],
            name=cam['name'],
            zone=cam['zone'],
            capture_interval=2.0,
            connection_timeout=3.0,
            max_reconnect_attempts=1
        )
        success = manager.add_camera(config)
        logger.info(f"{'✓' if success else '✗'} Added camera: {cam['name']}")

    # Wait for connection attempts
    time.sleep(5)

    # Get all cameras
    all_cameras = manager.get_all_cameras()
    logger.info(f"\n✓ Total cameras: {len(all_cameras)}")

    # Get active cameras
    active_cameras = manager.get_all_active_cameras()
    logger.info(f"  Active cameras: {len(active_cameras)}")

    # Get health summary
    health = manager.get_health_summary()
    logger.info("\nHealth Summary:")
    logger.info(f"  Total: {health['total_cameras']}")
    logger.info(f"  Active: {health['active_cameras']}")
    logger.info(f"  Inactive: {health['inactive_cameras']}")
    logger.info(f"  Health: {health['health_percentage']:.1f}%")

    # Get all statuses
    statuses = manager.get_all_camera_status()
    logger.info("\nCamera Statuses:")
    for camera_id, status in statuses.items():
        logger.info(f"  {status['name']}:")
        logger.info(f"    Connected: {status['is_connected']}")
        logger.info(f"    Healthy: {status['is_healthy']}")
        logger.info(f"    Frames: {status['total_frames_captured']}")

    # Test snapshot_all
    snapshots = manager.snapshot_all()
    logger.info(f"\n✓ Snapshot all: {len(snapshots)} cameras")
    for camera_id, frame in snapshots.items():
        logger.info(f"  {camera_id}: {'Frame available' if frame is not None else 'No frame'}")

    # Remove a camera
    manager.remove_camera('test_cam_001')
    logger.info("✓ Removed camera: test_cam_001")

    remaining = manager.get_all_cameras()
    logger.info(f"  Remaining cameras: {len(remaining)}")

    # Stop manager
    manager.stop()
    logger.info("✓ Manager stopped\n")

    return True


def test_context_managers():
    """Test context manager functionality"""
    print("\n" + "="*80)
    print("TEST 5: Context Managers")
    print("="*80)

    # Test RTSPHandler context manager
    config = CameraConfig(
        camera_id="test_ctx_001",
        rtsp_url="rtsp://admin:12345@192.168.1.100:554/stream",
        name="Test Context Camera",
        zone="Test Zone"
    )

    logger.info("Testing RTSPHandler context manager...")
    with RTSPHandler(config) as handler:
        logger.info("✓ Handler started via context manager")
        time.sleep(2)
    logger.info("✓ Handler automatically stopped")

    # Test CameraManager context manager
    logger.info("\nTesting CameraManager context manager...")
    with CameraManager() as manager:
        logger.info("✓ Manager started via context manager")
        manager.add_camera(config)
        time.sleep(2)
    logger.info("✓ Manager automatically stopped\n")

    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("RTSP Camera Stream Handler - Test Suite")
    print("="*80)

    tests = [
        ("Configuration Validation", test_camera_config),
        ("RTSP URL Builder", test_rtsp_url_builder),
        ("Camera Manager", test_camera_manager),
        ("Context Managers", test_context_managers),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"✗ Test '{test_name}' failed with exception: {e}", exc_info=True)
            results.append((test_name, False))

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        logger.info(f"{status}: {test_name}")

    print("="*80)
    logger.info(f"TOTAL: {passed}/{total} tests passed")
    print("="*80 + "\n")

    return passed == total


if __name__ == "__main__":
    # Run all tests
    success = run_all_tests()

    # Optional: Test with real camera
    # Uncomment and provide your actual RTSP URL to test real camera connection
    """
    print("\n" + "="*80)
    print("BONUS: Real Camera Test")
    print("="*80)
    print("To test with a real camera, uncomment and provide your RTSP URL")

    # Example for Hikvision camera:
    real_rtsp_url = build_rtsp_url(
        camera_type='hikvision',
        ip='YOUR_CAMERA_IP',
        username='YOUR_USERNAME',
        password='YOUR_PASSWORD',
        channel=1
    )

    test_single_camera_connection(real_rtsp_url)
    """

    exit(0 if success else 1)
