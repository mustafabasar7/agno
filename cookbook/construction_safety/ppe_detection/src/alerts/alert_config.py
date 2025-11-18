"""
Alert configuration for PPE detection system.
Defines notification channels, thresholds, recipients, and schedules.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from datetime import time
from enum import Enum


class AlertPriority(Enum):
    """Alert priority levels."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class NotificationChannel(Enum):
    """Available notification channels."""
    EMAIL = "email"
    WEBHOOK = "webhook"
    TELEGRAM = "telegram"
    SMS = "sms"
    WEBSOCKET = "websocket"


@dataclass
class RecipientGroup:
    """Recipient group configuration."""
    name: str
    email_addresses: List[str] = field(default_factory=list)
    telegram_chat_ids: List[str] = field(default_factory=list)
    phone_numbers: List[str] = field(default_factory=list)
    webhook_urls: List[str] = field(default_factory=list)
    priority_threshold: AlertPriority = AlertPriority.WARNING


@dataclass
class QuietHours:
    """Quiet hours configuration."""
    enabled: bool = True
    start_time: time = time(22, 0)  # 22:00
    end_time: time = time(7, 0)     # 07:00
    emergency_override: bool = True  # Send critical alerts even during quiet hours


@dataclass
class ThrottleConfig:
    """Alert throttling configuration."""
    max_alerts_per_hour: int = 20
    max_alerts_per_day: int = 100
    deduplication_window_minutes: int = 15
    same_zone_throttle_minutes: int = 5


@dataclass
class EscalationConfig:
    """Alert escalation configuration."""
    enabled: bool = True
    escalation_delay_minutes: int = 30
    max_escalation_level: int = 3
    escalation_groups: List[str] = field(default_factory=list)


@dataclass
class AlertConfig:
    """Main alert configuration."""

    # Notification channels
    enabled_channels: Set[NotificationChannel] = field(default_factory=lambda: {
        NotificationChannel.EMAIL,
        NotificationChannel.WEBHOOK,
        NotificationChannel.WEBSOCKET
    })

    # Recipient groups
    recipient_groups: Dict[str, RecipientGroup] = field(default_factory=dict)

    # Email configuration
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    email_from: str = "ppe-detection@example.com"

    # Telegram configuration
    telegram_bot_token: str = ""
    telegram_default_chat_id: str = ""

    # SMS configuration (Twilio)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""

    # Webhook configuration
    webhook_timeout_seconds: int = 10
    webhook_retry_attempts: int = 3

    # WebSocket configuration
    websocket_url: str = "ws://localhost:8080/alerts"

    # Alert thresholds
    violation_count_threshold: int = 3
    violation_time_window_minutes: int = 10
    compliance_rate_threshold: float = 0.80  # 80%

    # Critical zones (higher priority alerts)
    critical_zones: Set[str] = field(default_factory=lambda: {
        "Yüksekte Çalışma Alanı",
        "Elektrik Panosu",
        "Vinç Bölgesi",
        "Kazı Alanı"
    })

    # Throttling and quiet hours
    throttle: ThrottleConfig = field(default_factory=ThrottleConfig)
    quiet_hours: QuietHours = field(default_factory=QuietHours)

    # Escalation
    escalation: EscalationConfig = field(default_factory=EscalationConfig)

    # Alert history
    alert_retention_days: int = 90

    # Acknowledgment
    require_acknowledgment: bool = True
    auto_acknowledge_after_hours: int = 24

    def get_recipients_for_priority(self, priority: AlertPriority) -> List[RecipientGroup]:
        """Get recipient groups that should receive alerts of given priority."""
        recipients = []
        for group in self.recipient_groups.values():
            if self._should_notify_group(group, priority):
                recipients.append(group)
        return recipients

    def _should_notify_group(self, group: RecipientGroup, priority: AlertPriority) -> bool:
        """Check if group should be notified for given priority."""
        priority_order = {
            AlertPriority.INFO: 0,
            AlertPriority.WARNING: 1,
            AlertPriority.CRITICAL: 2
        }
        return priority_order[priority] >= priority_order[group.priority_threshold]

    def is_quiet_hours(self) -> bool:
        """Check if current time is within quiet hours."""
        if not self.quiet_hours.enabled:
            return False

        from datetime import datetime
        now = datetime.now().time()
        start = self.quiet_hours.start_time
        end = self.quiet_hours.end_time

        if start < end:
            return start <= now <= end
        else:  # Crosses midnight
            return now >= start or now <= end


# Example configurations for Turkish construction sites

