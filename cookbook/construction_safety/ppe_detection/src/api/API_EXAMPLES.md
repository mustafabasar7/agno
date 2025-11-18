# PPE Detection API - Example Requests & Responses

## Table of Contents
- [Getting Started](#getting-started)
- [Camera Management](#camera-management)
- [Detection](#detection)
- [Violations](#violations)
- [Statistics](#statistics)
- [WebSocket Live Feed](#websocket-live-feed)
- [Health & Status](#health--status)

---

## Getting Started

### Starting the API Server

```bash
# Development mode with auto-reload
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- OpenAPI JSON: http://localhost:8000/api/openapi.json

---

## Camera Management

### 1. Create New Camera

**Request:**
```bash
curl -X POST "http://localhost:8000/api/cameras" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Şantiye Giriş Kamerası",
    "rtsp_url": "rtsp://192.168.1.100:554/stream",
    "location": "Ana Giriş",
    "zone": "Bölge A",
    "enabled": true,
    "detection_interval": 5,
    "confidence_threshold": 0.7,
    "required_ppe": ["helmet", "vest"]
  }'
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "Şantiye Giriş Kamerası",
  "rtsp_url": "rtsp://192.168.1.100:554/stream",
  "location": "Ana Giriş",
  "zone": "Bölge A",
  "status": "active",
  "enabled": true,
  "detection_interval": 5,
  "confidence_threshold": 0.7,
  "required_ppe": ["helmet", "vest"],
  "created_at": "2023-11-18T10:30:00",
  "updated_at": "2023-11-18T10:30:00",
  "last_seen": "2023-11-18T10:30:00"
}
```

### 2. List All Cameras

**Request:**
```bash
curl -X GET "http://localhost:8000/api/cameras"
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Şantiye Giriş Kamerası",
    "rtsp_url": "rtsp://192.168.1.100:554/stream",
    "location": "Ana Giriş",
    "zone": "Bölge A",
    "status": "active",
    "enabled": true,
    "detection_interval": 5,
    "confidence_threshold": 0.7,
    "required_ppe": ["helmet", "vest"],
    "created_at": "2023-11-18T10:30:00",
    "updated_at": "2023-11-18T10:30:00",
    "last_seen": "2023-11-18T12:45:00"
  },
  {
    "id": 2,
    "name": "İnşaat Alanı Kamerası",
    "rtsp_url": "rtsp://192.168.1.101:554/stream",
    "location": "İnşaat Alanı",
    "zone": "Bölge B",
    "status": "active",
    "enabled": true,
    "detection_interval": 10,
    "confidence_threshold": 0.65,
    "required_ppe": ["helmet", "vest", "boots"],
    "created_at": "2023-11-18T09:15:00",
    "updated_at": "2023-11-18T09:15:00",
    "last_seen": "2023-11-18T12:44:30"
  }
]
```

### 3. Get Camera Details

**Request:**
```bash
curl -X GET "http://localhost:8000/api/cameras/1"
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Şantiye Giriş Kamerası",
  "rtsp_url": "rtsp://192.168.1.100:554/stream",
  "location": "Ana Giriş",
  "zone": "Bölge A",
  "status": "active",
  "enabled": true,
  "detection_interval": 5,
  "confidence_threshold": 0.7,
  "required_ppe": ["helmet", "vest"],
  "created_at": "2023-11-18T10:30:00",
  "updated_at": "2023-11-18T10:30:00",
  "last_seen": "2023-11-18T12:45:00"
}
```

### 4. Update Camera

**Request:**
```bash
curl -X PUT "http://localhost:8000/api/cameras/1" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false,
    "detection_interval": 10
  }'
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Şantiye Giriş Kamerası",
  "rtsp_url": "rtsp://192.168.1.100:554/stream",
  "location": "Ana Giriş",
  "zone": "Bölge A",
  "status": "active",
  "enabled": false,
  "detection_interval": 10,
  "confidence_threshold": 0.7,
  "required_ppe": ["helmet", "vest"],
  "created_at": "2023-11-18T10:30:00",
  "updated_at": "2023-11-18T12:50:00",
  "last_seen": "2023-11-18T12:45:00"
}
```

### 5. Delete Camera

**Request:**
```bash
curl -X DELETE "http://localhost:8000/api/cameras/1"
```

**Response (204 No Content)**

---

## Detection

### 1. Run Detection on Image

**Request:**
```bash
curl -X POST "http://localhost:8000/api/detect" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@construction_site.jpg" \
  -F "camera_id=1" \
  -F "confidence_threshold=0.7" \
  -F "save_results=true"
