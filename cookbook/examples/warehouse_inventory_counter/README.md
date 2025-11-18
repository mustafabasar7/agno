# 📦 Otomatik Depo Envanter Sayımı (Warehouse Inventory Counter)

Elle sayım yerine otomatik envanter! Depo raf fotoğraflarından ürün tespiti ve sayımı yapın.

## 🎯 Özellikler

- **🤖 Otomatik Ürün Tespiti**: YOLOv8 ile güçlendirilmiş nesne algılama
- **🔢 Akıllı Sayım**: Raflardaki ürünleri otomatik olarak sayar
- **📝 OCR Entegrasyonu**: Ürün etiketlerini ve kodlarını okur
- **📊 Detaylı Raporlama**: CSV formatında envanter raporları
- **🎨 Görsel Arayüz**: Kullanımı kolay Streamlit web arayüzü
- **🌍 Çoklu Dil Desteği**: Türkçe ve İngilizce OCR desteği

## 🎬 Kullanım Alanları

- **E-ticaret Depoları**: Hızlı envanter sayımı ve stok takibi
- **Perakende Mağazalar**: Raf içerik analizi ve ürün yerleşimi
- **Lojistik Merkezleri**: Gelen/giden ürün kontrolü
- **Depo Yönetimi**: Düzenli stok kontrolü ve raporlama

## 🚀 Kurulum

### 1. Gereksinimleri Yükleyin

```bash
pip install -r requirements.txt
```

### 2. Uygulamayı Başlatın

```bash
streamlit run app.py
```

