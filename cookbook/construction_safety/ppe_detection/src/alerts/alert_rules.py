"""
Alert rule engine for configurable alert conditions.
Defines when and how alerts should be triggered.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from enum import Enum
import re


class RuleCondition(Enum):
    """Types of rule conditions."""
    VIOLATION_COUNT = "violation_count"
    COMPLIANCE_RATE = "compliance_rate"
    CRITICAL_ZONE = "critical_zone"
    TIME_BASED = "time_based"
    PATTERN_BASED = "pattern_based"
    CUSTOM = "custom"


class RuleAction(Enum):
    """Actions to take when rule is triggered."""
    SEND_ALERT = "send_alert"
    ESCALATE = "escalate"
    LOG_ONLY = "log_only"
    STOP_WORK = "stop_work"
    SEND_SUMMARY = "send_summary"


@dataclass
class AlertRule:
    """Defines a configurable alert rule."""
    rule_id: str
    name: str
    description: str
    condition_type: RuleCondition
    action: RuleAction
    priority: str  # "critical", "warning", "info"
    enabled: bool = True

    # Condition parameters
    threshold_value: Optional[float] = None
    time_window_minutes: Optional[int] = None
    zones: Optional[List[str]] = None
    ppe_types: Optional[List[str]] = None

    # Action parameters
    recipient_groups: List[str] = field(default_factory=list)
    notification_channels: List[str] = field(default_factory=list)

    # Custom condition function
    custom_condition: Optional[Callable] = None

    # Schedule
    active_days: List[int] = field(default_factory=lambda: list(range(7)))  # 0=Monday
    active_hours: Optional[tuple] = None  # (start_hour, end_hour)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0

    def is_active(self, timestamp: datetime) -> bool:
        """Check if rule is active at given time."""
        if not self.enabled:
            return False

        # Check day of week
        if timestamp.weekday() not in self.active_days:
            return False

        # Check hours
        if self.active_hours:
            hour = timestamp.hour
            start, end = self.active_hours
            if start < end:
                if not (start <= hour < end):
                    return False
            else:  # Crosses midnight
                if not (hour >= start or hour < end):
                    return False

        return True

    def matches_zone(self, zone: str) -> bool:
        """Check if rule applies to given zone."""
        if not self.zones:
            return True  # Applies to all zones
        return zone in self.zones

    def matches_ppe_type(self, ppe_types: List[str]) -> bool:
        """Check if rule applies to given PPE types."""
        if not self.ppe_types:
            return True  # Applies to all PPE types
        return any(ppe in self.ppe_types for ppe in ppe_types)


class AlertRules:
    """Rule engine for managing and evaluating alert rules."""

    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self._load_default_rules()

    def _load_default_rules(self):
        """Load default alert rules for Turkish construction sites."""

        # Rule 1: Multiple violations in same zone
        self.add_rule(AlertRule(
            rule_id="RULE_001",
            name="Aynı Bölgede Çoklu İhlal",
            description="Aynı bölgede 10 dakika içinde 3'ten fazla ihlal",
            condition_type=RuleCondition.VIOLATION_COUNT,
            action=RuleAction.SEND_ALERT,
            priority="warning",
            threshold_value=3,
            time_window_minutes=10,
            recipient_groups=["safety_officer", "zone_supervisors"],
            notification_channels=["email", "telegram"]
        ))

        # Rule 2: Low compliance rate
        self.add_rule(AlertRule(
            rule_id="RULE_002",
            name="Düşük Uyum Oranı",
            description="Bölge uyum oranı %80'in altına düştü",
            condition_type=RuleCondition.COMPLIANCE_RATE,
            action=RuleAction.SEND_ALERT,
            priority="critical",
            threshold_value=0.80,
            time_window_minutes=60,
            recipient_groups=["safety_officer", "site_manager"],
            notification_channels=["email", "sms", "telegram"]
        ))

        # Rule 3: Critical zone violation
        self.add_rule(AlertRule(
            rule_id="RULE_003",
            name="Kritik Bölge İhlali",
            description="Yüksek riskli bölgelerde herhangi bir KKD ihlali",
            condition_type=RuleCondition.CRITICAL_ZONE,
            action=RuleAction.SEND_ALERT,
            priority="critical",
            zones=[
                "Yüksekte Çalışma Alanı",
                "Elektrik Panosu",
                "Vinç Bölgesi",
                "Kazı Alanı"
            ],
            recipient_groups=["safety_officer", "site_manager", "emergency"],
            notification_channels=["email", "sms", "telegram", "webhook"]
        ))

        # Rule 4: Helmet violation (most critical PPE)
        self.add_rule(AlertRule(
            rule_id="RULE_004",
            name="Baret İhlali",
            description="Baret kullanımı ihlali tespit edildi",
            condition_type=RuleCondition.PATTERN_BASED,
            action=RuleAction.SEND_ALERT,
            priority="warning",
            ppe_types=["helmet"],
            recipient_groups=["zone_supervisors"],
            notification_channels=["telegram", "websocket"]
        ))

        # Rule 5: Daily summary report
        self.add_rule(AlertRule(
            rule_id="RULE_005",
            name="Günlük Özet Rapor",
            description="Her gün saat 18:00'de özet rapor gönder",
            condition_type=RuleCondition.TIME_BASED,
            action=RuleAction.SEND_SUMMARY,
            priority="info",
            active_hours=(18, 19),  # Between 18:00-19:00
            recipient_groups=["safety_officer", "site_manager"],
            notification_channels=["email"]
        ))

        # Rule 6: Night shift critical violations
        self.add_rule(AlertRule(
            rule_id="RULE_006",
            name="Gece Vardiyası Kritik İhlal",
            description="Gece vardiyasında kritik ihlaller için özel bildirim",
            condition_type=RuleCondition.TIME_BASED,
            action=RuleAction.SEND_ALERT,
            priority="critical",
            active_hours=(20, 6),  # 20:00 - 06:00
            recipient_groups=["night_shift_supervisor", "emergency"],
            notification_channels=["sms", "telegram"]
        ))

        # Rule 7: Repeated violations by same worker
        self.add_rule(AlertRule(
            rule_id="RULE_007",
            name="Tekrarlayan Bireysel İhlal",
            description="Aynı çalışan 1 saat içinde 3 kez ihlal yaptı",
            condition_type=RuleCondition.PATTERN_BASED,
            action=RuleAction.ESCALATE,
            priority="warning",
            threshold_value=3,
            time_window_minutes=60,
            recipient_groups=["safety_officer", "hr_department"],
            notification_channels=["email"]
        ))

        # Rule 8: Weekend safety check
        self.add_rule(AlertRule(
            rule_id="RULE_008",
            name="Hafta Sonu Güvenlik Kontrolü",
            description="Hafta sonları herhangi bir ihlal olursa bildir",
            condition_type=RuleCondition.TIME_BASED,
            action=RuleAction.SEND_ALERT,
            priority="warning",
            active_days=[5, 6],  # Saturday, Sunday
            recipient_groups=["weekend_supervisor"],
            notification_channels=["sms", "telegram"]
        ))

        # Rule 9: High risk PPE combination missing
        self.add_rule(AlertRule(
            rule_id="RULE_009",
            name="Yüksek Risk KKD Kombinasyonu",
            description="Baret ve emniyet kemeri birlikte eksik (yüksekte çalışma)",
            condition_type=RuleCondition.PATTERN_BASED,
            action=RuleAction.SEND_ALERT,
            priority="critical",
            ppe_types=["helmet", "harness"],
            zones=["Yüksekte Çalışma Alanı"],
            recipient_groups=["safety_officer", "site_manager", "emergency"],
            notification_channels=["sms", "telegram", "webhook"]
        ))

        # Rule 10: Weekly compliance report
        self.add_rule(AlertRule(
            rule_id="RULE_010",
            name="Haftalık Uyum Raporu",
            description="Her Cuma saat 17:00'de haftalık rapor",
            condition_type=RuleCondition.TIME_BASED,
            action=RuleAction.SEND_SUMMARY,
            priority="info",
            active_days=[4],  # Friday
            active_hours=(17, 18),
            recipient_groups=["site_manager", "safety_officer", "management"],
            notification_channels=["email"]
        ))

    def add_rule(self, rule: AlertRule):
        """Add a new rule to the engine."""
        self.rules[rule.rule_id] = rule

    def remove_rule(self, rule_id: str):
        """Remove a rule from the engine."""
        if rule_id in self.rules:
            del self.rules[rule_id]

    def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        """Get a specific rule."""
        return self.rules.get(rule_id)

    def get_active_rules(self, timestamp: Optional[datetime] = None) -> List[AlertRule]:
        """Get all currently active rules."""
        if timestamp is None:
            timestamp = datetime.now()

        return [
            rule for rule in self.rules.values()
            if rule.is_active(timestamp)
        ]

    def evaluate_violation_count_rule(
        self,
        rule: AlertRule,
        zone: str,
        violation_count: int,
        time_window_minutes: int
    ) -> bool:
        """Evaluate violation count rule."""
        if rule.condition_type != RuleCondition.VIOLATION_COUNT:
            return False

        if not rule.matches_zone(zone):
            return False

        if rule.threshold_value and violation_count >= rule.threshold_value:
            if not rule.time_window_minutes or time_window_minutes <= rule.time_window_minutes:
                return True

        return False

    def evaluate_compliance_rate_rule(
        self,
        rule: AlertRule,
        zone: str,
        compliance_rate: float
    ) -> bool:
        """Evaluate compliance rate rule."""
        if rule.condition_type != RuleCondition.COMPLIANCE_RATE:
            return False

        if not rule.matches_zone(zone):
            return False

        if rule.threshold_value and compliance_rate < rule.threshold_value:
            return True

        return False

    def evaluate_critical_zone_rule(
        self,
        rule: AlertRule,
        zone: str,
        missing_ppe: List[str]
    ) -> bool:
        """Evaluate critical zone rule."""
        if rule.condition_type != RuleCondition.CRITICAL_ZONE:
            return False

        if not rule.matches_zone(zone):
            return False

        if not rule.matches_ppe_type(missing_ppe):
            return False

        return True

    def evaluate_pattern_rule(
        self,
        rule: AlertRule,
        zone: str,
        missing_ppe: List[str],
        **kwargs
    ) -> bool:
        """Evaluate pattern-based rule."""
        if rule.condition_type != RuleCondition.PATTERN_BASED:
            return False

        if not rule.matches_zone(zone):
            return False

        if not rule.matches_ppe_type(missing_ppe):
            return False

        # Check for specific patterns
        if rule.ppe_types:
            # All specified PPE types must be missing
            if set(rule.ppe_types).issubset(set(missing_ppe)):
                return True

        return True

    def evaluate_time_based_rule(
        self,
        rule: AlertRule,
        timestamp: datetime
    ) -> bool:
        """Evaluate time-based rule (for scheduled reports)."""
        if rule.condition_type != RuleCondition.TIME_BASED:
            return False

        return rule.is_active(timestamp)

    def evaluate_custom_rule(
        self,
        rule: AlertRule,
        **kwargs
    ) -> bool:
        """Evaluate custom rule with user-defined function."""
        if rule.condition_type != RuleCondition.CUSTOM:
            return False

        if rule.custom_condition is None:
            return False

        try:
            return rule.custom_condition(**kwargs)
        except Exception:
            return False

    def find_matching_rules(
        self,
        zone: str,
        missing_ppe: List[str],
        violation_count: int = 1,
        compliance_rate: Optional[float] = None,
        timestamp: Optional[datetime] = None,
        **kwargs
    ) -> List[AlertRule]:
        """Find all rules that match the given conditions."""
        if timestamp is None:
            timestamp = datetime.now()

        matching_rules = []
        active_rules = self.get_active_rules(timestamp)

        for rule in active_rules:
            matched = False

            if rule.condition_type == RuleCondition.VIOLATION_COUNT:
                if self.evaluate_violation_count_rule(
                    rule, zone, violation_count,
                    kwargs.get('time_window_minutes', 0)
                ):
                    matched = True

            elif rule.condition_type == RuleCondition.COMPLIANCE_RATE:
                if compliance_rate is not None:
                    if self.evaluate_compliance_rate_rule(rule, zone, compliance_rate):
                        matched = True

            elif rule.condition_type == RuleCondition.CRITICAL_ZONE:
                if self.evaluate_critical_zone_rule(rule, zone, missing_ppe):
                    matched = True

            elif rule.condition_type == RuleCondition.PATTERN_BASED:
                if self.evaluate_pattern_rule(rule, zone, missing_ppe, **kwargs):
                    matched = True

            elif rule.condition_type == RuleCondition.TIME_BASED:
                if self.evaluate_time_based_rule(rule, timestamp):
                    matched = True

            elif rule.condition_type == RuleCondition.CUSTOM:
                if self.evaluate_custom_rule(rule, zone=zone, missing_ppe=missing_ppe, **kwargs):
                    matched = True

            if matched:
                matching_rules.append(rule)

        return matching_rules

    def update_rule_trigger(self, rule_id: str):
        """Update rule trigger timestamp and count."""
        if rule_id in self.rules:
            rule = self.rules[rule_id]
            rule.last_triggered = datetime.now()
            rule.trigger_count += 1

    def get_rules_by_priority(self, priority: str) -> List[AlertRule]:
        """Get all rules of given priority."""
        return [rule for rule in self.rules.values() if rule.priority == priority]

    def get_rules_by_zone(self, zone: str) -> List[AlertRule]:
        """Get all rules applicable to given zone."""
        return [rule for rule in self.rules.values() if rule.matches_zone(zone)]

    def export_rules(self) -> Dict[str, Dict]:
        """Export rules configuration."""
        return {
            rule_id: {
                'name': rule.name,
                'description': rule.description,
                'condition_type': rule.condition_type.value,
                'action': rule.action.value,
                'priority': rule.priority,
                'enabled': rule.enabled,
                'threshold_value': rule.threshold_value,
                'time_window_minutes': rule.time_window_minutes,
                'zones': rule.zones,
                'ppe_types': rule.ppe_types,
                'recipient_groups': rule.recipient_groups,
                'notification_channels': rule.notification_channels,
                'trigger_count': rule.trigger_count,
                'last_triggered': rule.last_triggered.isoformat() if rule.last_triggered else None
            }
            for rule_id, rule in self.rules.items()
        }


# Example custom rule functions

def custom_contractor_rule(zone: str, worker_id: Optional[str], **kwargs) -> bool:
    """Example: Alert if contractor (ID starts with 'C') violates in critical zone."""
    critical_zones = ["Yüksekte Çalışma Alanı", "Elektrik Panosu"]
    if worker_id and worker_id.startswith('C') and zone in critical_zones:
        return True
    return False


def custom_temperature_rule(zone: str, temperature: Optional[float], **kwargs) -> bool:
    """Example: Special alerts during extreme temperatures."""
    if temperature is not None:
        if temperature > 35 or temperature < 0:  # Extreme temperatures
            return True
    return False


def custom_visitor_rule(worker_id: Optional[str], missing_ppe: List[str], **kwargs) -> bool:
    """Example: Stricter rules for visitors."""
    if worker_id and worker_id.startswith('V'):  # Visitor
        # Visitors must have ALL PPE
        if missing_ppe:
            return True
    return False
