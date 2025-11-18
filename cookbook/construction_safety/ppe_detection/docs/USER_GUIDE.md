# KKD Tespit Sistemi - Kullanım Kılavuzu

Şantiye yöneticileri ve güvenlik görevlileri için kapsamlı kullanım kılavuzu.

## İçindekiler

- [Giriş](#giriş)
- [Sisteme Giriş](#sisteme-giriş)
- [Ana Dashboard](#ana-dashboard)
- [Kamera Yönetimi](#kamera-yönetimi)
- [İhlal Kayıtları](#ihlal-kayıtları)
- [Raporlama](#raporlama)
- [Uyarı Ayarları](#uyarı-ayarları)
- [Kullanıcı Ayarları](#kullanıcı-ayarları)
- [Sık Kullanılan İşlemler](#sık-kullanılan-i̇şlemler)
- [Sorun Giderme](#sorun-giderme)

---

## Giriş

KKD (Kişisel Koruyucu Donanım) Tespit Sistemi, şantiyenizdeki işçilerin güvenlik ekipmanlarını doğru şekilde kullanıp kullanmadığını otomatik olarak tespit eden bir yapay zeka destekli güvenlik sistemidir.

### Sistem Özellikleri

- ✅ Gerçek zamanlı baret ve yelek tespiti
- ✅ Çoklu kamera desteği
- ✅ Otomatik uyarı sistemi
- ✅ Detaylı raporlama
- ✅ İhlal kayıtları ve istatistikler

### Tespit Edilen KKD Ürünleri

| KKD Türü | Açıklama |
|----------|----------|
| **Baret** | Güvenlik baretleri / kasklar |
| **Yelek** | Yüksek görünürlüklü emniyet yelekleri |
| **Eldiven** | Güvenlik eldivenleri |
| **Bot** | Çelik burunlu güvenlik botları |
| **Gözlük** | Koruyucu gözlükler |
| **Maske** | Yüz maskeleri |

---

## Sisteme Giriş

### Web Arayüzü

1. **Tarayıcınızda Adresi Açın**
   ```
   http://santiye-ip-adresi:8000
   ```
   veya
   ```
   https://kkd.santiyeadi.com
   ```

2. **Giriş Yapın** (v0.2.0+)
   - Kullanıcı adınızı girin
   - Şifrenizi girin
   - "Giriş Yap" butonuna tıklayın

3. **Dashboard'a Yönlendirme**
   - Başarılı giriş sonrası ana panele yönlendirileceksiniz

### API Erişimi

Mobil uygulama veya harici sistemler için API erişimi:

```bash
# Sağlık kontrolü
curl http://santiye-ip:8000/health

# API dokümantasyonu
http://santiye-ip:8000/docs
```

---

## Ana Dashboard

### Dashboard Görünümü

```
┌─────────────────────────────────────────────────────────────────┐
│  KKD Tespit Sistemi - Ana Panel                    [Ayarlar] [▣] │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │
│  │ Aktif Kamera   │  │  Uyumluluk     │  │  Bugünkü       │    │
│  │                │  │   Oranı        │  │  İhlaller      │    │
│  │     4/5        │  │   98.7%        │  │     15         │    │
│  └────────────────┘  └────────────────┘  └────────────────┘    │
│                                                                   │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │
│  │ Bugünkü Tespit │  │ Tespit Edilen  │  │ İşlem Bekleyen │    │
│  │                │  │  Kişi Sayısı   │  │    İhlaller    │    │
│  │    1,250       │  │    3,500       │  │      8         │    │
│  └────────────────┘  └────────────────┘  └────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Kamera Durumu                                           │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ ✓ Ana Giriş Kamerası          Aktif   Son: 1 dk önce   │    │
│  │ ✓ Yükleme Alanı Kamerası      Aktif   Son: 2 dk önce   │    │
│  │ ⚠ İnşaat Alanı Kamerası       Uyarı   Son: 15 dk önce  │    │
│  │ ✓ Depo Kamerası               Aktif   Son: 1 dk önce   │    │
│  │ ✗ Otopark Kamerası            Çevrimdışı               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Son İhlaller                                 [Tümünü Gör]│    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ 12:45 | Ana Giriş   | Baret Yok      | [Görüntüle]     │    │
│  │ 12:38 | Yükleme     | Yelek Yok      | [Görüntüle]     │    │
│  │ 12:20 | İnşaat      | Baret & Yelek  | [Görüntüle]     │    │
│  │ 11:55 | Depo        | Baret Yok      | [Görüntüle]     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Dashboard Bileşenleri

#### 1. Özet Kartları

**Aktif Kamera**
- Çalışan kamera sayısı / Toplam kamera
- Yeşil: Tüm kameralar çalışıyor
- Sarı: Bazı kameralar çevrimdışı
- Kırmızı: Kritik kameralar çevrimdışı

**Uyumluluk Oranı**
- Genel KKD uyumluluk yüzdesi
- Yeşil: %95+
- Sarı: %90-95
- Kırmızı: <%90

**Bugünkü İhlaller**
- Günlük toplam ihlal sayısı
- Tıklanabilir - detaylara gider

#### 2. Kamera Durumu Listesi

Her kamera için:
- **Durum İkonu**:
  - ✓ (Yeşil): Normal çalışıyor
  - ⚠ (Sarı): Uyarı durumu
  - ✗ (Kırmızı): Çevrimdışı

- **Kamera Adı**: Tıklanabilir
- **Son Tespit**: Son tespitin ne kadar önce olduğu
- **Hızlı İşlemler**: Ayarlar, Canlı Görüntü

#### 3. Son İhlaller

- Kronolojik ihlal listesi
- Her ihlal için:
  - Zaman damgası
  - Kamera/Konum
  - İhlal türü
  - "Görüntüle" butonu (detaylara gider)

---

## Kamera Yönetimi

### Kamera Listesi

**Erişim**: Ana menü → Kameralar

```
┌─────────────────────────────────────────────────────────────────┐
│  Kameralar                            [+ Yeni Kamera Ekle]       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Arama: [__________________] 🔍   Filtre: [Tümü ▼]  [Yenile]    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ ID │ Ad              │ Konum      │ Durum  │ İşlemler  │    │
│  ├────┼─────────────────┼────────────┼────────┼───────────┤    │
│  │ 1  │ Ana Giriş       │ Giriş      │ ✓ Aktif│ [▶][⚙][✗]│    │
│  │ 2  │ Yükleme Alanı   │ Yükleme    │ ✓ Aktif│ [▶][⚙][✗]│    │
│  │ 3  │ İnşaat Alanı    │ 3. Kat     │ ⚠ Uyarı│ [▶][⚙][✗]│    │
│  │ 4  │ Depo            │ Depo       │ ✓ Aktif│ [▶][⚙][✗]│    │
│  │ 5  │ Otopark         │ Otopark    │ ✗ Kapalı│[▶][⚙][✗]│    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘

İkonlar:
[▶] Canlı Görüntü
[⚙] Ayarlar
[✗] Sil
```

### Yeni Kamera Ekleme

1. **"+ Yeni Kamera Ekle" Butonuna Tıklayın**

2. **Kamera Bilgilerini Girin**:

```
┌─────────────────────────────────────────────────────────────────┐
│  Yeni Kamera Ekle                                     [Kapat] [X]│
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Kamera Adı:                                                     │
│  [Ana Giriş Kamerası_________________________________]           │
│                                                                   │
│  RTSP URL:                                                       │
│  [rtsp://admin:sifre@192.168.1.100:554/stream________]          │
│                                                                   │
│  Konum:                                                          │
│  [Şantiye Ana Girişi_________________________________]           │
│                                                                   │
│  Bölge:                                                          │
│  [Bölge A ▼___________________________________________]          │
│                                                                   │
│  Tespit Aralığı (saniye):                                        │
│  [5_________] (1-60 arası)                                       │
│                                                                   │
│  Güven Eşiği:                                                    │
│  [0.7_______] (0.0-1.0 arası)                                    │
│                                                                   │
│  Zorunlu KKD:                                                    │
│  ☑ Baret     ☑ Yelek                                            │
│  ☐ Eldiven   ☐ Bot                                              │
│  ☐ Gözlük    ☐ Maske                                            │
│                                                                   │
│  Kamera Aktif:                                                   │
│  ◉ Evet  ○ Hayır                                                │
│                                                                   │
│  [URL'yi Test Et]              [İptal]  [Kaydet]                │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

**Alan Açıklamaları**:

- **Kamera Adı**: Tanımlayıcı bir isim (ör: "Ana Giriş Kamerası")
- **RTSP URL**: Kamera stream adresi
  - Format: `rtsp://kullanici:sifre@ip:port/yol`
  - Örnek: `rtsp://admin:password@192.168.1.100:554/stream1`
- **Konum**: Fiziksel konum tanımı
- **Bölge**: Şantiye bölgesi (opsiyonel)
- **Tespit Aralığı**: Kaç saniyede bir tespit yapılacak
- **Güven Eşiği**: Minimum tespit güveni (0.7 önerilir)
- **Zorunlu KKD**: Bu kamerada zorunlu olan ekipmanlar

3. **"URL'yi Test Et" ile Bağlantıyı Kontrol Edin**
   - Yeşil ✓: Bağlantı başarılı
   - Kırmızı ✗: Bağlantı başarısız (URL'yi kontrol edin)

4. **"Kaydet" Butonuna Tıklayın**

### Kamera Düzenleme

1. İlgili kameranın [⚙] ikonuna tıklayın
2. Ayarları değiştirin
3. "Güncelle" butonuna tıklayın

### Kamera Silme

1. İlgili kameranın [✗] ikonuna tıklayın
2. Onay penceresinde "Evet" seçin
3. Kamera ve ilgili kayıtlar silinir

**⚠️ Uyarı**: Kamera silindiğinde geçmiş kayıtlar korunur, ancak canlı izleme durur.

### Canlı Görüntü

1. İlgili kameranın [▶] ikonuna tıklayın
2. Canlı görüntü ve anlık tespit sonuçları açılır

```
┌─────────────────────────────────────────────────────────────────┐
│  Ana Giriş Kamerası - Canlı Görüntü              [Tam Ekran] [X]│
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐      │
│  │                                                        │      │
│  │          [Canlı Kamera Görüntüsü]                    │      │
│  │                                                        │      │
│  │    [Tespit edilen kişiler ve KKD gösterimi]          │      │
│  │                                                        │      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐      │
│  │ Anlık Tespit Bilgileri:                              │      │
│  │                                                        │      │
│  │ Tespit Edilen Kişi: 3                                 │      │
│  │ Uyumlu: 2                                             │      │
│  │ İhlal: 1                                              │      │
│  │                                                        │      │
│  │ Kişi 1: ✓ Baret ✓ Yelek (Uyumlu)                     │      │
│  │ Kişi 2: ✓ Baret ✓ Yelek (Uyumlu)                     │      │
│  │ Kişi 3: ✗ Baret ✓ Yelek (İhlal - Baret Yok)         │      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                   │
│  [Ekran Görüntüsü Al]  [Kaydı Durdur]  [Rapor Et]              │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## İhlal Kayıtları

### İhlal Listesi

**Erişim**: Ana menü → İhlaller

```
┌─────────────────────────────────────────────────────────────────┐
│  İhlal Kayıtları                                [Dışa Aktar]     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Filtreler:                                                      │
│  Tarih: [01.11.2024 ▼] - [30.11.2024 ▼]                        │
│  Kamera: [Tümü ▼]  İhlal Türü: [Tümü ▼]                        │
│  Durum: [Bekleyen ▼]  [Filtrele]  [Temizle]                    │
│                                                                   │
│  Sayfa: 1-20 / 145 kayıt                                        │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │Tarih/Saat │Kamera    │Konum   │İhlal      │Durum│İşlem │    │
│  ├───────────┼──────────┼────────┼───────────┼─────┼──────┤    │
│  │18.11 12:45│Ana Giriş │Giriş   │Baret Yok  │●Yeni│[Gör] │    │
│  │18.11 12:38│Yükleme   │Yükleme │Yelek Yok  │●Yeni│[Gör] │    │
│  │18.11 12:20│İnşaat    │3. Kat  │Baret+Yelek│●Yeni│[Gör] │    │
│  │18.11 11:55│Depo      │Depo    │Baret Yok  │○İşl.│[Gör] │    │
│  │18.11 11:40│Ana Giriş │Giriş   │Yelek Yok  │✓Onay│[Gör] │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  [◄ Önceki]  [1] [2] [3] ... [8]  [Sonraki ►]                  │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘

Durum İkonları:
● Yeni - Yeni tespit edildi, işlem bekleniyor
○ İşlemde - Çalışan uyarıldı, takip ediliyor
✓ Onaylandı - İhlal işlendi ve kapatıldı
```

### İhlal Detayları

[Gör] butonuna tıklandığında:

```
┌─────────────────────────────────────────────────────────────────┐
│  İhlal Detayları - #12345                             [Kapat] [X]│
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐      │
│  │  Genel Bilgiler                                       │      │
│  ├───────────────────────────────────────────────────────┤      │
│  │  İhlal ID: 12345                                      │      │
│  │  Tarih/Saat: 18.11.2024 12:45:32                     │      │
│  │  Kamera: Ana Giriş Kamerası                           │      │
│  │  Konum: Şantiye Ana Girişi                            │      │
│  │  Bölge: Bölge A                                       │      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐      │
│  │  İhlal Detayları                                      │      │
│  ├───────────────────────────────────────────────────────┤      │
│  │  İhlal Türü: Baret Yok                                │      │
│  │  Eksik KKD: Baret                                     │      │
│  │  Tespit Güveni: %95.3                                 │      │
│  │  Tespit Edilen Kişi Sayısı: 1                         │      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐      │
│  │                 [İhlal Görüntüsü]                     │      │
│  │                                                        │      │
│  │   [Tespit edilen kişi ve eksik KKD işaretli]         │      │
│  │                                                        │      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐      │
│  │  İşlem Bilgileri                                      │      │
│  ├───────────────────────────────────────────────────────┤      │
│  │  Durum: ● Bekleyen                                    │      │
│  │  Onaylayan: -                                         │      │
│  │  Onay Tarihi: -                                       │      │
│  │  Notlar: -                                            │      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐      │
│  │  İhlali Onayla                                        │      │
│  ├───────────────────────────────────────────────────────┤      │
│  │  Onaylayan:                                           │      │
│  │  [Adınız Soyadınız_________________________]          │      │
│  │                                                        │      │
│  │  Notlar:                                              │      │
│  │  ┌──────────────────────────────────────────────┐    │      │
│  │  │ Çalışan uyarıldı, baret verildi.            │    │      │
│  │  │                                              │    │      │
│  │  └──────────────────────────────────────────────┘    │      │
│  │                                                        │      │
│  │  [İptal]                            [İhlali Onayla]  │      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### İhlali Onaylama

1. İhlal detaylarını açın
2. "İhlali Onayla" bölümünü doldurun:
   - Adınızı soyadınızı girin
   - Yapılan işlemi notlar kısmına yazın
3. "İhlali Onayla" butonuna tıklayın

**Örnek Notlar**:
- "Çalışan uyarıldı, baret verildi"
- "İş güvenliği eğitimi planlandı"
- "Yüklenici firma bilgilendirildi"
- "Tekrarlı ihlal - disiplin işlemi başlatıldı"

---

## Raporlama

### İstatistik Paneli

**Erişim**: Ana menü → Raporlar → İstatistikler

```
┌─────────────────────────────────────────────────────────────────┐
│  İstatistikler                                     [Dışa Aktar]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Tarih Aralığı: [01.11.2024] - [30.11.2024]  [Uygula]           │
│                                                                   │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │
│  │ Toplam Tespit  │  │  Tespit Edilen │  │ Toplam İhlal   │    │
│  │                │  │     Kişi       │  │                │    │
│  │    37,500      │  │    105,000     │  │      450       │    │
│  └────────────────┘  └────────────────┘  └────────────────┘    │
│                                                                   │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │
│  │  Uyumluluk     │  │ Ort. İşleme    │  │ Aktif Kamera   │    │
│  │    Oranı       │  │    Süresi      │  │                │    │
│  │    99.2%       │  │    245 ms      │  │     4/5        │    │
│  └────────────────┘  └────────────────┘  └────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Saatlik İhlal Dağılımı                                  │    │
│  │                                                          │    │
│  │    │     ▄                                              │    │
│  │  15│   ▄▄█▄                     ▄▄                      │    │
│  │    │  ▄████▄                   ████                     │    │
│  │  10│  █████▄                   ████▄                    │    │
│  │    │ ▄█████▄                  ▄█████                    │    │
│  │   5│▄███████                  ██████                    │    │
│  │    │████████▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄███████▄▄▄▄▄             │    │
│  │   0└────────────────────────────────────────            │    │
│  │     0  2  4  6  8 10 12 14 16 18 20 22                 │    │
│  │                    Saat                                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ İhlal Türleri                                           │    │
│  │                                                          │    │
│  │ Baret Yok:        ████████████████░░░░  250 (%55.6)    │    │
│  │ Yelek Yok:        ██████████░░░░░░░░░░  150 (%33.3)    │    │
│  │ Baret & Yelek:    ███░░░░░░░░░░░░░░░░░   50 (%11.1)    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Kamera Bazında İstatistikler                           │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ Kamera          │ Tespit │ İhlal │ Uyumluluk │ Durum  │    │
│  ├─────────────────┼────────┼───────┼───────────┼────────┤    │
│  │ Ana Giriş       │ 12,500 │  180  │   98.6%   │ ✓ Aktif│    │
│  │ Yükleme Alanı   │  8,750 │  120  │   98.6%   │ ✓ Aktif│    │
│  │ İnşaat Alanı    │ 10,000 │  100  │   99.0%   │ ⚠ Uyarı│    │
│  │ Depo            │  6,250 │   50  │   99.2%   │ ✓ Aktif│    │
│  │ Otopark         │      - │    -  │      -    │ ✗ Kapalı│    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Rapor Oluşturma

**Erişim**: Ana menü → Raporlar → Rapor Oluştur

1. **Rapor Türünü Seçin**:
   - Günlük Rapor
   - Haftalık Rapor
   - Aylık Rapor
   - Özel Tarih Aralığı

2. **Rapor İçeriğini Belirleyin**:
   - ☑ Özet İstatistikler
   - ☑ Kamera Bazlı Detaylar
   - ☑ İhlal Kayıtları
   - ☑ Grafikler ve Çizelgeler
   - ☐ İhlal Görselleri

3. **Format Seçin**:
   - PDF (yazdırma için önerilir)
   - Excel (analiz için önerilir)
   - CSV (veri transferi için)

4. **"Rapor Oluştur" Butonuna Tıklayın**

5. **Raporu İndirin**

### Otomatik Raporlar

**Erişim**: Ayarlar → Otomatik Raporlar

- Günlük özet (her gün saat 18:00)
- Haftalık rapor (her Pazartesi saat 09:00)
- Aylık rapor (her ayın 1'i saat 09:00)

E-posta ile otomatik gönderim yapılandırılabilir.

---

## Uyarı Ayarları

### Bildirim Kanalları

**Erişim**: Ayarlar → Uyarılar

```
┌─────────────────────────────────────────────────────────────────┐
│  Uyarı Ayarları                                           [Kaydet]│
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐      │
│  │ Bildirim Kanalları                                    │      │
│  ├───────────────────────────────────────────────────────┤      │
│  │                                                        │      │
│  │ ☑ E-posta Bildirimleri                                │      │
│  │   E-posta: [guvenlik@sirket.com_____________]         │      │
│  │   Kopya: [yonetici@sirket.com______________]          │      │
│  │                                                        │      │
│  │ ☑ SMS Bildirimleri                                    │      │
│  │   Telefon: [+90 555 123 4567________________]         │      │
│  │                                                        │      │
│  │ ☑ Telegram                                            │      │
│  │   Bot Token: [1234567890:ABC****____________]         │      │
│  │   Chat ID: [-100123456789___________________]         │      │
│  │                                                        │      │
│  │ ☐ Webhook                                             │      │
│  │   URL: [https://api.sirket.com/kkd_________]          │      │
│  │                                                        │      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐      │
│  │ Uyarı Kuralları                                       │      │
│  ├───────────────────────────────────────────────────────┤      │
│  │                                                        │      │
│  │ Kritik İhlaller (Baret Yok):                          │      │
│  │   Öncelik: [Yüksek ▼]                                 │      │
│  │   Kanallar: ☑ E-posta  ☑ SMS  ☑ Telegram            │      │
│  │                                                        │      │
│  │ Orta Seviye İhlaller (Yelek Yok):                     │      │
│  │   Öncelik: [Orta ▼]                                   │      │
│  │   Kanallar: ☑ E-posta  ☐ SMS  ☑ Telegram            │      │
│  │                                                        │      │
│  │ Düşük Seviye İhlaller:                                │      │
│  │   Öncelik: [Düşük ▼]                                  │      │
│  │   Kanallar: ☑ E-posta  ☐ SMS  ☐ Telegram            │      │
│  │                                                        │      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                   │
│  ┌───────────────────────────────────────────────────────┐      │
│  │ Sıklık Ayarları                                       │      │
│  ├───────────────────────────────────────────────────────┤      │
│  │                                                        │      │
│  │ Bekleme Süresi: [5______] dakika                      │      │
│  │ (Aynı ihlal için tekrar bildirim gönderilmeden        │      │
│  │  önce beklenecek süre)                                │      │
│  │                                                        │      │
│  │ Saatlik Maksimum: [60_____] bildirim                  │      │
│  │ Günlük Maksimum: [500____] bildirim                   │      │
│  │                                                        │      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                   │
│  [Test Bildirimi Gönder]              [İptal]  [Kaydet]         │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### E-posta Şablonu

Örnek e-posta bildirimi:

```
Konu: [KKD İhlali] Ana Giriş Kamerası - Baret Yok

KKD İhlali Tespit Edildi

─────────────────────────────────────
İHLAL BİLGİLERİ
─────────────────────────────────────

İhlal ID: 12345
Tarih/Saat: 18.11.2024 12:45:32
Kamera: Ana Giriş Kamerası
Konum: Şantiye Ana Girişi
Bölge: Bölge A

İhlal Türü: Baret Yok
Eksik KKD: Baret
Güven: %95.3

─────────────────────────────────────
YAPILMASI GEREKENLER
─────────────────────────────────────

1. Çalışanı derhal uyarın
2. Gerekli KKD'yi sağlayın
3. Sisteme ihlali onaylayın
4. Tekrar ederse disiplin işlemi başlatın

─────────────────────────────────────

İhlali görüntülemek için:
https://kkd.santiye.com/violations/12345

─────────────────────────────────────
Bu otomatik bir bildirimdir.
KKD Tespit Sistemi v0.1.0
```

---

## Kullanıcı Ayarları

### Profil Ayarları

**Erişim**: Sağ üst köşe → Kullanıcı İkonu → Ayarlar

- Kullanıcı adı
- E-posta adresi
- Telefon numarası
- Şifre değiştir
- Dil tercihi (Türkçe/İngilizce)

### Bildirim Tercihleri

- E-posta bildirimleri
- Tarayıcı bildirimleri
- Mobil bildirimler

---

## Sık Kullanılan İşlemler

### 1. Günlük Rutin Kontrol

**Sabah (09:00)**:
1. Dashboard'u açın
2. Tüm kameraların aktif olduğunu kontrol edin
3. Gece tespit edilen ihlalleri inceleyin
4. Bekleyen ihlalleri onaylayın

**Öğle (13:00)**:
1. Öğle arası ihlallerini kontrol edin
2. Kritik ihlaller için anında müdahale

**Akşam (18:00)**:
1. Günlük özet raporu inceleyin
2. Tüm ihlallerin işlendiğinden emin olun
3. Yarın için uyarı ayarlarını kontrol edin

### 2. Haftalık Kontrol

**Her Pazartesi**:
1. Haftalık rapor oluşturun
2. Trend analizi yapın
3. Tekrarlı ihlal yapan bölgeleri belirleyin
4. İyileştirme aksiyonları planlayın

### 3. Aylık Değerlendirme

**Her Ayın İlk Haftası**:
1. Aylık rapor oluşturun
2. Uyumluluk oranı trendini inceleyin
3. Yönetim raporlaması hazırlayın
4. Hedefler belirleyin

---

## Sorun Giderme

### Kamera Bağlantı Sorunları

**Problem**: Kamera "Çevrimdışı" görünüyor

**Çözümler**:
1. Kameranın elektrik bağlantısını kontrol edin
2. Ağ kablosunu kontrol edin
3. RTSP URL'sini doğrulayın
4. Kamera kullanıcı adı/şifresi doğru mu?
5. Kamerayı yeniden başlatın
6. Sistem yöneticinize başvurun

### Yanlış Tespit

**Problem**: Sistem baret var olmasına rağmen "Baret Yok" uyarısı veriyor

**Çözümler**:
1. Kamera açısını kontrol edin (yukarıdan çekim idealdir)
2. Aydınlatma yeterli mi?
3. Kamera lens temiz mi?
4. Güven eşiğini düşürmeyi deneyin (0.7 → 0.6)
5. Sistem yöneticinize başvurun

### Sistem Yavaş

**Problem**: Tespit sonuçları geç geliyor

**Çözümler**:
1. Aktif kamera sayısını azaltın
2. Tespit aralığını artırın (5 → 10 saniye)
3. Sunucu kaynaklarını kontrol edin
4. Sistem yöneticinize başvurun

### Uyarı Almıyorum

**Problem**: İhlaller tespit ediliyor ama e-posta/SMS gelmiyor

**Çözümler**:
1. Uyarı ayarlarını kontrol edin
2. E-posta/telefon numarası doğru mu?
3. Spam klasörünü kontrol edin
4. Test bildirimi gönderin
5. Sistem yöneticinize başvurun

---

## Destek ve İletişim

### Teknik Destek

- 📞 Telefon: +90 XXX XXX XX XX
- 📧 E-posta: destek@kkd-sistem.com
- 💬 Canlı Destek: https://kkd.santiye.com/destek

### Eğitim Talepleri

Sistem kullanımı konusunda eğitim için:
- egitim@kkd-sistem.com

### Özellik Talepleri

Yeni özellik önerileri için:
- oneriler@kkd-sistem.com

---

**KKD Tespit Sistemi v0.1.0**
**Şantiye güvenliği için geliştirilmiştir**
