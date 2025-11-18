"""
Example usage of PPE Detection system

This script demonstrates how to use the PPE detector for various tasks:
- Single image detection
- Video processing
- Compliance checking
- Custom configurations
"""

import cv2
import numpy as np
from pathlib import Path

from ppe_detector import PPEDetector, Detection, ComplianceResult
from model_config import ModelConfig, ConfigPresets


def example_image_detection():
    """Example: Detect PPE in a single image."""
    print("="*60)
    print("Example 1: Single Image Detection")
    print("="*60)

    # Initialize detector
    detector = PPEDetector(verbose=True)

    # Example with numpy array (simulated image)
    # In practice, load real image: image = cv2.imread("path/to/image.jpg")
    dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)

    # Detect PPE
    detections = detector.detect_ppe(dummy_image)

    print(f"\nFound {len(detections)} detections:")
    for i, det in enumerate(detections):
        print(f"  {i+1}. {det.class_name}: {det.confidence:.2f} at {det.bbox}")

    # Visualize (would save/display in practice)
    # visualized = detector.visualize_detections(dummy_image, detections)
    # cv2.imwrite("output.jpg", visualized)

    return detector, detections


def example_compliance_checking():
    """Example: Check PPE compliance for detected persons."""
    print("\n" + "="*60)
    print("Example 2: PPE Compliance Checking")
    print("="*60)

    detector = PPEDetector(verbose=True)

    # Simulate image with detections
    dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)

    # Detect PPE
    detections = detector.detect_ppe(dummy_image)

    # Check compliance
    compliance_results = detector.is_compliant(detections)

    print(f"\nCompliance Results:")
    for i, result in enumerate(compliance_results):
        print(f"\n  Person {i+1}:")
        print(f"    Status: {result.compliance_status}")
        print(f"    Has Helmet: {result.has_helmet}")
        print(f"    Has Vest: {result.has_vest}")
        print(f"    Confidence: {result.confidence_score:.2f}")

    # Visualize compliance
    # compliance_viz = detector.visualize_compliance(dummy_image, compliance_results)
    # cv2.imwrite("compliance_output.jpg", compliance_viz)

    # Get statistics
    stats = detector.get_statistics()
    print(f"\nStatistics:")
    print(f"  Total persons: {stats['total_persons_detected']}")
    print(f"  Compliant: {stats['total_compliant']}")
    print(f"  Non-compliant: {stats['total_non_compliant']}")
    print(f"  Compliance rate: {stats['compliance_rate']:.1%}")


def example_video_processing():
    """Example: Process video file."""
    print("\n" + "="*60)
    print("Example 3: Video Processing")
    print("="*60)

    # Use fast inference config for video
    config = ConfigPresets.video_processing()
    detector = PPEDetector(config=config, verbose=True)

    # Process video (example - would need actual video file)
    # video_path = "path/to/construction_site.mp4"
    # output_path = "path/to/output_with_detection.mp4"
    #
    # stats = detector.process_video(
    #     video_path=video_path,
    #     output_path=output_path,
    #     show_preview=False,
    #     check_compliance=True
    # )
    #
    # print(f"\nVideo processing complete!")
    # print(f"  Processed {stats['processed_frames']} frames")
    # print(f"  Output saved to: {stats['output_path']}")

    print("\nVideo processing requires actual video file.")
    print("Usage: detector.process_video(video_path, output_path)")


def example_custom_configuration():
    """Example: Use custom configuration."""
    print("\n" + "="*60)
    print("Example 4: Custom Configuration")
    print("="*60)

    # Create custom configuration
    config = ModelConfig()
    config.confidence_threshold = 0.7  # Higher confidence
    config.input_size = (640, 640)
    config.device = "cpu"

    # Or use preset
    # config = ConfigPresets.high_accuracy()
    # config = ConfigPresets.fast_inference()
    # config = ConfigPresets.production()

    print("\nCustom Configuration:")
    print(config.get_summary())

    detector = PPEDetector(config=config, verbose=True)
    print("\nDetector initialized with custom configuration!")


