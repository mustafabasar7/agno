# PPE Detection Model Optimization Guide

Complete guide to optimizing YOLO models for real-time PPE detection on CPU.

## Performance Targets

The optimization package is designed to achieve:

| Metric | Target | Typical Result |
|--------|--------|----------------|
| FPS (CPU) | ≥ 10 | 12-18 FPS |
| Memory | ≤ 500 MB | 300-400 MB |
| Model Size | ≤ 50 MB | 1.5-6 MB |
| Accuracy (mAP@50) | ≥ 85% | 84-88% |

## Quick Start

### 1. Install Dependencies

```bash
cd cookbook/construction_safety/ppe_detection
pip install -r src/models/optimization/requirements.txt
```

### 2. Test Installation

```bash
python examples/test_optimization.py
```

### 3. Optimize Your Model

```bash
python examples/optimize_model_example.py
```

## Step-by-Step Optimization

### Step 1: Choose Configuration

Select a preset based on your requirements:

```python
from models.optimization import PresetConfigs

# For best accuracy (slower)
config = PresetConfigs.get_high_accuracy()

# For balanced performance (recommended)
config = PresetConfigs.get_balanced()

# For maximum speed
config = PresetConfigs.get_maximum_speed()

# For edge devices (Raspberry Pi, etc.)
config = PresetConfigs.get_edge_device()
```

### Step 2: Optimize Model

```python
from models.optimization import ModelOptimizer

optimizer = ModelOptimizer(config)
results = optimizer.optimize_model(
    model_path="models/yolov8n.pt",
    output_dir="optimized_models/",
    calibration_data=calibration_images  # Optional, for quantization
)

print(f"Original: {results['original_size_mb']:.2f} MB")
print(f"Optimized: {results['optimized_size_mb']:.2f} MB")
print(f"Reduction: {results['size_reduction_percent']:.2f}%")
```

### Step 3: Benchmark Performance

```python
from models.optimization import PerformanceBenchmark

benchmark = PerformanceBenchmark(config)

# Benchmark optimized model
metrics = benchmark.benchmark_model(
    model_path=results['onnx_model'],
    test_images=test_images,
    ground_truth=annotations  # Optional
)

# Check if targets are met
validation = metrics['target_validation']
if validation['all_targets_met']:
    print("✓ All targets met!")
else:
    print("Targets not met:", validation['targets_met'])
```

### Step 4: Deploy

```python
from models.optimization import InferenceEngine

# Create engine with optimized model
engine = InferenceEngine(
    model_path="optimized_models/yolov8n_optimized.onnx",
    config=config
)

# Process images
for image in images:
    results = engine.predict(image)
    # Use results...
```

## Optimization Techniques

### Technique 1: Reduce Input Size

**Impact**: 2-4x faster
**Accuracy loss**: 5-10%

```python
config.input_size = (416, 416)  # Instead of (640, 640)
```

**When to use**:
- Need immediate performance boost
- Accuracy is acceptable
- Limited computational resources

### Technique 2: ONNX Conversion

**Impact**: 2-3x faster on CPU
**Accuracy loss**: < 1%

```python
config.level = OptimizationLevel.LEVEL_2_ONNX
config.onnx_simplify = True
config.onnx_dynamic_axes = True
```

**When to use**:
- CPU deployment
- Minimal accuracy loss required
- **Recommended for most use cases**

### Technique 3: Quantization

**Impact**: 3-4x faster, 75% smaller
**Accuracy loss**: 2-5%

```python
config.level = OptimizationLevel.LEVEL_3_QUANTIZATION

# Dynamic quantization (no calibration needed)
config.quantization_type = QuantizationType.DYNAMIC

# OR Static quantization (better accuracy, needs calibration)
config.quantization_type = QuantizationType.STATIC
config.quantization_calibration_samples = 100
```

**When to use**:
- Need maximum speed
- Model size is important (mobile/edge)
- Can accept slight accuracy reduction

### Technique 4: Frame Skipping (Video Only)

**Impact**: 2-5x faster for video
**Accuracy loss**: Minimal (temporal smoothing)

```python
config.enable_frame_skip = True
config.frame_skip = 3  # Process every 3rd frame
```

**When to use**:
- Processing video streams
- Scene doesn't change rapidly
- Need real-time performance

### Technique 5: Batch Processing

**Impact**: 1.5-2x faster
**Latency**: Increased (must wait for batch)

```python
config.batch_size = 4  # Process 4 frames at once
```

**When to use**:
- Processing recorded videos
- Multiple camera streams
- Latency is not critical

## Hardware-Specific Optimization

### Intel CPU

```python
config = OptimizationConfig()
config.level = OptimizationLevel.LEVEL_2_ONNX
config.num_threads = 4  # Match your CPU cores
config.device = "cpu"
config.input_size = (640, 640)
```

