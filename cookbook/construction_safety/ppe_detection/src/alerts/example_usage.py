"""
Example usage of the Alert and Notification System.
Demonstrates different scenarios for Turkish construction sites.
"""

import logging
from datetime import datetime, timedelta
import time

from alert_config import (
    AlertConfig, RecipientGroup, AlertPriority,
    get_example_config_small_site,
    get_example_config_large_site,
    get_example_config_critical_infrastructure
)
from alert_manager import AlertManager
from alert_rules import AlertRules, AlertRule, RuleCondition, RuleAction


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_basic_usage():
    """Basic usage example for small construction site."""
    logger.info("=== Example 1: Basic Usage ===")

    # Load configuration
    config = get_example_config_small_site()
    rules = AlertRules()
    alert_manager = AlertManager(config, rules)

    # Process a simple violation
    alert = alert_manager.process_violation(
        zone="İnşaat Alanı",
        camera_id="CAM_001",
        missing_ppe=["helmet"],
        worker_id="W12345",
        timestamp=datetime.now()
    )

    if alert:
        logger.info(f"Alert created: {alert.alert_id}")
        logger.info(f"Priority: {alert.priority.value}")
        logger.info(f"Sent via: {alert.sent_channels}")
    else:
        logger.info("Alert was filtered or throttled")


def example_critical_zone_violation():
    """Example of critical zone violation with escalation."""
    logger.info("\n=== Example 2: Critical Zone Violation ===")

    config = get_example_config_small_site()
    rules = AlertRules()
    alert_manager = AlertManager(config, rules)

    # Critical zone violation - missing helmet and harness
    alert = alert_manager.process_violation(
        zone="Yüksekte Çalışma Alanı",
        camera_id="CAM_005",
        missing_ppe=["helmet", "harness"],
        worker_id="W67890",
        image_url="http://example.com/violations/critical_001.jpg",
        timestamp=datetime.now()
    )

    if alert:
        logger.info(f"CRITICAL ALERT: {alert.alert_id}")
        logger.info(f"Zone: {alert.zone}")
        logger.info(f"Missing PPE: {alert.missing_ppe}")
        logger.info(f"Escalation scheduled: {alert.alert_id in alert_manager.pending_escalations}")


def example_multiple_violations_pattern():
    """Example of detecting multiple violations in same zone."""
    logger.info("\n=== Example 3: Multiple Violations Pattern ===")

    config = get_example_config_small_site()
    rules = AlertRules()
    alert_manager = AlertManager(config, rules)

    zone = "Kazı Alanı"

    # Simulate 5 violations in same zone over 8 minutes
    for i in range(5):
        alert = alert_manager.process_violation(
            zone=zone,
            camera_id="CAM_003",
            missing_ppe=["vest"],
            worker_id=f"W{1000 + i}",
            timestamp=datetime.now() + timedelta(minutes=i*2)
        )

        if alert:
            logger.info(f"Violation {i+1}: Alert {alert.alert_id}")
            logger.info(f"  Violation count in zone: {alert.violation_count}")
        else:
            logger.info(f"Violation {i+1}: Filtered (de-duplication)")

        # Simulate time passing
        time.sleep(0.1)


def example_compliance_monitoring():
    """Example of monitoring compliance rates."""
    logger.info("\n=== Example 4: Compliance Rate Monitoring ===")

    config = get_example_config_large_site()
    rules = AlertRules()
    alert_manager = AlertManager(config, rules)

    # Simulate low compliance scenario
    zones = ["Beton Dökme Alanı", "Demir Bağlama", "İskele Montaj"]

    for zone in zones:
        # Simulate multiple violations (low compliance)
        for i in range(4):
            alert_manager.process_violation(
                zone=zone,
                camera_id=f"CAM_{zone[:3]}",
                missing_ppe=["helmet"],
                worker_id=f"W{2000 + i}",
                timestamp=datetime.now()
            )

    # Check statistics
    stats = alert_manager.get_alert_statistics()
    logger.info(f"Total alerts: {stats['total_alerts']}")
    logger.info(f"By zone: {stats['by_zone']}")


