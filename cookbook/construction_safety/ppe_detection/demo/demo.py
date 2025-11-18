#!/usr/bin/env python3
"""
PPE Detection Interactive Demo

This script provides an interactive demo of the PPE detection system,
showcasing image processing, video processing, and real-time detection capabilities.
"""

import sys
import os
from pathlib import Path
import cv2
import numpy as np
from datetime import datetime
from typing import Optional, List, Dict
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.ppe_detector import PPEDetector, ComplianceResult
from src.models.model_config import default_config


class PPEDemo:
    """Interactive PPE Detection Demo"""

    def __init__(self, output_dir: str = "./output"):
        """Initialize demo with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.demo_images_dir = Path(__file__).parent / "data" / "demo_images"
        self.demo_videos_dir = Path(__file__).parent / "data" / "demo_videos"

        print("=" * 80)
        print("KKD (PPE) TESPİT SİSTEMİ - İNTERAKTİF DEMO")
        print("PPE Detection System - Interactive Demo")
        print("=" * 80)
        print()

        # Initialize detector
        print("Sistem başlatılıyor... / Initializing system...")
        self.detector = PPEDetector(verbose=True)
        print("\n✓ Sistem hazır! / System ready!\n")

    def demo_image_processing(self, image_path: Optional[str] = None):
        """Demo: Process a single image"""
        print("\n" + "=" * 80)
        print("DEMO 1: TEK GÖRÜNTÜ ANALİZİ / SINGLE IMAGE ANALYSIS")
        print("=" * 80)

        if image_path is None:
            # Use demo images
            demo_images = list(self.demo_images_dir.glob("*.jpg")) + \
                         list(self.demo_images_dir.glob("*.png"))

            if not demo_images:
                print("⚠ Demo görüntüleri bulunamadı / No demo images found")
                return

            image_path = str(demo_images[0])

        print(f"\nGörüntü işleniyor / Processing image: {image_path}")

        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Görüntü yüklenemedi / Failed to load image: {image_path}")
            return

        print(f"Görüntü boyutu / Image size: {image.shape[1]}x{image.shape[0]}")

        # Detect PPE
        print("\n1. KKD tespit ediliyor / Detecting PPE...")
        detections = self.detector.detect_ppe(image)
        print(f"   ✓ {len(detections)} nesne tespit edildi / objects detected")

        # Analyze compliance
        print("\n2. Uyumluluk kontrol ediliyor / Checking compliance...")
        compliance_results = self.detector.is_compliant(detections)

        # Print results
        print(f"\n   Toplam işçi / Total workers: {len(compliance_results)}")
        compliant = sum(1 for r in compliance_results if r.is_compliant)
        non_compliant = len(compliance_results) - compliant

        print(f"   ✓ Uyumlu / Compliant: {compliant}")
        print(f"   ✗ Uyumsuz / Non-compliant: {non_compliant}")

        # Detail each person
        print("\n   Detaylı sonuçlar / Detailed results:")
        for i, result in enumerate(compliance_results, 1):
            status_emoji = "✓" if result.is_compliant else "✗"
            print(f"   {status_emoji} İşçi {i} / Worker {i}: {result.compliance_status}")
            print(f"      - Baret / Helmet: {'Var/Yes' if result.has_helmet else 'Yok/No'}")
            print(f"      - Yelek / Vest: {'Var/Yes' if result.has_vest else 'Yok/No'}")

        # Visualize and save
        print("\n3. Görselleştirme oluşturuluyor / Creating visualization...")
        output_image = self.detector.visualize_compliance(image, compliance_results)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"demo_image_{timestamp}.jpg"
        cv2.imwrite(str(output_path), output_image)

        print(f"   ✓ Sonuç kaydedildi / Result saved: {output_path}")

        # Display image (if running with display)
        try:
            cv2.imshow('PPE Detection Demo', output_image)
            print("\n[Görüntü gösteriliyor - kapatmak için bir tuşa basın]")
            print("[Image displayed - press any key to close]")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        except:
            print("   (Görüntü GUI olmadan gösterilemiyor / Cannot display without GUI)")

    def demo_batch_processing(self):
        """Demo: Process multiple images"""
        print("\n" + "=" * 80)
        print("DEMO 2: TOPLU GÖRÜNTÜ ANALİZİ / BATCH IMAGE PROCESSING")
        print("=" * 80)

        demo_images = list(self.demo_images_dir.glob("*.jpg")) + \
                     list(self.demo_images_dir.glob("*.png"))

        if not demo_images:
            print("⚠ Demo görüntüleri bulunamadı / No demo images found")
            return

        print(f"\n{len(demo_images)} görüntü bulundu / images found")
        print("İşleniyor / Processing...\n")

        batch_stats = {
            "total_images": len(demo_images),
            "total_workers": 0,
            "total_compliant": 0,
            "total_non_compliant": 0,
            "images_processed": 0
        }

        for i, img_path in enumerate(demo_images, 1):
            print(f"[{i}/{len(demo_images)}] {img_path.name}")

            try:
                # Process image
                image = cv2.imread(str(img_path))
                if image is None:
                    print(f"  ⚠ Atlayıldı / Skipped")
                    continue

                detections = self.detector.detect_ppe(image)
                compliance_results = self.detector.is_compliant(detections)

                # Update stats
                batch_stats["images_processed"] += 1
                batch_stats["total_workers"] += len(compliance_results)
                batch_stats["total_compliant"] += sum(1 for r in compliance_results if r.is_compliant)
                batch_stats["total_non_compliant"] += sum(1 for r in compliance_results if not r.is_compliant)

                # Save annotated image
                output_image = self.detector.visualize_compliance(image, compliance_results)
                output_path = self.output_dir / f"batch_{img_path.stem}_annotated.jpg"
                cv2.imwrite(str(output_path), output_image)

                print(f"  ✓ {len(compliance_results)} işçi tespit edildi / workers detected")

            except Exception as e:
                print(f"  ❌ Hata / Error: {e}")

        # Print summary
        print("\n" + "=" * 80)
        print("TOPLU ANALİZ SONUÇLARI / BATCH PROCESSING SUMMARY")
        print("=" * 80)
        print(f"İşlenen görüntü / Images processed: {batch_stats['images_processed']}/{batch_stats['total_images']}")
        print(f"Toplam işçi / Total workers: {batch_stats['total_workers']}")
        print(f"Uyumlu / Compliant: {batch_stats['total_compliant']}")
        print(f"Uyumsuz / Non-compliant: {batch_stats['total_non_compliant']}")

        if batch_stats['total_workers'] > 0:
            compliance_rate = (batch_stats['total_compliant'] / batch_stats['total_workers']) * 100
            print(f"Uyumluluk oranı / Compliance rate: {compliance_rate:.1f}%")

    def demo_video_processing(self, video_path: Optional[str] = None):
        """Demo: Process video"""
        print("\n" + "=" * 80)
        print("DEMO 3: VİDEO ANALİZİ / VIDEO PROCESSING")
        print("=" * 80)

        if video_path is None:
            # Use demo videos
            demo_videos = list(self.demo_videos_dir.glob("*.mp4")) + \
                         list(self.demo_videos_dir.glob("*.avi"))

            if not demo_videos:
                print("⚠ Demo videoları bulunamadı / No demo videos found")
                return

            video_path = str(demo_videos[0])

        print(f"\nVideo işleniyor / Processing video: {video_path}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"demo_video_{timestamp}.mp4"

        # Process video
        stats = self.detector.process_video(
            video_path=video_path,
            output_path=output_path,
            show_preview=False,
            check_compliance=True
        )

        # Print results
        print("\n" + "=" * 80)
        print("VİDEO ANALİZ SONUÇLARI / VIDEO PROCESSING RESULTS")
        print("=" * 80)
        print(f"Toplam kare / Total frames: {stats['total_frames']}")
        print(f"İşlenen kare / Processed frames: {stats['processed_frames']}")
        print(f"FPS: {stats['fps']}")
        print(f"Çözünürlük / Resolution: {stats['resolution'][0]}x{stats['resolution'][1]}")
        print(f"Çıktı dosyası / Output file: {output_path}")

        # Print detection stats
        detector_stats = self.detector.get_statistics()
        print(f"\nToplam tespit / Total detections: {detector_stats['total_detections']}")
        print(f"Toplam işçi / Total workers: {detector_stats['total_persons_detected']}")
        print(f"Uyumlu / Compliant: {detector_stats['total_compliant']}")
        print(f"Uyumsuz / Non-compliant: {detector_stats['total_non_compliant']}")
        if detector_stats['total_persons_detected'] > 0:
            print(f"Uyumluluk oranı / Compliance rate: {detector_stats['compliance_rate']*100:.1f}%")

    def demo_camera_feed(self, camera_id: int = 0):
        """Demo: Real-time camera feed (if available)"""
        print("\n" + "=" * 80)
        print("DEMO 4: CANLI KAMERA AKIŞI / REAL-TIME CAMERA FEED")
        print("=" * 80)

        print(f"\nKamera açılıyor / Opening camera {camera_id}...")

        cap = cv2.VideoCapture(camera_id)

        if not cap.isOpened():
            print("❌ Kamera açılamadı / Cannot open camera")
            print("   Kamera cihazı bağlı değil veya kullanımda / Camera not connected or in use")
            return

        print("✓ Kamera hazır! / Camera ready!")
        print("\nTuşlar / Controls:")
        print("  'q' - Çıkış / Quit")
        print("  's' - Ekran görüntüsü kaydet / Save screenshot")

        frame_count = 0
        screenshot_count = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Kare okunamadı / Cannot read frame")
                    break

                frame_count += 1

                # Process every N frames for performance
                if frame_count % 2 == 0:
                    # Detect PPE
                    detections = self.detector.detect_ppe(frame)
                    compliance_results = self.detector.is_compliant(detections)

                    # Visualize
                    output_frame = self.detector.visualize_compliance(frame, compliance_results)

                    # Add stats overlay
                    compliant = sum(1 for r in compliance_results if r.is_compliant)
                    non_compliant = len(compliance_results) - compliant

                    cv2.putText(output_frame, f"Workers: {len(compliance_results)}",
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.putText(output_frame, f"Compliant: {compliant}",
                               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(output_frame, f"Non-compliant: {non_compliant}",
                               (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    output_frame = frame

                # Display
                cv2.imshow('PPE Detection - Live Feed', output_frame)

                # Handle keyboard
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\nÇıkılıyor / Quitting...")
                    break
                elif key == ord('s'):
                    screenshot_count += 1
                    screenshot_path = self.output_dir / f"screenshot_{screenshot_count}.jpg"
                    cv2.imwrite(str(screenshot_path), output_frame)
                    print(f"✓ Ekran görüntüsü kaydedildi / Screenshot saved: {screenshot_path}")

        finally:
            cap.release()
            cv2.destroyAllWindows()
            print(f"\nToplam kare işlendi / Total frames processed: {frame_count}")

    def generate_demo_report(self):
        """Generate comprehensive demo report"""
        print("\n" + "=" * 80)
        print("DEMO RAPORU OLUŞTURULUYOR / GENERATING DEMO REPORT")
        print("=" * 80)

        stats = self.detector.get_statistics()

        report = f"""

