#!/bin/bash

# Full Demo - Complete Feature Showcase
# Tam Demo - Tüm Özelliklerin Gösterimi

set -e

echo "============================================================================"
echo "KKD TESPİT SİSTEMİ - TAM DEMO"
echo "PPE DETECTION SYSTEM - FULL DEMO"
echo "============================================================================"
echo ""
echo "Bu demo tüm sistem özelliklerini gösterir:"
echo "This demo showcases all system features:"
echo ""
echo "  ✓ Tek görüntü analizi / Single image analysis"
echo "  ✓ Toplu görüntü işleme / Batch image processing"
echo "  ✓ Video işleme / Video processing"
echo "  ✓ Detaylı raporlama / Detailed reporting"
echo "  ✓ İstatistikler / Statistics"
echo ""
echo "Tahmini süre / Estimated time: 15-20 dakika / minutes"
echo ""
read -p "Devam etmek için Enter'a basın / Press Enter to continue..."

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DEMO_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$(dirname "$DEMO_DIR")"

cd "$DEMO_DIR"

# Create timestamp for this demo session
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="output/full_demo_$TIMESTAMP"
mkdir -p "$OUTPUT_DIR"

echo ""
echo "📍 Demo dizini / Demo directory: $DEMO_DIR"
echo "📁 Çıktı dizini / Output directory: $OUTPUT_DIR"
echo ""

# System check
echo "============================================================================"
echo "SİSTEM KONTROLÜ / SYSTEM CHECK"
echo "============================================================================"
echo ""

echo "🔍 Python kontrolü / Checking Python..."
python3 --version
echo ""

echo "🔍 Bağımlılıklar kontrol ediliyor / Checking dependencies..."
python3 << EOF
import sys
dependencies = {
    'cv2': 'opencv-python',
    'numpy': 'numpy',
    'ultralytics': 'ultralytics',
}

missing = []
for module, package in dependencies.items():
    try:
        __import__(module)
        print(f"  ✓ {package}")
    except ImportError:
        print(f"  ✗ {package} - EKSIK/MISSING")
        missing.append(package)

if missing:
    print(f"\n⚠ Eksik paketler / Missing packages: {', '.join(missing)}")
    print(f"  Yüklemek için / To install: pip install {' '.join(missing)}")
    sys.exit(1)
else:
    print("\n✓ Tüm bağımlılıklar yüklü / All dependencies installed")
EOF

echo ""

# Check demo data
echo "🔍 Demo verileri kontrol ediliyor / Checking demo data..."
IMAGE_COUNT=$(find data/demo_images -type f \( -name "*.jpg" -o -name "*.png" \) 2>/dev/null | wc -l)
VIDEO_COUNT=$(find data/demo_videos -type f \( -name "*.mp4" -o -name "*.avi" \) 2>/dev/null | wc -l)

echo "  Demo görüntüleri / Demo images: $IMAGE_COUNT"
echo "  Demo videoları / Demo videos: $VIDEO_COUNT"

if [ "$IMAGE_COUNT" -eq 0 ]; then
    echo "  ⚠ Demo görüntüleri bulunamadı / No demo images found"
    echo "    Mock görüntüler oluşturuluyor / Creating mock images..."
    mkdir -p data/demo_images
    # We'll create some placeholder files
    touch data/demo_images/sample_{1..5}.jpg
fi

echo ""

# Demo 1: Single Image
echo "============================================================================"
echo "DEMO 1: TEK GÖRÜNTÜ ANALİZİ / SINGLE IMAGE ANALYSIS"
echo "============================================================================"
echo ""
echo "Tek bir görüntüde KKD tespiti ve uyumluluk kontrolü"
echo "PPE detection and compliance checking on a single image"
echo ""

python3 demo.py --mode image --output "$OUTPUT_DIR"

echo ""
read -p "Devam etmek için Enter'a basın / Press Enter to continue..."

# Demo 2: Batch Processing
echo ""
echo "============================================================================"
echo "DEMO 2: TOPLU GÖRÜNTÜ İŞLEME / BATCH IMAGE PROCESSING"
echo "============================================================================"
echo ""
echo "Birden fazla görüntünün otomatik olarak işlenmesi"
echo "Automatic processing of multiple images"
echo ""

