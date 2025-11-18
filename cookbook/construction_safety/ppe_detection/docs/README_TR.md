# Şantiye Güvenliği için KKD Tespit Sistemi

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Docker](https://img.shields.io/badge/Docker-hazır-blue.svg)

> **Yapay zeka destekli bilgisayarlı görü kullanarak inşaat şantiyeleri için gerçek zamanlı Kişisel Koruyucu Donanım (KKD) tespit sistemi**

[🇬🇧 English Version](./README.md) | [📖 Dokümantasyon](./ARCHITECTURE.md) | [🚀 Hızlı Başlangıç](#hızlı-başlangıç)

---

## 📋 İçindekiler

- [Genel Bakış](#genel-bakış)
- [Neden KKD Tespiti?](#neden-kkd-tespiti)
- [Temel Özellikler](#temel-özellikler)
- [Hızlı Başlangıç](#hızlı-başlangıç)
- [Kurulum](#kurulum)
- [Yapılandırma](#yapılandırma)
- [Kullanım Örnekleri](#kullanım-örnekleri)
- [Ekran Görüntüleri](#ekran-görüntüleri)
- [API Dokümantasyonu](#api-dokümantasyonu)
- [Sorun Giderme](#sorun-giderme)
- [Katkıda Bulunma](#katkıda-bulunma)
- [Lisans](#lisans)

---

## 🎯 Genel Bakış

KKD Tespit Sistemi, inşaat şantiyelerinde kişisel koruyucu donanım uyumluluğunu otomatik olarak tespit etmek ve uygulamak için özel olarak tasarlanmış, yapay zeka destekli gerçek zamanlı bir izleme çözümüdür. En son teknoloji bilgisayarlı görü modelleri (YOLO) kullanarak canlı kamera beslemelerini izler, işçileri tespit eder ve baret, emniyet yeleği, eldiven ve diğer KKD gibi gerekli güvenlik ekipmanlarını giyip giymediğini doğrular.

### Değer Önerisi

- **⚡ Gerçek Zamanlı Tespit**: Saniyenin altında işleme süreleri ile anlık KKD uyumluluk kontrolü
- **🎯 Yüksek Doğruluk**: Gelişmiş YOLO modelleri ile %95+ tespit doğruluğu
- **📹 Çoklu Kamera Desteği**: Aynı anda birden fazla şantiye bölgesini izleme
- **🔔 Akıllı Uyarılar**: E-posta, SMS, Telegram ve webhook ile otomatik bildirimler
- **📊 Analiz Panosu**: Kapsamlı uyumluluk raporlaması ve trend analizi
- **💰 Maliyet Etkin**: İş kazalarını ve ilgili maliyetleri %70'e kadar azaltma
- **⚖️ Yasal Uyumluluk**: İSG ve diğer güvenlik standartlarını otomatik olarak karşılama

---

## 🏗️ Neden Şantiyelerde KKD Tespiti?

### Problem

İnşaat şantiyeleri en tehlikeli çalışma ortamları arasındadır:
- Her yıl **10 inşaat işçisinden 1'i** yaralanıyor
- **Kafa yaralanmaları** tüm inşaat ölümlerinin %10'unu oluşturuyor
- **Manuel güvenlik izleme** tutarsız ve emek yoğun
- **Uyumluluk ihlalleri** ağır cezalar ve yasal sorumlulukla sonuçlanıyor

### Çözüm

KKD Tespit Sistemimiz şunları sağlar:

1. **Otomatik İzleme**: İnsan yorgunluğu olmadan 7/24 gözetim
2. **Anlık İhlal Tespiti**: KKD eksikliğinde anında uyarılar
3. **Geçmiş Analizler**: Zaman içinde uyumluluk trendlerini izleme
4. **Kanıt Belgeleme**: Olaylar için otomatik görüntü yakalama
5. **Önleyici Güvenlik**: Kazalar olmadan önce durdurma

### Yatırım Getirisi Faydaları

- ✅ İş kazalarını **%60-70 azaltma**
- ✅ Proaktif güvenlik önlemleri göstererek **sigorta primlerini düşürme**
- ✅ **İSG cezalarından kaçınma** (ihlal başına 7.000-145.000 USD)
- ✅ Otomatik uyumluluk izleme ile **verimliliği artırma**
- ✅ Veri odaklı içgörüler ile **güvenlik kültürünü geliştirme**

Detaylı yatırım getirisi analizi için [İş Vakası Dokümanımıza](./BUSINESS_CASE.md) bakın.

---

## ✨ Temel Özellikler

### 🔍 Tespit Yetenekleri

- **Tespit Edilen KKD Ürünleri**:
  - 🪖 Baretler / Güvenlik kaskları
  - 🦺 Yüksek görünürlüklü emniyet yelekleri
  - 🧤 Güvenlik eldivenleri
  - 👢 Güvenlik botları
  - 🥽 Koruyucu gözlükler
  - 😷 Yüz maskeleri

- **Gelişmiş Tespit**:
  - Tek karede çoklu kişi tespiti
  - 10-30 FPS'de gerçek zamanlı işleme
  - Yapılandırılabilir güven eşikleri
  - Bölgeye özel KKD gereksinimleri
  - Kareler arası kişi takibi

### 🎥 Kamera Yönetimi

- **RTSP Kamera Desteği**: Çoğu IP kamera ile uyumlu
- **Çoklu Kamera İzleme**: Aynı anda 10+ kamerayı yönetme
- **Bölge Yapılandırması**: Bölge başına farklı KKD gereksinimleri
- **Kamera Sağlık İzleme**: Otomatik yeniden bağlanma ve sağlık kontrolleri
- **Esnek Zamanlama**: Kamera başına tespit aralıklarını yapılandırma

### 📊 Analiz ve Raporlama

- **Gerçek Zamanlı Panel**: Canlı uyumluluk istatistikleri
- **Geçmiş Raporlar**: Günlük, haftalık, aylık uyumluluk trendleri
- **İhlal Kayıtları**: Görüntü kanıtı ile detaylı kayıtlar
- **Kamera Performansı**: İşleme süresi ve tespit metrikleri
- **Dışa Aktarma**: CSV, PDF, Excel raporları

### 🔔 Uyarı Sistemi

- **Çoklu Bildirim Kanalları**:
  - 📧 E-posta uyarıları
  - 💬 Telegram bildirimleri
  - 📱 SMS uyarıları
  - 🔗 Webhook entegrasyonları
  - 🌐 WebSocket gerçek zamanlı güncellemeler

- **Akıllı Uyarı Kuralları**:
  - Yapılandırılabilir eşikler
  - Uyarı bekleme süreleri
  - Ciddiyet seviyeleri (düşük, orta, yüksek, kritik)
  - Özel uyarı şablonları

### 🔒 Kurumsal Özellikler

- **Ölçeklenebilir Mimari**: Yüzlerce kamerayı yönetme
- **Yüksek Kullanılabilirlik**: Redis önbellekleme, veritabanı replikasyonu
- **API-Öncelikli Tasarım**: Entegrasyonlar için RESTful API
- **Docker Dağıtımı**: Kolay konteynerleştirilmiş dağıtım
- **İzleme Yığını**: Prometheus + Grafana entegrasyonu
- **Veritabanı Migrasyonları**: Otomatik şema güncellemeleri

---

## 🚀 Hızlı Başlangıç

### Ön Gereksinimler

- Docker & Docker Compose (önerilen)
- VEYA Python 3.9+ ve pip

### Seçenek 1: Docker (Önerilen)

```bash
# Depoyu klonlayın
git clone <repository-url>
cd ppe_detection

# Ortam dosyasını kopyalayın ve yapılandırın
cp .env.example .env
nano .env  # Ayarlarınızla düzenleyin

# Tüm servisleri başlatın
make install
make start

# Logları görüntüleyin
make logs

# Uygulamaya erişin
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Sağlık: http://localhost:8000/health
```

### Seçenek 2: Yerel Kurulum

```bash
# Sanal ortam oluşturun
python -m venv venv
source venv/bin/activate  # Windows'ta: venv\Scripts\activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Ortamı kurun
cp .env.example .env
nano .env

# Veritabanını başlatın
python -m src.database.migrate

# Uygulamayı çalıştırın
python run_api.py
```

### Kurulumu Doğrulayın

```bash
# Sağlık endpoint'ini kontrol edin
curl http://localhost:8000/health

# Beklenen yanıt:
{
  "status": "healthy",
  "version": "0.1.0",
  "database_connected": true,
  "model_loaded": true
}
```

---

## 📥 Kurulum

### Sistem Gereksinimleri

**Minimum Gereksinimler:**
- CPU: 4 çekirdek
- RAM: 8 GB
- Depolama: 50 GB
- İşletim Sistemi: Linux (Ubuntu 20.04+), macOS, Windows 10+

**Üretim İçin Önerilen:**
- CPU: 8+ çekirdek
- RAM: 16 GB
- Depolama: 200 GB SSD
- GPU: 6GB+ VRAM ile NVIDIA GPU (opsiyonel, daha hızlı işleme için)
- İşletim Sistemi: Ubuntu 22.04 LTS

**Ağ Gereksinimleri:**
- Kamera başına minimum 10 Mbps
- Açık portlar: 8000 (API), 5432 (PostgreSQL), 6379 (Redis)

Detaylı kurulum talimatları için [SETUP.md](./SETUP.md) dosyasına bakın.

---

## ⚙️ Yapılandırma

### Ortam Değişkenleri

`.env` dosyasındaki temel yapılandırma seçenekleri:

```bash
# Uygulama
APP_ENV=production
APP_PORT=8000
LOG_LEVEL=info

# Veritabanı
DB_NAME=ppe_detection
DB_USER=postgres
DB_PASSWORD=güvenli_şifreniz

# Tespit Ayarları
DETECTION_CONFIDENCE_THRESHOLD=0.5  # 0.0 - 1.0
DETECTION_IOU_THRESHOLD=0.45

# Kameralar (virgülle ayrılmış)
CAMERA_URLS=rtsp://kamera1/stream,rtsp://kamera2/stream

# Uyarılar
ENABLE_ALERTS=true
ALERT_EMAIL_TO=guvenlik@sirket.com
```

### Kamera Yapılandırması

API veya yapılandırma dosyası üzerinden kamera ekleyin:

```python
# API üzerinden
POST /api/cameras
{
  "name": "Ana Giriş Kamerası",
  "rtsp_url": "rtsp://192.168.1.100:554/stream",
  "location": "Ana Giriş",
  "zone": "Bölge A",
  "detection_interval": 5,
  "confidence_threshold": 0.7,
  "required_ppe": ["helmet", "vest"]
}
```

Detaylı yapılandırma kılavuzu için [SETUP.md](./SETUP.md#yapılandırma) dosyasına bakın.

---

## 💡 Kullanım Örnekleri

### Örnek 1: Tek Görüntüde KKD Tespiti

```bash
curl -X POST "http://localhost:8000/api/detect" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@isci_resmi.jpg" \
  -F "confidence_threshold=0.7"
```

### Örnek 2: Tüm İhlalleri Listeleme

```python
import httpx

response = httpx.get(
    "http://localhost:8000/api/violations",
    params={
        "start_date": "2024-01-01T00:00:00",
        "end_date": "2024-01-31T23:59:59",
        "acknowledged": False
    }
)

violations = response.json()
for violation in violations:
    print(f"Kamera: {violation['camera_name']}")
    print(f"Eksik KKD: {violation['missing_ppe']}")
    print(f"Zaman: {violation['timestamp']}")
```

### Örnek 3: Gerçek Zamanlı İstatistikler

```python
import httpx

response = httpx.get("http://localhost:8000/api/stats")
stats = response.json()

print(f"Toplam Tespit: {stats['total_detections']}")
print(f"Uyumluluk Oranı: {stats['overall_compliance_rate']}%")
print(f"Aktif Kameralar: {stats['active_cameras']}")
```

### Örnek 4: WebSocket Canlı Besleme

```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/live?camera_id=1');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Tespit:', data);
    // Gerçek zamanlı tespit verileri ile UI'ı güncelle
};
```

Daha fazla örnek için [API.md](./API.md#örnekler) ve [examples/](../examples/) dizinine bakın.

---

## 📚 API Dokümantasyonu

### Temel Endpoint'ler

| Metod | Endpoint | Açıklama |
|-------|----------|----------|
| POST | `/api/detect` | Yüklenen görüntüde KKD tespiti |
| GET | `/api/cameras` | Tüm kameraları listele |
| POST | `/api/cameras` | Yeni kamera ekle |
| GET | `/api/violations` | İhlalleri filtrelerle listele |
| GET | `/api/stats` | Sistem istatistikleri |
| GET | `/api/health` | Sağlık kontrolü |
| WS | `/api/ws/live` | WebSocket canlı besleme |

### Hızlı API Testi

```bash
# Sağlık kontrolü
curl http://localhost:8000/health

# İnteraktif API dokümantasyonu
# Tarayıcıda açın: http://localhost:8000/docs
```

Tam API dokümantasyonu için [API.md](./API.md) dosyasına bakın.

---

## 🔧 Sorun Giderme

### Yaygın Sorunlar

#### 1. Docker konteynerları başlamıyor

```bash
# Konteyner durumunu kontrol edin
make ps

# Logları görüntüleyin
make logs

# Servisleri yeniden başlatın
make restart
```

#### 2. Kamera bağlantısı başarısız

**Problem**: Kamera "çevrimdışı" veya "hata" durumunu gösteriyor

**Çözümler**:
- RTSP URL'sinin doğru olduğunu kontrol edin: `rtsp://kullanici:sifre@ip:port/stream`
- Ağ bağlantısını kontrol edin: `ping kamera_ip`
- VLC ile stream'i test edin: `vlc rtsp://kamera_url`
- Kamera kimlik bilgilerini doğrulayın
- Güvenlik duvarı kurallarını kontrol edin

#### 3. Düşük tespit doğruluğu

**Problem**: Çok fazla yanlış pozitif veya kaçırılan tespit

**Çözümler**:
- Güven eşiğini ayarlayın (varsayılan: 0.5)
- İyi kamera konumlandırma ve aydınlatma sağlayın
- Daha yüksek çözünürlüklü kameralar kullanın (minimum 1080p)
- Özel ortamınız için kalibre edin
- Şantiyeye özel verilerle modeli yeniden eğitin

#### 4. Veritabanı bağlantı hataları

```bash
# Veritabanı durumunu kontrol edin
make db-shell

# Bağlantı başarısız olursa, veritabanını yeniden başlatın
docker-compose restart db

# Veritabanı loglarını kontrol edin
make logs-db
```

#### 5. Yüksek bellek kullanımı

**Problem**: Sistem bellekten tükeniyor

**Çözümler**:
- Eşzamanlı kamera sayısını azaltın
- Kare işleme hızını düşürün (`FRAME_PROCESSING_INTERVAL`'i artırın)
- Görüntü çözünürlüğünü azaltın
- Varsa GPU işlemeyi etkinleştirin
- Birden fazla instance ile yatay ölçeklendirin

---

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Nasıl yardımcı olabilirsiniz:

### Geliştirme Kurulumu

```bash
# Depoyu fork edin ve klonlayın
git clone <your-fork>
cd ppe_detection

# Geliştirme bağımlılıklarını yükleyin
pip install -r requirements.txt
pip install -e ".[dev]"

# Testleri çalıştırın
pytest

# Linter'ı çalıştırın
black src/
ruff check src/
```

### Katkı Kuralları

1. **Kod Stili**: PEP 8'i takip edin, Black formatter kullanın
2. **Test**: Yeni özellikler için test yazın
3. **Dokümantasyon**: API değişiklikleri için dokümanları güncelleyin
4. **Commit'ler**: Açık, tanımlayıcı commit mesajları kullanın
5. **Pull Request'ler**: Açıklama ve test sonuçları ekleyin

---

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır - detaylar için [LICENSE](../LICENSE) dosyasına bakın.

---

## 📞 Destek ve İletişim

- 🌐 Website: [ppe-detection.local](http://ppe-detection.local)
- 📧 E-posta: support@ppe-detection.local
- 💬 Discord: [Topluluğumuza katılın](https://discord.gg/ppe-detection)
- 🐛 Sorunlar: [GitHub Issues](https://github.com/your-org/ppe-detection/issues)

---

**İnşaat güvenliği için ❤️ ile yapılmıştır**
