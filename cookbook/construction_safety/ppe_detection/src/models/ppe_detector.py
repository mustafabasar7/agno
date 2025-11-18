"""
PPE (Personal Protective Equipment) Detector

This module implements a YOLO-based detector for construction safety PPE,
including helmets (barets) and safety vests (yoleks). It supports both
image and video frame processing with CPU-only inference.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
from ultralytics import YOLO
import warnings

from .model_config import ModelConfig, default_config


@dataclass
class Detection:
    """Data class representing a single detection."""

    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    confidence: float
    class_id: int
    class_name: str

    @property
    def center(self) -> Tuple[int, int]:
        """Get center point of bounding box."""
        x1, y1, x2, y2 = self.bbox
        return (int((x1 + x2) / 2), int((y1 + y2) / 2))

    @property
    def area(self) -> int:
        """Get area of bounding box."""
        x1, y1, x2, y2 = self.bbox
        return (x2 - x1) * (y2 - y1)

    def iou(self, other: 'Detection') -> float:
        """Calculate Intersection over Union with another detection."""
        x1_1, y1_1, x2_1, y2_1 = self.bbox
        x1_2, y1_2, x2_2, y2_2 = other.bbox

        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)

        if x2_i < x1_i or y2_i < y1_i:
            return 0.0

        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        union = self.area + other.area - intersection

        return intersection / union if union > 0 else 0.0

    def distance_to(self, other: 'Detection') -> float:
        """Calculate Euclidean distance to another detection's center."""
        x1, y1 = self.center
        x2, y2 = other.center
        return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)


@dataclass
class ComplianceResult:
    """Data class representing PPE compliance status for a person."""

    person_detection: Detection
    has_helmet: bool
    has_vest: bool
    is_compliant: bool
    helmet_detection: Optional[Detection] = None
    vest_detection: Optional[Detection] = None
    confidence_score: float = 0.0

    @property
    def compliance_status(self) -> str:
        """Get human-readable compliance status."""
        if self.is_compliant:
            return "COMPLIANT"
        elif not self.has_helmet and not self.has_vest:
            return "MISSING HELMET & VEST"
        elif not self.has_helmet:
            return "MISSING HELMET"
        elif not self.has_vest:
            return "MISSING VEST"
        return "NON-COMPLIANT"


