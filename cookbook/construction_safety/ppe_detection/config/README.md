# PPE Detection System - Configuration Management

Bu dizin PPE Detection sisteminin yapılandırma yönetimi dosyalarını içerir.

## 📁 Dizin Yapısı

```
config/
├── __init__.py                 # Config package initialization
├── settings.py                 # Ana yapılandırma sınıfları (Pydantic Settings)
├── config_loader.py            # Çoklu kaynaktan yapılandırma yükleme
├── config_validator.py         # Yapılandırma doğrulama ve güvenlik kontrolleri
├── .env.example                # Örnek environment variables
├── cameras.yaml.example        # Örnek kamera yapılandırması
├── README.md                   # Bu dosya
└── environments/               # Ortam-specific yapılandırmalar
    ├── development.yaml        # Geliştirme ortamı
    ├── staging.yaml            # Test ortamı
    └── production.yaml         # Canlı ortam
```

## 🚀 Hızlı Başlangıç

### 1. Environment Dosyası Oluşturma

```bash
# .env.example dosyasını kopyala
cp config/.env.example .env

# Değerleri düzenle
nano .env
```

### 2. Kamera Yapılandırması

```bash
# Kamera config örneğini kopyala
cp config/cameras.yaml.example config/cameras.yaml

# Kamera bilgilerini gir
nano config/cameras.yaml
```

### 3. Python'dan Kullanım

```python
from config import get_settings, validate_config

# Yapılandırmayı yükle
settings = get_settings()

# Doğrulama yap
validate_config(settings)

# Kullan
print(f"Database: {settings.get_db_connection_string()}")
print(f"Model: {settings.model.model_path}")
print(f"Cameras: {len(settings.cameras.cameras)}")
```

### 4. CLI'dan Yapılandırma

```bash
# Development ortamında çalıştır
python -m src.main --env development

# Production ortamında custom config ile
python -m src.main --env production --config config/my_config.yaml

# Debug modu
python -m src.main --debug

# Sadece doğrulama yap
python -m config.config_validator
```

## 📋 Yapılandırma Bölümleri

### DatabaseConfig
Veritabanı bağlantı ayarları (PostgreSQL/SQLite)

```python
database:
  type: "postgresql"
  host: "localhost"
  port: 5432
  username: "ppe_user"
  password: "secure_password"
  database: "ppe_detection"
  pool_size: 10
```

### CameraConfig
RTSP kamera stream ayarları

```python
cameras:
  cameras:
    - camera_id: "cam_01"
      name: "Main Entrance"
      rtsp_url: "rtsp://admin:pass@192.168.1.100:554/stream1"
      location: "Main Gate"
      zone: "Zone A"
      fps: 10
      resolution: [1920, 1080]
```

### ModelConfig
YOLOv8/YOLOv11 model ayarları

```python
model:
  model_path: "models/ppe_detection.pt"
  model_type: "yolov11"
  model_size: "m"
  confidence_threshold: 0.5
  device: "cuda"
  required_ppe: ["hardhat", "safety_vest"]
```

### AlertConfig
Bildirim ve uyarı ayarları

```python
alerts:
  enable_alerts: true
  enable_email: true
  enable_sms: false
  enable_webhook: true
  email_recipients: ["safety@company.com"]
  min_alert_interval: 60
```

### APIConfig
Harici servis entegrasyonları

```python
api:
  smtp_host: "smtp.gmail.com"
  smtp_port: 587
  twilio_account_sid: "ACxxxxxx"
  s3_enabled: true
  s3_bucket: "ppe-snapshots"
```

### MonitoringConfig
Sistem izleme ve metrikler

```python
monitoring:
  log_level: "INFO"
  log_file: "logs/ppe_detection.log"
  enable_metrics: true
  metrics_port: 9090
  save_violation_snapshots: true
```

## 🔧 Yapılandırma Yükleme Önceliği

Sistem yapılandırmayı şu sırayla yükler (yüksek öncelikten düşüğe):

1. **CLI Argümanları** - En yüksek öncelik
   ```bash
   python main.py --model-path models/custom.pt --confidence 0.6
   ```

2. **Environment Variables**
   ```bash
   export MODEL__CONFIDENCE_THRESHOLD=0.6
   python main.py
   ```

3. **Config Dosyaları** (.env)
   ```bash
   # .env dosyası
   MODEL__CONFIDENCE_THRESHOLD=0.6
   ```

4. **YAML Config Dosyaları**
   ```yaml
   # environments/development.yaml
   model:
     confidence_threshold: 0.6
   ```

5. **Varsayılan Değerler** - En düşük öncelik
   ```python
   # settings.py içinde tanımlı
   confidence_threshold: float = Field(default=0.5)
   ```

