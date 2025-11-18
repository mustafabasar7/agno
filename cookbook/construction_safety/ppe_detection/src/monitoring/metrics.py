"""
Metrics collection and export with Prometheus compatibility.
"""

import os
import psutil
import threading
import time
from collections import defaultdict, deque
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Deque, Dict, List, Optional

try:
    from prometheus_client import (
        Counter,
        Gauge,
        Histogram,
        Summary,
        CollectorRegistry,
        generate_latest,
        start_http_server,
    )

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from .logger import get_logger
from .monitoring_config import get_monitoring_config

logger = get_logger(__name__)


@dataclass
class MetricValue:
    """Individual metric value with timestamp."""

    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """Centralized metrics collection and aggregation."""

    def __init__(self):
        self.config = get_monitoring_config().metrics
        self._metrics: Dict[str, Deque[MetricValue]] = defaultdict(lambda: deque(maxlen=10000))
        self._lock = threading.RLock()
        self._process = psutil.Process(os.getpid())

        # Prometheus metrics (if available)
        if PROMETHEUS_AVAILABLE and self.config.prometheus_enabled:
            self.registry = CollectorRegistry()
            self._setup_prometheus_metrics()
        else:
            self.registry = None

        # Start background collection
        self._running = True
        self._collection_thread = threading.Thread(target=self._collect_system_metrics, daemon=True)
        self._collection_thread.start()

        logger.info("Metrics collector initialized", prometheus_enabled=PROMETHEUS_AVAILABLE)

    def _setup_prometheus_metrics(self) -> None:
        """Set up Prometheus metrics."""
        # Detection metrics
        self.prom_detections_total = Counter(
            "ppe_detections_total",
            "Total number of detections",
            ["camera_id", "object_type"],
            registry=self.registry,
        )

        self.prom_violations_total = Counter(
            "ppe_violations_total",
            "Total number of PPE violations",
            ["camera_id", "violation_type"],
            registry=self.registry,
        )

        self.prom_violation_rate = Gauge(
            "ppe_violation_rate",
            "Current violation rate (violations per hour)",
            ["camera_id"],
            registry=self.registry,
        )

        # Camera metrics
        self.prom_camera_uptime = Gauge(
            "ppe_camera_uptime_seconds",
            "Camera uptime in seconds",
            ["camera_id"],
            registry=self.registry,
        )

        self.prom_camera_fps = Gauge(
            "ppe_camera_fps",
            "Camera frames per second",
            ["camera_id"],
            registry=self.registry,
        )

        self.prom_camera_status = Gauge(
            "ppe_camera_status",
            "Camera status (1=online, 0=offline)",
            ["camera_id"],
            registry=self.registry,
        )

        # API metrics
        self.prom_api_requests_total = Counter(
            "ppe_api_requests_total",
            "Total API requests",
            ["method", "endpoint", "status"],
            registry=self.registry,
        )

        self.prom_api_response_time = Histogram(
            "ppe_api_response_time_seconds",
            "API response time in seconds",
            ["method", "endpoint"],
            registry=self.registry,
        )

        # Model metrics
        self.prom_inference_time = Histogram(
            "ppe_model_inference_time_seconds",
            "Model inference time in seconds",
            ["model_name"],
            registry=self.registry,
        )

        self.prom_model_batch_size = Histogram(
            "ppe_model_batch_size",
            "Model inference batch size",
            ["model_name"],
            registry=self.registry,
        )

        # System metrics
        self.prom_cpu_usage = Gauge(
            "ppe_cpu_usage_percent",
            "CPU usage percentage",
            registry=self.registry,
        )

        self.prom_memory_usage = Gauge(
            "ppe_memory_usage_bytes",
            "Memory usage in bytes",
            registry=self.registry,
        )

        self.prom_memory_percent = Gauge(
            "ppe_memory_usage_percent",
            "Memory usage percentage",
            registry=self.registry,
        )

        self.prom_disk_usage = Gauge(
            "ppe_disk_usage_percent",
            "Disk usage percentage",
            ["mount_point"],
            registry=self.registry,
        )

        # GPU metrics (if available)
        try:
            import GPUtil

            self.prom_gpu_usage = Gauge(
                "ppe_gpu_usage_percent",
                "GPU usage percentage",
                ["gpu_id"],
                registry=self.registry,
            )
            self.prom_gpu_memory = Gauge(
                "ppe_gpu_memory_usage_percent",
                "GPU memory usage percentage",
                ["gpu_id"],
                registry=self.registry,
            )
            self._gpu_available = True
        except ImportError:
            self._gpu_available = False

    def record_detection(
        self,
        camera_id: str,
        object_type: str,
        count: int = 1,
        **labels,
    ) -> None:
        """Record detection event."""
        metric_name = "detections_total"
        self._record_metric(metric_name, count, camera_id=camera_id, object_type=object_type, **labels)

        if self.registry:
            self.prom_detections_total.labels(camera_id=camera_id, object_type=object_type).inc(count)

    def record_violation(
        self,
        camera_id: str,
        violation_type: str,
        count: int = 1,
        **labels,
    ) -> None:
        """Record PPE violation."""
        metric_name = "violations_total"
        self._record_metric(metric_name, count, camera_id=camera_id, violation_type=violation_type, **labels)

        if self.registry:
            self.prom_violations_total.labels(camera_id=camera_id, violation_type=violation_type).inc(count)

    def update_violation_rate(self, camera_id: str, rate: float) -> None:
        """Update violation rate."""
        metric_name = "violation_rate"
        self._record_metric(metric_name, rate, camera_id=camera_id)

        if self.registry:
            self.prom_violation_rate.labels(camera_id=camera_id).set(rate)

    def update_camera_uptime(self, camera_id: str, uptime_seconds: float) -> None:
        """Update camera uptime."""
        metric_name = "camera_uptime"
        self._record_metric(metric_name, uptime_seconds, camera_id=camera_id)

        if self.registry:
            self.prom_camera_uptime.labels(camera_id=camera_id).set(uptime_seconds)

    def update_camera_fps(self, camera_id: str, fps: float) -> None:
        """Update camera FPS."""
        metric_name = "camera_fps"
        self._record_metric(metric_name, fps, camera_id=camera_id)

        if self.registry:
            self.prom_camera_fps.labels(camera_id=camera_id).set(fps)

    def update_camera_status(self, camera_id: str, online: bool) -> None:
        """Update camera status."""
        status_value = 1.0 if online else 0.0
        metric_name = "camera_status"
        self._record_metric(metric_name, status_value, camera_id=camera_id)

        if self.registry:
            self.prom_camera_status.labels(camera_id=camera_id).set(status_value)

    def record_api_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        response_time_ms: float,
    ) -> None:
        """Record API request metrics."""
        metric_name = "api_requests"
        self._record_metric(
            metric_name,
            1,
            method=method,
            endpoint=endpoint,
            status=str(status_code),
        )

        if self.registry:
            self.prom_api_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=str(status_code),
            ).inc()
            self.prom_api_response_time.labels(
                method=method,
                endpoint=endpoint,
            ).observe(response_time_ms / 1000.0)

    def record_inference_time(
        self,
        model_name: str,
        inference_time_ms: float,
        batch_size: int = 1,
    ) -> None:
        """Record model inference time."""
        metric_name = "inference_time"
        self._record_metric(metric_name, inference_time_ms, model_name=model_name)

        if self.registry:
            self.prom_inference_time.labels(model_name=model_name).observe(inference_time_ms / 1000.0)
            self.prom_model_batch_size.labels(model_name=model_name).observe(batch_size)

    @contextmanager
    def measure_time(self, operation: str, **labels):
        """Context manager to measure operation time."""
        start_time = time.time()
        try:
            yield
        finally:
            duration_ms = (time.time() - start_time) * 1000
            self._record_metric(f"{operation}_duration", duration_ms, **labels)

    def _record_metric(self, name: str, value: float, **labels) -> None:
        """Record a metric value."""
        with self._lock:
            metric = MetricValue(
                value=value,
                timestamp=datetime.utcnow(),
                labels=labels,
            )
            self._metrics[name].append(metric)

    def _collect_system_metrics(self) -> None:
        """Background thread to collect system metrics."""
        while self._running:
            try:
                # CPU usage
                cpu_percent = self._process.cpu_percent(interval=1)
                self._record_metric("cpu_usage_percent", cpu_percent)
                if self.registry:
                    self.prom_cpu_usage.set(cpu_percent)

                # Memory usage
                memory_info = self._process.memory_info()
                memory_percent = self._process.memory_percent()
                self._record_metric("memory_usage_bytes", memory_info.rss)
                self._record_metric("memory_usage_percent", memory_percent)
                if self.registry:
                    self.prom_memory_usage.set(memory_info.rss)
                    self.prom_memory_percent.set(memory_percent)

                # Disk usage
                disk_usage = psutil.disk_usage("/")
                self._record_metric("disk_usage_percent", disk_usage.percent)
                if self.registry:
                    self.prom_disk_usage.labels(mount_point="/").set(disk_usage.percent)

                # GPU metrics
                if self._gpu_available:
                    try:
                        import GPUtil

                        gpus = GPUtil.getGPUs()
                        for gpu in gpus:
                            self._record_metric("gpu_usage_percent", gpu.load * 100, gpu_id=str(gpu.id))
                            self._record_metric("gpu_memory_percent", gpu.memoryUtil * 100, gpu_id=str(gpu.id))
                            if self.registry:
                                self.prom_gpu_usage.labels(gpu_id=str(gpu.id)).set(gpu.load * 100)
                                self.prom_gpu_memory.labels(gpu_id=str(gpu.id)).set(gpu.memoryUtil * 100)
                    except Exception as e:
                        logger.debug("Failed to collect GPU metrics", error=str(e))

            except Exception as e:
                logger.error("Error collecting system metrics", exc_info=True, error=str(e))

            time.sleep(self.config.system_metrics_interval)

    def get_metrics(
        self,
        name: str,
        since: Optional[datetime] = None,
        **label_filters,
    ) -> List[MetricValue]:
        """Get metrics by name and optional filters."""
        with self._lock:
            metrics = self._metrics.get(name, deque())

            # Filter by timestamp
            if since:
                metrics = [m for m in metrics if m.timestamp >= since]

            # Filter by labels
            if label_filters:
                metrics = [
                    m
                    for m in metrics
                    if all(m.labels.get(k) == v for k, v in label_filters.items())
                ]

            return list(metrics)

    def get_metric_summary(self, name: str, window_minutes: int = 60) -> Dict[str, float]:
        """Get metric summary (min, max, avg, count) for a time window."""
        since = datetime.utcnow() - timedelta(minutes=window_minutes)
        metrics = self.get_metrics(name, since=since)

        if not metrics:
            return {"count": 0, "min": 0, "max": 0, "avg": 0, "sum": 0}

        values = [m.value for m in metrics]
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "sum": sum(values),
        }

    def calculate_hourly_rate(self, metric_name: str, camera_id: Optional[str] = None) -> float:
        """Calculate hourly rate for a metric."""
        since = datetime.utcnow() - timedelta(hours=1)
        filters = {"camera_id": camera_id} if camera_id else {}
        metrics = self.get_metrics(metric_name, since=since, **filters)
        return sum(m.value for m in metrics)

    def get_prometheus_metrics(self) -> bytes:
        """Get metrics in Prometheus format."""
        if not self.registry:
            return b""
        return generate_latest(self.registry)

    def start_prometheus_server(self, port: Optional[int] = None) -> None:
        """Start Prometheus metrics server."""
        if not PROMETHEUS_AVAILABLE:
            logger.warning("Prometheus client not available, cannot start metrics server")
            return

        port = port or self.config.prometheus_port
        try:
            start_http_server(port, registry=self.registry)
            logger.info("Prometheus metrics server started", port=port)
        except Exception as e:
            logger.error("Failed to start Prometheus server", exc_info=True, port=port, error=str(e))

    def export_metrics(self) -> Dict[str, Any]:
        """Export all metrics as dictionary."""
        with self._lock:
            return {
                name: [
                    {
                        "value": m.value,
                        "timestamp": m.timestamp.isoformat(),
                        "labels": m.labels,
                    }
                    for m in metrics
                ]
                for name, metrics in self._metrics.items()
            }

    def cleanup_old_metrics(self, retention_days: Optional[int] = None) -> None:
        """Remove old metrics beyond retention period."""
        retention_days = retention_days or self.config.retention_days
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        with self._lock:
            for name in self._metrics:
                self._metrics[name] = deque(
                    [m for m in self._metrics[name] if m.timestamp >= cutoff_date],
                    maxlen=self._metrics[name].maxlen,
                )

        logger.info("Old metrics cleaned up", retention_days=retention_days)

    def shutdown(self) -> None:
        """Shutdown metrics collector."""
        self._running = False
        if self._collection_thread.is_alive():
            self._collection_thread.join(timeout=5)
        logger.info("Metrics collector shutdown")


# Global metrics collector instance
metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global metrics_collector
    if metrics_collector is None:
        metrics_collector = MetricsCollector()
    return metrics_collector


# Example usage
if __name__ == "__main__":
    from .logger import setup_logging

    setup_logging()

    # Initialize metrics collector
    collector = get_metrics_collector()

    # Record some metrics
    collector.record_detection("camera_01", "person", count=1)
    collector.record_violation("camera_01", "no_helmet", count=1)
    collector.update_camera_fps("camera_01", 30.0)
    collector.record_api_request("GET", "/api/detections", 200, 45.2)
    collector.record_inference_time("yolov8", 42.5, batch_size=1)

    # Get metric summaries
    print("Detection summary:", collector.get_metric_summary("detections_total"))
    print("Hourly detection rate:", collector.calculate_hourly_rate("detections_total"))

    # Start Prometheus server (optional)
    # collector.start_prometheus_server(9090)

    time.sleep(2)
    collector.shutdown()
