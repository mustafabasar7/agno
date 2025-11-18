# RTSP Camera Stream Handler - Start Here 🎥

## Welcome! / Hoş Geldiniz! 🏗️

This is a complete RTSP camera stream handler system for PPE detection in Turkish construction sites.

**Status:** ✅ Complete and Ready to Use

---

## 📁 What's Included

**16 files created** with ~130 KB of production-ready code and documentation.

### Core System (3 files)
- ✅ `camera_config.py` - Camera configuration and validation
- ✅ `rtsp_handler.py` - Individual RTSP stream handler  
- ✅ `camera_manager.py` - Multi-camera management

### Configuration (3 files)
- ✅ `config_loader.py` - Load configs from YAML/environment
- ✅ `camera_config.example.yaml` - Example Turkish construction site config
- ✅ `.env.example` - Environment variable template

### Examples (4 files)
- ✅ `example_usage.py` - 5 comprehensive examples
- ✅ `production_example.py` - Production deployment example
- ✅ `test_camera_system.py` - Complete test suite
- ✅ `verify_installation.py` - Installation verification

### Documentation (5 files)
- 📖 `README.md` - Complete documentation
- 📖 `QUICK_START.md` - Quick reference guide
- 📖 `IMPLEMENTATION_SUMMARY.md` - Implementation details
- 📖 `FILES_CREATED.md` - File descriptions
- 📖 `00_START_HERE.md` - This file!

### Package (2 files)
- ✅ `__init__.py` - Package exports
- ✅ `requirements.txt` - Dependencies

---

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install pyyaml  # For YAML configuration (optional)
```

### 2. Verify Installation
```bash
python verify_installation.py
```

### 3. Try Basic Example
```python
from camera import CameraConfig, CameraManager, build_rtsp_url

# Build Hikvision RTSP URL
url = build_rtsp_url(
    camera_type='hikvision',
    ip='192.168.1.100',
    username='admin',
    password='password',
    channel=1
)

# Create camera configuration
config = CameraConfig(
    camera_id="cam_001",
    rtsp_url=url,
    name="Ana Giriş Kapısı",
    zone="Giriş Kontrol"
)

# Create manager and capture
with CameraManager() as manager:
    manager.add_camera(config)
    
    import time
    time.sleep(5)  # Wait for connection
    
    frame = manager.snapshot("cam_001")
    if frame is not None:
        import cv2
        cv2.imwrite("test_snapshot.jpg", frame)
        print("✅ Success! Snapshot saved to test_snapshot.jpg")
```

---

## 📚 Documentation Guide

### For First-Time Users
1. **Start Here:** `00_START_HERE.md` (this file)
2. **Quick Setup:** `QUICK_START.md`
3. **Run Examples:** `python example_usage.py`

### For Implementation
1. **Full Docs:** `README.md`
2. **API Reference:** `README.md` (API Reference section)
3. **Configuration:** `camera_config.example.yaml`

### For Production Deployment
1. **Production Guide:** `production_example.py`
2. **Deployment Options:** `QUICK_START.md` (Production Deployment section)
3. **API Integration:** `production_example.py` (API examples)

### For Understanding the Code
1. **Implementation Details:** `IMPLEMENTATION_SUMMARY.md`
2. **File Descriptions:** `FILES_CREATED.md`
3. **Source Code:** All `.py` files are well-documented

---

## 🎯 Use Cases

### Single Camera Example
```python
# See: example_usage.py - Example 1
python example_usage.py  # Uncomment example_1_single_camera()
```

### Multiple Cameras (Turkish Construction Site)
```python
# See: example_usage.py - Example 2
python example_usage.py  # Uncomment example_2_multiple_cameras_turkish_site()
```

### Production Deployment
```bash
# See: production_example.py
python production_example.py
```

### API Integration (Flask/FastAPI)
```python
# See: production_example.py - example_api_integration()
# Contains complete Flask and FastAPI examples
```

---

## 🔧 Supported Camera Types

All common construction site cameras are supported:

| Brand | Type | Example |
|-------|------|---------|
| Hikvision | `hikvision` | Most common in Turkish sites |
| Dahua | `dahua` | Popular alternative |
| Axis | `axis` | High-end cameras |
| ONVIF | `onvif` | Generic ONVIF cameras |
| Generic | `generic` | Custom RTSP streams |

### URL Builder Example
```python
from camera import build_rtsp_url

# Hikvision
url = build_rtsp_url('hikvision', '192.168.1.100', 'admin', 'pass123', channel=1)
# Result: rtsp://admin:pass123@192.168.1.100:554/Streaming/Channels/1

