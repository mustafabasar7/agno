"""
Configuration for PPE Detection Models

This module contains all configuration settings for the PPE detection system,
including model paths, class mappings, detection thresholds, and preprocessing parameters.
"""

from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, field


@dataclass
class ModelConfig:
    """Configuration class for PPE detection model settings."""

    # Model paths
    model_dir: Path = Path(__file__).parent.parent.parent / "models" / "weights"
    default_model_name: str = "yolov8n.pt"  # Nano model for faster CPU inference
    custom_model_name: str = "ppe_detector_best.pt"  # Fine-tuned model if available

    # Model architecture options: yolov8n, yolov8s, yolov8m, yolov8l, yolov8x
    # or yolov11n, yolov11s, yolov11m, yolov11l, yolov11x
    model_architecture: str = "yolov8n"  # Use nano for CPU efficiency

    # Device configuration
    device: str = "cpu"  # Force CPU-only inference (no GPU required)

    # Class mappings (PPE equipment classes)
    # Standard COCO person class + custom PPE classes
    class_names: Dict[int, str] = field(default_factory=lambda: {
        0: "helmet",      # Safety helmet (baret)
        1: "vest",        # Safety vest (yolek)
        2: "person",      # Person detection
        3: "no-helmet",   # Person without helmet (optional)
        4: "no-vest"      # Person without vest (optional)
    })

    # Reverse mapping for convenience
    @property
    def name_to_class(self) -> Dict[str, int]:
        """Returns reverse mapping from class names to IDs."""
        return {v: k for k, v in self.class_names.items()}

    # Detection thresholds
    confidence_threshold: float = 0.5  # Minimum confidence for detection
    nms_threshold: float = 0.45  # Non-maximum suppression threshold

    # Production thresholds (more conservative)
    production_confidence_threshold: float = 0.6
    production_nms_threshold: float = 0.4

    # Compliance checking thresholds
    compliance_confidence_threshold: float = 0.55  # Higher threshold for compliance
    iou_threshold: float = 0.3  # IoU threshold for person-PPE association

    # Input image settings
    input_size: Tuple[int, int] = (640, 640)  # Standard YOLO input size
    max_detection_size: Tuple[int, int] = (1280, 1280)  # Max size for high-res images

    # Preprocessing settings
    normalize_mean: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    normalize_std: Tuple[float, float, float] = (255.0, 255.0, 255.0)

    # Video processing settings
    video_frame_skip: int = 0  # Process every Nth frame (0 = process all frames)
    video_batch_size: int = 1  # Number of frames to process in batch

    # Visualization settings
    bbox_thickness: int = 2
    bbox_colors: Dict[str, Tuple[int, int, int]] = field(default_factory=lambda: {
        "helmet": (0, 255, 0),      # Green for helmet
        "vest": (0, 165, 255),       # Orange for vest
        "person": (255, 0, 0),       # Blue for person
        "no-helmet": (0, 0, 255),    # Red for no helmet
        "no-vest": (0, 0, 255),      # Red for no vest
        "compliant": (0, 255, 0),    # Green for compliant
        "non-compliant": (0, 0, 255) # Red for non-compliant
    })

    font_scale: float = 0.6
    font_thickness: int = 2
    label_background_alpha: float = 0.5

    # Model training/fine-tuning settings (for future use)
    training_config: Dict = field(default_factory=lambda: {
        "epochs": 100,
        "batch_size": 16,
        "learning_rate": 0.01,
        "image_size": 640,
        "augmentation": True,
        "patience": 20,  # Early stopping patience
        "save_period": 10  # Save checkpoint every N epochs
    })

    # Data augmentation settings (for training)
    augmentation_config: Dict = field(default_factory=lambda: {
        "hsv_h": 0.015,  # HSV-Hue augmentation
        "hsv_s": 0.7,    # HSV-Saturation augmentation
        "hsv_v": 0.4,    # HSV-Value augmentation
        "degrees": 0.0,  # Rotation degrees
        "translate": 0.1,  # Translation
        "scale": 0.5,    # Scaling
        "shear": 0.0,    # Shear
        "perspective": 0.0,  # Perspective
        "flipud": 0.0,   # Flip up-down probability
        "fliplr": 0.5,   # Flip left-right probability
        "mosaic": 1.0,   # Mosaic augmentation
        "mixup": 0.0     # Mixup augmentation
    })

    def get_model_path(self, use_custom: bool = False) -> Path:
        """
        Get the full path to the model file.

        Args:
            use_custom: If True, return path to custom fine-tuned model

        Returns:
            Path object pointing to the model file
        """
        self.model_dir.mkdir(parents=True, exist_ok=True)

        if use_custom:
            custom_path = self.model_dir / self.custom_model_name
            if custom_path.exists():
                return custom_path
            else:
                print(f"Custom model not found at {custom_path}, using default model")

        return self.model_dir / self.default_model_name

    def validate_thresholds(self) -> bool:
        """Validate that all thresholds are within valid ranges."""
        try:
            assert 0 < self.confidence_threshold <= 1, "Confidence threshold must be between 0 and 1"
            assert 0 < self.nms_threshold <= 1, "NMS threshold must be between 0 and 1"
            assert 0 < self.compliance_confidence_threshold <= 1, "Compliance threshold must be between 0 and 1"
            assert 0 < self.iou_threshold <= 1, "IoU threshold must be between 0 and 1"
            return True
        except AssertionError as e:
            print(f"Validation error: {e}")
            return False

    def update_for_production(self) -> None:
        """Update configuration for production use with more conservative thresholds."""
        self.confidence_threshold = self.production_confidence_threshold
        self.nms_threshold = self.production_nms_threshold
        print("Configuration updated for production mode")

    def get_summary(self) -> str:
        """Get a summary of current configuration."""
        summary = f"""
PPE Detection Model Configuration:
{'='*50}
Model: {self.model_architecture}
Device: {self.device}
Input Size: {self.input_size}
Confidence Threshold: {self.confidence_threshold}
NMS Threshold: {self.nms_threshold}
Classes: {', '.join(self.class_names.values())}
Model Path: {self.get_model_path()}
{'='*50}
        """
        return summary.strip()


