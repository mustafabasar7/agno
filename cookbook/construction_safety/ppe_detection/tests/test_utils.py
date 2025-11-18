"""
Test utility functions and helpers.

This module provides helper functions for creating test data,
assertions, and common testing operations.
"""

import numpy as np
import cv2
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import random
import string
from pathlib import Path

from models.ppe_detector import Detection, ComplianceResult
from database.models import Camera, Violation, DetectionLog


# ============================================================================
# Mock Data Generators
# ============================================================================

def generate_random_string(length: int = 10) -> str:
    """Generate random alphanumeric string."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_rtsp_url() -> str:
    """Generate random RTSP URL for testing."""
    ip = f"192.168.1.{random.randint(1, 254)}"
    port = random.choice([554, 8554])
    username = generate_random_string(8)
    password = generate_random_string(12)
    return f"rtsp://{username}:{password}@{ip}:{port}/stream"


def generate_mock_detection(
    class_name: str,
    bbox: Optional[Tuple[int, int, int, int]] = None,
    confidence: Optional[float] = None
) -> Detection:
    """
    Generate mock detection object.

    Args:
        class_name: Class name (person, helmet, vest)
        bbox: Bounding box (x1, y1, x2, y2) or None for random
        confidence: Confidence score or None for random

    Returns:
        Mock Detection object
    """
    if bbox is None:
        x1 = random.randint(0, 500)
        y1 = random.randint(0, 400)
        x2 = x1 + random.randint(50, 200)
        y2 = y1 + random.randint(100, 300)
        bbox = (x1, y1, x2, y2)

    if confidence is None:
        confidence = random.uniform(0.7, 0.99)

    class_ids = {"person": 0, "helmet": 1, "vest": 2}
    class_id = class_ids.get(class_name, 0)

    return Detection(
        bbox=bbox,
        confidence=confidence,
        class_id=class_id,
        class_name=class_name
    )


def generate_compliant_worker_detections() -> List[Detection]:
    """Generate detections for a compliant worker (person + helmet + vest)."""
    person_bbox = (100, 100, 300, 500)
    helmet_bbox = (150, 100, 250, 150)
    vest_bbox = (150, 200, 250, 400)

    return [
        generate_mock_detection("person", person_bbox, 0.95),
        generate_mock_detection("helmet", helmet_bbox, 0.92),
        generate_mock_detection("vest", vest_bbox, 0.88),
    ]


def generate_non_compliant_worker_detections(missing: str = "helmet") -> List[Detection]:
    """
    Generate detections for a non-compliant worker.

    Args:
        missing: Which PPE is missing ("helmet" or "vest")

    Returns:
        List of detections
    """
    person_bbox = (100, 100, 300, 500)
    detections = [generate_mock_detection("person", person_bbox, 0.95)]

    if missing != "helmet":
        helmet_bbox = (150, 100, 250, 150)
        detections.append(generate_mock_detection("helmet", helmet_bbox, 0.92))

    if missing != "vest":
        vest_bbox = (150, 200, 250, 400)
        detections.append(generate_mock_detection("vest", vest_bbox, 0.88))

    return detections


def generate_multiple_worker_detections(count: int = 3, compliance_rate: float = 0.8) -> List[Detection]:
    """
    Generate detections for multiple workers.

    Args:
        count: Number of workers
        compliance_rate: Percentage of workers that are compliant (0.0 to 1.0)

    Returns:
        List of detections
    """
    detections = []
    compliant_count = int(count * compliance_rate)

    for i in range(count):
        x_offset = i * 200
        person_bbox = (50 + x_offset, 100, 180 + x_offset, 500)

        detections.append(generate_mock_detection("person", person_bbox, 0.90 + i * 0.01))

        # Add PPE based on compliance
        if i < compliant_count:
            # Compliant worker
            helmet_bbox = (75 + x_offset, 100, 155 + x_offset, 150)
            vest_bbox = (75 + x_offset, 200, 155 + x_offset, 400)
            detections.append(generate_mock_detection("helmet", helmet_bbox, 0.88 + i * 0.01))
            detections.append(generate_mock_detection("vest", vest_bbox, 0.85 + i * 0.01))
        else:
            # Non-compliant worker (only vest)
            vest_bbox = (75 + x_offset, 200, 155 + x_offset, 400)
            detections.append(generate_mock_detection("vest", vest_bbox, 0.85 + i * 0.01))

    return detections


# ============================================================================
# Image Generators
# ============================================================================

def create_test_image(
    width: int = 640,
    height: int = 480,
    color: Optional[Tuple[int, int, int]] = None
) -> np.ndarray:
    """
    Create a test image with specified dimensions.

    Args:
        width: Image width
        height: Image height
        color: BGR color tuple or None for random

    Returns:
        NumPy array representing image
    """
    if color is None:
        return np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    else:
        img = np.zeros((height, width, 3), dtype=np.uint8)
        img[:] = color
        return img


def create_worker_image(
    has_helmet: bool = True,
    has_vest: bool = True,
    save_path: Optional[Path] = None
) -> np.ndarray:
    """
    Create synthetic image of worker with/without PPE.

    Args:
        has_helmet: Whether worker has helmet
        has_vest: Whether worker has vest
        save_path: Optional path to save image

    Returns:
        Image as NumPy array
    """
    img = np.ones((480, 640, 3), dtype=np.uint8) * 128

    # Draw person (blue rectangle)
    cv2.rectangle(img, (200, 150), (400, 450), (255, 0, 0), -1)

    # Draw helmet if present
    if has_helmet:
        cv2.circle(img, (300, 170), 30, (0, 255, 255), -1)

    # Draw vest if present
    if has_vest:
        cv2.rectangle(img, (250, 220), (350, 380), (0, 165, 255), -1)

    if save_path:
        cv2.imwrite(str(save_path), img)

    return img


def create_multiple_workers_image(
    worker_configs: List[Dict[str, bool]],
    save_path: Optional[Path] = None
) -> np.ndarray:
    """
    Create image with multiple workers.

    Args:
        worker_configs: List of dicts with 'has_helmet' and 'has_vest' keys
        save_path: Optional path to save image

    Returns:
        Image as NumPy array
    """
    img = np.ones((480, 640, 3), dtype=np.uint8) * 128

    width_per_worker = 640 // len(worker_configs)

    for i, config in enumerate(worker_configs):
        x_offset = i * width_per_worker
        center_x = x_offset + width_per_worker // 2

        # Draw person
        person_x1 = x_offset + 20
        person_x2 = x_offset + width_per_worker - 20
        cv2.rectangle(img, (person_x1, 150), (person_x2, 450), (255, 0, 0), -1)

        # Draw helmet if present
        if config.get("has_helmet", False):
            cv2.circle(img, (center_x, 170), 25, (0, 255, 255), -1)

        # Draw vest if present
        if config.get("has_vest", False):
            vest_x1 = person_x1 + 20
            vest_x2 = person_x2 - 20
            cv2.rectangle(img, (vest_x1, 220), (vest_x2, 380), (0, 165, 255), -1)

    if save_path:
        cv2.imwrite(str(save_path), img)

    return img


# ============================================================================
# Assertion Helpers
# ============================================================================

def assert_detection_valid(detection: Detection):
    """Assert that a detection object is valid."""
    assert detection.bbox is not None
    assert len(detection.bbox) == 4
    assert all(isinstance(x, (int, float)) for x in detection.bbox)
    assert 0.0 <= detection.confidence <= 1.0
    assert detection.class_name in ["person", "helmet", "vest", "hardhat", "safety_vest"]


def assert_compliance_result_valid(result: ComplianceResult):
    """Assert that a compliance result is valid."""
    assert result.person_detection is not None
    assert isinstance(result.has_helmet, bool)
    assert isinstance(result.has_vest, bool)
    assert isinstance(result.is_compliant, bool)
    assert 0.0 <= result.confidence_score <= 1.0


def assert_image_valid(image: np.ndarray):
    """Assert that an image is valid."""
    assert image is not None
    assert isinstance(image, np.ndarray)
    assert len(image.shape) in [2, 3]  # Grayscale or color
    if len(image.shape) == 3:
        assert image.shape[2] in [3, 4]  # BGR or BGRA


def assert_bbox_inside_image(bbox: Tuple[int, int, int, int], image_shape: Tuple[int, int]):
    """Assert that bounding box is inside image boundaries."""
    x1, y1, x2, y2 = bbox
    height, width = image_shape[:2]

    assert 0 <= x1 < width, f"x1 ({x1}) out of bounds"
    assert 0 <= x2 <= width, f"x2 ({x2}) out of bounds"
    assert 0 <= y1 < height, f"y1 ({y1}) out of bounds"
    assert 0 <= y2 <= height, f"y2 ({y2}) out of bounds"
    assert x1 < x2, f"x1 ({x1}) >= x2 ({x2})"
    assert y1 < y2, f"y1 ({y1}) >= y2 ({y2})"


# ============================================================================
# Performance Testing Helpers
# ============================================================================

def measure_fps(func, *args, duration_seconds: float = 1.0, **kwargs) -> float:
    """
    Measure FPS of a function.

    Args:
        func: Function to measure
        *args: Function arguments
        duration_seconds: How long to run
        **kwargs: Function keyword arguments

    Returns:
        Frames per second
    """
    import time
    start_time = time.time()
    frame_count = 0

    while time.time() - start_time < duration_seconds:
        func(*args, **kwargs)
        frame_count += 1

    elapsed = time.time() - start_time
    return frame_count / elapsed


def measure_latency(func, *args, iterations: int = 100, **kwargs) -> Dict[str, float]:
    """
    Measure function latency statistics.

    Args:
        func: Function to measure
        *args: Function arguments
        iterations: Number of iterations
        **kwargs: Function keyword arguments

    Returns:
        Dictionary with min, max, mean, median latencies in ms
    """
    import time
    latencies = []

    for _ in range(iterations):
        start_time = time.time()
        func(*args, **kwargs)
        latency_ms = (time.time() - start_time) * 1000
        latencies.append(latency_ms)

    return {
        "min_ms": min(latencies),
        "max_ms": max(latencies),
        "mean_ms": sum(latencies) / len(latencies),
        "median_ms": sorted(latencies)[len(latencies) // 2],
        "p95_ms": sorted(latencies)[int(len(latencies) * 0.95)],
        "p99_ms": sorted(latencies)[int(len(latencies) * 0.99)]
    }


# ============================================================================
# Database Test Helpers
# ============================================================================

def create_test_camera_data(
    name: Optional[str] = None,
    zone_id: int = 1,
    **kwargs
) -> Dict[str, Any]:
    """Create test camera data dictionary."""
    if name is None:
        name = f"Test-Camera-{generate_random_string(6)}"

    data = {
        "name": name,
        "rtsp_url": generate_random_rtsp_url(),
        "location": "Test Location",
        "zone_id": zone_id,
        "status": "active",
        "is_active": True,
        "fps": 15.0,
        "resolution": "1920x1080"
    }
    data.update(kwargs)
    return data


def create_test_violation_data(
    camera_id: int,
    **kwargs
) -> Dict[str, Any]:
    """Create test violation data dictionary."""
    data = {
        "camera_id": camera_id,
        "timestamp": datetime.utcnow(),
        "violation_type": "NO_HELMET",
        "confidence": random.uniform(0.8, 0.99),
        "person_count": 1,
        "severity": "high"
    }
    data.update(kwargs)
    return data


def create_test_detection_log_data(
    camera_id: int,
    **kwargs
) -> Dict[str, Any]:
    """Create test detection log data dictionary."""
    total_persons = random.randint(1, 10)
    compliant_count = random.randint(0, total_persons)

    data = {
        "camera_id": camera_id,
        "timestamp": datetime.utcnow(),
        "total_persons": total_persons,
        "compliant_count": compliant_count,
        "violation_count": total_persons - compliant_count,
        "processing_time_ms": random.uniform(100, 300)
    }
    data.update(kwargs)
    return data


# ============================================================================
# Turkish Construction Site Helpers
# ============================================================================

TURKISH_ZONES = [
    "Şantiye Girişi",
    "Kazı Alanı",
    "Yüksekte Çalışma Alanı",
    "İskele Bölgesi",
    "Malzeme Deposu",
    "Beton Dökümü",
    "Elektrik Tesisat",
    "İnşaat Sahaası"
]

TURKISH_PPE_ITEMS = [
    "baret",
    "yelek",
    "iş ayakkabısı",
    "emniyet kemeri",
    "eldiven",
    "koruyucu gözlük",
    "kulak tıkacı"
]


def get_random_turkish_zone() -> str:
    """Get random Turkish zone name."""
    return random.choice(TURKISH_ZONES)


def get_random_turkish_ppe_set() -> List[str]:
    """Get random set of Turkish PPE items."""
    count = random.randint(2, 4)
    return random.sample(TURKISH_PPE_ITEMS, count)


# ============================================================================
# Video Test Helpers
# ============================================================================

def create_test_video(
    output_path: Path,
    duration_seconds: float = 2.0,
    fps: int = 10,
    resolution: Tuple[int, int] = (640, 480)
) -> Path:
    """
    Create test video file.

    Args:
        output_path: Path to save video
        duration_seconds: Video duration
        fps: Frames per second
        resolution: Video resolution (width, height)

    Returns:
        Path to created video
    """
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, resolution)

    frame_count = int(duration_seconds * fps)

    for i in range(frame_count):
        # Create frame with changing content
        frame = np.random.randint(0, 255, (resolution[1], resolution[0], 3), dtype=np.uint8)

        # Add frame number
        cv2.putText(
            frame,
            f"Frame {i}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        out.write(frame)

    out.release()
    return output_path
