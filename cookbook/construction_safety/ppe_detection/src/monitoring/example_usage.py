"""
Example usage of the PPE detection monitoring infrastructure.

This script demonstrates how to use all components of the monitoring system:
- Structured logging
- Metrics collection
- Health checks
- Performance monitoring
"""

import asyncio
import random
import time
from datetime import datetime

from logger import setup_logging, get_logger, get_detection_logger, get_camera_logger, get_alert_logger
from metrics import get_metrics_collector
from health_check import get_health_checker, HealthStatus
from performance_monitor import get_performance_monitor
from monitoring_config import get_monitoring_config


def main():
    """Main example function."""
    print("=" * 80)
    print("PPE Detection Monitoring Infrastructure - Example Usage")
    print("=" * 80)

    # 1. Initialize logging
    print("\n1. Initializing Logging System...")
    setup_logging()

    app_logger = get_logger(__name__)
    detection_logger = get_detection_logger(__name__)
    camera_logger = get_camera_logger(__name__)
    alert_logger = get_alert_logger(__name__)

    app_logger.info("Monitoring system started", version="1.0.0", environment="development")

    # 2. Initialize metrics collector
    print("\n2. Initializing Metrics Collector...")
    metrics = get_metrics_collector()

    # Start Prometheus server (comment out if you don't want to run the server)
    # metrics.start_prometheus_server(9090)
    # print("   Prometheus metrics available at: http://localhost:9090/metrics")

    # 3. Initialize health checker
    print("\n3. Initializing Health Checker...")
    health_checker = get_health_checker()

    # 4. Initialize performance monitor
    print("\n4. Initializing Performance Monitor...")
    perf_monitor = get_performance_monitor()

    # 5. Simulate some operations
    print("\n5. Simulating PPE Detection Operations...")
    simulate_operations(
        app_logger,
        detection_logger,
        camera_logger,
        alert_logger,
        metrics,
        perf_monitor,
    )

    # 6. Run health checks
    print("\n6. Running Health Checks...")
    asyncio.run(run_health_checks(health_checker))

    # 7. Display metrics summary
    print("\n7. Metrics Summary:")
    display_metrics_summary(metrics)

    # 8. Display performance stats
    print("\n8. Performance Statistics:")
    display_performance_stats(perf_monitor)

    # 9. Check for bottlenecks
    print("\n9. Bottleneck Analysis:")
    check_bottlenecks(perf_monitor)

    # 10. Generate performance report
    print("\n10. Generating Performance Report...")
    report = perf_monitor.generate_report(window_minutes=60)
    print(f"   Report timestamp: {report['timestamp']}")
    print(f"   Window: {report['window_minutes']} minutes")
    print(f"   Tracked operations: {len(report['operations'])}")
    print(f"   Detected bottlenecks: {len(report['bottlenecks'])}")

    # Cleanup
    print("\n11. Shutting down...")
    metrics.shutdown()
    perf_monitor.shutdown()

    print("\nExample completed successfully!")
    print("=" * 80)


def simulate_operations(
    app_logger,
    detection_logger,
    camera_logger,
    alert_logger,
    metrics,
    perf_monitor,
):
    """Simulate PPE detection operations."""
    cameras = ["camera_01", "camera_02", "camera_03"]
    violation_types = ["no_helmet", "no_vest", "no_gloves", "no_goggles"]

    print("\n   Simulating 20 detection cycles...")

    for i in range(20):
        camera_id = random.choice(cameras)

        # Simulate camera status update
        if i % 5 == 0:
            fps = random.uniform(25, 35)
            metrics.update_camera_fps(camera_id, fps)
            metrics.update_camera_status(camera_id, True)
            camera_logger.log_camera_event(
                camera_id=camera_id,
                event_type="status_update",
                status="online",
                fps=fps,
            )

        # Simulate detection with performance tracking
        with perf_monitor.measure("detection_cycle", camera_id=camera_id):
            # Simulate model inference
            with perf_monitor.measure("model_inference", model="yolov8"):
                inference_time = random.uniform(30, 60)
                time.sleep(inference_time / 1000)  # Simulate processing

            # Random detections
            num_detections = random.randint(0, 5)
            detections = []
            violations = []

            for _ in range(num_detections):
                # Simulate detection
                detection = {
                    "type": "person",
                    "confidence": random.uniform(0.8, 0.99),
                    "bbox": [
                        random.randint(0, 1920),
                        random.randint(0, 1080),
                        random.randint(100, 300),
                        random.randint(100, 300),
                    ],
                }
                detections.append(detection)

                # Record detection metric
                metrics.record_detection(camera_id, "person", count=1)

                # Random violation (30% chance)
                if random.random() < 0.3:
                    violation_type = random.choice(violation_types)
                    violation = {
                        "type": violation_type,
                        "confidence": random.uniform(0.7, 0.95),
                    }
                    violations.append(violation)

                    # Record violation metric
                    metrics.record_violation(camera_id, violation_type, count=1)

                    # Log violation
                    detection_logger.log_violation(
                        camera_id=camera_id,
                        violation_type=violation_type,
                        confidence=violation["confidence"],
                    )

                    # Simulate alert
                    if random.random() < 0.5:
                        alert_logger.log_alert_sent(
                            alert_type="email",
                            recipient="supervisor@example.com",
                            success=True,
                            violation_type=violation_type,
                            camera_id=camera_id,
                        )

            # Log detection event
            detection_logger.log_detection(
                camera_id=camera_id,
                detections=detections,
                violations=violations,
                inference_time_ms=inference_time,
            )

            # Simulate API response
            with perf_monitor.measure("api_request", method="GET", endpoint="/detections"):
                api_time = random.uniform(10, 50)
                time.sleep(api_time / 1000)

            # Record API metric
            status_code = random.choice([200, 200, 200, 200, 500])  # 80% success
            metrics.record_api_request("GET", "/detections", status_code, api_time)

            # Record inference time
            metrics.record_inference_time("yolov8", inference_time, batch_size=1)

        # Small delay between cycles
        time.sleep(0.1)

    print("   Detection cycles completed")


