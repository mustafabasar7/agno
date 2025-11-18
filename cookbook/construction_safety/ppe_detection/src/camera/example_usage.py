"""
Example usage of RTSP camera stream handler for Turkish construction sites

This example demonstrates how to:
1. Configure cameras with Turkish naming
2. Connect to multiple RTSP streams
3. Capture snapshots from cameras
4. Monitor camera health
5. Handle common camera types (Hikvision, Dahua, etc.)
"""

import logging
import time
import cv2
from datetime import datetime

from camera_config import CameraConfig, build_rtsp_url
from camera_manager import CameraManager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_1_single_camera():
    """Example 1: Connect to a single camera"""
    print("\n" + "="*80)
    print("ÖRNEK 1: Tek Kamera Bağlantısı (Single Camera Connection)")
    print("="*80)

    # Create camera configuration
    config = CameraConfig(
        camera_id="cam_001",
        rtsp_url="rtsp://admin:12345@192.168.1.100:554/Streaming/Channels/101",
        name="Giriş Kapısı",  # Entrance Gate
        zone="Giriş Bölgesi",  # Entrance Zone
        capture_interval=5.0,  # Capture every 5 seconds
        location="İstanbul Şantiye - Giriş",
        description="Ana giriş kapısı kamerası"
    )

    # Create camera manager
    manager = CameraManager()
    manager.start()

    # Add camera
    success = manager.add_camera(config)
    if success:
        logger.info(f"Kamera eklendi: {config.name}")
    else:
        logger.error("Kamera eklenemedi!")
        return

    # Wait for camera to connect and capture frames
    time.sleep(10)

    # Get snapshot
    frame = manager.snapshot("cam_001")
    if frame is not None:
        logger.info(f"Görüntü alındı: {frame.shape}")
        # Save snapshot
        cv2.imwrite("/tmp/snapshot_giris.jpg", frame)
        logger.info("Görüntü kaydedildi: /tmp/snapshot_giris.jpg")
    else:
        logger.warning("Görüntü alınamadı!")

    # Get camera status
    status = manager.get_camera_status("cam_001")
    logger.info(f"Kamera durumu: {status}")

    # Cleanup
    manager.stop()


