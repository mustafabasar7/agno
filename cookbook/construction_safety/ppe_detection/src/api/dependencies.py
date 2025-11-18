"""
Dependency injection for FastAPI endpoints.
"""

import os
import time
from typing import AsyncGenerator, Optional
from functools import lru_cache

from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./ppe_detection.db")

engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


# Database dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session.

    Yields:
        AsyncSession: SQLAlchemy async session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Application state
class AppState:
    """Application state container."""

    def __init__(self):
        self.start_time = time.time()
        self.detection_model = None
        self.active_cameras = {}
        self.websocket_connections = set()
        self.request_count = 0
        self.detection_count = 0
        self.violation_count = 0

    @property
    def uptime(self) -> float:
        """Get uptime in seconds."""
        return time.time() - self.start_time

    def increment_requests(self):
        """Increment request counter."""
        self.request_count += 1

    def increment_detections(self):
        """Increment detection counter."""
        self.detection_count += 1

    def increment_violations(self):
        """Increment violation counter."""
        self.violation_count += 1


# Global app state instance
_app_state: Optional[AppState] = None


def get_app_state() -> AppState:
    """
    Get application state singleton.

    Returns:
        AppState: Application state instance
    """
    global _app_state
    if _app_state is None:
        _app_state = AppState()
    return _app_state


# Detection model dependency
class DetectionModelDependency:
    """Dependency for detection model."""

    def __init__(self):
        self._model = None

    async def __call__(self) -> "DetectionModel":
        """
        Get detection model instance.

        Returns:
            DetectionModel: The loaded detection model

        Raises:
            HTTPException: If model is not loaded
        """
        if self._model is None:
            # Lazy load model
            try:
                from src.models.detector import PPEDetector
                self._model = PPEDetector()
                await self._model.load_model()
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Model yüklenemedi: {str(e)}"
                )

        return self._model

    def set_model(self, model):
        """Set the model instance."""
        self._model = model

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._model is not None


detection_model = DetectionModelDependency()


# Authentication dependency (placeholder for future implementation)
async def verify_api_key(
    x_api_key: Optional[str] = Header(None, description="API anahtarı")
) -> str:
    """
    Verify API key (placeholder for future authentication).

    Args:
        x_api_key: API key from header

    Returns:
        str: Verified API key

    Raises:
        HTTPException: If API key is invalid
    """
    # TODO: Implement actual API key verification
    # For now, just check if API key is required
    api_key_required = os.getenv("API_KEY_REQUIRED", "false").lower() == "true"

    if api_key_required:
        if not x_api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API anahtarı gerekli",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        # Verify against environment variable
        valid_api_key = os.getenv("API_KEY")
        if x_api_key != valid_api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Geçersiz API anahtarı",
                headers={"WWW-Authenticate": "ApiKey"},
            )

    return x_api_key or "default"


# Rate limiting dependency (placeholder)
class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = {}

    async def __call__(self, client_id: str = "default"):
        """
        Check rate limit for client.

        Args:
            client_id: Client identifier

        Raises:
            HTTPException: If rate limit exceeded
        """
        # TODO: Implement proper rate limiting with Redis or similar
        # For now, this is a simple placeholder
        current_time = time.time()

        if client_id not in self.requests:
            self.requests[client_id] = []

        # Remove old requests (older than 1 minute)
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if current_time - req_time < 60
        ]

        # Check if limit exceeded
        if len(self.requests[client_id]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Çok fazla istek. Lütfen daha sonra tekrar deneyin.",
                headers={"Retry-After": "60"},
            )

        # Add current request
        self.requests[client_id].append(current_time)


# Create rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=60)


# Settings/Config dependency
class Settings:
    """Application settings."""

    def __init__(self):
        self.app_name = "PPE Detection API"
        self.version = "0.1.0"
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.max_upload_size_mb = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
        self.allowed_image_types = {"image/jpeg", "image/png", "image/jpg"}
        self.detection_timeout_seconds = int(os.getenv("DETECTION_TIMEOUT", "30"))
        self.database_url = DATABASE_URL
        self.cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
        self.model_path = os.getenv("MODEL_PATH", "models/ppe_detector.pt")
        self.save_detections = os.getenv("SAVE_DETECTIONS", "true").lower() == "true"
        self.detection_image_dir = os.getenv("DETECTION_IMAGE_DIR", "data/detections")


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings (cached).

    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Camera manager dependency
class CameraManager:
    """Manages active camera streams."""

    def __init__(self):
        self.active_streams = {}

    async def start_camera(self, camera_id: int, rtsp_url: str):
        """Start camera stream."""
        # TODO: Implement actual camera stream management
        pass

    async def stop_camera(self, camera_id: int):
        """Stop camera stream."""
        if camera_id in self.active_streams:
            del self.active_streams[camera_id]

    def get_camera_status(self, camera_id: int) -> str:
        """Get camera status."""
        return "active" if camera_id in self.active_streams else "inactive"


camera_manager = CameraManager()


# Storage dependency
class StorageManager:
    """Manages file storage for detections and violations."""

    def __init__(self, base_path: str = "data/detections"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    async def save_detection_image(
        self,
        image_data: bytes,
        detection_id: str
    ) -> str:
        """
        Save detection image to storage.

        Args:
            image_data: Image bytes
            detection_id: Detection identifier

        Returns:
            str: Path to saved image
        """
        from datetime import datetime

        # Create date-based subdirectory
        date_dir = datetime.now().strftime("%Y/%m/%d")
        save_dir = os.path.join(self.base_path, date_dir)
        os.makedirs(save_dir, exist_ok=True)

        # Save image
        filename = f"{detection_id}.jpg"
        filepath = os.path.join(save_dir, filename)

        with open(filepath, "wb") as f:
            f.write(image_data)

        return filepath

    async def get_detection_image(self, image_path: str) -> Optional[bytes]:
        """
        Get detection image from storage.

        Args:
            image_path: Path to image

        Returns:
            bytes: Image data or None if not found
        """
        try:
            with open(image_path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None


storage_manager = StorageManager()


# Pagination dependency
class PaginationParams:
    """Pagination parameters."""

    def __init__(
        self,
        limit: int = 100,
        offset: int = 0,
    ):
        self.limit = min(limit, 1000)  # Max 1000 items
        self.offset = max(offset, 0)  # Non-negative


def get_pagination_params(
    limit: int = 100,
    offset: int = 0,
) -> PaginationParams:
    """
    Get pagination parameters.

    Args:
        limit: Maximum number of items to return
        offset: Number of items to skip

    Returns:
        PaginationParams: Pagination parameters
    """
    return PaginationParams(limit=limit, offset=offset)
