"""
Alert Manager - Central coordinator for PPE violation alerts.
Handles detection, de-duplication, throttling, and notification dispatch.
"""

import hashlib
import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from threading import Lock
import json

from .alert_config import AlertConfig, AlertPriority, NotificationChannel
from .alert_rules import AlertRules
from .alert_templates import AlertTemplates, TemplateType


@dataclass
class Alert:
    """Represents a single alert."""
    alert_id: str
    timestamp: datetime
    priority: AlertPriority
    zone: str
    camera_id: str
    missing_ppe: List[str]
    worker_id: Optional[str] = None
    image_url: Optional[str] = None
    violation_count: int = 1
    compliance_rate: Optional[float] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    escalation_level: int = 0
    matched_rules: List[str] = field(default_factory=list)
    sent_channels: Set[str] = field(default_factory=set)
    metadata: Dict = field(default_factory=dict)

    def get_fingerprint(self) -> str:
        """Generate fingerprint for de-duplication."""
        key = f"{self.zone}:{self.camera_id}:{','.join(sorted(self.missing_ppe))}"
        return hashlib.md5(key.encode()).hexdigest()

    def to_dict(self) -> Dict:
        """Convert alert to dictionary."""
        return {
            'alert_id': self.alert_id,
            'timestamp': self.timestamp.isoformat(),
            'priority': self.priority.value,
            'zone': self.zone,
            'camera_id': self.camera_id,
            'missing_ppe': self.missing_ppe,
            'worker_id': self.worker_id,
            'image_url': self.image_url,
            'violation_count': self.violation_count,
            'compliance_rate': self.compliance_rate,
            'acknowledged': self.acknowledged,
            'acknowledged_by': self.acknowledged_by,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'escalation_level': self.escalation_level,
            'matched_rules': self.matched_rules,
            'sent_channels': list(self.sent_channels),
            'metadata': self.metadata
        }


