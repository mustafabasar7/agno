# İnşaat Güvenliği - KKD Tespit Sistemi Web Dashboard

Bu web dashboard, kişisel koruyucu donanım (KKD) tespit sisteminin görsel arayüzüdür. Canlı kamera görüntülerini, ihlal bildirimlerini ve istatistikleri görüntülemek için kullanılır.

## 📋 Özellikler

### Canlı İzleme
- **Kamera Grid Görünümü**: Tüm kameraların canlı görüntülerini grid formatında gösterir
- **Durum Göstergeleri**: Her kamera için aktif/çevrimdışı durum göstergesi
- **İhlal Uyarıları**: Kameralarda tespit edilen ihlaller için görsel uyarılar

### İhlal Yönetimi
- **Canlı Bildirimler**: WebSocket üzerinden gerçek zamanlı ihlal bildirimleri
- **Geçmiş Kayıtları**: Filtrelenebilir ihlal geçmişi tablosu
- **Görüntü Önizleme**: İhlal görüntülerini büyütülebilir modal'da görüntüleme
- **CSV Export**: İhlal verilerini CSV formatında indirme

### İstatistikler
- **Dashboard Kartları**: Toplam ihlal, uyum oranı, aktif kameralar
- **Grafikler**: Chart.js ile zaman serisi ve dağılım grafikleri
- **Trend Analizi**: Saatlik, günlük ve aylık trend görünümleri

### Kamera Yönetimi
- **Kamera Ekleme/Silme**: Sistemdeki kameraları yönetme
- **Durum Kontrolü**: Kamera durumlarını görüntüleme ve değiştirme
- **Snapshot Görünümleri**: Her kameradan anlık görüntüler

## 🚀 Kurulum

### Gereksinimler

- Modern web tarayıcı (Chrome, Firefox, Safari, Edge)
- Web sunucu (development için Python HTTP sunucu veya Node.js http-server kullanılabilir)
- Backend API servisi (ihlal tespit sistemi)

### Hızlı Başlangıç

#### 1. Python HTTP Sunucu ile

```bash
# Frontend dizinine gidin
cd /home/user/agno/cookbook/construction_safety/ppe_detection/src/frontend

# Python 3 ile basit HTTP sunucu başlatın
python3 -m http.server 8080

# Tarayıcınızda açın
# http://localhost:8080
```

#### 2. Node.js http-server ile

```bash
# http-server kurulumu (global)
npm install -g http-server

# Frontend dizinine gidin
cd /home/user/agno/cookbook/construction_safety/ppe_detection/src/frontend

# Sunucu başlatın
http-server -p 8080

# Tarayıcınızda açın
# http://localhost:8080
```

#### 3. Nginx ile Production Deployment

```nginx
# /etc/nginx/sites-available/ppe-dashboard
server {
    listen 80;
    server_name your-domain.com;

    root /home/user/agno/cookbook/construction_safety/ppe_detection/src/frontend;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /ws {
        proxy_pass http://localhost:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
```

## ⚙️ Konfigürasyon

### API ve WebSocket Bağlantıları

`static/js/main.js` dosyasında API ve WebSocket URL'lerini düzenleyin:

```javascript
// Konfigürasyon
const API_BASE_URL = 'http://localhost:8000/api';  // Backend API URL
const WS_URL = 'ws://localhost:8000/ws';            // WebSocket URL
```

### Production Ortamı için:

```javascript
const API_BASE_URL = 'https://your-domain.com/api';
const WS_URL = 'wss://your-domain.com/ws';
```

## 📡 Backend API Gereksinimleri

Dashboard'un çalışması için aşağıdaki API endpoint'lerinin mevcut olması gerekir:

### REST API Endpoints

```
GET  /api/cameras              - Tüm kameraları listele
POST /api/cameras              - Yeni kamera ekle
GET  /api/cameras/{id}         - Kamera detayları
PATCH /api/cameras/{id}        - Kamera güncelle
DELETE /api/cameras/{id}       - Kamera sil

GET  /api/violations           - İhlalleri listele
GET  /api/violations/{id}      - İhlal detayları

GET  /api/statistics           - İstatistikleri getir
```

### WebSocket Events

#### Server → Client (Gelen)

```javascript
{
    "type": "violation_detected",
    "violationId": "viol_123",
    "timestamp": "2025-11-18T10:30:00Z",
    "cameraId": "cam1",
    "cameraName": "Giriş Kapısı",
    "violationType": "helmet",
    "confidence": 0.95,
    "imageUrl": "http://...",
    "thumbnailUrl": "http://..."
}

{
    "type": "camera_status_changed",
    "cameraId": "cam1",
    "status": "active" | "offline"
}

{
    "type": "statistics_update",
    "statistics": {
        "totalViolations": 150,
        "complianceRate": 87,
        "activeCameras": 4,
        "totalCameras": 5,
        "detectedWorkers": 23
    }
}

{
    "type": "camera_snapshot",
    "cameraId": "cam1",
    "snapshotUrl": "data:image/jpeg;base64,..."
}
```

#### Client → Server (Giden)

