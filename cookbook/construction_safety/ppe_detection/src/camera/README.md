# RTSP Camera Stream Handler

Comprehensive RTSP camera stream handler for PPE detection in Turkish construction sites. Supports multiple cameras, automatic reconnection, health monitoring, and thread-safe frame capture.

## Features

- **Multi-Camera Support**: Manage multiple RTSP camera streams simultaneously
- **Automatic Reconnection**: Handles connection loss with configurable retry logic
- **Thread-Safe**: Thread-safe frame grabbing and camera management
- **Memory Efficient**: Stores only the latest frame, not entire video buffer
- **Health Monitoring**: Real-time monitoring of camera connection status
- **Flexible Configuration**: Support for various camera types (Hikvision, Dahua, Axis, ONVIF)
- **Turkish Language Support**: Examples and documentation for Turkish construction sites

## Architecture

### Components

1. **camera_config.py**: Camera configuration schema and validation
   - `CameraConfig`: Configuration dataclass for camera settings
   - `build_rtsp_url()`: Helper to build RTSP URLs for common camera types
   - `RTSP_URL_TEMPLATES`: Templates for various camera manufacturers

2. **rtsp_handler.py**: Individual RTSP stream handler
   - `RTSPHandler`: Manages single camera connection
   - Captures frames at configurable intervals
   - Automatic reconnection on failure
   - Thread-safe frame access

3. **camera_manager.py**: Multi-camera management
   - `CameraManager`: Manages multiple camera connections
   - Dynamic camera addition/removal
   - Health monitoring across all cameras
   - Batch snapshot capture

## Installation

### Requirements

```bash
pip install opencv-python numpy
```

### Optional Dependencies

For better RTSP stream handling:
```bash
pip install opencv-contrib-python
```

## Quick Start

### Single Camera Example

```python
from camera import CameraConfig, CameraManager

# Create camera configuration
config = CameraConfig(
    camera_id="cam_001",
    rtsp_url="rtsp://admin:12345@192.168.1.100:554/Streaming/Channels/101",
    name="Giriş Kapısı",
    zone="Giriş Bölgesi",
    capture_interval=5.0
)

# Create and start camera manager
manager = CameraManager()
manager.start()

# Add camera
manager.add_camera(config)

# Get snapshot
frame = manager.snapshot("cam_001")
if frame is not None:
    import cv2
    cv2.imwrite("snapshot.jpg", frame)

# Cleanup
manager.stop()
```

### Multiple Cameras Example

```python
from camera import CameraConfig, CameraManager, build_rtsp_url

# Create camera manager
manager = CameraManager()
manager.start()

# Define cameras for construction site
cameras = [
    {
        'id': 'cam_giris_001',
        'name': 'Ana Giriş',
        'zone': 'Giriş Kontrol',
        'ip': '192.168.1.100',
        'type': 'hikvision'
    },
    {
        'id': 'cam_insaat_001',
        'name': 'İnşaat Alanı',
        'zone': 'İnşaat Bölgesi',
        'ip': '192.168.1.101',
        'type': 'dahua'
    }
]

# Add cameras
for cam in cameras:
    rtsp_url = build_rtsp_url(
        camera_type=cam['type'],
        ip=cam['ip'],
        username='admin',
        password='password',
        channel=1
    )

    config = CameraConfig(
        camera_id=cam['id'],
        rtsp_url=rtsp_url,
        name=cam['name'],
        zone=cam['zone']
    )

    manager.add_camera(config)

# Get snapshots from all cameras
snapshots = manager.snapshot_all()
for camera_id, frame in snapshots.items():
    if frame is not None:
        cv2.imwrite(f"snapshot_{camera_id}.jpg", frame)

# Get health summary
health = manager.get_health_summary()
print(f"Active cameras: {health['active_cameras']}/{health['total_cameras']}")

# Cleanup
manager.stop()
```

## Configuration

### Camera Configuration Options

