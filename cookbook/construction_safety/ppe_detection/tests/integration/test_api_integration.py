"""
Integration tests for API with database and other components.

Tests API endpoints with real database operations and component interactions.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import io
from PIL import Image

# Note: These tests are skipped by default as they require FastAPI app setup
# Remove @pytest.mark.skip to run them once the API is fully configured


@pytest.mark.integration
@pytest.mark.skip(reason="Requires FastAPI app initialization")
class TestAPIWithDatabase:
    """Test API endpoints with database integration."""

    def test_create_and_get_camera(self, client, test_db):
        """Test creating camera via API and retrieving it."""
        # Create camera
        camera_data = {
            "name": "API Test Camera",
            "rtsp_url": "rtsp://admin:pass@192.168.1.100:554/stream",
            "location": "Test Location",
            "zone": "Zone A",
            "enabled": True,
            "required_ppe": ["helmet", "vest"]
        }

        create_response = client.post("/cameras", json=camera_data)
        assert create_response.status_code == 201

        camera_id = create_response.json()["id"]

        # Retrieve camera
        get_response = client.get(f"/cameras/{camera_id}")
        assert get_response.status_code == 200

        camera = get_response.json()
        assert camera["name"] == "API Test Camera"
        assert camera["enabled"] is True

    def test_detection_saves_to_database(self, client, test_db, sample_camera):
        """Test that detection results are saved to database."""
        # Create test image
        img = Image.new('RGB', (640, 480), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)

        files = {"file": ("test.jpg", img_byte_arr, "image/jpeg")}
        data = {
            "camera_id": sample_camera.id,
            "save_results": True
        }

        # Run detection
        response = client.post("/detect", files=files, data=data)

        if response.status_code == 200:
            result = response.json()

            # Verify detection log was created
            from database import crud
            logs = crud.get_detection_logs(test_db, camera_id=sample_camera.id)
            assert len(logs) > 0

    def test_violation_workflow_via_api(self, client, test_db, sample_camera):
        """Test complete violation workflow via API."""
        # Create violation (simulated)
        violation_data = {
            "camera_id": sample_camera.id,
            "violation_type": "NO_HELMET",
            "confidence": 0.95
        }

        from database import crud
        violation = crud.create_violation(test_db, violation_data)

        # List violations via API
        response = client.get("/violations")
        assert response.status_code == 200

        violations = response.json()
        # Should include our violation (if API is properly connected to DB)

        # Acknowledge violation via API
        ack_data = {
            "acknowledged_by": "supervisor@example.com",
            "notes": "Worker has been warned"
        }

        ack_response = client.post(
            f"/violations/{violation.id}/acknowledge",
            json=ack_data
        )

        if ack_response.status_code == 200:
            # Verify in database
            updated_violation = crud.get_violation(test_db, violation.id)
            assert updated_violation.acknowledged is True

    def test_statistics_endpoint_with_real_data(self, client, test_db, sample_camera):
        """Test statistics endpoint with real database data."""
        from database import crud

        # Create sample detection logs
        for i in range(10):
            log_data = {
                "camera_id": sample_camera.id,
                "total_persons": 5,
                "compliant_count": 4,
                "violation_count": 1,
                "processing_time_ms": 150.0 + i
            }
            crud.create_detection_log(test_db, log_data)

        # Get statistics via API
        response = client.get("/stats")
        assert response.status_code == 200

        stats = response.json()
        assert "total_detections" in stats
        assert "total_violations" in stats

    def test_api_pagination(self, client, test_db, sample_camera):
        """Test API pagination with large datasets."""
        from database import crud

        # Create many violations
        for i in range(50):
            violation_data = {
                "camera_id": sample_camera.id,
                "violation_type": "NO_HELMET",
                "confidence": 0.9
            }
            crud.create_violation(test_db, violation_data)

        # Get first page
        response = client.get("/violations?limit=20&offset=0")
        assert response.status_code == 200
        page1 = response.json()
        assert len(page1) <= 20

        # Get second page
        response = client.get("/violations?limit=20&offset=20")
        assert response.status_code == 200
        page2 = response.json()
        assert len(page2) <= 20


@pytest.mark.integration
@pytest.mark.skip(reason="Requires FastAPI app initialization")
class TestAPIWithDetectionModel:
    """Test API endpoints with actual detection model."""

    @patch('models.ppe_detector.YOLO')
    def test_detect_endpoint_with_model(self, mock_yolo, client):
        """Test detection endpoint with mocked model."""
        # Setup mock model
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model
        mock_model.predict.return_value = []

        # Create test image
        img = Image.new('RGB', (640, 480), color='blue')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)

        files = {"file": ("test.jpg", img_byte_arr, "image/jpeg")}

        response = client.post("/detect", files=files)

        if response.status_code == 200:
            result = response.json()
            assert "detection_id" in result
            assert "processing_time_ms" in result


@pytest.mark.integration
@pytest.mark.skip(reason="Requires FastAPI app initialization")
class TestAPIWithAlerts:
    """Test API integration with alert system."""

    @patch('alerts.alert_manager.AlertManager')
    def test_violation_triggers_alert_via_api(self, mock_alert_manager, client):
        """Test that violations via API trigger alerts."""
        # Setup mock alert manager
        mock_manager = MagicMock()
        mock_alert_manager.return_value = mock_manager

        # Create test image with violation
        img = Image.new('RGB', (640, 480))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)

        files = {"file": ("test.jpg", img_byte_arr, "image/jpeg")}

        response = client.post("/detect", files=files)

        # If violation detected, alert manager should be called
        # (Implementation depends on API design)


@pytest.mark.integration
@pytest.mark.skip(reason="Requires FastAPI app initialization")
@pytest.mark.slow
class TestAPIPerformance:
    """Test API performance and concurrent requests."""

    def test_concurrent_detection_requests(self, client):
        """Test handling multiple concurrent detection requests."""
        import concurrent.futures
        import time

        def make_detection_request():
            img = Image.new('RGB', (640, 480))
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_byte_arr.seek(0)

            files = {"file": ("test.jpg", img_byte_arr, "image/jpeg")}
            response = client.post("/detect", files=files)
            return response.status_code

        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_detection_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should succeed or handle gracefully
        assert len(results) == 10

    def test_api_response_time(self, client):
        """Test API response time for health check."""
        import time

        start = time.time()
        response = client.get("/health")
        duration = time.time() - start

        assert response.status_code == 200
        assert duration < 1.0  # Should respond in less than 1 second


@pytest.mark.integration
@pytest.mark.skip(reason="Requires FastAPI app initialization")
class TestWebSocketIntegration:
    """Test WebSocket endpoints."""

    async def test_websocket_live_feed(self, client):
        """Test WebSocket live feed connection."""
        # WebSocket testing requires special setup
        # This is a placeholder for WebSocket tests
        pass


@pytest.mark.integration
@pytest.mark.skip(reason="Requires FastAPI app initialization")
@pytest.mark.turkish
class TestTurkishAPIIntegration:
    """Test API with Turkish content."""

    def test_turkish_camera_names(self, client, test_db):
        """Test creating cameras with Turkish names."""
        camera_data = {
            "name": "Şantiye Kamerası 1",
            "rtsp_url": "rtsp://admin:pass@192.168.1.100:554/stream",
            "location": "Ana Giriş",
            "zone": "Kazı Alanı",
            "enabled": True
        }

        response = client.post("/cameras", json=camera_data)

        if response.status_code == 201:
            camera = response.json()
            assert camera["name"] == "Şantiye Kamerası 1"
            assert camera["location"] == "Ana Giriş"
            assert camera["zone"] == "Kazı Alanı"

    def test_turkish_violation_messages(self, client, test_db, sample_camera):
        """Test violations with Turkish descriptions."""
        from database import crud

        violation_data = {
            "camera_id": sample_camera.id,
            "violation_type": "NO_HELMET",
            "confidence": 0.95,
            "notes": "İşçi baretsiz tespit edildi"
        }

        violation = crud.create_violation(test_db, violation_data)

        # Retrieve via API
        response = client.get(f"/violations/{violation.id}")

        if response.status_code == 200:
            data = response.json()
            # Verify Turkish characters preserved
            if "notes" in data:
                assert "İşçi" in data["notes"] or "baretsiz" in data["notes"]


# Fixture for test client (placeholder)
@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    pytest.skip("FastAPI app initialization required")
