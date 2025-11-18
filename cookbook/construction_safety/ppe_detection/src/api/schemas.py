"""
Pydantic schemas for API request/response validation.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator


class CameraStatus(str, Enum):
    """Camera status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    OFFLINE = "offline"


class PPEType(str, Enum):
    """PPE equipment types."""
    HELMET = "helmet"
    VEST = "vest"
    GLOVES = "gloves"
    BOOTS = "boots"
    GOGGLES = "goggles"
    MASK = "mask"


class ViolationType(str, Enum):
    """Violation types."""
    MISSING_HELMET = "missing_helmet"
    MISSING_VEST = "missing_vest"
    MISSING_GLOVES = "missing_gloves"
    MISSING_BOOTS = "missing_boots"
    MISSING_GOGGLES = "missing_goggles"
    MISSING_MASK = "missing_mask"
    MULTIPLE_VIOLATIONS = "multiple_violations"


# Camera Management Schemas
class CameraConfigCreate(BaseModel):
    """Schema for creating a new camera configuration."""
    name: str = Field(..., min_length=1, max_length=100, description="Kamera adı")
    rtsp_url: str = Field(..., description="RTSP stream URL'si")
    location: str = Field(..., min_length=1, max_length=200, description="Kamera konumu")
    zone: Optional[str] = Field(None, max_length=50, description="Bölge/alan adı")
    enabled: bool = Field(True, description="Kamera aktif mi?")
    detection_interval: int = Field(
        5, ge=1, le=60, description="Tespit aralığı (saniye)"
    )
    confidence_threshold: float = Field(
        0.5, ge=0.0, le=1.0, description="Güven eşik değeri"
    )
    required_ppe: List[PPEType] = Field(
        default_factory=lambda: [PPEType.HELMET, PPEType.VEST],
        description="Zorunlu KKD listesi"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Şantiye Giriş Kamerası",
                "rtsp_url": "rtsp://192.168.1.100:554/stream",
                "location": "Ana Giriş",
                "zone": "Bölge A",
                "enabled": True,
                "detection_interval": 5,
                "confidence_threshold": 0.7,
                "required_ppe": ["helmet", "vest"]
            }
        }
    )


