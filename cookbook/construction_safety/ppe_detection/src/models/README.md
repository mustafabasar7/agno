# PPE Detection Model Integration

A comprehensive PPE (Personal Protective Equipment) detection system using YOLOv8/YOLOv11 for construction safety monitoring. Detects helmets (barets) and safety vests (yoleks) with CPU-only inference.

## Features

- **YOLOv8/YOLOv11 Integration**: State-of-the-art object detection
- **CPU-Only Inference**: No GPU required for deployment
- **Multi-Class Detection**: Helmets, safety vests, and persons
- **Compliance Checking**: Automatic verification of PPE usage
- **Image & Video Processing**: Works with both formats
- **Visualization Tools**: Built-in drawing and annotation
- **Fine-tuning Support**: Train on custom datasets
- **Production Ready**: Configurable thresholds and settings

## Quick Start

### Basic Usage

```python
from models import PPEDetector
import cv2

# Initialize detector
detector = PPEDetector(verbose=True)

# Load image
image = cv2.imread("construction_site.jpg")

# Detect PPE
detections = detector.detect_ppe(image)

# Check compliance
compliance_results = detector.is_compliant(detections)

# Visualize results
output = detector.visualize_compliance(image, compliance_results)
cv2.imwrite("output.jpg", output)

# Print results
for result in compliance_results:
    print(f"Person: {result.compliance_status}")
    print(f"  Helmet: {result.has_helmet}")
    print(f"  Vest: {result.has_vest}")
```

## Installation

The required dependencies are already in the project's `requirements.txt`:

```bash
pip install ultralytics>=8.0.0 opencv-python>=4.8.0 numpy>=1.24.0
```

## Components

### 1. `model_config.py`

Configuration management for the detection system.

**Key Classes:**
- `ModelConfig`: Main configuration dataclass
- `ConfigPresets`: Predefined configurations for different scenarios

**Configuration Options:**
```python
from models import ModelConfig

config = ModelConfig()
config.confidence_threshold = 0.6      # Detection confidence
config.nms_threshold = 0.45            # Non-maximum suppression
config.input_size = (640, 640)         # Input image size
config.device = "cpu"                   # CPU-only
```

**Preset Configurations:**
```python
from models import ConfigPresets

# Fast inference (lower accuracy, higher speed)
config = ConfigPresets.fast_inference()

# High accuracy (slower, better detection)
config = ConfigPresets.high_accuracy()

# Video processing (optimized for real-time)
config = ConfigPresets.video_processing()

# Production (balanced settings)
config = ConfigPresets.production()
```

### 2. `ppe_detector.py`

Main detector implementation with comprehensive functionality.

**Key Classes:**
- `PPEDetector`: Main detector class
- `Detection`: Single detection result
- `ComplianceResult`: Compliance check result

**Main Methods:**

#### detect_ppe()
Detect PPE equipment in an image.

```python
detections = detector.detect_ppe(
    image,                          # numpy array or file path
    confidence_threshold=0.5,        # optional override
    nms_threshold=0.45,              # optional override
    preprocess=False                 # apply preprocessing
)
```

**Returns:** List of `Detection` objects with:
- `bbox`: Bounding box coordinates (x1, y1, x2, y2)
- `confidence`: Detection confidence score
- `class_id`: Class identifier
- `class_name`: Class name (helmet, vest, person)

#### is_compliant()
Check if detected persons are wearing required PPE.

```python
compliance_results = detector.is_compliant(
    detections,                     # List of detections
    confidence_threshold=0.55       # Optional override
)
```

**Returns:** List of `ComplianceResult` objects with:
- `person_detection`: Person detection object
- `has_helmet`: Boolean - helmet detected
- `has_vest`: Boolean - vest detected
- `is_compliant`: Boolean - both helmet and vest present
- `helmet_detection`: Helmet detection object (if found)
- `vest_detection`: Vest detection object (if found)
- `confidence_score`: Average confidence of PPE detections

#### visualize_detections()
Draw bounding boxes and labels on image.

```python
output = detector.visualize_detections(
    image,                          # Input image
    detections,                     # List of detections
    show_labels=True,               # Show class labels
    show_confidence=True            # Show confidence scores
)
```

