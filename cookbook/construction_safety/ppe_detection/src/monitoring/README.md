# PPE Detection Monitoring Infrastructure

Comprehensive logging and monitoring system for the PPE detection application with support for Prometheus, Grafana, ELK Stack, and AWS CloudWatch.

## Features

- **Structured Logging**: JSON-formatted logs with multiple log levels and categories
- **Metrics Collection**: Prometheus-compatible metrics for detections, violations, performance, and system resources
- **Health Checks**: Comprehensive health monitoring for database, cameras, models, and system resources
- **Performance Monitoring**: Real-time performance tracking with bottleneck detection
- **Async Support**: Asynchronous logging for high-performance applications

## Components

### 1. Logger (`logger.py`)

Structured logging with JSON format, log rotation, and async support.

**Features:**
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Separate log files for:
  - Application logs
  - Detection logs
  - Camera logs
  - Alert logs
- Log rotation (100MB per file, keep 10 files)
- Async logging for performance

**Usage:**

```python
from monitoring import setup_logging, get_logger, get_detection_logger

# Initialize logging
setup_logging()

# Get loggers
logger = get_logger(__name__)
detection_logger = get_detection_logger(__name__)

# Log messages
logger.info("Application started", version="1.0.0")

# Log detection event
detection_logger.log_detection(
    camera_id="camera_01",
    detections=[{"type": "person", "confidence": 0.95}],
    violations=[{"type": "no_helmet", "confidence": 0.88}],
    inference_time_ms=45.2,
)
```

### 2. Metrics (`metrics.py`)

Prometheus-compatible metrics collection and export.

**Tracked Metrics:**
- Detection count per hour
- Violation rate
- Camera uptime and FPS
- API response times
- Model inference time
- CPU/Memory/GPU usage

**Usage:**

```python
from monitoring import get_metrics_collector

collector = get_metrics_collector()

# Record metrics
collector.record_detection("camera_01", "person", count=1)
collector.record_violation("camera_01", "no_helmet", count=1)
collector.update_camera_fps("camera_01", 30.0)
collector.record_api_request("GET", "/api/detections", 200, 45.2)
collector.record_inference_time("yolov8", 42.5, batch_size=1)

# Start Prometheus server
collector.start_prometheus_server(9090)

# Get metrics summary
stats = collector.get_metric_summary("detections_total")
print(f"Total detections: {stats['sum']}, Avg: {stats['avg']}")
```

### 3. Health Check (`health_check.py`)

Comprehensive health monitoring system.

**Checks:**
- Database connectivity
- Camera connectivity
- Model availability
- Disk space
- Memory usage
- CPU usage
- Process health

**Usage:**

```python
import asyncio
from monitoring import get_health_checker

async def main():
    checker = get_health_checker()

    # Run all checks
    health = await checker.run_all_checks(
        include_database=True,
        include_cameras=True,
        include_model=True,
        camera_ids=["camera_01", "camera_02"],
    )

    print(f"System Status: {health.status.value}")
    for check in health.checks:
        print(f"  {check.component}: {check.status.value}")

asyncio.run(main())
```

### 4. Performance Monitor (`performance_monitor.py`)

Real-time performance tracking and bottleneck detection.

**Features:**
- Measure operation duration
- Track performance statistics (min, max, avg, p95, p99)
- Detect performance degradation
- Identify bottlenecks
- Resource usage monitoring

**Usage:**

```python
from monitoring import get_performance_monitor

monitor = get_performance_monitor()

# Measure operation performance
with monitor.measure("api_request", endpoint="/detections"):
    # Your code here
    process_request()

# Get performance stats
stats = monitor.get_stats("api_request")
print(f"P95 latency: {stats.p95_ms:.2f}ms")

# Identify bottlenecks
bottlenecks = monitor.identify_bottlenecks()
for bottleneck in bottlenecks:
    print(f"Bottleneck: {bottleneck.component} - {bottleneck.description}")

# Generate performance report
report = monitor.generate_report(window_minutes=60)
```

### 5. Configuration (`monitoring_config.py`)

Centralized configuration for all monitoring components.

**Configuration via Environment Variables:**

```bash
# Logging
export LOG_DIR=/var/log/ppe-detection
export LOG_LEVEL=INFO

# Metrics
export PROMETHEUS_PORT=9090

# Health Checks
export MIN_DISK_SPACE_GB=10

# Performance
export MAX_CPU_PERCENT=80
export MAX_MEMORY_PERCENT=85

# Alerts
export ALERT_EMAIL_RECIPIENTS=admin@example.com,ops@example.com
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Export
export ELASTICSEARCH_URL=http://localhost:9200
export CLOUDWATCH_REGION=us-east-1
```

