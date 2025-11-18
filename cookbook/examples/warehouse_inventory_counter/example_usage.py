"""
Example usage of Warehouse Inventory Counter
Demonstrates how to use the detector and OCR programmatically
"""

from detector import WarehouseDetector
from ocr_reader import OCRReader
import cv2


def example_basic_detection():
    """Basic product detection example"""
    print("=" * 60)
    print("Example 1: Basic Product Detection")
    print("=" * 60)

    # Initialize detector
    detector = WarehouseDetector(
        model_name="yolov8n.pt",
        confidence_threshold=0.4
    )

    # Detect products (use your own image)
    image_path = "warehouse_shelf.jpg"

    try:
        detections, annotated_image = detector.detect(image_path)

        print(f"\n✅ Detected {len(detections)} products")

        # Show counts by category
        counts = detector.count_products(detections)
        print("\n📊 Products by category:")
        for category, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {category}: {count}")

        # Save annotated image
        cv2.imwrite("detected_products.jpg", annotated_image)
        print("\n💾 Saved annotated image to: detected_products.jpg")

    except FileNotFoundError:
        print(f"\n⚠️  Image not found: {image_path}")
        print("Please provide a warehouse shelf image to test.")


def example_detection_with_ocr():
    """Product detection with OCR text recognition"""
    print("\n" + "=" * 60)
    print("Example 2: Detection with OCR")
    print("=" * 60)

    # Initialize detector and OCR
    detector = WarehouseDetector(confidence_threshold=0.4)
    ocr_reader = OCRReader(languages=['tr', 'en'])

    image_path = "warehouse_shelf.jpg"

    try:
        # Detect products
        detections, annotated_image = detector.detect(image_path)
        print(f"\n✅ Detected {len(detections)} products")

        # Read labels
        if len(detections) > 0:
            print("\n📝 Reading product labels...")
            detections_with_text = ocr_reader.read_labels(image_path, detections)

            # Display results
            print("\n📋 Detailed product information:")
            for i, det in enumerate(detections_with_text, 1):
                ocr_text = det.get('ocr_text', 'N/A')
                print(f"\n  Product {i}:")
                print(f"    Type: {det['class']}")
                print(f"    Confidence: {det['confidence']:.2%}")
                print(f"    Label: {ocr_text if ocr_text else '(no text detected)'}")

    except FileNotFoundError:
        print(f"\n⚠️  Image not found: {image_path}")
        print("Please provide a warehouse shelf image to test.")


def example_batch_processing():
    """Process multiple images"""
    print("\n" + "=" * 60)
    print("Example 3: Batch Processing")
    print("=" * 60)

    from pathlib import Path

    detector = WarehouseDetector(confidence_threshold=0.4)

    # Process all images in a directory
    images_dir = Path("warehouse_images")

    if not images_dir.exists():
        print(f"\n⚠️  Directory not found: {images_dir}")
        print("Create a 'warehouse_images' folder and add shelf photos to test.")
        return

    image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))

    if not image_files:
        print(f"\n⚠️  No images found in {images_dir}")
        return

    print(f"\n📁 Processing {len(image_files)} images...\n")

    total_products = 0
    results = []

    for image_path in image_files:
        detections, _ = detector.detect(str(image_path))
        total_products += len(detections)

        result = {
            'filename': image_path.name,
            'product_count': len(detections),
            'categories': detector.count_products(detections)
        }
        results.append(result)

        print(f"  ✓ {image_path.name}: {len(detections)} products")

    print(f"\n📊 Summary:")
    print(f"  Total images: {len(image_files)}")
    print(f"  Total products: {total_products}")
    print(f"  Average products/image: {total_products/len(image_files):.1f}")


def example_custom_filtering():
    """Filter detections by specific product types"""
    print("\n" + "=" * 60)
    print("Example 4: Custom Filtering")
    print("=" * 60)

    detector = WarehouseDetector(confidence_threshold=0.4)
    image_path = "warehouse_shelf.jpg"

    try:
        detections, _ = detector.detect(image_path)

        # Filter for specific product types
        # Common COCO classes: 'bottle', 'cup', 'bowl', 'book', etc.
        target_classes = ['bottle', 'cup', 'book']

        filtered = detector.filter_by_class(detections, target_classes)

        print(f"\n✅ Total detections: {len(detections)}")
        print(f"🎯 Filtered ({', '.join(target_classes)}): {len(filtered)}")

        if len(filtered) > 0:
            counts = detector.count_products(filtered)
            print(f"\n📊 Breakdown:")
            for category, count in counts.items():
                print(f"  - {category}: {count}")

    except FileNotFoundError:
        print(f"\n⚠️  Image not found: {image_path}")


def example_spatial_analysis():
    """Analyze product positions on shelf"""
    print("\n" + "=" * 60)
    print("Example 5: Spatial Analysis")
    print("=" * 60)

    detector = WarehouseDetector(confidence_threshold=0.4)
    image_path = "warehouse_shelf.jpg"

    try:
        detections, _ = detector.detect(image_path)

        # Get product positions
        positions = detector.get_product_positions(detections)

        print(f"\n✅ Analyzing {len(positions)} product positions")

        # Group by horizontal position (shelf levels)
        # Assuming standard shelf height ~300 pixels
        shelf_levels = {}

        for class_name, x, y in positions:
            level = int(y // 300)  # Rough shelf level
            if level not in shelf_levels:
                shelf_levels[level] = []
            shelf_levels[level].append(class_name)

        print(f"\n📐 Products by shelf level:")
        for level in sorted(shelf_levels.keys()):
            products = shelf_levels[level]
            print(f"  Level {level}: {len(products)} products")
            # Show first few
            sample = products[:3]
            if len(products) > 3:
                sample.append(f"... +{len(products)-3} more")
            print(f"    ({', '.join(sample)})")

    except FileNotFoundError:
        print(f"\n⚠️  Image not found: {image_path}")


def main():
    """Run all examples"""
    print("\n🚀 Warehouse Inventory Counter - Example Usage\n")

    # Run examples
    example_basic_detection()
    example_detection_with_ocr()
    example_batch_processing()
    example_custom_filtering()
    example_spatial_analysis()

    print("\n" + "=" * 60)
    print("✅ Examples completed!")
    print("=" * 60)
    print("\n💡 To use the web interface, run:")
    print("   streamlit run app.py")
    print("\n📚 For more information, see README.md")


if __name__ == "__main__":
    main()