```python
CameraConfig(
    # Required
    camera_id="unique_id",           # Unique identifier
    rtsp_url="rtsp://...",           # RTSP stream URL
    name="Camera Name",              # Display name
    zone="Zone Name",                # Zone/area identifier

    # Capture settings
    capture_interval=5.0,            # Seconds between captures
    reconnect_interval=5.0,          # Seconds between reconnect attempts
    max_reconnect_attempts=3,        # Max consecutive reconnect attempts

    # Stream settings
    frame_width=None,                # Resize width (None = original)
    frame_height=None,               # Resize height (None = original)
    fps=30,                          # Target FPS

    # Timeout settings
    connection_timeout=10.0,         # Connection timeout (seconds)
    read_timeout=5.0,                # Frame read timeout (seconds)

    # Buffer settings
    buffer_size=1,                   # Frame buffer size (1 = latest only)

    # Metadata
    location="Location",             # Physical location
    description="Description",       # Camera description
    enabled=True,                    # Enable/disable camera
    metadata={}                      # Additional metadata
)
```

### Supported Camera Types

#### Hikvision
```python
rtsp_url = build_rtsp_url(
    camera_type='hikvision',
    ip='192.168.1.100',
    username='admin',
    password='password',
    channel=1  # Channel number (usually 1 or 101)
)
# Format: rtsp://admin:password@192.168.1.100:554/Streaming/Channels/1
```

#### Dahua
```python
rtsp_url = build_rtsp_url(
    camera_type='dahua',
    ip='192.168.1.101',
    username='admin',
    password='password',
    channel=1  # Channel number
)
# Format: rtsp://admin:password@192.168.1.101:554/cam/realmonitor?channel=1&subtype=0
```

#### Axis
```python
rtsp_url = build_rtsp_url(
    camera_type='axis',
    ip='192.168.1.102',
    username='root',
    password='password'
)
# Format: rtsp://root:password@192.168.1.102:554/axis-media/media.amp
```

#### ONVIF
```python
rtsp_url = build_rtsp_url(
    camera_type='onvif',
    ip='192.168.1.103',
    username='admin',
    password='password'
)
# Format: rtsp://admin:password@192.168.1.103:554/onvif1
```

#### Generic
```python
rtsp_url = build_rtsp_url(
    camera_type='generic',
    ip='192.168.1.104',
    username='admin',
    password='password',
    path='live/main'
)
# Format: rtsp://admin:password@192.168.1.104:554/live/main
```

## API Reference

### CameraManager

#### Methods

- `start()`: Start the camera manager and health monitoring
- `stop()`: Stop all cameras and cleanup resources
- `add_camera(config)`: Add a new camera
- `remove_camera(camera_id)`: Remove a camera
- `snapshot(camera_id)`: Get latest frame from specific camera
- `snapshot_all()`: Get latest frames from all cameras
- `get_all_active_cameras()`: Get list of active camera IDs
- `get_all_cameras()`: Get list of all camera IDs
- `get_camera_status(camera_id)`: Get status of specific camera
- `get_all_camera_status()`: Get status of all cameras
- `get_health_summary()`: Get overall health summary
- `enable_camera(camera_id)`: Enable a camera
- `disable_camera(camera_id)`: Disable a camera

#### Context Manager

```python
with CameraManager() as manager:
    # Add cameras
    manager.add_camera(config)

    # Use cameras
    frame = manager.snapshot("cam_001")

# Automatic cleanup
```

### RTSPHandler

#### Methods

- `start()`: Start capturing frames
- `stop()`: Stop capturing and release resources
- `get_frame()`: Get latest frame with timestamp
- `snapshot()`: Get latest frame only
- `is_healthy()`: Check if connection is healthy
- `get_status()`: Get detailed status information

#### Context Manager

```python
with RTSPHandler(config) as handler:
    # Capture frames
    frame = handler.snapshot()

# Automatic cleanup
```

## Turkish Construction Site Example

