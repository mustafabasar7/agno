"""
Configuration Validator
Yapılandırma doğrulama ve güvenlik kontrolleri
Uygulama başlangıcında çalışır
"""

import os
import sys
import socket
from pathlib import Path
from typing import List, Dict, Any, Tuple
from urllib.parse import urlparse
import warnings

from .settings import Settings, get_settings


class ConfigValidationError(Exception):
    """Yapılandırma doğrulama hatası"""
    pass


class ConfigValidationWarning(UserWarning):
    """Yapılandırma doğrulama uyarısı"""
    pass


class ConfigValidator:
    """
    Yapılandırma doğrulayıcı sınıf
    Başlangıçta tüm ayarları kontrol eder
    """

    def __init__(self, settings: Settings):
        """
        Args:
            settings: Doğrulanacak ayarlar
        """
        self.settings = settings
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self, strict: bool = False) -> Tuple[bool, List[str], List[str]]:
        """
        Tüm yapılandırmayı doğrula

        Args:
            strict: True ise uyarıları da hata olarak say

        Returns:
            (başarılı mı, hatalar listesi, uyarılar listesi)
        """
        print("🔍 Yapılandırma doğrulaması başlıyor...")

        # Tüm doğrulama fonksiyonlarını çalıştır
        self.validate_environment()
        self.validate_directories()
        self.validate_database()
        self.validate_model()
        self.validate_cameras()
        self.validate_alerts()
        self.validate_api_keys()
        self.validate_monitoring()
        self.validate_security()
        self.validate_network()

        # Sonuçları raporla
        self._print_results()

        # Strict modda uyarıları da hata say
        if strict and self.warnings:
            self.errors.extend(self.warnings)
            self.warnings = []

        is_valid = len(self.errors) == 0

        return is_valid, self.errors, self.warnings

    def validate_environment(self) -> None:
        """Çalışma ortamı doğrulaması"""
        print("  ✓ Ortam ayarları kontrol ediliyor...")

        env = self.settings.environment

        # Production'da debug kapalı olmalı
        if env == "production" and self.settings.debug:
            self.add_error(
                "Production ortamında DEBUG=True kullanılamaz! "
                "Güvenlik riski oluşturur."
            )

        # Production'da log level INFO veya üzeri olmalı
        if env == "production" and self.settings.monitoring.log_level == "DEBUG":
            self.add_warning(
                "Production ortamında LOG_LEVEL=DEBUG önerilmez. "
                "Performans sorunlarına yol açabilir."
            )

        # Environment değişkeninin geçerli olduğunu kontrol et
        valid_envs = ["development", "staging", "production"]
        if env not in valid_envs:
            self.add_error(
                f"Geçersiz environment: {env}. "
                f"Geçerli değerler: {', '.join(valid_envs)}"
            )

    def validate_directories(self) -> None:
        """Dizin yapısı doğrulaması"""
        print("  ✓ Dizin yapısı kontrol ediliyor...")

        # Kontrol edilecek dizinler
        directories = [
            ("Base directory", self.settings.base_dir),
            ("Model directory", self.settings.model.model_path.parent),
            ("Snapshot directory", self.settings.monitoring.snapshot_path),
        ]

        if self.settings.monitoring.log_file:
            directories.append(
                ("Log directory", self.settings.monitoring.log_file.parent)
            )

        # Her dizini kontrol et
        for name, path in directories:
            if not path.exists():
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    self.add_warning(f"{name} oluşturuldu: {path}")
                except Exception as e:
                    self.add_error(
                        f"{name} oluşturulamadı ({path}): {str(e)}"
                    )
            elif not path.is_dir():
                self.add_error(f"{name} bir dizin değil: {path}")

            # Yazma izni kontrolü
            if path.exists() and not os.access(path, os.W_OK):
                self.add_error(f"{name} yazma izni yok: {path}")

    def validate_database(self) -> None:
        """Veritabanı ayarları doğrulaması"""
        print("  ✓ Veritabanı ayarları kontrol ediliyor...")

        db_config = self.settings.database

        if db_config.type == "sqlite":
            # SQLite dosya yolu kontrolü
            sqlite_path = db_config.sqlite_path

            # Parent dizin var mı?
            if not sqlite_path.parent.exists():
                try:
                    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    self.add_error(
                        f"SQLite dizini oluşturulamadı: {str(e)}"
                    )

        elif db_config.type == "postgresql":
            # PostgreSQL ayarları kontrolü
            if not db_config.password.get_secret_value():
                self.add_error("PostgreSQL şifresi boş olamaz!")

            # Varsayılan şifre kontrolü
            default_passwords = ["password", "123456", "postgres", "admin"]
            if db_config.password.get_secret_value() in default_passwords:
                self.add_error(
                    "Güvensiz varsayılan şifre kullanılıyor! "
                    "Lütfen güçlü bir şifre belirleyin."
                )

            # Bağlantı havuzu ayarları
            if db_config.pool_size > 50:
                self.add_warning(
                    f"Pool size çok yüksek ({db_config.pool_size}). "
                    "Veritabanı kaynaklarını aşırı tüketebilir."
                )

    def validate_model(self) -> None:
        """Model ayarları doğrulaması"""
        print("  ✓ Model ayarları kontrol ediliyor...")

        model_config = self.settings.model

        # Model dosyası var mı?
        if not model_config.model_path.exists():
            self.add_error(
                f"Model dosyası bulunamadı: {model_config.model_path}\n"
                "Lütfen modeli indirin veya eğitin."
            )
        else:
            # Model dosya boyutu kontrolü
            file_size = model_config.model_path.stat().st_size
            if file_size < 1024:  # 1 KB'dan küçük
                self.add_warning(
                    f"Model dosyası çok küçük ({file_size} bytes). "
                    "Dosya bozuk olabilir."
                )

        # Device ayarları
        if model_config.device == "cuda":
            try:
                import torch
                if not torch.cuda.is_available():
                    self.add_error(
                        "CUDA device seçilmiş ancak CUDA kullanılamıyor! "
                        "CPU veya MPS kullanın."
                    )
                elif model_config.device_id >= torch.cuda.device_count():
                    self.add_error(
                        f"Geçersiz GPU ID: {model_config.device_id}. "
                        f"Mevcut GPU sayısı: {torch.cuda.device_count()}"
                    )
            except ImportError:
                self.add_error(
                    "PyTorch kurulu değil! "
                    "pip install torch ile yükleyin."
                )

        # Threshold kontrolü
        if model_config.confidence_threshold < 0.3:
            self.add_warning(
                f"Düşük confidence threshold ({model_config.confidence_threshold}). "
                "False positive artabilir."
            )
        elif model_config.confidence_threshold > 0.8:
            self.add_warning(
                f"Yüksek confidence threshold ({model_config.confidence_threshold}). "
                "İhlaller kaçırılabilir."
            )

        # Required PPE kontrolü
        if not model_config.required_ppe:
            self.add_warning("Zorunlu PPE ekipmanı tanımlanmamış!")

    def validate_cameras(self) -> None:
        """Kamera ayarları doğrulaması"""
        print("  ✓ Kamera ayarları kontrol ediliyor...")

        cameras_config = self.settings.cameras

        # En az bir kamera olmalı
        if not cameras_config.cameras:
            self.add_warning(
                "Hiç kamera tanımlanmamış! "
                "YAML config'den veya kod ile kamera ekleyin."
            )
            return

        # Her kamerayı kontrol et
        for idx, camera in enumerate(cameras_config.cameras):
            # RTSP URL kontrolü
            rtsp_url = camera.rtsp_url.get_secret_value()

            # URL format kontrolü
            try:
                parsed = urlparse(rtsp_url)
                if not parsed.scheme:
                    self.add_error(
                        f"Kamera {camera.camera_id}: Geçersiz URL formatı"
                    )
            except Exception as e:
                self.add_error(
                    f"Kamera {camera.camera_id}: URL parse hatası: {str(e)}"
                )

            # FPS kontrolü
            if camera.fps > 30 and not self.settings.is_development():
                self.add_warning(
                    f"Kamera {camera.camera_id}: "
                    f"Yüksek FPS ({camera.fps}). "
                    "CPU/GPU kullanımı artabilir."
                )

    def validate_alerts(self) -> None:
        """Alert ayarları doğrulaması"""
        print("  ✓ Alert ayarları kontrol ediliyor...")

        alert_config = self.settings.alerts

        if not alert_config.enable_alerts:
            self.add_warning("Alert sistemi devre dışı!")
            return

        # En az bir alert kanalı aktif olmalı
        channels = [
            alert_config.enable_email,
            alert_config.enable_sms,
            alert_config.enable_webhook,
            alert_config.enable_database
        ]

        if not any(channels):
            self.add_warning(
                "Hiçbir alert kanalı aktif değil! "
                "İhlaller bildirilmeyecek."
            )

        # Email kontrolü
        if alert_config.enable_email:
            if not alert_config.email_recipients:
                self.add_error("Email alertleri aktif ama alıcı yok!")

            # Email format kontrolü
            for email in alert_config.email_recipients:
                if "@" not in email:
                    self.add_error(f"Geçersiz email adresi: {email}")

        # SMS kontrolü
        if alert_config.enable_sms:
            if not alert_config.sms_recipients:
                self.add_error("SMS alertleri aktif ama alıcı yok!")

        # Webhook kontrolü
        if alert_config.enable_webhook:
            if not alert_config.webhook_urls:
                self.add_error("Webhook alertleri aktif ama URL yok!")

            # URL kontrolü
            for url in alert_config.webhook_urls:
                if not url.startswith(("http://", "https://")):
                    self.add_error(f"Geçersiz webhook URL: {url}")

        # Alert interval kontrolü
        if alert_config.min_alert_interval < 10:
            self.add_warning(
                f"Çok kısa alert interval ({alert_config.min_alert_interval}s). "
                "Alert spam'i oluşabilir."
            )

    def validate_api_keys(self) -> None:
        """API anahtarları doğrulaması"""
        print("  ✓ API anahtarları kontrol ediliyor...")

        api_config = self.settings.api

        # Email SMTP
        if self.settings.alerts.enable_email:
            if not api_config.smtp_username:
                self.add_error("SMTP kullanıcı adı boş!")

            if not api_config.smtp_password.get_secret_value():
                self.add_error("SMTP şifresi boş!")

        # SMS Twilio
        if self.settings.alerts.enable_sms:
            if not api_config.twilio_account_sid.get_secret_value():
                self.add_error("Twilio Account SID boş!")

            if not api_config.twilio_auth_token.get_secret_value():
                self.add_error("Twilio Auth Token boş!")

        # AWS S3
        if api_config.s3_enabled:
            if not api_config.s3_bucket:
                self.add_error("S3 bucket adı boş!")

            if not api_config.s3_access_key.get_secret_value():
                self.add_error("AWS Access Key boş!")

            if not api_config.s3_secret_key.get_secret_value():
                self.add_error("AWS Secret Key boş!")

        # Webhook authentication
        if (self.settings.alerts.enable_webhook and
                api_config.webhook_auth_enabled):
            if not api_config.webhook_auth_token.get_secret_value():
                self.add_warning(
                    "Webhook authentication aktif ama token boş!"
                )

    def validate_monitoring(self) -> None:
        """Monitoring ayarları doğrulaması"""
        print("  ✓ Monitoring ayarları kontrol ediliyor...")

        monitoring_config = self.settings.monitoring

        # Port çakışmaları kontrolü
        ports = [
            ("Metrics", monitoring_config.metrics_port),
            ("Health check", monitoring_config.health_check_port),
        ]

        used_ports = {}
        for name, port in ports:
            if port in used_ports:
                self.add_error(
                    f"Port çakışması: {name} ve {used_ports[port]} "
                    f"aynı portu kullanıyor ({port})"
                )
            used_ports[port] = name

        # Log dosyası boyutu kontrolü
        if monitoring_config.log_max_size < 1024 * 1024:  # 1 MB
            self.add_warning(
                "Log dosyası boyutu çok küçük. "
                "Sık rotasyon olabilir."
            )

        # Snapshot retention kontrolü
        if monitoring_config.snapshot_retention_days < 7:
            self.add_warning(
                "Kısa snapshot saklama süresi. "
                "Geçmiş kayıtlar silinecek."
            )

    def validate_security(self) -> None:
        """Güvenlik kontrolü"""
        print("  ✓ Güvenlik kontrolleri yapılıyor...")

        # Production'da hassas bilgiler
        if self.settings.is_production():
            # .env dosyası kontrolü
            env_file = self.settings.base_dir / ".env"
            if env_file.exists():
                # Dosya izinleri
                stat_info = env_file.stat()
                mode = oct(stat_info.st_mode)[-3:]
                if mode != "600":
                    self.add_warning(
                        f".env dosya izinleri güvensiz ({mode}). "
                        "chmod 600 .env ile düzeltin."
                    )

            # Debug mode kontrolü (tekrar)
            if self.settings.debug:
                self.add_error(
                    "Production'da DEBUG=True kullanılamaz!"
                )

            # Varsayılan şifreler kontrolü
            default_values = [
                "password", "123456", "admin", "default",
                "changeme", "secret"
            ]

            # Database şifresi
            db_pass = self.settings.database.password.get_secret_value()
            if db_pass.lower() in default_values:
                self.add_error(
                    "Production'da varsayılan database şifresi kullanılamaz!"
                )

    def validate_network(self) -> None:
        """Network bağlantıları kontrolü"""
        print("  ✓ Network bağlantıları kontrol ediliyor...")

        # Database bağlantısı (sadece PostgreSQL)
        if self.settings.database.type == "postgresql":
            host = self.settings.database.host
            port = self.settings.database.port

            if not self._check_port_open(host, port, timeout=5):
                self.add_warning(
                    f"PostgreSQL sunucusuna bağlanılamıyor: {host}:{port}\n"
                    "Sunucunun çalıştığından emin olun."
                )

    def _check_port_open(
        self, host: str, port: int, timeout: int = 3
    ) -> bool:
        """
        Port açık mı kontrol et

        Args:
            host: Sunucu adresi
            port: Port numarası
            timeout: Timeout (saniye)

        Returns:
            Port açıksa True
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def add_error(self, message: str) -> None:
        """Hata ekle"""
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        """Uyarı ekle"""
        self.warnings.append(message)

    def _print_results(self) -> None:
        """Doğrulama sonuçlarını yazdır"""
        print("\n" + "=" * 70)
        print("Yapılandırma Doğrulama Sonuçları")
        print("=" * 70)

        if self.errors:
            print(f"\n❌ {len(self.errors)} HATA bulundu:\n")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")

        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} UYARI bulundu:\n")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ Tüm kontroller başarılı!")

        print("\n" + "=" * 70 + "\n")


def validate_config(
    settings: Settings = None,
    strict: bool = False,
    exit_on_error: bool = True
) -> bool:
    """
    Yapılandırmayı doğrula

    Args:
        settings: Doğrulanacak ayarlar (None ise mevcut ayarları al)
        strict: Strict mod (uyarıları da hata say)
        exit_on_error: Hata varsa uygulamadan çık

    Returns:
        Doğrulama başarılı mı

    Raises:
        ConfigValidationError: Doğrulama başarısız ve exit_on_error=False ise
    """
    if settings is None:
        settings = get_settings()

    validator = ConfigValidator(settings)
    is_valid, errors, warnings = validator.validate_all(strict=strict)

    # Uyarıları warnings modülü ile göster
    for warning in warnings:
        warnings.warn(warning, ConfigValidationWarning)

    # Hatalar varsa
    if not is_valid:
        if exit_on_error:
            print("\n❌ Yapılandırma doğrulama başarısız!")
            print("Lütfen yukarıdaki hataları düzeltin ve tekrar deneyin.\n")
            sys.exit(1)
        else:
            raise ConfigValidationError(
                f"Yapılandırma doğrulama başarısız: {len(errors)} hata"
            )

    return is_valid


def quick_check() -> None:
    """Hızlı yapılandırma kontrolü (script olarak çalıştırma için)"""
    print("🚀 PPE Detection - Yapılandırma Kontrolü\n")

    try:
        settings = get_settings()
        validate_config(settings, strict=False, exit_on_error=True)
        print("✅ Yapılandırma başarıyla doğrulandı!\n")
        print("Uygulama başlatılmaya hazır.")

    except Exception as e:
        print(f"\n❌ Hata: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    quick_check()
