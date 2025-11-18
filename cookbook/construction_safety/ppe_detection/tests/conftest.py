"""
Pytest configuration and fixtures for PPE Detection tests.

This module provides shared fixtures, test configuration, and utilities
for unit and integration tests.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Generator, Dict, Any
import tempfile
import shutil

import pytest
import numpy as np
import cv2
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database.models import Base, Camera, Violation, DetectionLog, Zone, Alert, CameraStatus
from database.database import get_db
from models.model_config import ModelConfig
from camera.camera_config import CameraConfig
from alerts.alert_config import AlertConfig


# ============================================================================
# Test Configuration
# ============================================================================

@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Get test data directory."""
    data_dir = Path(__file__).parent / "fixtures" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture(scope="session")
def test_images_dir(test_data_dir) -> Path:
    """Get test images directory."""
    images_dir = test_data_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    return images_dir


@pytest.fixture(scope="session")
def test_output_dir() -> Generator[Path, None, None]:
    """Create and cleanup temporary output directory."""
    temp_dir = Path(tempfile.mkdtemp(prefix="ppe_test_"))
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """
    Create in-memory SQLite database for testing.

    Each test gets a fresh database that is cleaned up after the test.
    """
    # Create in-memory SQLite database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_camera(test_db: Session) -> Camera:
    """Create a sample camera for testing."""
    camera = Camera(
        name="Test Camera 1",
        rtsp_url="rtsp://test:test@192.168.1.100:554/stream",
        location="Test Location",
        zone_id=1,
        status=CameraStatus.ACTIVE,
        is_active=True,
        fps=15.0,
        resolution="1920x1080"
    )
    test_db.add(camera)
    test_db.commit()
    test_db.refresh(camera)
    return camera


@pytest.fixture
def sample_zone(test_db: Session) -> Zone:
    """Create a sample zone for testing."""
    zone = Zone(
        name="Test Zone A",
        description="Test construction zone",
        required_ppe=["helmet", "vest"]
    )
    test_db.add(zone)
    test_db.commit()
    test_db.refresh(zone)
    return zone


# ============================================================================
# Image Fixtures
# ============================================================================

@pytest.fixture
def sample_image() -> np.ndarray:
    """Create a sample test image (640x480 RGB)."""
    return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)


@pytest.fixture
def compliant_worker_image(test_images_dir) -> np.ndarray:
    """
    Create synthetic image with compliant worker (helmet + vest).

    Note: In production, this would be a real annotated image.
    """
    img = np.ones((480, 640, 3), dtype=np.uint8) * 128

    # Draw person (blue rectangle)
    cv2.rectangle(img, (200, 150), (400, 450), (255, 0, 0), -1)

    # Draw helmet (yellow circle on top)
    cv2.circle(img, (300, 170), 30, (0, 255, 255), -1)

    # Draw vest (orange rectangle on torso)
    cv2.rectangle(img, (250, 220), (350, 380), (0, 165, 255), -1)

    # Save to file
    image_path = test_images_dir / "compliant_worker.jpg"
    cv2.imwrite(str(image_path), img)

    return img


@pytest.fixture
def non_compliant_worker_image(test_images_dir) -> np.ndarray:
    """
    Create synthetic image with non-compliant worker (no helmet).
    """
    img = np.ones((480, 640, 3), dtype=np.uint8) * 128

    # Draw person (blue rectangle)
    cv2.rectangle(img, (200, 150), (400, 450), (255, 0, 0), -1)

    # Draw vest only (orange rectangle on torso)
    cv2.rectangle(img, (250, 220), (350, 380), (0, 165, 255), -1)

    # Save to file
    image_path = test_images_dir / "non_compliant_worker.jpg"
    cv2.imwrite(str(image_path), img)

    return img


@pytest.fixture
def partial_ppe_image(test_images_dir) -> np.ndarray:
    """
    Create synthetic image with partial PPE (helmet but no vest).
    """
    img = np.ones((480, 640, 3), dtype=np.uint8) * 128

    # Draw person (blue rectangle)
    cv2.rectangle(img, (200, 150), (400, 450), (255, 0, 0), -1)

    # Draw helmet only (yellow circle on top)
    cv2.circle(img, (300, 170), 30, (0, 255, 255), -1)

    # Save to file
    image_path = test_images_dir / "partial_ppe_worker.jpg"
    cv2.imwrite(str(image_path), img)

    return img


