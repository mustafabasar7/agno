#!/bin/bash

# Download Sample Demo Data
# Demo Verilerini İndir

set -e

echo "============================================================================"
echo "DEMO VERİLERİNİ İNDİRME / DOWNLOAD DEMO DATA"
echo "============================================================================"
echo ""
echo "Bu script örnek demo verilerini indirir:"
echo "This script downloads sample demo data:"
echo ""
echo "  - İnşaat sahası görüntüleri / Construction site images"
echo "  - Örnek videolar / Sample videos"
echo "  - Test verileri / Test data"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create directories
echo "📁 Dizinler oluşturuluyor / Creating directories..."
mkdir -p demo_images/{compliant,missing_helmet,missing_vest,missing_both,multiple_workers}
mkdir -p demo_videos
echo "✓ Dizinler oluşturuldu / Directories created"
echo ""

# Check for wget or curl
if command -v wget &> /dev/null; then
    DOWNLOAD_CMD="wget -O"
elif command -v curl &> /dev/null; then
    DOWNLOAD_CMD="curl -L -o"
else
    echo "❌ Hata: wget veya curl bulunamadı / Error: wget or curl not found"
    echo "   Lütfen birini yükleyin / Please install one of them"
    exit 1
fi

echo "📥 Örnek görüntüler indiriliyor / Downloading sample images..."
echo ""

# Function to download image
download_image() {
    local url="$1"
    local output="$2"
    local description="$3"

    echo "  📷 $description"
    if $DOWNLOAD_CMD "$output" "$url" 2>/dev/null; then
        echo "     ✓ İndirildi / Downloaded: $output"
    else
        echo "     ⚠ İndirilemedi / Failed to download"
    fi
}

# Unsplash örnek görseller (demo amaçlı)
# Unsplash sample images (for demo purposes)
# NOT: Gerçek kullanımda Unsplash API kullanın veya kendi görsellerinizi ekleyin
# NOTE: For real use, use Unsplash API or add your own images

echo "ℹ️  NOT: Bu script placeholder'ları oluşturur."
echo "ℹ️  NOTE: This script creates placeholders."
echo ""
echo "Gerçek demo görüntüleri için / For real demo images:"
echo "  1. Ücretsiz stok görseller: / Free stock images:"
echo "     - https://unsplash.com/s/photos/construction-worker"
echo "     - https://pexels.com/search/construction%20safety/"
echo "     - https://pixabay.com/images/search/hard%20hat/"
echo ""
echo "  2. Manuel indirme: / Manual download:"
echo "     - Görüntüleri indir / Download images"
echo "     - Uygun dizinlere kopyala / Copy to appropriate directories"
echo ""
echo "  3. Kendi görselleriniz: / Your own images:"
echo "     - İnşaat sahanızdan çekin / Capture from your construction site"
echo "     - KVKK uyumluluğu sağlayın / Ensure GDPR compliance"
echo ""

# Create placeholder info files
echo "📝 Placeholder dosyaları oluşturuluyor / Creating placeholder files..."

for category in compliant missing_helmet missing_vest missing_both multiple_workers; do
    cat > "demo_images/$category/README.txt" << EOF
Bu dizine $category kategorisi için örnek görüntüler ekleyin.
Add sample images for $category category to this directory.

Önerilen format / Recommended format: JPG, PNG
Minimum çözünürlük / Minimum resolution: 1280x720
Önerilen çözünürlük / Recommended resolution: 1920x1080

Örnek dosya isimleri / Sample file names:
- ${category}_001.jpg
- ${category}_002.jpg
- ${category}_003.jpg

Kaynak / Source: https://unsplash.com/s/photos/construction-worker
EOF
    echo "  ✓ demo_images/$category/README.txt"
done

# Create video placeholder
cat > "demo_videos/README.txt" << EOF
Bu dizine örnek videolar ekleyin.
Add sample videos to this directory.

Önerilen format / Recommended format: MP4 (H.264)
Çözünürlük / Resolution: 1280x720 veya 1920x1080
FPS: 25-30
Süre / Duration: 30 saniye - 2 dakika

Örnek dosya isimleri / Sample file names:
- construction_site_overview.mp4
- entry_checkpoint.mp4
- warehouse_area.mp4

Kaynak / Source:
- https://pixabay.com/videos/search/construction/
- https://pexels.com/search/videos/construction/
EOF

echo ""
echo "============================================================================"
echo "TAMAMLANDI / COMPLETED"
echo "============================================================================"
echo ""
echo "📊 Durum / Status:"
echo "  ✓ Dizinler oluşturuldu / Directories created"
echo "  ✓ Placeholder dosyalar oluşturuldu / Placeholder files created"
echo "  ⚠ Gerçek görüntüler eklenmedi / Real images not added"
echo ""
echo "📋 Sonraki Adımlar / Next Steps:"
echo ""
echo "1. Ücretsiz stok görsel sitelerinden indir:"
echo "   Download from free stock image sites:"
echo "   https://unsplash.com/s/photos/construction-worker"
echo ""
echo "2. Veya kendi görsellerinizi kullanın:"
echo "   Or use your own images:"
echo "   cp /path/to/your/images/*.jpg demo_images/compliant/"
echo ""
echo "3. Video eklemek için:"
echo "   To add videos:"
echo "   cp /path/to/your/videos/*.mp4 demo_videos/"
echo ""
echo "4. Demo'yu test edin:"
echo "   Test the demo:"
echo "   cd .. && python3 demo.py --mode image"
echo ""
echo "📁 Dizin yapısı / Directory structure:"
tree -L 2 demo_images/ demo_videos/ 2>/dev/null || find demo_images/ demo_videos/ -maxdepth 2
echo ""
echo "🎉 Hazır! / Ready!"
echo ""
