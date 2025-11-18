"""
Configuration for model optimization.

Defines optimization levels, quantization settings, and performance targets.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Tuple


class OptimizationLevel(Enum):
    """Optimization levels with different trade-offs."""
    LEVEL_1_BASIC = 1  # Just use smaller input size
    LEVEL_2_ONNX = 2  # ONNX conversion for faster inference
    LEVEL_3_QUANTIZATION = 3  # INT8 quantization
    LEVEL_4_PRUNING = 4  # Model pruning (advanced)


class QuantizationType(Enum):
    """Quantization types supported."""
    DYNAMIC = "dynamic"  # Dynamic quantization (weights only)
    STATIC = "static"  # Static quantization (weights + activations)
    QAT = "qat"  # Quantization-aware training


@dataclass
class OptimizationConfig:
    """Configuration for model optimization."""

    # Optimization level
    level: OptimizationLevel = OptimizationLevel.LEVEL_2_ONNX

    # Input size options (smaller = faster, but less accurate)
    input_sizes: Dict[str, Tuple[int, int]] = field(default_factory=lambda: {
        "tiny": (320, 320),
        "small": (416, 416),
        "medium": (640, 640),
        "large": (1280, 1280)
    })
    input_size: Tuple[int, int] = (640, 640)  # Default medium

    # ONNX export settings
    onnx_opset_version: int = 12
    onnx_simplify: bool = True
    onnx_dynamic_axes: bool = True  # Support dynamic batch size

    # Quantization settings
    quantization_type: QuantizationType = QuantizationType.DYNAMIC
    quantization_calibration_samples: int = 100  # For static quantization
    quantization_per_channel: bool = True  # Better accuracy

    # Pruning settings (Level 4)
    pruning_amount: float = 0.3  # Remove 30% of weights
    pruning_structured: bool = False  # Unstructured pruning

    # Performance targets
    target_fps: int = 10  # Minimum FPS on CPU
    target_memory_mb: int = 500  # Max RAM per camera
    target_model_size_mb: int = 50  # Max model size
    target_accuracy: float = 0.85  # Min accuracy (mAP)

    # Inference settings
    batch_size: int = 1  # Batch processing
    half_precision: bool = False  # FP16 (for GPU)

    # Video optimization
    frame_skip: int = 2  # Process every Nth frame
    enable_frame_skip: bool = True

    # Hardware settings
    device: str = "cpu"  # cpu, cuda, or cuda:0
    num_threads: int = 4  # For CPU inference

    # Benchmarking
    benchmark_warmup_runs: int = 10
    benchmark_test_runs: int = 100
    benchmark_timeout_seconds: int = 300

    def get_input_size_name(self) -> str:
        """Get the name of the current input size."""
        for name, size in self.input_sizes.items():
            if size == self.input_size:
                return name
        return "custom"

    def set_input_size_by_name(self, name: str):
        """Set input size by name."""
        if name in self.input_sizes:
            self.input_size = self.input_sizes[name]
        else:
            raise ValueError(f"Unknown input size: {name}. Choose from {list(self.input_sizes.keys())}")

    def get_optimization_description(self) -> str:
        """Get a description of the current optimization level."""
        descriptions = {
            OptimizationLevel.LEVEL_1_BASIC: "Basic optimization with smaller input size",
            OptimizationLevel.LEVEL_2_ONNX: "ONNX conversion for faster CPU inference",
            OptimizationLevel.LEVEL_3_QUANTIZATION: "INT8 quantization for reduced model size",
            OptimizationLevel.LEVEL_4_PRUNING: "Model pruning for maximum optimization"
        }
        return descriptions.get(self.level, "Unknown optimization level")

    def validate_targets(self, metrics: Dict[str, float]) -> Dict[str, bool]:
        """Validate if optimization targets are met."""
        validations = {
            "fps": metrics.get("fps", 0) >= self.target_fps,
            "memory": metrics.get("memory_mb", float('inf')) <= self.target_memory_mb,
            "model_size": metrics.get("model_size_mb", float('inf')) <= self.target_model_size_mb,
            "accuracy": metrics.get("accuracy", 0) >= self.target_accuracy
        }
        return validations


@dataclass
class PresetConfigs:
    """Preset optimization configurations for common use cases."""

    @staticmethod
    def get_high_accuracy() -> OptimizationConfig:
        """High accuracy, lower performance preset."""
        config = OptimizationConfig()
        config.level = OptimizationLevel.LEVEL_2_ONNX
        config.input_size = (1280, 1280)
        config.frame_skip = 1
        config.target_accuracy = 0.90
        return config

    @staticmethod
    def get_balanced() -> OptimizationConfig:
        """Balanced accuracy and performance (default)."""
        config = OptimizationConfig()
        config.level = OptimizationLevel.LEVEL_2_ONNX
        config.input_size = (640, 640)
        config.frame_skip = 2
        config.target_accuracy = 0.85
        return config

    @staticmethod
    def get_high_performance() -> OptimizationConfig:
        """High performance, lower accuracy preset."""
        config = OptimizationConfig()
        config.level = OptimizationLevel.LEVEL_3_QUANTIZATION
        config.input_size = (416, 416)
        config.frame_skip = 3
        config.target_fps = 15
        config.target_accuracy = 0.80
        config.quantization_type = QuantizationType.DYNAMIC
        return config

    @staticmethod
    def get_maximum_speed() -> OptimizationConfig:
        """Maximum speed for resource-constrained devices."""
        config = OptimizationConfig()
        config.level = OptimizationLevel.LEVEL_3_QUANTIZATION
        config.input_size = (320, 320)
        config.frame_skip = 5
        config.target_fps = 20
        config.target_accuracy = 0.75
        config.quantization_type = QuantizationType.DYNAMIC
        config.batch_size = 4  # Process multiple frames at once
        return config

    @staticmethod
    def get_edge_device() -> OptimizationConfig:
        """Optimized for edge devices (Raspberry Pi, etc.)."""
        config = OptimizationConfig()
        config.level = OptimizationLevel.LEVEL_3_QUANTIZATION
        config.input_size = (416, 416)
        config.frame_skip = 4
        config.target_fps = 5
        config.target_memory_mb = 300
        config.target_model_size_mb = 30
        config.target_accuracy = 0.80
        config.num_threads = 2
        return config


# Export default configuration
DEFAULT_CONFIG = OptimizationConfig()