@pytest.fixture
def multiple_workers_image(test_images_dir) -> np.ndarray:
    """
    Create synthetic image with multiple workers.
    """
    img = np.ones((480, 640, 3), dtype=np.uint8) * 128

    # Worker 1 - Compliant (left)
    cv2.rectangle(img, (50, 150), (200, 450), (255, 0, 0), -1)
    cv2.circle(img, (125, 170), 25, (0, 255, 255), -1)  # helmet
    cv2.rectangle(img, (100, 220), (150, 350), (0, 165, 255), -1)  # vest

    # Worker 2 - Non-compliant (center)
    cv2.rectangle(img, (250, 150), (390, 450), (255, 0, 0), -1)
    cv2.rectangle(img, (300, 220), (340, 350), (0, 165, 255), -1)  # vest only

    # Worker 3 - Compliant (right)
    cv2.rectangle(img, (440, 150), (590, 450), (255, 0, 0), -1)
    cv2.circle(img, (515, 170), 25, (0, 255, 255), -1)  # helmet
    cv2.rectangle(img, (490, 220), (540, 350), (0, 165, 255), -1)  # vest

    # Save to file
    image_path = test_images_dir / "multiple_workers.jpg"
    cv2.imwrite(str(image_path), img)

    return img


@pytest.fixture
def occlusion_image(test_images_dir) -> np.ndarray:
    """
    Create synthetic image with occlusion (partially hidden worker).
    """
    img = np.ones((480, 640, 3), dtype=np.uint8) * 128

    # Draw person (blue rectangle)
    cv2.rectangle(img, (200, 150), (400, 450), (255, 0, 0), -1)

    # Draw helmet (yellow circle on top)
    cv2.circle(img, (300, 170), 30, (0, 255, 255), -1)

    # Draw vest (orange rectangle on torso)
    cv2.rectangle(img, (250, 220), (350, 380), (0, 165, 255), -1)

    # Draw occlusion (gray rectangle covering part of person)
    cv2.rectangle(img, (320, 200), (500, 450), (100, 100, 100), -1)

    # Save to file
    image_path = test_images_dir / "occlusion_worker.jpg"
    cv2.imwrite(str(image_path), img)

    return img


# ============================================================================
# Model Configuration Fixtures
# ============================================================================

@pytest.fixture
def model_config() -> ModelConfig:
    """Create test model configuration."""
    from models.model_config import ModelConfig

    config = ModelConfig(
        model_architecture="yolov8n",
        confidence_threshold=0.5,
        nms_threshold=0.45,
        device="cpu",
        class_names={
            0: "person",
            1: "helmet",
            2: "vest"
        }
    )
    return config


@pytest.fixture
def camera_config() -> CameraConfig:
    """Create test camera configuration."""
    return CameraConfig(
        camera_id="test-cam-01",
        name="Test Camera",
        rtsp_url="rtsp://test:test@192.168.1.100:554/stream",
        username="test",
        password="test",
        zone="Test Zone",
        location="Test Location",
        enabled=True,
        fps=15,
        reconnect_interval=5
    )


@pytest.fixture
def alert_config() -> AlertConfig:
    """Create test alert configuration."""
    from alerts.alert_config import AlertConfig, ThrottleConfig, EscalationConfig

    return AlertConfig(
        enabled=True,
        throttle=ThrottleConfig(
            deduplication_window_minutes=5,
            same_zone_throttle_minutes=2,
            max_alerts_per_hour=100,
            max_alerts_per_day=1000
        ),
        escalation=EscalationConfig(
            enabled=False,
            escalation_delay_minutes=15,
            max_escalation_level=3
        ),
        critical_zones=["Yüksekte Çalışma", "Kazı Alanı"]
    )


# ============================================================================
# Mock Data Fixtures
# ============================================================================