```

**Python Example:**
```python
import requests

url = "http://localhost:8000/api/detect"

with open("construction_site.jpg", "rb") as f:
    files = {"file": f}
    data = {
        "camera_id": 1,
        "confidence_threshold": 0.7,
        "save_results": True
    }
    response = requests.post(url, files=files, data=data)

print(response.json())
```

**Response (200 OK):**
```json
{
  "detection_id": "det_20231118_124556_a3f2d8e1",
  "camera_id": 1,
  "timestamp": "2023-11-18T12:45:56",
  "image_path": "/data/detections/2023/11/18/det_20231118_124556_a3f2d8e1.jpg",
  "total_persons": 3,
  "compliant_persons": 2,
  "violation_count": 1,
  "persons": [
    {
      "person_id": 1,
      "bbox": {
        "x1": 120.5,
        "y1": 85.2,
        "x2": 245.8,
        "y2": 420.1
      },
      "confidence": 0.95,
      "detected_ppe": {
        "helmet": 0.98,
        "vest": 0.92
      },
      "missing_ppe": [],
      "is_compliant": true,
      "violations": []
    },
    {
      "person_id": 2,
      "bbox": {
        "x1": 320.0,
        "y1": 95.5,
        "x2": 445.2,
        "y2": 435.8
      },
      "confidence": 0.92,
      "detected_ppe": {
        "vest": 0.88
      },
      "missing_ppe": ["helmet"],
      "is_compliant": false,
      "violations": ["missing_helmet"]
    },
    {
      "person_id": 3,
      "bbox": {
        "x1": 500.0,
        "y1": 100.0,
        "x2": 625.0,
        "y2": 450.0
      },
      "confidence": 0.89,
      "detected_ppe": {
        "helmet": 0.94,
        "vest": 0.91
      },
      "missing_ppe": [],
      "is_compliant": true,
      "violations": []
    }
  ],
  "processing_time_ms": 245.6
}
```

---

## Violations

### 1. List All Violations

**Request:**
```bash
curl -X GET "http://localhost:8000/api/violations?limit=10&offset=0"
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "camera_id": 1,
    "camera_name": "Şantiye Giriş Kamerası",
    "location": "Ana Giriş",
    "detection_id": "det_20231118_124556_a3f2d8e1",
    "timestamp": "2023-11-18T12:45:56",
    "person_id": 2,
    "violation_types": ["missing_helmet"],
    "missing_ppe": ["helmet"],
    "confidence": 0.92,
    "image_path": "/data/detections/2023/11/18/det_20231118_124556_a3f2d8e1.jpg",
    "acknowledged": false,
    "acknowledged_by": null,
    "acknowledged_at": null,
    "notes": null
  }
]
```

### 2. Get Recent Violations (Last 24 Hours)

**Request:**
```bash
curl -X GET "http://localhost:8000/api/violations/recent?limit=50"
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "camera_id": 1,
    "camera_name": "Şantiye Giriş Kamerası",
    "location": "Ana Giriş",
    "detection_id": "det_20231118_124556_a3f2d8e1",
    "timestamp": "2023-11-18T12:45:56",
    "person_id": 2,
    "violation_types": ["missing_helmet"],
    "missing_ppe": ["helmet"],
    "confidence": 0.92,
    "image_path": "/data/detections/2023/11/18/det_20231118_124556_a3f2d8e1.jpg",
    "acknowledged": false,
    "acknowledged_by": null,
    "acknowledged_at": null,
    "notes": null
  },
  {
    "id": 2,
    "camera_id": 2,
    "camera_name": "İnşaat Alanı Kamerası",
    "location": "İnşaat Alanı",
    "detection_id": "det_20231118_113045_b7e4c2f9",
    "timestamp": "2023-11-18T11:30:45",
    "person_id": 1,
    "violation_types": ["missing_vest", "missing_boots"],
    "missing_ppe": ["vest", "boots"],
    "confidence": 0.87,
    "image_path": "/data/detections/2023/11/18/det_20231118_113045_b7e4c2f9.jpg",
    "acknowledged": true,
    "acknowledged_by": "Mehmet Demir",
    "acknowledged_at": "2023-11-18T11:45:00",
    "notes": "Çalışan uyarıldı, yelek verildi"
  }
]
```

### 3. Filter Violations

**Request:**
```bash
curl -X GET "http://localhost:8000/api/violations?camera_id=1&violation_type=missing_helmet&acknowledged=false"
```

### 4. Acknowledge Violation

**Request:**
```bash
curl -X POST "http://localhost:8000/api/violations/1/acknowledge" \
  -H "Content-Type: application/json" \
  -d '{
    "acknowledged_by": "Ahmet Yılmaz",
    "notes": "Çalışan uyarıldı, baret verildi"
  }'
