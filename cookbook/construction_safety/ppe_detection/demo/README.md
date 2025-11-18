# KKD Tespit Sistemi - Demo Paketi
# PPE Detection System - Demo Package

## 🎯 Genel Bakış / Overview

Bu demo paketi, KKD (Kişisel Koruyucu Donanım) tespit sisteminin tüm özelliklerini potansiyel müşterilere sunmak için tasarlanmış kapsamlı bir demo ortamı sağlar.

This demo package provides a comprehensive demonstration environment designed to showcase all features of the PPE (Personal Protective Equipment) detection system to potential customers.

---

## 📋 İçindekiler / Contents

```
demo/
├── demo.py                      # Ana demo script / Main demo script
├── demo_dashboard.py            # Demo dashboard / Demo dashboard
├── docker-compose.demo.yml      # Docker demo ortamı / Docker demo environment
├── DEMO_GUIDE.md               # Kapsamlı demo rehberi / Comprehensive demo guide
├── README.md                    # Bu dosya / This file
│
├── data/                        # Demo verileri / Demo data
│   ├── demo_images/            # Örnek görüntüler / Sample images
│   ├── demo_videos/            # Örnek videolar / Sample videos
│   ├── mock_camera_simulator.py # Kamera simülatörü / Camera simulator
│   └── README.md               # Veri dokümantasyonu / Data documentation
│
├── presentation/                # Sunum materyalleri / Presentation materials
│   ├── PRESENTATION_OUTLINE.md # Sunum içeriği / Presentation content
│   └── [PowerPoint, PDF dosyaları] / [PowerPoint, PDF files]
│
├── scripts/                     # Demo script'leri / Demo scripts
│   ├── quick_demo.sh           # 5 dakikalık hızlı demo / 5-minute quick demo
│   ├── full_demo.sh            # Tam özellik demo'su / Full feature demo
│   └── reset_demo.sh           # Demo sıfırlama / Demo reset
│
└── output/                      # Demo çıktıları / Demo outputs
    └── [Oluşturulan dosyalar] / [Generated files]
```

---

## 🚀 Hızlı Başlangıç / Quick Start

### Ön Gereksinimler / Prerequisites

```bash
# Python 3.8 veya üzeri / Python 3.8 or higher
python3 --version

# Gerekli paketleri yükle / Install required packages
cd ..  # Ana proje dizinine dön / Return to main project directory
pip install -r requirements.txt
```

### 1. Hızlı Demo (5 Dakika) / Quick Demo (5 Minutes)

```bash
cd demo/scripts
./quick_demo.sh
```

**Ne yapar? / What it does:**
- ✅ Tek görüntü analizi / Single image analysis
- ✅ Toplu görüntü işleme / Batch image processing
- ✅ Rapor oluşturma / Report generation

**Kullanım Senaryosu / Use Case:**
İlk görüşmelerde hızlıca sistemi tanıtmak için / For quick system introduction in initial meetings

### 2. Tam Demo (15-20 Dakika) / Full Demo (15-20 Minutes)

```bash
cd demo/scripts
./full_demo.sh
```

**Ne yapar? / What it does:**
- ✅ Tüm görüntü işleme özellikleri / All image processing features
- ✅ Video analizi / Video analysis
- ✅ Detaylı istatistikler / Detailed statistics
- ✅ Kapsamlı raporlama / Comprehensive reporting
- ✅ Dashboard gösterimi / Dashboard demonstration

**Kullanım Senaryosu / Use Case:**
Detaylı ürün sunumları ve pilot öncesi demo'lar için / For detailed product presentations and pre-pilot demos

### 3. Dashboard Demo

```bash
cd demo
python3 demo_dashboard.py --mode html
```

**Açmak için / To open:**
- Browser'da `demo_dashboard.html` dosyasını açın / Open `demo_dashboard.html` in browser
- Veya / Or: `python3 demo_dashboard.py --mode server --port 5000`
- Erişim / Access: http://localhost:5000

