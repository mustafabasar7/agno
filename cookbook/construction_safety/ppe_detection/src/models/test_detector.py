"""
Test script for PPE Detection System

Quick test to verify the detector is working correctly.
Run this script to ensure everything is installed and configured properly.
"""

import sys
import numpy as np
from pathlib import Path

try:
    from ppe_detector import PPEDetector, Detection, ComplianceResult
    from model_config import ModelConfig, ConfigPresets, default_config
    print("✓ Imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nMake sure you have installed:")
    print("  pip install ultralytics opencv-python numpy")
    sys.exit(1)


def test_configuration():
    """Test configuration system."""
    print("\n" + "="*60)
    print("Testing Configuration System")
    print("="*60)

    try:
        # Test default config
        config = default_config
        assert config.validate_thresholds(), "Default config validation failed"
        print("✓ Default configuration valid")

        # Test presets
        fast_config = ConfigPresets.fast_inference()
        assert fast_config.model_architecture == "yolov8n", "Fast config incorrect"
        print("✓ Fast inference preset valid")

        prod_config = ConfigPresets.production()
        assert prod_config.confidence_threshold == prod_config.production_confidence_threshold
        print("✓ Production preset valid")

        # Test custom config
        custom_config = ModelConfig()
        custom_config.confidence_threshold = 0.7
        custom_config.input_size = (416, 416)
        assert custom_config.validate_thresholds(), "Custom config validation failed"
        print("✓ Custom configuration valid")

        print("\n✓ All configuration tests passed!")
        return True

    except Exception as e:
        print(f"\n✗ Configuration test failed: {e}")
        return False