async def run_health_checks(health_checker):
    """Run health checks."""
    print("\n   Running system health checks...")

    # Run all checks
    health = await health_checker.run_all_checks(
        include_database=False,  # Set to True if database is available
        include_cameras=False,  # Set to True if cameras are available
        include_model=False,  # Set to True if model is available
    )

    print(f"\n   Overall Status: {health.status.value.upper()}")
    print(f"   System Uptime: {health.uptime_seconds:.2f} seconds")
    print(f"\n   Component Checks:")

    for check in health.checks:
        status_symbol = "✓" if check.status == HealthStatus.HEALTHY else "✗"
        print(f"     {status_symbol} {check.component:15s} - {check.message}")
        if check.details:
            for key, value in check.details.items():
                print(f"         {key}: {value}")


def display_metrics_summary(metrics):
    """Display metrics summary."""
    # Hourly rates
    detection_rate = metrics.calculate_hourly_rate("detections_total")
    violation_rate = metrics.calculate_hourly_rate("violations_total")

    print(f"\n   Hourly Rates:")
    print(f"     Detections: {detection_rate:.1f}/hour")
    print(f"     Violations: {violation_rate:.1f}/hour")

    # Get summaries for key metrics
    metrics_to_check = [
        ("detections_total", "Detections"),
        ("violations_total", "Violations"),
        ("camera_fps", "Camera FPS"),
        ("cpu_usage_percent", "CPU Usage"),
        ("memory_usage_percent", "Memory Usage"),
    ]

    print(f"\n   Metric Summaries (last 60 minutes):")
    for metric_name, display_name in metrics_to_check:
        summary = metrics.get_metric_summary(metric_name, window_minutes=60)
        if summary["count"] > 0:
            print(f"\n     {display_name}:")
            print(f"       Count:   {summary['count']}")
            print(f"       Min:     {summary['min']:.2f}")
            print(f"       Max:     {summary['max']:.2f}")
            print(f"       Avg:     {summary['avg']:.2f}")
            print(f"       Sum:     {summary['sum']:.2f}")


def display_performance_stats(perf_monitor):
    """Display performance statistics."""
    all_stats = perf_monitor.get_all_stats(window_minutes=60)

    if not all_stats:
        print("   No performance data available")
        return

    for operation, stats in all_stats.items():
        print(f"\n   {operation}:")
        print(f"     Count:        {stats.count}")
        print(f"     Min:          {stats.min_ms:.2f}ms")
        print(f"     Max:          {stats.max_ms:.2f}ms")
        print(f"     Avg:          {stats.avg_ms:.2f}ms")
        print(f"     Median:       {stats.median_ms:.2f}ms")
        print(f"     P95:          {stats.p95_ms:.2f}ms")
        print(f"     P99:          {stats.p99_ms:.2f}ms")
        print(f"     Error Rate:   {stats.error_rate * 100:.2f}%")
        print(f"     Throughput:   {stats.throughput_per_sec:.2f}/sec")


def check_bottlenecks(perf_monitor):
    """Check for performance bottlenecks."""
    bottlenecks = perf_monitor.identify_bottlenecks()

    if not bottlenecks:
        print("   No bottlenecks detected")
        return

    print(f"   Detected {len(bottlenecks)} bottleneck(s):\n")

    for bottleneck in bottlenecks:
        print(f"   Component: {bottleneck.component}")
        print(f"     Severity:  {bottleneck.severity.value}")
        print(f"     Issue:     {bottleneck.description}")
        print(f"     Current:   {bottleneck.current_value:.2f}")
        print(f"     Threshold: {bottleneck.threshold_value:.2f}")

        if bottleneck.suggestions:
            print(f"     Suggestions:")
            for suggestion in bottleneck.suggestions:
                print(f"       - {suggestion}")
        print()


if __name__ == "__main__":
    main()
