"""API module for PPE detection service"""

from .main import app
from .endpoints import router
from .schemas import (
    CameraConfig,
    CameraConfigCreate,
    CameraConfigUpdate,
    DetectionResult,
    ViolationRecord,
    StatsResponse,
    HealthStatus,
)

__all__ = [
    "app",
    "router",
    "CameraConfig",
    "CameraConfigCreate",
    "CameraConfigUpdate",
    "DetectionResult",
    "ViolationRecord",
    "StatsResponse",
    "HealthStatus",
]