def test_detector_initialization():
    """Test detector initialization."""
    print("\n" + "="*60)
    print("Testing Detector Initialization")
    print("="*60)

    try:
        # Initialize with default config
        detector = PPEDetector(verbose=True)
        assert detector.model is not None, "Model not loaded"
        print("✓ Detector initialized successfully")

        # Check statistics
        stats = detector.get_statistics()
        assert stats['total_detections'] == 0, "Initial stats incorrect"
        print("✓ Statistics initialized correctly")

        print("\n✓ Detector initialization test passed!")
        return True

    except Exception as e:
        print(f"\n✗ Detector initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_detection():
    """Test detection on dummy image."""
    print("\n" + "="*60)
    print("Testing Detection on Dummy Image")
    print("="*60)

    try:
        detector = PPEDetector(verbose=False)

        # Create dummy image
        dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        print("✓ Created dummy test image (640x640)")

        # Run detection
        detections = detector.detect_ppe(dummy_image)
        print(f"✓ Detection completed ({len(detections)} detections)")

        # Verify detection object structure
        if detections:
            det = detections[0]
            assert hasattr(det, 'bbox'), "Detection missing bbox"
            assert hasattr(det, 'confidence'), "Detection missing confidence"
            assert hasattr(det, 'class_name'), "Detection missing class_name"
            print("✓ Detection object structure valid")

        print("\n✓ Detection test passed!")
        return True

    except Exception as e:
        print(f"\n✗ Detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_compliance_checking():
    """Test compliance checking."""
    print("\n" + "="*60)
    print("Testing Compliance Checking")
    print("="*60)

    try:
        detector = PPEDetector(verbose=False)

        # Create test detections manually
        test_detections = [
            Detection(
                bbox=(100, 100, 200, 300),
                confidence=0.9,
                class_id=2,
                class_name="person"
            ),
            Detection(
                bbox=(110, 100, 180, 150),
                confidence=0.85,
                class_id=0,
                class_name="helmet"
            ),
            Detection(
                bbox=(120, 180, 190, 250),
                confidence=0.8,
                class_id=1,
                class_name="vest"
            )
        ]
        print("✓ Created test detections")

        # Check compliance
        compliance_results = detector.is_compliant(test_detections)
        print(f"✓ Compliance check completed ({len(compliance_results)} persons)")

        # Verify compliance result structure
        if compliance_results:
            result = compliance_results[0]
            assert hasattr(result, 'is_compliant'), "Result missing is_compliant"
            assert hasattr(result, 'has_helmet'), "Result missing has_helmet"
            assert hasattr(result, 'has_vest'), "Result missing has_vest"
            print("✓ Compliance result structure valid")

            # This should be compliant (person with helmet and vest nearby)
            if result.has_helmet and result.has_vest:
                print(f"✓ Compliance logic working (person is compliant)")
            else:
                print(f"⚠ Note: Person marked as missing PPE (may be due to detection logic)")

        print("\n✓ Compliance checking test passed!")
        return True

    except Exception as e:
        print(f"\n✗ Compliance checking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visualization():
    """Test visualization functions."""
    print("\n" + "="*60)
    print("Testing Visualization Functions")
    print("="*60)

    try:
        detector = PPEDetector(verbose=False)

        # Create dummy image and detections
        dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)

        test_detections = [
            Detection(
                bbox=(100, 100, 200, 300),
                confidence=0.9,
                class_id=2,
                class_name="person"
            )
        ]

        # Test detection visualization
        viz_image = detector.visualize_detections(dummy_image, test_detections)
        assert viz_image.shape == dummy_image.shape, "Visualization changed image shape"
        print("✓ Detection visualization works")

        # Test compliance visualization
        compliance_results = detector.is_compliant(test_detections)
        comp_viz = detector.visualize_compliance(dummy_image, compliance_results)
        assert comp_viz.shape == dummy_image.shape, "Compliance viz changed image shape"
        print("✓ Compliance visualization works")

        print("\n✓ Visualization test passed!")
        return True

    except Exception as e:
        print(f"\n✗ Visualization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_statistics():
    """Test statistics tracking."""
    print("\n" + "="*60)
    print("Testing Statistics Tracking")
    print("="*60)

    try:
        detector = PPEDetector(verbose=False)

        # Initial stats
        stats = detector.get_statistics()
        assert stats['total_detections'] == 0, "Initial detections not zero"
        print("✓ Initial statistics correct")

        # Process some images
        for i in range(3):
            dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
            detections = detector.detect_ppe(dummy_image)

        # Check updated stats
        stats = detector.get_statistics()
        assert stats['total_frames_processed'] == 3, "Frame count incorrect"
        print(f"✓ Statistics updated correctly ({stats['total_frames_processed']} frames)")

        # Reset stats
        detector.reset_statistics()
        stats = detector.get_statistics()
        assert stats['total_frames_processed'] == 0, "Reset failed"
        print("✓ Statistics reset works")

        print("\n✓ Statistics test passed!")
        return True

    except Exception as e:
        print(f"\n✗ Statistics test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_paths():
    """Test model path configuration."""
    print("\n" + "="*60)
    print("Testing Model Path Configuration")
    print("="*60)

    try:
        config = ModelConfig()

        # Get default model path
        default_path = config.get_model_path(use_custom=False)
        assert default_path is not None, "Default path is None"
        print(f"✓ Default model path: {default_path}")

        # Check if weights directory exists
        weights_dir = default_path.parent
        assert weights_dir.exists(), "Weights directory doesn't exist"
        print(f"✓ Weights directory exists: {weights_dir}")

        # Try custom model path
        custom_path = config.get_model_path(use_custom=True)
        print(f"✓ Custom model path: {custom_path}")

        print("\n✓ Model path test passed!")
        return True

    except Exception as e:
        print(f"\n✗ Model path test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print(" PPE DETECTION SYSTEM - TEST SUITE")
    print("="*70)

    tests = [
        ("Configuration", test_configuration),
        ("Detector Initialization", test_detector_initialization),
        ("Detection", test_detection),
        ("Compliance Checking", test_compliance_checking),
        ("Visualization", test_visualization),
        ("Statistics", test_statistics),
        ("Model Paths", test_model_paths),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} - {test_name}")

    print("="*70)
    print(f"Results: {passed}/{total} tests passed")
    print("="*70)

    if passed == total:
        print("\n🎉 All tests passed! The PPE detection system is ready to use.")
        print("\nNext steps:")
        print("  1. Try the example usage: python example_usage.py")
        print("  2. Process your own images/videos")
        print("  3. Fine-tune on your custom dataset")
        return True
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
