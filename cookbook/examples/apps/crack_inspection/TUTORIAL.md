# Concrete Crack Width Measurement - Complete Tutorial

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Detailed Usage Guide](#detailed-usage-guide)
4. [Understanding the Output](#understanding-the-output)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Usage](#advanced-usage)

## Introduction

This tutorial will guide you through using the Concrete Crack Width Measurement system for professional construction inspection and laboratory analysis.

### What This System Does

- **Detects cracks** in concrete samples automatically
- **Measures crack widths** in millimeters with calibration
- **Classifies severity** according to construction standards
- **Generates reports** suitable for building inspection documentation

### Prerequisites

```bash
# Install required packages
pip install -r requirements.txt

# Set up API keys
export ANTHROPIC_API_KEY="your-key-here"  # For Claude models
# OR
export OPENAI_API_KEY="your-key-here"     # For GPT-4 Vision
```

## Quick Start

### Option 1: Web Interface (Recommended for Beginners)

```bash
# Start the Gradio app
python app.py

# Open browser to http://localhost:7860
# Upload an image and click "Analyze"
```

### Option 2: Command Line

```bash
# Basic analysis
python agent.py sample.jpg

# With calibration
python agent.py sample.jpg --calibration-mm 25.4 --project "Project A"
```

### Option 3: Python Code

```python
from crack_inspection.agent import CrackInspectionAgent

agent = CrackInspectionAgent()
results = agent.analyze_image("sample.jpg", calibration_mm=25.4)
print(results)
```

## Detailed Usage Guide

### Step 1: Prepare Your Image

**Image Requirements:**
- Format: JPG, PNG, or other common formats
- Resolution: Minimum 1MP, recommended 2MP or higher
- Lighting: Even lighting, avoid harsh shadows
- Angle: Perpendicular to concrete surface (straight on)

**Include Calibration Reference:**
- Place a ruler, coin, or measuring tape in the image
- Ensure it's in the same plane as the crack
- Make sure it's clearly visible and in focus

**Example Setup:**
```
┌─────────────────────────────┐
│                             │
│    Concrete Sample          │
│                             │
│         ╱╲  ← Crack         │
│        ╱  ╲                 │
│                             │
│    [═══════] ← Ruler        │
│     0  1  2 cm              │
└─────────────────────────────┘
```

### Step 2: Choose Your Calibration Method

#### Method A: Known Object Dimensions

Common reference objects:

| Object | Dimension | Use Case |
|--------|-----------|----------|
| US Penny | 19.05 mm diameter | Small cracks, portable |
| US Quarter | 24.26 mm diameter | Medium cracks, portable |
| Ruler | Various marked | Most accurate, any size |
| Credit Card | 85.6 mm × 53.98 mm | Convenient, always available |

#### Method B: No Calibration (Relative Analysis)

- Omit `--calibration-mm` parameter
- System will provide relative analysis
- Less accurate but still useful for comparison

### Step 3: Run the Analysis

#### Using Web Interface

1. **Upload Image**: Click "Concrete Sample Image" and select your file
2. **Configure**:
   - Enter project name (e.g., "Building A Inspection")
   - Enter sample ID (e.g., "S-001")
   - Select calibration object type
   - Enter known dimension in mm
3. **Select Model**: Choose Claude or GPT-4 Vision
4. **Analyze**: Click "Analyze Concrete Sample"
5. **Review Results**: Check the Summary, Report, and JSON tabs

#### Using Command Line

```bash
# Example 1: With 1-inch ruler (25.4mm)
python agent.py sample.jpg \
  --calibration-mm 25.4 \
  --project "Bridge Inspection 2024" \
  --sample-id "PIER-A-001"

# Example 2: With US Quarter (24.26mm)
python agent.py sample.jpg \
  --calibration-mm 24.26 \
  --project "Foundation Check"

# Example 3: Using GPT-4 Vision
python agent.py sample.jpg \
  --calibration-mm 25.4 \
  --use-openai

# Example 4: No structured output (verbose mode)
python agent.py sample.jpg \
  --calibration-mm 25.4 \
  --no-structured
```

#### Using Python API

```python
from crack_inspection.agent import CrackInspectionAgent

# Create agent
agent = CrackInspectionAgent(
    model="claude-3-7-sonnet-latest",  # or gpt-4o
    use_openai=False,
    structured_output=True
)

# Analyze image
results = agent.analyze_image(
    image_path="path/to/sample.jpg",
    calibration_mm=25.4,
    project_name="My Construction Project",
    sample_id="SAMPLE-001"
)

# Access results
print(f"Cracks detected: {results['cracks_detected']}")
print(f"Number of cracks: {results['crack_count']}")

for i, (desc, width, classification) in enumerate(
    zip(
        results['crack_descriptions'],
        results['crack_widths_mm'],
        results['crack_classifications']
    )
):
    print(f"\nCrack {i+1}:")
    print(f"  Description: {desc}")
    print(f"  Width: {width:.3f} mm")
    print(f"  Classification: {classification}")

# Generate report
report = agent.generate_report(results)
print("\n" + report)

# Save to file
with open("inspection_report.txt", "w") as f:
    f.write(report)
```

## Understanding the Output

### Structured Output Fields

```python
{
  "cracks_detected": true,           # Boolean: Were cracks found?
  "crack_count": 2,                  # Integer: Number of cracks
  "crack_descriptions": [            # List: Description of each crack
    "Linear crack, upper left quadrant, 30-degree angle",
    "Branching crack pattern, center region"
  ],
  "calibration_object_detected": true,  # Boolean: Was reference found?
  "calibration_object_type": "Ruler",   # String: Type of reference
  "reference_dimension_pixels": 127.0,  # Float: Reference size in pixels
  "crack_widths_pixels": [15.0, 8.5],   # List: Crack sizes in pixels
  "crack_widths_mm": [2.992, 1.693],    # List: Crack sizes in mm
  "crack_classifications": [             # List: Severity classifications
    "Wide crack",
    "Medium crack"
  ],
  "severity_assessment": "High severity - repair required",
  "recommendations": [
    "Immediate repair required for crack #1",
    "Monitor crack #2 and repair if progression observed"
  ]
}
```

### Crack Classifications Explained

| Classification | Width Range | Severity | Typical Action |
|----------------|-------------|----------|----------------|
| **Hair crack** | < 0.1 mm | Minimal | Monitor during routine inspections |
| **Fine crack** | 0.1-0.3 mm | Low | Document and monitor quarterly |
| **Medium crack** | 0.3-1.0 mm | Moderate | Schedule repair within 6 months |
| **Wide crack** | 1.0-3.0 mm | High | Repair within 3 months |
| **Severe crack** | > 3.0 mm | Critical | Immediate repair + structural assessment |

### Report Format

The generated report includes:

1. **Header**: Project info, sample ID, date/time
2. **Findings**: Crack detection results
3. **Measurements**: Detailed crack data with classifications
4. **Severity Assessment**: Overall condition evaluation
5. **Recommendations**: Specific actions required

## Best Practices

### Photography Tips

1. **Lighting**:
   - Use diffuse natural light when possible
   - Avoid direct sunlight (creates harsh shadows)
   - Use flash with diffuser for indoor samples
   - Consistent lighting across the sample surface

2. **Camera Position**:
   - Hold camera perpendicular to surface
   - Maintain consistent distance for series of samples
   - Fill frame with sample area
   - Avoid extreme angles or distortion

3. **Focus and Clarity**:
   - Ensure crack is in sharp focus
   - Use macro mode for small cracks
   - Multiple images at different angles are helpful
   - Clean the lens before shooting

4. **Calibration Reference**:
   - Place reference in same plane as crack
   - Ensure reference is clearly visible
   - Position near but not overlapping crack
   - Use contrasting color for easy detection

### Measurement Accuracy

**Factors Affecting Accuracy:**
- Image resolution (higher is better)
- Calibration reference quality
- Camera angle (perpendicular is best)
- Lighting uniformity
- Crack visibility and contrast

**Improving Accuracy:**
- Use high-resolution cameras (≥5MP)
- Include precise calibration reference (ruler preferred)
- Take multiple images from slightly different angles
- Verify measurements against manual inspection
- Use consistent methodology across samples

### Batch Processing

For multiple samples:

```python
from pathlib import Path
from crack_inspection.agent import CrackInspectionAgent
import json

agent = CrackInspectionAgent()
samples_dir = Path("samples")
results_dir = Path("results")
results_dir.mkdir(exist_ok=True)

for img_path in samples_dir.glob("*.jpg"):
    print(f"Processing {img_path.name}...")

    results = agent.analyze_image(
        image_path=str(img_path),
        calibration_mm=25.4,
        sample_id=img_path.stem
    )

    # Save results
    output_file = results_dir / f"{img_path.stem}_analysis.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    # Generate report
    report = agent.generate_report(results)
    report_file = results_dir / f"{img_path.stem}_report.txt"
    with open(report_file, "w") as f:
        f.write(report)

    print(f"  → {results['crack_count']} cracks detected")

print("Batch processing complete!")
```

## Troubleshooting

### Common Issues

**Issue**: "No cracks detected" but cracks are visible

**Solutions**:
- Improve image contrast
- Ensure crack is in focus
- Try different lighting conditions
- Clean the concrete surface (remove dust/debris)
- Use image enhancement (increase contrast)

---

**Issue**: Inaccurate measurements

**Solutions**:
- Verify calibration reference is correct dimension
- Ensure reference is in same plane as crack
- Check that camera is perpendicular to surface
- Use higher resolution image
- Verify calibration object is detected correctly

---

**Issue**: Calibration object not detected

**Solutions**:
- Ensure reference object is clearly visible
- Increase contrast between reference and background
- Position reference in well-lit area
- Use standard objects (ruler, coin)
- Manually specify calibration in prompt

---

**Issue**: API errors or timeouts

**Solutions**:
- Check API key is set correctly
- Verify internet connection
- Reduce image size if very large (>10MB)
- Try different model (Claude vs GPT-4)
- Check API rate limits

### Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError` | Image path incorrect | Check file path is absolute or relative |
| `ModuleNotFoundError` | Missing dependencies | Run `pip install -r requirements.txt` |
| `AuthenticationError` | Invalid API key | Set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` |
| `RateLimitError` | Too many requests | Wait and retry, or upgrade API plan |

## Advanced Usage

### Custom Analysis Prompts

```python
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.crack_detection import CrackDetectionTools
from agno.media import Image

agent = Agent(
    model=Claude(id="claude-3-7-sonnet-latest"),
    tools=[CrackDetectionTools()],
)

# Custom detailed analysis
custom_prompt = """
Analyze this concrete sample with special attention to:
1. Map cracking patterns (interconnected cracks)
2. Signs of alkali-silica reaction (ASR)
3. Freeze-thaw damage indicators
4. Measure all cracks wider than 0.5mm

Reference object: 1-inch ruler (25.4mm)
"""

response = agent.run(
    custom_prompt,
    images=[Image(filepath="sample.jpg")]
)
```

### Integration with Construction Management

```python
# Example: Export to construction management system
import json
import requests

def export_to_cms(results, cms_api_url, project_id):
    """Export results to construction management system."""

    payload = {
        "project_id": project_id,
        "inspection_type": "crack_analysis",
        "timestamp": datetime.now().isoformat(),
        "findings": {
            "crack_count": results["crack_count"],
            "max_width_mm": max(results["crack_widths_mm"]) if results["crack_widths_mm"] else 0,
            "severity": results["severity_assessment"],
            "requires_action": any("repair" in r.lower() for r in results["recommendations"])
        },
        "full_report": results
    }

    response = requests.post(
        cms_api_url,
        json=payload,
        headers={"Authorization": f"Bearer {API_TOKEN}"}
    )

    return response.json()

# Usage
results = agent.analyze_image("sample.jpg", calibration_mm=25.4)
export_to_cms(results, "https://cms.example.com/api/inspections", "PROJECT-123")
```

### Multi-Image Analysis

```python
from agno.media import Image

def analyze_multiple_angles(image_paths, calibration_mm):
    """Analyze the same sample from multiple angles."""

    agent = CrackInspectionAgent()

    all_results = []
    for img_path in image_paths:
        results = agent.analyze_image(
            image_path=img_path,
            calibration_mm=calibration_mm,
            sample_id=f"SAMPLE-{Path(img_path).stem}"
        )
        all_results.append(results)

    # Aggregate results
    total_cracks = sum(r["crack_count"] for r in all_results)
    max_width = max(
        max(r["crack_widths_mm"]) if r["crack_widths_mm"] else 0
        for r in all_results
    )

    return {
        "multi_angle_analysis": True,
        "image_count": len(image_paths),
        "total_unique_cracks": total_cracks,
        "maximum_width_mm": max_width,
        "individual_results": all_results
    }

# Usage
angles = ["sample_front.jpg", "sample_side.jpg", "sample_top.jpg"]
combined = analyze_multiple_angles(angles, calibration_mm=25.4)
```

### Statistical Analysis

```python
import pandas as pd
import matplotlib.pyplot as plt

def analyze_project_trends(results_dir):
    """Analyze trends across multiple samples."""

    results = []
    for file in Path(results_dir).glob("*_analysis.json"):
        with open(file) as f:
            results.append(json.load(f))

    # Create DataFrame
    df = pd.DataFrame([
        {
            "sample_id": r["sample_id"],
            "crack_count": r["crack_count"],
            "max_width_mm": max(r["crack_widths_mm"]) if r["crack_widths_mm"] else 0,
            "severity": r["severity_assessment"]
        }
        for r in results
    ])

    # Statistics
    print("Project Statistics:")
    print(f"Total samples: {len(df)}")
    print(f"Samples with cracks: {df['crack_count'].gt(0).sum()}")
    print(f"Average crack width: {df['max_width_mm'].mean():.3f} mm")
    print(f"Maximum crack width: {df['max_width_mm'].max():.3f} mm")

    # Plot
    df.plot(x="sample_id", y="max_width_mm", kind="bar")
    plt.ylabel("Maximum Crack Width (mm)")
    plt.title("Crack Width by Sample")
    plt.tight_layout()
    plt.savefig("crack_analysis.png")

    return df

# Usage
df = analyze_project_trends("results/")
```

## Additional Resources

- **agno Documentation**: https://docs.agno.ai
- **Construction Standards**: ACI, ASTM, BS standards for crack assessment
- **Image Processing**: OpenCV tutorials for image enhancement
- **API Documentation**: Anthropic Claude API, OpenAI Vision API

## Support

For issues or questions:
- GitHub Issues: https://github.com/anthropics/agno/issues
- Documentation: Check the README.md in this directory
- Examples: See `example_simple.py` for code examples

---

**Last Updated**: 2024
**Version**: 1.0
