#!/usr/bin/env python3
"""
Verification script for RTSP camera stream handler installation

Run this script to verify that all components are properly installed and working.
"""

import sys
import os

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)


def check_dependencies():
    """Check if required dependencies are installed"""
    print_header("Checking Dependencies")

    dependencies = {
        'cv2': 'opencv-python',
        'numpy': 'numpy',
    }

    optional_dependencies = {
        'yaml': 'pyyaml',
        'dotenv': 'python-dotenv',
    }

    all_ok = True

    # Check required dependencies
    print("\nRequired Dependencies:")
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING (install with: pip install {package})")
            all_ok = False

    # Check optional dependencies
    print("\nOptional Dependencies:")
    for module, package in optional_dependencies.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ○ {package} - Not installed (optional)")

    return all_ok


def check_modules():
    """Check if camera modules can be imported"""
    print_header("Checking Camera Modules")

    modules = [
        ('camera_config', 'Camera Configuration'),
        ('rtsp_handler', 'RTSP Handler'),
        ('camera_manager', 'Camera Manager'),
        ('config_loader', 'Configuration Loader'),
    ]

    all_ok = True

    for module_name, description in modules:
        try:
            module = __import__(module_name)
            print(f"  ✓ {description} ({module_name}.py)")
        except ImportError as e:
            print(f"  ✗ {description} ({module_name}.py) - FAILED: {e}")
            all_ok = False
        except Exception as e:
            print(f"  ✗ {description} ({module_name}.py) - ERROR: {e}")
            all_ok = False

    return all_ok


def check_classes():
    """Check if main classes can be instantiated"""
    print_header("Checking Classes")

    all_ok = True

    # Check CameraConfig
    try:
        from camera_config import CameraConfig, build_rtsp_url, RTSP_URL_TEMPLATES

        config = CameraConfig(
            camera_id="test",
            rtsp_url="rtsp://admin:pass@192.168.1.1:554/stream",
            name="Test",
            zone="Test"
        )
        print(f"  ✓ CameraConfig - can create instance")
        print(f"    - Supported camera types: {list(RTSP_URL_TEMPLATES.keys())}")

        url = build_rtsp_url('hikvision', '192.168.1.1', 'admin', 'pass')
        print(f"  ✓ build_rtsp_url - works correctly")

    except Exception as e:
        print(f"  ✗ CameraConfig - FAILED: {e}")
        all_ok = False

    # Check RTSPHandler
    try:
        from rtsp_handler import RTSPHandler
        from camera_config import CameraConfig

        config = CameraConfig(
            camera_id="test",
            rtsp_url="rtsp://admin:pass@192.168.1.1:554/stream",
            name="Test",
            zone="Test"
        )
        handler = RTSPHandler(config)
        print(f"  ✓ RTSPHandler - can create instance")

    except Exception as e:
        print(f"  ✗ RTSPHandler - FAILED: {e}")
        all_ok = False

    # Check CameraManager
    try:
        from camera_manager import CameraManager

        manager = CameraManager()
        print(f"  ✓ CameraManager - can create instance")

    except Exception as e:
        print(f"  ✗ CameraManager - FAILED: {e}")
        all_ok = False

    return all_ok


def check_files():
    """Check if all required files exist"""
    print_header("Checking Files")

    current_dir = os.path.dirname(os.path.abspath(__file__))

    required_files = [
        '__init__.py',
        'camera_config.py',
        'rtsp_handler.py',
        'camera_manager.py',
        'config_loader.py',
        'requirements.txt',
    ]

    example_files = [
        'example_usage.py',
        'production_example.py',
        'test_camera_system.py',
    ]

    documentation_files = [
        'README.md',
        'QUICK_START.md',
        'IMPLEMENTATION_SUMMARY.md',
        'camera_config.example.yaml',
        '.env.example',
    ]

    all_ok = True

    print("\nCore Files:")
    for filename in required_files:
        filepath = os.path.join(current_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"  ✓ {filename} ({size} bytes)")
        else:
            print(f"  ✗ {filename} - MISSING")
            all_ok = False

    print("\nExample Files:")
    for filename in example_files:
        filepath = os.path.join(current_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"  ✓ {filename} ({size} bytes)")
        else:
            print(f"  ○ {filename} - Not found")

    print("\nDocumentation Files:")
    for filename in documentation_files:
        filepath = os.path.join(current_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"  ✓ {filename} ({size} bytes)")
        else:
            print(f"  ○ {filename} - Not found")

    return all_ok


