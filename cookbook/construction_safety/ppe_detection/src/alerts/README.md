# Alert and Notification System

Comprehensive alert and notification system for PPE (Personal Protective Equipment) detection in Turkish construction sites.

## Features

- **Multi-Channel Notifications**: Email, SMS, Telegram, Webhook, WebSocket
- **Smart Alert Rules**: Configurable conditions and thresholds
- **De-duplication**: Prevents spam from repeated violations
- **Throttling**: Limits alerts to prevent overload
- **Priority Levels**: Critical, Warning, Info
- **Escalation**: Automatic escalation if alerts not acknowledged
- **Quiet Hours**: Configurable quiet hours (with emergency override)
- **Turkish Templates**: Professional Turkish message templates
- **Zone-Based Filtering**: Different rules for different zones
- **Real-time Dashboard**: WebSocket updates for live monitoring

## Architecture

```
alerts/
├── __init__.py
├── alert_manager.py         # Main alert coordinator
├── alert_config.py          # Configuration and settings
├── alert_rules.py           # Rule engine
├── alert_templates.py       # Turkish message templates
└── notifiers/               # Notification channel implementations
    ├── email_notifier.py    # SMTP email notifications
    ├── webhook_notifier.py  # Webhook integrations (Slack, Teams, etc.)
    ├── telegram_notifier.py # Telegram bot notifications
    ├── sms_notifier.py      # SMS via Twilio or Turkish providers
    └── websocket_notifier.py # Real-time dashboard updates
```

## Quick Start

### 1. Basic Configuration

```python
from alerts.alert_config import get_example_config_small_site
from alerts.alert_manager import AlertManager
from alerts.alert_rules import AlertRules

# Load configuration for small construction site
config = get_example_config_small_site()

# Create alert manager
rules = AlertRules()
alert_manager = AlertManager(config, rules)
```

### 2. Process a Violation

```python
from datetime import datetime

# Detect a violation
alert = alert_manager.process_violation(
    zone="Yüksekte Çalışma Alanı",
    camera_id="CAM_001",
    missing_ppe=["helmet", "harness"],
    worker_id="W12345",
    image_url="http://example.com/violations/img_001.jpg",
    timestamp=datetime.now()
)

if alert:
    print(f"Alert sent: {alert.alert_id}")
else:
    print("Alert filtered or throttled")
```

### 3. Acknowledge Alert

```python
# Acknowledge an alert
success = alert_manager.acknowledge_alert(
    alert_id="VIO-20250118120000000",
    acknowledged_by="İSG Uzmanı - Ahmet Yılmaz"
)
```

### 4. Generate Summary Report

```python
from datetime import datetime, timedelta

# Generate daily report
start_time = datetime.now() - timedelta(days=1)
end_time = datetime.now()

report = alert_manager.generate_summary_report(start_time, end_time)
print(report)
```

## Configuration Examples

### Small Construction Site (50-100 workers)

```python
from alerts.alert_config import get_example_config_small_site

config = get_example_config_small_site()
```

### Large Construction Site (500+ workers)

```python
from alerts.alert_config import get_example_config_large_site

config = get_example_config_large_site()
```

### Critical Infrastructure (Power Plants, Refineries)

```python
from alerts.alert_config import get_example_config_critical_infrastructure

config = get_example_config_critical_infrastructure()
```

### Custom Configuration

```python
from alerts.alert_config import AlertConfig, RecipientGroup, AlertPriority

config = AlertConfig()

# Configure SMTP
config.smtp_host = "smtp.gmail.com"
config.smtp_port = 587
config.smtp_username = "your-email@gmail.com"
config.smtp_password = "your-app-password"
config.smtp_use_tls = True
config.email_from = "santiye-guvenlik@example.com"

# Configure Telegram
config.telegram_bot_token = "YOUR_BOT_TOKEN"
config.telegram_default_chat_id = "YOUR_CHAT_ID"

# Configure Twilio SMS
config.twilio_account_sid = "YOUR_ACCOUNT_SID"
config.twilio_auth_token = "YOUR_AUTH_TOKEN"
config.twilio_from_number = "+905551234567"

# Add recipient groups
config.recipient_groups = {
    "safety_officer": RecipientGroup(
        name="İSG Uzmanı",
        email_addresses=["isg@santiye.com"],
        telegram_chat_ids=["123456789"],
        phone_numbers=["+905551234567"],
        priority_threshold=AlertPriority.INFO
    ),
    "site_manager": RecipientGroup(
        name="Şantiye Müdürü",
        email_addresses=["mudur@santiye.com"],
        phone_numbers=["+905559876543"],
        priority_threshold=AlertPriority.WARNING
    )
}

# Configure thresholds
config.violation_count_threshold = 3
config.violation_time_window_minutes = 10
config.compliance_rate_threshold = 0.80

# Configure critical zones
config.critical_zones = {
    "Yüksekte Çalışma Alanı",
    "Elektrik Panosu",
    "Vinç Bölgesi"
}
```

