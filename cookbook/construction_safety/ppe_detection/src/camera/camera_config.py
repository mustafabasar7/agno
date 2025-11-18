"""Camera configuration schema and validation for RTSP streams"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
import re


@dataclass
class CameraConfig:
    """Configuration for a single camera stream"""

    camera_id: str
    rtsp_url: str
    name: str
    zone: str

    # Capture settings
    capture_interval: float = 5.0  # seconds between frame captures
    reconnect_interval: float = 5.0  # seconds between reconnection attempts
    max_reconnect_attempts: int = 3  # max consecutive reconnection attempts before marking failed

    # Stream settings
    frame_width: Optional[int] = None  # resize width (None = original)
    frame_height: Optional[int] = None  # resize height (None = original)
    fps: int = 30  # target FPS for stream reading

    # Timeout settings
    connection_timeout: float = 10.0  # seconds to wait for initial connection
    read_timeout: float = 5.0  # seconds to wait for frame read

    # Buffer settings
    buffer_size: int = 1  # number of frames to buffer (1 = only latest)

    # Metadata
    location: Optional[str] = None
    description: Optional[str] = None
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration after initialization"""
        self.validate()

    def validate(self) -> None:
        """Validate camera configuration"""
        # Validate camera_id
        if not self.camera_id or not isinstance(self.camera_id, str):
            raise ValueError("camera_id must be a non-empty string")

        # Validate RTSP URL
        if not self.rtsp_url or not isinstance(self.rtsp_url, str):
            raise ValueError("rtsp_url must be a non-empty string")

        if not self._is_valid_rtsp_url(self.rtsp_url):
            raise ValueError(f"Invalid RTSP URL format: {self.rtsp_url}")

        # Validate name and zone
        if not self.name or not isinstance(self.name, str):
            raise ValueError("name must be a non-empty string")

        if not self.zone or not isinstance(self.zone, str):
            raise ValueError("zone must be a non-empty string")

        # Validate intervals
        if self.capture_interval <= 0:
            raise ValueError("capture_interval must be positive")

        if self.reconnect_interval <= 0:
            raise ValueError("reconnect_interval must be positive")

        if self.max_reconnect_attempts < 0:
            raise ValueError("max_reconnect_attempts must be non-negative")

        # Validate timeouts
        if self.connection_timeout <= 0:
            raise ValueError("connection_timeout must be positive")

        if self.read_timeout <= 0:
            raise ValueError("read_timeout must be positive")

        # Validate buffer size
        if self.buffer_size < 1:
            raise ValueError("buffer_size must be at least 1")

    @staticmethod
    def _is_valid_rtsp_url(url: str) -> bool:
        """Check if URL is a valid RTSP URL format"""
        # Basic RTSP URL pattern
        rtsp_pattern = r'^rtsp://[\w\-\.]+(?::\d+)?(?:/.*)?$'
        # RTSP with credentials pattern
        rtsp_auth_pattern = r'^rtsp://[\w\-\.]+:[\w\-\.]+@[\w\-\.]+(?::\d+)?(?:/.*)?$'

        return bool(re.match(rtsp_pattern, url) or re.match(rtsp_auth_pattern, url))

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'camera_id': self.camera_id,
            'rtsp_url': self.rtsp_url,
            'name': self.name,
            'zone': self.zone,
            'capture_interval': self.capture_interval,
            'reconnect_interval': self.reconnect_interval,
            'max_reconnect_attempts': self.max_reconnect_attempts,
            'frame_width': self.frame_width,
            'frame_height': self.frame_height,
            'fps': self.fps,
            'connection_timeout': self.connection_timeout,
            'read_timeout': self.read_timeout,
            'buffer_size': self.buffer_size,
            'location': self.location,
            'description': self.description,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CameraConfig':
        """Create configuration from dictionary"""
        # Handle datetime conversion
        if 'created_at' in data and isinstance(data['created_at'], str):
            data = data.copy()
            data['created_at'] = datetime.fromisoformat(data['created_at'])

        return cls(**data)

    def get_sanitized_url(self) -> str:
        """Get RTSP URL with credentials masked for logging"""
        # Mask credentials in URL
        pattern = r'(rtsp://)([\w\-\.]+):([\w\-\.]+)@'
        return re.sub(pattern, r'\1***:***@', self.rtsp_url)


def create_camera_config_from_url(
    camera_id: str,
    rtsp_url: str,
    name: str,
    zone: str,
    **kwargs
) -> CameraConfig:
    """Helper function to create camera configuration from basic parameters"""
    return CameraConfig(
        camera_id=camera_id,
        rtsp_url=rtsp_url,
        name=name,
        zone=zone,
        **kwargs
    )


# Common RTSP URL templates for Turkish construction sites
RTSP_URL_TEMPLATES = {
    'hikvision': 'rtsp://{username}:{password}@{ip}:{port}/Streaming/Channels/{channel}',
    'dahua': 'rtsp://{username}:{password}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype=0',
    'axis': 'rtsp://{username}:{password}@{ip}:{port}/axis-media/media.amp',
    'generic': 'rtsp://{username}:{password}@{ip}:{port}/{path}',
    'onvif': 'rtsp://{username}:{password}@{ip}:{port}/onvif1',
}


def build_rtsp_url(
    camera_type: str,
    ip: str,
    username: str = 'admin',
    password: str = '',
    port: int = 554,
    channel: int = 1,
    path: str = ''
) -> str:
    """
    Build RTSP URL from components based on camera type

    Args:
        camera_type: Type of camera (hikvision, dahua, axis, generic, onvif)
        ip: IP address of the camera
        username: Username for authentication
        password: Password for authentication
        port: RTSP port (default 554)
        channel: Channel number (for multi-channel cameras)
        path: Custom path (for generic type)

    Returns:
        Formatted RTSP URL
    """
    if camera_type not in RTSP_URL_TEMPLATES:
        raise ValueError(f"Unknown camera type: {camera_type}. Choose from: {list(RTSP_URL_TEMPLATES.keys())}")

    template = RTSP_URL_TEMPLATES[camera_type]

    return template.format(
        username=username,
        password=password,
        ip=ip,
        port=port,
        channel=channel,
        path=path
    )
