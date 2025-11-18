"""
PPE Detection Configuration Management
Pydantic Settings kullanarak yapılandırma yönetimi
"""

from typing import Dict, List, Optional, Literal
from pathlib import Path
from pydantic import Field, field_validator, BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


# ============================================================================
# Veritabanı Yapılandırması
# ============================================================================
class DatabaseConfig(BaseModel):
    """
    Veritabanı bağlantı yapılandırması
    PostgreSQL/SQLite desteği
    """

    # Veritabanı tipi: postgresql, sqlite
    type: Literal["postgresql", "sqlite"] = Field(
        default="postgresql",
        description="Veritabanı tipi"
    )

    # PostgreSQL ayarları
    host: str = Field(default="localhost", description="Veritabanı sunucu adresi")
    port: int = Field(default=5432, description="Veritabanı portu")
    username: str = Field(default="ppe_user", description="Veritabanı kullanıcı adı")
    password: SecretStr = Field(default="", description="Veritabanı şifresi")
    database: str = Field(default="ppe_detection", description="Veritabanı adı")

    # SQLite ayarları
    sqlite_path: Path = Field(
        default=Path("data/ppe_detection.db"),
        description="SQLite veritabanı dosya yolu"
    )

    # Bağlantı havuzu ayarları
    pool_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Bağlantı havuzu boyutu"
    )
    max_overflow: int = Field(
        default=20,
        ge=0,
        le=100,
        description="Maksimum taşma bağlantı sayısı"
    )
    pool_timeout: int = Field(
        default=30,
        ge=1,
        description="Bağlantı havuzu zaman aşımı (saniye)"
    )
    pool_recycle: int = Field(
        default=3600,
        ge=60,
        description="Bağlantı yenileme süresi (saniye)"
    )

    # Echo SQL sorguları (geliştirme için)
    echo: bool = Field(default=False, description="SQL sorgularını logla")

    def get_connection_string(self) -> str:
        """Veritabanı bağlantı string'ini oluştur"""
        if self.type == "sqlite":
            return f"sqlite:///{self.sqlite_path}"
        else:
            password = self.password.get_secret_value()
            return f"postgresql://{self.username}:{password}@{self.host}:{self.port}/{self.database}"


# ============================================================================
# Kamera Yapılandırması
# ============================================================================
class CameraConfig(BaseModel):
    """
    RTSP kamera bağlantı yapılandırması
    Çoklu kamera desteği
    """

    # Kamera ID'si (benzersiz tanımlayıcı)
    camera_id: str = Field(description="Kamera benzersiz ID'si")

    # Kamera adı
    name: str = Field(description="Kamera görünen adı")

    # RTSP stream URL'i
    rtsp_url: SecretStr = Field(description="RTSP stream URL'i")

    # Kamera konumu/alanı
    location: str = Field(default="", description="Kamera fiziksel konumu")
    zone: str = Field(default="", description="Kamera bölgesi/alanı")

    # Stream ayarları
    fps: int = Field(default=10, ge=1, le=60, description="Saniye başına frame")
    resolution: tuple[int, int] = Field(
        default=(1920, 1080),
        description="Çözünürlük (genişlik, yükseklik)"
    )

    # Reconnection ayarları
    reconnect_delay: int = Field(
        default=5,
        ge=1,
        description="Yeniden bağlanma gecikmesi (saniye)"
    )
    max_reconnect_attempts: int = Field(
        default=10,
        ge=1,
        description="Maksimum yeniden bağlanma denemesi"
    )

    # Buffer ayarları
    buffer_size: int = Field(
        default=100,
        ge=1,
        description="Frame buffer boyutu"
    )

    # Kamera aktif mi?
    enabled: bool = Field(default=True, description="Kamera aktif durumu")

    @field_validator("rtsp_url")
    @classmethod
    def validate_rtsp_url(cls, v: SecretStr) -> SecretStr:
        """RTSP URL formatını doğrula"""
        url = v.get_secret_value()
        if not url.startswith(("rtsp://", "http://", "https://")):
            raise ValueError("Geçersiz stream URL formatı")
        return v


class CamerasConfig(BaseModel):
    """Tüm kameraların yapılandırması"""

    cameras: List[CameraConfig] = Field(
        default_factory=list,
        description="Kamera listesi"
    )

    # Global kamera ayarları
    default_fps: int = Field(default=10, ge=1, le=60)
    default_resolution: tuple[int, int] = Field(default=(1920, 1080))
    frame_skip: int = Field(
        default=1,
        ge=1,
        description="Kaç frame'de bir işle"
    )


