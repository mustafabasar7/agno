# KKD Tespit Sistemi - Demo Rehberi
# PPE Detection System - Demo Guide

## İçindekiler / Table of Contents

1. [Genel Bakış / Overview](#genel-bakış--overview)
2. [Kurulum / Setup](#kurulum--setup)
3. [Demo Senaryoları / Demo Scenarios](#demo-senaryoları--demo-scenarios)
4. [Satış Konuşma Noktaları / Sales Talking Points](#satış-konuşma-noktaları--sales-talking-points)
5. [Yaygın İtirazlar ve Yanıtları / Common Objections and Responses](#yaygın-itirazlar-ve-yanıtları--common-objections-and-responses)
6. [Teknik Detaylar / Technical Details](#teknik-detaylar--technical-details)

---

## Genel Bakış / Overview

Bu demo paketi, KKD (Kişisel Koruyucu Donanım) tespit sisteminin tüm özelliklerini Türk inşaat firmalarına sunmak için tasarlanmıştır.

This demo package is designed to showcase all features of the PPE (Personal Protective Equipment) detection system to Turkish construction companies.

### Sistem Yetenekleri / System Capabilities

✅ **Gerçek Zamanlı Tespit / Real-time Detection**
- Baret (kask) tespiti / Helmet detection
- Yelek tespiti / Safety vest detection
- Çoklu işçi takibi / Multiple worker tracking

✅ **Otomatik Uyumluluk Kontrolü / Automatic Compliance Checking**
- KKD eksikliklerini tespit / Detect PPE violations
- Anlık uyarılar / Instant alerts
- Detaylı raporlama / Detailed reporting

✅ **Çoklu Kamera Desteği / Multi-camera Support**
- Sınırsız kamera / Unlimited cameras
- Merkezi izleme / Centralized monitoring
- Bölge bazlı analiz / Zone-based analysis

✅ **Yapay Zeka Destekli / AI-Powered**
- %95+ doğruluk oranı / 95%+ accuracy rate
- Sürekli öğrenme / Continuous learning
- Hava koşullarına dayanıklı / Weather-resistant

---

## Kurulum / Setup

### Hızlı Başlangıç / Quick Start

```bash
# 1. Demo dizinine gidin / Navigate to demo directory
cd demo/

# 2. Hızlı demo (5 dakika) / Quick demo (5 minutes)
./scripts/quick_demo.sh

# 3. Tam demo (15-20 dakika) / Full demo (15-20 minutes)
./scripts/full_demo.sh

# 4. Dashboard'u başlatın / Start dashboard
python3 demo_dashboard.py --mode html
```

### Docker ile Kurulum / Setup with Docker

```bash
# Demo ortamını başlatın / Start demo environment
docker-compose -f docker-compose.demo.yml up -d

# Erişim adresleri / Access URLs:
# - API: http://localhost:8000
# - Dashboard: http://localhost:5000
# - Docs: http://localhost:8000/api/docs
```

### Sistem Gereksinimleri / System Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8 GB
- Disk: 20 GB
- İnternet: Kurulum için / For setup

**Önerilen / Recommended:**
- CPU: 8+ cores
- RAM: 16 GB
- GPU: NVIDIA (opsiyonel, 3x hızlandırma / optional, 3x speedup)
- Disk: 50 GB SSD

---

## Demo Senaryoları / Demo Scenarios

### Senaryo 1: Hızlı Demo (5 Dakika) / Quick Demo (5 Minutes)

**Amaç / Purpose:** Sistemi hızlıca tanıtmak, temel özellikleri göstermek

**Adımlar / Steps:**

1. **Açılış (30 saniye / 30 seconds)**
   ```
   "İş güvenliği maliyetlerinizi azaltmak ve iş kazalarını önlemek için
   yapay zeka destekli KKD tespit sistemimizi göstereceğim."

   "I'll show you our AI-powered PPE detection system that reduces
   safety costs and prevents workplace accidents."
   ```

2. **Tek Görüntü Analizi (2 dakika / 2 minutes)**
   - Örnek inşaat sahası görüntüsü yükle
   - Baret ve yelek tespitini göster
   - Uyumlu/uyumsuz işçileri vurgula

   **Konuşma Noktası:**
   ```
   "Sistem saniyeler içinde tüm işçileri tespit ediyor ve KKD eksikliklerini
   belirliyor. Görüyorsunuz ki 3 işçi tam donanımlı, 1 işçinin bareti eksik."
   ```

3. **Toplu Analiz (1.5 dakika / 1.5 minutes)**
   - 10 görüntüyü birden işle
   - İstatistikleri göster
   - Uyumluluk oranını vurgula

   **Konuşma Noktası:**
   ```
   "Günde binlerce görüntüyü otomatik analiz edebilir,
   uyumluluk raporları oluşturabilirsiniz."
   ```

4. **Dashboard Gösterimi (1 dakika / 1 minute)**
   - Canlı dashboard'u aç
   - Gerçek zamanlı ihlalleri göster
   - İstatistikleri vurgula

5. **Kapanış (30 saniye / 30 seconds)**
   ```
   "Sistemimiz 7/24 çalışır, anında uyarır ve raporlar.
   Detaylı bilgi için görüşelim."
   ```

### Senaryo 2: Detaylı Demo (15 Dakika) / Detailed Demo (15 Minutes)

**Amaç / Purpose:** Tüm özellikleri detaylıca göstermek

**Adımlar / Steps:**

1. **Giriş ve Problem Tanımı (2 dakika)**
   - İş kazası istatistikleri
   - KKD uyumsuzluğunun maliyetleri
   - Yasal zorunluluklar

2. **Sistem Mimarisi (2 dakika)**
   - Kamera entegrasyonu
   - Merkezi sunucu
   - Uyarı sistemi
   - Raporlama

3. **Canlı Demo (8 dakika)**
   - Görüntü işleme
   - Video analizi
   - Gerçek zamanlı tespit
   - Dashboard özellikleri

4. **ROI Hesaplaması (2 dakika)**
   - Kaza maliyetleri
   - Ceza tasarrufları
   - Sigorta primleri
   - Geri dönüş süresi

5. **Sonraki Adımlar (1 dakika)**
   - Pilot uygulama
   - Fiyatlandırma
   - Destek

### Senaryo 3: Teknik Demo (30 Dakika) / Technical Demo (30 Minutes)

**Hedef Kitle / Target Audience:** IT ekipleri, teknik yöneticiler

**İçerik / Content:**
- API entegrasyonu
- Kamera sistemi kurulumu
- Veritabanı yapısı
- Güvenlik özellikleri
- Performans metrikleri
- Özelleştirme seçenekleri

---

## Satış Konuşma Noktaları / Sales Talking Points

### 1. İş Güvenliği / Workplace Safety

**Türkçe:**
```
"Türkiye'de her yıl inşaat sektöründe 500+ ölümlü iş kazası yaşanıyor.
Bu kazaların %60'ı KKD kullanılmamasından kaynaklanıyor. Sistemimiz
bu kazaları önlemeye yardımcı olur."
```

**English:**
```
"Turkey sees 500+ fatal construction accidents yearly, 60% caused by
lack of PPE. Our system helps prevent these accidents."
```

### 2. Yasal Uyumluluk / Legal Compliance

**Türkçe:**
```
"6331 sayılı İş Sağlığı ve Güvenliği Kanunu, işverenleri KKD kullanımını
denetlemekle yükümlü kılıyor. Sistemimiz otomatik denetim ve dokümantasyon
sağlayarak yasal sorumluluklarınızı yerine getirmenize yardımcı olur."
```

### 3. Maliyet Tasarrufu / Cost Savings

**Türkçe:**
```
"Bir iş kazası ortalama 50.000-200.000 TL maliyete yol açıyor.
Sistem aylık maliyeti bu tutarın çok altında. İlk kazayı önlediğinizde
sistem maliyetini amorti etmiş olursunuz."
```

### 4. Operasyonel Verimlilik / Operational Efficiency

**Türkçe:**
```
"Güvenlik görevlileriniz 20-30 kamerayı takip edemez. Sistemimiz
7/24 tüm kameraları izler, sadece ihlal olduğunda uyarır.
İnsan kaynaklarınızı daha verimli kullanırsınız."
```

### 5. Veri ve Raporlama / Data and Reporting

**Türkçe:**
```
"Detaylı raporlar sayesinde hangi bölgelerde, hangi saatlerde daha çok
ihlal olduğunu görürsünüz. Bu verilerle eğitim ve önlem planları yapabilirsiniz."
```

### 6. Kolay Entegrasyon / Easy Integration

**Türkçe:**
```
"Mevcut kamera sisteminizle çalışır. Yeni kamera almaya gerek yok.
2-3 gün içinde kurulum tamamlanır, hemen kullanmaya başlarsınız."
```

---

## Yaygın İtirazlar ve Yanıtları / Common Objections and Responses

### İtiraz 1: "Çok Pahalı" / "Too Expensive"

**Yanıt / Response:**
```
Türkçe:
"Maliyeti değil, tasarrufu düşünelim. Bir iş kazası 100.000+ TL
tutabilir. Sistemimiz ayda X TL. İlk yıl 5-10 kat geri dönüş sağlar.
Ayrıca sigorta primlerinizde %15-20 indirim alabilirsiniz."

English:
"Let's think about savings, not cost. One accident can cost 100,000+ TL.
Our system is X TL/month. First year ROI is 5-10x. Plus, you can get
15-20% insurance premium discounts."
```

### İtiraz 2: "Mevcut Sistemimiz Var" / "We Have Existing System"

**Yanıt / Response:**
```
Türkçe:
"Mevcut sistemimiz kamera kayıt ediyor ama analiz etmiyor.
Kazadan sonra kayıtları izlemek yerine, kazayı önlemek daha iyi değil mi?
Ayrıca sistemimiz mevcut kameralarınızla entegre çalışır."

English:
"Existing systems record but don't analyze. Preventing accidents is better
than watching recordings after, right? Our system integrates with your
existing cameras."
```

### İtiraz 3: "İşçiler Rahatsız Olur" / "Workers Will Be Uncomfortable"

**Yanıt / Response:**
```
Türkçe:
"Sistem kimseyi cezalandırmak için değil, korumak için. İhlal tespit
edildiğinde önce nazik hatırlatma yapılır. İstatistikler gösteriyor ki
sistem kurulduktan sonra işçiler daha dikkatli oluyor ve kazalar azalıyor."

English:
"System is for protection, not punishment. Violations trigger gentle
reminders first. Statistics show workers become more careful and
accidents decrease after installation."
```

### İtiraz 4: "Hata Yapar mı?" / "Does It Make Mistakes?"

**Yanıt / Response:**
```
Türkçe:
"Yapay zeka %95+ doğrulukla çalışır. Her tespit kayıt altına alınır,
yanlış alarmları gözden geçirip sistemi eğitebilirsiniz.
Zamanla doğruluk oranı daha da artar."

English:
"AI works with 95%+ accuracy. All detections are recorded, you can review
false alarms and train the system. Accuracy improves over time."
```

### İtiraz 5: "Kurulum Zor mu?" / "Is Installation Difficult?"

**Yanıt / Response:**
```
Türkçe:
"Hayır, çok basit. Teknik ekibimiz 2-3 günde kurulumu yapar,
sistemi konfigüre eder ve ekibinizi eğitir. Kurulum sırasında
operasyonlarınız aksamamaz."

English:
"No, very simple. Our tech team completes installation in 2-3 days,
configures system and trains your team. Operations continue uninterrupted
during installation."
```

### İtiraz 6: "İnternet Kesintisi Olursa?" / "What If Internet Fails?"

**Yanıt / Response:**
```
Türkçe:
"Sistem lokal olarak çalışır, internete bağımlı değil. İnternet sadece
uzaktan erişim ve bulut yedekleme için kullanılır. İnternet kesilse bile
tespit ve kayıt devam eder."

English:
"System works locally, not internet-dependent. Internet only used for
remote access and cloud backup. Detection and recording continue even
without internet."
```

---

## Teknik Detaylar / Technical Details

### Model Spesifikasyonları / Model Specifications

- **Model:** YOLOv8 (You Only Look Once)
- **Doğruluk / Accuracy:** 95%+
- **İşleme Hızı / Processing Speed:** 30 FPS
- **Tespit Edilen Nesneler / Detected Objects:**
  - İnsan / Person
  - Baret / Helmet
  - Yelek / Safety vest
  - (Genişletilebilir / Expandable)

### Sistem Mimarisi / System Architecture

```
┌─────────────┐
│  Kameralar  │
│  Cameras    │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Video Akışı     │
│ Video Stream    │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ AI Model        │
│ (PPE Detection) │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Analiz & Kayıt  │
│ Analysis & Log  │
└──────┬──────────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌─────────────┐   ┌──────────────┐
│  Uyarılar   │   │   Raporlar   │
│  Alerts     │   │   Reports    │
└─────────────┘   └──────────────┘
```

### API Endpoints

```
GET  /api/health              - Sistem durumu / System status
POST /api/detect              - Görüntü analizi / Image analysis
GET  /api/violations          - İhlal listesi / Violation list
GET  /api/statistics          - İstatistikler / Statistics
GET  /api/reports/daily       - Günlük rapor / Daily report
POST /api/cameras/add         - Kamera ekle / Add camera
```

### Veri Formatları / Data Formats

**Tespit Sonucu / Detection Result:**
```json
{
  "timestamp": "2024-11-18T10:30:00Z",
  "camera_id": "CAM_001",
  "detections": [
    {
      "type": "person",
      "bbox": [100, 150, 200, 400],
      "confidence": 0.98,
      "has_helmet": true,
      "has_vest": false,
      "compliant": false
    }
  ],
  "violation_count": 1,
  "image_url": "/storage/detections/img_001.jpg"
}
```

### Güvenlik / Security

- ✅ HTTPS/TLS şifreleme / encryption
- ✅ Kullanıcı kimlik doğrulama / User authentication
- ✅ Rol tabanlı erişim / Role-based access
- ✅ Veri şifreleme / Data encryption
- ✅ Audit log / Denetim kaydı
- ✅ GDPR/KVKK uyumlu / compliant

### Performans / Performance

| Metrik | Değer | Notlar |
|--------|-------|--------|
| FPS (CPU) | 15-20 | Intel i5+ |
| FPS (GPU) | 60-90 | NVIDIA GTX 1660+ |
| Gecikme / Latency | <100ms | Gerçek zamanlı / Real-time |
| Kamera/Sunucu | 10-20 | CPU'ya bağlı / CPU dependent |
| Doğruluk / Accuracy | 95%+ | Test verilerinde / On test data |

---

## Fiyatlandırma Örneği / Pricing Example

### Paket 1: Başlangıç / Starter
- **5 kamera**
- **1 saha / site**
- **Temel raporlar / Basic reports**
- **Email destek / support**
- **Fiyat / Price:** ₺2,500/ay (≈$85/month)

### Paket 2: Profesyonel / Professional
- **20 kamera**
- **3 saha / site**
- **Gelişmiş raporlar / Advanced reports**
- **SMS uyarılar / SMS alerts**
- **7/24 destek / support**
- **Fiyat / Price:** ₺7,500/ay (≈$250/month)

### Paket 3: Kurumsal / Enterprise
- **Sınırsız kamera / Unlimited cameras**
- **Sınırsız saha / Unlimited sites**
- **Özel raporlar / Custom reports**
- **API entegrasyonu / API integration**
- **Yerinde destek / On-site support**
- **Fiyat / Price:** Özel / Custom

### ROI Hesaplama / ROI Calculation

**Senaryo / Scenario:** Orta ölçekli inşaat firması (100 işçi)

```
Yıllık Maliyetler / Annual Costs:
- İş kazası riski: 2 kaza x 100,000 TL = 200,000 TL
- SGK cezaları: ~50,000 TL
- Sigorta primi artışı: ~30,000 TL
TOPLAM RİSK / TOTAL RISK: ~280,000 TL

Sistem Maliyeti / System Cost:
- Profesyonel paket: 7,500 x 12 = 90,000 TL
- Kurulum: 15,000 TL
TOPLAM MALİYET / TOTAL COST: 105,000 TL

Tasarruf Potansiyeli / Savings Potential:
- Kaza önleme: ~150,000 TL
- Ceza önleme: ~40,000 TL
- Sigorta indirimi: ~20,000 TL
TOPLAM TASARRUF / TOTAL SAVINGS: ~210,000 TL

Net Fayda / Net Benefit: 210,000 - 105,000 = 105,000 TL
ROI: 100% (İlk yılda başabaş ve daha fazlası / Break-even + profit in year 1)
```

---

## Demo Checklist

### Demo Öncesi / Before Demo
- [ ] Laptop şarjı dolu / Laptop fully charged
- [ ] Demo dosyaları hazır / Demo files ready
- [ ] İnternet bağlantısı test edildi / Internet tested
- [ ] Yedek demo (offline) hazır / Offline demo ready
- [ ] Broşürler basıldı / Brochures printed
- [ ] Kartvizitler hazır / Business cards ready
- [ ] Fiyat listesi güncel / Price list updated

### Demo Sırasında / During Demo
- [ ] Kendini tanıt / Introduce yourself
- [ ] Firma hakkında bilgi al / Learn about company
- [ ] İhtiyaçları dinle / Listen to needs
- [ ] Demo'yu ihtiyaçlara göre ayarla / Customize demo
- [ ] Soruları yanıtla / Answer questions
- [ ] ROI hesapla / Calculate ROI
- [ ] Sonraki adımları planla / Plan next steps

### Demo Sonrası / After Demo
- [ ] Teşekkür emaili gönder / Send thank you email
- [ ] Demo kaydı paylaş / Share demo recording
- [ ] Teklif hazırla / Prepare proposal
- [ ] Takip görüşmesi planla / Schedule follow-up
- [ ] CRM'e not ekle / Add notes to CRM

---

## İletişim / Contact

**Teknik Destek / Technical Support:**
- Email: support@ppe-detection.com
- Tel: +90 XXX XXX XX XX
- WhatsApp: +90 XXX XXX XX XX

**Satış / Sales:**
- Email: sales@ppe-detection.com
- Tel: +90 XXX XXX XX XX

**Demo Talep / Request Demo:**
- Web: www.ppe-detection.com/demo
- Form: www.ppe-detection.com/contact

---

## Kaynaklar / Resources

- [Ürün Broşürü / Product Brochure](./presentation/product_brochure.pdf)
- [Teknik Döküman / Technical Documentation](./presentation/technical_specs.pdf)
- [Video Demo / Demo Video](./presentation/demo_video.mp4)
- [Başarı Hikayeleri / Success Stories](./presentation/case_studies.pdf)

---

**Son Güncelleme / Last Updated:** 2024-11-18
**Versiyon / Version:** 1.0.0