class PPEDetector:
    """
    PPE Detection system using YOLO for detecting helmets and safety vests.

    This detector can process both images and video frames, detect PPE equipment,
    check compliance, and visualize results.
    """

    def __init__(
        self,
        config: Optional[ModelConfig] = None,
        use_custom_model: bool = False,
        verbose: bool = True
    ):
        """
        Initialize the PPE detector.

        Args:
            config: ModelConfig instance. If None, uses default configuration
            use_custom_model: If True, attempts to load custom fine-tuned model
            verbose: If True, prints initialization info
        """
        self.config = config or default_config
        self.verbose = verbose

        # Validate configuration
        if not self.config.validate_thresholds():
            raise ValueError("Invalid configuration thresholds")

        # Initialize model
        self.model = None
        self._load_model(use_custom_model)

        # Statistics
        self.stats = {
            "total_detections": 0,
            "total_frames_processed": 0,
            "total_persons_detected": 0,
            "total_compliant": 0,
            "total_non_compliant": 0
        }

    def _load_model(self, use_custom: bool = False) -> None:
        """
        Load the YOLO model.

        Args:
            use_custom: If True, load custom fine-tuned model
        """
        try:
            model_path = self.config.get_model_path(use_custom)

            if not model_path.exists():
                if self.verbose:
                    print(f"Model not found at {model_path}")
                    print(f"Downloading {self.config.model_architecture} model...")

                # Download pretrained model
                self.model = YOLO(f"{self.config.model_architecture}.pt")

                # Save to expected location
                model_path.parent.mkdir(parents=True, exist_ok=True)

                if self.verbose:
                    print(f"Model downloaded successfully")
            else:
                if self.verbose:
                    print(f"Loading model from {model_path}")
                self.model = YOLO(str(model_path))

            # Set device
            if self.verbose:
                print(f"Using device: {self.config.device}")
                print(f"Model loaded successfully: {self.config.model_architecture}")

        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")

    def preprocess_image(
        self,
        image: np.ndarray,
        target_size: Optional[Tuple[int, int]] = None
    ) -> np.ndarray:
        """
        Preprocess image for detection.

        Args:
            image: Input image as numpy array (BGR format)
            target_size: Target size for resizing. If None, uses config default

        Returns:
            Preprocessed image
        """
        if target_size is None:
            target_size = self.config.input_size

        # Resize if needed
        if image.shape[:2] != target_size[::-1]:  # (height, width) vs (width, height)
            image = cv2.resize(image, target_size, interpolation=cv2.INTER_LINEAR)

        # YOLO handles normalization internally, so we just return the resized image
        return image

    def detect_ppe(
        self,
        image: Union[np.ndarray, str, Path],
        confidence_threshold: Optional[float] = None,
        nms_threshold: Optional[float] = None,
        preprocess: bool = False
    ) -> List[Detection]:
        """
        Detect PPE equipment in an image.

        Args:
            image: Input image (numpy array, file path, or Path object)
            confidence_threshold: Override default confidence threshold
            nms_threshold: Override default NMS threshold
            preprocess: If True, preprocess image before detection

        Returns:
            List of Detection objects
        """
        # Load image if path is provided
        if isinstance(image, (str, Path)):
            image = cv2.imread(str(image))
            if image is None:
                raise ValueError(f"Failed to load image from {image}")

        # Validate image
        if not isinstance(image, np.ndarray):
            raise TypeError("Image must be numpy array or valid file path")

        # Store original dimensions
        original_shape = image.shape[:2]

        # Preprocess if requested
        if preprocess:
            processed_image = self.preprocess_image(image)
        else:
            processed_image = image

        # Set thresholds
        conf = confidence_threshold or self.config.confidence_threshold
        iou = nms_threshold or self.config.nms_threshold

        # Run inference
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            results = self.model.predict(
                processed_image,
                conf=conf,
                iou=iou,
                device=self.config.device,
                verbose=False
            )

        # Parse results
        detections = []
        if results and len(results) > 0:
            result = results[0]

            if result.boxes is not None and len(result.boxes) > 0:
                boxes = result.boxes.xyxy.cpu().numpy()  # Bounding boxes
                confidences = result.boxes.conf.cpu().numpy()  # Confidence scores
                class_ids = result.boxes.cls.cpu().numpy().astype(int)  # Class IDs

                for box, conf_score, class_id in zip(boxes, confidences, class_ids):
                    x1, y1, x2, y2 = map(int, box)

                    # Get class name
                    class_name = self.config.class_names.get(
                        class_id,
                        f"class_{class_id}"
                    )

                    detection = Detection(
                        bbox=(x1, y1, x2, y2),
                        confidence=float(conf_score),
                        class_id=int(class_id),
                        class_name=class_name
                    )
                    detections.append(detection)

        # Update statistics
        self.stats["total_detections"] += len(detections)
        self.stats["total_frames_processed"] += 1

        return detections

    def is_compliant(
        self,
        detections: List[Detection],
        confidence_threshold: Optional[float] = None
    ) -> List[ComplianceResult]:
        """
        Check PPE compliance for detected persons.

        A person is compliant if they are wearing both a helmet and a safety vest.
        PPE items are associated with persons based on spatial proximity and IoU.

        Args:
            detections: List of Detection objects
            confidence_threshold: Override default compliance confidence threshold

        Returns:
            List of ComplianceResult objects, one per detected person
        """
        conf_threshold = confidence_threshold or self.config.compliance_confidence_threshold

        # Separate detections by class
        persons = [d for d in detections if d.class_name == "person" and d.confidence >= conf_threshold]
        helmets = [d for d in detections if d.class_name == "helmet" and d.confidence >= conf_threshold]
        vests = [d for d in detections if d.class_name == "vest" and d.confidence >= conf_threshold]

        compliance_results = []

        for person in persons:
            # Find nearest helmet and vest
            nearest_helmet = None
            nearest_vest = None
            min_helmet_dist = float('inf')
            min_vest_dist = float('inf')

            # Check helmets
            for helmet in helmets:
                # Calculate distance and IoU
                distance = person.distance_to(helmet)
                iou = person.iou(helmet)

                # Helmet should be near the top of the person bounding box
                # and either overlap or be very close
                if (iou > self.config.iou_threshold or distance < min_helmet_dist):
                    # Additional check: helmet should be above person's center
                    if helmet.center[1] < person.center[1]:
                        if distance < min_helmet_dist:
                            nearest_helmet = helmet
                            min_helmet_dist = distance

            # Check vests
            for vest in vests:
                distance = person.distance_to(vest)
                iou = person.iou(vest)

                # Vest should overlap with person or be very close
                if (iou > self.config.iou_threshold or distance < min_vest_dist):
                    if distance < min_vest_dist:
                        nearest_vest = vest
                        min_vest_dist = distance

            # Determine compliance
            has_helmet = nearest_helmet is not None
            has_vest = nearest_vest is not None
            is_compliant = has_helmet and has_vest

            # Calculate confidence score (average of PPE detections)
            confidence_scores = []
            if has_helmet:
                confidence_scores.append(nearest_helmet.confidence)
            if has_vest:
                confidence_scores.append(nearest_vest.confidence)

            avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0

            result = ComplianceResult(
                person_detection=person,
                has_helmet=has_helmet,
                has_vest=has_vest,
                is_compliant=is_compliant,
                helmet_detection=nearest_helmet,
                vest_detection=nearest_vest,
                confidence_score=float(avg_confidence)
            )

            compliance_results.append(result)

            # Update statistics
            self.stats["total_persons_detected"] += 1
            if is_compliant:
                self.stats["total_compliant"] += 1
            else:
                self.stats["total_non_compliant"] += 1

        return compliance_results

    def visualize_detections(
        self,
        image: np.ndarray,
        detections: List[Detection],
        show_labels: bool = True,
        show_confidence: bool = True
    ) -> np.ndarray:
        """
        Draw bounding boxes and labels on image.

        Args:
            image: Input image
            detections: List of Detection objects
            show_labels: If True, show class labels
            show_confidence: If True, show confidence scores

        Returns:
            Image with drawn detections
        """
        output_image = image.copy()

        for detection in detections:
            x1, y1, x2, y2 = detection.bbox
            color = self.config.bbox_colors.get(
                detection.class_name,
                (255, 255, 255)  # White default
            )

            # Draw bounding box
            cv2.rectangle(
                output_image,
                (x1, y1),
                (x2, y2),
                color,
                self.config.bbox_thickness
            )

            # Prepare label
            if show_labels:
                label = detection.class_name
                if show_confidence:
                    label += f" {detection.confidence:.2f}"

                # Get label size
                (label_width, label_height), baseline = cv2.getTextSize(
                    label,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    self.config.font_scale,
                    self.config.font_thickness
                )

                # Draw label background
                cv2.rectangle(
                    output_image,
                    (x1, y1 - label_height - baseline - 5),
                    (x1 + label_width, y1),
                    color,
                    -1  # Filled rectangle
                )

                # Draw label text
                cv2.putText(
                    output_image,
                    label,
                    (x1, y1 - baseline - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    self.config.font_scale,
                    (255, 255, 255),  # White text
                    self.config.font_thickness
                )

        return output_image

    def visualize_compliance(
        self,
        image: np.ndarray,
        compliance_results: List[ComplianceResult],
        show_details: bool = True
    ) -> np.ndarray:
        """
        Visualize compliance status on image.

        Args:
            image: Input image
            compliance_results: List of ComplianceResult objects
            show_details: If True, show detailed compliance information

        Returns:
            Image with compliance visualization
        """
        output_image = image.copy()

        for result in compliance_results:
            person = result.person_detection
            x1, y1, x2, y2 = person.bbox

            # Choose color based on compliance
            color = self.config.bbox_colors["compliant"] if result.is_compliant else self.config.bbox_colors["non-compliant"]

            # Draw person bounding box
            cv2.rectangle(
                output_image,
                (x1, y1),
                (x2, y2),
                color,
                self.config.bbox_thickness + 1
            )

            # Draw PPE bounding boxes
            if result.helmet_detection:
                hx1, hy1, hx2, hy2 = result.helmet_detection.bbox
                cv2.rectangle(
                    output_image,
                    (hx1, hy1),
                    (hx2, hy2),
                    self.config.bbox_colors["helmet"],
                    self.config.bbox_thickness
                )

            if result.vest_detection:
                vx1, vy1, vx2, vy2 = result.vest_detection.bbox
                cv2.rectangle(
                    output_image,
                    (vx1, vy1),
                    (vx2, vy2),
                    self.config.bbox_colors["vest"],
                    self.config.bbox_thickness
                )

            # Add status label
            if show_details:
                status = result.compliance_status
                label = f"{status}"

                # Get label size
                (label_width, label_height), baseline = cv2.getTextSize(
                    label,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    self.config.font_scale,
                    self.config.font_thickness
                )

                # Draw label background
                cv2.rectangle(
                    output_image,
                    (x1, y1 - label_height - baseline - 10),
                    (x1 + label_width + 10, y1),
                    color,
                    -1
                )

                # Draw label text
                cv2.putText(
                    output_image,
                    label,
                    (x1 + 5, y1 - baseline - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    self.config.font_scale,
                    (255, 255, 255),
                    self.config.font_thickness
                )

        return output_image

    def process_video(
        self,
        video_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        show_preview: bool = False,
        check_compliance: bool = True
    ) -> Dict:
        """
        Process video file and detect PPE.

        Args:
            video_path: Path to input video file
            output_path: Path to save output video (optional)
            show_preview: If True, show preview window during processing
            check_compliance: If True, check and visualize compliance

        Returns:
            Dictionary with processing statistics
        """
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            raise ValueError(f"Failed to open video: {video_path}")

        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Initialize video writer if output path provided
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

        frame_count = 0
        processed_count = 0

        if self.verbose:
            print(f"Processing video: {video_path}")
            print(f"Resolution: {width}x{height}, FPS: {fps}, Total frames: {total_frames}")

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1

                # Skip frames based on config
                if self.config.video_frame_skip > 0 and frame_count % (self.config.video_frame_skip + 1) != 0:
                    if writer:
                        writer.write(frame)
                    continue

                # Detect PPE
                detections = self.detect_ppe(frame)

                # Process based on mode
                if check_compliance:
                    compliance_results = self.is_compliant(detections)
                    output_frame = self.visualize_compliance(frame, compliance_results)
                else:
                    output_frame = self.visualize_detections(frame, detections)

                # Write frame
                if writer:
                    writer.write(output_frame)

                # Show preview
                if show_preview:
                    cv2.imshow('PPE Detection', output_frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                processed_count += 1

                # Progress update
                if self.verbose and processed_count % 30 == 0:
                    progress = (frame_count / total_frames) * 100
                    print(f"Progress: {progress:.1f}% ({frame_count}/{total_frames} frames)")

        finally:
            cap.release()
            if writer:
                writer.release()
            if show_preview:
                cv2.destroyAllWindows()

        stats = {
            "total_frames": frame_count,
            "processed_frames": processed_count,
            "fps": fps,
            "resolution": (width, height),
            "output_path": str(output_path) if output_path else None
        }

        if self.verbose:
            print(f"Video processing complete: {processed_count} frames processed")

        return stats

    def get_statistics(self) -> Dict:
        """Get detection statistics."""
        stats = self.stats.copy()

        if stats["total_persons_detected"] > 0:
            stats["compliance_rate"] = stats["total_compliant"] / stats["total_persons_detected"]
        else:
            stats["compliance_rate"] = 0.0

        return stats

    def reset_statistics(self) -> None:
        """Reset detection statistics."""
        self.stats = {
            "total_detections": 0,
            "total_frames_processed": 0,
            "total_persons_detected": 0,
            "total_compliant": 0,
            "total_non_compliant": 0
        }

    def save_model(self, output_path: Union[str, Path]) -> None:
        """
        Save current model to disk.

        Args:
            output_path: Path to save model
        """
        self.model.save(str(output_path))
        if self.verbose:
            print(f"Model saved to {output_path}")

    def fine_tune(
        self,
        dataset_yaml: Union[str, Path],
        epochs: Optional[int] = None,
        **kwargs
    ) -> None:
        """
        Fine-tune the model on custom PPE dataset.

        Args:
            dataset_yaml: Path to dataset YAML configuration file
            epochs: Number of training epochs (uses config default if None)
            **kwargs: Additional training arguments
        """
        epochs = epochs or self.config.training_config["epochs"]

        train_args = {
            "data": str(dataset_yaml),
            "epochs": epochs,
            "imgsz": self.config.training_config["image_size"],
            "batch": self.config.training_config["batch_size"],
            "device": self.config.device,
            **kwargs
        }

        if self.verbose:
            print(f"Starting fine-tuning for {epochs} epochs...")
            print(f"Dataset: {dataset_yaml}")

        results = self.model.train(**train_args)

        if self.verbose:
            print("Fine-tuning complete!")

        return results


if __name__ == "__main__":
    # Example usage
    print("Initializing PPE Detector...")

    # Create detector
    detector = PPEDetector(verbose=True)

    # Print configuration
    print("\n" + detector.config.get_summary())

    # Example: Process an image (if you have one)
    # detections = detector.detect_ppe("path/to/image.jpg")
    # compliance = detector.is_compliant(detections)
    # for result in compliance:
    #     print(f"Person: {result.compliance_status}")

    print("\nDetector ready for use!")