```

**Response (200 OK):**
```json
{
  "id": 1,
  "camera_id": 1,
  "camera_name": "Şantiye Giriş Kamerası",
  "location": "Ana Giriş",
  "detection_id": "det_20231118_124556_a3f2d8e1",
  "timestamp": "2023-11-18T12:45:56",
  "person_id": 2,
  "violation_types": ["missing_helmet"],
  "missing_ppe": ["helmet"],
  "confidence": 0.92,
  "image_path": "/data/detections/2023/11/18/det_20231118_124556_a3f2d8e1.jpg",
  "acknowledged": true,
  "acknowledged_by": "Ahmet Yılmaz",
  "acknowledged_at": "2023-11-18T13:00:00",
  "notes": "Çalışan uyarıldı, baret verildi"
}
```

---

## Statistics

### 1. Get Overall Statistics

**Request:**
```bash
curl -X GET "http://localhost:8000/api/stats"
```

**Response (200 OK):**
```json
{
  "period_start": "2023-11-17T13:00:00",
  "period_end": "2023-11-18T13:00:00",
  "total_cameras": 5,
  "active_cameras": 4,
  "total_detections": 1250,
  "total_persons_detected": 3500,
  "total_violations": 45,
  "overall_compliance_rate": 98.7,
  "avg_processing_time_ms": 234.5,
  "camera_stats": [
    {
      "camera_id": 1,
      "camera_name": "Şantiye Giriş Kamerası",
      "total_detections": 450,
      "total_violations": 15,
      "violation_rate": 3.3,
      "avg_processing_time_ms": 245.0,
      "status": "active",
      "last_detection": "2023-11-18T12:55:00"
    },
    {
      "camera_id": 2,
      "camera_name": "İnşaat Alanı Kamerası",
      "total_detections": 380,
      "total_violations": 12,
      "violation_rate": 3.2,
      "avg_processing_time_ms": 230.0,
      "status": "active",
      "last_detection": "2023-11-18T12:50:00"
    }
  ],
  "ppe_stats": [
    {
      "ppe_type": "helmet",
      "total_detections": 3500,
      "violations": 25,
      "compliance_rate": 99.3
    },
    {
      "ppe_type": "vest",
      "total_detections": 3500,
      "violations": 20,
      "compliance_rate": 99.4
    }
  ],
  "violations_by_hour": {
    "0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 1,
    "6": 2, "7": 3, "8": 5, "9": 5, "10": 4, "11": 3,
    "12": 4, "13": 3, "14": 5, "15": 5, "16": 3, "17": 2,
    "18": 1, "19": 0, "20": 0, "21": 0, "22": 0, "23": 0
  },
  "violations_by_type": {
    "missing_helmet": 25,
    "missing_vest": 20
  }
}
```

### 2. Get Statistics for Date Range

**Request:**
```bash
curl -X GET "http://localhost:8000/api/stats?start_date=2023-11-01T00:00:00&end_date=2023-11-18T23:59:59"
```

---

## WebSocket Live Feed

### JavaScript Example

```javascript
const ws = new WebSocket("ws://localhost:8000/api/ws/live?camera_id=1");

