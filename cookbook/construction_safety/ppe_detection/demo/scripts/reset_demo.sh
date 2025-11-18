#!/bin/bash

# Reset Demo - Clean demo data and output
# Demo Sıfırlama - Demo verilerini ve çıktıları temizle

echo "============================================================================"
echo "DEMO SIFIRLAMA / RESET DEMO"
echo "============================================================================"
echo ""
echo "Bu işlem şunları temizleyecek / This will clean:"
echo "  - Çıktı dosyaları / Output files"
echo "  - Oluşturulan raporlar / Generated reports"
echo "  - İşlenmiş görüntüler / Processed images"
echo "  - İşlenmiş videolar / Processed videos"
echo ""
echo "⚠️  NOT: Demo görüntüleri ve videoları silinmeyecek"
echo "⚠️  NOTE: Demo images and videos will NOT be deleted"
echo ""

read -p "Devam etmek istiyor musunuz? (y/N) / Continue? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "İptal edildi / Cancelled"
    exit 0
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DEMO_DIR="$(dirname "$SCRIPT_DIR")"

cd "$DEMO_DIR"

echo ""
echo "🗑️  Temizleniyor / Cleaning..."
echo ""

# Remove output directory
if [ -d "output" ]; then
    OUTPUT_SIZE=$(du -sh output 2>/dev/null | cut -f1)
    echo "  Çıktı dosyaları siliniyor / Removing output files ($OUTPUT_SIZE)..."
    rm -rf output/*
    echo "  ✓ Çıktı dizini temizlendi / Output directory cleaned"
else
    echo "  ℹ️  Çıktı dizini bulunamadı / Output directory not found"
fi

# Remove generated dashboard HTML
if [ -f "demo_dashboard.html" ]; then
    echo "  Dashboard HTML dosyası siliniyor / Removing dashboard HTML..."
    rm -f demo_dashboard.html
    echo "  ✓ Dashboard HTML silindi / Dashboard HTML removed"
fi

# Remove any temporary files
echo "  Geçici dosyalar siliniyor / Removing temporary files..."
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true
echo "  ✓ Geçici dosyalar temizlendi / Temporary files cleaned"

# Recreate empty output directory
mkdir -p output
echo "  ✓ Çıktı dizini yeniden oluşturuldu / Output directory recreated"

echo ""
echo "============================================================================"
echo "TEMİZLEME TAMAMLANDI / CLEANING COMPLETE"
echo "============================================================================"
echo ""
echo "Demo baştan çalıştırılmaya hazır / Demo ready to run from scratch"
echo ""
echo "Yeni demo çalıştırmak için / To run a new demo:"
echo "  ./quick_demo.sh   - Hızlı demo / Quick demo (5 min)"
echo "  ./full_demo.sh    - Tam demo / Full demo (15-20 min)"
echo ""