```python
from camera import CameraManager, CameraConfig, build_rtsp_url
import time

# Şantiye kameraları (Construction site cameras)
cameras = [
    {
        'id': 'cam_giris_001',
        'name': 'Ana Giriş Kapısı',
        'zone': 'Giriş Kontrol',
        'ip': '192.168.1.100',
        'type': 'hikvision',
        'location': 'Şantiye Ana Girişi'
    },
    {
        'id': 'cam_insaat_001',
        'name': 'İnşaat Alanı A',
        'zone': 'İnşaat Bölgesi',
        'ip': '192.168.1.101',
        'type': 'hikvision',
        'location': 'A Blok İnşaat Alanı'
    },
    {
        'id': 'cam_vinc_001',
        'name': 'Vinç Alanı',
        'zone': 'Vinç Operasyon',
        'ip': '192.168.1.102',
        'type': 'dahua',
        'location': 'Kule Vinç 1'
    },
    {
        'id': 'cam_depo_001',
        'name': 'Malzeme Deposu',
        'zone': 'Depo Bölgesi',
        'ip': '192.168.1.103',
        'type': 'hikvision',
        'location': 'Ana Malzeme Deposu'
    }
]

# Kamera yöneticisi oluştur (Create camera manager)
manager = CameraManager()
manager.start()

# Kameraları ekle (Add cameras)
for cam in cameras:
    rtsp_url = build_rtsp_url(
        camera_type=cam['type'],
        ip=cam['ip'],
        username='admin',
        password='Santiye123!',
        channel=1
    )

    config = CameraConfig(
        camera_id=cam['id'],
        rtsp_url=rtsp_url,
        name=cam['name'],
        zone=cam['zone'],
        location=cam['location'],
        capture_interval=5.0
    )

    manager.add_camera(config)
    print(f"Kamera eklendi: {cam['name']}")

# Kameraların bağlanmasını bekle (Wait for connection)
time.sleep(10)

# Sağlık raporu (Health report)
health = manager.get_health_summary()
print(f"\nKamera Sağlık Raporu:")
print(f"Toplam: {health['total_cameras']}")
print(f"Aktif: {health['active_cameras']}")
print(f"Sağlık: {health['health_percentage']:.1f}%")

# Görüntü yakala (Capture snapshots)
snapshots = manager.snapshot_all()
for camera_id, frame in snapshots.items():
    if frame is not None:
        cv2.imwrite(f"/tmp/{camera_id}.jpg", frame)
        print(f"Görüntü kaydedildi: {camera_id}")

# Temizlik (Cleanup)
manager.stop()
```

## Error Handling

The system includes comprehensive error handling:

- **Connection Failures**: Automatic reconnection with configurable retry logic
- **Network Issues**: Timeout handling for connections and frame reads
- **Thread Safety**: All operations are thread-safe
- **Resource Cleanup**: Automatic resource cleanup on stop

## Logging

Configure logging to monitor camera operations:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Performance Considerations

- **Memory Usage**: Stores only latest frame per camera
- **CPU Usage**: Configurable capture intervals to reduce load
- **Network Bandwidth**: Buffer size of 1 minimizes latency
- **Thread Count**: One thread per camera + one for health monitoring

## Troubleshooting

### Camera Won't Connect

1. Check RTSP URL format
2. Verify network connectivity
3. Check camera credentials
4. Ensure camera supports RTSP
5. Check firewall settings

### Frame Capture Issues

1. Increase `connection_timeout`
2. Increase `read_timeout`
3. Reduce `fps` setting
4. Check network bandwidth

### High CPU Usage

1. Increase `capture_interval`
2. Enable frame resizing
3. Reduce number of cameras

## License

This module is part of the PPE Detection system for construction safety.

## Examples

See `example_usage.py` for complete examples including:
- Single camera connection
- Multiple camera management
- Health monitoring
- Dynamic camera management
- Common camera type configurations
