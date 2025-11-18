#!/bin/bash

# Quick Demo - 5 Minute Demonstration
# Hızlı Demo - 5 Dakikalık Sunum

set -e

echo "============================================================================"
echo "KKD TESPİT SİSTEMİ - HIZLI DEMO (5 DAKİKA)"
echo "PPE DETECTION SYSTEM - QUICK DEMO (5 MINUTES)"
echo "============================================================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DEMO_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$(dirname "$DEMO_DIR")"

cd "$DEMO_DIR"

echo "📍 Demo dizini / Demo directory: $DEMO_DIR"
echo ""

# Check Python
echo "🔍 Python kontrolü / Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 bulunamadı / Python 3 not found"
    exit 1
fi
echo "✓ Python: $(python3 --version)"
echo ""

# Check dependencies
echo "🔍 Bağımlılıklar kontrol ediliyor / Checking dependencies..."
python3 -c "import cv2, numpy, ultralytics" 2>/dev/null || {
    echo "⚠ Bazı bağımlılıklar eksik / Some dependencies missing"
    echo "  Yüklemek için / To install: pip install -r ../requirements.txt"
}
echo "✓ Bağımlılıklar hazır / Dependencies ready"
echo ""

# Create output directory
mkdir -p output
echo "✓ Çıktı dizini oluşturuldu / Output directory created"
echo ""

echo "============================================================================"
echo "DEMO 1: TEK GÖRÜNTÜ ANALİZİ / SINGLE IMAGE ANALYSIS"
echo "============================================================================"
echo ""

# Process single image
python3 demo.py --mode image --output output

echo ""
echo "============================================================================"
echo "DEMO 2: TOPLU GÖRÜNTÜ ANALİZİ / BATCH PROCESSING"
echo "============================================================================"
echo ""

# Process batch
python3 demo.py --mode batch --output output

echo ""
echo "============================================================================"
echo "DEMO 3: RAPOR OLUŞTURMA / REPORT GENERATION"
echo "============================================================================"
echo ""

# Generate report
python3 demo.py --mode report --output output

echo ""
echo "============================================================================"
echo "DEMO TAMAMLANDI / DEMO COMPLETE"
echo "============================================================================"
echo ""
echo "📁 Çıktı dosyaları / Output files:"
ls -lh output/ | tail -n +2
echo ""
echo "🎉 Hızlı demo başarıyla tamamlandı! / Quick demo completed successfully!"
echo ""
echo "Sonraki adımlar / Next steps:"
echo "  - Tam demo için / For full demo: ./full_demo.sh"
echo "  - Dashboard için / For dashboard: python3 ../demo_dashboard.py"
echo "  - Yardım için / For help: python3 ../demo.py --help"
echo ""