@pytest.fixture
def mock_detection_data() -> Dict[str, Any]:
    """Mock detection data for testing."""
    return {
        "total_persons": 3,
        "compliant_count": 2,
        "violation_count": 1,
        "detections": [
            {
                "class_name": "person",
                "bbox": [100, 100, 200, 300],
                "confidence": 0.95
            },
            {
                "class_name": "helmet",
                "bbox": [110, 100, 150, 130],
                "confidence": 0.92
            },
            {
                "class_name": "vest",
                "bbox": [110, 150, 190, 250],
                "confidence": 0.88
            }
        ]
    }


@pytest.fixture
def mock_violation_data() -> Dict[str, Any]:
    """Mock violation data for testing."""
    return {
        "camera_id": 1,
        "timestamp": datetime.utcnow(),
        "violation_type": "NO_HELMET",
        "image_path": "/data/violations/test.jpg",
        "confidence": 0.95,
        "person_count": 1,
        "severity": "high"
    }


# ============================================================================
# Video Fixtures
# ============================================================================

@pytest.fixture
def sample_video(test_output_dir) -> Path:
    """Create a sample test video file."""
    video_path = test_output_dir / "test_video.mp4"

    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(video_path), fourcc, 10.0, (640, 480))

    # Write 30 frames
    for i in range(30):
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        out.write(frame)

    out.release()
    return video_path


# ============================================================================
# RTSP Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_rtsp_stream():
    """Mock RTSP stream for testing camera handlers."""
    class MockRTSPStream:
        def __init__(self):
            self.is_opened = True
            self.frame_count = 0

        def isOpened(self):
            return self.is_opened

        def read(self):
            if not self.is_opened:
                return False, None

            self.frame_count += 1
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            return True, frame

        def release(self):
            self.is_opened = False

        def get(self, prop):
            if prop == cv2.CAP_PROP_FPS:
                return 15.0
            elif prop == cv2.CAP_PROP_FRAME_WIDTH:
                return 640
            elif prop == cv2.CAP_PROP_FRAME_HEIGHT:
                return 480
            return 0

    return MockRTSPStream()


# ============================================================================
# Performance Testing Fixtures
# ============================================================================

@pytest.fixture
def performance_tracker():
    """Track performance metrics during tests."""
    class PerformanceTracker:
        def __init__(self):
            self.metrics = []

        def record(self, operation: str, duration_ms: float):
            self.metrics.append({
                "operation": operation,
                "duration_ms": duration_ms,
                "timestamp": datetime.now()
            })

        def get_average(self, operation: str) -> float:
            op_metrics = [m["duration_ms"] for m in self.metrics if m["operation"] == operation]
            return sum(op_metrics) / len(op_metrics) if op_metrics else 0

        def get_stats(self):
            return self.metrics

    return PerformanceTracker()


# ============================================================================
# Pytest Markers and Hooks
# ============================================================================

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "model: Tests requiring ML model")
    config.addinivalue_line("markers", "camera: Tests requiring camera/RTSP")
    config.addinivalue_line("markers", "database: Tests requiring database")
    config.addinivalue_line("markers", "turkish: Tests for Turkish construction scenarios")


# ============================================================================
# Test Utilities
# ============================================================================

@pytest.fixture
def assert_image_similarity():
    """Helper to assert two images are similar."""
    def _assert_similarity(img1: np.ndarray, img2: np.ndarray, threshold: float = 0.95):
        """Assert two images are similar based on structural similarity."""
        from skimage.metrics import structural_similarity as ssim

        # Convert to grayscale if needed
        if len(img1.shape) == 3:
            img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        else:
            img1_gray = img1

        if len(img2.shape) == 3:
            img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        else:
            img2_gray = img2

        # Resize to same dimensions if needed
        if img1_gray.shape != img2_gray.shape:
            img2_gray = cv2.resize(img2_gray, (img1_gray.shape[1], img1_gray.shape[0]))

        similarity = ssim(img1_gray, img2_gray)
        assert similarity >= threshold, f"Image similarity {similarity} below threshold {threshold}"

    return _assert_similarity
