"""
Optimized inference engine for PPE detection.

Features:
- ONNX Runtime for fast CPU inference
- Batch processing support
- Frame skipping for video streams
- Efficient preprocessing pipeline
- Memory management
"""

import logging
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any, Union
from collections import deque
import numpy as np

try:
    import cv2
    import onnxruntime as ort
    from ultralytics import YOLO
except ImportError as e:
    logging.warning(f"Some inference dependencies not installed: {e}")

from .optimization_config import OptimizationConfig

logger = logging.getLogger(__name__)


class InferenceEngine:
    """Optimized inference engine for PPE detection."""

    def __init__(self, model_path: str, config: OptimizationConfig):
        """
        Initialize the inference engine.

        Args:
            model_path: Path to model file (.pt or .onnx)
            config: Optimization configuration
        """
        self.model_path = Path(model_path)
        self.config = config
        self.model = None
        self.session = None
        self.is_onnx = self.model_path.suffix == ".onnx"

        # Frame skipping state
        self.frame_counter = 0
        self.last_results = None

        # Batch processing
        self.batch_buffer: deque = deque(maxlen=config.batch_size)

        # Performance tracking
        self.inference_times: deque = deque(maxlen=100)
        self.preprocessing_times: deque = deque(maxlen=100)

        # Memory management
        self.cache_size = 10
        self.result_cache: deque = deque(maxlen=self.cache_size)

        self._load_model()

    def _load_model(self):
        """Load the model based on file type."""
        logger.info(f"Loading model from: {self.model_path}")

        if self.is_onnx:
            self._load_onnx_model()
        else:
            self._load_yolo_model()

        logger.info(f"Model loaded successfully. Type: {'ONNX' if self.is_onnx else 'YOLO'}")

    def _load_onnx_model(self):
        """Load ONNX model with optimized settings."""
        # Configure session options
        sess_options = ort.SessionOptions()
        sess_options.intra_op_num_threads = self.config.num_threads
        sess_options.inter_op_num_threads = self.config.num_threads
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        # Enable optimizations
        sess_options.enable_cpu_mem_arena = True
        sess_options.enable_mem_pattern = True

        # Choose execution provider
        providers = ['CPUExecutionProvider']
        if 'cuda' in self.config.device.lower():
            providers.insert(0, 'CUDAExecutionProvider')

        self.session = ort.InferenceSession(
            str(self.model_path),
            sess_options=sess_options,
            providers=providers
        )

        # Get input/output names
        self.input_name = self.session.get_inputs()[0].name
        self.output_names = [output.name for output in self.session.get_outputs()]

        logger.info(f"ONNX Runtime initialized with providers: {self.session.get_providers()}")

    def _load_yolo_model(self):
        """Load YOLO model."""
        self.model = YOLO(str(self.model_path))
        logger.info("YOLO model loaded")

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for inference.

        Args:
            image: Input image (BGR format from OpenCV)

        Returns:
            Preprocessed image tensor
        """
        start_time = time.perf_counter()

        # Resize to input size
        img = cv2.resize(image, self.config.input_size, interpolation=cv2.INTER_LINEAR)

        if self.is_onnx:
            # ONNX preprocessing
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = img.astype(np.float32) / 255.0
            img = np.transpose(img, (2, 0, 1))
            img = np.expand_dims(img, axis=0)
        # YOLO handles preprocessing internally

        self.preprocessing_times.append(time.perf_counter() - start_time)

        return img

    def preprocess_batch(self, images: List[np.ndarray]) -> np.ndarray:
        """
        Preprocess a batch of images.

        Args:
            images: List of input images

        Returns:
            Batched image tensor
        """
        if self.is_onnx:
            preprocessed = [self.preprocess(img) for img in images]
            return np.concatenate(preprocessed, axis=0)
        else:
            # YOLO can handle list of images directly
            return images

    def predict(self, image: np.ndarray, return_details: bool = False) -> Dict[str, Any]:
        """
        Run inference on a single image.

        Args:
            image: Input image
            return_details: Return detailed results including timing

        Returns:
            Detection results
        """
        # Frame skipping logic
        if self.config.enable_frame_skip and self.frame_counter % self.config.frame_skip != 0:
            self.frame_counter += 1
            if self.last_results is not None:
                return self.last_results
            # If no cached results, process anyway
        self.frame_counter += 1

        # Preprocess
        processed_img = self.preprocess(image)

        # Inference
        start_time = time.perf_counter()

        if self.is_onnx:
            results = self._run_onnx_inference(processed_img)
        else:
            results = self._run_yolo_inference(image)

        inference_time = time.perf_counter() - start_time
        self.inference_times.append(inference_time)

        # Post-process results
        detections = self._postprocess_results(results, image.shape)

        output = {
            "detections": detections,
            "frame_number": self.frame_counter,
        }

        if return_details:
            output.update({
                "inference_time": inference_time,
                "preprocessing_time": self.preprocessing_times[-1] if self.preprocessing_times else 0,
                "fps": self.get_current_fps(),
            })

        # Cache results for frame skipping
        self.last_results = output
        self.result_cache.append(output)

        return output

    def predict_batch(
        self,
        images: List[np.ndarray],
        return_details: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Run inference on a batch of images.

        Args:
            images: List of input images
            return_details: Return detailed results

        Returns:
            List of detection results
        """
        if not images:
            return []

        # Preprocess batch
        processed_batch = self.preprocess_batch(images)

        # Inference
        start_time = time.perf_counter()

        if self.is_onnx:
            batch_results = self._run_onnx_inference(processed_batch)
        else:
            # YOLO can process list directly
            batch_results = self.model(images, verbose=False)

        inference_time = time.perf_counter() - start_time
        avg_time_per_image = inference_time / len(images)

        # Post-process each result
        results = []
        for i, image in enumerate(images):
            if self.is_onnx:
                # Extract results for this image from batch
                img_results = self._extract_batch_result(batch_results, i)
            else:
                img_results = batch_results[i]

            detections = self._postprocess_results(img_results, image.shape)

            output = {
                "detections": detections,
                "batch_index": i,
            }

            if return_details:
                output.update({
                    "inference_time": avg_time_per_image,
                    "total_batch_time": inference_time,
                })

            results.append(output)

        return results

    def _run_onnx_inference(self, input_tensor: np.ndarray) -> Any:
        """Run ONNX inference."""
        outputs = self.session.run(
            self.output_names,
            {self.input_name: input_tensor}
        )
        return outputs

    def _run_yolo_inference(self, image: np.ndarray) -> Any:
        """Run YOLO inference."""
        results = self.model(image, verbose=False, imgsz=self.config.input_size[0])
        return results[0]  # Single image

    def _postprocess_results(self, results: Any, original_shape: Tuple[int, int, int]) -> List[Dict[str, Any]]:
        """
        Post-process model outputs to extract detections.

        Args:
            results: Raw model outputs
            original_shape: Original image shape (H, W, C)

        Returns:
            List of detections
        """
        detections = []

        if self.is_onnx:
            # ONNX output format depends on model
            # Typically: [batch, num_detections, 6] where 6 = [x, y, w, h, conf, class]
            # This is a simplified implementation
            detections = self._parse_onnx_output(results, original_shape)
        else:
            # YOLO ultralytics format
            if hasattr(results, 'boxes'):
                boxes = results.boxes
                for i in range(len(boxes)):
                    detection = {
                        "bbox": boxes.xyxy[i].cpu().numpy().tolist(),
                        "confidence": float(boxes.conf[i].cpu().numpy()),
                        "class_id": int(boxes.cls[i].cpu().numpy()),
                        "class_name": results.names[int(boxes.cls[i])] if hasattr(results, 'names') else str(int(boxes.cls[i]))
                    }
                    detections.append(detection)

        return detections

    def _parse_onnx_output(self, outputs: List[np.ndarray], original_shape: Tuple[int, int, int]) -> List[Dict[str, Any]]:
        """Parse ONNX model outputs."""
        detections = []

        # YOLO ONNX output format: [batch, num_boxes, 5+num_classes]
        # where 5 = [x_center, y_center, width, height, objectness]
        if outputs and len(outputs) > 0:
            output = outputs[0]  # First output
            if len(output.shape) == 3:
                output = output[0]  # First batch

            # Filter by confidence threshold
            conf_threshold = 0.25
            for detection in output:
                if len(detection) >= 5:
                    objectness = detection[4]
                    if objectness > conf_threshold:
                        # Extract class scores
                        class_scores = detection[5:] if len(detection) > 5 else [objectness]
                        class_id = np.argmax(class_scores)
                        confidence = float(objectness * class_scores[class_id])

                        if confidence > conf_threshold:
                            # Scale bounding box to original image
                            x_center, y_center, width, height = detection[:4]
                            h, w = original_shape[:2]

                            x1 = int((x_center - width / 2) * w / self.config.input_size[1])
                            y1 = int((y_center - height / 2) * h / self.config.input_size[0])
                            x2 = int((x_center + width / 2) * w / self.config.input_size[1])
                            y2 = int((y_center + height / 2) * h / self.config.input_size[0])

                            detections.append({
                                "bbox": [x1, y1, x2, y2],
                                "confidence": confidence,
                                "class_id": int(class_id),
                                "class_name": f"class_{class_id}"
                            })

        return detections

    def _extract_batch_result(self, batch_results: List[np.ndarray], index: int) -> Any:
        """Extract results for a specific image from batch output."""
        # Extract the i-th result from batch
        return [result[index:index+1] if len(result.shape) > 1 else result for result in batch_results]

    def get_current_fps(self) -> float:
        """Get current FPS based on recent inference times."""
        if not self.inference_times:
            return 0.0
        avg_time = np.mean(self.inference_times)
        return 1.0 / avg_time if avg_time > 0 else 0.0

    def get_performance_stats(self) -> Dict[str, float]:
        """Get detailed performance statistics."""
        stats = {
            "avg_fps": self.get_current_fps(),
            "avg_inference_time_ms": np.mean(self.inference_times) * 1000 if self.inference_times else 0,
            "std_inference_time_ms": np.std(self.inference_times) * 1000 if self.inference_times else 0,
            "avg_preprocessing_time_ms": np.mean(self.preprocessing_times) * 1000 if self.preprocessing_times else 0,
            "min_inference_time_ms": np.min(self.inference_times) * 1000 if self.inference_times else 0,
            "max_inference_time_ms": np.max(self.inference_times) * 1000 if self.inference_times else 0,
        }

        # Add total pipeline time
        if self.inference_times and self.preprocessing_times:
            stats["avg_total_time_ms"] = stats["avg_inference_time_ms"] + stats["avg_preprocessing_time_ms"]

        return stats

    def reset_performance_counters(self):
        """Reset performance tracking counters."""
        self.inference_times.clear()
        self.preprocessing_times.clear()
        self.frame_counter = 0

    def clear_cache(self):
        """Clear result cache to free memory."""
        self.result_cache.clear()
        self.last_results = None

    def __del__(self):
        """Cleanup on destruction."""
        if self.session:
            del self.session
        if self.model:
            del self.model