class AlertManager:
    """
    Manages PPE violation alerts including:
    - Violation pattern detection
    - Real-time notification dispatch
    - De-duplication
    - Throttling
    - Escalation
    """

    def __init__(self, config: AlertConfig, rules: Optional[AlertRules] = None):
        self.config = config
        self.rules = rules or AlertRules()
        self.logger = logging.getLogger(__name__)

        # Alert storage
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: deque = deque(maxlen=10000)
        self.acknowledged_alerts: Dict[str, Alert] = {}

        # De-duplication tracking
        self.recent_fingerprints: Dict[str, datetime] = {}
        self.fingerprint_lock = Lock()

        # Throttling tracking
        self.hourly_alert_count = 0
        self.daily_alert_count = 0
        self.last_hour_reset = datetime.now()
        self.last_day_reset = datetime.now()
        self.throttle_lock = Lock()

        # Zone-specific throttling
        self.zone_last_alert: Dict[str, datetime] = {}

        # Violation tracking for pattern detection
        self.zone_violations: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.worker_violations: Dict[str, deque] = defaultdict(lambda: deque(maxlen=50))

        # Escalation tracking
        self.pending_escalations: Dict[str, datetime] = {}

        # Notifiers (lazy loaded)
        self._notifiers = {}

    def _get_notifier(self, channel: NotificationChannel):
        """Lazy load notifiers as needed."""
        if channel not in self._notifiers:
            if channel == NotificationChannel.EMAIL:
                from .notifiers.email_notifier import EmailNotifier
                self._notifiers[channel] = EmailNotifier(self.config)
            elif channel == NotificationChannel.WEBHOOK:
                from .notifiers.webhook_notifier import WebhookNotifier
                self._notifiers[channel] = WebhookNotifier(self.config)
            elif channel == NotificationChannel.TELEGRAM:
                from .notifiers.telegram_notifier import TelegramNotifier
                self._notifiers[channel] = TelegramNotifier(self.config)
            elif channel == NotificationChannel.SMS:
                from .notifiers.sms_notifier import SMSNotifier
                self._notifiers[channel] = SMSNotifier(self.config)
            elif channel == NotificationChannel.WEBSOCKET:
                from .notifiers.websocket_notifier import WebSocketNotifier
                self._notifiers[channel] = WebSocketNotifier(self.config)

        return self._notifiers.get(channel)

    def process_violation(
        self,
        zone: str,
        camera_id: str,
        missing_ppe: List[str],
        worker_id: Optional[str] = None,
        image_url: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[Alert]:
        """
        Process a PPE violation and trigger alerts if needed.

        Args:
            zone: Zone where violation occurred
            camera_id: Camera that detected violation
            missing_ppe: List of missing PPE items
            worker_id: Worker identifier (optional)
            image_url: URL to violation image (optional)
            timestamp: Time of violation (defaults to now)
            metadata: Additional metadata (optional)

        Returns:
            Alert object if alert was sent, None if filtered/throttled
        """
        if timestamp is None:
            timestamp = datetime.now()

        if metadata is None:
            metadata = {}

        # Check de-duplication
        if self._is_duplicate(zone, camera_id, missing_ppe, timestamp):
            self.logger.debug(f"Duplicate violation filtered: {zone} - {missing_ppe}")
            return None

        # Check zone throttling
        if self._is_zone_throttled(zone, timestamp):
            self.logger.debug(f"Zone throttled: {zone}")
            return None

        # Check quiet hours
        if self._is_quiet_hours(timestamp):
            self.logger.info(f"Quiet hours - alert suppressed: {zone}")
            return None

        # Track violation
        self._track_violation(zone, worker_id, timestamp)

        # Calculate violation patterns
        violation_count = self._get_zone_violation_count(zone,
                                                         self.config.violation_time_window_minutes)
        compliance_rate = self._calculate_compliance_rate(zone)

        # Determine priority
        priority = self._determine_priority(zone, missing_ppe, violation_count, compliance_rate)

        # Find matching rules
        matching_rules = self.rules.find_matching_rules(
            zone=zone,
            missing_ppe=missing_ppe,
            violation_count=violation_count,
            compliance_rate=compliance_rate,
            timestamp=timestamp,
            worker_id=worker_id,
            time_window_minutes=self.config.violation_time_window_minutes
        )

        if not matching_rules:
            self.logger.debug(f"No matching rules for violation in {zone}")
            return None

        # Create alert
        alert = Alert(
            alert_id=self._generate_alert_id(timestamp),
            timestamp=timestamp,
            priority=priority,
            zone=zone,
            camera_id=camera_id,
            missing_ppe=missing_ppe,
            worker_id=worker_id,
            image_url=image_url,
            violation_count=violation_count,
            compliance_rate=compliance_rate,
            matched_rules=[rule.rule_id for rule in matching_rules],
            metadata=metadata
        )

        # Check throttling
        if not self._check_throttle():
            self.logger.warning("Alert throttled - limit reached")
            return None

        # Send notifications
        self._send_alert(alert, matching_rules)

        # Store alert
        self.active_alerts[alert.alert_id] = alert
        self.alert_history.append(alert)

        # Schedule escalation if needed
        if self.config.escalation.enabled:
            self._schedule_escalation(alert)

        return alert

    def _is_duplicate(
        self,
        zone: str,
        camera_id: str,
        missing_ppe: List[str],
        timestamp: datetime
    ) -> bool:
        """Check if violation is a duplicate within deduplication window."""
        fingerprint = hashlib.md5(
            f"{zone}:{camera_id}:{','.join(sorted(missing_ppe))}".encode()
        ).hexdigest()

        with self.fingerprint_lock:
            if fingerprint in self.recent_fingerprints:
                last_seen = self.recent_fingerprints[fingerprint]
                window = timedelta(minutes=self.config.throttle.deduplication_window_minutes)

                if timestamp - last_seen < window:
                    return True

            self.recent_fingerprints[fingerprint] = timestamp

            # Clean old fingerprints
            cutoff = timestamp - timedelta(minutes=self.config.throttle.deduplication_window_minutes * 2)
            self.recent_fingerprints = {
                fp: ts for fp, ts in self.recent_fingerprints.items()
                if ts > cutoff
            }

        return False

    def _is_zone_throttled(self, zone: str, timestamp: datetime) -> bool:
        """Check if zone is throttled."""
        if zone in self.zone_last_alert:
            last_alert = self.zone_last_alert[zone]
            throttle_window = timedelta(minutes=self.config.throttle.same_zone_throttle_minutes)

            if timestamp - last_alert < throttle_window:
                return True

        self.zone_last_alert[zone] = timestamp
        return False

    def _is_quiet_hours(self, timestamp: datetime) -> bool:
        """Check if current time is in quiet hours."""
        if not self.config.quiet_hours.enabled:
            return False

        is_quiet = self.config.is_quiet_hours()

        # Emergency override for critical alerts
        if is_quiet and self.config.quiet_hours.emergency_override:
            return False

        return is_quiet

    def _check_throttle(self) -> bool:
        """Check global alert throttling limits."""
        with self.throttle_lock:
            now = datetime.now()

            # Reset hourly counter
            if now - self.last_hour_reset > timedelta(hours=1):
                self.hourly_alert_count = 0
                self.last_hour_reset = now

            # Reset daily counter
            if now - self.last_day_reset > timedelta(days=1):
                self.daily_alert_count = 0
                self.last_day_reset = now

            # Check limits
            if self.hourly_alert_count >= self.config.throttle.max_alerts_per_hour:
                return False

            if self.daily_alert_count >= self.config.throttle.max_alerts_per_day:
                return False

            # Increment counters
            self.hourly_alert_count += 1
            self.daily_alert_count += 1

        return True

    def _track_violation(self, zone: str, worker_id: Optional[str], timestamp: datetime):
        """Track violation for pattern detection."""
        self.zone_violations[zone].append(timestamp)

        if worker_id:
            self.worker_violations[worker_id].append(timestamp)

    def _get_zone_violation_count(self, zone: str, time_window_minutes: int) -> int:
        """Get violation count for zone within time window."""
        if zone not in self.zone_violations:
            return 0

        cutoff = datetime.now() - timedelta(minutes=time_window_minutes)
        return sum(1 for ts in self.zone_violations[zone] if ts > cutoff)

    def _calculate_compliance_rate(self, zone: str) -> Optional[float]:
        """Calculate compliance rate for zone."""
        # This would integrate with detection system
        # For now, return None
        return None

    def _determine_priority(
        self,
        zone: str,
        missing_ppe: List[str],
        violation_count: int,
        compliance_rate: Optional[float]
    ) -> AlertPriority:
        """Determine alert priority based on context."""

        # Critical if in critical zone
        if zone in self.config.critical_zones:
            return AlertPriority.CRITICAL

        # Critical if helmet missing
        if "helmet" in missing_ppe:
            return AlertPriority.CRITICAL

        # Critical if harness missing in elevated work area
        if "harness" in missing_ppe and "Yüksekte" in zone:
            return AlertPriority.CRITICAL

        # Critical if compliance rate very low
        if compliance_rate is not None and compliance_rate < 0.60:
            return AlertPriority.CRITICAL

        # Warning if multiple violations
        if violation_count >= 3:
            return AlertPriority.WARNING

        # Warning if multiple PPE missing
        if len(missing_ppe) >= 2:
            return AlertPriority.WARNING

        return AlertPriority.INFO

    def _generate_alert_id(self, timestamp: datetime) -> str:
        """Generate unique alert ID."""
        return f"VIO-{timestamp.strftime('%Y%m%d%H%M%S%f')}"

    def _send_alert(self, alert: Alert, matching_rules: List):
        """Send alert through configured channels."""

        # Determine recipients based on priority and rules
        recipients = self.config.get_recipients_for_priority(alert.priority)

        # Determine template type (default to manager)
        template_type = TemplateType.MANAGER

        # Send through each enabled channel
        for channel in self.config.enabled_channels:
            try:
                notifier = self._get_notifier(channel)
                if notifier:
                    success = notifier.send(
                        alert=alert,
                        recipients=recipients,
                        template_type=template_type
                    )

                    if success:
                        alert.sent_channels.add(channel.value)
                        self.logger.info(f"Alert {alert.alert_id} sent via {channel.value}")
                    else:
                        self.logger.error(f"Failed to send alert via {channel.value}")

            except Exception as e:
                self.logger.error(f"Error sending alert via {channel.value}: {e}")

        # Update rule triggers
        for rule in matching_rules:
            self.rules.update_rule_trigger(rule.rule_id)

    def _schedule_escalation(self, alert: Alert):
        """Schedule escalation if alert not acknowledged."""
        escalation_time = alert.timestamp + timedelta(
            minutes=self.config.escalation.escalation_delay_minutes
        )
        self.pending_escalations[alert.alert_id] = escalation_time

    def check_escalations(self):
        """Check and process pending escalations."""
        now = datetime.now()
        escalated = []

        for alert_id, escalation_time in list(self.pending_escalations.items()):
            if alert_id not in self.active_alerts:
                del self.pending_escalations[alert_id]
                continue

            alert = self.active_alerts[alert_id]

            # Skip if acknowledged
            if alert.acknowledged:
                del self.pending_escalations[alert_id]
                continue

            # Escalate if time reached
            if now >= escalation_time:
                self._escalate_alert(alert)
                escalated.append(alert_id)
                del self.pending_escalations[alert_id]

        return escalated

    def _escalate_alert(self, alert: Alert):
        """Escalate alert to next level."""
        alert.escalation_level += 1

        if alert.escalation_level > self.config.escalation.max_escalation_level:
            self.logger.warning(f"Alert {alert.alert_id} reached max escalation level")
            return

        # Get escalation group
        groups = self.config.escalation.escalation_groups
        if alert.escalation_level <= len(groups):
            group_name = groups[alert.escalation_level - 1]

            # Send escalation notification
            self.logger.warning(f"Escalating alert {alert.alert_id} to level {alert.escalation_level}")

            # Schedule next escalation
            self._schedule_escalation(alert)

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.acknowledged = True
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.now()

            # Move to acknowledged alerts
            self.acknowledged_alerts[alert_id] = alert
            del self.active_alerts[alert_id]

            # Remove from pending escalations
            if alert_id in self.pending_escalations:
                del self.pending_escalations[alert_id]

            self.logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
            return True

        return False

    def get_active_alerts(self, zone: Optional[str] = None) -> List[Alert]:
        """Get all active (unacknowledged) alerts."""
        alerts = list(self.active_alerts.values())

        if zone:
            alerts = [a for a in alerts if a.zone == zone]

        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)

    def get_alert_statistics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict:
        """Get alert statistics for reporting."""
        if start_time is None:
            start_time = datetime.now() - timedelta(days=1)

        if end_time is None:
            end_time = datetime.now()

        # Filter alerts in time range
        alerts = [
            alert for alert in self.alert_history
            if start_time <= alert.timestamp <= end_time
        ]

        # Calculate statistics
        total_alerts = len(alerts)
        alerts_by_priority = defaultdict(int)
        alerts_by_zone = defaultdict(int)
        ppe_violations = defaultdict(int)

        for alert in alerts:
            alerts_by_priority[alert.priority.value] += 1
            alerts_by_zone[alert.zone] += 1

            for ppe in alert.missing_ppe:
                ppe_violations[ppe] += 1

        return {
            'total_alerts': total_alerts,
            'period': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            },
            'by_priority': dict(alerts_by_priority),
            'by_zone': dict(alerts_by_zone),
            'ppe_violations': dict(ppe_violations),
            'active_alerts': len(self.active_alerts),
            'acknowledged_alerts': len(self.acknowledged_alerts)
        }

    def generate_summary_report(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> str:
        """Generate summary report."""
        stats = self.get_alert_statistics(start_time, end_time)

        # Prepare data for template
        top_violations = [
            {'ppe': ppe, 'count': count}
            for ppe, count in sorted(
                stats['ppe_violations'].items(),
                key=lambda x: x[1],
                reverse=True
            )
        ]

        top_zones = [
            {'name': zone, 'count': count}
            for zone, count in sorted(
                stats['by_zone'].items(),
                key=lambda x: x[1],
                reverse=True
            )
        ]

        # Calculate compliance rate (placeholder)
        compliance_rate = 0.85  # This would come from detection system

        # Determine trend
        trend = "Sabit"  # This would be calculated from historical data

        return AlertTemplates.format_summary_report(
            period="Günlük" if (end_time - start_time).days <= 1 else "Haftalık",
            total_violations=stats['total_alerts'],
            compliance_rate=compliance_rate,
            top_violations=top_violations,
            top_zones=top_zones,
            trend=trend,
            start_date=start_time,
            end_date=end_time
        )
