# Demo Data - KKD Tespit Sistemi
# Demo Data - PPE Detection System

## İçindekiler / Contents

Bu dizin demo için kullanılacak örnek veri setlerini içerir.
This directory contains sample datasets for demo purposes.

### Dizin Yapısı / Directory Structure

```
data/
├── demo_images/          # Demo görüntüleri / Demo images
│   ├── compliant/        # Tam KKD kullanımı / Full PPE compliance
│   ├── missing_helmet/   # Baret eksik / Missing helmet
│   ├── missing_vest/     # Yelek eksik / Missing vest
│   ├── missing_both/     # Her ikisi eksik / Missing both
│   └── multiple_workers/ # Çoklu işçi / Multiple workers
│
├── demo_videos/          # Demo videoları / Demo videos
│   ├── construction_site_1.mp4
│   ├── construction_site_2.mp4
│   └── warehouse_inspection.mp4
│
└── mock_camera/          # Mock kamera beslemeleri / Mock camera feeds
    ├── camera_1.stream
    ├── camera_2.stream
    └── camera_3.stream
```

---

## Demo Görüntüleri / Demo Images

### Gerekli Görüntüler / Required Images

Demo'nun tam işlevsel olması için her kategoriden en az 2-3 görüntüye ihtiyaç vardır.
For full functionality, at least 2-3 images per category are needed.

#### 1. Tam Uyumlu (Compliant)
**Açıklama / Description:**
- İşçiler tam KKD ile / Workers with full PPE
- Baret + Yelek / Helmet + Vest
- Net görüntü / Clear view

**Örnekler / Examples:**
- `compliant/worker_full_ppe_1.jpg`
- `compliant/worker_full_ppe_2.jpg`
- `compliant/multiple_compliant.jpg`

#### 2. Baret Eksik (Missing Helmet)
**Açıklama / Description:**
- İşçi yeleği var ama bareti yok
- Worker has vest but no helmet

**Örnekler / Examples:**
- `missing_helmet/worker_no_helmet_1.jpg`
- `missing_helmet/worker_no_helmet_2.jpg`

#### 3. Yelek Eksik (Missing Vest)
**Açıklama / Description:**
- İşçi bareti var ama yeleği yok
- Worker has helmet but no vest

**Örnekler / Examples:**
- `missing_vest/worker_no_vest_1.jpg`
- `missing_vest/worker_no_vest_2.jpg`

#### 4. Her İkisi Eksik (Missing Both)
**Açıklama / Description:**
- İşçi ne baret ne de yelek kullanıyor
- Worker has neither helmet nor vest

**Örnekler / Examples:**
- `missing_both/worker_no_ppe_1.jpg`
- `missing_both/worker_no_ppe_2.jpg`

#### 5. Çoklu İşçi (Multiple Workers)
**Açıklama / Description:**
- Çerçevede birden fazla işçi
- Multiple workers in frame
- Farklı uyumluluk durumları
- Different compliance statuses

**Örnekler / Examples:**
- `multiple_workers/construction_team_1.jpg`
- `multiple_workers/construction_team_2.jpg`

---

## Görüntü Gereksinimleri / Image Requirements

### Teknik Özellikler / Technical Specifications

**Format / Format:**
- JPG, PNG (önerilen / recommended)
- WebP, BMP (desteklenir / supported)

**Çözünürlük / Resolution:**
- Minimum: 640x480
- Önerilen / Recommended: 1920x1080 (Full HD)
- Maximum: 4K (3840x2160)

**Dosya Boyutu / File Size:**
- Minimum: 100 KB
- Maksimum / Maximum: 10 MB per file

**Kalite / Quality:**
- Net odak / Clear focus
- İyi ışıklandırma / Good lighting
- Minimal gürültü / Minimal noise

### Çekim Açıları / Camera Angles

**İdeal Açılar / Ideal Angles:**
1. Yüksek açı (45°) - Genel görünüm / High angle - Overview
2. Göz seviyesi - Detay / Eye level - Detail
3. Yan açı - Profil / Side angle - Profile