KKD TESPİT SİSTEMİ - DEMO RAPORU
PPE DETECTION SYSTEM - DEMO REPORT
{'=' * 80}

Tarih / Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

SİSTEM İSTATİSTİKLERİ / SYSTEM STATISTICS
{'-' * 80}
Toplam işlenen kare / Total frames processed: {stats['total_frames_processed']}
Toplam tespit / Total detections: {stats['total_detections']}
Toplam işçi / Total workers detected: {stats['total_persons_detected']}

UYUMLULUK ANALİZİ / COMPLIANCE ANALYSIS
{'-' * 80}
Uyumlu işçi / Compliant workers: {stats['total_compliant']}
Uyumsuz işçi / Non-compliant workers: {stats['total_non_compliant']}
Uyumluluk oranı / Compliance rate: {stats['compliance_rate']*100:.1f}%

YAPAY ZEKA MODELİ / AI MODEL
{'-' * 80}
Model: {self.detector.config.model_architecture}
Cihaz / Device: {self.detector.config.device}
Güven eşiği / Confidence threshold: {self.detector.config.confidence_threshold}

SİSTEM YETENEKLERİ / SYSTEM CAPABILITIES
{'-' * 80}
✓ Baret tespiti / Helmet detection
✓ Yelek tespiti / Safety vest detection
✓ Çoklu işçi tespiti / Multiple worker detection
✓ Gerçek zamanlı analiz / Real-time analysis
✓ Video işleme / Video processing
✓ Toplu görüntü analizi / Batch image processing
✓ Otomatik uyumluluk kontrolü / Automatic compliance checking
✓ Detaylı raporlama / Detailed reporting