python3 demo.py --mode batch --output "$OUTPUT_DIR"

echo ""
read -p "Devam etmek için Enter'a basın / Press Enter to continue..."

# Demo 3: Video Processing (if videos available)
if [ "$VIDEO_COUNT" -gt 0 ]; then
    echo ""
    echo "============================================================================"
    echo "DEMO 3: VİDEO İŞLEME / VIDEO PROCESSING"
    echo "============================================================================"
    echo ""
    echo "Video akışında gerçek zamanlı KKD tespiti"
    echo "Real-time PPE detection in video stream"
    echo ""

    python3 demo.py --mode video --output "$OUTPUT_DIR"

    echo ""
    read -p "Devam etmek için Enter'a basın / Press Enter to continue..."
fi

# Demo 4: Report Generation
echo ""
echo "============================================================================"
echo "DEMO 4: DETAYLI RAPOR OLUŞTURMA / DETAILED REPORT GENERATION"
echo "============================================================================"
echo ""
echo "Sistem istatistikleri ve detaylı analiz raporu"
echo "System statistics and detailed analysis report"
echo ""

python3 demo.py --mode report --output "$OUTPUT_DIR"

echo ""

# Show demo dashboard
echo "============================================================================"
echo "BONUS: CANLI DASHBOARD / LIVE DASHBOARD"
echo "============================================================================"
echo ""
echo "Gerçek zamanlı izleme dashboard'u simülasyonu"
echo "Real-time monitoring dashboard simulation"
echo ""
echo "Dashboard HTML dosyası oluşturuluyor / Creating dashboard HTML..."
python3 demo_dashboard.py --mode html

echo ""
echo "Dashboard dosyası: demo_dashboard.html"
echo "Tarayıcınızda açmak için / To open in browser:"
echo "  file://$(pwd)/demo_dashboard.html"
echo ""

# Summary
echo ""
echo "============================================================================"
echo "DEMO ÖZETİ / DEMO SUMMARY"
echo "============================================================================"
echo ""
echo "Tamamlanan demolar / Completed demos:"
echo "  ✓ Tek görüntü analizi / Single image analysis"
echo "  ✓ Toplu görüntü işleme / Batch image processing"
if [ "$VIDEO_COUNT" -gt 0 ]; then
    echo "  ✓ Video işleme / Video processing"
fi
echo "  ✓ Detaylı raporlama / Detailed reporting"
echo "  ✓ Dashboard simülasyonu / Dashboard simulation"
echo ""

echo "📁 Çıktı dosyaları / Output files:"
echo ""
ls -lh "$OUTPUT_DIR"/ | tail -n +2
echo ""

echo "📊 Oluşturulan dosyalar / Generated files:"
find "$OUTPUT_DIR" -type f | while read file; do
    echo "  - $(basename "$file")"
done
echo ""

# Calculate demo stats
TOTAL_OUTPUT_SIZE=$(du -sh "$OUTPUT_DIR" | cut -f1)
echo "💾 Toplam çıktı boyutu / Total output size: $TOTAL_OUTPUT_SIZE"
echo ""

echo "============================================================================"
echo "DEMO BAŞARIYLA TAMAMLANDI! / DEMO COMPLETED SUCCESSFULLY!"
echo "============================================================================"
echo ""
echo "Sonraki adımlar / Next steps:"
echo ""
echo "1. Çıktı dosyalarını inceleyin / Review output files:"
echo "   cd $OUTPUT_DIR && ls -la"
echo ""
echo "2. Raporu görüntüleyin / View report:"
echo "   cat $OUTPUT_DIR/demo_report_*.txt"
echo ""
echo "3. Dashboard'u açın / Open dashboard:"
echo "   python3 demo_dashboard.py --mode html"
echo ""
echo "4. Canlı kamera demosu için (kamera gerekli) / For live camera demo (requires camera):"
echo "   python3 demo.py --mode camera"
echo ""
echo "5. Demo'yu sıfırlamak için / To reset demo:"
echo "   ./reset_demo.sh"
echo ""
echo "🎉 Teşekkürler! / Thank you!"
echo ""
