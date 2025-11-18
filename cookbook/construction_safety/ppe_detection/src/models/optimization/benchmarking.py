"""
Benchmarking utilities for model optimization.

Measures:
- FPS on different hardware
- Inference latency
- Memory usage
- Accuracy metrics
- Generates performance reports
"""

import logging
import time
import json
import psutil
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import numpy as np

try:
    import cv2
    from ultralytics import YOLO
    import onnxruntime as ort
except ImportError as e:
    logging.warning(f"Some benchmarking dependencies not installed: {e}")

from .optimization_config import OptimizationConfig
from .inference_engine import InferenceEngine

logger = logging.getLogger(__name__)


class PerformanceBenchmark:
    """Comprehensive performance benchmarking for PPE detection models."""

    def __init__(self, config: OptimizationConfig):
        """
        Initialize the benchmark.

        Args:
            config: Optimization configuration
        """
        self.config = config
        self.results: Dict[str, Any] = {}
        self.system_info = self._get_system_info()

    def benchmark_model(
        self,
        model_path: str,
        test_images: List[np.ndarray],
        ground_truth: Optional[List[Dict]] = None,
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run comprehensive benchmark on a model.

        Args:
            model_path: Path to model file
            test_images: List of test images
            ground_truth: Optional ground truth annotations
            model_name: Optional name for the model

        Returns:
            Benchmark results
        """
        if model_name is None:
            model_name = Path(model_path).stem

        logger.info(f"Benchmarking model: {model_name}")
        logger.info(f"Test images: {len(test_images)}")

        results = {
            "model_name": model_name,
            "model_path": str(model_path),
            "timestamp": datetime.now().isoformat(),
            "system_info": self.system_info,
            "config": self._config_to_dict(),
        }

        # Create inference engine
        engine = InferenceEngine(model_path, self.config)

        # 1. Measure FPS and latency
        logger.info("Measuring FPS and latency...")
        fps_results = self._measure_fps(engine, test_images)
        results["fps_metrics"] = fps_results

        # 2. Measure memory usage
        logger.info("Measuring memory usage...")
        memory_results = self._measure_memory(engine, test_images)
        results["memory_metrics"] = memory_results

        # 3. Measure accuracy (if ground truth provided)
        if ground_truth:
            logger.info("Measuring accuracy...")
            accuracy_results = self._measure_accuracy(engine, test_images, ground_truth)
            results["accuracy_metrics"] = accuracy_results

        # 4. Model size
        results["model_size_mb"] = self._get_model_size(model_path)

        # 5. Detailed latency breakdown
        logger.info("Analyzing latency breakdown...")
        latency_breakdown = self._analyze_latency_breakdown(engine, test_images[:10])
        results["latency_breakdown"] = latency_breakdown

        # 6. Validate against targets
        results["target_validation"] = self._validate_targets(results)

        # Store results
        self.results[model_name] = results

        logger.info(f"Benchmark complete for {model_name}")
        self._print_summary(results)

        return results

    def _measure_fps(
        self,
        engine: InferenceEngine,
        test_images: List[np.ndarray]
    ) -> Dict[str, float]:
        """Measure FPS and inference latency."""
        # Warmup
        logger.info(f"Warmup: {self.config.benchmark_warmup_runs} runs")
        for i in range(self.config.benchmark_warmup_runs):
            img = test_images[i % len(test_images)]
            engine.predict(img)

        # Reset counters
        engine.reset_performance_counters()

        # Actual benchmark
        num_runs = min(len(test_images), self.config.benchmark_test_runs)
        logger.info(f"Running benchmark: {num_runs} runs")

        inference_times = []
        start_time = time.perf_counter()

        for i in range(num_runs):
            img = test_images[i % len(test_images)]
            t0 = time.perf_counter()
            engine.predict(img, return_details=False)
            t1 = time.perf_counter()
            inference_times.append(t1 - t0)

        total_time = time.perf_counter() - start_time

        # Calculate statistics
        inference_times = np.array(inference_times)

        return {
            "avg_fps": num_runs / total_time,
            "avg_inference_time_ms": np.mean(inference_times) * 1000,
            "std_inference_time_ms": np.std(inference_times) * 1000,
            "min_inference_time_ms": np.min(inference_times) * 1000,
            "max_inference_time_ms": np.max(inference_times) * 1000,
            "p50_inference_time_ms": np.percentile(inference_times, 50) * 1000,
            "p95_inference_time_ms": np.percentile(inference_times, 95) * 1000,
            "p99_inference_time_ms": np.percentile(inference_times, 99) * 1000,
            "total_time_seconds": total_time,
            "num_runs": num_runs,
        }

    def _measure_memory(
        self,
        engine: InferenceEngine,
        test_images: List[np.ndarray]
    ) -> Dict[str, float]:
        """Measure memory usage during inference."""
        import gc

        # Get process
        process = psutil.Process()

        # Force garbage collection
        gc.collect()

        # Baseline memory
        baseline_memory = process.memory_info().rss / (1024 * 1024)  # MB

        # Run inference and track memory
        memory_samples = []
        num_samples = min(50, len(test_images))

        for i in range(num_samples):
            img = test_images[i % len(test_images)]
            engine.predict(img)

            # Sample memory
            current_memory = process.memory_info().rss / (1024 * 1024)
            memory_samples.append(current_memory)

        # Force cleanup
        engine.clear_cache()
        gc.collect()

        # Final memory
        final_memory = process.memory_info().rss / (1024 * 1024)

        memory_samples = np.array(memory_samples)

        return {
            "baseline_memory_mb": baseline_memory,
            "avg_memory_mb": np.mean(memory_samples),
            "max_memory_mb": np.max(memory_samples),
            "min_memory_mb": np.min(memory_samples),
            "final_memory_mb": final_memory,
            "memory_increase_mb": final_memory - baseline_memory,
            "peak_memory_mb": np.max(memory_samples),
        }

    def _measure_accuracy(
        self,
        engine: InferenceEngine,
        test_images: List[np.ndarray],
        ground_truth: List[Dict]
    ) -> Dict[str, float]:
        """
        Measure accuracy metrics.

        Args:
            engine: Inference engine
            test_images: Test images
            ground_truth: Ground truth annotations

        Returns:
            Accuracy metrics
        """
        if len(test_images) != len(ground_truth):
            logger.warning("Test images and ground truth length mismatch")
            return {}

        # Run inference on all test images
        predictions = []
        for img in test_images:
            result = engine.predict(img)
            predictions.append(result["detections"])

        # Calculate metrics
        metrics = self._calculate_detection_metrics(predictions, ground_truth)

        return metrics

    def _calculate_detection_metrics(
        self,
        predictions: List[List[Dict]],
        ground_truth: List[Dict]
    ) -> Dict[str, float]:
        """Calculate detection metrics (precision, recall, mAP)."""
        # Simplified metrics calculation
        # In practice, you would use more sophisticated metrics like COCO mAP

        total_tp = 0
        total_fp = 0
        total_fn = 0
        total_detections = 0
        total_ground_truth = 0

        iou_threshold = 0.5

        for pred_boxes, gt_boxes in zip(predictions, ground_truth):
            total_detections += len(pred_boxes)
            total_ground_truth += len(gt_boxes.get("boxes", []))

            # Match predictions to ground truth
            matched_gt = set()

            for pred in pred_boxes:
                pred_bbox = pred["bbox"]
                best_iou = 0
                best_gt_idx = -1

                # Find best matching ground truth box
                for gt_idx, gt_box in enumerate(gt_boxes.get("boxes", [])):
                    iou = self._calculate_iou(pred_bbox, gt_box)
                    if iou > best_iou:
                        best_iou = iou
                        best_gt_idx = gt_idx

                # Check if match is good enough
                if best_iou >= iou_threshold and best_gt_idx not in matched_gt:
                    total_tp += 1
                    matched_gt.add(best_gt_idx)
                else:
                    total_fp += 1

            # Count missed ground truth boxes
            total_fn += len(gt_boxes.get("boxes", [])) - len(matched_gt)

        # Calculate metrics
        precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
        recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "mAP_50": f1_score,  # Simplified mAP approximation
            "total_detections": total_detections,
            "total_ground_truth": total_ground_truth,
            "true_positives": total_tp,
            "false_positives": total_fp,
            "false_negatives": total_fn,
        }

    def _calculate_iou(self, box1: List[float], box2: List[float]) -> float:
        """Calculate Intersection over Union (IoU) between two boxes."""
        x1_min, y1_min, x1_max, y1_max = box1
        x2_min, y2_min, x2_max, y2_max = box2

        # Calculate intersection
        x_min = max(x1_min, x2_min)
        y_min = max(y1_min, y2_min)
        x_max = min(x1_max, x2_max)
        y_max = min(y1_max, y2_max)

        if x_max < x_min or y_max < y_min:
            return 0.0

        intersection = (x_max - x_min) * (y_max - y_min)

        # Calculate union
        area1 = (x1_max - x1_min) * (y1_max - y1_min)
        area2 = (x2_max - x2_min) * (y2_max - y2_min)
        union = area1 + area2 - intersection

        return intersection / union if union > 0 else 0.0

    def _analyze_latency_breakdown(
        self,
        engine: InferenceEngine,
        test_images: List[np.ndarray]
    ) -> Dict[str, float]:
        """Analyze latency breakdown (preprocessing, inference, postprocessing)."""
        preprocessing_times = []
        inference_times = []
        total_times = []

        for img in test_images:
            # Measure preprocessing
            t0 = time.perf_counter()
            preprocessed = engine.preprocess(img)
            t1 = time.perf_counter()
            preprocessing_times.append(t1 - t0)

            # Measure total time
            t0 = time.perf_counter()
            engine.predict(img)
            t1 = time.perf_counter()
            total_times.append(t1 - t0)

        # Get inference times from engine
        if engine.inference_times:
            inference_times = list(engine.inference_times)[-len(test_images):]
        else:
            inference_times = [0] * len(test_images)

        return {
            "avg_preprocessing_ms": np.mean(preprocessing_times) * 1000,
            "avg_inference_ms": np.mean(inference_times) * 1000,
            "avg_total_ms": np.mean(total_times) * 1000,
            "preprocessing_percent": (np.mean(preprocessing_times) / np.mean(total_times)) * 100 if np.mean(total_times) > 0 else 0,
            "inference_percent": (np.mean(inference_times) / np.mean(total_times)) * 100 if np.mean(total_times) > 0 else 0,
        }

    def _validate_targets(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate results against optimization targets."""
        fps = results.get("fps_metrics", {}).get("avg_fps", 0)
        memory = results.get("memory_metrics", {}).get("peak_memory_mb", float('inf'))
        model_size = results.get("model_size_mb", float('inf'))
        accuracy = results.get("accuracy_metrics", {}).get("mAP_50", 0)

        metrics = {
            "fps": fps,
            "memory_mb": memory,
            "model_size_mb": model_size,
            "accuracy": accuracy,
        }

        validations = self.config.validate_targets(metrics)

        return {
            "targets_met": validations,
            "all_targets_met": all(validations.values()),
            "targets": {
                "fps": self.config.target_fps,
                "memory_mb": self.config.target_memory_mb,
                "model_size_mb": self.config.target_model_size_mb,
                "accuracy": self.config.target_accuracy,
            },
            "actual": metrics,
        }

    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        import cpuinfo

        try:
            cpu_info = cpuinfo.get_cpu_info()
            cpu_name = cpu_info.get('brand_raw', 'Unknown')
        except:
            cpu_name = platform.processor()

        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": cpu_name,
            "cpu_count": psutil.cpu_count(logical=False),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "total_memory_gb": psutil.virtual_memory().total / (1024**3),
            "python_version": platform.python_version(),
        }

    def _get_model_size(self, model_path: str) -> float:
        """Get model size in MB."""
        path = Path(model_path)
        if path.exists():
            return path.stat().st_size / (1024 * 1024)
        return 0.0

    def _config_to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "optimization_level": self.config.level.name,
            "input_size": self.config.input_size,
            "batch_size": self.config.batch_size,
            "frame_skip": self.config.frame_skip,
            "device": self.config.device,
            "num_threads": self.config.num_threads,
        }

    def _print_summary(self, results: Dict[str, Any]):
        """Print benchmark summary."""
        print("\n" + "=" * 60)
        print(f"BENCHMARK SUMMARY: {results['model_name']}")
        print("=" * 60)

        # FPS metrics
        fps_metrics = results.get("fps_metrics", {})
        print(f"\nPerformance:")
        print(f"  Average FPS: {fps_metrics.get('avg_fps', 0):.2f}")
        print(f"  Avg Latency: {fps_metrics.get('avg_inference_time_ms', 0):.2f} ms")
        print(f"  P95 Latency: {fps_metrics.get('p95_inference_time_ms', 0):.2f} ms")

        # Memory metrics
        memory_metrics = results.get("memory_metrics", {})
        print(f"\nMemory:")
        print(f"  Peak Memory: {memory_metrics.get('peak_memory_mb', 0):.2f} MB")
        print(f"  Avg Memory: {memory_metrics.get('avg_memory_mb', 0):.2f} MB")

        # Model size
        print(f"\nModel Size:")
        print(f"  {results.get('model_size_mb', 0):.2f} MB")

        # Accuracy (if available)
        if "accuracy_metrics" in results:
            acc_metrics = results["accuracy_metrics"]
            print(f"\nAccuracy:")
            print(f"  Precision: {acc_metrics.get('precision', 0):.3f}")
            print(f"  Recall: {acc_metrics.get('recall', 0):.3f}")
            print(f"  F1 Score: {acc_metrics.get('f1_score', 0):.3f}")

        # Target validation
        validation = results.get("target_validation", {})
        print(f"\nTarget Validation:")
        targets_met = validation.get("targets_met", {})
        for target, met in targets_met.items():
            status = "✓" if met else "✗"
            actual = validation.get("actual", {}).get(target, 0)
            target_val = validation.get("targets", {}).get(target, 0)
            print(f"  {status} {target}: {actual:.2f} (target: {target_val:.2f})")

        print("\n" + "=" * 60 + "\n")

    def compare_models(
        self,
        model_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare multiple benchmarked models.

        Args:
            model_names: List of model names to compare (default: all)

        Returns:
            Comparison results
        """
        if model_names is None:
            model_names = list(self.results.keys())

        if len(model_names) < 2:
            logger.warning("Need at least 2 models to compare")
            return {}

        comparison = {
            "models": model_names,
            "metrics": {}
        }

        # Compare each metric
        metrics_to_compare = [
            ("fps_metrics", "avg_fps"),
            ("fps_metrics", "avg_inference_time_ms"),
            ("memory_metrics", "peak_memory_mb"),
            ("model_size_mb", None),
        ]

        for metric_path in metrics_to_compare:
            if len(metric_path) == 2 and metric_path[1]:
                category, metric = metric_path
                key = f"{category}.{metric}"
            else:
                category = metric_path[0]
                metric = None
                key = category

            values = []
            for model_name in model_names:
                if model_name in self.results:
                    result = self.results[model_name]
                    if metric:
                        value = result.get(category, {}).get(metric, 0)
                    else:
                        value = result.get(category, 0)
                    values.append(value)
                else:
                    values.append(None)

            comparison["metrics"][key] = dict(zip(model_names, values))

        return comparison

    def generate_report(
        self,
        output_path: str,
        include_charts: bool = True
    ):
        """
        Generate comprehensive benchmark report.

        Args:
            output_path: Path to save report (JSON file)
            include_charts: Include performance charts (requires matplotlib)
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        report = {
            "timestamp": datetime.now().isoformat(),
            "system_info": self.system_info,
            "config": self._config_to_dict(),
            "results": self.results,
        }

        # Add comparison if multiple models
        if len(self.results) > 1:
            report["comparison"] = self.compare_models()

        # Save JSON report
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report saved to: {output_path}")

        # Generate charts if requested
        if include_charts:
            try:
                self._generate_charts(output_path.parent)
            except Exception as e:
                logger.warning(f"Could not generate charts: {e}")

    def _generate_charts(self, output_dir: Path):
        """Generate performance charts."""
        try:
            import matplotlib.pyplot as plt

            if not self.results:
                return

            # FPS comparison chart
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))

            model_names = list(self.results.keys())

            # 1. FPS comparison
            fps_values = [self.results[m]["fps_metrics"]["avg_fps"] for m in model_names]
            axes[0, 0].bar(model_names, fps_values)
            axes[0, 0].set_title("Average FPS")
            axes[0, 0].set_ylabel("FPS")
            axes[0, 0].axhline(y=self.config.target_fps, color='r', linestyle='--', label='Target')
            axes[0, 0].legend()

            # 2. Latency comparison
            latency_values = [self.results[m]["fps_metrics"]["avg_inference_time_ms"] for m in model_names]
            axes[0, 1].bar(model_names, latency_values)
            axes[0, 1].set_title("Average Latency")
            axes[0, 1].set_ylabel("Milliseconds")

            # 3. Memory usage
            memory_values = [self.results[m]["memory_metrics"]["peak_memory_mb"] for m in model_names]
            axes[1, 0].bar(model_names, memory_values)
            axes[1, 0].set_title("Peak Memory Usage")
            axes[1, 0].set_ylabel("MB")
            axes[1, 0].axhline(y=self.config.target_memory_mb, color='r', linestyle='--', label='Target')
            axes[1, 0].legend()

            # 4. Model size
            size_values = [self.results[m]["model_size_mb"] for m in model_names]
            axes[1, 1].bar(model_names, size_values)
            axes[1, 1].set_title("Model Size")
            axes[1, 1].set_ylabel("MB")
            axes[1, 1].axhline(y=self.config.target_model_size_mb, color='r', linestyle='--', label='Target')
            axes[1, 1].legend()

            plt.tight_layout()
            plt.savefig(output_dir / "benchmark_comparison.png", dpi=150)
            plt.close()

            logger.info(f"Charts saved to: {output_dir}/benchmark_comparison.png")

        except ImportError:
            logger.warning("matplotlib not installed, skipping chart generation")