Uygulama tarayıcınızda otomatik olarak açılacaktır (genellikle http://localhost:8501).

## 📖 Nasıl Kullanılır

### Adım 1: Fotoğraf Yükleme
- Ana ekrandan "Browse files" butonuna tıklayın
- Depo rafınızın fotoğrafını seçin
- JPG, JPEG veya PNG formatı desteklenir

### Adım 2: Ayarları Yapılandırma
Sol taraftaki ayarlar panelinden:
- **Güven Eşiği**: Tespit hassasiyetini ayarlayın (varsayılan: 0.4)
- **OCR**: Ürün etiketlerini okumak için açın/kapatın
- **Etiketleri Göster**: Tespit sonuçlarını görselde gösterin

### Adım 3: Tespit ve Sayım
- "Tespit Et ve Say" butonuna tıklayın
- Sistem ürünleri otomatik olarak tespit edecek ve sayacak
- Sonuçlar ekranda görüntülenecek

### Adım 4: Sonuçları İndirme
- **CSV Raporu**: Detaylı envanter listesi
- **İşaretli Görsel**: Tespit edilen ürünlerin işaretli fotoğrafı

## 🛠️ Teknik Detaylar

### Kullanılan Teknolojiler

#### YOLOv8 (Object Detection)
- En son nesne algılama modeli
- Hızlı ve doğru tespit
- 80 farklı nesne sınıfı (COCO dataset)
- Özelleştirilebilir güven eşiği

#### EasyOCR
- Çoklu dil desteği (Türkçe, İngilizce)
- Ürün etiketleri ve kodlarını okuma
- Yüksek doğruluk oranı

#### Streamlit
- Modern web arayüzü
- Kolay kullanım
- Etkileşimli görselleştirme

### Mimari

```
warehouse_inventory_counter/
├── app.py              # Streamlit web uygulaması
├── detector.py         # YOLOv8 tespit motoru
├── ocr_reader.py       # OCR okuma modülü
├── requirements.txt    # Python bağımlılıkları
└── README.md          # Dokümantasyon
```

## 💡 İpuçları

### En İyi Sonuçlar İçin:

1. **Fotoğraf Kalitesi**
   - İyi aydınlatılmış ortamda çekim yapın
   - Net ve odaklanmış fotoğraflar kullanın
   - Mümkünse yüksek çözünürlüklü kamera kullanın

2. **Çekim Açısı**
   - Rafa doğrudan bakacak şekilde çekin
   - Çok eğik açılardan kaçının
   - Ürünlerin net görünmesini sağlayın

3. **Ayarlar**
   - Karmaşık raflarda güven eşiğini düşürün
   - Basit raflarda yüksek tutun
   - Farklı değerlerle deneme yapın

4. **OCR Kullanımı**
   - Etiketli ürünler için OCR'ı aktif edin
   - Etiket olmayan ürünler için kapatın
   - OCR sonuçlarını CSV'de kontrol edin

## 🎓 Örnek Kullanım Senaryoları

### Senaryo 1: Günlük Envanter Kontrolü
```python
# Sabah ve akşam raf fotoğrafları çekin
# Farkları karşılaştırın
# Eksik ürünleri tespit edin
```

### Senaryo 2: Stok Devir Analizi
```python
# Belirli aralıklarla fotoğraf çekin
# Ürün hareketlerini takip edin
# Popüler ürünleri belirleyin
```

### Senaryo 3: Raf Düzeni Optimizasyonu
```python
# Mevcut düzeni analiz edin
# Ürün yerleşimini optimize edin
# Yeni düzeni test edin
```

## 🔧 Gelişmiş Kullanım

### Python API Kullanımı

```python
from detector import WarehouseDetector
from ocr_reader import OCRReader

# Tespit sistemi
detector = WarehouseDetector(confidence_threshold=0.4)
detections, annotated_img = detector.detect("shelf_photo.jpg")

# Ürün sayımı
counts = detector.count_products(detections)
print(f"Toplam ürün: {len(detections)}")
print(f"Kategoriler: {counts}")

# OCR okuma
ocr = OCRReader(languages=['tr', 'en'])
detections_with_text = ocr.read_labels("shelf_photo.jpg", detections)

for det in detections_with_text:
    print(f"{det['class']}: {det.get('ocr_text', 'N/A')}")
```

### Toplu İşlem

```python
import os
from pathlib import Path

# Klasördeki tüm fotoğrafları işle
photos_dir = "warehouse_photos"
for photo in Path(photos_dir).glob("*.jpg"):
    detections, _ = detector.detect(str(photo))
    print(f"{photo.name}: {len(detections)} ürün tespit edildi")
```

## 🐛 Sorun Giderme

### YOLOv8 Modeli İndirilemiyor
```bash
# Manuel indirme
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

### OCR Hatası Alıyorum
```bash
# EasyOCR'ı yeniden yükleyin
pip uninstall easyocr
pip install easyocr
```

### Streamlit Çalışmıyor
```bash
# Streamlit'i güncelleyin
pip install --upgrade streamlit
```

### GPU Kullanmak İstiyorum
```python
# detector.py dosyasında:
self.model = YOLO(model_name)  # Otomatik GPU kullanır

# ocr_reader.py dosyasında:
self.reader = easyocr.Reader(languages, gpu=True)  # GPU'yu aktif et
```

## 📊 Performans

- **Tespit Hızı**: ~100-200ms/fotoğraf (CPU)
- **OCR Hızı**: ~500-1000ms/fotoğraf
- **Desteklenen Görüntü Boyutu**: 640x640 - 4096x4096
- **Bellek Kullanımı**: ~2-4GB (model + OCR)

## 🔮 Gelecek Geliştirmeler

- [ ] Özel model eğitimi (kendi ürünleriniz için)
- [ ] Barkod okuma entegrasyonu
- [ ] Video akışı desteği (gerçek zamanlı sayım)
- [ ] Mobil uygulama
- [ ] Otomatik rapor gönderimi (e-posta/Slack)
- [ ] Çoklu raf karşılaştırma
- [ ] Tarihsel trend analizi
- [ ] REST API servisi

## 📄 Lisans

Bu proje Agno framework'ü altında geliştirilmiştir.

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen bir issue açın veya pull request gönderin.

## 📞 Destek

Sorularınız için:
- GitHub Issues
- Agno Community: https://community.agno.com
- Discord: https://discord.gg/4MtYHHrgA8

---

**E-ticaret depoları ve perakende için otomatik envanter çözümü** 🚀
