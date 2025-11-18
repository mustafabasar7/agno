"""
Configuration Test Script
Yapılandırma sistemini test etmek için kullanılır
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    get_settings,
    validate_config,
    ConfigLoader,
    load_cameras_from_yaml,
)


def test_basic_loading():
    """Temel yapılandırma yükleme testi"""
    print("=" * 70)
    print("Test 1: Temel Yapılandırma Yükleme")
    print("=" * 70)

    try:
        settings = get_settings()
        print("✅ Settings başarıyla yüklendi")
        print(f"  - Environment: {settings.environment}")
        print(f"  - Debug: {settings.debug}")
        print(f"  - Database: {settings.database.type}")
        print(f"  - Model: {settings.model.model_type}")
        return True
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        return False


def test_validation():
    """Yapılandırma doğrulama testi"""
    print("\n" + "=" * 70)
    print("Test 2: Yapılandırma Doğrulama")
    print("=" * 70)

    try:
        settings = get_settings()
        is_valid, errors, warnings = validate_config(
            settings,
            strict=False,
            exit_on_error=False
        )

        if is_valid:
            print("✅ Doğrulama başarılı")
        else:
            print(f"⚠️  {len(errors)} hata bulundu")
            for error in errors[:5]:  # İlk 5 hatayı göster
                print(f"  - {error}")

        if warnings:
            print(f"  {len(warnings)} uyarı bulundu")

        return is_valid
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        return False


def test_config_loader():
    """Config loader testi"""
    print("\n" + "=" * 70)
    print("Test 3: Config Loader")
    print("=" * 70)

    try:
        loader = ConfigLoader()

        # Development config yükle
        settings = loader.load(environment="development")
        print("✅ Development config yüklendi")
        print(f"  - Environment: {settings.environment}")
        print(f"  - Debug: {settings.debug}")

        return True
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_database_config():
    """Database yapılandırma testi"""
    print("\n" + "=" * 70)
    print("Test 4: Database Configuration")
    print("=" * 70)

    try:
        settings = get_settings()
        db_config = settings.database

        print(f"  Database Type: {db_config.type}")
        print(f"  Pool Size: {db_config.pool_size}")
        print(f"  Max Overflow: {db_config.max_overflow}")

        # Connection string oluştur
        conn_str = settings.get_db_connection_string()
        print(f"  Connection String: {conn_str[:50]}...")

        print("✅ Database config testi başarılı")
        return True
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        return False


def test_model_config():
    """Model yapılandırma testi"""
    print("\n" + "=" * 70)
    print("Test 5: Model Configuration")
    print("=" * 70)

    try:
        settings = get_settings()
        model_config = settings.model

        print(f"  Model Type: {model_config.model_type}")
        print(f"  Model Size: {model_config.model_size}")
        print(f"  Model Path: {model_config.model_path}")
        print(f"  Device: {model_config.device}")
        print(f"  Confidence: {model_config.confidence_threshold}")
        print(f"  Required PPE: {', '.join(model_config.required_ppe)}")

        print("✅ Model config testi başarılı")
        return True
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        return False


def test_camera_config():
    """Kamera yapılandırma testi"""
    print("\n" + "=" * 70)
    print("Test 6: Camera Configuration")
    print("=" * 70)

    try:
        settings = get_settings()
        cameras_config = settings.cameras

        print(f"  Default FPS: {cameras_config.default_fps}")
        print(f"  Default Resolution: {cameras_config.default_resolution}")
        print(f"  Total Cameras: {len(cameras_config.cameras)}")

        if cameras_config.cameras:
            print("\n  Configured Cameras:")
            for cam in cameras_config.cameras:
                status = "✅" if cam.enabled else "❌"
                print(f"    {status} {cam.camera_id}: {cam.name}")
                print(f"       Location: {cam.location}")
                print(f"       Zone: {cam.zone}")
        else:
            print("  ⚠️  No cameras configured")

        print("\n✅ Camera config testi başarılı")
        return True
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        return False


def test_alert_config():
    """Alert yapılandırma testi"""
    print("\n" + "=" * 70)
    print("Test 7: Alert Configuration")
    print("=" * 70)

    try:
        settings = get_settings()
        alert_config = settings.alerts

        print(f"  Alerts Enabled: {alert_config.enable_alerts}")
        print(f"  Email Alerts: {alert_config.enable_email}")
        print(f"  SMS Alerts: {alert_config.enable_sms}")
        print(f"  Webhook Alerts: {alert_config.enable_webhook}")
        print(f"  Database Logging: {alert_config.enable_database}")

        if alert_config.email_recipients:
            print(f"  Email Recipients: {', '.join(alert_config.email_recipients[:3])}")

        print("✅ Alert config testi başarılı")
        return True
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        return False


def test_monitoring_config():
    """Monitoring yapılandırma testi"""
    print("\n" + "=" * 70)
    print("Test 8: Monitoring Configuration")
    print("=" * 70)

    try:
        settings = get_settings()
        monitoring_config = settings.monitoring

        print(f"  Log Level: {monitoring_config.log_level}")
        print(f"  Log File: {monitoring_config.log_file}")
        print(f"  Metrics Enabled: {monitoring_config.enable_metrics}")
        print(f"  Metrics Port: {monitoring_config.metrics_port}")
        print(f"  Health Check Port: {monitoring_config.health_check_port}")
        print(f"  Save Snapshots: {monitoring_config.save_violation_snapshots}")

        print("✅ Monitoring config testi başarılı")
        return True
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        return False


def test_feature_flags():
    """Feature flags testi"""
    print("\n" + "=" * 70)
    print("Test 9: Feature Flags")
    print("=" * 70)

    try:
        settings = get_settings()
        feature_flags = settings.feature_flags

        print("  Feature Flags:")
        for flag, enabled in feature_flags.items():
            status = "✅" if enabled else "❌"
            print(f"    {status} {flag}")

        print("\n✅ Feature flags testi başarılı")
        return True
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        return False


def test_environment_specific():
    """Ortam-specific ayarlar testi"""
    print("\n" + "=" * 70)
    print("Test 10: Environment-Specific Settings")
    print("=" * 70)

    try:
        settings = get_settings()

        print(f"  Current Environment: {settings.environment}")
        print(f"  Is Development: {settings.is_development()}")
        print(f"  Is Staging: {settings.is_staging()}")
        print(f"  Is Production: {settings.is_production()}")
        print(f"  Effective Log Level: {settings.get_log_level()}")

        print("✅ Environment-specific testi başarılı")
        return True
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        return False


def test_config_export():
    """Yapılandırma export testi"""
    print("\n" + "=" * 70)
    print("Test 11: Configuration Export")
    print("=" * 70)

    try:
        settings = get_settings()

        # JSON export
        config_dict = settings.model_dump()
        print(f"  Exported {len(config_dict)} top-level keys")

        # Key listesi
        print("\n  Configuration Sections:")
        for key in config_dict.keys():
            print(f"    - {key}")

        print("\n✅ Config export testi başarılı")
        return True
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        return False


def run_all_tests():
    """Tüm testleri çalıştır"""
    print("\n")
    print("🚀 PPE Detection - Configuration System Tests")
    print("=" * 70)
    print("\n")

    tests = [
        ("Basic Loading", test_basic_loading),
        ("Validation", test_validation),
        ("Config Loader", test_config_loader),
        ("Database Config", test_database_config),
        ("Model Config", test_model_config),
        ("Camera Config", test_camera_config),
        ("Alert Config", test_alert_config),
        ("Monitoring Config", test_monitoring_config),
        ("Feature Flags", test_feature_flags),
        ("Environment Specific", test_environment_specific),
        ("Config Export", test_config_export),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Test hatası: {test_name}")
            print(f"  {str(e)}")
            results[test_name] = False

    # Sonuçları özetle
    print("\n" + "=" * 70)
    print("Test Sonuçları")
    print("=" * 70)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")

    print("\n" + "=" * 70)
    print(f"Toplam: {passed}/{total} test başarılı")
    print("=" * 70)

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
