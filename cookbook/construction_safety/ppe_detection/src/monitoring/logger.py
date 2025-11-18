"""
Structured logging with JSON format, rotation, and async support.
"""

import json
import logging
import logging.handlers
import sys
import threading
import traceback
from datetime import datetime
from enum import Enum
from pathlib import Path
from queue import Queue
from typing import Any, Dict, Optional

from .monitoring_config import get_monitoring_config


class LogLevel(Enum):
    """Log levels."""

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class LogCategory(Enum):
    """Log categories for separate log files."""

    APPLICATION = "application"
    DETECTION = "detection"
    CAMERA = "camera"
    ALERT = "alert"


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields
        if hasattr(record, "category"):
            log_data["category"] = record.category

        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add process and thread info
        log_data["process"] = {
            "id": record.process,
            "name": record.processName,
        }
        log_data["thread"] = {
            "id": record.thread,
            "name": record.threadName,
        }

        return json.dumps(log_data, default=str)


class AsyncLogHandler(logging.Handler):
    """Async log handler using a queue."""

    def __init__(self, target_handler: logging.Handler, queue_size: int = 10000):
        super().__init__()
        self.target_handler = target_handler
        self.queue: Queue = Queue(maxsize=queue_size)
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def emit(self, record: logging.LogRecord) -> None:
        """Add record to queue."""
        try:
            self.queue.put_nowait(record)
        except Exception:
            self.handleError(record)

    def _worker(self) -> None:
        """Worker thread to process log records."""
        while True:
            try:
                record = self.queue.get()
                if record is None:  # Sentinel to stop thread
                    break
                self.target_handler.emit(record)
            except Exception:
                pass

    def close(self) -> None:
        """Close the handler."""
        self.queue.put(None)  # Stop worker thread
        self.thread.join(timeout=5)
        self.target_handler.close()
        super().close()