## 🌍 Ortam Yapılandırmaları

### Development (Geliştirme)
- SQLite database
- Düşük FPS ve çözünürlük
- Debug logging
- Alert sistemleri kapalı
- Test videoları

```bash
python -m src.main --env development
```

### Staging (Test)
- PostgreSQL database
- Production benzeri ayarlar
- Tüm alert kanalları test edilir
- S3 snapshot storage
- Test kameraları

```bash
python -m src.main --env staging
```

### Production (Canlı)
- PostgreSQL HA cluster
- Optimize edilmiş ayarlar
- Tüm alert kanalları aktif
- Güvenlik sıkılaştırmaları
- Gerçek kameralar

```bash
python -m src.main --env production
```

## 🔐 Güvenlik En İyi Pratikleri

### 1. Hassas Bilgileri Koruma

```bash
# ❌ YANLIŞ - Config dosyasında hardcode
database:
  password: "MyPassword123"

# ✅ DOĞRU - Environment variable
database:
  password: ${DATABASE_PASSWORD}
```

### 2. .env Dosyası Güvenliği

```bash
# .env dosyasını git'e commit etme
echo ".env" >> .gitignore

# Dosya izinlerini kısıtla
chmod 600 .env

# Root yetkisiyle çalıştırma
chown user:user .env
```

### 3. Production Güvenlik Kontrol Listesi

- [ ] DEBUG=False
- [ ] Güçlü database şifresi
- [ ] SSL/TLS aktif
- [ ] Firewall kuralları
- [ ] IP whitelist
- [ ] API key rotasyonu
- [ ] Log maskinge (şifre gizleme)
- [ ] Backup encryption

## 🧪 Yapılandırma Doğrulama

### Otomatik Doğrulama

```bash
# Yapılandırmayı doğrula
python -m config.config_validator

# Strict mod (uyarıları da hata say)
python -m config.config_validator --strict
```

### Programatik Doğrulama

```python
from config import validate_config, get_settings

settings = get_settings()

# Doğrulama yap
is_valid, errors, warnings = validate_config(
    settings,
    strict=False,
    exit_on_error=False
)

if not is_valid:
    print("Hatalar:", errors)
```

### Kontrol Edilen Şeyler

- ✅ Gerekli dosyaların varlığı
- ✅ Dizin yapısı ve izinler
- ✅ Database bağlantısı
- ✅ Model dosyası
- ✅ RTSP URL formatları
- ✅ Port çakışmaları
- ✅ Güvenlik ayarları
- ✅ Production hazırlığı

## 🔄 Hot Reload

Bazı ayarlar uygulama yeniden başlatılmadan güncellenebilir:

```python
from config import reload_settings

# Yapılandırmayı yeniden yükle
settings = reload_settings()
```

**Hot Reload Destekleyen Ayarlar:**
- Log level
- Alert thresholds
- Feature flags
- Camera enable/disable
- FPS ve resolution

**Restart Gerektiren Ayarlar:**
- Database connection
- Model path
- Device (CPU/GPU)
- Port ayarları

## 📊 Environment Variables

### Nested Configuration

Pydantic Settings nested delimiter kullanır:

```bash
# Tek seviye
DATABASE_TYPE=postgresql

# İç içe (double underscore)
DATABASE__HOST=localhost
DATABASE__PORT=5432
MODEL__CONFIDENCE_THRESHOLD=0.5
MONITORING__LOG_LEVEL=DEBUG
```

### Boolean Values

```bash
# True değerler: true, 1, yes, on
DEBUG=true
ALERTS__ENABLE_EMAIL=1

# False değerler: false, 0, no, off
DEBUG=false
ALERTS__ENABLE_SMS=0
```

### List Values

```bash
# JSON formatı
ALERTS__EMAIL_RECIPIENTS=["user1@example.com", "user2@example.com"]
MODEL__REQUIRED_PPE=["hardhat", "safety_vest"]
```

## 🛠️ CLI Argümanları

### Genel Argümanlar

```bash
--env, --environment     # Ortam seçimi (development/staging/production)
--config                 # Custom YAML config dosyası
--env-file               # Custom .env dosyası
--debug                  # Debug modunu aktifleştir
--validate-only          # Sadece doğrula, çalıştırma
```

### Model Argümanları

```bash
--model-path PATH        # Model dosya yolu
--model-type TYPE        # Model tipi (yolov8/yolov11)
--device DEVICE          # İşlem cihazı (cpu/cuda/mps)
--confidence FLOAT       # Güven eşiği (0.0-1.0)
```

