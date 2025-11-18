"""
SMS notifier using Twilio API.
Sends urgent alerts via SMS for critical situations.
"""

import logging
import requests
from typing import List, Optional
from base64 import b64encode
from datetime import datetime

from ..alert_config import AlertConfig, RecipientGroup
from ..alert_templates import AlertTemplates, TemplateType


class SMSNotifier:
    """Send alerts via SMS using Twilio."""

    def __init__(self, config: AlertConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{config.twilio_account_sid}"

    def send(
        self,
        alert,
        recipients: List[RecipientGroup],
        template_type: TemplateType = TemplateType.SUPERVISOR
    ) -> bool:
        """
        Send alert via SMS.

        Args:
            alert: Alert object
            recipients: List of recipient groups
            template_type: Template type (SMS uses short format)

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            if not self._validate_config():
                return False

            # Collect all phone numbers
            phone_numbers = []
            for group in recipients:
                phone_numbers.extend(group.phone_numbers)

            if not phone_numbers:
                self.logger.warning("No phone numbers configured")
                return False

            # Generate short SMS message
            message = AlertTemplates.format_sms_alert(
                alert.zone,
                alert.missing_ppe,
                alert.priority.value
            )

            success_count = 0
            for phone_number in phone_numbers:
                if self._send_sms(phone_number, message):
                    success_count += 1

            return success_count > 0

        except Exception as e:
            self.logger.error(f"Error sending SMS alert: {e}")
            return False

    def _validate_config(self) -> bool:
        """Validate Twilio configuration."""
        if not self.config.twilio_account_sid:
            self.logger.warning("Twilio account SID not configured")
            return False

        if not self.config.twilio_auth_token:
            self.logger.warning("Twilio auth token not configured")
            return False

        if not self.config.twilio_from_number:
            self.logger.warning("Twilio from number not configured")
            return False

        return True

    def _send_sms(self, to_number: str, message: str) -> bool:
        """Send SMS to a specific number."""
        try:
            # Format phone number (ensure it starts with +)
            if not to_number.startswith('+'):
                to_number = '+' + to_number

            # Prepare authentication
            auth_string = f"{self.config.twilio_account_sid}:{self.config.twilio_auth_token}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = b64encode(auth_bytes).decode('ascii')

            # API endpoint
            url = f"{self.base_url}/Messages.json"

            # Payload
            data = {
                'From': self.config.twilio_from_number,
                'To': to_number,
                'Body': message
            }

            # Headers
            headers = {
                'Authorization': f'Basic {auth_b64}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            # Send request
            response = requests.post(url, data=data, headers=headers, timeout=10)

            if response.status_code == 201:
                response_data = response.json()
                message_sid = response_data.get('sid')
                self.logger.info(f"SMS sent successfully to {to_number} (SID: {message_sid})")
                return True
            else:
                self.logger.error(f"SMS failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Error sending SMS to {to_number}: {e}")
            return False

    def send_bulk_sms(self, phone_numbers: List[str], message: str) -> int:
        """
        Send SMS to multiple numbers.

        Args:
            phone_numbers: List of phone numbers
            message: Message to send

        Returns:
            Number of successfully sent messages
        """
        success_count = 0

        for phone_number in phone_numbers:
            if self._send_sms(phone_number, message):
                success_count += 1

        return success_count

    def send_emergency_alert(
        self,
        phone_numbers: List[str],
        zone: str,
        incident_type: str = "KKD İhlali"
    ) -> bool:
        """Send emergency SMS alert."""
        try:
            message = f"⚠️ ACİL: {zone} - {incident_type}. Derhal bölgeyi kontrol edin! {datetime.now().strftime('%H:%M')}"

            success_count = self.send_bulk_sms(phone_numbers, message)

            return success_count > 0

        except Exception as e:
            self.logger.error(f"Error sending emergency alert: {e}")
            return False

    def get_message_status(self, message_sid: str) -> Optional[dict]:
        """Get status of sent message."""
        try:
            auth_string = f"{self.config.twilio_account_sid}:{self.config.twilio_auth_token}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = b64encode(auth_bytes).decode('ascii')

            url = f"{self.base_url}/Messages/{message_sid}.json"

            headers = {
                'Authorization': f'Basic {auth_b64}'
            }

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return response.json()

            return None

        except Exception as e:
            self.logger.error(f"Error getting message status: {e}")
            return None

    def test_connection(self) -> bool:
        """Test Twilio configuration."""
        try:
            if not self._validate_config():
                return False

            auth_string = f"{self.config.twilio_account_sid}:{self.config.twilio_auth_token}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = b64encode(auth_bytes).decode('ascii')

            url = f"{self.base_url}.json"

            headers = {
                'Authorization': f'Basic {auth_b64}'
            }

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                account_data = response.json()
                self.logger.info(f"Twilio connection successful: {account_data.get('friendly_name')}")
                return True
            else:
                self.logger.error(f"Twilio connection failed: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"Twilio connection test failed: {e}")
            return False


class AlternativeSMSNotifier:
    """
    Alternative SMS implementation using different providers.
    Can be adapted for Turkish SMS providers like Netgsm, iletimerkezi, etc.
    """

    def __init__(self, config: AlertConfig, provider_config: dict):
        """
        Args:
            config: Alert configuration
            provider_config: Provider-specific configuration
                {
                    'api_url': 'https://api.provider.com/send',
                    'api_key': 'your-api-key',
                    'sender': 'SENDER_NAME',
                    'header_name': 'HEADER_NAME'
                }
        """
        self.config = config
        self.provider_config = provider_config
        self.logger = logging.getLogger(__name__)

    def send_sms(self, to_number: str, message: str) -> bool:
        """Send SMS using alternative provider."""
        try:
            # Example implementation for Turkish SMS providers
            # This is a generic template - adjust based on actual provider API

            url = self.provider_config.get('api_url')
            api_key = self.provider_config.get('api_key')
            sender = self.provider_config.get('sender', 'SANTIYE')

            # Most Turkish SMS providers use similar formats
            payload = {
                'username': api_key,
                'password': self.provider_config.get('password', ''),
                'header': self.provider_config.get('header_name', sender),
                'message': message,
                'phones': to_number.replace('+90', '')  # Remove country code for Turkish numbers
            }

            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                self.logger.info(f"SMS sent via alternative provider to {to_number}")
                return True
            else:
                self.logger.error(f"SMS failed: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"Error sending SMS: {e}")
            return False


# Example configurations for Turkish SMS providers

def get_netgsm_config() -> dict:
    """Configuration for Netgsm Turkish SMS provider."""
    return {
        'api_url': 'https://api.netgsm.com.tr/sms/send/get',
        'api_key': 'YOUR_API_KEY',
        'sender': 'SANTIYE',
        'header_name': 'SANTIYE'
    }


def get_iletimerkezi_config() -> dict:
    """Configuration for iletimerkezi Turkish SMS provider."""
    return {
        'api_url': 'https://api.iletimerkezi.com/v1/send-sms',
        'api_key': 'YOUR_API_KEY',
        'sender': 'SANTIYE',
        'header_name': 'SANTIYE'
    }


def get_vatansms_config() -> dict:
    """Configuration for Vatansms Turkish SMS provider."""
    return {
        'api_url': 'https://api.vatansms.net/api/v1/1toN',
        'api_key': 'YOUR_API_KEY',
        'sender': 'SANTIYE',
        'header_name': 'SANTIYE'
    }