**Ne yapar? / What it does:**
- ✅ Gerçek zamanlı ihlal simülasyonu / Real-time violation simulation
- ✅ Canlı istatistikler / Live statistics
- ✅ İnteraktif dashboard / Interactive dashboard
- ✅ Kamera olmadan çalışır / Works without cameras

**Kullanım Senaryosu / Use Case:**
Satış sunumları ve uzaktan demo'lar için / For sales presentations and remote demos

### 4. Docker ile Tam Ortam / Full Environment with Docker

```bash
cd demo
docker-compose -f docker-compose.demo.yml up -d
```

**Erişim / Access:**
- API: http://localhost:8000
- Dashboard: http://localhost:5000
- API Docs: http://localhost:8000/api/docs

---

## 📊 Demo Senaryoları / Demo Scenarios

### Senaryo 1: Satış Sunumu (5-10 Dakika)

**Hedef Kitle / Target Audience:** Karar vericiler, yöneticiler / Decision makers, managers

**Akış / Flow:**

1. **Problem Tanımı (1 dk)**
   ```
   "Türkiye'de her yıl 500+ ölümlü inşaat kazası yaşanıyor.
   Bunların %60'ı KKD eksikliğinden kaynaklanıyor."
   ```

2. **Çözüm Tanıtımı (1 dk)**
   ```
   "Yapay zeka destekli sistemimiz 7/24 otomatik izleme yapıyor."
   ```

3. **Canlı Demo (5 dk)**
   - Tek görüntü analizi göster
   - Dashboard'u aç
   - İstatistikleri vurgula

4. **ROI ve Fiyatlandırma (2 dk)**
   ```
   "İlk yıl %100+ ROI. Aylık X TL'den başlayan paketler."
   ```

5. **Sonraki Adımlar (1 dk)**
   ```
   "15 günlük ücretsiz pilot uygulama yapalım."
   ```

### Senaryo 2: Teknik Sunum (30 Dakika)

**Hedef Kitle / Target Audience:** IT ekipleri, teknik yöneticiler / IT teams, technical managers

**Akış / Flow:**

1. Sistem mimarisi açıklaması
2. API dokümantasyonu gösterimi
3. Kamera entegrasyonu demo'su
4. Performans metrikleri
5. Güvenlik özellikleri
6. Özelleştirme seçenekleri
7. Q&A

### Senaryo 3: Pilot Hazırlık (60 Dakika)

**Hedef Kitle / Target Audience:** Proje ekibi / Project team

**Akış / Flow:**

1. Detaylı sistem incelemesi
2. Sahada test senaryoları
3. Gereksinimlerin belirlenmesi
4. Kurulum planı
5. Eğitim planı
6. Başarı kriterleri

---

## 🎬 Demo Kullanım Kılavuzu / Demo Usage Guide

### demo.py - İnteraktif Demo Script

```bash
# Yardım / Help
python3 demo.py --help

# Tek görüntü işle / Process single image
python3 demo.py --mode image --image path/to/image.jpg

# Toplu işleme / Batch processing
python3 demo.py --mode batch

# Video işle / Process video
python3 demo.py --mode video --video path/to/video.mp4

# Canlı kamera (kamera gerekli) / Live camera (requires camera)
python3 demo.py --mode camera --camera 0

# Rapor oluştur / Generate report
python3 demo.py --mode report

# Hepsini çalıştır / Run all
python3 demo.py --mode all --output ./output
```

### demo_dashboard.py - Dashboard

```bash
# Standalone HTML oluştur / Create standalone HTML
python3 demo_dashboard.py --mode html

# Flask server başlat / Start Flask server
python3 demo_dashboard.py --mode server --port 5000
```

### mock_camera_simulator.py - Kamera Simülatörü

```bash
# Test pattern göster / Show test pattern
python3 data/mock_camera_simulator.py

# Video döngüsü / Loop video
python3 data/mock_camera_simulator.py \
  --video data/demo_videos/construction.mp4 \
  --loop

# Mock RTSP server / Mock RTSP server
python3 data/mock_camera_simulator.py \
  --rtsp \
  --video data/demo_videos/construction.mp4 \
  --stream-name cam1
```

---

## 📁 Demo Verileri / Demo Data