def example_2_multiple_cameras_turkish_site():
    """Example 2: Multiple cameras for a Turkish construction site"""
    print("\n" + "="*80)
    print("ÖRNEK 2: Çoklu Kamera Yönetimi - Türk Şantiyesi (Multi-Camera Management)")
    print("="*80)

    # Define cameras for different zones in Turkish construction site
    cameras = [
        {
            'camera_id': 'cam_giris_001',
            'name': 'Ana Giriş Kapısı',
            'zone': 'Giriş Kontrol',
            'ip': '192.168.1.100',
            'camera_type': 'hikvision',
            'location': 'Şantiye Ana Girişi'
        },
        {
            'camera_id': 'cam_insaat_001',
            'name': 'İnşaat Alanı 1',
            'zone': 'İnşaat Bölgesi A',
            'ip': '192.168.1.101',
            'camera_type': 'hikvision',
            'location': 'A Blok İnşaat Alanı'
        },
        {
            'camera_id': 'cam_insaat_002',
            'name': 'İnşaat Alanı 2',
            'zone': 'İnşaat Bölgesi B',
            'ip': '192.168.1.102',
            'camera_type': 'dahua',
            'location': 'B Blok İnşaat Alanı'
        },
        {
            'camera_id': 'cam_depo_001',
            'name': 'Malzeme Deposu',
            'zone': 'Depo Bölgesi',
            'ip': '192.168.1.103',
            'camera_type': 'hikvision',
            'location': 'Ana Malzeme Deposu'
        },
        {
            'camera_id': 'cam_vinc_001',
            'name': 'Vinç Alanı',
            'zone': 'Vinç Operasyon',
            'ip': '192.168.1.104',
            'camera_type': 'hikvision',
            'location': 'Kule Vinç 1'
        },
    ]

    # Create camera manager
    manager = CameraManager()
    manager.start()

    # Add all cameras
    for cam_info in cameras:
        # Build RTSP URL
        rtsp_url = build_rtsp_url(
            camera_type=cam_info['camera_type'],
            ip=cam_info['ip'],
            username='admin',
            password='Santiye123!',
            port=554,
            channel=1
        )

        # Create configuration
        config = CameraConfig(
            camera_id=cam_info['camera_id'],
            rtsp_url=rtsp_url,
            name=cam_info['name'],
            zone=cam_info['zone'],
            location=cam_info['location'],
            capture_interval=5.0,
            reconnect_interval=3.0,
            max_reconnect_attempts=5
        )

        # Add camera
        manager.add_camera(config)
        logger.info(f"Kamera eklendi: {cam_info['name']} ({cam_info['zone']})")

    # Wait for cameras to connect
    logger.info("Kameraların bağlanması bekleniyor...")
    time.sleep(15)

    # Get health summary
    health = manager.get_health_summary()
    logger.info(f"\n{'='*60}")
    logger.info(f"Kamera Sağlık Raporu (Camera Health Report)")
    logger.info(f"{'='*60}")
    logger.info(f"Toplam Kamera: {health['total_cameras']}")
    logger.info(f"Aktif Kamera: {health['active_cameras']}")
    logger.info(f"İnaktif Kamera: {health['inactive_cameras']}")
    logger.info(f"Sağlık Yüzdesi: {health['health_percentage']:.1f}%")
    logger.info(f"\nBölge İstatistikleri:")
    for zone, stats in health['zone_statistics'].items():
        logger.info(f"  {zone}: {stats['active']}/{stats['total']} aktif")

    # Get active cameras
    active_cameras = manager.get_all_active_cameras()
    logger.info(f"\nAktif Kameralar: {len(active_cameras)}")
    for cam_id in active_cameras:
        status = manager.get_camera_status(cam_id)
        logger.info(f"  - {status['name']} ({status['zone']}): {status['total_frames_captured']} kare")

    # Capture snapshots from all cameras
    logger.info("\nTüm kameralardan görüntü alınıyor...")
    snapshots = manager.snapshot_all()

    # Save snapshots
    for camera_id, frame in snapshots.items():
        if frame is not None:
            config = manager.get_camera_config(camera_id)
            filename = f"/tmp/snapshot_{camera_id}.jpg"
            cv2.imwrite(filename, frame)
            logger.info(f"Görüntü kaydedildi: {config.name} -> {filename}")
        else:
            logger.warning(f"Görüntü alınamadı: {camera_id}")

    # Monitor for a while
    logger.info("\nKameralar 30 saniye izleniyor...")
    for i in range(6):
        time.sleep(5)
        active = len(manager.get_all_active_cameras())
        logger.info(f"  Durum kontrolü {i+1}/6: {active} kamera aktif")

    # Cleanup
    logger.info("\nKameralar kapatılıyor...")
    manager.stop()
    logger.info("Tamamlandı!")


def example_3_camera_health_monitoring():
    """Example 3: Camera health monitoring and reconnection"""
    print("\n" + "="*80)
    print("ÖRNEK 3: Kamera Sağlık İzleme ve Yeniden Bağlanma (Health Monitoring)")
    print("="*80)

    # Create camera with shorter intervals for demonstration
    config = CameraConfig(
        camera_id="cam_test_001",
        rtsp_url="rtsp://admin:12345@192.168.1.100:554/Streaming/Channels/101",
        name="Test Kamerası",
        zone="Test Bölgesi",
        capture_interval=2.0,  # Capture every 2 seconds
        reconnect_interval=3.0,  # Reconnect every 3 seconds
        max_reconnect_attempts=5
    )

    manager = CameraManager()
    manager.start()
    manager.add_camera(config)

    # Monitor camera status
    logger.info("Kamera durumu izleniyor (30 saniye)...")
    for i in range(15):
        time.sleep(2)

        status = manager.get_camera_status("cam_test_001")
        if status:
            logger.info(
                f"Zaman: {i*2}s | "
                f"Bağlı: {status['is_connected']} | "
                f"Sağlıklı: {status['is_healthy']} | "
                f"Kareler: {status['total_frames_captured']} | "
                f"Hatalar: {status['consecutive_failures']}"
            )

            if status['last_error']:
                logger.warning(f"  Son Hata: {status['last_error']}")

    manager.stop()