# Default configuration instance
default_config = ModelConfig()


# Configuration presets for different use cases
class ConfigPresets:
    """Predefined configuration presets for different scenarios."""

    @staticmethod
    def fast_inference() -> ModelConfig:
        """Configuration optimized for fast CPU inference."""
        config = ModelConfig()
        config.model_architecture = "yolov8n"  # Nano model
        config.input_size = (416, 416)  # Smaller input for speed
        config.confidence_threshold = 0.5
        return config

    @staticmethod
    def high_accuracy() -> ModelConfig:
        """Configuration optimized for accuracy (slower)."""
        config = ModelConfig()
        config.model_architecture = "yolov8m"  # Medium model
        config.input_size = (640, 640)
        config.confidence_threshold = 0.6
        config.nms_threshold = 0.4
        return config

    @staticmethod
    def video_processing() -> ModelConfig:
        """Configuration optimized for video processing."""
        config = ModelConfig()
        config.model_architecture = "yolov8n"
        config.input_size = (640, 640)
        config.video_frame_skip = 2  # Process every 3rd frame
        config.confidence_threshold = 0.55
        return config

    @staticmethod
    def production() -> ModelConfig:
        """Production-ready configuration."""
        config = ModelConfig()
        config.model_architecture = "yolov8s"  # Small model for balance
        config.confidence_threshold = config.production_confidence_threshold
        config.nms_threshold = config.production_nms_threshold
        return config


if __name__ == "__main__":
    # Example usage and testing
    config = default_config
    print(config.get_summary())
    print(f"\nThresholds valid: {config.validate_thresholds()}")

    print("\n" + "="*50)
    print("Production Config:")
    prod_config = ConfigPresets.production()
    print(prod_config.get_summary())
