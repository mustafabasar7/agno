"""
Configuration Loader
Çoklu kaynaktan yapılandırma yükleme
Öncelik: CLI args > Environment vars > Config files > Defaults
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml
from dotenv import load_dotenv

from .settings import Settings, CameraConfig


class ConfigLoader:
    """
    Yapılandırma yükleyici sınıf
    Farklı kaynaklardan ayarları birleştirir
    """

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Args:
            base_dir: Ana dizin (None ise otomatik tespit)
        """
        if base_dir is None:
            # Config dosyasının parent dizini
            base_dir = Path(__file__).parent.parent

        self.base_dir = base_dir
        self.config_dir = base_dir / "config"
        self.env_loaded = False

    def load(
        self,
        env_file: Optional[Path] = None,
        config_file: Optional[Path] = None,
        environment: Optional[str] = None,
        cli_args: Optional[Dict[str, Any]] = None
    ) -> Settings:
        """
        Yapılandırmayı yükle

        Öncelik sırası (yüksekten düşüğe):
        1. CLI argümanları
        2. Environment değişkenleri
        3. .env dosyası
        4. YAML config dosyası
        5. Varsayılan değerler

        Args:
            env_file: .env dosya yolu
            config_file: YAML config dosya yolu
            environment: Ortam (development/staging/production)
            cli_args: CLI argümanları dict

        Returns:
            Settings instance
        """
        print("📦 Yapılandırma yükleniyor...\n")

        # 1. Environment değişkenlerini oku
        self._load_env_file(env_file)

        # 2. Environment belirle
        if environment is None:
            environment = os.getenv("ENVIRONMENT", "development")

        # 3. YAML config dosyasını yükle
        yaml_config = self._load_yaml_config(config_file, environment)

        # 4. Environment değişkenlerini override olarak uygula
        env_overrides = self._collect_env_overrides()

        # 5. CLI argümanlarını uygula
        cli_overrides = cli_args or {}

        # 6. Tüm ayarları birleştir
        final_config = self._merge_configs(
            yaml_config,
            env_overrides,
            cli_overrides
        )

        # 7. Environment'ı set et
        final_config["environment"] = environment

        # 8. Settings oluştur
        settings = Settings(**final_config)

        print("✅ Yapılandırma yüklendi\n")
        self._print_config_summary(settings)

        return settings

    def _load_env_file(self, env_file: Optional[Path] = None) -> None:
        """
        .env dosyasını yükle

        Args:
            env_file: .env dosya yolu (None ise otomatik tespit)
        """
        if self.env_loaded:
            return

        # .env dosya yolunu belirle
        if env_file is None:
            # Sırayla dene: base_dir/.env, config/.env
            possible_paths = [
                self.base_dir / ".env",
                self.config_dir / ".env",
            ]

            for path in possible_paths:
                if path.exists():
                    env_file = path
                    break

        # .env dosyasını yükle
        if env_file and env_file.exists():
            print(f"  📄 .env dosyası yükleniyor: {env_file}")
            load_dotenv(env_file, override=True)
            self.env_loaded = True
        else:
            print("  ⚠️  .env dosyası bulunamadı, environment değişkenleri kullanılıyor")

    def _load_yaml_config(
        self,
        config_file: Optional[Path] = None,
        environment: str = "development"
    ) -> Dict[str, Any]:
        """
        YAML config dosyasını yükle

        Args:
            config_file: Config dosya yolu
            environment: Ortam adı

        Returns:
            Config dictionary
        """
        # Config dosya yolunu belirle
        if config_file is None:
            # environments/{environment}.yaml
            config_file = (
                self.config_dir / "environments" / f"{environment}.yaml"
            )

        # Dosya yoksa boş dict dön
        if not config_file.exists():
            print(f"  ⚠️  YAML config bulunamadı: {config_file}")
            return {}

        print(f"  📄 YAML config yükleniyor: {config_file}")

        # YAML dosyasını oku
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
            return config
        except Exception as e:
            print(f"  ❌ YAML okuma hatası: {str(e)}")
            return {}

    def _collect_env_overrides(self) -> Dict[str, Any]:
        """
        Environment değişkenlerinden override'ları topla

        Returns:
            Override dictionary
        """
        # Pydantic Settings otomatik olarak env var'ları işler
        # Bu fonksiyon ekstra override'lar için kullanılabilir
        overrides = {}

        # Özel environment variable mapping'leri buraya eklenebilir
        # Örnek: LOG_LEVEL -> monitoring.log_level

        return overrides

    def _merge_configs(
        self,
        yaml_config: Dict[str, Any],
        env_overrides: Dict[str, Any],
        cli_overrides: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Tüm config kaynaklarını birleştir

        Args:
            yaml_config: YAML'dan gelen config
            env_overrides: Environment override'ları
            cli_overrides: CLI override'ları

        Returns:
            Birleştirilmiş config
        """
        # Base olarak YAML config'i al
        final_config = yaml_config.copy()

        # Environment override'larını uygula
        final_config = self._deep_merge(final_config, env_overrides)

        # CLI override'larını uygula (en yüksek öncelik)
        final_config = self._deep_merge(final_config, cli_overrides)

        return final_config

    def _deep_merge(
        self,
        base: Dict[str, Any],
        override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        İki dictionary'yi deep merge et

        Args:
            base: Temel dictionary
            override: Override dictionary

        Returns:
            Birleştirilmiş dictionary
        """
        result = base.copy()

        for key, value in override.items():
            if (
                key in result and
                isinstance(result[key], dict) and
                isinstance(value, dict)
            ):
                # İç içe dict'leri recursive merge et
                result[key] = self._deep_merge(result[key], value)
            else:
                # Değeri override et
                result[key] = value

        return result

    def _print_config_summary(self, settings: Settings) -> None:
        """
        Yapılandırma özetini yazdır

        Args:
            settings: Settings instance
        """
        print("=" * 70)
        print("Yapılandırma Özeti")
        print("=" * 70)
        print(f"  Uygulama: {settings.app_name} v{settings.app_version}")
        print(f"  Ortam: {settings.environment}")
        print(f"  Debug: {settings.debug}")
        print(f"  Base Dir: {settings.base_dir}")
        print(f"  Database: {settings.database.type}")
        print(f"  Model: {settings.model.model_type} ({settings.model.model_size})")
        print(f"  Device: {settings.model.device}")
        print(f"  Cameras: {len(settings.cameras.cameras)}")
        print(f"  Alerts: {'Enabled' if settings.alerts.enable_alerts else 'Disabled'}")
        print(f"  Log Level: {settings.monitoring.log_level}")
        print("=" * 70 + "\n")


class CLIConfigLoader:
    """
    CLI argümanlarından yapılandırma yükleyici
    Komut satırı arayüzü desteği
    """

    def __init__(self):
        """Initialize CLI parser"""
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """
        Argument parser oluştur

        Returns:
            ArgumentParser instance
        """
        parser = argparse.ArgumentParser(
            description="PPE Detection System - Configuration",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Örnekler:
  # Development ortamında çalıştır
  python -m src.main --env development

  # Production ortamında custom config ile
  python -m src.main --env production --config /path/to/config.yaml

  # Debug modu ile
  python -m src.main --debug

  # Custom .env dosyası ile
  python -m src.main --env-file /path/to/.env

  # Model path override
  python -m src.main --model-path models/custom_model.pt

  # Confidence threshold override
  python -m src.main --confidence 0.6
            """
        )

        # Genel ayarlar
        parser.add_argument(
            "--env", "--environment",
            type=str,
            choices=["development", "staging", "production"],
            help="Çalışma ortamı"
        )

        parser.add_argument(
            "--config", "--config-file",
            type=Path,
            help="YAML config dosya yolu"
        )

        parser.add_argument(
            "--env-file",
            type=Path,
            help=".env dosya yolu"
        )

        parser.add_argument(
            "--debug",
            action="store_true",
            help="Debug modunu aktifleştir"
        )

        parser.add_argument(
            "--validate-only",
            action="store_true",
            help="Sadece config'i doğrula, uygulamayı başlatma"
        )

        # Model ayarları
        model_group = parser.add_argument_group("Model Ayarları")

        model_group.add_argument(
            "--model-path",
            type=Path,
            help="Model dosya yolu"
        )

        model_group.add_argument(
            "--model-type",
            type=str,
            choices=["yolov8", "yolov11"],
            help="Model tipi"
        )

        model_group.add_argument(
            "--device",
            type=str,
            choices=["cpu", "cuda", "mps"],
            help="İşlem cihazı"
        )

        model_group.add_argument(
            "--confidence",
            type=float,
            help="Güven eşiği (0.0-1.0)"
        )

        # Database ayarları
        db_group = parser.add_argument_group("Database Ayarları")

        db_group.add_argument(
            "--db-type",
            type=str,
            choices=["postgresql", "sqlite"],
            help="Veritabanı tipi"
        )

        db_group.add_argument(
            "--db-host",
            type=str,
            help="Database host"
        )

        db_group.add_argument(
            "--db-port",
            type=int,
            help="Database port"
        )

        db_group.add_argument(
            "--db-name",
            type=str,
            help="Database adı"
        )

        # Monitoring ayarları
        monitor_group = parser.add_argument_group("Monitoring Ayarları")

        monitor_group.add_argument(
            "--log-level",
            type=str,
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Log seviyesi"
        )

        monitor_group.add_argument(
            "--log-file",
            type=Path,
            help="Log dosya yolu"
        )

        return parser

    def parse_args(self, args: Optional[List[str]] = None) -> argparse.Namespace:
        """
        CLI argümanlarını parse et

        Args:
            args: Argüman listesi (None ise sys.argv kullanılır)

        Returns:
            Parsed arguments
        """
        return self.parser.parse_args(args)

    def args_to_dict(self, args: argparse.Namespace) -> Dict[str, Any]:
        """
        Parsed argümanları config dict'e çevir

        Args:
            args: Parsed arguments

        Returns:
            Config dictionary
        """
        config = {}

        # Debug
        if args.debug:
            config["debug"] = True

        # Model ayarları
        if args.model_path or args.model_type or args.device or args.confidence:
            config["model"] = {}

            if args.model_path:
                config["model"]["model_path"] = args.model_path

            if args.model_type:
                config["model"]["model_type"] = args.model_type

            if args.device:
                config["model"]["device"] = args.device

            if args.confidence is not None:
                config["model"]["confidence_threshold"] = args.confidence

        # Database ayarları
        if args.db_type or args.db_host or args.db_port or args.db_name:
            config["database"] = {}

            if args.db_type:
                config["database"]["type"] = args.db_type

            if args.db_host:
                config["database"]["host"] = args.db_host

            if args.db_port:
                config["database"]["port"] = args.db_port

            if args.db_name:
                config["database"]["database"] = args.db_name

        # Monitoring ayarları
        if args.log_level or args.log_file:
            config["monitoring"] = {}

            if args.log_level:
                config["monitoring"]["log_level"] = args.log_level

            if args.log_file:
                config["monitoring"]["log_file"] = args.log_file

        return config


def load_config_from_cli(args: Optional[List[str]] = None) -> Settings:
    """
    CLI argümanlarından yapılandırma yükle

    Args:
        args: CLI argümanları (None ise sys.argv)

    Returns:
        Settings instance
    """
    # CLI parser oluştur
    cli_loader = CLIConfigLoader()
    parsed_args = cli_loader.parse_args(args)

    # Config loader oluştur
    loader = ConfigLoader()

    # CLI argümanlarını dict'e çevir
    cli_config = cli_loader.args_to_dict(parsed_args)

    # Yapılandırmayı yükle
    settings = loader.load(
        env_file=parsed_args.env_file,
        config_file=parsed_args.config,
        environment=parsed_args.env,
        cli_args=cli_config
    )

    return settings


def load_cameras_from_yaml(yaml_path: Path) -> List[CameraConfig]:
    """
    YAML dosyasından kamera yapılandırmalarını yükle

    Args:
        yaml_path: YAML dosya yolu

    Returns:
        Kamera config listesi
    """
    if not yaml_path.exists():
        print(f"⚠️  Kamera config dosyası bulunamadı: {yaml_path}")
        return []

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        cameras = data.get("cameras", {}).get("cameras", [])

        # CameraConfig instance'larına çevir
        camera_configs = []
        for cam_data in cameras:
            camera_configs.append(CameraConfig(**cam_data))

        print(f"✅ {len(camera_configs)} kamera yapılandırması yüklendi")
        return camera_configs

    except Exception as e:
        print(f"❌ Kamera config okuma hatası: {str(e)}")
        return []


def merge_camera_configs(
    settings: Settings,
    camera_yaml: Optional[Path] = None
) -> Settings:
    """
    Kamera yapılandırmalarını ana settings'e merge et

    Args:
        settings: Ana settings
        camera_yaml: Kamera YAML dosya yolu

    Returns:
        Güncellenmiş settings
    """
    if camera_yaml is None:
        # Default kamera config dosyası
        camera_yaml = settings.base_dir / "config" / "cameras.yaml"

    if camera_yaml.exists():
        cameras = load_cameras_from_yaml(camera_yaml)
        settings.cameras.cameras = cameras

    return settings


if __name__ == "__main__":
    # CLI'dan config yükle ve test et
    print("🚀 Configuration Loader Test\n")

    try:
        settings = load_config_from_cli()
        print("\n✅ Yapılandırma başarıyla yüklendi!")

    except Exception as e:
        print(f"\n❌ Hata: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