# ============================================================================
# Model Yapılandırması
# ============================================================================
class ModelConfig(BaseModel):
    """
    YOLOv8/YOLOv11 model yapılandırması
    PPE detection model ayarları
    """

    # Model dosya yolu
    model_path: Path = Field(
        default=Path("models/ppe_detection.pt"),
        description="Model dosya yolu"
    )

    # Model tipi
    model_type: Literal["yolov8", "yolov11"] = Field(
        default="yolov11",
        description="Model tipi"
    )

    # Model boyutu (n, s, m, l, x)
    model_size: Literal["n", "s", "m", "l", "x"] = Field(
        default="m",
        description="Model boyutu (n=nano, s=small, m=medium, l=large, x=xlarge)"
    )

    # İnference ayarları
    confidence_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Güven eşiği"
    )
    iou_threshold: float = Field(
        default=0.45,
        ge=0.0,
        le=1.0,
        description="NMS IoU eşiği"
    )

    # Device ayarları
    device: Literal["cpu", "cuda", "mps"] = Field(
        default="cuda",
        description="İşlem cihazı"
    )
    device_id: int = Field(
        default=0,
        ge=0,
        description="GPU ID (cuda için)"
    )

    # Batch processing
    batch_size: int = Field(
        default=1,
        ge=1,
        description="Batch boyutu"
    )

    # Half precision (FP16)
    half_precision: bool = Field(
        default=False,
        description="FP16 half precision kullan"
    )

    # PPE sınıfları
    ppe_classes: Dict[str, int] = Field(
        default={
            "hardhat": 0,
            "mask": 1,
            "safety_vest": 2,
            "person": 3,
            "no_hardhat": 4,
            "no_mask": 5,
            "no_safety_vest": 6
        },
        description="PPE sınıf isimleri ve ID'leri"
    )

    # Required PPE
    required_ppe: List[str] = Field(
        default=["hardhat", "safety_vest"],
        description="Zorunlu PPE ekipmanları"
    )

    # Model warmup
    warmup_iterations: int = Field(
        default=10,
        ge=0,
        description="Model warmup iterasyon sayısı"
    )

    @field_validator("model_path")
    @classmethod
    def validate_model_path(cls, v: Path) -> Path:
        """Model dosya yolunu doğrula"""
        if not v.suffix in [".pt", ".onnx", ".engine"]:
            raise ValueError("Geçersiz model dosya formatı")
        return v


# ============================================================================
# Alert Yapılandırması
# ============================================================================
class AlertConfig(BaseModel):
    """
    Uyarı ve bildirim yapılandırması
    Email, SMS, webhook desteği
    """

    # Alert seviyeleri
    enable_alerts: bool = Field(default=True, description="Uyarıları aktifleştir")

    # Minimum alert interval (spam önleme)
    min_alert_interval: int = Field(
        default=60,
        ge=0,
        description="Minimum uyarı aralığı (saniye)"
    )

    # Alert kanalları
    enable_email: bool = Field(default=True, description="Email uyarıları")
    enable_sms: bool = Field(default=False, description="SMS uyarıları")
    enable_webhook: bool = Field(default=True, description="Webhook uyarıları")
    enable_database: bool = Field(default=True, description="Veritabanı kayıt")

    # Email ayarları
    email_recipients: List[str] = Field(
        default_factory=list,
        description="Email alıcıları"
    )
    email_cc: List[str] = Field(
        default_factory=list,
        description="Email CC alıcıları"
    )

    # SMS ayarları
    sms_recipients: List[str] = Field(
        default_factory=list,
        description="SMS alıcıları (telefon numaraları)"
    )

    # Webhook ayarları
    webhook_urls: List[str] = Field(
        default_factory=list,
        description="Webhook URL'leri"
    )
    webhook_timeout: int = Field(
        default=10,
        ge=1,
        description="Webhook timeout (saniye)"
    )

    # Alert öncelikleri
    critical_violations: List[str] = Field(
        default=["no_hardhat"],
        description="Kritik ihlaller (anında uyarı)"
    )

    # Alert birleştirme
    aggregate_alerts: bool = Field(
        default=True,
        description="Uyarıları birleştir"
    )
    aggregation_window: int = Field(
        default=300,
        ge=60,
        description="Birleştirme penceresi (saniye)"
    )

    # Sessiz saatler
    quiet_hours_enabled: bool = Field(
        default=False,
        description="Sessiz saatleri aktifleştir"
    )
    quiet_hours_start: str = Field(
        default="22:00",
        description="Sessiz saat başlangıcı (HH:MM)"
    )
    quiet_hours_end: str = Field(
        default="07:00",
        description="Sessiz saat bitişi (HH:MM)"
    )