def example_real_image_workflow():
    """Example: Complete workflow with real image."""
    print("\n" + "="*60)
    print("Example 5: Complete Real Image Workflow")
    print("="*60)

    # Initialize detector
    detector = PPEDetector(verbose=True)

    # In practice, you would load a real image:
    # image_path = "construction_site.jpg"
    # image = cv2.imread(image_path)

    # For demo, create sample image
    image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)

    # Step 1: Detect PPE
    print("\nStep 1: Detecting PPE...")
    detections = detector.detect_ppe(image)
    print(f"Found {len(detections)} objects")

    # Step 2: Check compliance
    print("\nStep 2: Checking compliance...")
    compliance_results = detector.is_compliant(detections)
    print(f"Analyzed {len(compliance_results)} persons")

    # Step 3: Visualize results
    print("\nStep 3: Visualizing results...")

    # Option A: Show all detections
    detection_viz = detector.visualize_detections(
        image,
        detections,
        show_labels=True,
        show_confidence=True
    )

    # Option B: Show compliance status
    compliance_viz = detector.visualize_compliance(
        image,
        compliance_results,
        show_details=True
    )

    # Save results
    # cv2.imwrite("detections.jpg", detection_viz)
    # cv2.imwrite("compliance.jpg", compliance_viz)

    print("\nWorkflow complete!")
    print("In production, save images with cv2.imwrite()")


def example_model_fine_tuning():
    """Example: Fine-tune model on custom dataset."""
    print("\n" + "="*60)
    print("Example 6: Model Fine-tuning")
    print("="*60)

    print("\nFine-tuning requires a custom dataset in YOLO format:")
    print("  - dataset.yaml: Dataset configuration")
    print("  - images/: Training and validation images")
    print("  - labels/: Corresponding annotations")

    # Example fine-tuning code (requires dataset)
    # detector = PPEDetector(verbose=True)
    #
    # detector.fine_tune(
    #     dataset_yaml="data/ppe_dataset/dataset.yaml",
    #     epochs=100,
    #     batch=16,
    #     imgsz=640
    # )
    #
    # # Save fine-tuned model
    # detector.save_model("models/weights/ppe_detector_best.pt")

    print("\nFor fine-tuning, prepare your dataset and use:")
    print("  detector.fine_tune(dataset_yaml='path/to/dataset.yaml')")


def example_batch_processing():
    """Example: Process multiple images in batch."""
    print("\n" + "="*60)
    print("Example 7: Batch Image Processing")
    print("="*60)

    detector = PPEDetector(verbose=True)

    # Example: Process multiple images
    image_paths = [
        # "images/site1.jpg",
        # "images/site2.jpg",
        # "images/site3.jpg",
    ]

    results = []

    # for img_path in image_paths:
    #     image = cv2.imread(img_path)
    #     detections = detector.detect_ppe(image)
    #     compliance = detector.is_compliant(detections)
    #
    #     results.append({
    #         "image": img_path,
    #         "detections": detections,
    #         "compliance": compliance
    #     })
    #
    #     # Visualize and save
    #     viz = detector.visualize_compliance(image, compliance)
    #     output_path = f"output/{Path(img_path).stem}_result.jpg"
    #     cv2.imwrite(output_path, viz)

    # Get overall statistics
    # stats = detector.get_statistics()
    # print(f"\nBatch Processing Statistics:")
    # print(f"  Images processed: {len(image_paths)}")
    # print(f"  Total persons: {stats['total_persons_detected']}")
    # print(f"  Compliance rate: {stats['compliance_rate']:.1%}")

    print("\nBatch processing example shown in comments.")
    print("Uncomment code and provide image paths to run.")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("PPE Detection System - Usage Examples")
    print("="*60)

    try:
        # Run examples
        example_image_detection()
        example_compliance_checking()
        example_video_processing()
        example_custom_configuration()
        example_real_image_workflow()
        example_model_fine_tuning()
        example_batch_processing()

        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60)

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
