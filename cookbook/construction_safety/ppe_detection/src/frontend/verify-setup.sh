#!/bin/bash

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "================================================"
echo "🏗️  KKD Tespit Sistemi - Dashboard Kurulum Kontrolü"
echo "================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "index.html" ]; then
    echo -e "${RED}❌ Hata: index.html bulunamadı!${NC}"
    echo "   Bu scripti frontend dizininde çalıştırın."
    exit 1
fi

echo -e "${BLUE}📂 Dosya Kontrolü${NC}"
echo "-------------------"

# Check required files
files=(
    "index.html"
    "static/css/main.css"
    "static/js/main.js"
    "static/js/websocket.js"
    "static/js/charts.js"
    "server.py"
    "README.md"
    "QUICKSTART.md"
)

all_files_ok=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        echo -e "${GREEN}✅${NC} $file ($size)"
    else
        echo -e "${RED}❌${NC} $file - EKSIK!"
        all_files_ok=false
    fi
done

echo ""
echo -e "${BLUE}📊 Kod İstatistikleri${NC}"
echo "-------------------"
total_lines=$(wc -l index.html static/css/main.css static/js/*.js 2>/dev/null | tail -1 | awk '{print $1}')
echo -e "Toplam kod satırı: ${GREEN}$total_lines${NC}"

echo ""
echo -e "${BLUE}🔍 Bağımlılık Kontrolü${NC}"
echo "-------------------"

# Check Python
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✅${NC} Python 3: $python_version"
else
    echo -e "${RED}❌${NC} Python 3 bulunamadı!"
fi

# Check if port 8080 is available
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️${NC}  Port 8080 kullanımda (başka port kullanmanız gerekebilir)"
else
    echo -e "${GREEN}✅${NC} Port 8080 uygun"
fi

echo ""
echo -e "${BLUE}🚀 Başlatma Komutları${NC}"
echo "-------------------"
echo "Frontend başlatmak için:"
echo -e "${YELLOW}  python3 server.py${NC}"
echo ""
echo "Alternatif olarak:"
echo -e "${YELLOW}  python3 -m http.server 8080${NC}"
echo ""

if [ "$all_files_ok" = true ]; then
    echo -e "${GREEN}✅ Tüm dosyalar mevcut - Kurulum başarılı!${NC}"
    echo ""
    echo "🌐 Dashboard'u açmak için:"
    echo "   1. 'python3 server.py' komutunu çalıştırın"
    echo "   2. Tarayıcıda http://localhost:8080 adresini açın"
    echo ""
else
    echo -e "${RED}❌ Bazı dosyalar eksik - Lütfen kurulumu kontrol edin${NC}"
    exit 1
fi

echo "================================================"
echo ""