# ============================================================================
# API Yapılandırması
# ============================================================================
class APIConfig(BaseModel):
    """
    Harici API'ler ve servisler yapılandırması
    Email, SMS, cloud storage vb.
    """

    # Email servisi (SMTP)
    smtp_host: str = Field(default="smtp.gmail.com", description="SMTP sunucu")
    smtp_port: int = Field(default=587, description="SMTP port")
    smtp_username: str = Field(default="", description="SMTP kullanıcı adı")
    smtp_password: SecretStr = Field(default="", description="SMTP şifresi")
    smtp_use_tls: bool = Field(default=True, description="TLS kullan")
    email_from: str = Field(
        default="ppe-detection@example.com",
        description="Gönderen email adresi"
    )

    # SMS servisi (Twilio)
    twilio_account_sid: SecretStr = Field(default="", description="Twilio Account SID")
    twilio_auth_token: SecretStr = Field(default="", description="Twilio Auth Token")
    twilio_phone_number: str = Field(default="", description="Twilio telefon numarası")

    # Cloud Storage (AWS S3)
    s3_enabled: bool = Field(default=False, description="S3 storage aktif")
    s3_bucket: str = Field(default="", description="S3 bucket adı")
    s3_region: str = Field(default="us-east-1", description="S3 region")
    s3_access_key: SecretStr = Field(default="", description="AWS Access Key")
    s3_secret_key: SecretStr = Field(default="", description="AWS Secret Key")

    # Webhook authentication
    webhook_auth_enabled: bool = Field(
        default=True,
        description="Webhook authentication"
    )
    webhook_auth_token: SecretStr = Field(
        default="",
        description="Webhook auth token"
    )

    # API rate limiting
    rate_limit_enabled: bool = Field(
        default=True,
        description="Rate limiting aktif"
    )
    rate_limit_per_minute: int = Field(
        default=60,
        ge=1,
        description="Dakika başına istek limiti"
    )


# ============================================================================
# Monitoring Yapılandırması
# ============================================================================
class MonitoringConfig(BaseModel):
    """
    Sistem izleme ve metrik toplama yapılandırması
    Prometheus, logging, health checks
    """

    # Logging ayarları
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Log seviyesi"
    )
    log_file: Optional[Path] = Field(
        default=Path("logs/ppe_detection.log"),
        description="Log dosya yolu"
    )
    log_max_size: int = Field(
        default=10 * 1024 * 1024,  # 10 MB
        description="Maksimum log dosya boyutu (bytes)"
    )
    log_backup_count: int = Field(
        default=5,
        ge=1,
        description="Log dosya yedekleme sayısı"
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )

    # Metrics collection
    enable_metrics: bool = Field(
        default=True,
        description="Metrik toplamayı aktifleştir"
    )
    metrics_port: int = Field(
        default=9090,
        ge=1024,
        le=65535,
        description="Prometheus metrics portu"
    )

    # Performance monitoring
    track_inference_time: bool = Field(
        default=True,
        description="Inference süresini izle"
    )
    track_fps: bool = Field(
        default=True,
        description="FPS'i izle"
    )
    track_memory: bool = Field(
        default=True,
        description="Bellek kullanımını izle"
    )

    # Health checks
    health_check_enabled: bool = Field(
        default=True,
        description="Health check endpoint"
    )
    health_check_port: int = Field(
        default=8080,
        ge=1024,
        le=65535,
        description="Health check portu"
    )
    health_check_interval: int = Field(
        default=30,
        ge=5,
        description="Health check aralığı (saniye)"
    )

    # Alerting on system issues
    alert_on_camera_failure: bool = Field(
        default=True,
        description="Kamera hatalarında uyar"
    )
    alert_on_high_memory: bool = Field(
        default=True,
        description="Yüksek bellek kullanımında uyar"
    )
    memory_threshold_percent: int = Field(
        default=90,
        ge=50,
        le=99,
        description="Bellek uyarı eşiği (%)"
    )

    # Snapshot/Screenshot kaydetme
    save_violation_snapshots: bool = Field(
        default=True,
        description="İhlal görüntülerini kaydet"
    )
    snapshot_path: Path = Field(
        default=Path("data/snapshots"),
        description="Snapshot kayıt yolu"
    )
    snapshot_retention_days: int = Field(
        default=30,
        ge=1,
        description="Snapshot saklama süresi (gün)"
    )