ws.onopen = () => {
  console.log("WebSocket connected");
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log("Live update:", message);

  /*
  Example message:
  {
    "type": "detection",
    "camera_id": 1,
    "data": {
      "timestamp": "2023-11-18T12:45:56",
      "total_persons": 2,
      "violations": 0,
      "status": "active"
    },
    "timestamp": "2023-11-18T12:45:56"
  }
  */
};

ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};

ws.onclose = () => {
  console.log("WebSocket disconnected");
};
```

### Python Example

```python
import asyncio
import websockets
import json

async def connect_live_feed():
    uri = "ws://localhost:8000/api/ws/live?camera_id=1"

    async with websockets.connect(uri) as websocket:
        print("Connected to live feed")

        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Live update: {data}")

asyncio.run(connect_live_feed())
```

---

## Health & Status

### 1. Health Check

**Request:**
```bash
curl -X GET "http://localhost:8000/api/health"
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2023-11-18T13:00:00",
  "version": "0.1.0",
  "uptime_seconds": 3600.5,
  "database_connected": true,
  "model_loaded": true,
  "active_cameras": 4
}
```

### 2. Ping

**Request:**
```bash
curl -X GET "http://localhost:8000/ping"
```

**Response (200 OK):**
```json
{
  "status": "ok",
  "message": "pong"
}
```

### 3. Version

**Request:**
```bash
curl -X GET "http://localhost:8000/version"
```

**Response (200 OK):**
```json
{
  "version": "0.1.0",
  "app_name": "PPE Detection API"
}
```

---

## Error Responses

### 404 Not Found

```json
{
  "error": "Kamera bulunamadı",
  "detail": "ID 123 ile kamera kayıtlı değil",
  "timestamp": "2023-11-18T13:00:00",
  "path": "/api/cameras/123"
}
```

### 422 Validation Error

```json
{
  "error": "Geçersiz istek verisi",
  "detail": "body -> confidence_threshold: ensure this value is less than or equal to 1.0",
  "timestamp": "2023-11-18T13:00:00",
  "path": "/api/detect"
}
```

### 500 Internal Server Error

```json
{
  "error": "Sunucu hatası",
  "detail": "Beklenmeyen bir hata oluştu. Lütfen daha sonra tekrar deneyin.",
  "timestamp": "2023-11-18T13:00:00",
  "path": "/api/detect"
}
```

---

## Environment Variables

Create a `.env` file in the project root:

```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///./ppe_detection.db
SQL_ECHO=false

# API Configuration
DEBUG=false
MAX_UPLOAD_SIZE_MB=10
DETECTION_TIMEOUT=30
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Model
MODEL_PATH=models/ppe_detector.pt

# Storage
SAVE_DETECTIONS=true
DETECTION_IMAGE_DIR=data/detections

# Authentication (optional)
API_KEY_REQUIRED=false
API_KEY=your-secret-api-key-here

# Monitoring
LOG_LEVEL=INFO
PROMETHEUS_PORT=9090
```

---

## Rate Limiting

The API implements basic rate limiting:
- Default: 60 requests per minute per client
- Exceeded requests return 429 Too Many Requests

**Response (429):**
```json
{
  "error": "Çok fazla istek. Lütfen daha sonra tekrar deneyin.",
  "detail": null,
  "timestamp": "2023-11-18T13:00:00",
  "path": "/api/detect"
}
```

**Headers:**
```
Retry-After: 60
```
