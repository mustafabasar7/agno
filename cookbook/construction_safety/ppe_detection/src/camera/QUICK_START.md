# Quick Start Guide - RTSP Camera System

## Turkish Construction Site Setup / Türk Şantiyesi Kurulum

### 1. Installation / Kurulum

```bash
# Install dependencies
pip install -r requirements.txt

# For YAML configuration support
pip install pyyaml

# For environment variable management
pip install python-dotenv
```

### 2. Configuration / Yapılandırma

#### Option A: YAML Configuration (Recommended)

```bash
# Copy example configuration
cp camera_config.example.yaml camera_config.yaml

# Edit with your camera details
nano camera_config.yaml
```

Update camera details:
```yaml
cameras:
  - camera_id: "cam_giris_001"
    name: "Ana Giriş Kapısı"
    zone: "Giriş Kontrol"
    camera_type: "hikvision"
    ip: "192.168.1.100"
    username: "admin"
    password: "your_password"
    channel: 1
```

#### Option B: Environment Variables

```bash
# Copy example .env
cp .env.example .env

# Edit with your camera details
nano .env
```

Update variables:
```bash
CAMERA_1_ID=cam_giris_001
CAMERA_1_URL=rtsp://admin:password@192.168.1.100:554/Streaming/Channels/101
CAMERA_1_NAME=Ana Giriş Kapısı
CAMERA_1_ZONE=Giriş Kontrol
```

### 3. Basic Usage / Temel Kullanım

#### Simple Single Camera Example

```python
from camera import CameraConfig, CameraManager

# Create camera configuration
config = CameraConfig(
    camera_id="cam_001",
    rtsp_url="rtsp://admin:password@192.168.1.100:554/Streaming/Channels/101",
    name="Giriş Kapısı",
    zone="Giriş Bölgesi"
)

# Create manager and add camera
manager = CameraManager()
manager.start()
manager.add_camera(config)

# Wait for connection
import time
time.sleep(5)

# Get snapshot
frame = manager.snapshot("cam_001")
if frame is not None:
    import cv2
    cv2.imwrite("snapshot.jpg", frame)
    print("Snapshot saved!")

# Cleanup
manager.stop()
```

#### Production Example with Configuration File

```python
from camera.config_loader import get_config_from_file
from camera import CameraManager

# Load configurations
configs = get_config_from_file('camera_config.yaml')

# Create and start manager
manager = CameraManager()
manager.start()

# Add all cameras
for config in configs:
    manager.add_camera(config)

# Monitor health
health = manager.get_health_summary()
print(f"Active: {health['active_cameras']}/{health['total_cameras']}")

# Capture snapshots from all cameras
snapshots = manager.snapshot_all()
for camera_id, frame in snapshots.items():
    if frame is not None:
        cv2.imwrite(f"{camera_id}.jpg", frame)

# Cleanup
manager.stop()
```

### 4. Common Camera Types / Yaygın Kamera Türleri

#### Hikvision

```python
from camera import build_rtsp_url

url = build_rtsp_url(
    camera_type='hikvision',
    ip='192.168.1.100',
    username='admin',
    password='12345',
    channel=1
)
# rtsp://admin:12345@192.168.1.100:554/Streaming/Channels/1
```

#### Dahua

```python
url = build_rtsp_url(
    camera_type='dahua',
    ip='192.168.1.101',
    username='admin',
    password='12345',
    channel=1
)
# rtsp://admin:12345@192.168.1.101:554/cam/realmonitor?channel=1&subtype=0
```

#### Axis

```python
url = build_rtsp_url(
    camera_type='axis',
    ip='192.168.1.102',
    username='root',
    password='12345'
)
# rtsp://root:12345@192.168.1.102:554/axis-media/media.amp
```

#### ONVIF (Generic)

```python
url = build_rtsp_url(
    camera_type='onvif',
    ip='192.168.1.103',
    username='admin',
    password='12345'
)
# rtsp://admin:12345@192.168.1.103:554/onvif1
```

### 5. Testing / Test

```bash
# Run test suite
python test_camera_system.py

# Run examples
python example_usage.py

# Run production example
python production_example.py
```

### 6. Production Deployment / Üretim Dağıtımı

#### As a Service (systemd)

Create `/etc/systemd/system/ppe-camera.service`:

```ini
[Unit]
Description=PPE Detection Camera System
After=network.target

[Service]
Type=simple
User=ppe-user
WorkingDirectory=/opt/ppe_detection
Environment="PYTHONPATH=/opt/ppe_detection"
ExecStart=/usr/bin/python3 /opt/ppe_detection/src/camera/production_example.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable ppe-camera
sudo systemctl start ppe-camera
sudo systemctl status ppe-camera
```

#### With Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install OpenCV dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY src/camera/ ./camera/
COPY camera_config.yaml .

