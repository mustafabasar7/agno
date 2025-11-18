"""Camera and video processing module"""

from .camera_config import (
    CameraConfig,
    create_camera_config_from_url,
    build_rtsp_url,
    RTSP_URL_TEMPLATES
)
from .rtsp_handler import RTSPHandler
from .camera_manager import CameraManager

__all__ = [
    'CameraConfig',
    'create_camera_config_from_url',
    'build_rtsp_url',
    'RTSP_URL_TEMPLATES',
    'RTSPHandler',
    'CameraManager',
]
