# PPE Detection API Documentation

Complete REST API reference for the PPE Detection System.

## Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Request/Response Format](#requestresponse-format)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Endpoints](#endpoints)
  - [Health & Status](#health--status)
  - [Camera Management](#camera-management)
  - [Detection](#detection)
  - [Violations](#violations)
  - [Statistics](#statistics)
  - [WebSocket](#websocket)
- [Code Examples](#code-examples)
- [Postman Collection](#postman-collection)

---

## Overview

The PPE Detection API is a RESTful API built with FastAPI that provides:

- Real-time PPE detection on images and video streams
- Multi-camera management
- Violation tracking and reporting
- Comprehensive analytics and statistics
- Real-time updates via WebSocket

**API Version**: 0.1.0
**Protocol**: HTTP/HTTPS
**Format**: JSON
**Documentation**: Interactive docs available at `/docs`

---

## Base URL

### Development
```
http://localhost:8000
```

### Production
```
https://your-domain.com
```

### Docker
```
http://localhost:8000  # Direct to app
http://localhost:80    # Through Nginx
```

---

## Authentication

### Current Version (0.1.0)

**Status**: No authentication required (MVP)

Future versions will support:
- API Key authentication
- JWT tokens
- OAuth 2.0

### Future Implementation (v0.2.0+)

**API Key Header:**
```http
X-API-Key: your_api_key_here
```

**Bearer Token:**
```http
Authorization: Bearer <jwt_token>
```

---

## Request/Response Format

### Content Types

**Request:**
- `application/json` - JSON data
- `multipart/form-data` - File uploads

**Response:**
- `application/json` - All responses

### Common Headers

```http
Content-Type: application/json
Accept: application/json
```

### Standard Response Structure

**Success Response:**
```json
{
  "id": 1,
  "name": "Resource name",
  "created_at": "2024-11-18T12:34:56",
  ...
}
```

**List Response:**
```json
[
  {
    "id": 1,
    ...
  },
  {
    "id": 2,
    ...
  }
]
```

**Error Response:**
```json
{
  "error": "Error message",
  "detail": "Detailed error description",
  "timestamp": "2024-11-18T12:34:56",
  "path": "/api/endpoint"
}
```

---

## Error Handling

### HTTP Status Codes

| Status Code | Meaning | Description |
|-------------|---------|-------------|
| **200** | OK | Request successful |
| **201** | Created | Resource created successfully |
| **204** | No Content | Resource deleted successfully |
| **400** | Bad Request | Invalid request parameters |
| **404** | Not Found | Resource not found |
| **413** | Payload Too Large | File size exceeds limit |
| **422** | Unprocessable Entity | Validation error |
| **500** | Internal Server Error | Server error |
| **503** | Service Unavailable | Service temporarily unavailable |

### Error Response Examples

**404 Not Found:**
```json
{
  "error": "Kamera bulunamadı",
  "detail": "ID 123 ile kamera kayıtlı değil",
  "timestamp": "2024-11-18T12:34:56",
  "path": "/api/cameras/123"
}
```

**400 Bad Request:**
```json
{
  "error": "Desteklenmeyen dosya tipi",
  "detail": "Desteklenmeyen dosya tipi: application/pdf. İzin verilen tipler: image/jpeg, image/png",
  "timestamp": "2024-11-18T12:34:56",
  "path": "/api/detect"
}
```

**422 Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "confidence_threshold"],
      "msg": "ensure this value is less than or equal to 1.0",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

## Rate Limiting

### Current Limits (v0.1.0)

**Status**: Not implemented in MVP

### Future Limits (v0.2.0+)

| Endpoint Type | Rate Limit |
|---------------|------------|
| Detection API | 60 requests/minute |
| Query APIs | 100 requests/minute |
| WebSocket | 10 connections/IP |

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1700312400
```

---

## Endpoints

### Health & Status

#### GET /health

Check system health and status.

**Request:**
```http
GET /health HTTP/1.1
Host: localhost:8000
```

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2024-11-18T12:34:56",
  "version": "0.1.0",
  "uptime_seconds": 3600.5,
  "database_connected": true,
  "model_loaded": true,
  "active_cameras": 4
}
```

**Status Values:**
- `healthy` - All systems operational
- `degraded` - Some systems have issues
- `unhealthy` - Critical systems down

**Example:**
```bash
curl http://localhost:8000/health
```

---

### Camera Management

#### GET /api/cameras

List all cameras.

**Query Parameters:**
- `enabled_only` (boolean, optional) - Filter for enabled cameras only
  - Default: `false`

**Request:**
```http
GET /api/cameras?enabled_only=true HTTP/1.1
Host: localhost:8000
```

**Response:** `200 OK`
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
    "created_at": "2024-11-18T10:00:00",
    "updated_at": "2024-11-18T12:00:00",
    "last_seen": "2024-11-18T12:34:56"
  }
]
```

**Example:**
```bash
curl "http://localhost:8000/api/cameras?enabled_only=true"
```

---

#### GET /api/cameras/{camera_id}

Get camera details by ID.

**Path Parameters:**
- `camera_id` (integer, required) - Camera ID

**Request:**
```http
GET /api/cameras/1 HTTP/1.1
Host: localhost:8000
```

**Response:** `200 OK`
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
  "created_at": "2024-11-18T10:00:00",
  "updated_at": "2024-11-18T12:00:00",
  "last_seen": "2024-11-18T12:34:56"
}
```

**Response:** `404 Not Found`
```json
{
  "error": "Kamera bulunamadı",
  "detail": "ID 999 ile kamera kayıtlı değil"
}
```

**Example:**
```bash
curl http://localhost:8000/api/cameras/1
```

---

#### POST /api/cameras

Create a new camera.

**Request Body:**
```json
{
  "name": "Şantiye Giriş Kamerası",
  "rtsp_url": "rtsp://192.168.1.100:554/stream",
  "location": "Ana Giriş",
  "zone": "Bölge A",
  "enabled": true,
  "detection_interval": 5,
  "confidence_threshold": 0.7,
  "required_ppe": ["helmet", "vest"]
}
```

**Field Descriptions:**
- `name` (string, required) - Camera name (1-100 characters)
- `rtsp_url` (string, required) - RTSP stream URL
- `location` (string, required) - Physical location (1-200 characters)
- `zone` (string, optional) - Zone/area name (max 50 characters)
- `enabled` (boolean, optional) - Enable camera (default: true)
- `detection_interval` (integer, optional) - Detection interval in seconds (1-60, default: 5)
- `confidence_threshold` (float, optional) - Confidence threshold (0.0-1.0, default: 0.5)
- `required_ppe` (array, optional) - Required PPE items (default: ["helmet", "vest"])

**PPE Types:**
- `helmet` - Safety helmet/hard hat
- `vest` - High-visibility safety vest
- `gloves` - Safety gloves
- `boots` - Safety boots
- `goggles` - Safety goggles
- `mask` - Face mask

**Response:** `201 Created`
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
  "created_at": "2024-11-18T12:34:56",
  "updated_at": "2024-11-18T12:34:56",
  "last_seen": "2024-11-18T12:34:56"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/cameras" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Main Entrance Camera",
    "rtsp_url": "rtsp://admin:password@192.168.1.100:554/stream",
    "location": "Main Entrance",
    "zone": "Zone A",
    "detection_interval": 5,
    "confidence_threshold": 0.7,
    "required_ppe": ["helmet", "vest"]
  }'
```

---

#### PUT /api/cameras/{camera_id}

Update camera configuration.

**Path Parameters:**
- `camera_id` (integer, required) - Camera ID

**Request Body:** (all fields optional)
```json
{
  "name": "Updated Camera Name",
  "enabled": false,
  "detection_interval": 10,
  "confidence_threshold": 0.8
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Updated Camera Name",
  "rtsp_url": "rtsp://192.168.1.100:554/stream",
  "location": "Ana Giriş",
  "zone": "Bölge A",
  "status": "active",
  "enabled": false,
  "detection_interval": 10,
  "confidence_threshold": 0.8,
  "required_ppe": ["helmet", "vest"],
  "created_at": "2024-11-18T10:00:00",
  "updated_at": "2024-11-18T12:45:00",
  "last_seen": "2024-11-18T12:34:56"
}
```

**Example:**
```bash
curl -X PUT "http://localhost:8000/api/cameras/1" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false,
    "detection_interval": 10
  }'
```

---

#### DELETE /api/cameras/{camera_id}

Delete a camera.

**Path Parameters:**
- `camera_id` (integer, required) - Camera ID

**Request:**
```http
DELETE /api/cameras/1 HTTP/1.1
Host: localhost:8000
```

**Response:** `204 No Content`

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/cameras/1"
```

---

### Detection

#### POST /api/detect

Run PPE detection on uploaded image.

**Request:**
```http
POST /api/detect HTTP/1.1
Host: localhost:8000
Content-Type: multipart/form-data
```

**Form Data:**
- `file` (file, required) - Image file (JPEG, PNG)
- `camera_id` (integer, optional) - Camera ID
- `confidence_threshold` (float, optional) - Override confidence threshold (0.0-1.0)
- `required_ppe` (array, optional) - Override required PPE list
- `save_results` (boolean, optional) - Save detection results (default: true)

**Supported Image Types:**
- `image/jpeg`
- `image/png`

**File Size Limits:**
- Maximum: 10 MB (configurable via `MAX_IMAGE_SIZE_MB`)

**Response:** `200 OK`
```json
{
  "detection_id": "det_20241118_123456_abc123",
  "camera_id": 1,
  "timestamp": "2024-11-18T12:34:56",
  "image_path": "/data/detections/2024/11/18/det_20241118_123456_abc123.jpg",
  "total_persons": 3,
  "compliant_persons": 2,
  "violation_count": 1,
  "persons": [
    {
      "person_id": 1,
      "bbox": {
        "x1": 100.5,
        "y1": 150.2,
        "x2": 300.8,
        "y2": 450.6
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
        "x1": 350.0,
        "y1": 200.0,
        "x2": 550.0,
        "y2": 500.0
      },
      "confidence": 0.89,
      "detected_ppe": {
        "vest": 0.85
      },
      "missing_ppe": ["helmet"],
      "is_compliant": false,
      "violations": ["missing_helmet"]
    }
  ],
  "processing_time_ms": 234.5
}
```

**Example:**
```bash
# Basic detection
curl -X POST "http://localhost:8000/api/detect" \
  -F "file=@worker.jpg"

# With custom threshold
curl -X POST "http://localhost:8000/api/detect" \
  -F "file=@worker.jpg" \
  -F "confidence_threshold=0.8"

# With camera association
curl -X POST "http://localhost:8000/api/detect" \
  -F "file=@worker.jpg" \
  -F "camera_id=1"
```

**Python Example:**
```python
import httpx

with open('worker.jpg', 'rb') as f:
    response = httpx.post(
        'http://localhost:8000/api/detect',
        files={'file': f},
        data={'confidence_threshold': 0.7}
    )

result = response.json()
print(f"Detected {result['total_persons']} persons")
print(f"Violations: {result['violation_count']}")
```

---

### Violations

#### GET /api/violations

List violations with filters.

**Query Parameters:**
- `camera_id` (integer, optional) - Filter by camera ID
- `start_date` (datetime, optional) - Filter by start date (ISO 8601)
- `end_date` (datetime, optional) - Filter by end date (ISO 8601)
- `violation_type` (string, optional) - Filter by violation type
- `acknowledged` (boolean, optional) - Filter by acknowledgment status
- `limit` (integer, optional) - Maximum records (1-1000, default: 100)
- `offset` (integer, optional) - Records to skip (default: 0)

**Violation Types:**
- `missing_helmet`
- `missing_vest`
- `missing_gloves`
- `missing_boots`
- `missing_goggles`
- `missing_mask`
- `multiple_violations`

**Request:**
```http
GET /api/violations?camera_id=1&acknowledged=false&limit=10 HTTP/1.1
Host: localhost:8000
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "camera_id": 1,
    "camera_name": "Şantiye Giriş Kamerası",
    "location": "Ana Giriş",
    "detection_id": "det_20241118_123456",
    "timestamp": "2024-11-18T10:34:56",
    "person_id": 1,
    "violation_types": ["missing_helmet"],
    "missing_ppe": ["helmet"],
    "confidence": 0.95,
    "image_path": "/data/detections/2024/11/18/det_20241118_123456.jpg",
    "acknowledged": false,
    "acknowledged_by": null,
    "acknowledged_at": null,
    "notes": null
  }
]
```

**Example:**
```bash
# Get recent unacknowledged violations
curl "http://localhost:8000/api/violations?acknowledged=false&limit=20"

# Get violations for specific camera
curl "http://localhost:8000/api/violations?camera_id=1"

# Get violations in date range
curl "http://localhost:8000/api/violations?start_date=2024-11-01T00:00:00&end_date=2024-11-30T23:59:59"
```

---

#### GET /api/violations/recent

Get violations from last 24 hours.

**Query Parameters:**
- `limit` (integer, optional) - Maximum records (1-1000, default: 100)

**Request:**
```http
GET /api/violations/recent?limit=50 HTTP/1.1
Host: localhost:8000
```

**Response:** `200 OK` (same format as `/api/violations`)

**Example:**
```bash
curl "http://localhost:8000/api/violations/recent?limit=50"
```

---

#### GET /api/violations/{violation_id}

Get violation details by ID.

**Path Parameters:**
- `violation_id` (integer, required) - Violation ID

**Request:**
```http
GET /api/violations/1 HTTP/1.1
Host: localhost:8000
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "camera_id": 1,
  "camera_name": "Şantiye Giriş Kamerası",
  "location": "Ana Giriş",
  "detection_id": "det_20241118_123456",
  "timestamp": "2024-11-18T10:34:56",
  "person_id": 1,
  "violation_types": ["missing_helmet"],
  "missing_ppe": ["helmet"],
  "confidence": 0.95,
  "image_path": "/data/detections/2024/11/18/det_20241118_123456.jpg",
  "acknowledged": false,
  "acknowledged_by": null,
  "acknowledged_at": null,
  "notes": null
}
```

**Example:**
```bash
curl http://localhost:8000/api/violations/1
```

---

#### POST /api/violations/{violation_id}/acknowledge

Acknowledge a violation.

**Path Parameters:**
- `violation_id` (integer, required) - Violation ID

**Request Body:**
```json
{
  "acknowledged_by": "Ahmet Yılmaz",
  "notes": "Çalışan uyarıldı, baret verildi"
}
```

**Field Descriptions:**
- `acknowledged_by` (string, required) - Person who acknowledged (1-100 characters)
- `notes` (string, optional) - Additional notes (max 500 characters)

**Response:** `200 OK`
```json
{
  "id": 1,
  "camera_id": 1,
  "camera_name": "Şantiye Giriş Kamerası",
  "location": "Ana Giriş",
  "detection_id": "det_20241118_123456",
  "timestamp": "2024-11-18T10:34:56",
  "person_id": 1,
  "violation_types": ["missing_helmet"],
  "missing_ppe": ["helmet"],
  "confidence": 0.95,
  "image_path": "/data/detections/2024/11/18/det_20241118_123456.jpg",
  "acknowledged": true,
  "acknowledged_by": "Ahmet Yılmaz",
  "acknowledged_at": "2024-11-18T12:45:00",
  "notes": "Çalışan uyarıldı, baret verildi"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/violations/1/acknowledge" \
  -H "Content-Type: application/json" \
  -d '{
    "acknowledged_by": "Ahmet Yılmaz",
    "notes": "Worker warned and provided helmet"
  }'
```

---

### Statistics

#### GET /api/stats

Get system statistics.

**Query Parameters:**
- `start_date` (datetime, optional) - Start date for statistics (default: 24 hours ago)
- `end_date` (datetime, optional) - End date for statistics (default: now)

**Request:**
```http
GET /api/stats?start_date=2024-11-01T00:00:00&end_date=2024-11-30T23:59:59 HTTP/1.1
Host: localhost:8000
```

**Response:** `200 OK`
```json
{
  "period_start": "2024-11-01T00:00:00",
  "period_end": "2024-11-30T23:59:59",
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
      "last_detection": "2024-11-18T12:30:00"
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
    "0": 1,
    "1": 0,
    "2": 0,
    "8": 5,
    "9": 5,
    "14": 5,
    "15": 5
  },
  "violations_by_type": {
    "missing_helmet": 25,
    "missing_vest": 20
  }
}
```

**Example:**
```bash
# Last 24 hours (default)
curl http://localhost:8000/api/stats

# Custom date range
curl "http://localhost:8000/api/stats?start_date=2024-11-01T00:00:00&end_date=2024-11-30T23:59:59"
```

---

### WebSocket

#### WS /api/ws/live

Real-time detection updates via WebSocket.

**Query Parameters:**
- `camera_id` (integer, optional) - Filter updates for specific camera

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/live?camera_id=1');

ws.onopen = () => {
    console.log('Connected to live feed');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Detection update:', data);
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

ws.onclose = () => {
    console.log('Disconnected from live feed');
};
```

**Message Format:**
```json
{
  "type": "detection",
  "camera_id": 1,
  "data": {
    "timestamp": "2024-11-18T12:34:56",
    "total_persons": 2,
    "violations": 0,
    "status": "active"
  },
  "timestamp": "2024-11-18T12:34:56"
}
```

**Message Types:**
- `detection` - New detection result
- `status` - Camera status update
- `error` - Error message

**Python Example:**
```python
import asyncio
import websockets
import json

async def connect():
    uri = "ws://localhost:8000/api/ws/live?camera_id=1"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received: {data}")

asyncio.run(connect())
```

---

## Code Examples

### Python - httpx

```python
import httpx
from datetime import datetime, timedelta

# Base URL
base_url = "http://localhost:8000"

# Health check
def check_health():
    response = httpx.get(f"{base_url}/health")
    return response.json()

# List cameras
def list_cameras():
    response = httpx.get(f"{base_url}/api/cameras")
    return response.json()

# Add camera
def add_camera(name, rtsp_url, location):
    camera_data = {
        "name": name,
        "rtsp_url": rtsp_url,
        "location": location,
        "detection_interval": 5,
        "confidence_threshold": 0.7,
        "required_ppe": ["helmet", "vest"]
    }
    response = httpx.post(f"{base_url}/api/cameras", json=camera_data)
    return response.json()

# Detect PPE in image
def detect_ppe(image_path):
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = httpx.post(f"{base_url}/api/detect", files=files)
    return response.json()

# Get recent violations
def get_recent_violations(limit=100):
    params = {"limit": limit, "acknowledged": False}
    response = httpx.get(f"{base_url}/api/violations/recent", params=params)
    return response.json()

# Acknowledge violation
def acknowledge_violation(violation_id, acknowledged_by, notes=""):
    ack_data = {
        "acknowledged_by": acknowledged_by,
        "notes": notes
    }
    response = httpx.post(
        f"{base_url}/api/violations/{violation_id}/acknowledge",
        json=ack_data
    )
    return response.json()

# Get statistics
def get_stats(days=7):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }
    response = httpx.get(f"{base_url}/api/stats", params=params)
    return response.json()

# Example usage
if __name__ == "__main__":
    # Check system health
    health = check_health()
    print(f"System status: {health['status']}")

    # List all cameras
    cameras = list_cameras()
    print(f"Total cameras: {len(cameras)}")

    # Run detection
    result = detect_ppe("worker.jpg")
    print(f"Detected {result['total_persons']} persons, {result['violation_count']} violations")

    # Get statistics
    stats = get_stats(days=30)
    print(f"Compliance rate: {stats['overall_compliance_rate']}%")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const BASE_URL = 'http://localhost:8000';

// Health check
async function checkHealth() {
    const response = await axios.get(`${BASE_URL}/health`);
    return response.data;
}

// List cameras
async function listCameras() {
    const response = await axios.get(`${BASE_URL}/api/cameras`);
    return response.data;
}

// Add camera
async function addCamera(name, rtspUrl, location) {
    const cameraData = {
        name: name,
        rtsp_url: rtspUrl,
        location: location,
        detection_interval: 5,
        confidence_threshold: 0.7,
        required_ppe: ['helmet', 'vest']
    };
    const response = await axios.post(`${BASE_URL}/api/cameras`, cameraData);
    return response.data;
}

// Detect PPE in image
async function detectPPE(imagePath) {
    const form = new FormData();
    form.append('file', fs.createReadStream(imagePath));

    const response = await axios.post(`${BASE_URL}/api/detect`, form, {
        headers: form.getHeaders()
    });
    return response.data;
}

// Get recent violations
async function getRecentViolations(limit = 100) {
    const response = await axios.get(`${BASE_URL}/api/violations/recent`, {
        params: { limit, acknowledged: false }
    });
    return response.data;
}

// Get statistics
async function getStats(days = 7) {
    const endDate = new Date();
    const startDate = new Date(endDate.getTime() - days * 24 * 60 * 60 * 1000);

    const response = await axios.get(`${BASE_URL}/api/stats`, {
        params: {
            start_date: startDate.toISOString(),
            end_date: endDate.toISOString()
        }
    });
    return response.data;
}

// Example usage
(async () => {
    try {
        // Check health
        const health = await checkHealth();
        console.log(`System status: ${health.status}`);

        // List cameras
        const cameras = await listCameras();
        console.log(`Total cameras: ${cameras.length}`);

        // Run detection
        const result = await detectPPE('worker.jpg');
        console.log(`Detected ${result.total_persons} persons, ${result.violation_count} violations`);

        // Get stats
        const stats = await getStats(30);
        console.log(`Compliance rate: ${stats.overall_compliance_rate}%`);
    } catch (error) {
        console.error('Error:', error.message);
    }
})();
```

### cURL Examples

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

# Health check
curl -X GET "$BASE_URL/health"

# List cameras
curl -X GET "$BASE_URL/api/cameras"

# Add camera
curl -X POST "$BASE_URL/api/cameras" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Main Entrance",
    "rtsp_url": "rtsp://192.168.1.100:554/stream",
    "location": "Main Entrance",
    "detection_interval": 5,
    "confidence_threshold": 0.7,
    "required_ppe": ["helmet", "vest"]
  }'

# Update camera
curl -X PUT "$BASE_URL/api/cameras/1" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false
  }'

# Delete camera
curl -X DELETE "$BASE_URL/api/cameras/1"

# Detect PPE
curl -X POST "$BASE_URL/api/detect" \
  -F "file=@worker.jpg" \
  -F "confidence_threshold=0.7"

# List violations
curl -X GET "$BASE_URL/api/violations?acknowledged=false&limit=20"

# Get violation details
curl -X GET "$BASE_URL/api/violations/1"

# Acknowledge violation
curl -X POST "$BASE_URL/api/violations/1/acknowledge" \
  -H "Content-Type: application/json" \
  -d '{
    "acknowledged_by": "John Doe",
    "notes": "Worker provided with helmet"
  }'

# Get statistics
curl -X GET "$BASE_URL/api/stats?start_date=2024-11-01T00:00:00&end_date=2024-11-30T23:59:59"
```

---

## Postman Collection

### Import Collection

Create a new Postman collection with these requests:

**Collection Structure:**
```
PPE Detection API
├── Health
│   └── GET Health Check
├── Cameras
│   ├── GET List Cameras
│   ├── GET Get Camera
│   ├── POST Create Camera
│   ├── PUT Update Camera
│   └── DELETE Delete Camera
├── Detection
│   └── POST Detect PPE
├── Violations
│   ├── GET List Violations
│   ├── GET Recent Violations
│   ├── GET Get Violation
│   └── POST Acknowledge Violation
└── Statistics
    └── GET Get Stats
```

### Environment Variables

```json
{
  "name": "PPE Detection - Local",
  "values": [
    {
      "key": "base_url",
      "value": "http://localhost:8000",
      "enabled": true
    },
    {
      "key": "api_key",
      "value": "your_api_key_here",
      "enabled": false
    }
  ]
}
```

### Download Collection

**JSON Export:**

Save as `PPE_Detection_API.postman_collection.json`:

```json
{
  "info": {
    "name": "PPE Detection API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health",
      "item": [
        {
          "name": "Health Check",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}/health",
              "host": ["{{base_url}}"],
              "path": ["health"]
            }
          }
        }
      ]
    },
    {
      "name": "Cameras",
      "item": [
        {
          "name": "List Cameras",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}/api/cameras",
              "host": ["{{base_url}}"],
              "path": ["api", "cameras"]
            }
          }
        },
        {
          "name": "Create Camera",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"name\": \"Main Entrance Camera\",\n  \"rtsp_url\": \"rtsp://192.168.1.100:554/stream\",\n  \"location\": \"Main Entrance\",\n  \"zone\": \"Zone A\",\n  \"detection_interval\": 5,\n  \"confidence_threshold\": 0.7,\n  \"required_ppe\": [\"helmet\", \"vest\"]\n}"
            },
            "url": {
              "raw": "{{base_url}}/api/cameras",
              "host": ["{{base_url}}"],
              "path": ["api", "cameras"]
            }
          }
        }
      ]
    }
  ]
}
```

---

## Interactive Documentation

### Swagger UI

Access interactive API documentation:

**URL:** `http://localhost:8000/docs`

Features:
- Try out endpoints directly
- View request/response schemas
- See example values
- Test authentication

### ReDoc

Alternative documentation interface:

**URL:** `http://localhost:8000/redoc`

Features:
- Clean, searchable interface
- Detailed schema documentation
- Code samples
- Markdown support

---

## Support

For API support:
- 📧 Email: api-support@ppe-detection.local
- 💬 Discord: [Join community](https://discord.gg/ppe-detection)
- 📖 Docs: [Full documentation](https://docs.ppe-detection.local)
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/ppe-detection/issues)
