"""
Simple API test script to verify the API is working correctly.

Run this script to test basic API functionality:
    python src/api/test_api_simple.py
"""

import asyncio
import sys
from pathlib import Path

import httpx


BASE_URL = "http://localhost:8000"


async def test_ping():
    """Test ping endpoint."""
    print("Testing /ping endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/ping")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print("✓ Ping test passed")
        return True


async def test_version():
    """Test version endpoint."""
    print("\nTesting /version endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/version")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        print(f"✓ Version test passed (v{data['version']})")
        return True


async def test_health():
    """Test health endpoint."""
    print("\nTesting /api/health endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "uptime_seconds" in data
        print(f"✓ Health check passed (status: {data['status']})")
        print(f"  - Database connected: {data['database_connected']}")
        print(f"  - Model loaded: {data['model_loaded']}")
        print(f"  - Active cameras: {data['active_cameras']}")
        print(f"  - Uptime: {data['uptime_seconds']:.2f}s")
        return True


async def test_list_cameras():
    """Test list cameras endpoint."""
    print("\nTesting /api/cameras endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/cameras")
        assert response.status_code == 200
        cameras = response.json()
        print(f"✓ List cameras passed ({len(cameras)} cameras found)")
        return True


async def test_create_camera():
    """Test create camera endpoint."""
    print("\nTesting POST /api/cameras endpoint...")
    camera_data = {
        "name": "Test Camera",
        "rtsp_url": "rtsp://192.168.1.100:554/stream",
        "location": "Test Location",
        "zone": "Test Zone",
        "enabled": True,
        "detection_interval": 5,
        "confidence_threshold": 0.7,
        "required_ppe": ["helmet", "vest"]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/cameras",
            json=camera_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == camera_data["name"]
        assert data["location"] == camera_data["location"]
        print(f"✓ Create camera passed (ID: {data['id']})")
        return True


async def test_get_stats():
    """Test statistics endpoint."""
    print("\nTesting /api/stats endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/stats")
        assert response.status_code == 200
        stats = response.json()
        assert "total_cameras" in stats
        assert "total_detections" in stats
        assert "overall_compliance_rate" in stats
        print(f"✓ Statistics test passed")
        print(f"  - Total cameras: {stats['total_cameras']}")
        print(f"  - Active cameras: {stats['active_cameras']}")
        print(f"  - Total detections: {stats['total_detections']}")
        print(f"  - Compliance rate: {stats['overall_compliance_rate']:.1f}%")
        return True


async def test_get_violations():
    """Test violations endpoint."""
    print("\nTesting /api/violations endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/violations")
        assert response.status_code == 200
        violations = response.json()
        print(f"✓ List violations passed ({len(violations)} violations found)")
        return True


async def test_recent_violations():
    """Test recent violations endpoint."""
    print("\nTesting /api/violations/recent endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/violations/recent")
        assert response.status_code == 200
        violations = response.json()
        print(f"✓ Recent violations passed ({len(violations)} violations in last 24h)")
        return True


async def test_root():
    """Test root endpoint."""
    print("\nTesting / endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        print(f"✓ Root endpoint passed")
        print(f"  - API Name: {data['name']}")
        print(f"  - Version: {data['version']}")
        return True


async def main():
    """Run all tests."""
    print("=" * 70)
    print("PPE Detection API - Simple Test Suite")
    print("=" * 70)
    print(f"\nBase URL: {BASE_URL}")
    print("\nMake sure the API server is running before running these tests.")
    print("Start the server with: python run_api.py --reload")
    print("=" * 70)

    tests = [
        ("Ping", test_ping),
        ("Version", test_version),
        ("Health", test_health),
        ("Root", test_root),
        ("List Cameras", test_list_cameras),
        ("Create Camera", test_create_camera),
        ("Statistics", test_get_stats),
        ("List Violations", test_get_violations),
        ("Recent Violations", test_recent_violations),
    ]

    passed = 0
    failed = 0
    errors = []

    for test_name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            failed += 1
            errors.append((test_name, str(e)))
            print(f"✗ {test_name} test failed: {e}")

    print("\n" + "=" * 70)
    print("Test Results")
    print("=" * 70)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if errors:
        print("\nFailed Tests:")
        for test_name, error in errors:
            print(f"  - {test_name}: {error}")

    print("=" * 70)

    if failed > 0:
        print("\n⚠️  Some tests failed. Please check the API server is running.")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)
