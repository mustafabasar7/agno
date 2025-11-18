"""
Example: Process video with optimized PPE detection.

This script demonstrates:
1. Loading an optimized model
2. Processing video with frame skipping
3. Real-time performance monitoring
4. Saving annotated video
"""

import sys
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.optimization import (
    OptimizationConfig,
    VideoInferenceEngine,
    PresetConfigs
)


def process_video_with_stats(
    model_path: str,
    video_path: str,
    output_path: str,
    config: OptimizationConfig
):
    """Process video and display statistics."""
    print("=" * 80)
    print("Video Processing with Optimized PPE Detection")
    print("=" * 80)

    print(f"\nConfiguration:")
    print(f"  Model: {model_path}")
    print(f"  Video: {video_path}")
    print(f"  Output: {output_path}")
    print(f"  Input size: {config.input_size}")
    print(f"  Frame skip: {config.frame_skip}")

    # Create inference engine
    engine = VideoInferenceEngine(model_path, config)

    # Statistics collector
    violation_count = 0
    total_detections = 0
    frames_with_detections = 0

    def frame_callback(frame, results, frame_number):
        """Callback for each processed frame."""
        nonlocal violation_count, total_detections, frames_with_detections

        detections = results["detections"]
        total_detections += len(detections)

        if detections:
            frames_with_detections += 1

        # Count PPE violations (example logic)
        for det in detections:
            class_name = det["class_name"].lower()
            if "no" in class_name or "missing" in class_name:
                violation_count += 1

        # Print progress every 100 frames
        if frame_number % 100 == 0:
            fps = results.get("fps", 0)
            print(f"Frame {frame_number}: {len(detections)} detections, FPS: {fps:.2f}")

    # Process video
    print("\nProcessing video...")
    start_time = time.time()

    stats = engine.process_video(
        video_path=video_path,
        output_path=output_path,
        display=False,  # Set to True to display in real-time
        callback=frame_callback
    )

    processing_time = time.time() - start_time

    # Print results
    print("\n" + "=" * 80)
    print("Processing Complete!")
    print("=" * 80)

    print(f"\nVideo Statistics:")
    print(f"  Total frames: {stats['total_frames']}")
    print(f"  Processed frames: {stats['processed_frames']}")
    print(f"  Processing time: {processing_time:.2f} seconds")
    print(f"  Effective FPS: {stats['effective_fps']:.2f}")
    print(f"  Original video FPS: {stats['video_fps']:.2f}")
    print(f"  Speedup factor: {stats['speedup_factor']:.2f}x")

    print(f"\nDetection Statistics:")
    print(f"  Total detections: {total_detections}")
    print(f"  Frames with detections: {frames_with_detections}")
    print(f"  Average detections per frame: {total_detections / stats['processed_frames']:.2f}")
    print(f"  Potential violations: {violation_count}")

    print(f"\nPerformance:")
    perf_stats = engine.get_performance_stats()
    print(f"  Average FPS: {perf_stats['avg_fps']:.2f}")
    print(f"  Average latency: {perf_stats['avg_inference_time_ms']:.2f} ms")
    print(f"  Preprocessing: {perf_stats['avg_preprocessing_time_ms']:.2f} ms")

    print(f"\nOutput saved to: {output_path}")


def main():
    """Main video processing workflow."""
    # Choose optimization preset
    # Options: high_accuracy, balanced, high_performance, maximum_speed, edge_device
    config = PresetConfigs.get_high_performance()

    # Or create custom configuration for video processing
    # config = OptimizationConfig()
    # config.level = OptimizationLevel.LEVEL_2_ONNX
    # config.input_size = (416, 416)  # Smaller for faster processing
    # config.frame_skip = 3  # Process every 3rd frame
    # config.enable_frame_skip = True

    # Paths
    model_path = "optimized_models/yolov8n_optimized.onnx"
    video_path = "data/sample_videos/construction_site.mp4"
    output_path = "output/processed_video.mp4"

    # Check if files exist
    if not Path(model_path).exists():
        print(f"ERROR: Model not found at {model_path}")
        print("Please run optimize_model_example.py first to create an optimized model")
        return

    if not Path(video_path).exists():
        print(f"WARNING: Video not found at {video_path}")
        print("Please provide a video file or update the path")
        return

    # Process video
    process_video_with_stats(
        model_path=model_path,
        video_path=video_path,
        output_path=output_path,
        config=config
    )


if __name__ == "__main__":
    main()
