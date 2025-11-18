"""
Health check system for monitoring service availability and system status.
"""

import asyncio
import os
import shutil
import socket
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import psutil

from .logger import get_logger
from .monitoring_config import get_monitoring_config

logger = get_logger(__name__)


class HealthStatus(Enum):
    """Health check status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    component: str
    status: HealthStatus
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)
    response_time_ms: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "component": self.component,
            "status": self.status.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat() + "Z",
            "details": self.details,
            "response_time_ms": self.response_time_ms,
        }


@dataclass
class SystemHealth:
    """Overall system health status."""

    status: HealthStatus
    timestamp: datetime
    checks: List[HealthCheckResult]
    uptime_seconds: float
    version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat() + "Z",
            "uptime_seconds": self.uptime_seconds,
            "version": self.version,
            "checks": [check.to_dict() for check in self.checks],
        }


class HealthChecker:
    """Comprehensive health checking system."""

    def __init__(self):
        self.config = get_monitoring_config().health_check
        self._start_time = time.time()
        self._check_registry: Dict[str, Callable] = {}
        self._last_results: Dict[str, HealthCheckResult] = {}

        # Register default health checks
        self._register_default_checks()

        logger.info("Health checker initialized")

    def _register_default_checks(self) -> None:
        """Register default health checks."""
        self.register_check("disk_space", self._check_disk_space)
        self.register_check("memory", self._check_memory)
        self.register_check("cpu", self._check_cpu)
        self.register_check("process", self._check_process)

    def register_check(self, name: str, check_func: Callable) -> None:
        """Register a health check function."""
        self._check_registry[name] = check_func
        logger.debug("Health check registered", check_name=name)

    async def check_database(self, db_connection: Optional[Any] = None) -> HealthCheckResult:
        """Check database connectivity and health."""
        start_time = time.time()
        component = "database"

        try:
            if db_connection is None:
                # Try to import and check database module
                try:
                    from ..database.connection import get_db_connection

                    db_connection = get_db_connection()
                except ImportError:
                    return HealthCheckResult(
                        component=component,
                        status=HealthStatus.UNKNOWN,
                        message="Database module not available",
                    )

            # Try a simple query
            if hasattr(db_connection, "execute"):
                await asyncio.wait_for(
                    asyncio.to_thread(db_connection.execute, "SELECT 1"),
                    timeout=self.config.database_timeout,
                )
            elif hasattr(db_connection, "ping"):
                await asyncio.wait_for(
                    asyncio.to_thread(db_connection.ping),
                    timeout=self.config.database_timeout,
                )
            else:
                # Assume healthy if connection object exists
                pass

            response_time_ms = (time.time() - start_time) * 1000

            return HealthCheckResult(
                component=component,
                status=HealthStatus.HEALTHY,
                message="Database is accessible",
                response_time_ms=response_time_ms,
                details={"timeout": self.config.database_timeout},
            )

        except asyncio.TimeoutError:
            return HealthCheckResult(
                component=component,
                status=HealthStatus.UNHEALTHY,
                message=f"Database timeout after {self.config.database_timeout}s",
                details={"timeout": self.config.database_timeout},
            )
        except Exception as e:
            logger.error("Database health check failed", exc_info=True, error=str(e))
            return HealthCheckResult(
                component=component,
                status=HealthStatus.UNHEALTHY,
                message=f"Database error: {str(e)}",
                details={"error": str(e)},
            )

    async def check_camera(self, camera_id: str, camera_url: Optional[str] = None) -> HealthCheckResult:
        """Check camera connectivity and availability."""
        start_time = time.time()
        component = f"camera_{camera_id}"

        try:
            # Try to import camera module
            try:
                from ..camera.manager import get_camera_manager

                camera_manager = get_camera_manager()
                is_online = await asyncio.wait_for(
                    asyncio.to_thread(camera_manager.is_camera_online, camera_id),
                    timeout=self.config.camera_timeout,
                )
            except ImportError:
                # Fallback: try to connect to camera URL if provided
                if camera_url:
                    is_online = await self._check_url_reachable(camera_url, self.config.camera_timeout)
                else:
                    return HealthCheckResult(
                        component=component,
                        status=HealthStatus.UNKNOWN,
                        message="Camera module not available",
                    )

            response_time_ms = (time.time() - start_time) * 1000

            if is_online:
                return HealthCheckResult(
                    component=component,
                    status=HealthStatus.HEALTHY,
                    message="Camera is online",
                    response_time_ms=response_time_ms,
                    details={"camera_id": camera_id},
                )
            else:
                return HealthCheckResult(
                    component=component,
                    status=HealthStatus.UNHEALTHY,
                    message="Camera is offline",
                    details={"camera_id": camera_id},
                )

        except asyncio.TimeoutError:
            return HealthCheckResult(
                component=component,
                status=HealthStatus.UNHEALTHY,
                message=f"Camera timeout after {self.config.camera_timeout}s",
                details={"camera_id": camera_id, "timeout": self.config.camera_timeout},
            )
        except Exception as e:
            logger.error("Camera health check failed", exc_info=True, camera_id=camera_id, error=str(e))
            return HealthCheckResult(
                component=component,
                status=HealthStatus.UNHEALTHY,
                message=f"Camera error: {str(e)}",
                details={"camera_id": camera_id, "error": str(e)},
            )

    async def check_model(self, model_name: str = "default") -> HealthCheckResult:
        """Check model availability and readiness."""
        start_time = time.time()
        component = f"model_{model_name}"

        try:
            # Try to import model module
            try:
                from ..models.detector import get_detector

                detector = get_detector()
                is_loaded = await asyncio.wait_for(
                    asyncio.to_thread(detector.is_model_loaded),
                    timeout=self.config.model_timeout,
                )
            except ImportError:
                return HealthCheckResult(
                    component=component,
                    status=HealthStatus.UNKNOWN,
                    message="Model module not available",
                )

            response_time_ms = (time.time() - start_time) * 1000

            if is_loaded:
                return HealthCheckResult(
                    component=component,
                    status=HealthStatus.HEALTHY,
                    message="Model is loaded and ready",
                    response_time_ms=response_time_ms,
                    details={"model_name": model_name},
                )
            else:
                return HealthCheckResult(
                    component=component,
                    status=HealthStatus.UNHEALTHY,
                    message="Model is not loaded",
                    details={"model_name": model_name},
                )

        except asyncio.TimeoutError:
            return HealthCheckResult(
                component=component,
                status=HealthStatus.UNHEALTHY,
                message=f"Model check timeout after {self.config.model_timeout}s",
                details={"model_name": model_name, "timeout": self.config.model_timeout},
            )
        except Exception as e:
            logger.error("Model health check failed", exc_info=True, model_name=model_name, error=str(e))
            return HealthCheckResult(
                component=component,
                status=HealthStatus.DEGRADED,
                message=f"Model error: {str(e)}",
                details={"model_name": model_name, "error": str(e)},
            )

    def _check_disk_space(self) -> HealthCheckResult:
        """Check disk space availability."""
        component = "disk_space"

        try:
            disk_usage = shutil.disk_usage("/")
            free_gb = disk_usage.free / (1024**3)
            total_gb = disk_usage.total / (1024**3)
            used_percent = (disk_usage.used / disk_usage.total) * 100

            if free_gb < self.config.min_disk_space_gb:
                status = HealthStatus.UNHEALTHY
                message = f"Low disk space: {free_gb:.2f}GB free"
            elif used_percent > self.config.disk_warning_threshold_percent:
                status = HealthStatus.DEGRADED
                message = f"Disk usage high: {used_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk space OK: {free_gb:.2f}GB free"

            return HealthCheckResult(
                component=component,
                status=status,
                message=message,
                details={
                    "free_gb": round(free_gb, 2),
                    "total_gb": round(total_gb, 2),
                    "used_percent": round(used_percent, 2),
                    "threshold_gb": self.config.min_disk_space_gb,
                },
            )

        except Exception as e:
            logger.error("Disk space check failed", exc_info=True, error=str(e))
            return HealthCheckResult(
                component=component,
                status=HealthStatus.UNKNOWN,
                message=f"Failed to check disk space: {str(e)}",
            )

    def _check_memory(self) -> HealthCheckResult:
        """Check memory usage."""
        component = "memory"

        try:
            memory = psutil.virtual_memory()
            used_percent = memory.percent
            available_gb = memory.available / (1024**3)

            if used_percent > 95:
                status = HealthStatus.UNHEALTHY
                message = f"Critical memory usage: {used_percent:.1f}%"
            elif used_percent > 85:
                status = HealthStatus.DEGRADED
                message = f"High memory usage: {used_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage OK: {used_percent:.1f}%"

            return HealthCheckResult(
                component=component,
                status=status,
                message=message,
                details={
                    "used_percent": round(used_percent, 2),
                    "available_gb": round(available_gb, 2),
                    "total_gb": round(memory.total / (1024**3), 2),
                },
            )

        except Exception as e:
            logger.error("Memory check failed", exc_info=True, error=str(e))
            return HealthCheckResult(
                component=component,
                status=HealthStatus.UNKNOWN,
                message=f"Failed to check memory: {str(e)}",
            )

    def _check_cpu(self) -> HealthCheckResult:
        """Check CPU usage."""
        component = "cpu"

        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            if cpu_percent > 95:
                status = HealthStatus.UNHEALTHY
                message = f"Critical CPU usage: {cpu_percent:.1f}%"
            elif cpu_percent > 80:
                status = HealthStatus.DEGRADED
                message = f"High CPU usage: {cpu_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"CPU usage OK: {cpu_percent:.1f}%"

            return HealthCheckResult(
                component=component,
                status=status,
                message=message,
                details={
                    "usage_percent": round(cpu_percent, 2),
                    "cpu_count": cpu_count,
                },
            )

        except Exception as e:
            logger.error("CPU check failed", exc_info=True, error=str(e))
            return HealthCheckResult(
                component=component,
                status=HealthStatus.UNKNOWN,
                message=f"Failed to check CPU: {str(e)}",
            )

    def _check_process(self) -> HealthCheckResult:
        """Check current process health."""
        component = "process"

        try:
            process = psutil.Process(os.getpid())
            num_threads = process.num_threads()
            num_fds = process.num_fds() if hasattr(process, "num_fds") else 0
            cpu_percent = process.cpu_percent(interval=0.1)
            memory_percent = process.memory_percent()

            status = HealthStatus.HEALTHY
            message = "Process healthy"

            if num_threads > 100:
                status = HealthStatus.DEGRADED
                message = f"High thread count: {num_threads}"
            elif memory_percent > 50:
                status = HealthStatus.DEGRADED
                message = f"High process memory: {memory_percent:.1f}%"

            return HealthCheckResult(
                component=component,
                status=status,
                message=message,
                details={
                    "pid": process.pid,
                    "num_threads": num_threads,
                    "num_fds": num_fds,
                    "cpu_percent": round(cpu_percent, 2),
                    "memory_percent": round(memory_percent, 2),
                },
            )

        except Exception as e:
            logger.error("Process check failed", exc_info=True, error=str(e))
            return HealthCheckResult(
                component=component,
                status=HealthStatus.UNKNOWN,
                message=f"Failed to check process: {str(e)}",
            )

    async def _check_url_reachable(self, url: str, timeout: float) -> bool:
        """Check if a URL is reachable."""
        try:
            # Simple socket connection test for RTSP/HTTP URLs
            if url.startswith("rtsp://"):
                host = url.split("//")[1].split(":")[0]
                port = 554  # Default RTSP port
            elif url.startswith("http://"):
                host = url.split("//")[1].split(":")[0]
                port = 80
            elif url.startswith("https://"):
                host = url.split("//")[1].split(":")[0]
                port = 443
            else:
                return False

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0

        except Exception:
            return False

    async def run_all_checks(
        self,
        include_database: bool = False,
        include_cameras: bool = False,
        include_model: bool = False,
        camera_ids: Optional[List[str]] = None,
    ) -> SystemHealth:
        """Run all registered health checks."""
        results: List[HealthCheckResult] = []

        # Run registered checks
        for name, check_func in self._check_registry.items():
            try:
                result = check_func()
                results.append(result)
                self._last_results[name] = result
            except Exception as e:
                logger.error("Health check failed", exc_info=True, check_name=name, error=str(e))
                results.append(
                    HealthCheckResult(
                        component=name,
                        status=HealthStatus.UNKNOWN,
                        message=f"Check failed: {str(e)}",
                    )
                )

        # Optional checks
        if include_database:
            db_result = await self.check_database()
            results.append(db_result)
            self._last_results["database"] = db_result

        if include_cameras and camera_ids:
            for camera_id in camera_ids:
                camera_result = await self.check_camera(camera_id)
                results.append(camera_result)
                self._last_results[f"camera_{camera_id}"] = camera_result

        if include_model:
            model_result = await self.check_model()
            results.append(model_result)
            self._last_results["model"] = model_result

        # Determine overall status
        overall_status = self._calculate_overall_status(results)

        uptime_seconds = time.time() - self._start_time

        return SystemHealth(
            status=overall_status,
            timestamp=datetime.utcnow(),
            checks=results,
            uptime_seconds=uptime_seconds,
        )

    def _calculate_overall_status(self, results: List[HealthCheckResult]) -> HealthStatus:
        """Calculate overall system status from individual checks."""
        if not results:
            return HealthStatus.UNKNOWN

        statuses = [r.status for r in results]

        if any(s == HealthStatus.UNHEALTHY for s in statuses):
            return HealthStatus.UNHEALTHY
        elif any(s == HealthStatus.DEGRADED for s in statuses):
            return HealthStatus.DEGRADED
        elif all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN

    def get_last_result(self, component: str) -> Optional[HealthCheckResult]:
        """Get the last result for a specific component."""
        return self._last_results.get(component)

    def get_uptime(self) -> float:
        """Get system uptime in seconds."""
        return time.time() - self._start_time


# Global health checker instance
health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get the global health checker instance."""
    global health_checker
    if health_checker is None:
        health_checker = HealthChecker()
    return health_checker


# Example usage
if __name__ == "__main__":
    import asyncio
    from .logger import setup_logging

    setup_logging()

    async def main():
        checker = get_health_checker()

        # Run all checks
        health = await checker.run_all_checks(
            include_database=False,
            include_cameras=False,
            include_model=False,
        )

        print("System Health:")
        print(f"Status: {health.status.value}")
        print(f"Uptime: {health.uptime_seconds:.2f}s")
        print("\nComponent Checks:")
        for check in health.checks:
            print(f"  {check.component}: {check.status.value} - {check.message}")

    asyncio.run(main())