### AMD CPU

```python
# Similar to Intel
config.num_threads = psutil.cpu_count(logical=False)
```

### Raspberry Pi 4

```python
config = PresetConfigs.get_edge_device()
# Or customize:
config.level = OptimizationLevel.LEVEL_3_QUANTIZATION
config.input_size = (416, 416)
config.num_threads = 2
config.frame_skip = 4
config.batch_size = 1
```

### NVIDIA GPU (Optional)

```python
config.device = "cuda:0"
config.half_precision = True  # FP16
# Install: pip install onnxruntime-gpu
```

## Optimization Workflow

### Development Environment

1. Start with high accuracy configuration
2. Train/fine-tune model
3. Validate on test set

```python
config = PresetConfigs.get_high_accuracy()
# Train and validate...
```

### Testing Environment

1. Test different optimization levels
2. Measure performance vs accuracy trade-off
3. Select best configuration

```python
results = {}
for level in [LEVEL_1, LEVEL_2, LEVEL_3]:
    config.level = level
    # Optimize and benchmark
    results[level] = benchmark_model(...)

# Compare results
compare_models(results)
```

### Production Environment

1. Deploy optimized model
2. Monitor performance
3. Adjust configuration as needed

```python
# Use balanced or high performance
config = PresetConfigs.get_balanced()
engine = InferenceEngine(optimized_model, config)
```

## Common Scenarios

### Scenario 1: Single Camera, Real-Time Detection

**Requirements**: 10 FPS, High accuracy

```python
config = PresetConfigs.get_balanced()
config.level = OptimizationLevel.LEVEL_2_ONNX
config.input_size = (640, 640)
config.frame_skip = 2
```

**Expected**: 12-15 FPS, 86-88% mAP

### Scenario 2: Multiple Cameras (4-8)

**Requirements**: 5 FPS per camera, Moderate accuracy

```python
config = PresetConfigs.get_high_performance()
config.level = OptimizationLevel.LEVEL_3_QUANTIZATION
config.input_size = (416, 416)
config.frame_skip = 3
config.batch_size = 4  # Process all cameras together
```

**Expected**: 6-8 FPS per camera, 82-85% mAP

### Scenario 3: Edge Device (Raspberry Pi)

**Requirements**: 3-5 FPS, Low memory

```python
config = PresetConfigs.get_edge_device()
config.level = OptimizationLevel.LEVEL_3_QUANTIZATION
config.input_size = (320, 320)
config.frame_skip = 5
config.num_threads = 2
config.batch_size = 1
```

**Expected**: 4-6 FPS, 78-82% mAP, < 300 MB RAM

### Scenario 4: Recorded Video Processing

**Requirements**: Process faster than real-time, High accuracy

```python
config = OptimizationConfig()
config.level = OptimizationLevel.LEVEL_2_ONNX
config.input_size = (640, 640)
config.frame_skip = 2
config.batch_size = 8  # Large batches
```

**Expected**: 20-30 FPS (2-3x real-time), 86-88% mAP

## Troubleshooting

### Problem: FPS Too Low

**Solutions**:
1. Reduce input size: `(640, 640)` → `(416, 416)`
2. Increase frame skip: `2` → `3` or `4`
3. Apply quantization: `LEVEL_2_ONNX` → `LEVEL_3_QUANTIZATION`
4. Reduce batch size: `4` → `1`
5. Check CPU usage: Increase `num_threads`

### Problem: Memory Usage Too High

**Solutions**:
1. Use quantized model (75% reduction)
2. Reduce input size
3. Clear cache regularly: `engine.clear_cache()`
4. Reduce batch size
5. Reduce result cache: `engine.cache_size = 5`

### Problem: Accuracy Too Low

**Solutions**:
1. Increase input size: `(416, 416)` → `(640, 640)`
2. Use ONNX instead of quantization
3. Reduce frame skip
4. Use per-channel quantization: `config.quantization_per_channel = True`
5. Use static quantization with more calibration samples

### Problem: Model Conversion Fails

**Solutions**:
1. Update ultralytics: `pip install --upgrade ultralytics`
2. Update ONNX: `pip install --upgrade onnx onnxruntime`
3. Try different opset version: `config.onnx_opset_version = 11`
4. Disable simplification: `config.onnx_simplify = False`

### Problem: Quantization Reduces Accuracy Too Much

**Solutions**:
1. Use dynamic quantization (better than static for small models)
2. Use per-channel quantization: `config.quantization_per_channel = True`
3. Increase calibration samples: `config.quantization_calibration_samples = 200`
4. Fall back to ONNX without quantization

## Benchmarking Best Practices

### 1. Use Representative Test Data

