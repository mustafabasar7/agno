"""
Webhook notifier for integrations with external services.
Supports Slack, Microsoft Teams, Discord, and custom webhooks.
"""

import logging
import requests
import json
from typing import List, Dict, Optional
from datetime import datetime

from ..alert_config import AlertConfig, RecipientGroup
from ..alert_templates import AlertTemplates, TemplateType


class WebhookNotifier:
    """Send alerts via webhooks to external services."""

    def __init__(self, config: AlertConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def send(
        self,
        alert,
        recipients: List[RecipientGroup],
        template_type: TemplateType = TemplateType.MANAGER
    ) -> bool:
        """
        Send alert via webhook.

        Args:
            alert: Alert object
            recipients: List of recipient groups
            template_type: Template type to use

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Collect all webhook URLs
            webhook_urls = []
            for group in recipients:
                webhook_urls.extend(group.webhook_urls)

            if not webhook_urls:
                self.logger.warning("No webhook URLs configured")
                return False

            success_count = 0
            for url in webhook_urls:
                if self._send_webhook(url, alert, template_type):
                    success_count += 1

            return success_count > 0

        except Exception as e:
            self.logger.error(f"Error sending webhook alert: {e}")
            return False

    def _send_webhook(self, url: str, alert, template_type: TemplateType) -> bool:
        """Send to a single webhook URL."""
        try:
            # Detect webhook type
            webhook_type = self._detect_webhook_type(url)

            # Generate payload based on type
            if webhook_type == 'slack':
                payload = self._create_slack_payload(alert, template_type)
            elif webhook_type == 'teams':
                payload = self._create_teams_payload(alert, template_type)
            elif webhook_type == 'discord':
                payload = self._create_discord_payload(alert, template_type)
            else:
                payload = self._create_generic_payload(alert, template_type)

            # Send request
            response = requests.post(
                url,
                json=payload,
                timeout=self.config.webhook_timeout_seconds,
                headers={'Content-Type': 'application/json'}
            )

            response.raise_for_status()
            self.logger.info(f"Webhook sent successfully to {webhook_type}")
            return True

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Webhook request failed: {e}")

            # Retry if configured
            if self.config.webhook_retry_attempts > 1:
                return self._retry_webhook(url, alert, template_type)

            return False

    def _retry_webhook(self, url: str, alert, template_type: TemplateType) -> bool:
        """Retry sending webhook."""
        import time

        for attempt in range(1, self.config.webhook_retry_attempts):
            try:
                time.sleep(2 ** attempt)  # Exponential backoff
                self.logger.info(f"Retrying webhook (attempt {attempt + 1})")

                if self._send_webhook(url, alert, template_type):
                    return True

            except Exception as e:
                self.logger.error(f"Retry {attempt} failed: {e}")

        return False

    def _detect_webhook_type(self, url: str) -> str:
        """Detect webhook service type from URL."""
        if 'slack.com' in url:
            return 'slack'
        elif 'office.com' in url or 'outlook.com' in url:
            return 'teams'
        elif 'discord.com' in url or 'discordapp.com' in url:
            return 'discord'
        else:
            return 'generic'

    def _create_slack_payload(self, alert, template_type: TemplateType) -> Dict:
        """Create Slack message payload."""

        # Priority color
        priority_colors = {
            'critical': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8'
        }
        color = priority_colors.get(alert.priority.value, '#6c757d')

        # Format message
        message = AlertTemplates.format_violation_alert(
            template_type,
            alert.priority.value,
            alert.zone,
            alert.camera_id,
            alert.missing_ppe,
            alert.timestamp,
            alert.worker_id,
            alert.image_url,
            alert.violation_count,
            alert.compliance_rate
        )

        # PPE names in Turkish
        ppe_names = [AlertTemplates.PPE_NAMES.get(ppe, ppe) for ppe in alert.missing_ppe]

        payload = {
            "username": "KKD Tespit Sistemi",
            "icon_emoji": ":warning:",
            "attachments": [
                {
                    "color": color,
                    "fallback": f"KKD İhlali - {alert.zone}",
                    "pretext": f"*{AlertTemplates.SEVERITY_NAMES.get(alert.priority.value, 'UYARI')} - KKD İhlali Tespit Edildi*",
                    "fields": [
                        {
                            "title": "Bölge",
                            "value": alert.zone,
                            "short": True
                        },
                        {
                            "title": "Kamera",
                            "value": alert.camera_id,
                            "short": True
                        },
                        {
                            "title": "Eksik KKD",
                            "value": ", ".join(ppe_names),
                            "short": False
                        },
                        {
                            "title": "Zaman",
                            "value": alert.timestamp.strftime('%d.%m.%Y %H:%M:%S'),
                            "short": True
                        },
                        {
                            "title": "İhlal Sayısı (10 dk)",
                            "value": str(alert.violation_count),
                            "short": True
                        }
                    ],
                    "footer": f"Alert ID: {alert.alert_id}",
                    "ts": int(alert.timestamp.timestamp())
                }
            ]
        }

        # Add image if available
        if alert.image_url:
            payload["attachments"][0]["image_url"] = alert.image_url

        # Add action buttons
        payload["attachments"][0]["actions"] = [
            {
                "type": "button",
                "text": "Dashboard'u Aç",
                "url": "http://localhost:8080/dashboard"
            },
            {
                "type": "button",
                "text": "Görüntüle",
                "url": alert.image_url if alert.image_url else "http://localhost:8080/alerts"
            }
        ]

        return payload

    def _create_teams_payload(self, alert, template_type: TemplateType) -> Dict:
        """Create Microsoft Teams message payload (Adaptive Card)."""

        # Priority color
        priority_colors = {
            'critical': 'attention',
            'warning': 'warning',
            'info': 'good'
        }
        color = priority_colors.get(alert.priority.value, 'default')

        # PPE names
        ppe_names = [AlertTemplates.PPE_NAMES.get(ppe, ppe) for ppe in alert.missing_ppe]

        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": f"KKD İhlali - {alert.zone}",
            "themeColor": "DC3545" if alert.priority.value == "critical" else "FFC107",
            "title": f"⚠️ {AlertTemplates.SEVERITY_NAMES.get(alert.priority.value, 'UYARI')} - KKD İhlali",
            "sections": [
                {
                    "activityTitle": f"Bölge: {alert.zone}",
                    "activitySubtitle": alert.timestamp.strftime('%d.%m.%Y %H:%M:%S'),
                    "facts": [
                        {
                            "name": "Kamera ID:",
                            "value": alert.camera_id
                        },
                        {
                            "name": "Eksik KKD:",
                            "value": ", ".join(ppe_names)
                        },
                        {
                            "name": "İhlal Sayısı:",
                            "value": str(alert.violation_count)
                        },
                        {
                            "name": "Alert ID:",
                            "value": alert.alert_id
                        }
                    ]
                }
            ],
            "potentialAction": [
                {
                    "@type": "OpenUri",
                    "name": "Dashboard'u Aç",
                    "targets": [
                        {
                            "os": "default",
                            "uri": "http://localhost:8080/dashboard"
                        }
                    ]
                }
            ]
        }

        # Add image if available
        if alert.image_url:
            payload["sections"][0]["images"] = [
                {
                    "image": alert.image_url
                }
            ]

        return payload

    def _create_discord_payload(self, alert, template_type: TemplateType) -> Dict:
        """Create Discord message payload."""

        # Priority color (decimal)
        priority_colors = {
            'critical': 14430003,  # Red
            'warning': 16763904,   # Orange
            'info': 1541891        # Blue
        }
        color = priority_colors.get(alert.priority.value, 8421504)

        # PPE names
        ppe_names = [AlertTemplates.PPE_NAMES.get(ppe, ppe) for ppe in alert.missing_ppe]

        embed = {
            "title": f"🚨 {AlertTemplates.SEVERITY_NAMES.get(alert.priority.value, 'UYARI')} - KKD İhlali",
            "description": f"**Bölge:** {alert.zone}\n**Eksik KKD:** {', '.join(ppe_names)}",
            "color": color,
            "fields": [
                {
                    "name": "Kamera ID",
                    "value": alert.camera_id,
                    "inline": True
                },
                {
                    "name": "İhlal Sayısı",
                    "value": str(alert.violation_count),
                    "inline": True
                },
                {
                    "name": "Zaman",
                    "value": alert.timestamp.strftime('%d.%m.%Y %H:%M:%S'),
                    "inline": False
                }
            ],
            "footer": {
                "text": f"Alert ID: {alert.alert_id}"
            },
            "timestamp": alert.timestamp.isoformat()
        }

        # Add image if available
        if alert.image_url:
            embed["image"] = {"url": alert.image_url}

        payload = {
            "username": "KKD Tespit Sistemi",
            "avatar_url": "https://example.com/safety-icon.png",
            "embeds": [embed]
        }

        return payload

    def _create_generic_payload(self, alert, template_type: TemplateType) -> Dict:
        """Create generic JSON payload for custom webhooks."""
        return AlertTemplates.format_webhook_payload(
            alert.priority.value,
            alert.zone,
            alert.camera_id,
            alert.missing_ppe,
            alert.timestamp,
            alert.worker_id,
            alert.image_url,
            alert.violation_count,
            alert.compliance_rate
        )

    def send_test_notification(self, url: str) -> bool:
        """Send test notification to verify webhook configuration."""
        try:
            test_payload = {
                "type": "test",
                "message": "PPE Detection System - Test Notification",
                "timestamp": datetime.now().isoformat(),
                "status": "ok"
            }

            # Detect type and create appropriate payload
            webhook_type = self._detect_webhook_type(url)

            if webhook_type == 'slack':
                test_payload = {
                    "text": "✅ KKD Tespit Sistemi - Test Bildirimi Başarılı"
                }
            elif webhook_type == 'teams':
                test_payload = {
                    "@type": "MessageCard",
                    "@context": "https://schema.org/extensions",
                    "summary": "Test Notification",
                    "title": "✅ KKD Tespit Sistemi",
                    "text": "Test bildirimi başarılı!"
                }
            elif webhook_type == 'discord':
                test_payload = {
                    "content": "✅ KKD Tespit Sistemi - Test Bildirimi Başarılı"
                }

            response = requests.post(
                url,
                json=test_payload,
                timeout=self.config.webhook_timeout_seconds
            )

            response.raise_for_status()
            self.logger.info(f"Test notification sent successfully to {webhook_type}")
            return True

        except Exception as e:
            self.logger.error(f"Test notification failed: {e}")
            return False
