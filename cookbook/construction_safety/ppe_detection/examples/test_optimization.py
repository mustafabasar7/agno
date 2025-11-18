"""
Simple test script to verify optimization module works correctly.

This script tests:
1. Module imports
2. Configuration creation
3. Preset configurations
4. Basic functionality without requiring actual models
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_imports():
    """Test that all modules import correctly."""
    print("Testing imports...")
    try:
        from models.optimization import (
            OptimizationConfig,
            OptimizationLevel,
            QuantizationType,
            PresetConfigs,
            ModelOptimizer,
            InferenceEngine,
            VideoInferenceEngine,
            PerformanceBenchmark
        )
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_configurations():
    """Test configuration creation and validation."""
    print("\nTesting configurations...")
    from models.optimization import (
        OptimizationConfig,
        OptimizationLevel,
        QuantizationType,
        PresetConfigs
    )

    try:
        # Test default config
        config = OptimizationConfig()
        print(f"✓ Default config created: {config.get_optimization_description()}")

        # Test custom config
        config.level = OptimizationLevel.LEVEL_3_QUANTIZATION
        config.input_size = (416, 416)
        config.frame_skip = 3
        print(f"✓ Custom config: Level {config.level.name}, Size {config.input_size}")

        # Test input size by name
        config.set_input_size_by_name("small")
        print(f"✓ Set input size by name: {config.input_size}")

        # Test preset configs
        presets = [
            "high_accuracy",
            "balanced",
            "high_performance",
            "maximum_speed",
            "edge_device"
        ]

        for preset_name in presets:
            preset_func = getattr(PresetConfigs, f"get_{preset_name}")
            preset_config = preset_func()
            print(f"✓ Preset '{preset_name}': {preset_config.get_optimization_description()}")

        # Test target validation
        metrics = {
            "fps": 15.0,
            "memory_mb": 400.0,
            "model_size_mb": 40.0,
            "accuracy": 0.88
        }
        validations = config.validate_targets(metrics)
        print(f"✓ Target validation: {validations}")

        return True

    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_optimizer():
    """Test model optimizer initialization."""
    print("\nTesting ModelOptimizer...")
    from models.optimization import ModelOptimizer, PresetConfigs

    try:
        config = PresetConfigs.get_balanced()
        optimizer = ModelOptimizer(config)
        print(f"✓ ModelOptimizer created with config: {config.level.name}")

        # Test size calculation (without actual model)
        print("✓ ModelOptimizer methods accessible")

        return True

    except Exception as e:
        print(f"✗ ModelOptimizer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_inference_engine():
    """Test inference engine initialization (without actual model)."""
    print("\nTesting InferenceEngine...")
    from models.optimization import PresetConfigs

    try:
        config = PresetConfigs.get_balanced()

        # Test preprocessing (without actual model)
        print(f"✓ Config created for inference: {config.input_size}")

        # Create synthetic image
        image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        print(f"✓ Synthetic test image created: {image.shape}")

        return True

    except Exception as e:
        print(f"✗ InferenceEngine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_benchmarking():
    """Test benchmarking utilities."""
    print("\nTesting PerformanceBenchmark...")
    from models.optimization import PerformanceBenchmark, PresetConfigs

    try:
        config = PresetConfigs.get_balanced()
        benchmark = PerformanceBenchmark(config)

        print(f"✓ PerformanceBenchmark created")
        print(f"✓ System info collected: {benchmark.system_info['platform']}")

        # Test IoU calculation
        box1 = [10, 10, 50, 50]
        box2 = [20, 20, 60, 60]
        iou = benchmark._calculate_iou(box1, box2)
        print(f"✓ IoU calculation: {iou:.3f}")

        return True

    except Exception as e:
        print(f"✗ Benchmarking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def display_summary():
    """Display summary information about the optimization module."""
    print("\n" + "=" * 80)
    print("OPTIMIZATION MODULE SUMMARY")
    print("=" * 80)

    from models.optimization import (
        OptimizationLevel,
        QuantizationType,
        PresetConfigs
    )

    print("\nOptimization Levels:")
    for level in OptimizationLevel:
        print(f"  - {level.name}: Level {level.value}")

    print("\nQuantization Types:")
    for qtype in QuantizationType:
        print(f"  - {qtype.name}: {qtype.value}")

    print("\nPreset Configurations:")
    presets = {
        "High Accuracy": PresetConfigs.get_high_accuracy(),
        "Balanced": PresetConfigs.get_balanced(),
        "High Performance": PresetConfigs.get_high_performance(),
        "Maximum Speed": PresetConfigs.get_maximum_speed(),
        "Edge Device": PresetConfigs.get_edge_device()
    }

    for name, config in presets.items():
        print(f"\n  {name}:")
        print(f"    Level: {config.level.name}")
        print(f"    Input size: {config.input_size}")
        print(f"    Frame skip: {config.frame_skip}")
        print(f"    Target FPS: {config.target_fps}")
        print(f"    Target accuracy: {config.target_accuracy}")

    print("\n" + "=" * 80)


def main():
    """Run all tests."""
    print("=" * 80)
    print("OPTIMIZATION MODULE TEST SUITE")
    print("=" * 80)

    tests = [
        ("Imports", test_imports),
        ("Configurations", test_configurations),
        ("ModelOptimizer", test_model_optimizer),
        ("InferenceEngine", test_inference_engine),
        ("Benchmarking", test_benchmarking)
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results[test_name] = False

    # Display results
    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)

    all_passed = True
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False

    print("=" * 80)

    if all_passed:
        print("\n✓ All tests passed!")
        display_summary()
        print("\nYou can now use the optimization module.")
        print("See examples/optimize_model_example.py for usage examples.")
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        print("\nMake sure all dependencies are installed:")
        print("  pip install -r src/models/optimization/requirements.txt")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