class VideoInferenceEngine(InferenceEngine):
    """Specialized inference engine for video streams."""

    def __init__(self, model_path: str, config: OptimizationConfig):
        """Initialize video inference engine."""
        super().__init__(model_path, config)
        self.video_fps = 30  # Default video FPS
        self.effective_fps = None

    def process_video(
        self,
        video_path: str,
        output_path: Optional[str] = None,
        display: bool = False,
        callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Process a video file with optimized inference.

        Args:
            video_path: Path to input video
            output_path: Optional path to save annotated video
            display: Display results in real-time
            callback: Optional callback function for each frame

        Returns:
            Processing statistics
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        # Get video properties
        self.video_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        logger.info(f"Processing video: {total_frames} frames @ {self.video_fps} FPS")
        logger.info(f"Resolution: {width}x{height}")
        logger.info(f"Frame skip: {self.config.frame_skip}")

        # Setup video writer if output path provided
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, self.video_fps, (width, height))

        frame_count = 0
        processed_frames = 0
        start_time = time.time()

        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                # Run inference
                results = self.predict(frame, return_details=True)
                processed_frames += 1

                # Call callback if provided
                if callback:
                    callback(frame, results, frame_count)

                # Annotate frame
                annotated_frame = self._annotate_frame(frame, results["detections"])

                # Write to output
                if writer:
                    writer.write(annotated_frame)

                # Display
                if display:
                    cv2.imshow("PPE Detection", annotated_frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                frame_count += 1

                # Progress logging
                if frame_count % 100 == 0:
                    progress = (frame_count / total_frames) * 100
                    logger.info(f"Progress: {progress:.1f}% ({frame_count}/{total_frames})")

        finally:
            cap.release()
            if writer:
                writer.release()
            if display:
                cv2.destroyAllWindows()

        # Calculate statistics
        total_time = time.time() - start_time
        self.effective_fps = processed_frames / total_time if total_time > 0 else 0

        stats = {
            "total_frames": frame_count,
            "processed_frames": processed_frames,
            "total_time_seconds": total_time,
            "effective_fps": self.effective_fps,
            "video_fps": self.video_fps,
            "speedup_factor": self.effective_fps / self.video_fps if self.video_fps > 0 else 0,
        }

        logger.info(f"Video processing complete. Effective FPS: {self.effective_fps:.2f}")

        return stats

    def _annotate_frame(self, frame: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
        """Annotate frame with detection results."""
        annotated = frame.copy()

        for detection in detections:
            bbox = detection["bbox"]
            confidence = detection["confidence"]
            class_name = detection["class_name"]

            # Draw bounding box
            x1, y1, x2, y2 = map(int, bbox)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            cv2.putText(
                annotated,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

        return annotated
