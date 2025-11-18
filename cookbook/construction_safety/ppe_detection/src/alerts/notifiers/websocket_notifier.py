"""
WebSocket notifier for real-time dashboard updates.
Pushes alerts to connected web clients in real-time.
"""

import logging
import json
import asyncio
from typing import List, Set, Optional
from datetime import datetime
import threading

from ..alert_config import AlertConfig, RecipientGroup
from ..alert_templates import AlertTemplates, TemplateType


class WebSocketNotifier:
    """Send real-time alerts via WebSocket to connected dashboards."""

    def __init__(self, config: AlertConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Connected clients
        self.connected_clients: Set = set()
        self.client_subscriptions: dict = {}  # client_id -> list of zones

        # Message queue for async processing
        self.message_queue: asyncio.Queue = None
        self.is_running = False

        # Threading for async operations
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.thread: Optional[threading.Thread] = None

    def send(
        self,
        alert,
        recipients: List[RecipientGroup],
        template_type: TemplateType = TemplateType.MANAGER
    ) -> bool:
        """
        Send alert via WebSocket.

        Args:
            alert: Alert object
            recipients: List of recipient groups (not used for WebSocket)
            template_type: Template type to use

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            if not self.connected_clients:
                self.logger.debug("No WebSocket clients connected")
                return True  # Not an error, just no clients

            # Prepare payload
            payload = self._create_websocket_payload(alert, template_type)

            # Send to all connected clients or filtered by zone subscriptions
            self._broadcast_message(payload, alert.zone)

            return True

        except Exception as e:
            self.logger.error(f"Error sending WebSocket alert: {e}")
            return False

    def _create_websocket_payload(self, alert, template_type: TemplateType) -> dict:
        """Create WebSocket message payload."""

        # Get formatted message
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

        payload = {
            'type': 'alert',
            'event': 'ppe_violation',
            'data': {
                'alert_id': alert.alert_id,
                'timestamp': alert.timestamp.isoformat(),
                'priority': alert.priority.value,
                'zone': alert.zone,
                'camera_id': alert.camera_id,
                'missing_ppe': alert.missing_ppe,
                'worker_id': alert.worker_id,
                'image_url': alert.image_url,
                'violation_count': alert.violation_count,
                'compliance_rate': alert.compliance_rate,
                'message': message,
                'acknowledged': alert.acknowledged
            },
            'metadata': {
                'sent_at': datetime.now().isoformat(),
                'server': 'ppe-detection-system'
            }
        }

        return payload

    def _broadcast_message(self, payload: dict, zone: Optional[str] = None):
        """Broadcast message to connected clients."""
        try:
            # Filter clients by zone subscription if applicable
            target_clients = self._get_target_clients(zone)

            if not target_clients:
                self.logger.debug("No target clients for broadcast")
                return

            # Convert payload to JSON
            message = json.dumps(payload)

            # Send to each client
            for client in target_clients:
                try:
                    self._send_to_client(client, message)
                except Exception as e:
                    self.logger.error(f"Error sending to client: {e}")
                    # Remove disconnected client
                    self.connected_clients.discard(client)

        except Exception as e:
            self.logger.error(f"Error broadcasting message: {e}")

    def _get_target_clients(self, zone: Optional[str] = None) -> Set:
        """Get clients that should receive the message."""
        if zone is None:
            # Send to all clients
            return self.connected_clients.copy()

        # Filter by zone subscription
        target_clients = set()
        for client in self.connected_clients:
            client_id = id(client)
            subscriptions = self.client_subscriptions.get(client_id, [])

            # Send if subscribed to zone or subscribed to all zones
            if not subscriptions or zone in subscriptions or '*' in subscriptions:
                target_clients.add(client)

        return target_clients

    def _send_to_client(self, client, message: str):
        """Send message to a specific client."""
        # This would use the actual WebSocket library (websockets, socket.io, etc.)
        # Implementation depends on the WebSocket framework being used

        # Placeholder for actual WebSocket send
        # In a real implementation, this would be something like:
        # await client.send(message)
        # or
        # client.emit('alert', message)

        self.logger.debug(f"Message sent to client: {message[:100]}...")

    def add_client(self, client, subscriptions: Optional[List[str]] = None):
        """Add a new WebSocket client connection."""
        self.connected_clients.add(client)

        if subscriptions:
            client_id = id(client)
            self.client_subscriptions[client_id] = subscriptions

        self.logger.info(f"Client connected. Total clients: {len(self.connected_clients)}")

        # Send welcome message
        self._send_welcome_message(client)

    def remove_client(self, client):
        """Remove a WebSocket client connection."""
        self.connected_clients.discard(client)

        client_id = id(client)
        if client_id in self.client_subscriptions:
            del self.client_subscriptions[client_id]

        self.logger.info(f"Client disconnected. Total clients: {len(self.connected_clients)}")

    def _send_welcome_message(self, client):
        """Send welcome message to newly connected client."""
        welcome_payload = {
            'type': 'system',
            'event': 'connected',
            'data': {
                'message': 'KKD Tespit Sistemi\'ne bağlandınız',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            }
        }

        try:
            message = json.dumps(welcome_payload)
            self._send_to_client(client, message)
        except Exception as e:
            self.logger.error(f"Error sending welcome message: {e}")

    def broadcast_system_message(self, message: str, message_type: str = "info"):
        """Broadcast system message to all clients."""
        payload = {
            'type': 'system',
            'event': 'notification',
            'data': {
                'message': message,
                'type': message_type,
                'timestamp': datetime.now().isoformat()
            }
        }

        self._broadcast_message(payload)

    def broadcast_statistics_update(self, statistics: dict):
        """Broadcast statistics update to dashboard."""
        payload = {
            'type': 'statistics',
            'event': 'update',
            'data': statistics,
            'timestamp': datetime.now().isoformat()
        }

        self._broadcast_message(payload)

    def broadcast_alert_acknowledged(self, alert_id: str, acknowledged_by: str):
        """Broadcast alert acknowledgment to all clients."""
        payload = {
            'type': 'alert',
            'event': 'acknowledged',
            'data': {
                'alert_id': alert_id,
                'acknowledged_by': acknowledged_by,
                'timestamp': datetime.now().isoformat()
            }
        }

        self._broadcast_message(payload)

    def get_connection_stats(self) -> dict:
        """Get WebSocket connection statistics."""
        return {
            'connected_clients': len(self.connected_clients),
            'subscriptions': {
                str(client_id): zones
                for client_id, zones in self.client_subscriptions.items()
            }
        }


# Socket.IO implementation (alternative)

class SocketIONotifier:
    """Alternative implementation using Socket.IO."""

    def __init__(self, config: AlertConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.sio = None  # socketio.AsyncServer instance

    def initialize(self, sio):
        """Initialize with Socket.IO server instance."""
        self.sio = sio
        self._setup_event_handlers()

    def _setup_event_handlers(self):
        """Setup Socket.IO event handlers."""
        if not self.sio:
            return

        @self.sio.event
        async def connect(sid, environ):
            self.logger.info(f"Client connected: {sid}")

        @self.sio.event
        async def disconnect(sid):
            self.logger.info(f"Client disconnected: {sid}")

        @self.sio.event
        async def subscribe_zone(sid, data):
            """Handle zone subscription."""
            zone = data.get('zone')
            await self.sio.enter_room(sid, f"zone:{zone}")
            self.logger.info(f"Client {sid} subscribed to zone: {zone}")

        @self.sio.event
        async def unsubscribe_zone(sid, data):
            """Handle zone unsubscription."""
            zone = data.get('zone')
            await self.sio.leave_room(sid, f"zone:{zone}")
            self.logger.info(f"Client {sid} unsubscribed from zone: {zone}")

        @self.sio.event
        async def acknowledge_alert(sid, data):
            """Handle alert acknowledgment from client."""
            alert_id = data.get('alert_id')
            user = data.get('user', 'Unknown')
            self.logger.info(f"Alert {alert_id} acknowledged by {user} (client: {sid})")

            # Broadcast acknowledgment
            await self.sio.emit('alert_acknowledged', {
                'alert_id': alert_id,
                'acknowledged_by': user,
                'timestamp': datetime.now().isoformat()
            })

    async def send_alert(self, alert, template_type: TemplateType = TemplateType.MANAGER):
        """Send alert via Socket.IO."""
        if not self.sio:
            self.logger.warning("Socket.IO not initialized")
            return False

        try:
            payload = {
                'alert_id': alert.alert_id,
                'timestamp': alert.timestamp.isoformat(),
                'priority': alert.priority.value,
                'zone': alert.zone,
                'camera_id': alert.camera_id,
                'missing_ppe': alert.missing_ppe,
                'worker_id': alert.worker_id,
                'image_url': alert.image_url,
                'violation_count': alert.violation_count,
                'compliance_rate': alert.compliance_rate
            }

            # Emit to all clients
            await self.sio.emit('new_alert', payload)

            # Emit to zone-specific room
            await self.sio.emit('new_alert', payload, room=f"zone:{alert.zone}")

            self.logger.info(f"Alert {alert.alert_id} sent via Socket.IO")
            return True

        except Exception as e:
            self.logger.error(f"Error sending Socket.IO alert: {e}")
            return False

    async def broadcast_statistics(self, statistics: dict):
        """Broadcast statistics update."""
        if self.sio:
            await self.sio.emit('statistics_update', statistics)


# Example integration with aiohttp

"""
Example usage with aiohttp and socketio:

from aiohttp import web
import socketio

# Create Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

# Initialize notifier
notifier = SocketIONotifier(config)
notifier.initialize(sio)

# In your alert manager:
async def send_websocket_alert(alert):
    await notifier.send_alert(alert)

# Run server
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=8080)
"""
