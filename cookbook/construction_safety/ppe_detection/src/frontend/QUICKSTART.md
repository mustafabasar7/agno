# 🚀 Hızlı Başlangıç Kılavuzu

## 3 Adımda Dashboard'u Başlatın

### 1️⃣ Backend API'yi Çalıştırın

Dashboard, backend API ile iletişim kurar. Backend servisi çalıştırın:

```bash
# Backend dizinine gidin ve servisi başlatın
cd /home/user/agno/cookbook/construction_safety/ppe_detection
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### 2️⃣ Dashboard Sunucusunu Başlatın

Yeni bir terminal açın ve frontend sunucusunu başlatın:

```bash
# Frontend dizinine gidin
cd /home/user/agno/cookbook/construction_safety/ppe_detection/src/frontend

# Python HTTP sunucu ile başlatın
python3 server.py

# VEYA doğrudan Python HTTP sunucu kullanın
python3 -m http.server 8080
```

### 3️⃣ Tarayıcıda Açın

```
http://localhost:8080
```

---

## 🎮 Demo Modu (Backend olmadan)

Backend henüz hazır değilse, dashboard otomatik olarak **mock (sahte) veri** ile çalışır.

Sadece adım 2'yi uygulayın ve tarayıcınızda açın. Dashboard otomatik olarak örnek verilerle çalışacaktır.

---

## ⚙️ Yapılandırma

### API ve WebSocket URL'lerini Değiştirme

`static/js/main.js` dosyasını düzenleyin:

```javascript
const API_BASE_URL = 'http://localhost:8000/api';  // Backend API
const WS_URL = 'ws://localhost:8000/ws';            // WebSocket
```

---

## 📋 Dashboard Özellikleri

✅ **Canlı Kamera Görüntüleri** - Grid formatında tüm kameralar
✅ **Gerçek Zamanlı İhlal Bildirimleri** - WebSocket ile anında uyarılar
✅ **İstatistik Kartları** - İhlal, uyum oranı, kamera durumları
✅ **İhlal Geçmişi** - Filtrelenebilir tablo ve CSV export
✅ **Grafikler** - Chart.js ile trend ve dağılım grafikleri
✅ **Kamera Yönetimi** - Kamera ekleme, silme, durum kontrolü
✅ **Responsive Tasarım** - Desktop, tablet, mobil uyumlu
✅ **Türkçe Arayüz** - Tam Türkçe kullanıcı arayüzü

---

## 🎨 Renk Kodları

| Renk | Anlamı | Kullanım |
|------|--------|----------|
| 🔴 Kırmızı | İhlal | İhlal bildirimleri ve uyarılar |
| 🟢 Yeşil | Uyumlu | Aktif kameralar, başarılı işlemler |
| 🟡 Sarı | Uyarı | Dikkat gerektiren durumlar |
| ⚫ Gri | Pasif | Çevrimdışı kameralar |

---

## 🔍 Sorun Giderme

### Kameralar Görünmüyor?
- Backend API'nin çalıştığından emin olun
- `http://localhost:8000/api/cameras` adresini tarayıcıda kontrol edin

### WebSocket Bağlanamıyor?
- WebSocket URL'sinin doğru olduğunu kontrol edin
- Tarayıcı konsolunda hata mesajlarını inceleyin
- Firewall ayarlarını kontrol edin

### Grafikler Yüklenmiyor?
- Chart.js CDN bağlantısını kontrol edin
- İnternet bağlantınızı doğrulayın
- Tarayıcı konsolunda hata mesajlarını inceleyin

---

## 📱 Mobil Kullanım

Dashboard mobil cihazlarda **salt görüntüleme modu** ile çalışır. Tam özellikler için desktop tarayıcı kullanın.

---

## 🔗 Faydalı Linkler

- **Backend API Docs**: `http://localhost:8000/docs`
- **Dashboard**: `http://localhost:8080`
- **Detaylı Dokümantasyon**: [README.md](README.md)

---

## 💡 İpuçları

1. **Mock Veri**: Backend olmadan test için otomatik mock veri yüklenir
2. **Canlı Güncellemeler**: WebSocket bağlantısı ile tüm veriler gerçek zamanlı güncellenir
3. **CSV Export**: İhlal geçmişini CSV formatında indirebilirsiniz
4. **Grafik Periyotları**: Bugün, Bu Hafta, Bu Ay seçenekleriyle trend analizi
5. **Keyboard Shortcuts**: Modal'ları ESC tuşu ile kapatabilirsiniz

---

**İyi çalışmalar! 🏗️**
