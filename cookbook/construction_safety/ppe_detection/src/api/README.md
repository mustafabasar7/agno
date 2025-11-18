# PPE Detection API

FastAPI-based REST API for Personal Protective Equipment (PPE) detection in construction sites.

## Overview

This API provides endpoints for:
- **Camera Management**: Add, update, and monitor RTSP cameras
- **Real-time Detection**: Run PPE detection on images and video streams
- **Violation Tracking**: Record and manage safety violations
- **Statistics & Analytics**: Generate compliance reports and statistics
- **Live Feed**: WebSocket support for real-time updates

## Features

✅ **Async/Await**: Full async support for high performance
✅ **Type Safety**: Pydantic models for request/response validation
✅ **Error Handling**: Comprehensive error handling with Turkish messages
✅ **CORS Support**: Configurable CORS for frontend integration
✅ **Rate Limiting**: Built-in rate limiting for API protection
✅ **WebSocket**: Live detection feed via WebSocket
✅ **Health Checks**: System health monitoring endpoints
✅ **API Documentation**: Auto-generated Swagger UI and ReDoc
✅ **Middleware**: Request logging, compression, and metrics
✅ **Turkish Language**: Full Turkish language support in responses

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or if using the project as a package
pip install -e .
```

### 2. Configuration

Create a `.env` file (see `.env.example`):

```bash
cp .env.example .env
```

Key configuration:

```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///./ppe_detection.db

# API
DEBUG=false
CORS_ORIGINS=http://localhost:3000

# Model
MODEL_PATH=models/ppe_detector.pt
```

### 3. Run the Server

**Option 1: Using the run script**

```bash
# Development mode (with auto-reload)
python run_api.py --reload

# Production mode
python run_api.py --production --workers 4
```

**Option 2: Using uvicorn directly**

```bash
# Development
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Access the API

- API Root: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/api/docs
- API Docs (ReDoc): http://localhost:8000/api/redoc
- Health Check: http://localhost:8000/api/health

## API Structure

```
src/api/
├── __init__.py          # Module exports
├── main.py              # FastAPI application & middleware
├── endpoints.py         # API route handlers
├── schemas.py           # Pydantic models
├── dependencies.py      # Dependency injection
├── API_EXAMPLES.md      # API usage examples
└── README.md            # This file
```

## API Endpoints

### Camera Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/cameras` | Create new camera |
| GET | `/api/cameras` | List all cameras |
| GET | `/api/cameras/{id}` | Get camera details |
| PUT | `/api/cameras/{id}` | Update camera |
| DELETE | `/api/cameras/{id}` | Delete camera |

### Detection

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/detect` | Run detection on image |

### Violations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/violations` | List violations with filters |
| GET | `/api/violations/recent` | Get last 24 hours violations |
| GET | `/api/violations/{id}` | Get violation details |
| POST | `/api/violations/{id}/acknowledge` | Acknowledge violation |

### Statistics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats` | Get system statistics |

### Live Feed

| Protocol | Endpoint | Description |
|----------|----------|-------------|
| WebSocket | `/api/ws/live` | Live detection feed |

### Health & Info

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/ping` | Simple ping |
| GET | `/version` | API version |

## Usage Examples

See [API_EXAMPLES.md](./API_EXAMPLES.md) for detailed examples including:
- Camera CRUD operations
- Image detection requests
- Violation management
- Statistics queries
- WebSocket connections
- Error handling

### Quick Example: Run Detection

**Python:**

```python
import requests

url = "http://localhost:8000/api/detect"

with open("construction_site.jpg", "rb") as f:
    files = {"file": f}
    data = {"camera_id": 1, "confidence_threshold": 0.7}
    response = requests.post(url, files=files, data=data)

result = response.json()
print(f"Detected {result['total_persons']} persons")
print(f"Violations: {result['violation_count']}")
```

**cURL:**

```bash
curl -X POST "http://localhost:8000/api/detect" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@construction_site.jpg" \
  -F "camera_id=1" \
  -F "confidence_threshold=0.7"
```

## Data Models

### Camera Configuration

```python
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

### Detection Result