#### visualize_compliance()
Visualize compliance status with color-coded boxes.

```python
output = detector.visualize_compliance(
    image,                          # Input image
    compliance_results,             # List of compliance results
    show_details=True               # Show compliance status
)
```

**Color Coding:**
- Green: Compliant (has both helmet and vest)
- Red: Non-compliant (missing PPE)
- Orange: Safety vest
- Green: Helmet

#### process_video()
Process entire video file with PPE detection.

```python
stats = detector.process_video(
    video_path="input.mp4",         # Input video
    output_path="output.mp4",       # Output video (optional)
    show_preview=False,             # Show live preview
    check_compliance=True           # Enable compliance checking
)
```

**Returns:** Dictionary with processing statistics:
- `total_frames`: Total frames in video
- `processed_frames`: Number of frames processed
- `fps`: Video frame rate
- `resolution`: Video resolution (width, height)
- `output_path`: Path to output video

## Class Mappings

The system uses the following class mappings:

| Class ID | Class Name  | Description |
|----------|-------------|-------------|
| 0        | helmet      | Safety helmet (baret) |
| 1        | vest        | Safety vest (yolek) |
| 2        | person      | Person detection |
| 3        | no-helmet   | Person without helmet (optional) |
| 4        | no-vest     | Person without vest (optional) |

## Configuration Details

### Detection Thresholds

```python
# Development/Testing
confidence_threshold = 0.5          # General detection
nms_threshold = 0.45                # Non-maximum suppression

# Production (more conservative)
production_confidence_threshold = 0.6
production_nms_threshold = 0.4

# Compliance Checking
compliance_confidence_threshold = 0.55  # Higher for compliance
iou_threshold = 0.3                     # Person-PPE association
```

### Input Image Settings

```python
input_size = (640, 640)            # Standard YOLO input
max_detection_size = (1280, 1280)  # For high-res images
```

### Model Architectures

Available YOLO models (in order of speed/accuracy tradeoff):

**YOLOv8:**
- `yolov8n`: Nano - Fastest, lowest accuracy
- `yolov8s`: Small - Good balance
- `yolov8m`: Medium - Better accuracy
- `yolov8l`: Large - High accuracy
- `yolov8x`: Extra Large - Best accuracy, slowest

**YOLOv11:**
- `yolov11n`: Nano - Latest version, faster
- `yolov11s`: Small - Improved accuracy
- `yolov11m`: Medium - Better performance
- `yolov11l`: Large - High accuracy
- `yolov11x`: Extra Large - Best performance

**Recommended for CPU:**
- Development: `yolov8n` or `yolov11n` (nano models)
- Production: `yolov8s` or `yolov11s` (small models)

## Advanced Usage

### Custom Model Path

```python
detector = PPEDetector(use_custom_model=True)
# Looks for: models/weights/ppe_detector_best.pt
```

### Fine-tuning on Custom Dataset

```python
# Initialize detector
detector = PPEDetector()

# Fine-tune on custom dataset
detector.fine_tune(
    dataset_yaml="data/ppe_dataset/dataset.yaml",
    epochs=100,
    batch=16,
    imgsz=640
)

# Save fine-tuned model
detector.save_model("models/weights/ppe_detector_best.pt")
```

**Dataset Format (YOLO):**
```
dataset/
├── dataset.yaml          # Dataset configuration
├── images/
│   ├── train/           # Training images
│   └── val/             # Validation images
└── labels/
    ├── train/           # Training annotations (.txt)
    └── val/             # Validation annotations (.txt)
```

**dataset.yaml example:**
```yaml
path: /path/to/dataset
train: images/train
val: images/val

nc: 3  # Number of classes
names: ['helmet', 'vest', 'person']
```

### Batch Processing

```python
from pathlib import Path

detector = PPEDetector()

image_dir = Path("images/")
output_dir = Path("output/")
output_dir.mkdir(exist_ok=True)

for img_path in image_dir.glob("*.jpg"):
    # Load and process
    image = cv2.imread(str(img_path))
    detections = detector.detect_ppe(image)
    compliance = detector.is_compliant(detections)

    # Visualize and save
    output = detector.visualize_compliance(image, compliance)
    output_path = output_dir / f"{img_path.stem}_result.jpg"
    cv2.imwrite(str(output_path), output)

# Get overall statistics
stats = detector.get_statistics()
print(f"Compliance Rate: {stats['compliance_rate']:.1%}")
```

