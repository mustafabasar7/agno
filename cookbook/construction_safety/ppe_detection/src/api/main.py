"""
FastAPI application for PPE Detection service.

This is the main entry point for the PPE Detection API.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .endpoints import router
from .dependencies import get_app_state, get_settings, engine, Base
from .schemas import ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown tasks.
    """
    # Startup
    logger.info("Starting PPE Detection API...")

    # Initialize database
    try:
        async with engine.begin() as conn:
            # Create tables if they don't exist
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    # Initialize app state
    app_state = get_app_state()
    logger.info("Application state initialized")

    # Load detection model (optional - can be lazy loaded)
    try:
        # Model will be lazy loaded on first request
        logger.info("Detection model will be loaded on first request")
    except Exception as e:
        logger.warning(f"Failed to pre-load detection model: {e}")

    logger.info("PPE Detection API started successfully")

    yield

    # Shutdown
    logger.info("Shutting down PPE Detection API...")

    # Close database connections
    await engine.dispose()
    logger.info("Database connections closed")

    # Clean up resources
    logger.info("PPE Detection API shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="PPE Detection API",
    description="İnşaat sahası için KKD (Kişisel Koruyucu Donanım) tespit sistemi",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Get settings
settings = get_settings()


# ============================================================================
# Middleware
# ============================================================================

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and track metrics."""
    start_time = time.time()

    # Get app state
    app_state = get_app_state()
    app_state.increment_requests()

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    # Log request
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration:.3f}s"
    )

    # Add custom headers
    response.headers["X-Process-Time"] = str(duration)
    response.headers["X-Request-ID"] = str(request.headers.get("X-Request-ID", ""))

    return response


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            detail=str(exc.detail) if hasattr(exc, 'detail') else None,
            path=str(request.url.path),
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="Geçersiz istek verisi",
            detail=" | ".join(errors),
            path=str(request.url.path),
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Sunucu hatası",
            detail="Beklenmeyen bir hata oluştu. Lütfen daha sonra tekrar deneyin.",
            path=str(request.url.path),
        ).model_dump(),
    )


# ============================================================================
# Routes
# ============================================================================

# Include API router
app.include_router(router, prefix="/api", tags=["api"])


# Root endpoint
@app.get(
    "/",
    tags=["root"],
    summary="API Bilgisi",
    description="API hakkında temel bilgileri döndürür"
)
async def root() -> Dict[str, Any]:
    """
    Root endpoint - API information.

    Returns:
        Dict: API information
    """
    return {
        "name": "PPE Detection API",
        "version": settings.version,
        "description": "İnşaat sahası için KKD tespit sistemi",
        "docs": "/api/docs",
        "health": "/api/health",
    }


# Ping endpoint
@app.get(
    "/ping",
    tags=["health"],
    summary="Ping",
    description="API'nin çalışır durumda olup olmadığını kontrol eder"
)
async def ping() -> Dict[str, str]:
    """
    Simple ping endpoint.

    Returns:
        Dict: Pong response
    """
    return {"status": "ok", "message": "pong"}


# Version endpoint
@app.get(
    "/version",
    tags=["info"],
    summary="Versiyon Bilgisi",
    description="API versiyonunu döndürür"
)
async def version() -> Dict[str, str]:
    """
    Get API version.

    Returns:
        Dict: Version information
    """
    return {
        "version": settings.version,
        "app_name": settings.app_name,
    }


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info",
    )
