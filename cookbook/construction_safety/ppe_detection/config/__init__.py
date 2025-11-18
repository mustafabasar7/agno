"""
PPE Detection Configuration Package

Bu paket yapılandırma yönetimi için gerekli tüm modülleri içerir.

Kullanım:
    from config import get_settings, validate_config, load_config_from_cli

    # Ayarları yükle
    settings = get_settings()

    # Yapılandırmayı doğrula
    validate_config(settings)

    # CLI'dan yükle
    settings = load_config_from_cli()
"""

from .settings import (
    Settings,
    DatabaseConfig,
    CameraConfig,
    CamerasConfig,
    ModelConfig,
    AlertConfig,
    APIConfig,
    MonitoringConfig,
    get_settings,
    get_config,
    reload_settings,
)

from .config_validator import (
    ConfigValidator,
    ConfigValidationError,
    ConfigValidationWarning,
    validate_config,
    quick_check,
)

from .config_loader import (
    ConfigLoader,
    CLIConfigLoader,
    load_config_from_cli,
    load_cameras_from_yaml,
    merge_camera_configs,
)

# Version
__version__ = "1.0.0"

# Public API
__all__ = [
    # Settings
    "Settings",
    "DatabaseConfig",
    "CameraConfig",
    "CamerasConfig",
    "ModelConfig",
    "AlertConfig",
    "APIConfig",
    "MonitoringConfig",
    "get_settings",
    "get_config",
    "reload_settings",
    # Validator
    "ConfigValidator",
    "ConfigValidationError",
    "ConfigValidationWarning",
    "validate_config",
    "quick_check",
    # Loader
    "ConfigLoader",
    "CLIConfigLoader",
    "load_config_from_cli",
    "load_cameras_from_yaml",
    "merge_camera_configs",
]


def initialize_config(
    validate: bool = True,
    strict: bool = False
) -> Settings:
    """
    Yapılandırmayı başlat ve doğrula

    Args:
        validate: Doğrulama yap
        strict: Strict mod (uyarıları da hata say)

    Returns:
        Settings instance

    Raises:
        ConfigValidationError: Doğrulama başarısız
    """
    # Ayarları yükle
    settings = get_settings()

    # Doğrula
    if validate:
        validate_config(settings, strict=strict, exit_on_error=False)

    return settings
