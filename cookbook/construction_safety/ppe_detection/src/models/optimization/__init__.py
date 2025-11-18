"""
Model optimization package for PPE detection.

Provides tools for:
- Converting YOLO models to ONNX
- Model quantization (INT8)
- Optimized inference with ONNX Runtime
- Performance benchmarking
- Memory optimization

Example usage:
    from models.optimization import (
        OptimizationConfig,
        ModelOptimizer,
        InferenceEngine,
        PerformanceBenchmark,
        PresetConfigs
    )

    # Create configuration
    config = PresetConfigs.get_balanced()

    # Optimize model
    optimizer = ModelOptimizer(config)
    results = optimizer.optimize_model(
        "yolov8n.pt",
        "optimized_models/"
    )

    # Run inference
    engine = InferenceEngine(results["onnx_model"], config)
    detections = engine.predict(image)

    # Benchmark
    benchmark = PerformanceBenchmark(config)
    metrics = benchmark.benchmark_model(
        results["onnx_model"],
        test_images
    )
"""

from .optimization_config import (
    OptimizationConfig,
    OptimizationLevel,
    QuantizationType,
    PresetConfigs,
    DEFAULT_CONFIG
)

from .model_optimizer import (
    ModelOptimizer,
    PPECalibrationDataReader
)

from .inference_engine import (
    InferenceEngine,
    VideoInferenceEngine
)

from .benchmarking import (
    PerformanceBenchmark
)

__all__ = [
    # Configuration
    "OptimizationConfig",
    "OptimizationLevel",
    "QuantizationType",
    "PresetConfigs",
    "DEFAULT_CONFIG",

    # Optimization
    "ModelOptimizer",
    "PPECalibrationDataReader",

    # Inference
    "InferenceEngine",
    "VideoInferenceEngine",

    # Benchmarking
    "PerformanceBenchmark",
]

__version__ = "1.0.0"
