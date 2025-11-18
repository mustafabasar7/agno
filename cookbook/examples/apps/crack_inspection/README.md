# Concrete Crack Width Measurement System

Professional AI-powered crack detection and width measurement for construction inspection and laboratory analysis.

## Overview

This application uses advanced computer vision and AI to automatically detect and measure cracks in concrete samples. Designed for:

- 🏗️ **Construction Laboratories** - Automated sample analysis
- 📋 **Building Inspection Reports** - Professional documentation
- 🔬 **Quality Control** - Consistent, objective measurements
- ⚡ **Fast Turnaround** - Instant analysis and reporting

## Features

- **Automatic Crack Detection**: Identifies cracks, fissures, and surface defects
- **Precise Measurements**: Measures crack widths in millimeters using calibration
- **Calibration Support**: Works with rulers, coins, or any reference object
- **Classification System**: Categorizes cracks by severity (hair/fine/medium/wide/severe)
- **Professional Reports**: Generates formatted inspection reports
- **Multiple AI Models**: Supports Claude 3.5 Sonnet, Claude 3 Opus, and GPT-4 Vision
- **Structured Output**: JSON data export for further analysis

## Usage

### Web Interface (Gradio)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Then open http://localhost:7860 in your browser.

### Command Line Interface

```bash
# Basic analysis
python agent.py concrete_sample.jpg

# With calibration (25.4mm ruler)
python agent.py sample.jpg --calibration-mm 25.4 --project "Building A" --sample-id "S-001"

# Using GPT-4 Vision
python agent.py sample.jpg --use-openai --calibration-mm 25.4
```

### Python API

```python
from crack_inspection.agent import CrackInspectionAgent

# Create agent
agent = CrackInspectionAgent(model="claude-3-7-sonnet-latest")

# Analyze image
results = agent.analyze_image(
    image_path="concrete_sample.jpg",
    calibration_mm=25.4,  # Known dimension in mm
    project_name="Building A Inspection",
    sample_id="S-001"
)

# Generate report
report = agent.generate_report(results)
print(report)
```

## Calibration

For accurate measurements, include a reference object with known dimensions:

| Object | Typical Size |
|--------|--------------|
| US Penny | 19.05 mm diameter |
| US Nickel | 21.21 mm diameter |
| US Quarter | 24.26 mm diameter |
| Ruler | Marked measurements |
| Measuring Tape | Marked measurements |

## Crack Classification Standards

Based on international construction standards:

| Classification | Width | Severity | Action |
|----------------|-------|----------|--------|
| Hair crack | < 0.1 mm | Minimal | Monitor |
| Fine crack | 0.1-0.3 mm | Low | Monitor and document |
| Medium crack | 0.3-1.0 mm | Moderate | Repair recommended |
| Wide crack | 1.0-3.0 mm | High | Repair required |
| Severe crack | > 3.0 mm | Critical | Immediate repair + structural assessment |

## Environment Variables

```bash
# For Claude models
export ANTHROPIC_API_KEY="your-api-key"

# For OpenAI models
export OPENAI_API_KEY="your-api-key"
```

## HuggingFace Space Deployment

This app is ready for deployment on HuggingFace Spaces:

1. Create a new Space on HuggingFace
2. Upload all files from this directory
3. Set environment variables (API keys) in Space settings
4. The app will automatically launch on port 7860

## Architecture

```
┌─────────────────────────────────────────┐
│         User Interface (Gradio)         │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│      CrackInspectionAgent (agno)        │
│  ┌─────────────────────────────────┐   │
│  │  Vision Model (Claude/GPT-4)    │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │   CrackDetectionTools           │   │
│  │   - analyze_concrete_image()    │   │
│  │   - calculate_calibration()     │   │
│  │   - measure_crack_width()       │   │
│  │   - generate_report()           │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Technical Details

### Image Processing Flow

1. **Image Input**: Upload concrete sample photograph
2. **Vision Analysis**: AI model examines image for cracks and references
3. **Calibration**: Detect and measure reference object
4. **Crack Detection**: Identify all visible cracks
5. **Pixel Measurement**: Estimate crack widths in pixels
6. **Conversion**: Calculate mm using calibration factor
7. **Classification**: Categorize by severity
8. **Report Generation**: Create professional documentation

### Measurement Accuracy

- Depends on image quality and resolution
- Calibration object improves accuracy significantly
- Best results with:
  - High resolution images (>2MP)
  - Good lighting (even, no harsh shadows)
  - Clear calibration reference
  - Perpendicular camera angle

## Examples

### Example 1: Basic Crack Detection

```python
from crack_inspection.agent import CrackInspectionAgent

agent = CrackInspectionAgent()
results = agent.analyze_image("crack_sample.jpg")
```

### Example 2: With Calibration

```python
agent = CrackInspectionAgent()
results = agent.analyze_image(
    image_path="crack_sample.jpg",
    calibration_mm=25.4,  # 1 inch ruler
    project_name="Bridge Inspection 2024",
    sample_id="PIER-A-001"
)

# Results include:
# - Crack locations and patterns
# - Width measurements in mm
# - Severity classifications
# - Repair recommendations
```

### Example 3: Batch Processing

```python
from pathlib import Path
from crack_inspection.agent import CrackInspectionAgent

agent = CrackInspectionAgent()
samples_dir = Path("concrete_samples")

for img_path in samples_dir.glob("*.jpg"):
    results = agent.analyze_image(
        image_path=str(img_path),
        sample_id=img_path.stem
    )
    print(f"Sample {img_path.stem}: {results['crack_count']} cracks detected")
```

## Contributing

Contributions welcome! Areas for improvement:

- [ ] Additional crack pattern recognition (map cracking, alligator cracking)
- [ ] Multi-image analysis (different angles)
- [ ] Historical tracking and trend analysis
- [ ] Integration with construction management systems
- [ ] Support for other defect types (spalling, delamination)

## License

This project is part of the agno framework. See main repository for license details.

## Citation

If you use this tool in research or professional reports:

```
Concrete Crack Width Measurement System
Built with agno AI Agent Framework
https://github.com/anthropics/agno
```

## Support

For issues or questions:
- Open an issue on GitHub
- Check agno documentation: https://docs.agno.ai
- Contact your agno support representative

---

**⚠️ Important Notice**: This tool is designed to assist professional inspectors but should not replace qualified structural engineering assessment for critical applications. Always consult with licensed engineers for structural concerns.