## Alert Rules

The system comes with pre-configured rules for common scenarios:

### Rule 1: Multiple Violations in Same Zone
- Trigger: 3+ violations in 10 minutes in same zone
- Priority: Warning
- Recipients: Safety Officer, Zone Supervisors

### Rule 2: Low Compliance Rate
- Trigger: Compliance rate < 80%
- Priority: Critical
- Recipients: Safety Officer, Site Manager

### Rule 3: Critical Zone Violation
- Trigger: Any violation in critical zones
- Priority: Critical
- Recipients: Safety Officer, Site Manager, Emergency Team

### Rule 4: Helmet Violation
- Trigger: Helmet missing
- Priority: Warning
- Recipients: Zone Supervisors

### Rule 5: Daily Summary Report
- Trigger: Every day at 18:00
- Priority: Info
- Recipients: Safety Officer, Site Manager

### Custom Rules

```python
from alerts.alert_rules import AlertRule, RuleCondition, RuleAction

# Create custom rule
custom_rule = AlertRule(
    rule_id="CUSTOM_001",
    name="Gece Kritik Bölge",
    description="Gece vardiyasında kritik bölge ihlali",
    condition_type=RuleCondition.PATTERN_BASED,
    action=RuleAction.SEND_ALERT,
    priority="critical",
    zones=["Elektrik Panosu"],
    active_hours=(20, 6),  # 20:00 - 06:00
    recipient_groups=["night_supervisor", "emergency"],
    notification_channels=["sms", "telegram"]
)

# Add to rule engine
rules.add_rule(custom_rule)
```

## Message Templates

The system includes professional Turkish message templates for different audiences:

### Manager Template
Brief, actionable information focusing on what needs to be done.

### Safety Officer Template
Detailed technical information including legal references and action items.

### Supervisor Template
Practical, immediate action-focused messages.

### Summary Reports
Comprehensive daily/weekly reports with statistics and trends.

## Notification Channels

### Email (SMTP)

```python
# Configure in alert_config.py
config.smtp_host = "smtp.gmail.com"
config.smtp_port = 587
config.smtp_username = "your-email@gmail.com"
config.smtp_password = "your-app-password"
```

### Telegram

```python
# 1. Create bot via @BotFather
# 2. Get bot token
# 3. Get chat ID (send message to bot, then use getUpdates API)

config.telegram_bot_token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
config.telegram_default_chat_id = "123456789"
```

### SMS (Twilio)

```python
config.twilio_account_sid = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
config.twilio_auth_token = "your_auth_token"
config.twilio_from_number = "+905551234567"
```

### SMS (Turkish Providers)

```python
from alerts.notifiers.sms_notifier import AlternativeSMSNotifier, get_netgsm_config

# Configure Turkish SMS provider
provider_config = get_netgsm_config()
provider_config['api_key'] = 'YOUR_API_KEY'

sms_notifier = AlternativeSMSNotifier(config, provider_config)
```

### Webhook (Slack, Teams, Discord)

```python
# Add webhook URLs to recipient groups
config.recipient_groups["ops_team"] = RecipientGroup(
    name="Operasyon Ekibi",
    webhook_urls=[
        "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
        "https://outlook.office.com/webhook/YOUR_TEAMS_WEBHOOK"
    ]
)
```

### WebSocket (Real-time Dashboard)

```python
# WebSocket notifier automatically broadcasts to connected clients
# No additional configuration needed - just connect from your dashboard
```

## De-duplication

The system prevents spam by de-duplicating similar violations:

```python
# Configure de-duplication window
config.throttle.deduplication_window_minutes = 15

# Same violation (zone + camera + missing PPE) within 15 minutes
# will be filtered out
```

## Throttling

Prevent alert overload with configurable limits:

```python
# Global throttling
config.throttle.max_alerts_per_hour = 20
config.throttle.max_alerts_per_day = 100

# Zone-specific throttling
config.throttle.same_zone_throttle_minutes = 5
```

## Quiet Hours

Configure quiet hours to prevent alerts during night time:

```python
from datetime import time

config.quiet_hours.enabled = True
config.quiet_hours.start_time = time(22, 0)  # 22:00
config.quiet_hours.end_time = time(7, 0)     # 07:00
config.quiet_hours.emergency_override = True  # Send critical alerts anyway
```

## Escalation

Automatic escalation if alerts are not acknowledged:

```python
config.escalation.enabled = True
config.escalation.escalation_delay_minutes = 30
config.escalation.max_escalation_level = 3
config.escalation.escalation_groups = [
    "zone_supervisors",  # Level 1
    "safety_officer",    # Level 2
    "site_manager",      # Level 3
    "emergency"          # Level 4
]
```

## Statistics and Reporting

```python
# Get statistics
stats = alert_manager.get_alert_statistics(
    start_time=datetime.now() - timedelta(days=7),
    end_time=datetime.now()
)

print(f"Total alerts: {stats['total_alerts']}")
print(f"By priority: {stats['by_priority']}")
print(f"By zone: {stats['by_zone']}")
print(f"PPE violations: {stats['ppe_violations']}")
```

## Integration Example

```python
import logging
from datetime import datetime
from alerts.alert_config import get_example_config_small_site
from alerts.alert_manager import AlertManager
from alerts.alert_rules import AlertRules

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize system
config = get_example_config_small_site()
rules = AlertRules()
alert_manager = AlertManager(config, rules)

# Process violations from your detection system
def on_violation_detected(detection_result):
    """Called when PPE detection system detects a violation."""

    alert = alert_manager.process_violation(
        zone=detection_result['zone'],
        camera_id=detection_result['camera_id'],
        missing_ppe=detection_result['missing_ppe'],
        worker_id=detection_result.get('worker_id'),
        image_url=detection_result.get('image_url'),
        timestamp=datetime.now(),
        metadata={
            'confidence': detection_result.get('confidence'),
            'detector_version': '1.0.0'
        }
    )

    if alert:
        logging.info(f"Alert sent: {alert.alert_id}")
    else:
        logging.debug("Violation filtered")

# Periodic tasks
def check_escalations():
    """Run periodically (e.g., every minute) to check escalations."""
    escalated = alert_manager.check_escalations()
    if escalated:
        logging.info(f"Escalated alerts: {escalated}")

# Generate daily report
def send_daily_report():
    """Run once per day (e.g., at 18:00)."""
    report = alert_manager.generate_summary_report()
    # Send report via email or other channels
    logging.info("Daily report generated")
```

## Testing

```python
# Test email configuration
from alerts.notifiers.email_notifier import EmailNotifier

notifier = EmailNotifier(config)
# Send test email manually

# Test Telegram connection
from alerts.notifiers.telegram_notifier import TelegramNotifier

telegram = TelegramNotifier(config)
if telegram.test_connection():
    print("Telegram connected successfully!")

# Test Twilio SMS
from alerts.notifiers.sms_notifier import SMSNotifier

sms = SMSNotifier(config)
if sms.test_connection():
    print("Twilio connected successfully!")

# Test webhook
from alerts.notifiers.webhook_notifier import WebhookNotifier

webhook = WebhookNotifier(config)
webhook.send_test_notification("https://hooks.slack.com/services/YOUR/WEBHOOK")
```

## Troubleshooting

### Email Not Sending

1. Check SMTP credentials
2. Enable "Less secure app access" for Gmail
3. Use App Password for Gmail with 2FA
4. Check firewall/network settings

### Telegram Not Working

1. Verify bot token with @BotFather
2. Start conversation with bot before sending
3. Check chat ID is correct
4. Verify network can reach api.telegram.org

### SMS Not Sending

1. Check Twilio account credentials
2. Verify phone numbers are in E.164 format (+905551234567)
3. Check Twilio account balance
4. Verify numbers are not blocked

### Webhook Failing

1. Check webhook URL is accessible
2. Verify SSL certificate is valid
3. Check webhook timeout settings
4. Review webhook provider logs

## Performance Considerations

- **De-duplication**: Uses in-memory cache, cleared periodically
- **Throttling**: Lightweight counters, reset hourly/daily
- **Message Queue**: Consider using Redis or RabbitMQ for high-volume scenarios
- **Database**: Store alert history in database for long-term retention
- **Async Processing**: Use async notifiers for better performance

## Security

- **Credentials**: Never commit credentials to version control
- **Environment Variables**: Use environment variables for sensitive data
- **Encryption**: Use TLS/SSL for all network communications
- **Rate Limiting**: Implement rate limiting to prevent abuse
- **Authentication**: Secure webhook endpoints with authentication

## License

Part of the PPE Detection System for Turkish Construction Sites.