def example_custom_rule():
    """Example of creating and using custom rules."""
    logger.info("\n=== Example 5: Custom Alert Rule ===")

    config = get_example_config_small_site()
    rules = AlertRules()

    # Create custom rule for contractor violations
    contractor_rule = AlertRule(
        rule_id="CUSTOM_CONTRACTOR",
        name="Taşeron İhlal Kontrolü",
        description="Taşeron çalışanlarının ihlalleri için özel bildirim",
        condition_type=RuleCondition.PATTERN_BASED,
        action=RuleAction.SEND_ALERT,
        priority="warning",
        threshold_value=1,  # Any violation
        recipient_groups=["safety_officer", "contractor_supervisor"],
        notification_channels=["email", "telegram"]
    )

    rules.add_rule(contractor_rule)
    alert_manager = AlertManager(config, rules)

    # Process contractor violation (worker ID starts with 'T' for taşeron)
    alert = alert_manager.process_violation(
        zone="Boyahane",
        camera_id="CAM_007",
        missing_ppe=["mask", "goggles"],
        worker_id="T12345",
        timestamp=datetime.now()
    )

    if alert:
        logger.info(f"Contractor violation alert: {alert.alert_id}")
        logger.info(f"Matched rules: {alert.matched_rules}")


def example_escalation_workflow():
    """Example of alert escalation workflow."""
    logger.info("\n=== Example 6: Escalation Workflow ===")

    config = get_example_config_small_site()
    config.escalation.enabled = True
    config.escalation.escalation_delay_minutes = 1  # Short delay for demo

    rules = AlertRules()
    alert_manager = AlertManager(config, rules)

    # Create alert
    alert = alert_manager.process_violation(
        zone="Elektrik Panosu",
        camera_id="CAM_008",
        missing_ppe=["gloves", "goggles"],
        worker_id="W99999",
        timestamp=datetime.now()
    )

    if alert:
        logger.info(f"Alert created: {alert.alert_id}")
        logger.info(f"Escalation scheduled for: {alert_manager.pending_escalations.get(alert.alert_id)}")

        # Simulate checking escalations after delay
        logger.info("Checking for escalations...")
        escalated = alert_manager.check_escalations()

        if escalated:
            logger.info(f"Escalated alerts: {escalated}")
        else:
            logger.info("No escalations yet (delay not reached)")


def example_acknowledgment():
    """Example of alert acknowledgment."""
    logger.info("\n=== Example 7: Alert Acknowledgment ===")

    config = get_example_config_small_site()
    rules = AlertRules()
    alert_manager = AlertManager(config, rules)

    # Create alert
    alert = alert_manager.process_violation(
        zone="Vinç Bölgesi",
        camera_id="CAM_009",
        missing_ppe=["vest"],
        worker_id="W77777",
        timestamp=datetime.now()
    )

    if alert:
        logger.info(f"Alert created: {alert.alert_id}")
        logger.info(f"Acknowledged: {alert.acknowledged}")

        # Acknowledge alert
        success = alert_manager.acknowledge_alert(
            alert_id=alert.alert_id,
            acknowledged_by="İSG Uzmanı - Mehmet Demir"
        )

        if success:
            logger.info("Alert acknowledged successfully")
            logger.info(f"Active alerts: {len(alert_manager.active_alerts)}")
            logger.info(f"Acknowledged alerts: {len(alert_manager.acknowledged_alerts)}")


def example_summary_report():
    """Example of generating summary reports."""
    logger.info("\n=== Example 8: Summary Report ===")

    config = get_example_config_small_site()
    rules = AlertRules()
    alert_manager = AlertManager(config, rules)

    # Simulate a day's worth of violations
    zones = ["İnşaat Alanı", "Kazı Alanı", "Yüksekte Çalışma Alanı"]
    ppe_types = [["helmet"], ["vest"], ["helmet", "vest"], ["harness"]]

    for i in range(15):
        zone = zones[i % len(zones)]
        ppe = ppe_types[i % len(ppe_types)]

        alert_manager.process_violation(
            zone=zone,
            camera_id=f"CAM_{i % 5}",
            missing_ppe=ppe,
            worker_id=f"W{3000 + i}",
            timestamp=datetime.now() - timedelta(hours=24-i)
        )

    # Generate report
    start_time = datetime.now() - timedelta(days=1)
    end_time = datetime.now()

    report = alert_manager.generate_summary_report(start_time, end_time)
    logger.info("Daily Summary Report:\n" + report)


def example_quiet_hours():
    """Example of quiet hours configuration."""
    logger.info("\n=== Example 9: Quiet Hours ===")

    config = get_example_config_small_site()

    # Enable quiet hours
    from datetime import time
    config.quiet_hours.enabled = True
    config.quiet_hours.start_time = time(22, 0)
    config.quiet_hours.end_time = time(7, 0)
    config.quiet_hours.emergency_override = True

    rules = AlertRules()
    alert_manager = AlertManager(config, rules)

    # Test if quiet hours are active
    is_quiet = config.is_quiet_hours()
    logger.info(f"Currently in quiet hours: {is_quiet}")

    # Process violation during quiet hours
    # (Would be suppressed unless critical with emergency_override)
    alert = alert_manager.process_violation(
        zone="Genel Alan",
        camera_id="CAM_010",
        missing_ppe=["vest"],
        worker_id="W88888",
        timestamp=datetime.now()
    )

    if alert:
        logger.info(f"Alert sent despite quiet hours: {alert.alert_id}")
    else:
        logger.info("Alert suppressed due to quiet hours")


