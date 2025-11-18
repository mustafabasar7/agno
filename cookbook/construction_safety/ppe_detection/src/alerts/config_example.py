"""
Configuration examples for different Turkish construction site scenarios.
Copy and modify this file as config.py for your specific needs.
"""

from datetime import time
from alert_config import (
    AlertConfig, RecipientGroup, AlertPriority,
    NotificationChannel, ThrottleConfig, QuietHours, EscalationConfig
)


def get_production_config() -> AlertConfig:
    """
    Production configuration template.
    Replace placeholder values with your actual credentials.
    """
    config = AlertConfig()

    # ========================================
    # EMAIL CONFIGURATION (SMTP)
    # ========================================
    config.smtp_host = "smtp.gmail.com"
    config.smtp_port = 587
    config.smtp_username = "your-email@gmail.com"  # CHANGE THIS
    config.smtp_password = "your-app-password"      # CHANGE THIS (use app password for Gmail)
    config.smtp_use_tls = True
    config.email_from = "santiye-guvenlik@yourcompany.com"  # CHANGE THIS

    # ========================================
    # TELEGRAM CONFIGURATION
    # ========================================
    # 1. Create bot via @BotFather on Telegram
    # 2. Copy the bot token
    # 3. Get chat ID by sending /start to your bot, then:
    #    https://api.telegram.org/bot<TOKEN>/getUpdates
    config.telegram_bot_token = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"  # CHANGE THIS
    config.telegram_default_chat_id = "123456789"  # CHANGE THIS

    # ========================================
    # TWILIO SMS CONFIGURATION
    # ========================================
    # Get credentials from https://www.twilio.com/console
    config.twilio_account_sid = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # CHANGE THIS
    config.twilio_auth_token = "your_auth_token_here"  # CHANGE THIS
    config.twilio_from_number = "+905551234567"  # CHANGE THIS (verified Twilio number)

    # ========================================
    # WEBHOOK CONFIGURATION
    # ========================================
    config.webhook_timeout_seconds = 10
    config.webhook_retry_attempts = 3

    # ========================================
    # WEBSOCKET CONFIGURATION
    # ========================================
    config.websocket_url = "ws://localhost:8080/alerts"  # CHANGE THIS if needed

    # ========================================
    # ENABLED NOTIFICATION CHANNELS
    # ========================================
    config.enabled_channels = {
        NotificationChannel.EMAIL,
        NotificationChannel.TELEGRAM,
        # NotificationChannel.SMS,      # Uncomment if SMS is configured
        # NotificationChannel.WEBHOOK,  # Uncomment if webhooks are configured
        NotificationChannel.WEBSOCKET
    }

    # ========================================
    # RECIPIENT GROUPS
    # ========================================
    config.recipient_groups = {
        "safety_officer": RecipientGroup(
            name="İSG Uzmanı",
            email_addresses=["isg@yourcompany.com"],  # CHANGE THIS
            telegram_chat_ids=["123456789"],  # CHANGE THIS
            phone_numbers=["+905551234567"],  # CHANGE THIS
            priority_threshold=AlertPriority.INFO
        ),

        "site_manager": RecipientGroup(
            name="Şantiye Müdürü",
            email_addresses=["santiye.muduru@yourcompany.com"],  # CHANGE THIS
            telegram_chat_ids=["987654321"],  # CHANGE THIS
            phone_numbers=["+905559876543"],  # CHANGE THIS
            priority_threshold=AlertPriority.WARNING
        ),

        "zone_supervisors": RecipientGroup(
            name="Bölge Şefleri",
            email_addresses=[
                "bolge1@yourcompany.com",  # CHANGE THIS
                "bolge2@yourcompany.com",  # CHANGE THIS
            ],
            telegram_chat_ids=["111111111", "222222222"],  # CHANGE THIS
            priority_threshold=AlertPriority.WARNING
        ),

        "emergency": RecipientGroup(
            name="Acil Durum Ekibi",
            email_addresses=["acil@yourcompany.com"],  # CHANGE THIS
            phone_numbers=["+905551111111"],  # CHANGE THIS
            priority_threshold=AlertPriority.CRITICAL
        ),

        "management": RecipientGroup(
            name="Üst Yönetim",
            email_addresses=[
                "genel.mudur@yourcompany.com",  # CHANGE THIS
            ],
            priority_threshold=AlertPriority.CRITICAL
        )
    }

    # ========================================
    # ALERT THRESHOLDS
    # ========================================
    config.violation_count_threshold = 3  # Alert if >= 3 violations
    config.violation_time_window_minutes = 10  # Within 10 minutes
    config.compliance_rate_threshold = 0.80  # 80% compliance minimum

    # ========================================
    # CRITICAL ZONES (Higher priority alerts)
    # ========================================
    config.critical_zones = {
        "Yüksekte Çalışma Alanı",
        "Elektrik Panosu",
        "Vinç Bölgesi",
        "Kazı Alanı",
        "Kapalı Alan",
        # Add your critical zones here
    }

    # ========================================
    # THROTTLING
    # ========================================
    config.throttle = ThrottleConfig(
        max_alerts_per_hour=20,
        max_alerts_per_day=100,
        deduplication_window_minutes=15,
        same_zone_throttle_minutes=5
    )

    # ========================================
    # QUIET HOURS
    # ========================================
    config.quiet_hours = QuietHours(
        enabled=True,
        start_time=time(22, 0),  # 22:00
        end_time=time(7, 0),     # 07:00
        emergency_override=True   # Send critical alerts even during quiet hours
    )

    # ========================================
    # ESCALATION
    # ========================================
    config.escalation = EscalationConfig(
        enabled=True,
        escalation_delay_minutes=30,
        max_escalation_level=3,
        escalation_groups=[
            "zone_supervisors",  # Level 1
            "safety_officer",    # Level 2
            "site_manager",      # Level 3
            "management"         # Level 4 (max)
        ]
    )

    # ========================================
    # OTHER SETTINGS
    # ========================================
    config.alert_retention_days = 90
    config.require_acknowledgment = True
    config.auto_acknowledge_after_hours = 24

    return config


