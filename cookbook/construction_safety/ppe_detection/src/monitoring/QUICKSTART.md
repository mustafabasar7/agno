# Quick Start Guide - PPE Detection Monitoring

Get started with the monitoring infrastructure in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose (optional, for Prometheus/Grafana)

## Step 1: Install Dependencies

```bash
cd /home/user/agno/cookbook/construction_safety/ppe_detection/src/monitoring
pip install -r requirements.txt
```

## Step 2: Run Example

```bash
python example_usage.py
```

This will:
- Initialize the logging system
- Collect metrics from simulated operations
- Run health checks
- Display performance statistics
- Identify any bottlenecks

## Step 3: View Logs

Logs are stored in `logs/` directory:

```bash
# View application logs
tail -f logs/application.log | jq

# View detection logs
tail -f logs/detection.log | jq

# View camera logs
tail -f logs/camera.log | jq

# View alert logs
tail -f logs/alert.log | jq
```

## Step 4: Start Prometheus & Grafana (Optional)

```bash
# Start monitoring stack
docker-compose up -d

# View logs
docker-compose logs -f

# Stop monitoring stack
docker-compose down
```

Access the dashboards:
- Prometheus: http://localhost:9091
- Grafana: http://localhost:3000 (admin/admin)

## Step 5: Integrate with Your Application

```python
from monitoring import (
    setup_logging,
    get_logger,
    get_metrics_collector,
    get_performance_monitor,
)

# Initialize
setup_logging()
logger = get_logger(__name__)
metrics = get_metrics_collector()
perf = get_performance_monitor()

# Start Prometheus server
metrics.start_prometheus_server(9090)

# Log messages
logger.info("Application started")

# Record metrics
metrics.record_detection("camera_01", "person", count=1)
metrics.record_violation("camera_01", "no_helmet", count=1)

# Measure performance
with perf.measure("api_request", endpoint="/detections"):
    # Your code here
    process_request()
```

## Common Use Cases

### 1. Track Detection Events

```python
from monitoring import get_detection_logger, get_metrics_collector

logger = get_detection_logger(__name__)
metrics = get_metrics_collector()

# Log and record detection
logger.log_detection(
    camera_id="camera_01",
    detections=[{"type": "person", "confidence": 0.95}],
    violations=[{"type": "no_helmet", "confidence": 0.88}],
    inference_time_ms=45.2,
)

metrics.record_detection("camera_01", "person", count=1)
metrics.record_violation("camera_01", "no_helmet", count=1)
```

### 2. Monitor API Performance

```python
from monitoring import get_performance_monitor, get_metrics_collector

perf = get_performance_monitor()
metrics = get_metrics_collector()

# Measure API request
with perf.measure("api_request", method="GET", endpoint="/detections"):
    response = handle_request()

# Record API metrics
metrics.record_api_request("GET", "/detections", 200, 45.2)

# Get performance stats
stats = perf.get_stats("api_request")
print(f"P95 latency: {stats.p95_ms:.2f}ms")
```

### 3. Health Checks

```python
import asyncio
from monitoring import get_health_checker

async def check_system():
    checker = get_health_checker()
    health = await checker.run_all_checks()

    if health.status != HealthStatus.HEALTHY:
        # Send alert
        print(f"System unhealthy: {health.status}")

asyncio.run(check_system())
```

### 4. Identify Bottlenecks

```python
from monitoring import get_performance_monitor

perf = get_performance_monitor()

# Get bottlenecks
bottlenecks = perf.identify_bottlenecks()

for bottleneck in bottlenecks:
    print(f"{bottleneck.component}: {bottleneck.description}")
    print(f"Suggestions: {', '.join(bottleneck.suggestions)}")
```

## Configuration via Environment Variables

```bash
# Logging
export LOG_DIR=/var/log/ppe-detection
export LOG_LEVEL=INFO

# Metrics
export PROMETHEUS_PORT=9090

# Performance
export MAX_CPU_PERCENT=80
export MAX_MEMORY_PERCENT=85

# Alerts
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

## Grafana Dashboard Setup

1. Import dashboard:
   - Open Grafana: http://localhost:3000
   - Login: admin/admin
   - Go to Dashboards > Import
   - Upload `grafana_dashboard.json`

2. View metrics:
   - Navigate to the "PPE Detection System" dashboard
   - View real-time metrics, alerts, and system status

## Troubleshooting

### Logs not appearing

```python
# Make sure logging is initialized
from monitoring import setup_logging
setup_logging()
```

### Metrics not collected

```python
# Check if metrics collector is running
from monitoring import get_metrics_collector
collector = get_metrics_collector()
print(collector.export_metrics())
```

### Prometheus can't scrape metrics

```bash
# Make sure the metrics server is running
# Check if port 9090 is accessible
curl http://localhost:9090/metrics
```

### High memory usage

```python
# Cleanup old metrics
collector.cleanup_old_metrics(retention_days=7)
```

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Customize alert thresholds in `monitoring_config.py`
3. Set up Prometheus alert rules in `alerts.yml`
4. Configure Slack/email notifications
5. Integrate with your CI/CD pipeline

## Support

For issues or questions, please refer to:
- [README.md](README.md) - Full documentation
- [example_usage.py](example_usage.py) - Example code
- Grafana dashboard for visualization

## Quick Reference

| Component | File | Purpose |
|-----------|------|---------|
| Logging | logger.py | Structured logging with JSON format |
| Metrics | metrics.py | Prometheus-compatible metrics |
| Health | health_check.py | System health monitoring |
| Performance | performance_monitor.py | Performance tracking |
| Config | monitoring_config.py | Configuration management |
| Dashboard | grafana_dashboard.json | Grafana visualization |
| Example | example_usage.py | Usage examples |