def example_statistics():
    """Example of getting alert statistics."""
    logger.info("\n=== Example 10: Statistics ===")

    config = get_example_config_large_site()
    rules = AlertRules()
    alert_manager = AlertManager(config, rules)

    # Simulate violations
    for i in range(20):
        alert_manager.process_violation(
            zone=f"Bölge {(i % 3) + 1}",
            camera_id=f"CAM_{i % 5}",
            missing_ppe=["helmet"] if i % 2 == 0 else ["vest"],
            worker_id=f"W{4000 + i}",
            timestamp=datetime.now() - timedelta(hours=i)
        )

    # Get statistics
    stats = alert_manager.get_alert_statistics()

    logger.info("Alert Statistics:")
    logger.info(f"  Total alerts: {stats['total_alerts']}")
    logger.info(f"  By priority: {stats['by_priority']}")
    logger.info(f"  By zone: {stats['by_zone']}")
    logger.info(f"  PPE violations: {stats['ppe_violations']}")
    logger.info(f"  Active alerts: {stats['active_alerts']}")
    logger.info(f"  Acknowledged: {stats['acknowledged_alerts']}")


def example_different_site_configs():
    """Example comparing different site configurations."""
    logger.info("\n=== Example 11: Different Site Configurations ===")

    # Small site
    small_config = get_example_config_small_site()
    logger.info("Small Site Config:")
    logger.info(f"  Violation threshold: {small_config.violation_count_threshold}")
    logger.info(f"  Max alerts/hour: {small_config.throttle.max_alerts_per_hour}")
    logger.info(f"  Recipient groups: {list(small_config.recipient_groups.keys())}")

    # Large site
    large_config = get_example_config_large_site()
    logger.info("\nLarge Site Config:")
    logger.info(f"  Violation threshold: {large_config.violation_count_threshold}")
    logger.info(f"  Max alerts/hour: {large_config.throttle.max_alerts_per_hour}")
    logger.info(f"  Recipient groups: {list(large_config.recipient_groups.keys())}")

    # Critical infrastructure
    critical_config = get_example_config_critical_infrastructure()
    logger.info("\nCritical Infrastructure Config:")
    logger.info(f"  Violation threshold: {critical_config.violation_count_threshold}")
    logger.info(f"  Compliance threshold: {critical_config.compliance_rate_threshold}")
    logger.info(f"  Critical zones: {len(critical_config.critical_zones)}")
    logger.info(f"  Quiet hours enabled: {critical_config.quiet_hours.enabled}")


def example_rule_export():
    """Example of exporting and viewing rules."""
    logger.info("\n=== Example 12: Rule Export ===")

    rules = AlertRules()

    # Export all rules
    rules_export = rules.export_rules()

    logger.info("Configured Alert Rules:")
    for rule_id, rule_data in rules_export.items():
        logger.info(f"\n{rule_id}: {rule_data['name']}")
        logger.info(f"  Description: {rule_data['description']}")
        logger.info(f"  Priority: {rule_data['priority']}")
        logger.info(f"  Condition: {rule_data['condition_type']}")
        logger.info(f"  Action: {rule_data['action']}")
        if rule_data['zones']:
            logger.info(f"  Zones: {rule_data['zones']}")


def main():
    """Run all examples."""
    examples = [
        ("Basic Usage", example_basic_usage),
        ("Critical Zone Violation", example_critical_zone_violation),
        ("Multiple Violations Pattern", example_multiple_violations_pattern),
        ("Compliance Monitoring", example_compliance_monitoring),
        ("Custom Rule", example_custom_rule),
        ("Escalation Workflow", example_escalation_workflow),
        ("Acknowledgment", example_acknowledgment),
        ("Summary Report", example_summary_report),
        ("Quiet Hours", example_quiet_hours),
        ("Statistics", example_statistics),
        ("Different Site Configs", example_different_site_configs),
        ("Rule Export", example_rule_export),
    ]

    logger.info("=" * 70)
    logger.info("PPE Detection Alert System - Example Usage")
    logger.info("=" * 70)

    for name, example_func in examples:
        try:
            example_func()
            logger.info(f"\n{'=' * 70}\n")
            time.sleep(0.5)  # Small delay between examples
        except Exception as e:
            logger.error(f"Error in example '{name}': {e}", exc_info=True)

    logger.info("All examples completed!")


if __name__ == "__main__":
    main()