def get_development_config() -> AlertConfig:
    """
    Development/testing configuration.
    Uses console output and limited notifications.
    """
    config = AlertConfig()

    # Minimal email config for testing
    config.smtp_host = "smtp.gmail.com"
    config.smtp_port = 587
    config.email_from = "test@localhost"

    # Only enable WebSocket for development
    config.enabled_channels = {
        NotificationChannel.WEBSOCKET
    }

    # Single test recipient
    config.recipient_groups = {
        "developer": RecipientGroup(
            name="Developer",
            email_addresses=["developer@localhost"],
            priority_threshold=AlertPriority.INFO
        )
    }

    # Lower thresholds for testing
    config.violation_count_threshold = 2
    config.violation_time_window_minutes = 5

    # No quiet hours in development
    config.quiet_hours.enabled = False

    # Faster escalation for testing
    config.escalation.escalation_delay_minutes = 1

    return config


def get_demo_config() -> AlertConfig:
    """
    Demo configuration for presentations.
    Shows all features with fake data.
    """
    config = AlertConfig()

    # Demo recipients (not real)
    config.recipient_groups = {
        "demo_safety": RecipientGroup(
            name="Demo İSG Uzmanı",
            email_addresses=["demo-isg@example.com"],
            telegram_chat_ids=["000000000"],
            priority_threshold=AlertPriority.INFO
        ),
        "demo_manager": RecipientGroup(
            name="Demo Şantiye Müdürü",
            email_addresses=["demo-mudur@example.com"],
            priority_threshold=AlertPriority.WARNING
        )
    }

    # Demo zones
    config.critical_zones = {
        "Demo Yüksekte Çalışma",
        "Demo Elektrik Panosu"
    }

    # Show all features
    config.enabled_channels = {
        NotificationChannel.WEBSOCKET
    }

    config.quiet_hours.enabled = False
    config.escalation.enabled = True
    config.escalation.escalation_delay_minutes = 2

    return config


# ========================================
# TURKISH SMS PROVIDER CONFIGURATIONS
# ========================================

# If using Turkish SMS providers instead of Twilio:

NETGSM_CONFIG = {
    'provider': 'netgsm',
    'api_url': 'https://api.netgsm.com.tr/sms/send/get',
    'username': 'YOUR_USERNAME',  # CHANGE THIS
    'password': 'YOUR_PASSWORD',  # CHANGE THIS
    'header': 'SANTIYE',          # Your registered sender name
}

ILETIMERKEZI_CONFIG = {
    'provider': 'iletimerkezi',
    'api_url': 'https://api.iletimerkezi.com/v1/send-sms',
    'api_key': 'YOUR_API_KEY',    # CHANGE THIS
    'api_secret': 'YOUR_SECRET',  # CHANGE THIS
    'sender': 'SANTIYE',
}

VATANSMS_CONFIG = {
    'provider': 'vatansms',
    'api_url': 'https://api.vatansms.net/api/v1/1toN',
    'api_id': 'YOUR_API_ID',      # CHANGE THIS
    'api_key': 'YOUR_API_KEY',    # CHANGE THIS
    'sender': 'SANTIYE',
}


# ========================================
# WEBHOOK URLS FOR INTEGRATIONS
# ========================================

# Slack webhook example
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX"

# Microsoft Teams webhook example
TEAMS_WEBHOOK_URL = "https://outlook.office.com/webhook/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX@XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX/IncomingWebhook/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# Discord webhook example
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/XXXXXXXXXXXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# Custom webhook example
CUSTOM_WEBHOOK_URL = "https://your-server.com/webhooks/ppe-alerts"


# ========================================
# ENVIRONMENT-BASED CONFIGURATION
# ========================================

def get_config_from_env():
    """
    Load configuration from environment variables.
    Useful for Docker deployments and CI/CD.
    """
    import os

    config = AlertConfig()

    # Email
    config.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    config.smtp_port = int(os.getenv('SMTP_PORT', '587'))
    config.smtp_username = os.getenv('SMTP_USERNAME', '')
    config.smtp_password = os.getenv('SMTP_PASSWORD', '')
    config.email_from = os.getenv('EMAIL_FROM', 'alerts@example.com')

    # Telegram
    config.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    config.telegram_default_chat_id = os.getenv('TELEGRAM_CHAT_ID', '')

    # Twilio
    config.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
    config.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN', '')
    config.twilio_from_number = os.getenv('TWILIO_FROM_NUMBER', '')

    # Thresholds
    config.violation_count_threshold = int(os.getenv('VIOLATION_THRESHOLD', '3'))
    config.compliance_rate_threshold = float(os.getenv('COMPLIANCE_THRESHOLD', '0.80'))

    return config


# ========================================
# USAGE
# ========================================

if __name__ == "__main__":
    # Example: Load production config
    config = get_production_config()
    print(f"Configuration loaded: {len(config.recipient_groups)} recipient groups")
    print(f"Enabled channels: {[ch.value for ch in config.enabled_channels]}")
    print(f"Critical zones: {len(config.critical_zones)}")

    # Example: Load from environment
    # config = get_config_from_env()

    # Example: Load development config
    # config = get_development_config()