def example_4_dynamic_camera_management():
    """Example 4: Dynamic camera addition and removal"""
    print("\n" + "="*80)
    print("ÖRNEK 4: Dinamik Kamera Yönetimi (Dynamic Camera Management)")
    print("="*80)

    manager = CameraManager()
    manager.start()

    # Add camera 1
    config1 = CameraConfig(
        camera_id="cam_dynamic_001",
        rtsp_url="rtsp://admin:12345@192.168.1.100:554/Streaming/Channels/101",
        name="Dinamik Kamera 1",
        zone="Bölge A"
    )
    manager.add_camera(config1)
    logger.info("Kamera 1 eklendi")

    time.sleep(5)

    # Add camera 2
    config2 = CameraConfig(
        camera_id="cam_dynamic_002",
        rtsp_url="rtsp://admin:12345@192.168.1.101:554/Streaming/Channels/101",
        name="Dinamik Kamera 2",
        zone="Bölge B"
    )
    manager.add_camera(config2)
    logger.info("Kamera 2 eklendi")

    time.sleep(5)

    # List all cameras
    all_cameras = manager.get_all_cameras()
    logger.info(f"Toplam kamera sayısı: {len(all_cameras)}")

    # Remove camera 1
    manager.remove_camera("cam_dynamic_001")
    logger.info("Kamera 1 kaldırıldı")

    time.sleep(5)

    # Check remaining cameras
    remaining = manager.get_all_cameras()
    logger.info(f"Kalan kamera sayısı: {len(remaining)}")

    manager.stop()


def example_5_common_camera_types():
    """Example 5: Configuration examples for common camera types"""
    print("\n" + "="*80)
    print("ÖRNEK 5: Yaygın Kamera Türleri Yapılandırması (Common Camera Types)")
    print("="*80)

    # Hikvision camera
    hikvision_url = build_rtsp_url(
        camera_type='hikvision',
        ip='192.168.1.100',
        username='admin',
        password='Pass123',
        channel=1
    )
    logger.info(f"Hikvision RTSP URL: {hikvision_url}")

    # Dahua camera
    dahua_url = build_rtsp_url(
        camera_type='dahua',
        ip='192.168.1.101',
        username='admin',
        password='Pass123',
        channel=1
    )
    logger.info(f"Dahua RTSP URL: {dahua_url}")

    # Axis camera
    axis_url = build_rtsp_url(
        camera_type='axis',
        ip='192.168.1.102',
        username='root',
        password='Pass123'
    )
    logger.info(f"Axis RTSP URL: {axis_url}")

    # ONVIF camera
    onvif_url = build_rtsp_url(
        camera_type='onvif',
        ip='192.168.1.103',
        username='admin',
        password='Pass123'
    )
    logger.info(f"ONVIF RTSP URL: {onvif_url}")

    # Generic camera
    generic_url = build_rtsp_url(
        camera_type='generic',
        ip='192.168.1.104',
        username='admin',
        password='Pass123',
        path='live/main'
    )
    logger.info(f"Generic RTSP URL: {generic_url}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("RTSP Kamera Stream Handler - Türk Şantiyeleri İçin Örnekler")
    print("RTSP Camera Stream Handler - Examples for Turkish Construction Sites")
    print("="*80)

    # Note: These examples use placeholder IP addresses and credentials
    # In production, replace with actual camera details

    logger.info("\nBu örnekler demo amaçlıdır. Gerçek kamera bilgilerinizi kullanın.")
    logger.info("These examples are for demonstration. Use your actual camera details.\n")

    # Uncomment the example you want to run:

    # example_1_single_camera()
    # example_2_multiple_cameras_turkish_site()
    # example_3_camera_health_monitoring()
    # example_4_dynamic_camera_management()
    example_5_common_camera_types()

    print("\n" + "="*80)
    print("Örnekler tamamlandı! (Examples completed!)")
    print("="*80 + "\n")