**Kaçınılması Gerekenler / Avoid:**
- Aşırı karanlık / Too dark
- Aşırı parlak (overexposed) / Too bright
- Bulanık görüntü / Blurry images
- Kötü çerçeveleme / Poor framing

---

## Demo Videoları / Demo Videos

### Video Özellikleri / Video Specifications

**Format / Format:**
- MP4 (H.264) - önerilen / recommended
- AVI, MOV - desteklenir / supported

**Çözünürlük / Resolution:**
- Minimum: 720p (1280x720)
- Önerilen / Recommended: 1080p (1920x1080)

**FPS:**
- Minimum: 15 FPS
- Önerilen / Recommended: 30 FPS

**Süre / Duration:**
- Demo için / For demo: 30 saniye - 2 dakika
- Test için / For testing: 5-10 dakika

**Dosya Boyutu / File Size:**
- Maksimum / Maximum: 100 MB per video

### Önerilen İçerik / Recommended Content

1. **İnşaat Sahası Genel / Construction Site Overview**
   - Geniş açı / Wide angle
   - Çoklu işçi / Multiple workers
   - Farklı aktiviteler / Various activities
   - Süre / Duration: 1-2 dakika

2. **Giriş Kontrol Noktası / Entry Checkpoint**
   - İşçilerin girişi / Workers entering
   - KKD kontrolü / PPE check
   - Süre / Duration: 30-60 saniye

3. **Depo/Malzeme Alanı / Warehouse/Material Area**
   - İşçi hareketleri / Worker movements
   - Yükleme/boşaltma / Loading/unloading
   - Süre / Duration: 1-2 dakika

---

## Mock Kamera Beslemeleri / Mock Camera Feeds

### Mock Kamera Simülatörü / Mock Camera Simulator

Demo sırasında gerçek kamera olmadan canlı besleme simüle etmek için kullanılır.
Used to simulate live feeds during demos without actual cameras.

### Kullanım / Usage

```python
# Mock kamera başlat / Start mock camera
python3 mock_camera_simulator.py --video demo_videos/construction_site_1.mp4 --loop

# RTSP stream simüle et / Simulate RTSP stream
python3 mock_camera_simulator.py --rtsp --port 8554 --stream-name cam1
```

### Yapılandırma / Configuration

```yaml
# mock_camera_config.yml
cameras:
  - id: CAM_001
    name: "Ana Giriş"
    video_source: "demo_videos/construction_site_1.mp4"
    loop: true
    fps: 30

  - id: CAM_002
    name: "İnşaat Sahası A"
    video_source: "demo_videos/construction_site_2.mp4"
    loop: true
    fps: 25

  - id: CAM_003
    name: "Depo Alanı"
    video_source: "demo_videos/warehouse_inspection.mp4"
    loop: true
    fps: 30
```

---

## Veri Toplama Rehberi / Data Collection Guide

### Kendi Verilerinizi Oluşturma / Creating Your Own Data

#### Görüntü Çekimi / Image Capture

1. **İzin Alın / Get Permission**
   - İnşaat sahası yönetiminden / From site management
   - İşçilerden (KVKK) / From workers (GDPR)

2. **Ekipman / Equipment**
   - Akıllı telefon (12+ MP) / Smartphone (12+ MP)
   - DSLR kamera (önerilen) / DSLR camera (recommended)
   - Tripod (sabit çekimler için) / Tripod (for stable shots)

3. **Çekim Koşulları / Shooting Conditions**
   - Gündüz, iyi ışık / Daytime, good light
   - Farklı hava koşulları / Various weather conditions
   - Farklı saatler / Different times

4. **Çeşitlilik / Variety**
   - Farklı işçiler / Different workers
   - Farklı açılar / Different angles
   - Farklı aktiviteler / Different activities
   - Farklı KKD durumları / Different PPE statuses

#### Video Çekimi / Video Recording