{'=' * 80}

        """

        # Save report
        report_path = self.output_dir / f"demo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(report)
        print(f"✓ Rapor kaydedildi / Report saved: {report_path}")

        return report_path


def main():
    """Main demo function"""
    parser = argparse.ArgumentParser(
        description="KKD Tespit Sistemi İnteraktif Demo / PPE Detection System Interactive Demo"
    )
    parser.add_argument(
        '--mode',
        choices=['image', 'batch', 'video', 'camera', 'report', 'all'],
        default='all',
        help='Demo modu / Demo mode'
    )
    parser.add_argument(
        '--image',
        type=str,
        help='İşlenecek görüntü dosyası / Image file to process'
    )
    parser.add_argument(
        '--video',
        type=str,
        help='İşlenecek video dosyası / Video file to process'
    )
    parser.add_argument(
        '--camera',
        type=int,
        default=0,
        help='Kamera ID / Camera ID (default: 0)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='./output',
        help='Çıktı dizini / Output directory'
    )

    args = parser.parse_args()

    # Create demo instance
    demo = PPEDemo(output_dir=args.output)

    # Run demo based on mode
    if args.mode == 'image' or args.mode == 'all':
        demo.demo_image_processing(args.image)

    if args.mode == 'batch' or args.mode == 'all':
        demo.demo_batch_processing()

    if args.mode == 'video' or args.mode == 'all':
        demo.demo_video_processing(args.video)

    if args.mode == 'camera':
        demo.demo_camera_feed(args.camera)

    if args.mode == 'report' or args.mode == 'all':
        demo.generate_demo_report()

    print("\n" + "=" * 80)
    print("DEMO TAMAMLANDI / DEMO COMPLETE")
    print("=" * 80)
    print(f"\nÇıktı dosyaları / Output files: {args.output}")
    print("\nTeşekkürler! / Thank you!")


if __name__ == "__main__":
    main()
