"""
OCR Reader for product labels and text recognition
Uses EasyOCR for multilingual text detection
"""

import cv2
import numpy as np
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("Warning: EasyOCR not installed. OCR functionality will be disabled.")


class OCRReader:
    """
    OCR Reader for detecting and reading text on product labels
    Supports multiple languages including Turkish and English
    """

    def __init__(self, languages=['tr', 'en']):
        """
        Initialize OCR reader

        Args:
            languages: List of language codes (e.g., ['tr', 'en'])
        """
        self.languages = languages
        self.reader = None

        if EASYOCR_AVAILABLE:
            try:
                self.reader = easyocr.Reader(languages, gpu=False)
            except Exception as e:
                print(f"Error initializing EasyOCR: {e}")
                self.reader = None
        else:
            print("EasyOCR not available. Install with: pip install easyocr")

    def read_text(self, image_path, bbox=None):
        """
        Read text from image or specific bounding box region

        Args:
            image_path: Path to image file
            bbox: Optional bounding box [x, y, w, h] to crop region

        Returns:
            List of (text, confidence) tuples
        """
        if self.reader is None:
            return []

        # Read image
        image = cv2.imread(image_path)
        if image is None:
            return []

        # Crop to bounding box if provided
        if bbox is not None:
            x, y, w, h = [int(v) for v in bbox]
            # Add padding
            padding = 10
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(image.shape[1] - x, w + 2 * padding)
            h = min(image.shape[0] - y, h + 2 * padding)
            image = image[y:y+h, x:x+w]

        # Run OCR
        try:
            results = self.reader.readtext(image)
            # Extract text and confidence
            text_results = [(text, conf) for (bbox, text, conf) in results]
            return text_results
        except Exception as e:
            print(f"OCR error: {e}")
            return []

    def read_labels(self, image_path, detections, confidence_threshold=0.3):
        """
        Read text labels for each detected product

        Args:
            image_path: Path to image file
            detections: List of detection dictionaries from detector
            confidence_threshold: Minimum OCR confidence threshold

        Returns:
            Updated detections with 'ocr_text' field
        """
        if self.reader is None:
            return detections

        for det in detections:
            bbox = det['box']
            ocr_results = self.read_text(image_path, bbox)

            # Filter by confidence and join text
            filtered_text = [
                text for text, conf in ocr_results
                if conf >= confidence_threshold
            ]

            if filtered_text:
                det['ocr_text'] = ' | '.join(filtered_text)
                det['ocr_confidence'] = np.mean([
                    conf for text, conf in ocr_results
                    if conf >= confidence_threshold
                ])
            else:
                det['ocr_text'] = ''
                det['ocr_confidence'] = 0.0

        return detections

    def extract_product_codes(self, text):
        """
        Extract product codes/SKUs from OCR text
        Common patterns: numeric codes, alphanumeric codes

        Args:
            text: OCR text string

        Returns:
            List of potential product codes
        """
        import re

        # Common patterns for product codes
        patterns = [
            r'\b[A-Z]{2,4}\d{4,8}\b',  # e.g., ABC1234
            r'\b\d{8,13}\b',  # Barcodes (EAN-8, EAN-13)
            r'\b[A-Z]\d{6,}\b',  # e.g., A123456
        ]

        codes = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            codes.extend(matches)

        return list(set(codes))  # Remove duplicates

    def get_text_in_region(self, image_path, x, y, w, h):
        """
        Get all text in a specific region

        Args:
            image_path: Path to image
            x, y, w, h: Region coordinates

        Returns:
            Concatenated text string
        """
        results = self.read_text(image_path, bbox=[x, y, w, h])
        return ' '.join([text for text, _ in results])