1. **Kamera Konumu / Camera Position**
   - Sabit pozisyon / Fixed position
   - Yükseklik: 2.5-4 metre / Height: 2.5-4 meters
   - Açı: 30-45 derece / Angle: 30-45 degrees

2. **Süre / Duration**
   - Minimum 5 dakika sürekli çekim
   - Minimum 5 minutes continuous recording

3. **Hareket / Movement**
   - Kamera sabit / Camera fixed
   - İşçiler hareket ediyor / Workers moving
   - Doğal iş akışı / Natural workflow

---

## Lisanslama ve Telif Hakları / Licensing and Copyright

### Demo Görüntüleri için Kaynaklar / Sources for Demo Images

**Ücretsiz Stok Görseller / Free Stock Images:**
- Unsplash.com (commercial use allowed)
- Pexels.com (commercial use allowed)
- Pixabay.com (commercial use allowed)

**Arama Terimleri / Search Terms:**
- "construction worker"
- "construction safety"
- "hard hat worker"
- "safety vest"
- "construction site"
- "inşaat işçisi"
- "baret"
- "yelek"

### Lisans Notları / License Notes

⚠️ **ÖNEMLİ / IMPORTANT:**

1. Demo görüntüleri ticari kullanım için uygun olmalı
   Demo images must be suitable for commercial use

2. Kişisel verileri içeren görüntüler için KVKK uyumluluğu gerekli
   GDPR/KVKK compliance required for images with personal data

3. Telif hakkı korumalı materyaller kullanmayın
   Do not use copyrighted materials without permission

4. Müşteri demo'larında gerçek işçi görüntüleri kullanıyorsanız,
   yazılı izin alın
   Get written permission if using real worker images in customer demos

---

## Veri Hazırlama Script'leri / Data Preparation Scripts

### Görüntü İşleme / Image Processing

```bash
# Görüntüleri yeniden boyutlandır / Resize images
python3 scripts/resize_images.py \
  --input demo_images/ \
  --output demo_images_processed/ \
  --size 1920x1080

# Görüntü kalitesini optimize et / Optimize image quality
python3 scripts/optimize_images.py \
  --input demo_images/ \
  --quality 85 \
  --format jpg
```

### Video İşleme / Video Processing

```bash
# Video'yu kırp / Trim video
ffmpeg -i input.mp4 -ss 00:00:10 -t 00:01:00 -c copy output.mp4

# Video'yu sıkıştır / Compress video
ffmpeg -i input.mp4 -vcodec h264 -acodec aac -b:v 2000k output.mp4

# Frame çıkar / Extract frames
ffmpeg -i input.mp4 -vf fps=1 frame_%04d.jpg
```

---

## Sıkça Sorulan Sorular / FAQ

### Q1: Demo için kaç görüntü gerekli?
**A:** Minimum 10 görüntü (her kategoriden 2), önerilen 20+ görüntü.

### Q2: Kendi kamera kayıtlarımı kullanabilir miyim?
**A:** Evet, KVKK uyumluluğu sağlandığında kullanabilirsiniz.

### Q3: Video formatı neden önemli?
**A:** MP4/H.264 en iyi uyumluluk ve performans sağlar.

### Q4: Düşük kaliteli görüntüler çalışır mı?
**A:** Evet ama tespit doğruluğu düşer. HD kalite önerilir.

### Q5: Gece görüntüleri destekleniyor mu?
**A:** Evet, yeterli aydınlatma varsa (IR kameralar da çalışır).

---

## Destek / Support

Veri hazırlama konusunda yardıma mı ihtiyacınız var?
Need help with data preparation?

**İletişim / Contact:**
- Email: support@ppe-detection.com
- Tel: +90 XXX XXX XX XX

**Kaynaklar / Resources:**
- [Veri Hazırlama Rehberi](../docs/data_preparation_guide.pdf)
- [Video Eğitimler](https://youtube.com/...)
- [Örnek Veri Seti](https://drive.google.com/...)

---

**Son Güncelleme / Last Updated:** 2024-11-18
**Versiyon / Version:** 1.0
