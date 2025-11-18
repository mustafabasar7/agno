"""
Real-time performance monitoring and bottleneck detection.
"""

import asyncio
import statistics
import threading
import time
from collections import defaultdict, deque
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Deque, Dict, List, Optional, Tuple

import psutil

from .logger import get_logger
from .metrics import get_metrics_collector
from .monitoring_config import get_monitoring_config

logger = get_logger(__name__)


class PerformanceLevel(Enum):
    """Performance level indicators."""

    EXCELLENT = "excellent"
    GOOD = "good"
    DEGRADED = "degraded"
    POOR = "poor"


@dataclass
class PerformanceMeasurement:
    """Individual performance measurement."""

    operation: str
    duration_ms: float
    timestamp: datetime
    success: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceStats:
    """Performance statistics for an operation."""

    operation: str
    count: int
    min_ms: float
    max_ms: float
    avg_ms: float
    median_ms: float
    p95_ms: float
    p99_ms: float
    error_rate: float
    throughput_per_sec: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "operation": self.operation,
            "count": self.count,
            "min_ms": round(self.min_ms, 2),
            "max_ms": round(self.max_ms, 2),
            "avg_ms": round(self.avg_ms, 2),
            "median_ms": round(self.median_ms, 2),
            "p95_ms": round(self.p95_ms, 2),
            "p99_ms": round(self.p99_ms, 2),
            "error_rate": round(self.error_rate, 4),
            "throughput_per_sec": round(self.throughput_per_sec, 2),
        }


@dataclass
class BottleneckInfo:
    """Information about detected performance bottleneck."""

    component: str
    severity: PerformanceLevel
    description: str
    current_value: float
    threshold_value: float
    timestamp: datetime
    suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "component": self.component,
            "severity": self.severity.value,
            "description": self.description,
            "current_value": round(self.current_value, 2),
            "threshold_value": round(self.threshold_value, 2),
            "timestamp": self.timestamp.isoformat() + "Z",
            "suggestions": self.suggestions,
        }


