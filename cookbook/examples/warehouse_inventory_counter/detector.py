"""
YOLOv8-based object detection for warehouse inventory counting
"""

import cv2
import numpy as np
from ultralytics import YOLO
import os


class WarehouseDetector:
    """
    Warehouse product detector using YOLOv8
    Detects and counts products on shelves automatically
    """

    def __init__(self, model_name="yolov8n.pt", confidence_threshold=0.4):
        """
        Initialize the detector

        Args:
            model_name: YOLOv8 model name (yolov8n/s/m/l/x)
            confidence_threshold: Minimum confidence score for detections
        """
        self.confidence_threshold = confidence_threshold
        self.model_name = model_name

        # Load YOLOv8 model
        try:
            self.model = YOLO(model_name)
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Downloading YOLOv8n model...")
            self.model = YOLO("yolov8n.pt")

        # Define colors for different classes
        self.colors = self._generate_colors(80)  # COCO has 80 classes

    def _generate_colors(self, n):
        """Generate distinct colors for different classes"""
        np.random.seed(42)
        colors = []
        for i in range(n):
            color = tuple(np.random.randint(0, 255, 3).tolist())
            colors.append(color)
        return colors

    def detect(self, image_path):
        """
        Detect products in warehouse shelf image

        Args:
            image_path: Path to the image file

        Returns:
            detections: List of detection dictionaries
            annotated_image: Image with bounding boxes drawn
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")

        # Run inference
        results = self.model(image, conf=self.confidence_threshold)

        # Parse detections
        detections = []
        annotated_image = image.copy()

        for result in results:
            boxes = result.boxes

            for box in boxes:
                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]

                # Store detection
                detection = {
                    'box': [float(x1), float(y1), float(x2 - x1), float(y2 - y1)],  # x, y, w, h
                    'confidence': confidence,
                    'class': class_name,
                    'class_id': class_id
                }
                detections.append(detection)

                # Draw bounding box
                color = self.colors[class_id % len(self.colors)]
                cv2.rectangle(
                    annotated_image,
                    (int(x1), int(y1)),
                    (int(x2), int(y2)),
                    color,
                    2
                )

                # Draw label background
                label = f"{class_name}: {confidence:.2f}"
                (label_width, label_height), _ = cv2.getTextSize(
                    label,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    2
                )

                cv2.rectangle(
                    annotated_image,
                    (int(x1), int(y1) - label_height - 10),
                    (int(x1) + label_width, int(y1)),
                    color,
                    -1
                )

                # Draw label text
                cv2.putText(
                    annotated_image,
                    label,
                    (int(x1), int(y1) - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

        return detections, annotated_image

    def count_products(self, detections):
        """
        Count products by class

        Args:
            detections: List of detection dictionaries

        Returns:
            Dictionary with class names as keys and counts as values
        """
        counts = {}
        for det in detections:
            class_name = det['class']
            counts[class_name] = counts.get(class_name, 0) + 1
        return counts

    def filter_by_class(self, detections, class_names):
        """
        Filter detections by class name

        Args:
            detections: List of detection dictionaries
            class_names: List of class names to keep

        Returns:
            Filtered list of detections
        """
        return [det for det in detections if det['class'] in class_names]

    def get_product_positions(self, detections):
        """
        Get spatial positions of detected products
        Useful for shelf organization analysis

        Args:
            detections: List of detection dictionaries

        Returns:
            List of (class_name, center_x, center_y) tuples
        """
        positions = []
        for det in detections:
            x, y, w, h = det['box']
            center_x = x + w / 2
            center_y = y + h / 2
            positions.append((det['class'], center_x, center_y))
        return positions
