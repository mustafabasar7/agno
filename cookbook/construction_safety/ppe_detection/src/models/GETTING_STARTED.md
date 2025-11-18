# Getting Started with PPE Detection

A 5-minute guide to start detecting PPE in construction site images.

## Prerequisites

```bash
pip install ultralytics opencv-python numpy
```

## 1. Basic Detection (3 lines)

Create a file `detect.py`:

```python
from models import PPEDetector
import cv2

detector = PPEDetector()                    # Initialize detector
image = cv2.imread("your_image.jpg")        # Load your image
detections = detector.detect_ppe(image)     # Detect PPE

# Print results
for det in detections:
    print(f"{det.class_name}: {det.confidence:.2f}")
```

Run it:
```bash
python detect.py
```

**First run:** Downloads YOLOv8 model (~6MB), takes 30-60 seconds
**Subsequent runs:** Instant startup

## 2. Check Compliance (Add 2 lines)

```python
from models import PPEDetector
import cv2

detector = PPEDetector()
image = cv2.imread("your_image.jpg")
detections = detector.detect_ppe(image)

# Add these lines:
compliance = detector.is_compliant(detections)
for result in compliance:
    print(f"Person: {result.compliance_status}")
    print(f"  Helmet: {'✓' if result.has_helmet else '✗'}")
    print(f"  Vest: {'✓' if result.has_vest else '✗'}")
```

## 3. Visualize Results (Add 2 more lines)

```python
from models import PPEDetector
import cv2

detector = PPEDetector()
image = cv2.imread("your_image.jpg")
detections = detector.detect_ppe(image)
compliance = detector.is_compliant(detections)

# Add these lines:
output = detector.visualize_compliance(image, compliance)
cv2.imwrite("result.jpg", output)
```

Now you have a `result.jpg` with color-coded boxes showing compliance!

## 4. Process a Video (1 line)

```python
from models import PPEDetector

detector = PPEDetector()
detector.process_video("input.mp4", "output.mp4", check_compliance=True)
```

## 5. Faster Processing (for older CPUs)

```python
from models import PPEDetector, ConfigPresets

# Use fast configuration
detector = PPEDetector(config=ConfigPresets.fast_inference())

# Everything else stays the same
image = cv2.imread("your_image.jpg")
detections = detector.detect_ppe(image)
```

## Complete Working Example

Save as `ppe_check.py`:

```python
#!/usr/bin/env python3
"""Quick PPE compliance checker"""

from models import PPEDetector
import cv2
import sys

def main():
    # Check arguments
    if len(sys.argv) < 2:
        print("Usage: python ppe_check.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    # Initialize detector
    print("Initializing detector...")
    detector = PPEDetector(verbose=True)

    # Load image
    print(f"Loading {image_path}...")
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image {image_path}")
        sys.exit(1)

    # Detect PPE
    print("Detecting PPE...")
    detections = detector.detect_ppe(image)
    print(f"Found {len(detections)} objects")

    # Check compliance
    print("Checking compliance...")
    compliance = detector.is_compliant(detections)

    # Print results
    print("\n" + "="*50)
    print("COMPLIANCE REPORT")
    print("="*50)

    for i, result in enumerate(compliance, 1):
        print(f"\nPerson #{i}:")
        print(f"  Status: {result.compliance_status}")
        print(f"  Helmet: {'✓ Yes' if result.has_helmet else '✗ No'}")
        print(f"  Vest: {'✓ Yes' if result.has_vest else '✗ No'}")
        print(f"  Confidence: {result.confidence_score:.1%}")

    # Overall statistics
    stats = detector.get_statistics()
    print("\n" + "="*50)
    print(f"Total Persons: {stats['total_persons_detected']}")
    print(f"Compliant: {stats['total_compliant']}")
    print(f"Non-Compliant: {stats['total_non_compliant']}")
    if stats['total_persons_detected'] > 0:
        print(f"Compliance Rate: {stats['compliance_rate']:.1%}")
    print("="*50)

    # Save visualization
    output_path = image_path.replace('.', '_result.')
    output = detector.visualize_compliance(image, compliance)
    cv2.imwrite(output_path, output)
    print(f"\nVisualization saved to: {output_path}")

if __name__ == "__main__":
    main()
```

Run it:
```bash
chmod +x ppe_check.py
python ppe_check.py construction_site.jpg
```

Output:
```
Initializing detector...
Model loaded successfully: yolov8n
Loading construction_site.jpg...
Detecting PPE...
Found 8 objects
Checking compliance...

==================================================
COMPLIANCE REPORT
==================================================

Person #1:
  Status: COMPLIANT
  Helmet: ✓ Yes
  Vest: ✓ Yes
  Confidence: 89.5%

Person #2:
  Status: MISSING HELMET
  Helmet: ✗ No
  Vest: ✓ Yes
  Confidence: 78.2%

==================================================
Total Persons: 2
Compliant: 1
Non-Compliant: 1
Compliance Rate: 50.0%
==================================================

Visualization saved to: construction_site_result.jpg
```

## What Next?

### More Examples
```bash
python example_usage.py        # See 7 different usage examples
```

### Run Tests
```bash
python test_detector.py        # Verify everything works
```

### Read Documentation
- `README.md` - Full documentation
- `QUICK_REFERENCE.md` - Code snippets and tips
- `IMPLEMENTATION_SUMMARY.md` - Architecture details

### Common Tasks

**Batch process images:**
```python
from pathlib import Path

detector = PPEDetector()
for img_path in Path("images/").glob("*.jpg"):
    image = cv2.imread(str(img_path))
    detections = detector.detect_ppe(image)
    # Process...
```

**Adjust sensitivity:**
```python
# More detections (may have false positives)
detections = detector.detect_ppe(image, confidence_threshold=0.3)

# Fewer detections (more conservative)
detections = detector.detect_ppe(image, confidence_threshold=0.7)
```

**Use different model:**
```python
from models import ModelConfig

config = ModelConfig()
config.model_architecture = "yolov8s"  # Bigger = more accurate but slower
detector = PPEDetector(config=config)
```

**Real-time camera:**
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

## Troubleshooting

**"Module not found"**
```bash
pip install ultralytics opencv-python numpy
```

**"Model download slow"**
- First run downloads ~6MB YOLOv8 model
- Subsequent runs use cached model
- No internet needed after first run

**"Too slow on my CPU"**
```python
from models import ConfigPresets
detector = PPEDetector(config=ConfigPresets.fast_inference())
```

**"Not detecting helmets/vests"**
- Using pretrained COCO model (may not detect PPE well)
- For best results: fine-tune on your own construction site images
- See README.md section on fine-tuning

## File Locations

Everything is in:
```
/home/user/agno/cookbook/construction_safety/ppe_detection/src/models/
```

Your models are saved to:
```
/home/user/agno/cookbook/construction_safety/ppe_detection/models/weights/
```

## That's It!

You now know enough to:
- ✓ Detect PPE in images
- ✓ Check compliance
- ✓ Visualize results
- ✓ Process videos
- ✓ Adjust configurations

Happy detecting! 🏗️👷‍♂️