def check_api():
    """Check if main API functions work"""
    print_header("Checking API")

    all_ok = True

    try:
        from camera_config import CameraConfig, create_camera_config_from_url, build_rtsp_url
        from rtsp_handler import RTSPHandler
        from camera_manager import CameraManager

        # Test creating config with helper
        config = create_camera_config_from_url(
            camera_id="test",
            rtsp_url="rtsp://admin:pass@192.168.1.1:554/stream",
            name="Test Camera",
            zone="Test Zone"
        )
        print(f"  ✓ create_camera_config_from_url() works")

        # Test config validation
        config.validate()
        print(f"  ✓ Configuration validation works")

        # Test config serialization
        config_dict = config.to_dict()
        config_restored = CameraConfig.from_dict(config_dict)
        assert config_restored.camera_id == config.camera_id
        print(f"  ✓ Configuration serialization works")

        # Test URL sanitization
        sanitized = config.get_sanitized_url()
        assert 'pass' not in sanitized
        print(f"  ✓ URL sanitization works")

        # Test manager context manager
        with CameraManager() as manager:
            pass
        print(f"  ✓ CameraManager context manager works")

        # Test handler context manager
        with RTSPHandler(config) as handler:
            pass
        print(f"  ✓ RTSPHandler context manager works")

    except Exception as e:
        print(f"  ✗ API check failed: {e}")
        all_ok = False

    return all_ok


def print_usage_example():
    """Print a simple usage example"""
    print_header("Quick Usage Example")

    print("""
from camera import CameraConfig, CameraManager

# Create configuration
config = CameraConfig(
    camera_id="cam_001",
    rtsp_url="rtsp://admin:password@192.168.1.100:554/stream",
    name="Giriş Kapısı",
    zone="Giriş Bölgesi"
)

# Create manager and add camera
manager = CameraManager()
manager.start()
manager.add_camera(config)

# Wait for connection
import time
time.sleep(5)

# Get snapshot
frame = manager.snapshot("cam_001")
if frame is not None:
    import cv2
    cv2.imwrite("snapshot.jpg", frame)

# Cleanup
manager.stop()
""")


def main():
    """Main verification function"""
    print("="*80)
    print("  RTSP Camera Stream Handler - Installation Verification")
    print("  İnşaat Şantiyesi Kamera Sistemi - Kurulum Doğrulama")
    print("="*80)

    results = []

    # Run checks
    results.append(("Dependencies", check_dependencies()))
    results.append(("Files", check_files()))
    results.append(("Modules", check_modules()))
    results.append(("Classes", check_classes()))
    results.append(("API", check_api()))

    # Print summary
    print_header("Verification Summary")

    all_passed = True
    for check_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {status}: {check_name}")
        if not passed:
            all_passed = False

    print("\n" + "="*80)

    if all_passed:
        print("  ✓ All checks passed!")
        print("  ✓ Installation is complete and working correctly.")
        print_usage_example()
        print("\n  Next steps:")
        print("    1. Review examples: python example_usage.py")
        print("    2. Run tests: python test_camera_system.py")
        print("    3. Configure cameras: edit camera_config.yaml")
        print("    4. Deploy: python production_example.py")
        print("="*80 + "\n")
        return 0
    else:
        print("  ✗ Some checks failed!")
        print("  ✗ Please review the errors above and fix them.")
        print("\n  Common fixes:")
        print("    - Install dependencies: pip install -r requirements.txt")
        print("    - Check file permissions")
        print("    - Verify Python version (3.7+)")
        print("="*80 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
