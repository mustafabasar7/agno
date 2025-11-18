"""
Telegram notifier for instant messaging alerts.
Uses Telegram Bot API to send real-time notifications.
"""

import logging
import requests
from typing import List, Optional
from datetime import datetime

from ..alert_config import AlertConfig, RecipientGroup
from ..alert_templates import AlertTemplates, TemplateType


class TelegramNotifier:
    """Send alerts via Telegram Bot API."""

    def __init__(self, config: AlertConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.base_url = f"https://api.telegram.org/bot{config.telegram_bot_token}"

    def send(
        self,
        alert,
        recipients: List[RecipientGroup],
        template_type: TemplateType = TemplateType.SUPERVISOR
    ) -> bool:
        """
        Send alert via Telegram.

        Args:
            alert: Alert object
            recipients: List of recipient groups
            template_type: Template type to use (default: SUPERVISOR for concise messages)

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            if not self.config.telegram_bot_token:
                self.logger.warning("Telegram bot token not configured")
                return False

            # Collect all chat IDs
            chat_ids = []
            for group in recipients:
                chat_ids.extend(group.telegram_chat_ids)

            if not chat_ids:
                self.logger.warning("No Telegram chat IDs configured")
                return False

            # Generate message
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

            success_count = 0
            for chat_id in chat_ids:
                if self._send_message(chat_id, message, alert):
                    success_count += 1

            return success_count > 0

        except Exception as e:
            self.logger.error(f"Error sending Telegram alert: {e}")
            return False

    def _send_message(self, chat_id: str, message: str, alert) -> bool:
        """Send message to a specific chat."""
        try:
            # If image is available, send as photo with caption
            if alert.image_url:
                return self._send_photo(chat_id, alert.image_url, message, alert)
            else:
                return self._send_text(chat_id, message, alert)

        except Exception as e:
            self.logger.error(f"Error sending to chat {chat_id}: {e}")
            return False

    def _send_text(self, chat_id: str, message: str, alert) -> bool:
        """Send text message."""
        try:
            # Format message with Markdown
            formatted_message = self._format_markdown(message)

            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": formatted_message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False
            }

            # Add inline keyboard for actions
            keyboard = self._create_inline_keyboard(alert)
            if keyboard:
                payload["reply_markup"] = keyboard

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            self.logger.info(f"Telegram message sent to chat {chat_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send text message: {e}")
            return False

    def _send_photo(self, chat_id: str, photo_url: str, caption: str, alert) -> bool:
        """Send photo with caption."""
        try:
            # Format caption with Markdown (max 1024 characters for caption)
            formatted_caption = self._format_markdown(caption)
            if len(formatted_caption) > 1024:
                formatted_caption = formatted_caption[:1021] + "..."

            url = f"{self.base_url}/sendPhoto"
            payload = {
                "chat_id": chat_id,
                "photo": photo_url,
                "caption": formatted_caption,
                "parse_mode": "Markdown"
            }

            # Add inline keyboard
            keyboard = self._create_inline_keyboard(alert)
            if keyboard:
                payload["reply_markup"] = keyboard

            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()

            self.logger.info(f"Telegram photo sent to chat {chat_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send photo: {e}")
            # Fallback to text message
            return self._send_text(chat_id, caption, alert)

    def _format_markdown(self, text: str) -> str:
        """Format text for Telegram Markdown."""
        # Escape special characters
        # Note: This is basic formatting, might need adjustment based on actual message content

        # Replace emojis and format for Telegram
        text = text.replace('🚨', '🚨')
        text = text.replace('📍', '📍')
        text = text.replace('⏰', '⏰')
        text = text.replace('⚠️', '⚠️')
        text = text.replace('❌', '❌')
        text = text.replace('✅', '✅')
        text = text.replace('🎯', '🎯')

        # Make headers bold
        lines = text.split('\n')
        formatted_lines = []

        for line in lines:
            # Bold important headers
            if any(keyword in line for keyword in ['KRİTİK', 'UYARI', 'BİLGİ', 'ESKALASYON']):
                line = f"*{line}*"
            # Make zone, time, etc. bold
            elif ':' in line and any(keyword in line for keyword in ['Bölge', 'Zaman', 'Eksik KKD', 'Çalışan']):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    line = f"*{parts[0]}:*{parts[1]}"

            formatted_lines.append(line)

        return '\n'.join(formatted_lines)

    def _create_inline_keyboard(self, alert) -> Optional[dict]:
        """Create inline keyboard with action buttons."""
        buttons = []

        # Dashboard button
        buttons.append([{
            "text": "📊 Dashboard'u Aç",
            "url": "http://localhost:8080/dashboard"
        }])

        # View image button (if available)
        if alert.image_url:
            buttons.append([{
                "text": "🖼️ Görüntüyü Aç",
                "url": alert.image_url
            }])

        # Acknowledge button (callback)
        buttons.append([{
            "text": "✅ Onaylıyorum",
            "callback_data": f"ack_{alert.alert_id}"
        }])

        return {"inline_keyboard": buttons} if buttons else None

    def send_location(self, chat_id: str, latitude: float, longitude: float, title: str) -> bool:
        """Send location (useful for marking violation zones on map)."""
        try:
            url = f"{self.base_url}/sendLocation"
            payload = {
                "chat_id": chat_id,
                "latitude": latitude,
                "longitude": longitude,
                "title": title
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            self.logger.info(f"Location sent to chat {chat_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send location: {e}")
            return False

    def send_document(self, chat_id: str, document_url: str, caption: str = "") -> bool:
        """Send document (e.g., PDF report)."""
        try:
            url = f"{self.base_url}/sendDocument"
            payload = {
                "chat_id": chat_id,
                "document": document_url,
                "caption": caption
            }

            response = requests.post(url, json=payload, timeout=20)
            response.raise_for_status()

            self.logger.info(f"Document sent to chat {chat_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send document: {e}")
            return False

    def send_summary_report(self, chat_ids: List[str], report: str) -> bool:
        """Send summary report to multiple chats."""
        try:
            success_count = 0

            for chat_id in chat_ids:
                # Split long reports if needed
                if len(report) > 4000:
                    # Split into chunks
                    chunks = [report[i:i+4000] for i in range(0, len(report), 4000)]
                    for i, chunk in enumerate(chunks):
                        header = f"📊 *Rapor (Bölüm {i+1}/{len(chunks)})*\n\n" if len(chunks) > 1 else ""
                        if self._send_text(chat_id, header + chunk, None):
                            success_count += 1
                else:
                    if self._send_text(chat_id, report, None):
                        success_count += 1

            return success_count > 0

        except Exception as e:
            self.logger.error(f"Error sending summary report: {e}")
            return False

    def get_updates(self, offset: Optional[int] = None) -> List[dict]:
        """Get updates from Telegram (for handling callbacks and commands)."""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {"timeout": 30}
            if offset:
                params["offset"] = offset

            response = requests.get(url, params=params, timeout=35)
            response.raise_for_status()

            data = response.json()
            return data.get("result", [])

        except Exception as e:
            self.logger.error(f"Error getting updates: {e}")
            return []

    def answer_callback_query(self, callback_query_id: str, text: str) -> bool:
        """Answer callback query (from inline keyboard buttons)."""
        try:
            url = f"{self.base_url}/answerCallbackQuery"
            payload = {
                "callback_query_id": callback_query_id,
                "text": text,
                "show_alert": False
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return True

        except Exception as e:
            self.logger.error(f"Error answering callback: {e}")
            return False

    def test_connection(self) -> bool:
        """Test bot connection and configuration."""
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get("ok"):
                bot_info = data.get("result", {})
                self.logger.info(f"Telegram bot connected: {bot_info.get('username')}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Telegram connection test failed: {e}")
            return False

    def set_webhook(self, webhook_url: str) -> bool:
        """Set webhook for receiving updates."""
        try:
            url = f"{self.base_url}/setWebhook"
            payload = {
                "url": webhook_url,
                "allowed_updates": ["message", "callback_query"]
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            self.logger.info(f"Webhook set to: {webhook_url}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to set webhook: {e}")
            return False

    def delete_webhook(self) -> bool:
        """Delete webhook (switch to polling mode)."""
        try:
            url = f"{self.base_url}/deleteWebhook"
            response = requests.post(url, timeout=10)
            response.raise_for_status()

            self.logger.info("Webhook deleted")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete webhook: {e}")
            return False
