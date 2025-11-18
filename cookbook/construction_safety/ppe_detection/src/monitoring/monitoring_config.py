"""
Configuration for monitoring, logging, and metrics collection.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class LoggingConfig:
    """Configuration for logging system."""

    log_dir: Path = field(default_factory=lambda: Path("logs"))
    max_bytes: int = 100 * 1024 * 1024  # 100MB
    backup_count: int = 10
    log_format: str = "json"
    log_level: str = "INFO"

    # Separate log files
    app_log_file: str = "application.log"
    detection_log_file: str = "detection.log"
    camera_log_file: str = "camera.log"
    alert_log_file: str = "alert.log"

    # Async logging
    use_async_logging: bool = True
    queue_size: int = 10000


@dataclass
class MetricsConfig:
    """Configuration for metrics collection."""

    # Collection intervals (seconds)
    collection_interval: int = 10
    system_metrics_interval: int = 30

    # Prometheus
    prometheus_enabled: bool = True
    prometheus_port: int = 9090

    # Metric retention
    retention_days: int = 30

    # Custom metrics
    track_detections: bool = True
    track_violations: bool = True
    track_camera_uptime: bool = True
    track_api_performance: bool = True
    track_model_inference: bool = True
    track_system_resources: bool = True


@dataclass
class HealthCheckConfig:
    """Configuration for health checks."""

    # Health check intervals (seconds)
    check_interval: int = 60

    # Component timeouts (seconds)
    database_timeout: int = 5
    camera_timeout: int = 10
    model_timeout: int = 5

    # Disk space thresholds
    min_disk_space_gb: float = 10.0
    disk_warning_threshold_percent: float = 80.0

    # Service availability
    require_database: bool = True
    require_cameras: bool = True
    require_model: bool = True


@dataclass
class PerformanceConfig:
    """Configuration for performance monitoring."""

    # Performance tracking
    track_response_times: bool = True
    track_inference_times: bool = True
    track_throughput: bool = True

    # Alert thresholds
    max_response_time_ms: float = 1000.0
    max_inference_time_ms: float = 500.0
    min_fps: float = 10.0

    # Resource thresholds
    max_cpu_percent: float = 80.0
    max_memory_percent: float = 85.0
    max_gpu_memory_percent: float = 90.0

    # Performance degradation detection
    enable_degradation_detection: bool = True
    degradation_window_minutes: int = 15
    degradation_threshold_percent: float = 30.0


@dataclass
class AlertConfig:
    """Configuration for alerting."""

    # Alert thresholds
    violation_rate_threshold: float = 0.5  # 50% violation rate
    high_violation_count: int = 10  # violations per hour
    camera_offline_duration_minutes: int = 5

    # Alert channels
    enable_email_alerts: bool = False
    enable_slack_alerts: bool = False
    enable_webhook_alerts: bool = False

    # Email configuration
    email_recipients: List[str] = field(default_factory=list)
    email_smtp_server: str = ""
    email_smtp_port: int = 587

    # Slack configuration
    slack_webhook_url: str = ""

    # Webhook configuration
    webhook_url: str = ""


@dataclass
class ExportConfig:
    """Configuration for metrics export."""

    # Grafana
    grafana_enabled: bool = False
    grafana_url: str = ""
    grafana_api_key: str = ""

    # Prometheus
    prometheus_enabled: bool = True
    prometheus_pushgateway_url: str = ""

    # ELK Stack
    elasticsearch_enabled: bool = False
    elasticsearch_url: str = ""
    elasticsearch_index: str = "ppe-detection"

    # AWS CloudWatch
    cloudwatch_enabled: bool = False
    cloudwatch_region: str = "us-east-1"
    cloudwatch_namespace: str = "PPEDetection"

    # Export intervals
    export_interval_seconds: int = 60


@dataclass
class MonitoringConfig:
    """Main monitoring configuration."""

    logging: LoggingConfig = field(default_factory=LoggingConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    health_check: HealthCheckConfig = field(default_factory=HealthCheckConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    alerts: AlertConfig = field(default_factory=AlertConfig)
    export: ExportConfig = field(default_factory=ExportConfig)

    # Environment
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))

    @classmethod
    def from_env(cls) -> "MonitoringConfig":
        """Create configuration from environment variables."""
        config = cls()

        # Logging
        if log_dir := os.getenv("LOG_DIR"):
            config.logging.log_dir = Path(log_dir)
        if log_level := os.getenv("LOG_LEVEL"):
            config.logging.log_level = log_level

        # Metrics
        if prom_port := os.getenv("PROMETHEUS_PORT"):
            config.metrics.prometheus_port = int(prom_port)

        # Health checks
        if disk_min := os.getenv("MIN_DISK_SPACE_GB"):
            config.health_check.min_disk_space_gb = float(disk_min)

        # Performance
        if max_cpu := os.getenv("MAX_CPU_PERCENT"):
            config.performance.max_cpu_percent = float(max_cpu)
        if max_mem := os.getenv("MAX_MEMORY_PERCENT"):
            config.performance.max_memory_percent = float(max_mem)

        # Alerts
        if email_recipients := os.getenv("ALERT_EMAIL_RECIPIENTS"):
            config.alerts.email_recipients = email_recipients.split(",")
        if slack_webhook := os.getenv("SLACK_WEBHOOK_URL"):
            config.alerts.slack_webhook_url = slack_webhook
            config.alerts.enable_slack_alerts = True

        # Export
        if es_url := os.getenv("ELASTICSEARCH_URL"):
            config.export.elasticsearch_url = es_url
            config.export.elasticsearch_enabled = True
        if cw_region := os.getenv("CLOUDWATCH_REGION"):
            config.export.cloudwatch_region = cw_region
            config.export.cloudwatch_enabled = True

        return config

    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []

        # Check log directory is writable
        try:
            self.logging.log_dir.mkdir(parents=True, exist_ok=True)
            if not os.access(self.logging.log_dir, os.W_OK):
                errors.append(f"Log directory {self.logging.log_dir} is not writable")
        except Exception as e:
            errors.append(f"Cannot create log directory: {e}")

        # Validate metrics port
        if not 1024 <= self.metrics.prometheus_port <= 65535:
            errors.append(f"Invalid Prometheus port: {self.metrics.prometheus_port}")

        # Validate thresholds
        if self.performance.max_cpu_percent <= 0 or self.performance.max_cpu_percent > 100:
            errors.append(f"Invalid max_cpu_percent: {self.performance.max_cpu_percent}")
        if self.performance.max_memory_percent <= 0 or self.performance.max_memory_percent > 100:
            errors.append(f"Invalid max_memory_percent: {self.performance.max_memory_percent}")

        # Validate alert configuration
        if self.alerts.enable_email_alerts and not self.alerts.email_recipients:
            errors.append("Email alerts enabled but no recipients configured")
        if self.alerts.enable_slack_alerts and not self.alerts.slack_webhook_url:
            errors.append("Slack alerts enabled but no webhook URL configured")

        return errors


# Global configuration instance
_monitoring_config: MonitoringConfig | None = None


def get_monitoring_config() -> MonitoringConfig:
    """Get the global monitoring configuration instance."""
    global _monitoring_config
    if _monitoring_config is None:
        _monitoring_config = MonitoringConfig.from_env()

        # Validate configuration
        errors = _monitoring_config.validate()
        if errors:
            print("Warning: Monitoring configuration has errors:")
            for error in errors:
                print(f"  - {error}")

    return _monitoring_config


def set_monitoring_config(config: MonitoringConfig) -> None:
    """Set the global monitoring configuration instance."""
    global _monitoring_config
    _monitoring_config = config
