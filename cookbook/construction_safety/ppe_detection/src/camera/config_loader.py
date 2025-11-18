"""
Configuration loader for camera system

Loads camera configurations from YAML files and environment variables
"""

import os
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from camera_config import CameraConfig, build_rtsp_url


logger = logging.getLogger(__name__)


def load_camera_configs_from_yaml(yaml_file: str) -> List[CameraConfig]:
    """
    Load camera configurations from YAML file

    Args:
        yaml_file: Path to YAML configuration file

    Returns:
        List of CameraConfig objects

    Raises:
        ImportError: If PyYAML is not installed
        FileNotFoundError: If YAML file doesn't exist
        ValueError: If configuration is invalid
    """
    try:
        import yaml
    except ImportError:
        raise ImportError(
            "PyYAML is required to load YAML configurations. "
            "Install it with: pip install pyyaml"
        )

    # Check if file exists
    if not os.path.exists(yaml_file):
        raise FileNotFoundError(f"Configuration file not found: {yaml_file}")

    # Load YAML file
    with open(yaml_file, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    if not config_data or 'cameras' not in config_data:
        raise ValueError("Invalid configuration file: 'cameras' section not found")

    # Get defaults
    defaults = config_data.get('defaults', {})

    # Create camera configurations
    camera_configs = []

    for cam_data in config_data['cameras']:
        try:
            # Build RTSP URL if components are provided
            if 'camera_type' in cam_data and 'ip' in cam_data:
                rtsp_url = build_rtsp_url(
                    camera_type=cam_data['camera_type'],
                    ip=cam_data['ip'],
                    username=cam_data.get('username', 'admin'),
                    password=cam_data.get('password', ''),
                    port=cam_data.get('port', 554),
                    channel=cam_data.get('channel', 1),
                    path=cam_data.get('path', '')
                )
            elif 'rtsp_url' in cam_data:
                rtsp_url = cam_data['rtsp_url']
            else:
                logger.error(f"Camera {cam_data.get('camera_id')} missing RTSP URL or connection details")
                continue

            # Merge with defaults
            config_params = {
                'camera_id': cam_data['camera_id'],
                'rtsp_url': rtsp_url,
                'name': cam_data['name'],
                'zone': cam_data['zone'],
                'location': cam_data.get('location'),
                'description': cam_data.get('description'),
                'enabled': cam_data.get('enabled', defaults.get('enabled', True)),
                'capture_interval': cam_data.get('capture_interval', defaults.get('capture_interval', 5.0)),
                'reconnect_interval': cam_data.get('reconnect_interval', defaults.get('reconnect_interval', 5.0)),
                'max_reconnect_attempts': cam_data.get('max_reconnect_attempts', defaults.get('max_reconnect_attempts', 3)),
                'connection_timeout': cam_data.get('connection_timeout', defaults.get('connection_timeout', 10.0)),
                'read_timeout': cam_data.get('read_timeout', defaults.get('read_timeout', 5.0)),
                'buffer_size': cam_data.get('buffer_size', defaults.get('buffer_size', 1)),
                'fps': cam_data.get('fps', defaults.get('fps', 30)),
                'frame_width': cam_data.get('frame_width'),
                'frame_height': cam_data.get('frame_height'),
            }

            # Create configuration
            config = CameraConfig(**config_params)
            camera_configs.append(config)

            logger.info(f"Loaded camera configuration: {config.name} ({config.camera_id})")

        except Exception as e:
            logger.error(f"Failed to load camera {cam_data.get('camera_id', 'unknown')}: {e}")
            continue

    logger.info(f"Loaded {len(camera_configs)} camera configurations from {yaml_file}")

    return camera_configs


def load_camera_configs_from_env() -> List[CameraConfig]:
    """
    Load camera configurations from environment variables

    Expected environment variables:
    - CAMERA_<N>_ID: Camera ID
    - CAMERA_<N>_URL: RTSP URL
    - CAMERA_<N>_NAME: Camera name
    - CAMERA_<N>_ZONE: Camera zone
    - CAMERA_<N>_LOCATION: Camera location (optional)
    - CAMERA_<N>_INTERVAL: Capture interval (optional)

    Where <N> is a number (1, 2, 3, ...)

    Returns:
        List of CameraConfig objects
    """
    camera_configs = []
    camera_num = 1

    while True:
        # Check if camera ID exists
        camera_id_key = f"CAMERA_{camera_num}_ID"
        camera_id = os.getenv(camera_id_key)

        if not camera_id:
            # No more cameras
            break

        try:
            # Get required fields
            rtsp_url = os.getenv(f"CAMERA_{camera_num}_URL")
            name = os.getenv(f"CAMERA_{camera_num}_NAME")
            zone = os.getenv(f"CAMERA_{camera_num}_ZONE")

            if not rtsp_url or not name or not zone:
                logger.error(
                    f"Camera {camera_num}: Missing required environment variables "
                    f"(URL, NAME, or ZONE)"
                )
                camera_num += 1
                continue

            # Get optional fields
            location = os.getenv(f"CAMERA_{camera_num}_LOCATION")
            description = os.getenv(f"CAMERA_{camera_num}_DESCRIPTION")
            capture_interval = float(os.getenv(f"CAMERA_{camera_num}_INTERVAL", "5.0"))
            enabled = os.getenv(f"CAMERA_{camera_num}_ENABLED", "true").lower() == "true"

            # Create configuration
            config = CameraConfig(
                camera_id=camera_id,
                rtsp_url=rtsp_url,
                name=name,
                zone=zone,
                location=location,
                description=description,
                capture_interval=capture_interval,
                enabled=enabled
            )

            camera_configs.append(config)
            logger.info(f"Loaded camera from environment: {name} ({camera_id})")

        except Exception as e:
            logger.error(f"Failed to load camera {camera_num} from environment: {e}")

        camera_num += 1

    logger.info(f"Loaded {len(camera_configs)} camera configurations from environment")

    return camera_configs


def load_camera_configs(
    yaml_file: Optional[str] = None,
    use_env: bool = True
) -> List[CameraConfig]:
    """
    Load camera configurations from YAML and/or environment variables

    Args:
        yaml_file: Path to YAML configuration file (optional)
        use_env: Whether to load from environment variables

    Returns:
        List of CameraConfig objects
    """
    configs = []

    # Load from YAML if provided
    if yaml_file:
        try:
            yaml_configs = load_camera_configs_from_yaml(yaml_file)
            configs.extend(yaml_configs)
        except Exception as e:
            logger.error(f"Failed to load configurations from YAML: {e}")

    # Load from environment if enabled
    if use_env:
        try:
            env_configs = load_camera_configs_from_env()
            configs.extend(env_configs)
        except Exception as e:
            logger.error(f"Failed to load configurations from environment: {e}")

    if not configs:
        logger.warning("No camera configurations loaded!")

    return configs


def get_config_from_file(config_file: Optional[str] = None) -> List[CameraConfig]:
    """
    Get camera configurations from file with automatic discovery

    Searches for configuration in the following order:
    1. Provided config_file path
    2. CAMERA_CONFIG_FILE environment variable
    3. ./camera_config.yaml
    4. ./config/camera_config.yaml
    5. /etc/ppe_detection/camera_config.yaml

    Args:
        config_file: Path to configuration file (optional)

    Returns:
        List of CameraConfig objects
    """
    # List of possible configuration file locations
    config_locations = []

    # Add provided config file
    if config_file:
        config_locations.append(config_file)

    # Add environment variable location
    env_config = os.getenv('CAMERA_CONFIG_FILE')
    if env_config:
        config_locations.append(env_config)

    # Add default locations
    config_locations.extend([
        'camera_config.yaml',
        'config/camera_config.yaml',
        '/etc/ppe_detection/camera_config.yaml',
    ])

    # Try each location
    for location in config_locations:
        if os.path.exists(location):
            logger.info(f"Found configuration file: {location}")
            try:
                return load_camera_configs_from_yaml(location)
            except Exception as e:
                logger.error(f"Failed to load configuration from {location}: {e}")
                continue

    # Fall back to environment variables
    logger.warning("No configuration file found, trying environment variables")
    return load_camera_configs_from_env()


def save_camera_configs_to_yaml(
    configs: List[CameraConfig],
    yaml_file: str,
    include_site_info: bool = True
) -> None:
    """
    Save camera configurations to YAML file

    Args:
        configs: List of CameraConfig objects
        yaml_file: Path to output YAML file
        include_site_info: Whether to include site information section
    """
    try:
        import yaml
    except ImportError:
        raise ImportError(
            "PyYAML is required to save YAML configurations. "
            "Install it with: pip install pyyaml"
        )

    # Build configuration dictionary
    config_data = {}

    if include_site_info:
        config_data['site'] = {
            'name': 'Construction Site',
            'location': 'Turkey',
            'timezone': 'Europe/Istanbul'
        }

    # Add defaults
    config_data['defaults'] = {
        'capture_interval': 5.0,
        'reconnect_interval': 5.0,
        'max_reconnect_attempts': 3,
        'connection_timeout': 10.0,
        'read_timeout': 5.0,
        'buffer_size': 1,
        'fps': 30,
        'enabled': True
    }

    # Add cameras
    config_data['cameras'] = []
    for config in configs:
        cam_dict = config.to_dict()

        # Remove some fields that shouldn't be in YAML
        cam_dict.pop('created_at', None)
        cam_dict.pop('metadata', None)

        config_data['cameras'].append(cam_dict)

    # Write to file
    with open(yaml_file, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    logger.info(f"Saved {len(configs)} camera configurations to {yaml_file}")


# Example usage in main
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Example 1: Load from YAML
    print("\nExample 1: Load from YAML file")
    try:
        configs = load_camera_configs_from_yaml('camera_config.yaml')
        print(f"Loaded {len(configs)} cameras from YAML")
        for config in configs:
            print(f"  - {config.name} ({config.zone})")
    except Exception as e:
        print(f"Error: {e}")

    # Example 2: Load from environment
    print("\nExample 2: Load from environment variables")
    os.environ['CAMERA_1_ID'] = 'cam_env_001'
    os.environ['CAMERA_1_URL'] = 'rtsp://admin:pass@192.168.1.100:554/stream'
    os.environ['CAMERA_1_NAME'] = 'Env Camera 1'
    os.environ['CAMERA_1_ZONE'] = 'Test Zone'

    configs = load_camera_configs_from_env()
    print(f"Loaded {len(configs)} cameras from environment")
    for config in configs:
        print(f"  - {config.name} ({config.zone})")

    # Example 3: Auto-discovery
    print("\nExample 3: Auto-discovery")
    configs = get_config_from_file()
    print(f"Auto-discovered {len(configs)} cameras")
