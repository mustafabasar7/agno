"""
Example usage of the PPE Detection database layer.

This module demonstrates common database operations including:
- Database initialization
- Creating and querying records
- Using filters and pagination
- Getting statistics
- Transaction management
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

# Import database components
from database import (
    init_db,
    create_zone,
    create_camera,
    create_violation,
    create_detection_log,
    get_cameras,
    get_violations,
    get_violation_stats,
    get_detection_stats,
    update_camera_status,
    acknowledge_violation,
    CameraStatus,
    ViolationType,
)


def example_1_initialize_database():
    """Example 1: Initialize database and create tables."""
    print("=" * 60)
    print("Example 1: Initialize Database")
    print("=" * 60)

    # Initialize with SQLite (development)
    db = init_db(
        database_url="sqlite:///./data/ppe_detection_example.db",
        create_tables=True
    )

    print("Database initialized successfully!")
    print(f"Database URL: {db.config.database_url}")
    print(f"Database type: {'SQLite' if db.config.is_sqlite else 'PostgreSQL'}")
    print()

    return db


def example_2_create_zones(db):
    """Example 2: Create zones with PPE requirements."""
    print("=" * 60)
    print("Example 2: Create Zones")
    print("=" * 60)

    with db.session_scope() as session:
        # Create construction zone
        zone1 = create_zone(session, {
            "name": "Construction Area A",
            "description": "Main construction zone with heavy machinery",
            "required_ppe": ["helmet", "vest", "boots", "gloves"]
        })
        print(f"Created: {zone1.name} (ID: {zone1.id})")

        # Create warehouse zone
        zone2 = create_zone(session, {
            "name": "Warehouse",
            "description": "Storage and logistics area",
            "required_ppe": ["helmet", "vest"]
        })
        print(f"Created: {zone2.name} (ID: {zone2.id})")

        # Create office zone
        zone3 = create_zone(session, {
            "name": "Site Office",
            "description": "Administrative area",
            "required_ppe": ["vest"]
        })
        print(f"Created: {zone3.name} (ID: {zone3.id})")

    print()
    return [zone1, zone2, zone3]


def example_3_create_cameras(db, zones):
    """Example 3: Create cameras for different zones."""
    print("=" * 60)
    print("Example 3: Create Cameras")
    print("=" * 60)

    cameras = []
    with db.session_scope() as session:
        # Camera 1 - Construction area
        camera1 = create_camera(session, {
            "name": "CAM-CONST-01",
            "rtsp_url": "rtsp://192.168.1.100:554/stream1",
            "zone_id": zones[0].id,
            "status": CameraStatus.ACTIVE,
            "location": "Construction Area - North Entrance",
            "fps": 30,
            "resolution": "1920x1080"
        })
        cameras.append(camera1)
        print(f"Created: {camera1.name} at {camera1.location}")

        # Camera 2 - Construction area
        camera2 = create_camera(session, {
            "name": "CAM-CONST-02",
            "rtsp_url": "rtsp://192.168.1.101:554/stream1",
            "zone_id": zones[0].id,
            "status": CameraStatus.ACTIVE,
            "location": "Construction Area - South Side",
            "fps": 30,
            "resolution": "1920x1080"
        })
        cameras.append(camera2)
        print(f"Created: {camera2.name} at {camera2.location}")

        # Camera 3 - Warehouse
        camera3 = create_camera(session, {
            "name": "CAM-WARE-01",
            "rtsp_url": "rtsp://192.168.1.102:554/stream1",
            "zone_id": zones[1].id,
            "status": CameraStatus.ACTIVE,
            "location": "Warehouse - Main Entrance",
            "fps": 15,
            "resolution": "1280x720"
        })
        cameras.append(camera3)
        print(f"Created: {camera3.name} at {camera3.location}")

    print()
    return cameras


def example_4_create_violations(db, cameras):
    """Example 4: Create violation records."""
    print("=" * 60)
    print("Example 4: Create Violations")
    print("=" * 60)

    violations = []
    with db.session_scope() as session:
        # Violation 1 - No helmet
        violation1 = create_violation(session, {
            "camera_id": cameras[0].id,
            "timestamp": datetime.now() - timedelta(hours=2),
            "image_path": "/data/violations/2024/11/18/violation_001.jpg",
            "violation_type": ViolationType.NO_HELMET,
            "confidence": 0.95,
            "person_count": 1,
            "severity": "high",
            "bounding_boxes": [{"x": 100, "y": 150, "w": 200, "h": 300}],
            "metadata": {"worker_id": "unknown", "shift": "morning"}
        })
        violations.append(violation1)
        print(f"Created violation: {violation1.violation_type.value} "
              f"(Confidence: {violation1.confidence:.2f})")

        # Violation 2 - No vest
        violation2 = create_violation(session, {
            "camera_id": cameras[1].id,
            "timestamp": datetime.now() - timedelta(hours=1),
            "image_path": "/data/violations/2024/11/18/violation_002.jpg",
            "violation_type": ViolationType.NO_VEST,
            "confidence": 0.88,
            "person_count": 1,
            "severity": "medium",
        })
        violations.append(violation2)
        print(f"Created violation: {violation2.violation_type.value} "
              f"(Confidence: {violation2.confidence:.2f})")

        # Violation 3 - Multiple violations
        violation3 = create_violation(session, {
            "camera_id": cameras[0].id,
            "timestamp": datetime.now() - timedelta(minutes=30),
            "image_path": "/data/violations/2024/11/18/violation_003.jpg",
            "violation_type": ViolationType.MULTIPLE,
            "confidence": 0.92,
            "person_count": 2,
            "severity": "critical",
            "metadata": {
                "violations": ["no_helmet", "no_vest"],
                "count": 2
            }
        })
        violations.append(violation3)
        print(f"Created violation: {violation3.violation_type.value} "
              f"(Confidence: {violation3.confidence:.2f})")

    print()
    return violations


def example_5_create_detection_logs(db, cameras):
    """Example 5: Create detection log entries."""
    print("=" * 60)
    print("Example 5: Create Detection Logs")
    print("=" * 60)

    with db.session_scope() as session:
        # Log 1 - Good compliance
        log1 = create_detection_log(session, {
            "camera_id": cameras[0].id,
            "timestamp": datetime.now() - timedelta(minutes=5),
            "total_persons": 5,
            "compliant_count": 5,
            "violation_count": 0,
            "processing_time_ms": 145.3,
        })
        print(f"Log created: {log1.total_persons} persons, "
              f"{log1.compliance_rate:.1f}% compliant")

        # Log 2 - Some violations
        log2 = create_detection_log(session, {
            "camera_id": cameras[1].id,
            "timestamp": datetime.now() - timedelta(minutes=3),
            "total_persons": 8,
            "compliant_count": 6,
            "violation_count": 2,
            "processing_time_ms": 167.8,
        })
        print(f"Log created: {log2.total_persons} persons, "
              f"{log2.compliance_rate:.1f}% compliant")

        # Log 3 - Poor compliance
        log3 = create_detection_log(session, {
            "camera_id": cameras[0].id,
            "timestamp": datetime.now(),
            "total_persons": 3,
            "compliant_count": 1,
            "violation_count": 2,
            "processing_time_ms": 132.1,
        })
        print(f"Log created: {log3.total_persons} persons, "
              f"{log3.compliance_rate:.1f}% compliant")

    print()


def example_6_query_cameras(db):
    """Example 6: Query cameras with filters."""
    print("=" * 60)
    print("Example 6: Query Cameras")
    print("=" * 60)

    with db.session_scope() as session:
        # Get all active cameras
        active_cameras = get_cameras(session, active_only=True)
        print(f"Active cameras: {len(active_cameras)}")
        for camera in active_cameras:
            print(f"  - {camera.name}: {camera.status.value}")

        # Get cameras by status
        print("\nCameras by status:")
        for status in [CameraStatus.ACTIVE, CameraStatus.INACTIVE]:
            cameras = get_cameras(session, active_only=False, status=status)
            print(f"  {status.value}: {len(cameras)}")

    print()


def example_7_query_violations(db):
    """Example 7: Query violations with filters and pagination."""
    print("=" * 60)
    print("Example 7: Query Violations")
    print("=" * 60)

    with db.session_scope() as session:
        # Get recent violations
        violations, total = get_violations(
            session,
            start_date=datetime.now() - timedelta(days=1),
            limit=10
        )
        print(f"Recent violations (last 24h): {total}")
        for v in violations[:3]:
            print(f"  - {v.violation_type.value} at {v.timestamp} "
                  f"(Confidence: {v.confidence:.2f})")

        # Get unacknowledged violations
        unack_violations, unack_total = get_violations(
            session,
            acknowledged=False
        )
        print(f"\nUnacknowledged violations: {unack_total}")

        # Get high severity violations
        high_severity, high_total = get_violations(
            session,
            severity="high",
            min_confidence=0.9
        )
        print(f"High severity violations (>90% confidence): {high_total}")

    print()


def example_8_get_statistics(db):
    """Example 8: Get violation and detection statistics."""
    print("=" * 60)
    print("Example 8: Get Statistics")
    print("=" * 60)

    with db.session_scope() as session:
        # Violation statistics
        violation_stats = get_violation_stats(
            session,
            start_date=datetime.now() - timedelta(days=7)
        )
        print("Violation Statistics (Last 7 days):")
        print(f"  Total violations: {violation_stats['total_violations']}")
        print(f"  Average confidence: {violation_stats['average_confidence']:.2f}")
        print(f"  Acknowledged: {violation_stats['acknowledged_count']}")
        print(f"  Unacknowledged: {violation_stats['unacknowledged_count']}")

        print("\n  Violations by type:")
        for vtype, count in violation_stats['violations_by_type'].items():
            print(f"    {vtype}: {count}")

        print("\n  Violations by severity:")
        for severity, count in violation_stats['violations_by_severity'].items():
            print(f"    {severity}: {count}")

        # Detection statistics
        detection_stats = get_detection_stats(
            session,
            start_date=datetime.now() - timedelta(days=7)
        )
        print("\nDetection Statistics (Last 7 days):")
        print(f"  Total detections: {detection_stats['total_detections']}")
        print(f"  Persons detected: {detection_stats['total_persons_detected']}")
        print(f"  Compliant: {detection_stats['total_compliant']}")
        print(f"  Violations: {detection_stats['total_violations']}")
        print(f"  Average compliance: {detection_stats['average_compliance_rate']:.2f}%")
        print(f"  Avg processing time: {detection_stats['average_processing_time_ms']:.2f}ms")

    print()


def example_9_update_operations(db):
    """Example 9: Update camera status and acknowledge violations."""
    print("=" * 60)
    print("Example 9: Update Operations")
    print("=" * 60)

    with db.session_scope() as session:
        # Update camera status
        camera = update_camera_status(
            session,
            camera_id=1,
            status=CameraStatus.ACTIVE,
            update_heartbeat=True
        )
        if camera:
            print(f"Updated camera {camera.name} status to {camera.status.value}")
            print(f"Last heartbeat: {camera.last_heartbeat}")

        # Acknowledge a violation
        violation = acknowledge_violation(
            session,
            violation_id=1,
            acknowledged_by="supervisor@example.com",
            notes="Violation reviewed. Worker warned and retrained."
        )
        if violation:
            print(f"\nAcknowledged violation {violation.id}")
            print(f"Acknowledged by: {violation.acknowledged_by}")
            print(f"Acknowledged at: {violation.acknowledged_at}")
            print(f"Notes: {violation.notes}")

    print()


def example_10_pagination(db):
    """Example 10: Demonstrate pagination."""
    print("=" * 60)
    print("Example 10: Pagination")
    print("=" * 60)

    with db.session_scope() as session:
        page_size = 2
        page = 1

        while True:
            skip = (page - 1) * page_size
            violations, total = get_violations(
                session,
                skip=skip,
                limit=page_size,
                order_by="timestamp",
                order_desc=True
            )

            if not violations:
                break

            print(f"\nPage {page} of {(total + page_size - 1) // page_size}:")
            for v in violations:
                print(f"  - ID {v.id}: {v.violation_type.value} "
                      f"at {v.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

            page += 1
            if skip + page_size >= total:
                break

    print()


def run_all_examples():
    """Run all examples in sequence."""
    print("\n" + "=" * 60)
    print("PPE Detection Database - Example Usage")
    print("=" * 60 + "\n")

    # Ensure data directory exists
    os.makedirs("./data", exist_ok=True)

    try:
        # Initialize database
        db = example_1_initialize_database()

        # Create sample data
        zones = example_2_create_zones(db)
        cameras = example_3_create_cameras(db, zones)
        violations = example_4_create_violations(db, cameras)
        example_5_create_detection_logs(db, cameras)

        # Query examples
        example_6_query_cameras(db)
        example_7_query_violations(db)
        example_8_get_statistics(db)
        example_9_update_operations(db)
        example_10_pagination(db)

        print("=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)

        # Close database
        db.close()

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