```python
# Good: Real construction site images
test_images = load_construction_images()

# Bad: Random synthetic images
test_images = [np.random.randint(0, 255, (640, 640, 3)) for _ in range(100)]
```

### 2. Include Ground Truth

```python
# Enables accuracy metrics
metrics = benchmark.benchmark_model(
    model_path=model_path,
    test_images=test_images,
    ground_truth=annotations  # Important!
)
```

### 3. Warm Up Properly

```python
# Warmup is automatic, but you can configure it
config.benchmark_warmup_runs = 20  # More for consistent results
config.benchmark_test_runs = 200   # More for statistical significance
```

### 4. Monitor System Resources

```python
# Benchmark includes memory monitoring
memory_metrics = metrics['memory_metrics']
print(f"Peak memory: {memory_metrics['peak_memory_mb']:.2f} MB")
```

### 5. Generate Reports

```python
# Always generate reports for comparison
benchmark.generate_report(
    "reports/benchmark_results.json",
    include_charts=True
)
```

## Advanced Optimization

### Custom Optimization Pipeline

```python
from models.optimization import ModelOptimizer

class CustomOptimizer(ModelOptimizer):
    def optimize_model(self, model_path, output_dir, calibration_data=None):
        # Step 1: Convert to ONNX
        onnx_path = self._convert_to_onnx(model_path, output_dir)

        # Step 2: Custom optimization
        # Your custom logic here

        # Step 3: Quantize
        if self.config.level.value >= 3:
            quantized_path = self._quantize_model(onnx_path, output_dir, calibration_data)

        return results
```

### Custom Inference Pipeline

```python
from models.optimization import InferenceEngine

class CustomInferenceEngine(InferenceEngine):
    def preprocess(self, image):
        # Custom preprocessing
        processed = super().preprocess(image)
        # Additional processing...
        return processed

    def postprocess(self, results, original_shape):
        # Custom postprocessing
        detections = super()._postprocess_results(results, original_shape)
        # Additional logic...
        return detections
```

## Performance Monitoring

### Real-Time Monitoring

```python
engine = InferenceEngine(model_path, config)

# Process with monitoring
for i, frame in enumerate(video_frames):
    result = engine.predict(frame, return_details=True)

    # Monitor every 100 frames
    if i % 100 == 0:
        stats = engine.get_performance_stats()
        print(f"Frame {i}: {stats['avg_fps']:.2f} FPS, "
              f"{stats['avg_inference_time_ms']:.2f} ms")

        # Alert if performance degrades
        if stats['avg_fps'] < config.target_fps:
            print("WARNING: FPS below target!")
            engine.clear_cache()  # Try to free memory
```

### Production Monitoring

```python
import time
import logging

class ProductionEngine:
    def __init__(self, model_path, config):
        self.engine = InferenceEngine(model_path, config)
        self.stats_window = []
        self.alert_threshold = 0.8  # 80% of target

    def process_frame(self, frame):
        start = time.time()
        result = self.engine.predict(frame)
        latency = time.time() - start

        # Track performance
        self.stats_window.append(latency)
        if len(self.stats_window) > 100:
            self.stats_window.pop(0)

        # Check performance
        avg_latency = np.mean(self.stats_window)
        fps = 1.0 / avg_latency
        if fps < config.target_fps * self.alert_threshold:
            logging.warning(f"Performance degraded: {fps:.2f} FPS")

        return result
```

## Deployment Checklist

- [ ] Model optimized for target hardware
- [ ] Benchmarked on representative data
- [ ] All targets met (FPS, memory, accuracy)
- [ ] Tested with real camera streams
- [ ] Error handling implemented
- [ ] Performance monitoring enabled
- [ ] Resource cleanup configured
- [ ] Logging configured
- [ ] Documentation updated
- [ ] Backup/fallback model available

## Next Steps

1. **Test the installation**:
   ```bash
   python examples/test_optimization.py
   ```

2. **Run optimization example**:
   ```bash
   python examples/optimize_model_example.py
   ```

3. **Process a video**:
   ```bash
   python examples/video_processing_example.py
   ```

4. **Read the API documentation**:
   ```bash
   # See src/models/optimization/README.md
   ```

5. **Experiment with different configurations**:
   - Try different optimization levels
   - Test different input sizes
   - Benchmark on your hardware
   - Find optimal configuration for your use case

## Resources

- **API Documentation**: `src/models/optimization/README.md`
- **Examples**: `examples/optimize_model_example.py`, `examples/video_processing_example.py`
- **Test Suite**: `examples/test_optimization.py`
- **Requirements**: `src/models/optimization/requirements.txt`

## Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the examples
3. Check system requirements
4. Verify all dependencies are installed
5. Run the test suite to verify installation

---

**Last Updated**: 2024
**Version**: 1.0.0