class CameraConfigUpdate(BaseModel):
    """Schema for updating camera configuration."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    rtsp_url: Optional[str] = None
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    zone: Optional[str] = Field(None, max_length=50)
    enabled: Optional[bool] = None
    detection_interval: Optional[int] = Field(None, ge=1, le=60)
    confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    required_ppe: Optional[List[PPEType]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "enabled": False,
                "detection_interval": 10
            }
        }
    )


class CameraConfig(BaseModel):
    """Schema for camera configuration response."""
    id: int
    name: str
    rtsp_url: str
    location: str
    zone: Optional[str] = None
    status: CameraStatus
    enabled: bool
    detection_interval: int
    confidence_threshold: float
    required_ppe: List[PPEType]
    created_at: datetime
    updated_at: datetime
    last_seen: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Detection Schemas
class BoundingBox(BaseModel):
    """Bounding box coordinates."""
    x1: float = Field(..., description="Sol üst köşe X koordinatı")
    y1: float = Field(..., description="Sol üst köşe Y koordinatı")
    x2: float = Field(..., description="Sağ alt köşe X koordinatı")
    y2: float = Field(..., description="Sağ alt köşe Y koordinatı")

    @field_validator('x1', 'x2', 'y1', 'y2')
    @classmethod
    def validate_coordinates(cls, v):
        if v < 0:
            raise ValueError("Koordinatlar negatif olamaz")
        return v


class PersonDetection(BaseModel):
    """Detected person with PPE status."""
    person_id: int = Field(..., description="Kişi ID")
    bbox: BoundingBox = Field(..., description="Kişi sınırlayıcı kutu")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Tespit güven skoru")
    detected_ppe: Dict[PPEType, float] = Field(
        default_factory=dict, description="Tespit edilen KKD ve güven skorları"
    )
    missing_ppe: List[PPEType] = Field(
        default_factory=list, description="Eksik KKD listesi"
    )
    is_compliant: bool = Field(..., description="KKD uyumlu mu?")
    violations: List[ViolationType] = Field(
        default_factory=list, description="İhlal tipleri"
    )


class DetectionRequest(BaseModel):
    """Request for running detection on an image."""
    camera_id: Optional[int] = Field(None, description="Kamera ID (opsiyonel)")
    confidence_threshold: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Özel güven eşiği"
    )
    required_ppe: Optional[List[PPEType]] = Field(
        None, description="Özel zorunlu KKD listesi"
    )
    save_results: bool = Field(True, description="Sonuçları kaydet?")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "camera_id": 1,
                "confidence_threshold": 0.7,
                "required_ppe": ["helmet", "vest"],
                "save_results": True
            }
        }
    )


class DetectionResult(BaseModel):
    """Detection result response."""
    detection_id: Optional[str] = Field(None, description="Tespit ID")
    camera_id: Optional[int] = Field(None, description="Kamera ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="Tespit zamanı")
    image_path: Optional[str] = Field(None, description="İşlenmiş görüntü yolu")
    total_persons: int = Field(..., description="Toplam tespit edilen kişi sayısı")
    compliant_persons: int = Field(..., description="Uyumlu kişi sayısı")
    violation_count: int = Field(..., description="İhlal sayısı")
    persons: List[PersonDetection] = Field(
        default_factory=list, description="Tespit edilen kişiler"
    )
    processing_time_ms: float = Field(..., description="İşleme süresi (ms)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detection_id": "det_20231118_123456",
                "camera_id": 1,
                "timestamp": "2023-11-18T12:34:56",
                "total_persons": 3,
                "compliant_persons": 2,
                "violation_count": 1,
                "processing_time_ms": 245.6
            }
        }
    )


# Violation Schemas
class ViolationRecord(BaseModel):
    """Violation record."""
    id: int
    camera_id: int
    camera_name: str
    location: str
    detection_id: str
    timestamp: datetime
    person_id: int
    violation_types: List[ViolationType]
    missing_ppe: List[PPEType]
    confidence: float
    image_path: Optional[str] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ViolationFilters(BaseModel):
    """Filters for querying violations."""
    camera_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    violation_type: Optional[ViolationType] = None
    acknowledged: Optional[bool] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


class ViolationAcknowledge(BaseModel):
    """Acknowledge violation."""
    acknowledged_by: str = Field(..., min_length=1, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "acknowledged_by": "Ahmet Yılmaz",
                "notes": "Çalışan uyarıldı, baret verildi"
            }
        }
    )


# Statistics Schemas
class CameraStats(BaseModel):
    """Statistics for a single camera."""
    camera_id: int
    camera_name: str
    total_detections: int
    total_violations: int
    violation_rate: float
    avg_processing_time_ms: float
    status: CameraStatus
    last_detection: Optional[datetime] = None


class PPEStats(BaseModel):
    """Statistics for PPE compliance."""
    ppe_type: PPEType
    total_detections: int
    violations: int
    compliance_rate: float


class StatsResponse(BaseModel):
    """Overall statistics response."""
    period_start: datetime
    period_end: datetime
    total_cameras: int
    active_cameras: int
    total_detections: int
    total_persons_detected: int
    total_violations: int
    overall_compliance_rate: float
    avg_processing_time_ms: float
    camera_stats: List[CameraStats] = Field(default_factory=list)
    ppe_stats: List[PPEStats] = Field(default_factory=list)
    violations_by_hour: Dict[int, int] = Field(default_factory=dict)
    violations_by_type: Dict[ViolationType, int] = Field(default_factory=dict)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "period_start": "2023-11-18T00:00:00",
                "period_end": "2023-11-18T23:59:59",
                "total_cameras": 5,
                "active_cameras": 4,
                "total_detections": 1250,
                "total_persons_detected": 3500,
                "total_violations": 45,
                "overall_compliance_rate": 98.7,
                "avg_processing_time_ms": 234.5
            }
        }
    )


# WebSocket Schemas
class LiveDetectionMessage(BaseModel):
    """Message for live detection WebSocket."""
    type: str = Field(..., description="Mesaj tipi: detection, status, error")
    camera_id: int
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


# Health & Status Schemas
class HealthStatus(BaseModel):
    """API health status."""
    status: str = Field(..., description="Sağlık durumu: healthy, degraded, unhealthy")
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = Field(..., description="API versiyonu")
    uptime_seconds: float
    database_connected: bool
    model_loaded: bool
    active_cameras: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "timestamp": "2023-11-18T12:34:56",
                "version": "0.1.0",
                "uptime_seconds": 3600.5,
                "database_connected": True,
                "model_loaded": True,
                "active_cameras": 4
            }
        }
    )


# Error Responses
class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Hata mesajı")
    detail: Optional[str] = Field(None, description="Detaylı hata açıklaması")
    timestamp: datetime = Field(default_factory=datetime.now)
    path: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "Kamera bulunamadı",
                "detail": "ID 123 ile kamera kayıtlı değil",
                "timestamp": "2023-11-18T12:34:56",
                "path": "/api/cameras/123"
            }
        }
    )


# Pagination
class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: List[Any] = Field(default_factory=list)
    total: int
    limit: int
    offset: int
    has_more: bool
