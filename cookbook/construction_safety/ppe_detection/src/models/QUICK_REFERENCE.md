# PPE Detection - Quick Reference Guide

## Installation

```bash
pip install ultralytics opencv-python numpy
```

## Basic Detection (3 lines)

```python
from models import PPEDetector
import cv2

detector = PPEDetector()
image = cv2.imread("image.jpg")
detections = detector.detect_ppe(image)
```

## Compliance Check (5 lines)

```python
from models import PPEDetector
import cv2

detector = PPEDetector()
image = cv2.imread("image.jpg")
detections = detector.detect_ppe(image)
compliance = detector.is_compliant(detections)
output = detector.visualize_compliance(image, compliance)
cv2.imwrite("output.jpg", output)
```

## Video Processing

```python
detector = PPEDetector()
detector.process_video("input.mp4", "output.mp4", check_compliance=True)
```

## Configuration Presets

```python
from models import PPEDetector, ConfigPresets

# Fast (CPU-optimized)
detector = PPEDetector(config=ConfigPresets.fast_inference())

# High Accuracy
detector = PPEDetector(config=ConfigPresets.high_accuracy())

# Production
detector = PPEDetector(config=ConfigPresets.production())

# Video Processing
detector = PPEDetector(config=ConfigPresets.video_processing())
```

## Custom Configuration

```python
from models import PPEDetector, ModelConfig

config = ModelConfig()
config.confidence_threshold = 0.7
config.input_size = (416, 416)
config.model_architecture = "yolov8n"

detector = PPEDetector(config=config)
```

## Detection Results

```python
# Access detection properties
for det in detections:
    print(f"Class: {det.class_name}")
    print(f"Confidence: {det.confidence:.2f}")
    print(f"BBox: {det.bbox}")  # (x1, y1, x2, y2)
    print(f"Center: {det.center}")
    print(f"Area: {det.area}")
```

## Compliance Results

```python
for result in compliance:
    print(f"Status: {result.compliance_status}")
    print(f"Has Helmet: {result.has_helmet}")
    print(f"Has Vest: {result.has_vest}")
    print(f"Compliant: {result.is_compliant}")
    print(f"Confidence: {result.confidence_score:.2f}")
```

## Statistics

```python
stats = detector.get_statistics()
print(f"Compliance Rate: {stats['compliance_rate']:.1%}")
print(f"Total Persons: {stats['total_persons_detected']}")
print(f"Compliant: {stats['total_compliant']}")
```

## Fine-tuning

```python
detector = PPEDetector()
detector.fine_tune("dataset/dataset.yaml", epochs=100)
detector.save_model("models/weights/custom_ppe.pt")
```

## Batch Processing

```python
from pathlib import Path

detector = PPEDetector()

for img_path in Path("images/").glob("*.jpg"):
    image = cv2.imread(str(img_path))
    detections = detector.detect_ppe(image)
    compliance = detector.is_compliant(detections)
    output = detector.visualize_compliance(image, compliance)
    cv2.imwrite(f"output/{img_path.name}", output)
```

## Common Parameters

### detect_ppe()
- `image`: numpy array or file path
- `confidence_threshold`: float (0-1), default from config
- `nms_threshold`: float (0-1), default from config
- `preprocess`: bool, apply preprocessing

### is_compliant()
- `detections`: list of Detection objects
- `confidence_threshold`: float (0-1), override default

### visualize_detections()
- `image`: numpy array
- `detections`: list of Detection objects
- `show_labels`: bool, show class names
- `show_confidence`: bool, show confidence scores

### visualize_compliance()
- `image`: numpy array
- `compliance_results`: list of ComplianceResult objects
- `show_details`: bool, show compliance status

### process_video()
- `video_path`: path to input video
- `output_path`: path to save output (optional)
- `show_preview`: bool, show live preview
- `check_compliance`: bool, enable compliance checking

## Model Architectures

| Model | Speed | Accuracy | Recommended For |
|-------|-------|----------|-----------------|
| yolov8n | Fastest | Lowest | CPU, Real-time |
| yolov8s | Fast | Good | Production |
| yolov8m | Medium | Better | Accuracy needed |
| yolov8l | Slow | High | Offline processing |
| yolov11n | Fastest+ | Good | Latest, CPU |
| yolov11s | Fast+ | Better | Latest, Production |

## Thresholds Guide

### Confidence Threshold
- `0.3-0.4`: More detections, more false positives
- `0.5`: Balanced (default)
- `0.6-0.7`: Fewer false positives, may miss some
- `0.8+`: Very conservative

### NMS Threshold
- `0.3`: Strict, removes more overlapping boxes
- `0.45`: Balanced (default)
- `0.6`: Lenient, keeps more boxes

### IoU Threshold (Person-PPE association)
- `0.2`: Loose association
- `0.3`: Balanced (default)
- `0.5`: Strict association

## Troubleshooting

### Slow processing?
```python
config = ModelConfig()
config.model_architecture = "yolov8n"  # Use nano
config.input_size = (416, 416)         # Smaller input
detector = PPEDetector(config=config)
```

### Low accuracy?
```python
config = ModelConfig()
config.model_architecture = "yolov8s"  # Bigger model
config.confidence_threshold = 0.4       # Lower threshold
detector = PPEDetector(config=config)
```

### Too many false positives?
```python
config = ModelConfig()
config.confidence_threshold = 0.7       # Higher threshold
detector = PPEDetector(config=config)
```

## File Locations

```
src/models/
├── ppe_detector.py      # Main detector
├── model_config.py      # Configuration
├── example_usage.py     # Examples
├── test_detector.py     # Test suite
└── README.md           # Full documentation

models/weights/
├── yolov8n.pt          # Auto-downloaded
└── ppe_detector_best.pt # Custom model (optional)
```

## API Integration Example

```python
from flask import Flask, request, jsonify
from models import PPEDetector
import cv2
import numpy as np

app = Flask(__name__)
detector = PPEDetector()

@app.route('/detect', methods=['POST'])
def detect():
    file = request.files['image']
    img_array = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    detections = detector.detect_ppe(image)
    compliance = detector.is_compliant(detections)

    return jsonify([{
        'compliant': r.is_compliant,
        'helmet': r.has_helmet,
        'vest': r.has_vest
    } for r in compliance])
```

## Testing

```bash
# Run test suite
python test_detector.py

# Run examples
python example_usage.py
```

## Class IDs

- `0`: helmet
- `1`: vest
- `2`: person
- `3`: no-helmet (optional)
- `4`: no-vest (optional)

## Color Codes (BGR)

- Helmet: Green (0, 255, 0)
- Vest: Orange (0, 165, 255)
- Person: Blue (255, 0, 0)
- Compliant: Green (0, 255, 0)
- Non-compliant: Red (0, 0, 255)