```javascript
{
    "type": "handshake",
    "clientId": "client_123",
    "timestamp": "2025-11-18T10:30:00Z"
}

{
    "type": "ping",
    "timestamp": "2025-11-18T10:30:00Z"
}
```

## 🎨 Özelleştirme

### Renk Şeması

`static/css/main.css` dosyasında CSS değişkenlerini düzenleyin:

```css
:root {
    --color-primary: #2563eb;      /* Ana renk */
    --color-danger: #ef4444;       /* İhlal rengi (kırmızı) */
    --color-success: #10b981;      /* Uyumlu renk (yeşil) */
    --color-warning: #f59e0b;      /* Uyarı rengi (sarı) */
    --color-inactive: #9ca3af;     /* Pasif renk (gri) */
}
```

### Dashboard Dili

Dashboard şu anda Türkçe olarak yapılandırılmıştır. Dil değiştirmek için:

1. `index.html` içindeki metin içeriklerini değiştirin
2. `static/js/main.js` içindeki `getViolationTypeLabel()` fonksiyonunu güncelleyin

## 📱 Responsive Tasarım

Dashboard üç farklı ekran boyutu için optimize edilmiştir:

- **Desktop (> 1024px)**: Tam özellikli görünüm, yan yana paneller
- **Tablet (768px - 1024px)**: Tek sütun düzeni, tam özellikler
- **Mobile (< 768px)**: Sadece görüntüleme modu, basitleştirilmiş arayüz

## 🔧 Geliştirme Modu

Backend API henüz hazır değilse, dashboard otomatik olarak mock (sahte) veri ile çalışır:

```javascript
// main.js içinde
function fetchInitialData() {
    try {
        // API çağrıları...
    } catch (error) {
        // Hata durumunda mock veri yükle
        loadMockData();
    }
}
```

Mock veri, geliştirme ve test için gerçekçi örnek veriler içerir.

## 📊 Grafik Özelleştirme

Chart.js grafikleri `static/js/charts.js` dosyasında özelleştirilebilir:

```javascript
// Grafik renklerini değiştirme
backgroundColor: [
    '#ef4444',  // Baret - Kırmızı
    '#f59e0b',  // Yelek - Turuncu
    '#3b82f6',  // Eldiven - Mavi
    '#8b5cf6',  // Bot - Mor
    '#10b981'   // Gözlük - Yeşil
]

// Animasyon süresi
duration: 750  // ms
```

## 🔒 Güvenlik Notları

### Production Deployment için:

1. **HTTPS Kullanın**: Tüm iletişim HTTPS üzerinden olmalı
2. **WebSocket Güvenliği**: WSS (WebSocket Secure) kullanın
3. **CORS Ayarları**: Backend'de uygun CORS başlıkları yapılandırın
4. **Authentication**: API endpoint'lerine kimlik doğrulama ekleyin
5. **Rate Limiting**: API isteklerini sınırlayın

### Örnek Backend CORS Ayarları (FastAPI)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🐛 Hata Ayıklama

### WebSocket Bağlantı Sorunları

```javascript
// Tarayıcı konsolunda WebSocket durumunu kontrol edin
console.log(ws.readyState);
// 0: CONNECTING, 1: OPEN, 2: CLOSING, 3: CLOSED
```

### API Çağrı Hataları

Chrome DevTools > Network sekmesinde API isteklerini kontrol edin:
- Status kodları
- Response verileri
- Request headers

### Chart Render Sorunları

```javascript
// Chart instance'ını kontrol edin
console.log(violationsChart);
console.log(violationTypesChart);
```

## 📁 Dosya Yapısı

```
frontend/
├── index.html              # Ana HTML dosyası
├── README.md              # Bu dosya
└── static/
    ├── css/
    │   └── main.css       # Tüm CSS stilleri
    └── js/
        ├── main.js        # Ana JavaScript, UI yönetimi
        ├── websocket.js   # WebSocket bağlantı yönetimi
        └── charts.js      # Chart.js grafik yönetimi
```

## 🔄 Güncelleme ve Bakım

### Cache Temizleme

Güncellemelerden sonra tarayıcı cache'ini temizleyin:
- Chrome: Ctrl+Shift+Delete
- Firefox: Ctrl+Shift+Delete
- Safari: Cmd+Option+E

### Versiyon Kontrolü

CSS ve JS dosyalarına versiyon numarası ekleyerek cache sorunlarını önleyin:

```html
<link rel="stylesheet" href="static/css/main.css?v=1.0.0">
<script src="static/js/main.js?v=1.0.0"></script>
```

## 🤝 Katkıda Bulunma

Geliştirmelere katkıda bulunmak için:

1. Yeni özellikler ekleyin
2. Hataları düzeltin
3. Dokümantasyonu güncelleyin
4. Test senaryoları ekleyin

## 📞 Destek

Sorun yaşarsanız:

1. Tarayıcı konsolundaki hata mesajlarını kontrol edin
2. Network sekmesinde API isteklerini inceleyin
3. Backend log'larını kontrol edin
4. WebSocket bağlantı durumunu doğrulayın

## 📝 Lisans

Bu proje, ana proje lisansı altında lisanslanmıştır.

---

**Son Güncelleme**: 2025-11-18

**Versiyon**: 1.0.0