# Run
CMD ["python", "camera/production_example.py"]
```

Build and run:
```bash
docker build -t ppe-camera .
docker run -d \
    --name ppe-camera \
    --restart unless-stopped \
    -v /var/ppe_detection:/var/ppe_detection \
    -v $(pwd)/camera_config.yaml:/app/camera_config.yaml \
    ppe-camera
```

### 7. API Integration / API Entegrasyonu

#### With Flask

```python
from flask import Flask, jsonify
from camera import CameraManager
from camera.config_loader import get_config_from_file

app = Flask(__name__)

# Initialize camera system
manager = CameraManager()
manager.start()
for config in get_config_from_file():
    manager.add_camera(config)

@app.route('/api/cameras/status')
def get_status():
    health = manager.get_health_summary()
    return jsonify(health)

@app.route('/api/cameras/<camera_id>/snapshot')
def get_snapshot(camera_id):
    frame = manager.snapshot(camera_id)
    if frame is None:
        return {'error': 'Not found'}, 404

    import cv2, io
    _, buffer = cv2.imencode('.jpg', frame)
    return send_file(io.BytesIO(buffer), mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

#### With FastAPI

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from camera import CameraManager
from camera.config_loader import get_config_from_file
import cv2, io

app = FastAPI()

# Initialize
manager = CameraManager()
manager.start()
for config in get_config_from_file():
    manager.add_camera(config)

@app.get("/api/cameras/status")
async def get_status():
    return manager.get_health_summary()

@app.get("/api/cameras/{camera_id}/snapshot")
async def get_snapshot(camera_id: str):
    frame = manager.snapshot(camera_id)
    if frame is None:
        return {"error": "Not found"}

    _, buffer = cv2.imencode('.jpg', frame)
    return StreamingResponse(
        io.BytesIO(buffer),
        media_type="image/jpeg"
    )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
```

### 8. Monitoring / İzleme

#### Health Check Script

```bash
#!/bin/bash
# /opt/ppe_detection/scripts/health_check.sh

STATUS=$(curl -s http://localhost:5000/api/cameras/status)
ACTIVE=$(echo $STATUS | jq '.active_cameras')
TOTAL=$(echo $STATUS | jq '.total_cameras')

if [ "$ACTIVE" -lt "$TOTAL" ]; then
    echo "WARNING: Only $ACTIVE/$TOTAL cameras active"
    exit 1
fi

echo "OK: All cameras active"
exit 0
```

#### Cron Job for Monitoring

```bash
# Check every 5 minutes
*/5 * * * * /opt/ppe_detection/scripts/health_check.sh
```

### 9. Troubleshooting / Sorun Giderme

#### Camera Won't Connect

```bash
# Test RTSP URL with ffmpeg
ffmpeg -rtsp_transport tcp -i "rtsp://admin:password@192.168.1.100:554/stream" -frames:v 1 test.jpg

# Test with VLC
vlc rtsp://admin:password@192.168.1.100:554/stream

# Check network connectivity
ping 192.168.1.100
telnet 192.168.1.100 554
```

#### High CPU Usage

```python
# Increase capture interval
config = CameraConfig(
    capture_interval=10.0,  # Capture every 10 seconds instead of 5
    ...
)

# Resize frames
config = CameraConfig(
    frame_width=640,
    frame_height=480,
    ...
)
```

#### Memory Issues

```python
# Ensure buffer size is 1
config = CameraConfig(
    buffer_size=1,  # Only keep latest frame
    ...
)
```

### 10. Common Turkish Construction Site Zones

```yaml
zones:
  - "Giriş Kontrol"          # Entrance Control
  - "İnşaat Bölgesi"         # Construction Area
  - "Vinç Operasyon"         # Crane Operation
  - "Depo Bölgesi"           # Storage Area
  - "Ekipman Bölgesi"        # Equipment Area
  - "Sosyal Tesis"           # Social Facilities
  - "Park Alanı"             # Parking Area
  - "Yükleme Boşaltma"       # Loading/Unloading
  - "İskele Alanı"           # Scaffolding Area
  - "Kapalı İnşaat"          # Indoor Construction
```

### 11. Support / Destek

For issues or questions:
- Check logs: `/var/log/ppe_detection/camera.log`
- Run tests: `python test_camera_system.py`
- Review examples: `example_usage.py`
- Production setup: `production_example.py`

---

## Quick Reference / Hızlı Referans

| Task | Command |
|------|---------|
| Install | `pip install -r requirements.txt` |
| Configure | Edit `camera_config.yaml` |
| Test | `python test_camera_system.py` |
| Run | `python production_example.py` |
| Health Check | Check `/api/cameras/status` endpoint |
| Logs | `tail -f /var/log/ppe_detection/camera.log` |

---

**İyi kullanımlar! / Good luck!** 🏗️
