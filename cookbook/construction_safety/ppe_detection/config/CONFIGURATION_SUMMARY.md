# PPE Detection - Configuration Management Summary

## 📋 Oluşturulan Dosyalar

### Ana Yapılandırma Dosyaları

#### 1. **settings.py** (21 KB)
Ana yapılandırma sınıfları - Pydantic Settings kullanılarak oluşturulmuştur.

**İçerik:**
- `DatabaseConfig` - Veritabanı yapılandırması (PostgreSQL/SQLite)
- `CameraConfig` - Kamera yapılandırması (RTSP stream)
- `CamerasConfig` - Çoklu kamera yönetimi
- `ModelConfig` - YOLOv8/YOLOv11 model ayarları
- `AlertConfig` - Bildirim ve uyarı sistemi
- `APIConfig` - Harici API entegrasyonları (SMTP, Twilio, S3)
- `MonitoringConfig` - Logging, metrics, health checks
- `Settings` - Ana yapılandırma sınıfı (tüm config'leri birleştirir)

**Özellikler:**
- Type validation (Pydantic)
- Environment variable desteği
- Default değerler
- Nested configuration
- Secret management (SecretStr)
- Helper metodlar (is_production, get_db_connection_string, vb.)

**Kullanım:**
```python
from config import get_settings

settings = get_settings()
print(settings.database.get_connection_string())
print(settings.model.model_path)
```

---

#### 2. **config_loader.py** (16 KB)
Çoklu kaynaktan yapılandırma yükleme sistemi.

**Özellikler:**
- Öncelik yönetimi: CLI args > Env vars > Config files > Defaults
- YAML config dosyası desteği
- .env dosyası desteği
- Ortam-specific yapılandırma (dev/staging/prod)
- Deep merge algoritması
- CLI argument parser

**Sınıflar:**
- `ConfigLoader` - Ana loader sınıfı
- `CLIConfigLoader` - CLI argüman yönetimi

**Kullanım:**
```python
from config import load_config_from_cli

# CLI argümanlarından yükle
settings = load_config_from_cli()

# Veya manuel
loader = ConfigLoader()
settings = loader.load(
    env_file=".env",
    config_file="config/environments/production.yaml",
    environment="production"
)
```

**CLI Kullanımı:**
```bash
python -m src.main --env production --config custom.yaml --debug
python -m src.main --model-path models/custom.pt --confidence 0.6
```

---

#### 3. **config_validator.py** (19 KB)
Yapılandırma doğrulama ve güvenlik kontrolleri.

**Doğrulanan Şeyler:**
- ✅ Environment ayarları (production'da debug kapalı mı?)
- ✅ Dizin yapısı ve izinler
- ✅ Database bağlantısı
- ✅ Model dosyası varlığı
- ✅ RTSP URL formatları
- ✅ Alert alıcıları
- ✅ API anahtarları
- ✅ Port çakışmaları
- ✅ Güvenlik ayarları (varsayılan şifreler, file permissions)
- ✅ Network bağlantıları

**Kullanım:**
```python
from config import validate_config

settings = get_settings()
is_valid = validate_config(settings, strict=False)

# Veya direkt script olarak
python -m config.config_validator
```

---

### Ortam Yapılandırmaları

#### 4. **environments/development.yaml** (3.5 KB)
Geliştirme ortamı için optimize edilmiş yapılandırma.

**Özellikler:**
- SQLite database (kolay kurulum)
- Düşük FPS (5) ve çözünürlük (1280x720)
- Debug logging aktif
- Alert sistemleri kapalı
- Test videoları
- CPU device

---

#### 5. **environments/staging.yaml** (4.2 KB)
Test ortamı - Production'a en yakın ayarlar.

**Özellikler:**
- PostgreSQL database
- Production benzeri ayarlar
- Tüm alert kanalları test edilir
- S3 snapshot storage
- GPU device (CUDA)
- Test kameraları

---

#### 6. **environments/production.yaml** (6.8 KB)
Canlı ortam - Güvenlik ve performans optimize edilmiş.

**Özellikler:**
- PostgreSQL HA cluster
- Yüksek çözünürlük (1920x1080)
- Tüm alert kanalları aktif
- SSL/TLS zorunlu
- IP whitelisting
- Backup & recovery
- Audit logging
- GDPR/KVKK compliance
- On-call rotation
- Maintenance windows

---

### Yardımcı Dosyalar

#### 7. **.env.example** (7 KB)
Tüm environment variable'ları içeren örnek dosya.

**Bölümler:**
- Genel ayarlar
- Database ayarları
- Kamera ayarları
- Model ayarları
- Alert ayarları
- API ayarları (SMTP, Twilio, S3)
- Monitoring ayarları
- Feature flags
- İş mantığı ayarları

**Kullanım:**
```bash
cp .env.example .env
nano .env  # Değerleri düzenle
```

---

#### 8. **cameras.yaml.example** (7.2 KB)
Kamera yapılandırması için şablon.

**İçerik:**
- 6 örnek kamera yapılandırması
- Test kameraları (video dosyası, webcam)
- RTSP URL format örnekleri
- Çözünürlük ve FPS önerileri
- Güvenlik notları
- Network gereksinimleri

**Kullanım:**
```bash
cp config/cameras.yaml.example config/cameras.yaml
nano config/cameras.yaml  # Gerçek kamera bilgilerini gir
```

---

### Test ve Dokümantasyon

#### 9. **config_test.py** (9.8 KB)
Kapsamlı yapılandırma test suite'i.

**Testler:**
1. Basic Loading - Temel yapılandırma yükleme
2. Validation - Doğrulama sistemi
3. Config Loader - Çoklu kaynak yükleme
4. Database Config - Veritabanı ayarları
5. Model Config - Model ayarları
6. Camera Config - Kamera ayarları
7. Alert Config - Bildirim ayarları
8. Monitoring Config - İzleme ayarları
9. Feature Flags - Özellik bayrakları
10. Environment Specific - Ortam-specific ayarlar
11. Config Export - Yapılandırma export

**Kullanım:**
```bash
python -m config.config_test
```

---

#### 10. **generate_schema.py** (6.4 KB)
JSON Schema ve template oluşturucu.

**Oluşturduğu Dosyalar:**
- `config_schema.json` - JSON Schema (API validation için)
- `CONFIG_SCHEMA.md` - Markdown dokümantasyon
- `template.env` - .env template
- `template.yaml` - YAML template

**Kullanım:**
```bash
python -m config.generate_schema
```

Çıktı: `config/generated/` dizini

---

#### 11. **README.md** (13 KB)
Kapsamlı yapılandırma dokümantasyonu.

**İçerik:**
- Hızlı başlangıç
- Yapılandırma bölümleri
- Öncelik sistemi
- Ortam yapılandırmaları
- Güvenlik en iyi pratikleri
- Doğrulama
- Hot reload
- Environment variables
- CLI argümanları
- Sorun giderme
- İleri seviye kullanım
- SSS

---

#### 12. **__init__.py** (2 KB)
Config package initialization.

**Export edilen modüller:**
- Settings sınıfları
- Validator fonksiyonları
- Loader fonksiyonları
- Helper fonksiyonlar

---

## 🚀 Hızlı Başlangıç Kılavuzu

### 1. Development Ortamında Çalıştırma

```bash
# 1. .env dosyası oluştur
cp .env.example .env

# 2. Development için ayarları yapılandır
# .env dosyasında ENVIRONMENT=development olduğundan emin ol

# 3. (Opsiyonel) Kamera yapılandırması
cp config/cameras.yaml.example config/cameras.yaml

# 4. Yapılandırmayı doğrula
python -m config.config_validator

# 5. Test et
python -m config.config_test

# 6. Uygulamayı çalıştır
python -m src.main --env development
```

### 2. Staging Ortamında Test

```bash
# 1. .env dosyasını staging için düzenle
# DATABASE__PASSWORD, SMTP credentials vb. ekle

# 2. Staging yapılandırması ile çalıştır
python -m src.main --env staging

# 3. Veya custom config ile
python -m src.main \
  --env staging \
  --config config/environments/staging.yaml
```

### 3. Production Deployment

```bash
# 1. Environment variables ayarla (docker-compose, k8s secrets, vb.)
export ENVIRONMENT=production
export DATABASE__PASSWORD="secure_password"
export SMTP_PASSWORD="smtp_password"
export TWILIO_AUTH_TOKEN="token"

# 2. Config doğrulaması (strict mode)
python -m config.config_validator --strict

# 3. Uygulamayı başlat
python -m src.main --env production

# 4. Health check
curl http://localhost:8080/health

# 5. Metrics
curl http://localhost:9090/metrics
```

---

## 📊 Yapılandırma Öncelik Sırası

```
┌─────────────────────────────────────┐
│  1. CLI Arguments (En Yüksek)      │ --model-path models/custom.pt
├─────────────────────────────────────┤
│  2. Environment Variables           │ export MODEL__CONFIDENCE=0.6
├─────────────────────────────────────┤
│  3. .env Dosyası                    │ MODEL__CONFIDENCE=0.6
├─────────────────────────────────────┤
│  4. YAML Config Dosyaları           │ model.confidence: 0.6
├─────────────────────────────────────┤
│  5. Default Değerler (En Düşük)     │ Field(default=0.5)
└─────────────────────────────────────┘
```

---

## 🔐 Güvenlik Kontrol Listesi

### Development
- [ ] `.env` dosyası oluşturuldu
- [ ] Kamera credentials test edildi
- [ ] Model dosyası indirildi
- [ ] Database bağlantısı test edildi

### Staging
- [ ] Tüm environment variables ayarlandı
- [ ] Alert sistemleri test edildi
- [ ] S3 storage yapılandırıldı
- [ ] SSL certificates yüklendi
- [ ] Load testing yapıldı

### Production
- [ ] `DEBUG=False` olduğu doğrulandı
- [ ] Güçlü database şifresi kullanıldı
- [ ] Tüm API keys güvenli şekilde saklandı
- [ ] `.env` dosyası git'e commit edilmedi
- [ ] File permissions kontrol edildi (chmod 600)
- [ ] SSL/TLS aktif
- [ ] Firewall kuralları yapılandırıldı
- [ ] IP whitelist tanımlandı
- [ ] Backup sistemi çalışıyor
- [ ] Monitoring ve alerting aktif
- [ ] Log rotation yapılandırıldı
- [ ] Audit logging aktif
- [ ] Rollback planı hazır

---

## 🛠️ Özelleştirme Örnekleri

### Custom Model Kullanma

```bash
# CLI ile
python -m src.main --model-path models/custom_yolov11x.pt --confidence 0.7

# Environment variable ile
export MODEL__MODEL_PATH=models/custom_yolov11x.pt
export MODEL__CONFIDENCE_THRESHOLD=0.7
python -m src.main
```

### Custom Database

```bash
# PostgreSQL
export DATABASE__TYPE=postgresql
export DATABASE__HOST=db.company.com
export DATABASE__PORT=5432
export DATABASE__USERNAME=ppe_user
export DATABASE__PASSWORD=secure_password
export DATABASE__DATABASE=ppe_production

# SQLite
export DATABASE__TYPE=sqlite
export DATABASE__SQLITE_PATH=/data/ppe_detection.db
```

### Alert Yapılandırması

```bash
# Email
export ALERTS__ENABLE_EMAIL=true
export ALERTS__EMAIL_RECIPIENTS='["safety@company.com","supervisor@company.com"]'

# SMS
export ALERTS__ENABLE_SMS=true
export ALERTS__SMS_RECIPIENTS='["+905551234567"]'

# Webhook
export ALERTS__ENABLE_WEBHOOK=true
export ALERTS__WEBHOOK_URLS='["https://hooks.slack.com/services/YOUR/WEBHOOK"]'
```

---

## 📈 Performans İpuçları

### GPU Kullanımı
```bash
export MODEL__DEVICE=cuda
export MODEL__DEVICE_ID=0
export MODEL__HALF_PRECISION=true
```

### Kamera Optimizasyonu
```yaml
cameras:
  frame_skip: 2  # Her 2 frame'de bir işle
  default_fps: 5  # Düşük FPS
  default_resolution: [1280, 720]  # Düşük çözünürlük
```

### Batch Processing
```bash
export MODEL__BATCH_SIZE=4  # Batch size artır (GPU için)
```

---

## 🔄 Hot Reload

Bazı ayarlar runtime'da değiştirilebilir:

```python
from config import reload_settings

# Yapılandırmayı yeniden yükle
settings = reload_settings()
```

**Hot Reload Destekleyen:**
- Log level
- Alert thresholds
- Feature flags
- Camera enable/disable

**Restart Gerektiren:**
- Database connection
- Model path
- Device (CPU/GPU)
- Port ayarları

---

## 📞 Yardım ve Destek

### Sorun Giderme

1. **Config yüklenmiyor:**
   ```bash
   python -m config.config_validator
   ```

2. **Environment variables çalışmıyor:**
   ```bash
   env | grep -E "(DATABASE|MODEL|CAMERA)"
   ```

3. **Database bağlantı hatası:**
   ```bash
   python -c "from config import get_settings; print(get_settings().get_db_connection_string())"
   ```

4. **Model bulunamıyor:**
   ```bash
   ls -lh models/
   ```

### Loglar

```bash
# Config validation log
tail -f logs/config_validation.log

# Application log
tail -f logs/ppe_detection.log
```

---

## 📚 Ek Kaynaklar

- **Pydantic Settings:** https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- **12 Factor App:** https://12factor.net/config
- **OWASP Config:** https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/

---

## ✅ Özet

**Oluşturulan Toplam Dosya:** 12
- **Python Modülleri:** 5 (settings.py, config_loader.py, config_validator.py, config_test.py, generate_schema.py)
- **Ortam Configs:** 3 (development.yaml, staging.yaml, production.yaml)
- **Template/Example:** 2 (.env.example, cameras.yaml.example)
- **Dokümantasyon:** 2 (README.md, bu dosya)

**Toplam Kod:** ~100 KB
**Satır Sayısı:** ~2500+ satır (yorumlar dahil)

**Temel Özellikler:**
✅ Pydantic Settings ile type-safe configuration
✅ Çoklu kaynak desteği (CLI, env vars, YAML, defaults)
✅ Öncelik yönetimi
✅ Kapsamlı doğrulama
✅ Güvenlik kontrolleri
✅ Ortam-specific configs
✅ Hot reload desteği
✅ Secret management
✅ Comprehensive testing
✅ JSON Schema generation
✅ Full documentation

**Kullanıma Hazır!** 🚀