### Database Argümanları

```bash
--db-type TYPE          # Database tipi (postgresql/sqlite)
--db-host HOST          # Database host
--db-port PORT          # Database port
--db-name NAME          # Database adı
```

### Monitoring Argümanları

```bash
--log-level LEVEL       # Log seviyesi
--log-file PATH         # Log dosya yolu
```

### Örnek Kullanımlar

```bash
# Development ortamında debug ile
python -m src.main --env development --debug

# Custom model ve confidence
python -m src.main --model-path models/custom.pt --confidence 0.6

# Production ortamında custom config
python -m src.main \
  --env production \
  --config /etc/ppe/config.yaml \
  --env-file /etc/ppe/.env

# SQLite database ile test
python -m src.main --db-type sqlite --log-level DEBUG
```

## 📝 Kamera Yapılandırması

### YAML'dan Kamera Yükleme

```python
from config import load_cameras_from_yaml, merge_camera_configs

# Kameraları yükle
cameras = load_cameras_from_yaml("config/cameras.yaml")

# Settings'e ekle
settings = merge_camera_configs(settings, "config/cameras.yaml")
```

### Programatik Kamera Ekleme

```python
from config import CameraConfig

# Yeni kamera oluştur
camera = CameraConfig(
    camera_id="cam_new",
    name="New Camera",
    rtsp_url="rtsp://192.168.1.100:554/stream1",
    location="New Location",
    zone="Zone X",
    fps=10,
    resolution=(1920, 1080)
)

# Settings'e ekle
settings.cameras.cameras.append(camera)
```

## 🐛 Sorun Giderme

### Yapılandırma Yüklenemiyor

```bash
# Doğrulama çalıştır
python -m config.config_validator

# Debug modu ile çalıştır
python -m src.main --debug

# Environment variables'ı kontrol et
env | grep -E "(DATABASE|MODEL|CAMERA)"
```

### Database Bağlantı Hatası

```bash
# PostgreSQL çalışıyor mu?
pg_isready -h localhost -p 5432

# Bağlantı string'ini test et
python -c "from config import get_settings; print(get_settings().get_db_connection_string())"
```

### Model Bulunamıyor

```bash
# Model dosyasını kontrol et
ls -lh models/

# Model path'i yazdır
python -c "from config import get_settings; print(get_settings().model.model_path)"
```

### Kamera Bağlantı Hatası

```bash
# RTSP URL'yi test et (ffmpeg ile)
ffmpeg -i "rtsp://camera-url" -frames:v 1 test.jpg

# Network bağlantısını kontrol et
ping 192.168.1.100
```

## 📚 İleri Seviye Kullanım

### Custom Config Validator

```python
from config import ConfigValidator

class CustomValidator(ConfigValidator):
    def validate_custom_rules(self):
        # Özel doğrulama kuralları
        if self.settings.is_production():
            if not self.settings.api.s3_enabled:
                self.add_error("Production'da S3 zorunlu!")

validator = CustomValidator(settings)
validator.validate_all()
```

### Config Template Engine

```python
import os
from jinja2 import Template

# Template render
template = Template(open("config.yaml.j2").read())
config_yaml = template.render(
    env=os.getenv("ENV"),
    db_host=os.getenv("DB_HOST")
)
```

### Secrets Management

```python
# AWS Secrets Manager
import boto3

def load_secrets():
    client = boto3.client('secretsmanager')
    secret = client.get_secret_value(SecretId='ppe/production')
    return json.loads(secret['SecretString'])

secrets = load_secrets()
os.environ['DATABASE__PASSWORD'] = secrets['db_password']
```

## 📖 Referanslar

- [Pydantic Settings Dokümantasyonu](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [12 Factor App - Config](https://12factor.net/config)
- [OWASP Configuration Management](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)

## ❓ Sık Sorulan Sorular

### Config dosyasını runtime'da değiştirebilir miyim?

Evet, `reload_settings()` fonksiyonu ile. Ancak bazı ayarlar (database, model) restart gerektirir.

### Production'da hangi ortam kullanmalıyım?

Environment variable ile: `export ENVIRONMENT=production`

### Hassas bilgileri nasıl saklarım?

.env dosyası veya AWS Secrets Manager/HashiCorp Vault gibi secrets management sistemleri.

### Birden fazla .env dosyası kullanabilir miyim?

Evet, CLI ile: `--env-file /path/to/.env`

### Config değişikliklerini nasıl test ederim?

Önce staging'de test edin, sonra production'a alın. Rollback planı hazırlayın.

## 📞 Destek

Sorularınız için:
- GitHub Issues
- Technical Documentation
- Team Slack Channel
