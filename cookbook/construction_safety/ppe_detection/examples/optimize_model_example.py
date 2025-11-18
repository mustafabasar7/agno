"""
Example: Optimize a YOLO model for PPE detection.

This script demonstrates how to:
1. Load a YOLO model
2. Convert it to ONNX
3. Apply quantization
4. Benchmark performance
5. Compare original vs optimized models
"""

import sys
from pathlib import Path
import numpy as np
import cv2

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.optimization import (
    OptimizationConfig,
    OptimizationLevel,
    ModelOptimizer,
    InferenceEngine,
    PerformanceBenchmark,
    PresetConfigs
)


def load_test_images(image_dir: str, num_images: int = 100):
    """Load test images from directory."""
    image_dir = Path(image_dir)
    images = []

    # Get image files
    image_files = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png"))

    for img_file in image_files[:num_images]:
        img = cv2.imread(str(img_file))
        if img is not None:
            images.append(img)

    # If not enough images, create synthetic ones
    while len(images) < num_images:
        synthetic = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        images.append(synthetic)

    print(f"Loaded {len(images)} test images")
    return images


def main():
    """Main optimization workflow."""
    print("=" * 80)
    print("PPE Detection Model Optimization Example")
    print("=" * 80)

    # Configuration
    # You can choose from preset configurations or create custom ones
    print("\nAvailable preset configurations:")
    print("1. High Accuracy - Slower but more accurate")
    print("2. Balanced - Good balance (default)")
    print("3. High Performance - Faster but less accurate")
    print("4. Maximum Speed - Fastest for resource-constrained devices")
    print("5. Edge Device - Optimized for Raspberry Pi, etc.")

    # Use balanced configuration (you can change this)
    config = PresetConfigs.get_balanced()

    # Or create custom configuration
    # config = OptimizationConfig()
    # config.level = OptimizationLevel.LEVEL_3_QUANTIZATION
    # config.input_size = (640, 640)
    # config.frame_skip = 2

    print(f"\nUsing configuration: {config.get_optimization_description()}")
    print(f"Input size: {config.input_size}")
    print(f"Optimization level: {config.level.name}")

    # Paths
    model_path = "models/yolov8n.pt"  # Your YOLO model
    output_dir = "optimized_models"
    test_images_dir = "data/sample_images"

    # Check if model exists
    if not Path(model_path).exists():
        print(f"\nWARNING: Model not found at {model_path}")
        print("Please download a YOLO model or update the path")
        print("\nExample to download YOLOv8n:")
        print("  from ultralytics import YOLO")
        print("  model = YOLO('yolov8n.pt')")
        return

    # Load test images
    print("\nLoading test images...")
    test_images = load_test_images(test_images_dir, num_images=100)

    # Step 1: Optimize the model
    print("\n" + "=" * 80)
    print("STEP 1: Model Optimization")
    print("=" * 80)

    optimizer = ModelOptimizer(config)

    # Optional: Prepare calibration data for static quantization
    calibration_data = test_images[:20] if config.level.value >= 3 else None

    optimization_results = optimizer.optimize_model(
        model_path=model_path,
        output_dir=output_dir,
        calibration_data=calibration_data
    )

    print("\nOptimization Results:")
    print(f"  Original size: {optimization_results['original_size_mb']:.2f} MB")
    print(f"  Optimized size: {optimization_results['optimized_size_mb']:.2f} MB")
    print(f"  Size reduction: {optimization_results['size_reduction_percent']:.2f}%")
    print(f"  Optimizations applied: {', '.join(optimization_results['optimizations_applied'])}")

    # Step 2: Benchmark original model
    print("\n" + "=" * 80)
    print("STEP 2: Benchmarking Original Model")
    print("=" * 80)

    benchmark = PerformanceBenchmark(config)

    original_metrics = benchmark.benchmark_model(
        model_path=model_path,
        test_images=test_images[:50],
        model_name="original_yolo"
    )

    # Step 3: Benchmark optimized model
    print("\n" + "=" * 80)
    print("STEP 3: Benchmarking Optimized Model")
    print("=" * 80)

    optimized_model_path = optimization_results.get(
        "quantized_model",
        optimization_results.get("onnx_model")
    )

    optimized_metrics = benchmark.benchmark_model(
        model_path=optimized_model_path,
        test_images=test_images[:50],
        model_name="optimized_model"
    )

    # Step 4: Compare models
    print("\n" + "=" * 80)
    print("STEP 4: Model Comparison")
    print("=" * 80)

    comparison = benchmark.compare_models()

    print("\nPerformance Comparison:")
    for metric, values in comparison["metrics"].items():
        print(f"\n{metric}:")
        for model_name, value in values.items():
            print(f"  {model_name}: {value:.2f}")

    # Calculate improvements
    orig_fps = original_metrics["fps_metrics"]["avg_fps"]
    opt_fps = optimized_metrics["fps_metrics"]["avg_fps"]
    speedup = opt_fps / orig_fps if orig_fps > 0 else 0

    print(f"\nSpeedup: {speedup:.2f}x")
    print(f"FPS improvement: {((opt_fps - orig_fps) / orig_fps * 100):.2f}%")

    # Step 5: Generate report
    print("\n" + "=" * 80)
    print("STEP 5: Generating Report")
    print("=" * 80)

    report_path = Path(output_dir) / "optimization_report.json"
    benchmark.generate_report(str(report_path), include_charts=True)

    print(f"\nReport saved to: {report_path}")

    # Step 6: Test inference with optimized model
    print("\n" + "=" * 80)
    print("STEP 6: Testing Optimized Inference")
    print("=" * 80)

    engine = InferenceEngine(optimized_model_path, config)

    # Test on a few images
    print("\nRunning inference on 10 test images...")
    for i in range(10):
        img = test_images[i]
        result = engine.predict(img, return_details=True)

        print(f"Image {i+1}:")
        print(f"  Detections: {len(result['detections'])}")
        print(f"  FPS: {result['fps']:.2f}")
        print(f"  Inference time: {result['inference_time']*1000:.2f} ms")

    # Performance stats
    stats = engine.get_performance_stats()
    print(f"\nOverall Performance:")
    print(f"  Average FPS: {stats['avg_fps']:.2f}")
    print(f"  Average latency: {stats['avg_inference_time_ms']:.2f} ms")
    print(f"  P95 latency: {stats.get('p95_inference_time_ms', 0):.2f} ms")

    print("\n" + "=" * 80)
    print("Optimization Complete!")
    print("=" * 80)
    print(f"\nOptimized model saved to: {optimized_model_path}")
    print(f"Report saved to: {report_path}")

    # Target validation
    validation = optimized_metrics.get("target_validation", {})
    if validation.get("all_targets_met"):
        print("\n✓ All optimization targets met!")
    else:
        print("\n✗ Some targets not met:")
        for target, met in validation.get("targets_met", {}).items():
            if not met:
                actual = validation["actual"][target]
                target_val = validation["targets"][target]
                print(f"  - {target}: {actual:.2f} (target: {target_val:.2f})")


if __name__ == "__main__":
    main()
