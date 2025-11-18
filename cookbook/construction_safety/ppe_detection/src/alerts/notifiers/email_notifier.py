"""
Email notifier using SMTP.
Sends professional email alerts to configured recipients.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from typing import List, Optional
import requests
from datetime import datetime

from ..alert_config import AlertConfig, RecipientGroup
from ..alert_templates import AlertTemplates, TemplateType


class EmailNotifier:
    """Send alerts via email using SMTP."""

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
        Send alert via email.

        Args:
            alert: Alert object
            recipients: List of recipient groups
            template_type: Template type to use

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Collect all email addresses
            email_addresses = []
            for group in recipients:
                email_addresses.extend(group.email_addresses)

            if not email_addresses:
                self.logger.warning("No email recipients configured")
                return False

            # Generate message
            subject = AlertTemplates.format_email_subject(
                alert.priority.value,
                alert.zone,
                "KKD İhlali"
            )

            body = AlertTemplates.format_violation_alert(
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

            # Create message
            msg = MIMEMultipart('related')
            msg['From'] = self.config.email_from
            msg['To'] = ', '.join(email_addresses)
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')

            # Add HTML body
            html_body = self._create_html_email(alert, body, template_type)
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))

            # Attach image if available
            if alert.image_url:
                try:
                    image_data = self._download_image(alert.image_url)
                    if image_data:
                        image = MIMEImage(image_data)
                        image.add_header('Content-ID', '<violation_image>')
                        msg.attach(image)
                except Exception as e:
                    self.logger.warning(f"Failed to attach image: {e}")

            # Send email
            return self._send_smtp(msg, email_addresses)

        except Exception as e:
            self.logger.error(f"Error sending email alert: {e}")
            return False

    def _create_html_email(self, alert, body: str, template_type: TemplateType) -> str:
        """Create HTML formatted email."""

        # Priority color
        priority_colors = {
            'critical': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8'
        }
        color = priority_colors.get(alert.priority.value, '#6c757d')

        # Convert text body to HTML
        body_html = body.replace('\n', '<br>')

        html = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KKD İhlali Bildirimi</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px;">
    <div style="background-color: {color}; color: white; padding: 20px; border-radius: 5px 5px 0 0;">
        <h1 style="margin: 0; font-size: 24px;">KKD İhlali Bildirimi</h1>
        <p style="margin: 5px 0 0 0; font-size: 14px;">Şantiye Güvenlik Sistemi</p>
    </div>

    <div style="background-color: #f8f9fa; padding: 20px; border: 1px solid #dee2e6;">
        <div style="background-color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
            <pre style="font-family: 'Courier New', monospace; font-size: 13px; white-space: pre-wrap; word-wrap: break-word;">
{body_html}
            </pre>
        </div>

        <div style="background-color: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
            <p style="margin: 0; font-size: 14px;"><strong>⚠️ Önemli Hatırlatma:</strong></p>
            <p style="margin: 5px 0 0 0; font-size: 13px;">
                Lütfen bu bildirimi aldığınızda derhal gerekli aksiyonları alın.
                Alert ID: <strong>{alert.alert_id}</strong>
            </p>
        </div>
"""

        # Add image if available
        if alert.image_url:
            html += f"""
        <div style="background-color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; text-align: center;">
            <p style="margin: 0 0 10px 0; font-weight: bold;">İhlal Görseli:</p>
            <img src="cid:violation_image" alt="İhlal Fotoğrafı" style="max-width: 100%; height: auto; border: 2px solid #dee2e6; border-radius: 5px;">
            <p style="margin: 10px 0 0 0; font-size: 12px; color: #6c757d;">
                <a href="{alert.image_url}" style="color: #007bff; text-decoration: none;">Tam boyutta görüntüle</a>
            </p>
        </div>
"""

        html += f"""
        <div style="background-color: white; padding: 15px; border-radius: 5px;">
            <table style="width: 100%; font-size: 13px;">
                <tr>
                    <td style="padding: 5px;"><strong>Alert ID:</strong></td>
                    <td style="padding: 5px;">{alert.alert_id}</td>
                </tr>
                <tr>
                    <td style="padding: 5px;"><strong>Öncelik:</strong></td>
                    <td style="padding: 5px;">
                        <span style="background-color: {color}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px;">
                            {alert.priority.value.upper()}
                        </span>
                    </td>
                </tr>
                <tr>
                    <td style="padding: 5px;"><strong>Bölge:</strong></td>
                    <td style="padding: 5px;">{alert.zone}</td>
                </tr>
                <tr>
                    <td style="padding: 5px;"><strong>Kamera:</strong></td>
                    <td style="padding: 5px;">{alert.camera_id}</td>
                </tr>
                <tr>
                    <td style="padding: 5px;"><strong>Zaman:</strong></td>
                    <td style="padding: 5px;">{alert.timestamp.strftime('%d.%m.%Y %H:%M:%S')}</td>
                </tr>
            </table>
        </div>
    </div>

    <div style="background-color: #343a40; color: white; padding: 15px; border-radius: 0 0 5px 5px; font-size: 12px; text-align: center;">
        <p style="margin: 0;">Bu mesaj PPE Tespit Sistemi tarafından otomatik olarak gönderilmiştir.</p>
        <p style="margin: 5px 0 0 0;">
            Dashboard: <a href="http://localhost:8080/dashboard" style="color: #17a2b8;">localhost:8080/dashboard</a>
        </p>
    </div>
</body>
</html>
"""
        return html

    def _download_image(self, url: str, timeout: int = 10) -> Optional[bytes]:
        """Download image from URL."""
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.content
        except Exception as e:
            self.logger.error(f"Error downloading image: {e}")
            return None

    def _send_smtp(self, msg: MIMEMultipart, recipients: List[str]) -> bool:
        """Send email via SMTP."""
        try:
            # Connect to SMTP server
            if self.config.smtp_use_tls:
                server = smtplib.SMTP(self.config.smtp_host, self.config.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.config.smtp_host, self.config.smtp_port)

            # Login if credentials provided
            if self.config.smtp_username and self.config.smtp_password:
                server.login(self.config.smtp_username, self.config.smtp_password)

            # Send email
            server.send_message(msg)
            server.quit()

            self.logger.info(f"Email sent successfully to {len(recipients)} recipients")
            return True

        except Exception as e:
            self.logger.error(f"SMTP error: {e}")
            return False

    def send_summary_report(
        self,
        subject: str,
        body: str,
        recipients: List[str]
    ) -> bool:
        """Send summary report email."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.email_from
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')

            # Create HTML version
            html_body = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>{subject}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #007bff; color: white; padding: 20px; border-radius: 5px 5px 0 0;">
        <h1 style="margin: 0;">{subject}</h1>
    </div>
    <div style="background-color: #f8f9fa; padding: 20px; border: 1px solid #dee2e6; border-radius: 0 0 5px 5px;">
        <pre style="font-family: 'Courier New', monospace; white-space: pre-wrap; word-wrap: break-word;">
{body}
        </pre>
    </div>
    <div style="margin-top: 20px; padding: 15px; background-color: #e9ecef; border-radius: 5px; font-size: 12px; text-align: center;">
        <p style="margin: 0;">Bu rapor otomatik olarak oluşturulmuştur.</p>
    </div>
</body>
</html>
"""
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))

            return self._send_smtp(msg, recipients)

        except Exception as e:
            self.logger.error(f"Error sending summary report: {e}")
            return False