def get_example_config_small_site() -> AlertConfig:
    """Configuration for small construction site (50-100 workers)."""
    config = AlertConfig()

    # Recipients
    config.recipient_groups = {
        "site_manager": RecipientGroup(
            name="Şantiye Müdürü",
            email_addresses=["santiye.muduru@insaat.com"],
            telegram_chat_ids=["123456789"],
            phone_numbers=["+905551234567"],
            priority_threshold=AlertPriority.WARNING
        ),
        "safety_officer": RecipientGroup(
            name="İSG Uzmanı",
            email_addresses=["isg@insaat.com"],
            telegram_chat_ids=["987654321"],
            phone_numbers=["+905559876543"],
            priority_threshold=AlertPriority.INFO
        ),
        "emergency": RecipientGroup(
            name="Acil Durum Ekibi",
            email_addresses=["acil@insaat.com"],
            phone_numbers=["+905551111111"],
            priority_threshold=AlertPriority.CRITICAL
        )
    }

    # Escalation groups
    config.escalation.escalation_groups = ["safety_officer", "site_manager", "emergency"]

    return config


def get_example_config_large_site() -> AlertConfig:
    """Configuration for large construction site (500+ workers)."""
    config = AlertConfig()

    # Recipients
    config.recipient_groups = {
        "zone_supervisors": RecipientGroup(
            name="Bölge Şefleri",
            email_addresses=[
                "bolge1@insaat.com",
                "bolge2@insaat.com",
                "bolge3@insaat.com"
            ],
            telegram_chat_ids=["111111111", "222222222", "333333333"],
            priority_threshold=AlertPriority.INFO
        ),
        "safety_team": RecipientGroup(
            name="İSG Ekibi",
            email_addresses=["isg-ekip@insaat.com"],
            telegram_chat_ids=["444444444"],
            phone_numbers=["+905552222222"],
            priority_threshold=AlertPriority.WARNING
        ),
        "site_management": RecipientGroup(
            name="Üst Yönetim",
            email_addresses=[
                "genel.mudur@insaat.com",
                "santiye.muduru@insaat.com"
            ],
            phone_numbers=["+905553333333", "+905554444444"],
            priority_threshold=AlertPriority.CRITICAL
        ),
        "emergency_response": RecipientGroup(
            name="112 Acil Müdahale",
            phone_numbers=["+905555555555"],
            priority_threshold=AlertPriority.CRITICAL
        )
    }

    # Higher thresholds for large sites
    config.violation_count_threshold = 5
    config.throttle.max_alerts_per_hour = 50
    config.throttle.max_alerts_per_day = 500

    # Stricter escalation
    config.escalation.escalation_delay_minutes = 15
    config.escalation.escalation_groups = [
        "zone_supervisors",
        "safety_team",
        "site_management",
        "emergency_response"
    ]

    return config


def get_example_config_critical_infrastructure() -> AlertConfig:
    """Configuration for critical infrastructure projects (power plants, refineries)."""
    config = AlertConfig()

    # Recipients
    config.recipient_groups = {
        "safety_control_room": RecipientGroup(
            name="Güvenlik Kontrol Merkezi",
            email_addresses=["kontrol@santiye.com"],
            telegram_chat_ids=["555555555"],
            webhook_urls=["https://control-center.com/webhooks/ppe"],
            priority_threshold=AlertPriority.INFO
        ),
        "hse_manager": RecipientGroup(
            name="HSE Müdürü",
            email_addresses=["hse.mudur@santiye.com"],
            telegram_chat_ids=["666666666"],
            phone_numbers=["+905556666666"],
            priority_threshold=AlertPriority.WARNING
        ),
        "project_management": RecipientGroup(
            name="Proje Yönetimi",
            email_addresses=["proje@santiye.com"],
            phone_numbers=["+905557777777"],
            priority_threshold=AlertPriority.CRITICAL
        ),
        "client_representative": RecipientGroup(
            name="İşveren Temsilcisi",
            email_addresses=["isveren@client.com"],
            priority_threshold=AlertPriority.CRITICAL
        )
    }

    # Very strict thresholds
    config.violation_count_threshold = 2
    config.compliance_rate_threshold = 0.95  # 95%

    # More critical zones
    config.critical_zones = {
        "Reaktör Bölgesi",
        "Yüksek Gerilim Alanı",
        "Patlayıcı Madde Deposu",
        "Radyasyon Kontrollü Alan",
        "Yüksekte Çalışma (>10m)",
        "Kapalı Alan",
        "Kimyasal Depolama"
    }

    # Minimal throttling for critical sites
    config.throttle.max_alerts_per_hour = 100
    config.throttle.deduplication_window_minutes = 5

    # No quiet hours for critical infrastructure
    config.quiet_hours.enabled = False

    # Faster escalation
    config.escalation.escalation_delay_minutes = 10
    config.escalation.escalation_groups = [
        "safety_control_room",
        "hse_manager",
        "project_management",
        "client_representative"
    ]

    return config


# Default configuration
DEFAULT_CONFIG = get_example_config_small_site()