## Installation

### Required Dependencies

```bash
pip install prometheus-client psutil
```

### Optional Dependencies

```bash
# For GPU monitoring
pip install GPUtil

# For ELK Stack integration
pip install elasticsearch

# For AWS CloudWatch
pip install boto3
```

## Integration

### Prometheus

1. Start the metrics server:

```python
from monitoring import get_metrics_collector

collector = get_metrics_collector()
collector.start_prometheus_server(9090)
```

2. Configure Prometheus to scrape metrics:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'ppe-detection'
    static_configs:
      - targets: ['localhost:9090']
```

### Grafana

1. Import the dashboard:
   - Copy `grafana_dashboard.json`
   - In Grafana: Create > Import > Upload JSON file

2. Configure data source:
   - Add Prometheus data source
   - URL: `http://localhost:9090`

### ELK Stack

Enable Elasticsearch export in configuration:

```python
from monitoring import get_monitoring_config, set_monitoring_config

config = get_monitoring_config()
config.export.elasticsearch_enabled = True
config.export.elasticsearch_url = "http://localhost:9200"
config.export.elasticsearch_index = "ppe-detection"
set_monitoring_config(config)
```

### AWS CloudWatch

Enable CloudWatch export:

```python
config.export.cloudwatch_enabled = True
config.export.cloudwatch_region = "us-east-1"
config.export.cloudwatch_namespace = "PPEDetection"
```

## Example Dashboard

The included Grafana dashboard (`grafana_dashboard.json`) provides:

- **System Overview**: Total detections, violations, violation rate, active cameras
- **Detection Trends**: Real-time detection and violation charts by camera and type
- **Performance Metrics**: API response times and model inference times with alerts
- **System Resources**: CPU, memory, disk usage with thresholds
- **Camera Status**: FPS and uptime monitoring
- **GPU Metrics**: GPU usage and memory (if available)
- **API Metrics**: Request rates and status codes

## Alerts

Configure alerts in the monitoring configuration:

```python
config.alerts.violation_rate_threshold = 0.5  # 50% violation rate
config.alerts.high_violation_count = 10  # violations per hour
config.alerts.camera_offline_duration_minutes = 5

# Email alerts
config.alerts.enable_email_alerts = True
config.alerts.email_recipients = ["admin@example.com"]
config.alerts.email_smtp_server = "smtp.example.com"
config.alerts.email_smtp_port = 587

# Slack alerts
config.alerts.enable_slack_alerts = True
config.alerts.slack_webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

## Best Practices

1. **Log Levels**: Use appropriate log levels
   - DEBUG: Detailed diagnostic information
   - INFO: General informational messages
   - WARNING: Warning messages for potential issues
   - ERROR: Error messages for failures
   - CRITICAL: Critical issues requiring immediate attention

2. **Metrics**: Record metrics at appropriate intervals
   - High-frequency metrics (detections, API requests): Real-time
   - System metrics: Every 30 seconds
   - Aggregated metrics: Every 5-10 minutes

3. **Health Checks**: Run health checks periodically
   - Critical components: Every 1 minute
   - Non-critical components: Every 5 minutes

4. **Performance Monitoring**: Set baselines for operations
   ```python
   monitor.set_baseline("api_request", baseline_ms=100)
   monitor.set_baseline("model_inference", baseline_ms=50)
   ```

5. **Resource Limits**: Configure appropriate thresholds
   - CPU: 80% warning, 95% critical
   - Memory: 85% warning, 95% critical
   - Disk: 80% warning, 90% critical

## Troubleshooting

### High Memory Usage

```python
# Check memory stats
stats = collector.get_metric_summary("memory_usage_percent")
print(f"Memory usage: {stats['avg']:.1f}%")

# Cleanup old metrics
collector.cleanup_old_metrics(retention_days=7)
```

### Performance Degradation

```python
# Identify bottlenecks
bottlenecks = monitor.identify_bottlenecks()
for bottleneck in bottlenecks:
    print(f"{bottleneck.component}: {bottleneck.description}")
    print(f"Current: {bottleneck.current_value:.2f}, Threshold: {bottleneck.threshold_value:.2f}")
    print("Suggestions:")
    for suggestion in bottleneck.suggestions:
        print(f"  - {suggestion}")
```

### Camera Offline

```python
# Check camera health
result = await checker.check_camera("camera_01")
if result.status != HealthStatus.HEALTHY:
    print(f"Camera offline: {result.message}")
    # Trigger alerts, restart camera, etc.
```

## License

MIT License