class PPELogger:
    """Enhanced logger with structured logging and categorization."""

    def __init__(self, name: str, category: Optional[LogCategory] = None):
        self.name = name
        self.category = category or LogCategory.APPLICATION
        self.logger = logging.getLogger(name)

    def _log(
        self,
        level: LogLevel,
        message: str,
        extra_data: Optional[Dict[str, Any]] = None,
        exc_info: bool = False,
    ) -> None:
        """Internal logging method."""
        extra = {
            "category": self.category.value,
            "extra_data": extra_data or {},
        }
        self.logger.log(level.value, message, extra=extra, exc_info=exc_info)

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self._log(LogLevel.DEBUG, message, extra_data=kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self._log(LogLevel.INFO, message, extra_data=kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self._log(LogLevel.WARNING, message, extra_data=kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs) -> None:
        """Log error message."""
        self._log(LogLevel.ERROR, message, extra_data=kwargs, exc_info=exc_info)

    def critical(self, message: str, exc_info: bool = False, **kwargs) -> None:
        """Log critical message."""
        self._log(LogLevel.CRITICAL, message, extra_data=kwargs, exc_info=exc_info)

    # Specialized logging methods for different categories
    def log_detection(
        self,
        camera_id: str,
        detections: list,
        violations: list,
        inference_time_ms: float,
        **kwargs,
    ) -> None:
        """Log detection event."""
        self.info(
            "Detection completed",
            camera_id=camera_id,
            detection_count=len(detections),
            violation_count=len(violations),
            inference_time_ms=inference_time_ms,
            detections=detections,
            violations=violations,
            **kwargs,
        )

    def log_violation(
        self,
        camera_id: str,
        violation_type: str,
        person_id: Optional[str] = None,
        confidence: Optional[float] = None,
        **kwargs,
    ) -> None:
        """Log PPE violation."""
        self.warning(
            "PPE violation detected",
            camera_id=camera_id,
            violation_type=violation_type,
            person_id=person_id,
            confidence=confidence,
            **kwargs,
        )

    def log_camera_event(
        self,
        camera_id: str,
        event_type: str,
        status: str,
        **kwargs,
    ) -> None:
        """Log camera event."""
        self.info(
            f"Camera event: {event_type}",
            camera_id=camera_id,
            event_type=event_type,
            status=status,
            **kwargs,
        )

    def log_alert_sent(
        self,
        alert_type: str,
        recipient: str,
        success: bool,
        **kwargs,
    ) -> None:
        """Log alert sent."""
        if success:
            self.info(
                "Alert sent successfully",
                alert_type=alert_type,
                recipient=recipient,
                **kwargs,
            )
        else:
            self.error(
                "Failed to send alert",
                alert_type=alert_type,
                recipient=recipient,
                **kwargs,
            )

    def log_performance(
        self,
        operation: str,
        duration_ms: float,
        **kwargs,
    ) -> None:
        """Log performance metrics."""
        self.debug(
            f"Performance: {operation}",
            operation=operation,
            duration_ms=duration_ms,
            **kwargs,
        )

    def log_api_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        **kwargs,
    ) -> None:
        """Log API request."""
        self.info(
            "API request",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            **kwargs,
        )


def _create_rotating_handler(
    log_file: Path,
    max_bytes: int,
    backup_count: int,
    use_async: bool = True,
    queue_size: int = 10000,
) -> logging.Handler:
    """Create a rotating file handler with optional async support."""
    handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    handler.setFormatter(StructuredFormatter())

    if use_async:
        return AsyncLogHandler(handler, queue_size=queue_size)
    return handler


def setup_logging(config: Optional[Any] = None) -> None:
    """Set up logging system with separate files for different categories."""
    if config is None:
        config = get_monitoring_config().logging

    # Create log directory
    config.log_dir.mkdir(parents=True, exist_ok=True)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.log_level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler (with simple format for readability)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root_logger.addHandler(console_handler)

    # Application log file (all logs)
    app_handler = _create_rotating_handler(
        config.log_dir / config.app_log_file,
        config.max_bytes,
        config.backup_count,
        config.use_async_logging,
        config.queue_size,
    )
    root_logger.addHandler(app_handler)

    # Category-specific log files
    category_files = {
        LogCategory.DETECTION: config.detection_log_file,
        LogCategory.CAMERA: config.camera_log_file,
        LogCategory.ALERT: config.alert_log_file,
    }

    for category, filename in category_files.items():
        handler = _create_rotating_handler(
            config.log_dir / filename,
            config.max_bytes,
            config.backup_count,
            config.use_async_logging,
            config.queue_size,
        )
        # Add filter to only log records with matching category
        handler.addFilter(lambda record, cat=category: getattr(record, "category", None) == cat.value)
        root_logger.addHandler(handler)

    # Log startup
    logger = get_logger(__name__)
    logger.info(
        "Logging system initialized",
        log_dir=str(config.log_dir),
        log_level=config.log_level,
        async_logging=config.use_async_logging,
    )


def get_logger(
    name: str,
    category: Optional[LogCategory] = None,
) -> PPELogger:
    """Get a logger instance with the specified name and category."""
    return PPELogger(name, category)


# Convenience functions for category-specific loggers
def get_detection_logger(name: str) -> PPELogger:
    """Get a logger for detection events."""
    return get_logger(name, LogCategory.DETECTION)


def get_camera_logger(name: str) -> PPELogger:
    """Get a logger for camera events."""
    return get_logger(name, LogCategory.CAMERA)


def get_alert_logger(name: str) -> PPELogger:
    """Get a logger for alert events."""
    return get_logger(name, LogCategory.ALERT)


# Example usage
if __name__ == "__main__":
    # Initialize logging
    setup_logging()

    # Test different loggers
    app_logger = get_logger(__name__)
    app_logger.info("Application started", version="1.0.0")

    detection_logger = get_detection_logger(__name__)
    detection_logger.log_detection(
        camera_id="camera_01",
        detections=[{"type": "person", "confidence": 0.95}],
        violations=[{"type": "no_helmet", "confidence": 0.88}],
        inference_time_ms=45.2,
    )

    camera_logger = get_camera_logger(__name__)
    camera_logger.log_camera_event(
        camera_id="camera_01",
        event_type="connected",
        status="online",
    )

    alert_logger = get_alert_logger(__name__)
    alert_logger.log_alert_sent(
        alert_type="email",
        recipient="admin@example.com",
        success=True,
    )

    # Test error logging
    try:
        raise ValueError("Test exception")
    except Exception:
        app_logger.error("An error occurred", exc_info=True)