### Statistics Tracking

```python
# Get current statistics
stats = detector.get_statistics()

print(f"Total Detections: {stats['total_detections']}")
print(f"Persons Detected: {stats['total_persons_detected']}")
print(f"Compliant: {stats['total_compliant']}")
print(f"Non-Compliant: {stats['total_non_compliant']}")
print(f"Compliance Rate: {stats['compliance_rate']:.1%}")

# Reset statistics
detector.reset_statistics()
```

### Video Processing with Frame Skipping

```python
# Configure for faster video processing
config = ModelConfig()
config.video_frame_skip = 2  # Process every 3rd frame
config.model_architecture = "yolov8n"

detector = PPEDetector(config=config)

stats = detector.process_video(
    video_path="construction_site.mp4",
    output_path="output_with_ppe.mp4",
    check_compliance=True
)
```

## Performance Optimization

### CPU Optimization Tips

1. **Use Nano Model**: `yolov8n` or `yolov11n` for fastest inference
2. **Reduce Input Size**: Use `(416, 416)` instead of `(640, 640)`
3. **Skip Frames**: Process every Nth frame in videos
4. **Batch Processing**: Process multiple images together
5. **Adjust Thresholds**: Higher confidence = fewer false positives

### Example: Fast Configuration

```python
config = ModelConfig()
config.model_architecture = "yolov8n"
config.input_size = (416, 416)
config.confidence_threshold = 0.6
config.video_frame_skip = 2

detector = PPEDetector(config=config)
```

## Troubleshooting

### Model Not Found
First run downloads the model automatically:
```python
detector = PPEDetector()  # Downloads yolov8n.pt on first run
```

### Low Detection Accuracy
- Lower confidence threshold: `config.confidence_threshold = 0.4`
- Use larger model: `config.model_architecture = "yolov8s"`
- Fine-tune on your specific dataset

### Slow Processing
- Use nano model: `config.model_architecture = "yolov8n"`
- Reduce input size: `config.input_size = (416, 416)`
- Skip frames in video: `config.video_frame_skip = 2`

### Memory Issues
- Process images in smaller batches
- Reduce input size
- Use nano model

## Integration Examples

### Flask API

```python
from flask import Flask, request, jsonify
from models import PPEDetector
import cv2
import numpy as np

app = Flask(__name__)
detector = PPEDetector()

@app.route('/detect', methods=['POST'])
def detect_ppe():
    file = request.files['image']
    image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)

    detections = detector.detect_ppe(image)
    compliance = detector.is_compliant(detections)

    results = [{
        'compliant': r.is_compliant,
        'has_helmet': r.has_helmet,
        'has_vest': r.has_vest,
        'status': r.compliance_status
    } for r in compliance]

    return jsonify(results)
```

### Real-time Camera Stream

```python
detector = PPEDetector()
cap = cv2.VideoCapture(0)  # Webcam

while True:
    ret, frame = cap.read()
    if not ret:
        break

    detections = detector.detect_ppe(frame)
    compliance = detector.is_compliant(detections)
    output = detector.visualize_compliance(frame, compliance)

    cv2.imshow('PPE Detection', output)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

## File Structure

```
src/models/
├── __init__.py              # Module exports
├── model_config.py          # Configuration management
├── ppe_detector.py          # Main detector implementation
├── example_usage.py         # Usage examples
└── README.md               # This file

models/weights/              # Model storage (auto-created)
├── yolov8n.pt              # Downloaded automatically
└── ppe_detector_best.pt    # Custom fine-tuned model (optional)
```

## License & Credits

- Built on [Ultralytics YOLOv8/YOLOv11](https://github.com/ultralytics/ultralytics)
- Uses OpenCV for image processing
- Part of the Agno Construction Safety project

## Support

For issues or questions:
1. Check the example usage in `example_usage.py`
2. Review configuration options in `model_config.py`
3. Consult Ultralytics documentation for YOLO-specific questions