### Görüntü Gereksinimleri / Image Requirements

Demo'nun tam işlevsel olması için aşağıdaki kategorilerde görüntüler gereklidir:

For full functionality, images are needed in the following categories:

1. **Tam Uyumlu / Compliant** (3+ görüntü / images)
   - İşçiler tam KKD ile / Workers with full PPE
   - Baret + Yelek / Helmet + Vest

2. **Baret Eksik / Missing Helmet** (2+ görüntü / images)
   - Sadece yelek / Vest only

3. **Yelek Eksik / Missing Vest** (2+ görüntü / images)
   - Sadece baret / Helmet only

4. **Her İkisi Eksik / Missing Both** (2+ görüntü / images)
   - KKD yok / No PPE

5. **Çoklu İşçi / Multiple Workers** (3+ görüntü / images)
   - Farklı uyumluluk durumları / Mixed compliance

### Görüntü Kaynaklari / Image Sources

**Ücretsiz Stok Görseller / Free Stock Images:**
- [Unsplash](https://unsplash.com/s/photos/construction-worker)
- [Pexels](https://www.pexels.com/search/construction%20safety/)
- [Pixabay](https://pixabay.com/images/search/construction%20worker/)

**Arama Terimleri / Search Terms:**
- construction worker helmet
- construction safety vest
- hard hat worker
- safety equipment
- inşaat işçisi
- baret
- emniyet yeleği

### Görüntü Hazırlama / Image Preparation

```bash
# Görüntüleri demo dizinine kopyala / Copy images to demo directory
cp /path/to/images/*.jpg demo/data/demo_images/

# Otomatik kategorilere ayır (gelişmiş) / Auto categorize (advanced)
python3 scripts/categorize_images.py \
  --input demo/data/demo_images/ \
  --auto-categorize
```

---

## 🎨 Sunum Materyalleri / Presentation Materials

### PowerPoint Sunumu / PowerPoint Presentation

Sunum içeriği ve slayt düzeni için bakınız:
See presentation content and slide layout at:

📄 `presentation/PRESENTATION_OUTLINE.md`

**Ana Konular / Main Topics:**
1. Problem tanımı / Problem statement
2. Çözüm tanıtımı / Solution introduction
3. Teknik yetenekler / Technical capabilities
4. Canlı demo / Live demo
5. ROI ve fiyatlandırma / ROI and pricing
6. Sonraki adımlar / Next steps

### Broşür ve Materyaller / Brochures and Materials

**Önerilen Materyaller / Recommended Materials:**
- [ ] Ürün broşürü (4 sayfa) / Product brochure (4 pages)
- [ ] Teknik özellikler kartı / Technical specs sheet
- [ ] Başarı hikayeleri / Success stories
- [ ] Fiyat listesi / Price list
- [ ] Kartvizitler / Business cards
- [ ] USB bellek (demo dosyaları ile) / USB stick (with demo files)

---

## 💡 Demo İpuçları / Demo Tips

### Başlamadan Önce / Before Starting

✅ **Kontrol Listesi / Checklist:**
- [ ] Laptop şarjı dolu / Laptop fully charged
- [ ] Demo dosyaları test edildi / Demo files tested
- [ ] İnternet bağlantısı çalışıyor / Internet connection working
- [ ] Yedek demo hazır (offline) / Backup demo ready (offline)
- [ ] Projektör/ekran test edildi / Projector/screen tested
- [ ] Sunum materyalleri hazır / Presentation materials ready
- [ ] Müşteri bilgileri gözden geçirildi / Customer info reviewed

### Demo Sırasında / During Demo

✅ **En İyi Pratikler / Best Practices:**

1. **İhtiyaç Dinleyin / Listen to Needs**
   - Önce müşterinin sorunlarını dinleyin
   - Demo'yu ihtiyaçlara göre özelleştirin

2. **Basit Başlayın / Start Simple**
   - Karmaşık özelliklerle boğmayın
   - Temel faydaları vurgulayın

3. **Göster, Söyleme / Show, Don't Tell**
   - Canlı demo her zaman daha etkili
   - Gerçek örnekler kullanın

4. **İnteraktif Olun / Be Interactive**
   - Sorular sorun
   - Müşteriyi dahil edin
   - Geri bildirim alın

5. **Sorunlara Hazırlıklı Olun / Prepare for Issues**
   - Plan B her zaman hazır
   - Teknik sorunları sakin karşılayın
   - Offline demo hazır bulundurun

### Yaygın Hatalar / Common Mistakes

❌ **Kaçınılması Gerekenler / Things to Avoid:**

1. Çok fazla teknik detay
   Too much technical detail

2. Müşteri ihtiyaçlarını dinlemeden sunum
   Presenting without listening to customer needs

3. Demo'da hata olduğunda paniklemek
   Panicking when demo has errors

4. Fiyattan önce değer göstermemek
   Not showing value before discussing price

5. Sonraki adımları planlamadan bitirmek
   Ending without planning next steps

---

## 🔧 Sorun Giderme / Troubleshooting

### Yaygın Sorunlar / Common Issues

#### 1. Demo görüntüleri bulunamıyor / Demo images not found

**Çözüm / Solution:**
```bash
# Demo görüntüleri dizinini kontrol et / Check demo images directory
ls -la demo/data/demo_images/

# Boşsa, örnek görüntüler ekle / If empty, add sample images
# Ücretsiz stok görseller indir / Download free stock images
```

#### 2. Python modülü bulunamıyor / Python module not found

**Çözüm / Solution:**
```bash
# Gereksinimleri yükle / Install requirements
pip install -r ../requirements.txt

# Veya tek tek / Or individually
pip install opencv-python numpy ultralytics
```

#### 3. Kamera açılamıyor / Cannot open camera

**Çözüm / Solution:**
```bash
# Mock kamera simülatörü kullan / Use mock camera simulator
python3 data/mock_camera_simulator.py --loop

# Veya video kullan / Or use video
python3 demo.py --mode video --video data/demo_videos/sample.mp4
```

#### 4. Dashboard açılmıyor / Dashboard won't open

**Çözüm / Solution:**
```bash
# HTML modunu kullan (Flask gerektirmez) / Use HTML mode (no Flask required)
python3 demo_dashboard.py --mode html

# Browser'da aç / Open in browser
open demo_dashboard.html  # macOS
xdg-open demo_dashboard.html  # Linux
start demo_dashboard.html  # Windows
```

#### 5. Performans sorunları / Performance issues

**Çözüm / Solution:**
```bash
# Daha küçük model kullan / Use smaller model
# model_config.py dosyasında model_architecture = "yolov8n" olarak ayarla

# Frame skip artır / Increase frame skip
# Video işlerken her 2. frame'i işle
```

---

## 📈 Demo Metrikleri / Demo Metrics

### Başarı Kriterleri / Success Criteria

Demo sonrası izlemek için önerilen metrikler:
Recommended metrics to track after demo:

- [ ] Müşteri ilgisi seviyesi (1-10) / Customer interest level (1-10)
- [ ] Teknik sorular sayısı / Number of technical questions
- [ ] Pilot uygulama talebi / Pilot application request
- [ ] Teklif talebi / Proposal request
- [ ] Sonraki görüşme planlandı mı? / Next meeting scheduled?
- [ ] Karar verici katıldı mı? / Decision maker attended?

### Takip Süreci / Follow-up Process

**Demo Sonrası / After Demo:**

1. **Aynı Gün / Same Day:**
   - Teşekkür emaili gönder / Send thank you email
   - Demo kaydı paylaş / Share demo recording
   - Demo materyallerini paylaş / Share demo materials

2. **1-2 Gün İçinde / Within 1-2 Days:**
   - Teklif hazırla ve gönder / Prepare and send proposal
   - ROI hesaplaması ekle / Include ROI calculation
   - Referansları paylaş / Share references

3. **1 Hafta İçinde / Within 1 Week:**
   - Takip araması yap / Make follow-up call
   - Soruları yanıtla / Answer questions
   - Pilot uygulama detaylarını planla / Plan pilot details

---

## 📞 Destek / Support

### Demo ile İlgili Yardım / Help with Demos

**Teknik Destek / Technical Support:**
- Email: support@ppe-detection.com
- Tel: +90 XXX XXX XX XX
- WhatsApp: +90 XXX XXX XX XX

**Satış Desteği / Sales Support:**
- Email: sales@ppe-detection.com
- Tel: +90 XXX XXX XX XX

**Demo Materyalleri / Demo Materials:**
- Web: www.ppe-detection.com/demo
- Kaynaklar / Resources: www.ppe-detection.com/resources

---

## 📚 Ek Kaynaklar / Additional Resources

### Dokümantasyon / Documentation

- [Ana README](../README.md) - Sistem genel bakış / System overview
- [DEMO_GUIDE.md](./DEMO_GUIDE.md) - Detaylı demo rehberi / Detailed demo guide
- [PRESENTATION_OUTLINE.md](./presentation/PRESENTATION_OUTLINE.md) - Sunum içeriği / Presentation content
- [Data README](./data/README.md) - Demo veri rehberi / Demo data guide

### Video Eğitimler / Video Tutorials

- Demo nasıl hazırlanır / How to prepare demo
- Satış sunumu teknikleri / Sales presentation techniques
- Yaygın sorunlar ve çözümleri / Common issues and solutions

### Şablonlar / Templates

- PowerPoint sunum şablonu / PowerPoint presentation template
- Email şablonları / Email templates
- Teklif şablonu / Proposal template
- ROI hesaplama Excel / ROI calculation Excel

---

## 🔄 Demo Güncellemeleri / Demo Updates

### Versiyon Geçmişi / Version History

**v1.0.0** (2024-11-18)
- İlk demo paketi yayını / Initial demo package release
- Temel demo senaryoları / Basic demo scenarios
- Dashboard gösterimi / Dashboard demonstration
- Kapsamlı dokümantasyon / Comprehensive documentation

### Gelecek Özellikler / Future Features

Planlanan / Planned:
- [ ] İnteraktif 3D demo / Interactive 3D demo
- [ ] AR (Artırılmış Gerçeklik) demo / AR demo
- [ ] VR demo ortamı / VR demo environment
- [ ] Çevrimiçi demo platformu / Online demo platform
- [ ] Otomatik demo video oluşturucu / Automatic demo video generator

---

## 📝 Lisans ve Telif Hakları / License and Copyright

**Demo Materyalleri / Demo Materials:**
- Demo script'leri ve kod: MIT License
- Demo scripts and code: MIT License
- Dokümantasyon: CC BY 4.0
- Documentation: CC BY 4.0

**Demo Görüntüleri / Demo Images:**
- Ücretsiz stok görseller kullanılmalı / Must use free stock images
- Ticari kullanım lisanslı / Commercial use licensed
- KVKK/GDPR uyumlu / KVKK/GDPR compliant

⚠️ **UYARI / WARNING:**
Müşteri demo'larında kullanılan gerçek işçi görüntüleri için yazılı izin alınmalıdır.
Written permission required for real worker images used in customer demos.

---

## 🎉 Demo Başarı Hikayeleri / Demo Success Stories

### Başarılı Demo Örnekleri / Successful Demo Examples

**🏗️ Örnek 1: ABC İnşaat**
- Demo süresi: 15 dakika
- Sonuç: Aynı gün pilot uygulama anlaşması
- ROI gösterimi etkili oldu

**🏗️ Örnek 2: XYZ Yapı**
- Demo süresi: 30 dakika (teknik)
- Sonuç: 2 gün içinde 3 şantiye için sözleşme
- API entegrasyonu demo'su karar vericiydi

**🏗️ Örnek 3: DEF İnşaat**
- Demo süresi: 10 dakika (uzaktan)
- Sonuç: Dashboard demo ile ilgi çekti
- Sonrasında yerinde detaylı demo yapıldı

---

**Son Güncelleme / Last Updated:** 2024-11-18
**Versiyon / Version:** 1.0.0
**Bakım / Maintained by:** PPE Detection Team

---

**🚀 Demo'nuza Başarılar Dileriz! / Good Luck with Your Demo!**