# ============================================================================
# Ana Yapılandırma Sınıfı
# ============================================================================
class Settings(BaseSettings):
    """
    Ana yapılandırma sınıfı
    Tüm yapılandırma bölümlerini içerir
    """

    model_config = SettingsConfigDict(
        # .env dosyasından oku
        env_file=".env",
        env_file_encoding="utf-8",
        # İç içe yapılandırma desteği
        env_nested_delimiter="__",
        # Case sensitive
        case_sensitive=False,
        # Extra fields'a izin verme
        extra="ignore",
        # JSON şemaları oluştur
        json_schema_extra={
            "title": "PPE Detection Configuration",
            "description": "Construction safety PPE detection system configuration"
        }
    )

    # ========================================================================
    # Genel Ayarlar
    # ========================================================================

    # Uygulama bilgileri
    app_name: str = Field(
        default="PPE Detection System",
        description="Uygulama adı"
    )
    app_version: str = Field(
        default="1.0.0",
        description="Uygulama versiyonu"
    )

    # Environment
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Çalışma ortamı"
    )

    # Debug mode
    debug: bool = Field(
        default=False,
        description="Debug modu"
    )

    # Çalışma dizini
    base_dir: Path = Field(
        default=Path(__file__).parent.parent,
        description="Ana çalışma dizini"
    )

    # ========================================================================
    # Yapılandırma Bölümleri
    # ========================================================================

    database: DatabaseConfig = Field(
        default_factory=DatabaseConfig,
        description="Veritabanı yapılandırması"
    )

    cameras: CamerasConfig = Field(
        default_factory=CamerasConfig,
        description="Kamera yapılandırması"
    )

    model: ModelConfig = Field(
        default_factory=ModelConfig,
        description="Model yapılandırması"
    )

    alerts: AlertConfig = Field(
        default_factory=AlertConfig,
        description="Alert yapılandırması"
    )

    api: APIConfig = Field(
        default_factory=APIConfig,
        description="API yapılandırması"
    )

    monitoring: MonitoringConfig = Field(
        default_factory=MonitoringConfig,
        description="Monitoring yapılandırması"
    )

    # ========================================================================
    # Feature Flags
    # ========================================================================

    # Özellik bayrakları (A/B testing, gradual rollout için)
    feature_flags: Dict[str, bool] = Field(
        default={
            "enable_person_tracking": True,
            "enable_zone_detection": True,
            "enable_heat_map": False,
            "enable_analytics_dashboard": True,
            "enable_auto_calibration": False,
            "enable_night_mode": False,
        },
        description="Özellik bayrakları"
    )

    # ========================================================================
    # İş Mantığı Ayarları
    # ========================================================================

    # Violation detection
    violation_grace_period: int = Field(
        default=5,
        ge=0,
        description="İhlal tespit bekleme süresi (saniye)"
    )

    # Person tracking
    person_tracking_enabled: bool = Field(
        default=True,
        description="Kişi takibi aktif"
    )
    person_tracking_max_age: int = Field(
        default=30,
        ge=1,
        description="Kişi takip maksimum yaş (frame)"
    )

    # Zone management
    zones_enabled: bool = Field(
        default=False,
        description="Bölge yönetimi aktif"
    )

    # ========================================================================
    # Yardımcı Metodlar
    # ========================================================================

    def is_production(self) -> bool:
        """Production ortamı mı?"""
        return self.environment == "production"

    def is_development(self) -> bool:
        """Development ortamı mı?"""
        return self.environment == "development"

    def is_staging(self) -> bool:
        """Staging ortamı mı?"""
        return self.environment == "staging"

    def get_log_level(self) -> str:
        """Log seviyesini al"""
        if self.debug:
            return "DEBUG"
        return self.monitoring.log_level

    def get_db_connection_string(self) -> str:
        """Veritabanı bağlantı string'ini al"""
        return self.database.get_connection_string()

    def ensure_directories(self) -> None:
        """Gerekli dizinleri oluştur"""
        directories = [
            self.monitoring.log_file.parent if self.monitoring.log_file else None,
            self.monitoring.snapshot_path,
            self.model.model_path.parent,
            self.base_dir / "data",
            self.base_dir / "data" / "snapshots",
            self.base_dir / "logs",
        ]

        for directory in directories:
            if directory:
                directory.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Singleton Pattern için Global Instance
# ============================================================================

_settings_instance: Optional[Settings] = None


def get_settings(reload: bool = False) -> Settings:
    """
    Settings singleton instance'ını al

    Args:
        reload: True ise yapılandırmayı yeniden yükle

    Returns:
        Settings instance
    """
    global _settings_instance

    if _settings_instance is None or reload:
        _settings_instance = Settings()
        _settings_instance.ensure_directories()

    return _settings_instance


def reload_settings() -> Settings:
    """
    Yapılandırmayı yeniden yükle (hot reload)

    Returns:
        Yeni Settings instance
    """
    return get_settings(reload=True)


# Convenience function
def get_config() -> Settings:
    """Kısa yol: Settings'i al"""
    return get_settings()


if __name__ == "__main__":
    # Test için
    settings = get_settings()
    print(f"Environment: {settings.environment}")
    print(f"Debug: {settings.debug}")
    print(f"Database: {settings.get_db_connection_string()}")
    print(f"Log Level: {settings.get_log_level()}")