```python
{
  "detection_id": "det_20231118_124556",
  "camera_id": 1,
  "timestamp": "2023-11-18T12:45:56",
  "total_persons": 3,
  "compliant_persons": 2,
  "violation_count": 1,
  "processing_time_ms": 245.6,
  "persons": [...]
}
```

### Violation Record

```python
{
  "id": 1,
  "camera_id": 1,
  "camera_name": "Şantiye Giriş Kamerası",
  "location": "Ana Giriş",
  "detection_id": "det_20231118_124556",
  "timestamp": "2023-11-18T12:45:56",
  "violation_types": ["missing_helmet"],
  "missing_ppe": ["helmet"],
  "confidence": 0.95,
  "acknowledged": false
}
```

## Middleware & Features

### CORS Configuration

Configure allowed origins in `.env`:

```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

Or use `*` for development (not recommended for production).

### Request Logging

All requests are automatically logged with:
- HTTP method and path
- Status code
- Processing duration
- Custom headers (X-Process-Time, X-Request-ID)

### Error Handling

All errors return standardized JSON responses:

```json
{
  "error": "Kamera bulunamadı",
  "detail": "ID 123 ile kamera kayıtlı değil",
  "timestamp": "2023-11-18T13:00:00",
  "path": "/api/cameras/123"
}
```

### Rate Limiting

Default: 60 requests per minute per client

Exceeded requests return HTTP 429 with `Retry-After` header.

### GZip Compression

Responses larger than 1KB are automatically compressed.

## Authentication

API key authentication is implemented but disabled by default.

To enable:

```bash
# In .env
API_KEY_REQUIRED=true
API_KEY=your-secret-api-key-here
```

Include in requests:

```bash
curl -H "X-API-Key: your-secret-api-key-here" http://localhost:8000/api/cameras
```

## Database

### SQLite (Default)

```bash
DATABASE_URL=sqlite+aiosqlite:///./ppe_detection.db
```

### PostgreSQL (Production)

```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ppe_detection
```

### Migrations

Using Alembic:

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Monitoring

### Health Checks

```bash
curl http://localhost:8000/api/health
```

Returns:
- API status (healthy/degraded/unhealthy)
- Database connection status
- Model load status
- Active camera count
- Uptime

### Prometheus Metrics

Enable in `.env`:

```bash
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
```

Metrics available at: http://localhost:9090/metrics

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src.api --cov-report=html

# Run specific test file
pytest tests/api/test_endpoints.py

# Run async tests
pytest -v tests/api/test_async_endpoints.py
```

## Performance

### Optimization Tips

1. **Use async everywhere**: All database queries are async
2. **Enable workers**: Use multiple workers in production
3. **Cache responses**: Implement Redis caching for stats
4. **Database connection pooling**: Configure pool size appropriately
5. **Image optimization**: Resize images before detection

### Benchmarks

Typical performance on modern hardware:

- **Detection latency**: 200-300ms per image
- **API throughput**: 100+ requests/second
- **WebSocket connections**: 100+ concurrent

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/ppe
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: password
```

### Production Checklist

- [ ] Set `DEBUG=false`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure proper CORS origins
- [ ] Enable API key authentication
- [ ] Set up HTTPS/TLS
- [ ] Configure rate limiting
- [ ] Enable monitoring (Prometheus/Grafana)
- [ ] Set up logging aggregation
- [ ] Configure database backups
- [ ] Set up auto-scaling
- [ ] Configure health checks

## Troubleshooting

### Common Issues

**1. Model not loading**

Check model path in `.env`:
```bash
MODEL_PATH=models/ppe_detector.pt
```

**2. Database connection errors**

Verify database URL format:
```bash
# SQLite
DATABASE_URL=sqlite+aiosqlite:///./ppe_detection.db

# PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
```

**3. CORS errors**

Add your frontend origin to `.env`:
```bash
CORS_ORIGINS=http://localhost:3000
```

**4. File upload too large**

Increase max upload size:
```bash
MAX_UPLOAD_SIZE_MB=20
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [Link to issues]
- Documentation: [Link to docs]
- Email: support@example.com
