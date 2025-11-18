"""
Model optimizer for converting YOLO models to optimized formats.

Supports:
- YOLO to ONNX conversion
- INT8 quantization
- Model pruning
- Accuracy comparison
- Benchmarking
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

try:
    from ultralytics import YOLO
    import onnx
    import onnxruntime as ort
    from onnxruntime.quantization import quantize_dynamic, quantize_static, QuantType
    from onnxruntime.quantization import CalibrationDataReader
except ImportError as e:
    logging.warning(f"Some optimization dependencies not installed: {e}")

from .optimization_config import OptimizationConfig, OptimizationLevel, QuantizationType

logger = logging.getLogger(__name__)


class ModelOptimizer:
    """Optimizes YOLO models for deployment."""

    def __init__(self, config: OptimizationConfig):
        """
        Initialize the model optimizer.

        Args:
            config: Optimization configuration
        """
        self.config = config
        self.original_model_path: Optional[Path] = None
        self.optimized_model_path: Optional[Path] = None
        self.optimization_metrics: Dict[str, Any] = {}

    def optimize_model(
        self,
        model_path: str,
        output_dir: str,
        calibration_data: Optional[List[np.ndarray]] = None
    ) -> Dict[str, Any]:
        """
        Optimize a YOLO model based on configuration.

        Args:
            model_path: Path to the original YOLO model (.pt file)
            output_dir: Directory to save optimized models
            calibration_data: Calibration data for static quantization

        Returns:
            Dictionary with optimization results and paths
        """
        self.original_model_path = Path(model_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        results = {
            "original_model": str(self.original_model_path),
            "optimization_level": self.config.level.name,
            "optimizations_applied": []
        }

        logger.info(f"Starting optimization at level: {self.config.level.name}")
        logger.info(f"Input size: {self.config.input_size}")

        # Level 1: Basic optimization (smaller input size)
        if self.config.level.value >= OptimizationLevel.LEVEL_1_BASIC.value:
            logger.info("Level 1: Using smaller input size")
            results["optimizations_applied"].append("smaller_input_size")
            results["input_size"] = self.config.input_size

        # Level 2: ONNX conversion
        if self.config.level.value >= OptimizationLevel.LEVEL_2_ONNX.value:
            logger.info("Level 2: Converting to ONNX")
            onnx_path = self._convert_to_onnx(model_path, output_dir)
            results["onnx_model"] = str(onnx_path)
            results["optimizations_applied"].append("onnx_conversion")
            self.optimized_model_path = onnx_path

        # Level 3: Quantization
        if self.config.level.value >= OptimizationLevel.LEVEL_3_QUANTIZATION.value:
            logger.info("Level 3: Applying quantization")
            if self.optimized_model_path and self.optimized_model_path.suffix == ".onnx":
                quantized_path = self._quantize_model(
                    self.optimized_model_path,
                    output_dir,
                    calibration_data
                )
                results["quantized_model"] = str(quantized_path)
                results["optimizations_applied"].append("quantization")
                results["quantization_type"] = self.config.quantization_type.value
                self.optimized_model_path = quantized_path

        # Level 4: Pruning
        if self.config.level.value >= OptimizationLevel.LEVEL_4_PRUNING.value:
            logger.info("Level 4: Applying model pruning")
            # Note: Pruning typically requires retraining, so this is a placeholder
            logger.warning("Model pruning requires retraining and is not fully implemented")
            results["optimizations_applied"].append("pruning_placeholder")

        # Calculate model sizes
        original_size = self._get_model_size(self.original_model_path)
        optimized_size = self._get_model_size(self.optimized_model_path) if self.optimized_model_path else original_size

        results["original_size_mb"] = original_size
        results["optimized_size_mb"] = optimized_size
        results["size_reduction_percent"] = ((original_size - optimized_size) / original_size) * 100

        logger.info(f"Optimization complete. Size reduced by {results['size_reduction_percent']:.2f}%")

        self.optimization_metrics = results
        return results

    def _convert_to_onnx(self, model_path: str, output_dir: Path) -> Path:
        """
        Convert YOLO model to ONNX format.

        Args:
            model_path: Path to YOLO .pt file
            output_dir: Output directory

        Returns:
            Path to ONNX model
        """
        try:
            model = YOLO(model_path)

            # Generate output filename
            model_name = Path(model_path).stem
            onnx_path = output_dir / f"{model_name}_optimized.onnx"

            logger.info(f"Exporting YOLO model to ONNX: {onnx_path}")

            # Export to ONNX
            model.export(
                format="onnx",
                imgsz=self.config.input_size[0],  # YOLO uses single int for square images
                opset=self.config.onnx_opset_version,
                simplify=self.config.onnx_simplify,
                dynamic=self.config.onnx_dynamic_axes,
            )

            # The export creates the file with a specific name pattern
            # Move it to our desired location
            exported_path = Path(model_path).parent / f"{model_name}.onnx"
            if exported_path.exists():
                import shutil
                shutil.move(str(exported_path), str(onnx_path))

            # Verify ONNX model
            if onnx_path.exists():
                onnx_model = onnx.load(str(onnx_path))
                onnx.checker.check_model(onnx_model)
                logger.info("ONNX model verified successfully")

            return onnx_path

        except Exception as e:
            logger.error(f"ONNX conversion failed: {e}")
            raise

    def _quantize_model(
        self,
        onnx_path: Path,
        output_dir: Path,
        calibration_data: Optional[List[np.ndarray]] = None
    ) -> Path:
        """
        Quantize ONNX model to INT8.

        Args:
            onnx_path: Path to ONNX model
            output_dir: Output directory
            calibration_data: Calibration data for static quantization

        Returns:
            Path to quantized model
        """
        model_name = onnx_path.stem
        quantized_path = output_dir / f"{model_name}_quantized.onnx"

        try:
            if self.config.quantization_type == QuantizationType.DYNAMIC:
                logger.info("Applying dynamic quantization (weights only)")
                quantize_dynamic(
                    model_input=str(onnx_path),
                    model_output=str(quantized_path),
                    weight_type=QuantType.QUInt8,
                    per_channel=self.config.quantization_per_channel,
                )

            elif self.config.quantization_type == QuantizationType.STATIC:
                logger.info("Applying static quantization (weights + activations)")
                if calibration_data is None:
                    logger.warning("No calibration data provided, falling back to dynamic quantization")
                    return self._quantize_model(onnx_path, output_dir, None)

                # Create calibration data reader
                data_reader = PPECalibrationDataReader(
                    calibration_data,
                    self.config.input_size
                )

                quantize_static(
                    model_input=str(onnx_path),
                    model_output=str(quantized_path),
                    calibration_data_reader=data_reader,
                    weight_type=QuantType.QInt8,
                    per_channel=self.config.quantization_per_channel,
                )

            else:
                logger.error(f"Unsupported quantization type: {self.config.quantization_type}")
                return onnx_path

            logger.info(f"Quantized model saved to: {quantized_path}")
            return quantized_path

        except Exception as e:
            logger.error(f"Quantization failed: {e}")
            logger.warning("Returning original ONNX model")
            return onnx_path

    def _get_model_size(self, model_path: Optional[Path]) -> float:
        """Get model size in MB."""
        if model_path is None or not model_path.exists():
            return 0.0
        return model_path.stat().st_size / (1024 * 1024)

    def compare_models(
        self,
        original_model_path: str,
        optimized_model_path: str,
        test_images: List[np.ndarray],
        ground_truth: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """
        Compare original and optimized models.

        Args:
            original_model_path: Path to original YOLO model
            optimized_model_path: Path to optimized model
            test_images: List of test images
            ground_truth: Optional ground truth labels

        Returns:
            Comparison metrics
        """
        logger.info("Comparing original and optimized models...")

        results = {
            "original": {},
            "optimized": {},
            "comparison": {}
        }

        # Benchmark original model
        logger.info("Benchmarking original model...")
        original_metrics = self._benchmark_model(original_model_path, test_images, is_onnx=False)
        results["original"] = original_metrics

        # Benchmark optimized model
        logger.info("Benchmarking optimized model...")
        optimized_metrics = self._benchmark_model(optimized_model_path, test_images, is_onnx=True)
        results["optimized"] = optimized_metrics

        # Calculate improvements
        if original_metrics["avg_inference_time"] > 0:
            speedup = original_metrics["avg_inference_time"] / optimized_metrics["avg_inference_time"]
            fps_improvement = (optimized_metrics["fps"] - original_metrics["fps"]) / original_metrics["fps"] * 100
        else:
            speedup = 0
            fps_improvement = 0

        results["comparison"] = {
            "speedup_factor": speedup,
            "fps_improvement_percent": fps_improvement,
            "size_reduction_mb": results["original"]["model_size_mb"] - results["optimized"]["model_size_mb"],
            "size_reduction_percent": (
                (results["original"]["model_size_mb"] - results["optimized"]["model_size_mb"]) /
                results["original"]["model_size_mb"] * 100
            ) if results["original"]["model_size_mb"] > 0 else 0
        }

        logger.info(f"Speedup: {speedup:.2f}x")
        logger.info(f"FPS improvement: {fps_improvement:.2f}%")

        return results

    def _benchmark_model(
        self,
        model_path: str,
        test_images: List[np.ndarray],
        is_onnx: bool = False
    ) -> Dict[str, float]:
        """Benchmark a model on test images."""
        path = Path(model_path)

        # Warmup
        logger.info(f"Warming up model ({self.config.benchmark_warmup_runs} runs)...")
        if is_onnx:
            session = ort.InferenceSession(str(path), providers=['CPUExecutionProvider'])
            for _ in range(self.config.benchmark_warmup_runs):
                if test_images:
                    img = self._preprocess_image(test_images[0])
                    session.run(None, {session.get_inputs()[0].name: img})
        else:
            model = YOLO(model_path)
            for _ in range(self.config.benchmark_warmup_runs):
                if test_images:
                    model(test_images[0], verbose=False)

        # Actual benchmark
        inference_times = []
        num_runs = min(len(test_images), self.config.benchmark_test_runs)

        logger.info(f"Running benchmark ({num_runs} runs)...")
        for i in range(num_runs):
            img = test_images[i % len(test_images)]

            start_time = time.perf_counter()
            if is_onnx:
                processed_img = self._preprocess_image(img)
                session.run(None, {session.get_inputs()[0].name: processed_img})
            else:
                model(img, verbose=False)
            end_time = time.perf_counter()

            inference_times.append(end_time - start_time)

        avg_time = np.mean(inference_times)
        std_time = np.std(inference_times)
        fps = 1.0 / avg_time if avg_time > 0 else 0

        return {
            "avg_inference_time": avg_time,
            "std_inference_time": std_time,
            "min_inference_time": np.min(inference_times),
            "max_inference_time": np.max(inference_times),
            "fps": fps,
            "model_size_mb": self._get_model_size(path),
            "num_runs": num_runs
        }

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for ONNX inference."""
        import cv2

        # Resize to input size
        img = cv2.resize(image, self.config.input_size)

        # Convert BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Normalize to [0, 1]
        img = img.astype(np.float32) / 255.0

        # Transpose to CHW format
        img = np.transpose(img, (2, 0, 1))

        # Add batch dimension
        img = np.expand_dims(img, axis=0)

        return img


class PPECalibrationDataReader(CalibrationDataReader):
    """Calibration data reader for static quantization."""

    def __init__(self, calibration_images: List[np.ndarray], input_size: Tuple[int, int]):
        """
        Initialize calibration data reader.

        Args:
            calibration_images: List of calibration images
            input_size: Model input size
        """
        self.calibration_images = calibration_images
        self.input_size = input_size
        self.current_index = 0

    def get_next(self) -> Optional[Dict[str, np.ndarray]]:
        """Get next calibration sample."""
        if self.current_index >= len(self.calibration_images):
            return None

        image = self.calibration_images[self.current_index]
        self.current_index += 1

        # Preprocess image
        processed = self._preprocess(image)

        return {"images": processed}

    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        """Preprocess calibration image."""
        import cv2

        img = cv2.resize(image, self.input_size)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))
        img = np.expand_dims(img, axis=0)

        return img