# Dahua
url = build_rtsp_url('dahua', '192.168.1.101', 'admin', 'pass123', channel=1)
# Result: rtsp://admin:pass123@192.168.1.101:554/cam/realmonitor?channel=1&subtype=0
```

---

## 📋 Feature Checklist

All requested features implemented:

- ✅ RTSP camera stream connection
- ✅ Configurable frame capture intervals (e.g., every 5 seconds)
- ✅ Automatic reconnection on connection loss
- ✅ Multiple camera support (simultaneous)
- ✅ Thread-safe frame grabbing
- ✅ Memory efficient (doesn't store all frames)
- ✅ `snapshot(camera_id)` - returns latest frame
- ✅ `get_all_active_cameras()` - list of working cameras
- ✅ `add_camera(config)` - adds new camera
- ✅ `remove_camera(camera_id)` - removes camera
- ✅ Error handling for network issues
- ✅ Health monitoring of camera connections
- ✅ Camera configuration schema
- ✅ Common RTSP URL format support
- ✅ Turkish construction site examples

---

## 🏗️ Turkish Construction Site Zones

Predefined zones in example configuration:

- **Giriş Kontrol** - Entrance Control
- **İnşaat Bölgesi** - Construction Area
- **Vinç Operasyon** - Crane Operation
- **Depo Bölgesi** - Storage Area
- **Ekipman Bölgesi** - Equipment Area
- **Sosyal Tesis** - Social Facilities
- **Park Alanı** - Parking Area
- **Yükleme Boşaltma** - Loading/Unloading

See `camera_config.example.yaml` for complete zone definitions.

---

## 🧪 Testing

### Run All Tests
```bash
python test_camera_system.py
```

### Verify Installation
```bash
python verify_installation.py
```

### Test Categories
1. ✅ Configuration validation
2. ✅ RTSP URL builder
3. ✅ Camera manager
4. ✅ Context managers
5. ✅ API functionality

---

## 🚢 Production Deployment

### Option 1: Direct Python
```bash
python production_example.py
```

### Option 2: Systemd Service
See `QUICK_START.md` for systemd service configuration.

### Option 3: Docker
See `QUICK_START.md` for Dockerfile example.

### Option 4: API Service (Flask/FastAPI)
See `production_example.py` for complete API examples.

---

## 🔍 Troubleshooting

### Camera Won't Connect
```bash
# Test with VLC
vlc rtsp://admin:password@192.168.1.100:554/stream

# Test with ffmpeg
ffmpeg -i "rtsp://admin:password@192.168.1.100:554/stream" -frames:v 1 test.jpg
```

### Check Logs
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues
- Network connectivity → Check firewall, ping camera
- Wrong credentials → Verify username/password
- Wrong URL format → Use build_rtsp_url()
- High CPU usage → Increase capture_interval

See `README.md` for detailed troubleshooting.

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────┐
│              Camera Manager                         │
│  (Manages multiple cameras, health monitoring)     │
└──────────────┬──────────────────────────────────────┘
               │
               ├──── RTSP Handler 1 (Camera 1)
               │     └── Thread-safe frame capture
               │
               ├──── RTSP Handler 2 (Camera 2)
               │     └── Thread-safe frame capture
               │
               └──── RTSP Handler N (Camera N)
                     └── Thread-safe frame capture

Each handler:
- Connects to RTSP stream
- Captures frames at intervals
- Auto-reconnects on failure
- Stores only latest frame
```

---

## 💡 Next Steps

### For Development
1. Read `README.md` for full documentation
2. Try examples in `example_usage.py`
3. Customize `camera_config.example.yaml`

### For Production
1. Configure cameras in `camera_config.yaml`
2. Set up systemd service or Docker
3. Integrate with PPE detection system
4. Set up monitoring and alerts

### For Integration
1. Review API examples in `production_example.py`
2. Implement PPE detection hooks
3. Set up database for violations
4. Configure alerting system

---

## 🤝 Support & Documentation

| Need | File |
|------|------|
| Quick setup | `QUICK_START.md` |
| Full documentation | `README.md` |
| Examples | `example_usage.py` |
| Production setup | `production_example.py` |
| Testing | `test_camera_system.py` |
| Implementation details | `IMPLEMENTATION_SUMMARY.md` |
| File descriptions | `FILES_CREATED.md` |

---

## 📝 Configuration Files

### YAML Configuration (Recommended)
```bash
cp camera_config.example.yaml camera_config.yaml
nano camera_config.yaml  # Edit with your cameras
```

### Environment Variables
```bash
cp .env.example .env
nano .env  # Edit with your cameras
```

### Python Code
```python
config = CameraConfig(
    camera_id="cam_001",
    rtsp_url="rtsp://...",
    name="Camera Name",
    zone="Zone Name"
)
```

---

## ✅ System Status

- **Implementation:** ✅ Complete
- **Testing:** ✅ Test suite included
- **Documentation:** ✅ Comprehensive
- **Examples:** ✅ 5 working examples
- **Production Ready:** ✅ Yes
- **Turkish Support:** ✅ Full support

---

## 🎓 Learning Path

### Beginner
1. Run `verify_installation.py`
2. Read `QUICK_START.md`
3. Try single camera example
4. Read `README.md`

### Intermediate
1. Try multiple camera example
2. Customize configuration
3. Run test suite
4. Review `production_example.py`

### Advanced
1. Integrate with PPE detection
2. Set up production deployment
3. Implement API endpoints
4. Configure monitoring

---

## 🔗 File Links

**Must Read:**
- [`QUICK_START.md`](./QUICK_START.md) - Start here for setup
- [`README.md`](./README.md) - Complete documentation

**Examples:**
- [`example_usage.py`](./example_usage.py) - 5 working examples
- [`production_example.py`](./production_example.py) - Production deployment

**Configuration:**
- [`camera_config.example.yaml`](./camera_config.example.yaml) - Example config
- [`.env.example`](./.env.example) - Environment variables

**Testing:**
- [`test_camera_system.py`](./test_camera_system.py) - Test suite
- [`verify_installation.py`](./verify_installation.py) - Installation check

---

## 📞 Getting Help

1. **Check documentation** - Most questions answered in README.md
2. **Run verification** - `python verify_installation.py`
3. **Check logs** - Enable DEBUG logging
4. **Review examples** - Complete working examples provided

---

## 🎉 You're Ready!

Everything you need is here. Start with:

```bash
# 1. Install
pip install -r requirements.txt

# 2. Verify
python verify_installation.py

# 3. Try example
python example_usage.py

# 4. Configure your cameras
cp camera_config.example.yaml camera_config.yaml

# 5. Deploy!
python production_example.py
```

**İyi kullanımlar! / Good luck!** 🚀

---

**Created:** 2025-11-18  
**Location:** `/home/user/agno/cookbook/construction_safety/ppe_detection/src/camera/`  
**Total Files:** 16 files (~130 KB)  
**Status:** ✅ Production Ready
