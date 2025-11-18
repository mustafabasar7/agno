"""
Quick Start Guide for Alert System Integration
Demonstrates how to integrate the alert system with your PPE detection pipeline.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
import json

# Import alert system components
from alert_config import get_example_config_small_site
from alert_manager import AlertManager
from alert_rules import AlertRules


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PPEDetectionAlertSystem:
    """
    Wrapper class to integrate alert system with PPE detection.
    Use this as a template for your implementation.
    """

    def __init__(self, config=None):
        """Initialize the alert system."""
        # Load configuration
        if config is None:
            config = get_example_config_small_site()

        self.config = config
        self.rules = AlertRules()
        self.alert_manager = AlertManager(config, self.rules)

        logger.info("Alert system initialized")

    def process_detection_result(self, detection_result: Dict) -> Optional[str]:
        """
        Process a detection result from the PPE detection model.

        Args:
            detection_result: Dictionary containing detection information
                {
                    'zone': str,
                    'camera_id': str,
                    'missing_ppe': List[str],
                    'worker_id': Optional[str],
                    'image_path': Optional[str],
                    'timestamp': datetime,
                    'confidence': float,
                    'detected_objects': List[Dict]
                }

        Returns:
            Alert ID if alert was sent, None otherwise
        """
        try:
            # Extract detection data
            zone = detection_result.get('zone', 'Unknown Zone')
            camera_id = detection_result.get('camera_id', 'Unknown Camera')
            missing_ppe = detection_result.get('missing_ppe', [])
            worker_id = detection_result.get('worker_id')
            image_path = detection_result.get('image_path')
            timestamp = detection_result.get('timestamp', datetime.now())
            confidence = detection_result.get('confidence', 0.0)

            # Skip if no violations detected
            if not missing_ppe:
                logger.debug(f"No PPE violations in {zone}")
                return None

            # Skip low confidence detections
            if confidence < 0.75:
                logger.debug(f"Low confidence detection ({confidence:.2f}), skipping alert")
                return None

            # Convert image path to URL if needed
            image_url = self._convert_image_path_to_url(image_path)

            # Prepare metadata
            metadata = {
                'confidence': confidence,
                'detection_model': detection_result.get('model_version', 'unknown'),
                'detected_objects': detection_result.get('detected_objects', [])
            }

            # Process violation through alert manager
            alert = self.alert_manager.process_violation(
                zone=zone,
                camera_id=camera_id,
                missing_ppe=missing_ppe,
                worker_id=worker_id,
                image_url=image_url,
                timestamp=timestamp,
                metadata=metadata
            )

            if alert:
                logger.info(f"Alert sent: {alert.alert_id} for zone {zone}")
                return alert.alert_id
            else:
                logger.debug(f"Alert filtered for zone {zone}")
                return None

        except Exception as e:
            logger.error(f"Error processing detection result: {e}", exc_info=True)
            return None

    def _convert_image_path_to_url(self, image_path: Optional[str]) -> Optional[str]:
        """
        Convert local image path to accessible URL.
        Modify this based on your image storage setup.
        """
        if not image_path:
            return None

        # Example: If images are served from a web server
        # base_url = "http://your-server.com/violation-images/"
        # return base_url + os.path.basename(image_path)

        # For now, return the path as-is
        return image_path

    def acknowledge_alert(self, alert_id: str, user: str) -> bool:
        """Acknowledge an alert."""
        return self.alert_manager.acknowledge_alert(alert_id, user)

    def get_active_alerts(self, zone: Optional[str] = None) -> List:
        """Get active (unacknowledged) alerts."""
        return self.alert_manager.get_active_alerts(zone)

    def get_statistics(self, hours: int = 24) -> Dict:
        """Get alert statistics for the last N hours."""
        from datetime import timedelta
        start_time = datetime.now() - timedelta(hours=hours)
        return self.alert_manager.get_alert_statistics(start_time)

    def generate_daily_report(self) -> str:
        """Generate daily summary report."""
        from datetime import timedelta
        start_time = datetime.now() - timedelta(days=1)
        return self.alert_manager.generate_summary_report(start_time)

    def check_escalations(self):
        """Check and process pending escalations."""
        return self.alert_manager.check_escalations()


# ========================================
# EXAMPLE USAGE SCENARIOS
# ========================================

def scenario_1_basic_integration():
    """
    Scenario 1: Basic integration with detection pipeline.
    """
    logger.info("=== Scenario 1: Basic Integration ===")

    # Initialize alert system
    alert_system = PPEDetectionAlertSystem()

    # Simulate detection results
    detection_results = [
        {
            'zone': 'İnşaat Alanı - Kat 3',
            'camera_id': 'CAM_301',
            'missing_ppe': ['helmet'],
            'worker_id': 'W12345',
            'image_path': '/data/violations/2025-01-18/violation_001.jpg',
            'timestamp': datetime.now(),
            'confidence': 0.95,
            'detected_objects': [
                {'class': 'person', 'confidence': 0.98},
                {'class': 'no_helmet', 'confidence': 0.95}
            ]
        },
        {
            'zone': 'Yüksekte Çalışma Alanı',
            'camera_id': 'CAM_401',
            'missing_ppe': ['helmet', 'harness'],
            'worker_id': 'W67890',
            'image_path': '/data/violations/2025-01-18/violation_002.jpg',
            'timestamp': datetime.now(),
            'confidence': 0.92
        }
    ]

    # Process each detection
    for result in detection_results:
        alert_id = alert_system.process_detection_result(result)
        if alert_id:
            logger.info(f"Processed: Alert {alert_id} for {result['zone']}")


def scenario_2_real_time_processing():
    """
    Scenario 2: Real-time processing with video stream.
    """
    logger.info("\n=== Scenario 2: Real-time Processing ===")

    alert_system = PPEDetectionAlertSystem()

    # Simulate real-time detection callback
    def on_detection_callback(frame_data: Dict):
        """
        This function would be called by your video processing pipeline
        whenever a violation is detected in a video frame.
        """
        alert_id = alert_system.process_detection_result(frame_data)
        if alert_id:
            logger.info(f"Real-time alert: {alert_id}")

    # Example frame data
    frame_data = {
        'zone': 'Vinç Bölgesi',
        'camera_id': 'CAM_VINC_01',
        'missing_ppe': ['vest'],
        'timestamp': datetime.now(),
        'confidence': 0.89,
        'image_path': '/tmp/frame_12345.jpg'
    }

    on_detection_callback(frame_data)


def scenario_3_batch_processing():
    """
    Scenario 3: Batch processing of stored images.
    """
    logger.info("\n=== Scenario 3: Batch Processing ===")

    alert_system = PPEDetectionAlertSystem()

    # Simulate batch of detections from image processing
    batch_results = []
    zones = ['Kazı Alanı', 'Beton Dökme', 'Demir Bağlama']

    for i in range(10):
        batch_results.append({
            'zone': zones[i % 3],
            'camera_id': f'CAM_{i % 3 + 1:02d}',
            'missing_ppe': ['helmet'] if i % 2 == 0 else ['vest'],
            'worker_id': f'W{1000 + i}',
            'timestamp': datetime.now(),
            'confidence': 0.85 + (i % 10) / 100
        })

    # Process batch
    alert_count = 0
    for result in batch_results:
        if alert_system.process_detection_result(result):
            alert_count += 1

    logger.info(f"Batch processing complete: {alert_count} alerts sent from {len(batch_results)} detections")


def scenario_4_monitoring_and_reporting():
    """
    Scenario 4: Monitoring and reporting workflow.
    """
    logger.info("\n=== Scenario 4: Monitoring and Reporting ===")

    alert_system = PPEDetectionAlertSystem()

    # Simulate some violations
    for i in range(5):
        alert_system.process_detection_result({
            'zone': 'Test Zone',
            'camera_id': 'CAM_TEST',
            'missing_ppe': ['helmet'],
            'timestamp': datetime.now(),
            'confidence': 0.9
        })

    # Get active alerts
    active_alerts = alert_system.get_active_alerts()
    logger.info(f"Active alerts: {len(active_alerts)}")

    # Get statistics
    stats = alert_system.get_statistics(hours=24)
    logger.info(f"Statistics (24h): {stats['total_alerts']} total alerts")

    # Check escalations
    escalated = alert_system.check_escalations()
    if escalated:
        logger.info(f"Escalated alerts: {escalated}")


def scenario_5_dashboard_integration():
    """
    Scenario 5: Integration with web dashboard.
    """
    logger.info("\n=== Scenario 5: Dashboard Integration ===")

    alert_system = PPEDetectionAlertSystem()

    # API endpoint examples for your web application

    def api_get_active_alerts(zone: Optional[str] = None) -> List[Dict]:
        """API: Get active alerts (for dashboard display)."""
        alerts = alert_system.get_active_alerts(zone)
        return [alert.to_dict() for alert in alerts]

    def api_acknowledge_alert(alert_id: str, user: str) -> Dict:
        """API: Acknowledge an alert (from dashboard action)."""
        success = alert_system.acknowledge_alert(alert_id, user)
        return {'success': success, 'alert_id': alert_id}

    def api_get_statistics(hours: int = 24) -> Dict:
        """API: Get statistics (for dashboard charts)."""
        return alert_system.get_statistics(hours)

    def api_get_daily_report() -> Dict:
        """API: Get daily report (for dashboard summary)."""
        report = alert_system.generate_daily_report()
        return {'report': report, 'generated_at': datetime.now().isoformat()}

    # Simulate API calls
    logger.info("Simulating dashboard API calls...")

    alerts = api_get_active_alerts()
    logger.info(f"Dashboard: Retrieved {len(alerts)} active alerts")

    stats = api_get_statistics()
    logger.info(f"Dashboard: Statistics retrieved")

    # report = api_get_daily_report()
    # logger.info(f"Dashboard: Daily report generated")


def scenario_6_scheduled_tasks():
    """
    Scenario 6: Scheduled tasks (cron jobs, celery tasks, etc.).
    """
    logger.info("\n=== Scenario 6: Scheduled Tasks ===")

    alert_system = PPEDetectionAlertSystem()

    # Task 1: Check escalations (run every minute)
    def task_check_escalations():
        """Check for alerts that need escalation."""
        escalated = alert_system.check_escalations()
        if escalated:
            logger.info(f"Escalation task: {len(escalated)} alerts escalated")

    # Task 2: Send daily report (run at 18:00 daily)
    def task_send_daily_report():
        """Generate and send daily report."""
        report = alert_system.generate_daily_report()
        logger.info("Daily report task: Report generated and sent")
        # Here you would send the report via email or other channel

    # Task 3: Cleanup old alerts (run daily at midnight)
    def task_cleanup_old_alerts():
        """Clean up old acknowledged alerts."""
        # Implement cleanup logic
        logger.info("Cleanup task: Old alerts archived")

    # Simulate running tasks
    logger.info("Running scheduled tasks...")
    task_check_escalations()
    # task_send_daily_report()


# ========================================
# MAIN EXECUTION
# ========================================

def main():
    """Run all scenarios."""
    scenarios = [
        scenario_1_basic_integration,
        scenario_2_real_time_processing,
        scenario_3_batch_processing,
        scenario_4_monitoring_and_reporting,
        scenario_5_dashboard_integration,
        scenario_6_scheduled_tasks,
    ]

    logger.info("=" * 70)
    logger.info("PPE Detection Alert System - Quick Start Guide")
    logger.info("=" * 70)

    for scenario in scenarios:
        try:
            scenario()
            logger.info("\n" + "=" * 70 + "\n")
        except Exception as e:
            logger.error(f"Error in scenario: {e}", exc_info=True)

    logger.info("Quick start guide completed!")
    logger.info("\nNext steps:")
    logger.info("1. Configure your credentials in config_example.py")
    logger.info("2. Integrate with your PPE detection model")
    logger.info("3. Set up scheduled tasks for escalation checks")
    logger.info("4. Configure your preferred notification channels")
    logger.info("5. Test with real violations before going to production")


if __name__ == "__main__":
    main()