class PerformanceMonitor:
    """Real-time performance monitoring and analysis."""

    def __init__(self):
        self.config = get_monitoring_config().performance
        self.metrics_collector = get_metrics_collector()

        # Performance measurements storage
        self._measurements: Dict[str, Deque[PerformanceMeasurement]] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        self._lock = threading.RLock()

        # Baseline performance metrics
        self._baselines: Dict[str, float] = {}

        # Detected bottlenecks
        self._bottlenecks: List[BottleneckInfo] = []

        # Resource monitoring
        self._resource_samples: Deque[Dict[str, float]] = deque(maxlen=100)

        # Background monitoring
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

        logger.info("Performance monitor initialized")

    @contextmanager
    def measure(self, operation: str, **metadata):
        """Context manager to measure operation performance."""
        start_time = time.time()
        success = True
        error = None

        try:
            yield
        except Exception as e:
            success = False
            error = str(e)
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000

            # Record measurement
            measurement = PerformanceMeasurement(
                operation=operation,
                duration_ms=duration_ms,
                timestamp=datetime.utcnow(),
                success=success,
                metadata={**metadata, "error": error} if error else metadata,
            )

            with self._lock:
                self._measurements[operation].append(measurement)

            # Record to metrics collector
            self.metrics_collector._record_metric(
                f"performance_{operation}",
                duration_ms,
                success=success,
                **metadata,
            )

            # Check for performance degradation
            if self.config.enable_degradation_detection:
                self._check_degradation(operation, duration_ms)

            logger.log_performance(operation, duration_ms, success=success, **metadata)

    async def measure_async(self, operation: str, **metadata):
        """Async context manager to measure operation performance."""
        start_time = time.time()
        success = True
        error = None

        try:
            yield
        except Exception as e:
            success = False
            error = str(e)
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000

            measurement = PerformanceMeasurement(
                operation=operation,
                duration_ms=duration_ms,
                timestamp=datetime.utcnow(),
                success=success,
                metadata={**metadata, "error": error} if error else metadata,
            )

            with self._lock:
                self._measurements[operation].append(measurement)

            self.metrics_collector._record_metric(
                f"performance_{operation}",
                duration_ms,
                success=success,
                **metadata,
            )

    def record_measurement(
        self,
        operation: str,
        duration_ms: float,
        success: bool = True,
        **metadata,
    ) -> None:
        """Manually record a performance measurement."""
        measurement = PerformanceMeasurement(
            operation=operation,
            duration_ms=duration_ms,
            timestamp=datetime.utcnow(),
            success=success,
            metadata=metadata,
        )

        with self._lock:
            self._measurements[operation].append(measurement)

        self.metrics_collector._record_metric(
            f"performance_{operation}",
            duration_ms,
            success=success,
            **metadata,
        )

    def get_stats(
        self,
        operation: str,
        window_minutes: Optional[int] = None,
    ) -> Optional[PerformanceStats]:
        """Get performance statistics for an operation."""
        with self._lock:
            measurements = list(self._measurements.get(operation, []))

        if not measurements:
            return None

        # Filter by time window if specified
        if window_minutes:
            cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
            measurements = [m for m in measurements if m.timestamp >= cutoff]

        if not measurements:
            return None

        durations = [m.duration_ms for m in measurements]
        errors = [m for m in measurements if not m.success]

        # Calculate time range for throughput
        time_range_seconds = (
            (measurements[-1].timestamp - measurements[0].timestamp).total_seconds()
            or 1
        )

        return PerformanceStats(
            operation=operation,
            count=len(measurements),
            min_ms=min(durations),
            max_ms=max(durations),
            avg_ms=statistics.mean(durations),
            median_ms=statistics.median(durations),
            p95_ms=self._percentile(durations, 95),
            p99_ms=self._percentile(durations, 99),
            error_rate=len(errors) / len(measurements) if measurements else 0,
            throughput_per_sec=len(measurements) / time_range_seconds,
        )

    def get_all_stats(self, window_minutes: Optional[int] = None) -> Dict[str, PerformanceStats]:
        """Get performance statistics for all operations."""
        with self._lock:
            operations = list(self._measurements.keys())

        stats = {}
        for operation in operations:
            op_stats = self.get_stats(operation, window_minutes)
            if op_stats:
                stats[operation] = op_stats

        return stats

    def set_baseline(self, operation: str, baseline_ms: Optional[float] = None) -> None:
        """Set performance baseline for an operation."""
        if baseline_ms is None:
            # Calculate from current stats
            stats = self.get_stats(operation)
            if stats:
                baseline_ms = stats.median_ms
            else:
                logger.warning("No stats available to set baseline", operation=operation)
                return

        self._baselines[operation] = baseline_ms
        logger.info("Performance baseline set", operation=operation, baseline_ms=baseline_ms)

    def _check_degradation(self, operation: str, duration_ms: float) -> None:
        """Check for performance degradation."""
        baseline = self._baselines.get(operation)
        if not baseline:
            return

        # Calculate degradation percentage
        degradation_percent = ((duration_ms - baseline) / baseline) * 100

        if degradation_percent > self.config.degradation_threshold_percent:
            logger.warning(
                "Performance degradation detected",
                operation=operation,
                current_ms=duration_ms,
                baseline_ms=baseline,
                degradation_percent=degradation_percent,
            )

            # Create bottleneck info
            severity = PerformanceLevel.DEGRADED if degradation_percent < 50 else PerformanceLevel.POOR

            bottleneck = BottleneckInfo(
                component=operation,
                severity=severity,
                description=f"Performance degraded by {degradation_percent:.1f}%",
                current_value=duration_ms,
                threshold_value=baseline,
                timestamp=datetime.utcnow(),
                suggestions=[
                    "Check system resources (CPU, memory)",
                    "Review recent code changes",
                    "Analyze operation logs for errors",
                ],
            )

            with self._lock:
                self._bottlenecks.append(bottleneck)
                # Keep only recent bottlenecks
                if len(self._bottlenecks) > 100:
                    self._bottlenecks = self._bottlenecks[-100:]

    def identify_bottlenecks(self) -> List[BottleneckInfo]:
        """Identify current performance bottlenecks."""
        bottlenecks = []

        # Check response times
        if self.config.track_response_times:
            api_stats = self.get_stats("api_request", window_minutes=5)
            if api_stats and api_stats.p95_ms > self.config.max_response_time_ms:
                bottlenecks.append(
                    BottleneckInfo(
                        component="api_response",
                        severity=PerformanceLevel.DEGRADED,
                        description="API response time exceeds threshold",
                        current_value=api_stats.p95_ms,
                        threshold_value=self.config.max_response_time_ms,
                        timestamp=datetime.utcnow(),
                        suggestions=[
                            "Enable caching for frequently accessed data",
                            "Optimize database queries",
                            "Consider horizontal scaling",
                        ],
                    )
                )

        # Check inference times
        if self.config.track_inference_times:
            inference_stats = self.get_stats("model_inference", window_minutes=5)
            if inference_stats and inference_stats.p95_ms > self.config.max_inference_time_ms:
                bottlenecks.append(
                    BottleneckInfo(
                        component="model_inference",
                        severity=PerformanceLevel.DEGRADED,
                        description="Model inference time exceeds threshold",
                        current_value=inference_stats.p95_ms,
                        threshold_value=self.config.max_inference_time_ms,
                        timestamp=datetime.utcnow(),
                        suggestions=[
                            "Use smaller model or quantization",
                            "Enable GPU acceleration",
                            "Increase batch size",
                            "Use model optimization (TensorRT, ONNX)",
                        ],
                    )
                )

        # Check system resources
        resource_bottlenecks = self._check_resource_bottlenecks()
        bottlenecks.extend(resource_bottlenecks)

        # Add recent degradation bottlenecks
        with self._lock:
            recent_cutoff = datetime.utcnow() - timedelta(minutes=5)
            recent_bottlenecks = [
                b for b in self._bottlenecks if b.timestamp >= recent_cutoff
            ]
            bottlenecks.extend(recent_bottlenecks)

        return bottlenecks

    def _check_resource_bottlenecks(self) -> List[BottleneckInfo]:
        """Check for resource-related bottlenecks."""
        bottlenecks = []

        try:
            # CPU check
            cpu_percent = psutil.cpu_percent(interval=0.1)
            if cpu_percent > self.config.max_cpu_percent:
                bottlenecks.append(
                    BottleneckInfo(
                        component="cpu",
                        severity=PerformanceLevel.DEGRADED,
                        description="High CPU usage",
                        current_value=cpu_percent,
                        threshold_value=self.config.max_cpu_percent,
                        timestamp=datetime.utcnow(),
                        suggestions=[
                            "Optimize CPU-intensive operations",
                            "Use multiprocessing for parallel tasks",
                            "Consider upgrading CPU",
                        ],
                    )
                )

            # Memory check
            memory = psutil.virtual_memory()
            if memory.percent > self.config.max_memory_percent:
                bottlenecks.append(
                    BottleneckInfo(
                        component="memory",
                        severity=PerformanceLevel.DEGRADED,
                        description="High memory usage",
                        current_value=memory.percent,
                        threshold_value=self.config.max_memory_percent,
                        timestamp=datetime.utcnow(),
                        suggestions=[
                            "Check for memory leaks",
                            "Reduce batch sizes",
                            "Implement caching with size limits",
                            "Add more RAM",
                        ],
                    )
                )

            # GPU check (if available)
            try:
                import GPUtil

                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    gpu_memory_percent = gpu.memoryUtil * 100
                    if gpu_memory_percent > self.config.max_gpu_memory_percent:
                        bottlenecks.append(
                            BottleneckInfo(
                                component=f"gpu_{gpu.id}",
                                severity=PerformanceLevel.DEGRADED,
                                description=f"High GPU memory usage on GPU {gpu.id}",
                                current_value=gpu_memory_percent,
                                threshold_value=self.config.max_gpu_memory_percent,
                                timestamp=datetime.utcnow(),
                                suggestions=[
                                    "Reduce model batch size",
                                    "Use mixed precision training/inference",
                                    "Clear GPU cache regularly",
                                ],
                            )
                        )
            except ImportError:
                pass

        except Exception as e:
            logger.error("Error checking resource bottlenecks", exc_info=True, error=str(e))

        return bottlenecks

    def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while self._running:
            try:
                # Sample current resources
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()

                sample = {
                    "timestamp": time.time(),
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / (1024**3),
                }

                # Add GPU metrics if available
                try:
                    import GPUtil

                    gpus = GPUtil.getGPUs()
                    for i, gpu in enumerate(gpus):
                        sample[f"gpu_{i}_usage"] = gpu.load * 100
                        sample[f"gpu_{i}_memory"] = gpu.memoryUtil * 100
                except ImportError:
                    pass

                self._resource_samples.append(sample)

                # Check for alerts
                if cpu_percent > self.config.max_cpu_percent:
                    logger.warning("High CPU usage detected", cpu_percent=cpu_percent)

                if memory.percent > self.config.max_memory_percent:
                    logger.warning("High memory usage detected", memory_percent=memory.percent)

            except Exception as e:
                logger.error("Error in performance monitoring loop", exc_info=True, error=str(e))

            time.sleep(10)  # Sample every 10 seconds

    def get_resource_trends(self, window_minutes: int = 15) -> Dict[str, Dict[str, float]]:
        """Get resource usage trends over time window."""
        cutoff_time = time.time() - (window_minutes * 60)

        samples = [s for s in self._resource_samples if s["timestamp"] >= cutoff_time]

        if not samples:
            return {}

        trends = {}

        # CPU trends
        cpu_values = [s["cpu_percent"] for s in samples]
        trends["cpu"] = {
            "min": min(cpu_values),
            "max": max(cpu_values),
            "avg": statistics.mean(cpu_values),
            "current": cpu_values[-1] if cpu_values else 0,
        }

        # Memory trends
        memory_values = [s["memory_percent"] for s in samples]
        trends["memory"] = {
            "min": min(memory_values),
            "max": max(memory_values),
            "avg": statistics.mean(memory_values),
            "current": memory_values[-1] if memory_values else 0,
        }

        return trends

    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * (percentile / 100))
        index = min(index, len(sorted_data) - 1)
        return sorted_data[index]

    def generate_report(self, window_minutes: int = 60) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        all_stats = self.get_all_stats(window_minutes)
        bottlenecks = self.identify_bottlenecks()
        resource_trends = self.get_resource_trends(window_minutes)

        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "window_minutes": window_minutes,
            "operations": {op: stats.to_dict() for op, stats in all_stats.items()},
            "bottlenecks": [b.to_dict() for b in bottlenecks],
            "resource_trends": resource_trends,
        }

    def shutdown(self) -> None:
        """Shutdown performance monitor."""
        self._running = False
        if self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5)
        logger.info("Performance monitor shutdown")


# Global performance monitor instance
performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global performance_monitor
    if performance_monitor is None:
        performance_monitor = PerformanceMonitor()
    return performance_monitor


# Example usage
if __name__ == "__main__":
    from .logger import setup_logging

    setup_logging()

    monitor = get_performance_monitor()

    # Simulate some operations
    for i in range(10):
        with monitor.measure("api_request", endpoint="/detections"):
            time.sleep(0.05)  # Simulate work

        with monitor.measure("model_inference", model="yolov8"):
            time.sleep(0.03)  # Simulate inference

    # Get stats
    print("\nPerformance Stats:")
    for operation, stats in monitor.get_all_stats().items():
        print(f"\n{operation}:")
        print(f"  Count: {stats.count}")
        print(f"  Avg: {stats.avg_ms:.2f}ms")
        print(f"  P95: {stats.p95_ms:.2f}ms")
        print(f"  Throughput: {stats.throughput_per_sec:.2f}/s")

    # Check bottlenecks
    bottlenecks = monitor.identify_bottlenecks()
    if bottlenecks:
        print("\nDetected Bottlenecks:")
        for bottleneck in bottlenecks:
            print(f"  {bottleneck.component}: {bottleneck.description}")

    time.sleep(2)
    monitor.shutdown()
