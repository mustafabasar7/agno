"""
Configuration Schema Generator
JSON Schema ve dokümantasyon oluşturur
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Settings


def generate_json_schema() -> Dict[str, Any]:
    """
    Settings sınıfından JSON Schema oluştur

    Returns:
        JSON Schema dictionary
    """
    return Settings.model_json_schema()


def save_schema(schema: Dict[str, Any], output_path: Path) -> None:
    """
    Schema'yı dosyaya kaydet

    Args:
        schema: JSON Schema
        output_path: Çıktı dosya yolu
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)

    print(f"✅ Schema kaydedildi: {output_path}")


def generate_markdown_doc(schema: Dict[str, Any]) -> str:
    """
    Schema'dan Markdown dokümantasyon oluştur

    Args:
        schema: JSON Schema

    Returns:
        Markdown string
    """
    md = "# PPE Detection Configuration Schema\n\n"
    md += "Bu dokümantasyon otomatik olarak oluşturulmuştur.\n\n"

    # Ana özellikler
    properties = schema.get('properties', {})

    for prop_name, prop_info in properties.items():
        md += f"## {prop_name}\n\n"

        # Açıklama
        if 'description' in prop_info:
            md += f"{prop_info['description']}\n\n"

        # Tip
        if 'type' in prop_info:
            md += f"**Type:** `{prop_info['type']}`\n\n"

        # Default değer
        if 'default' in prop_info:
            md += f"**Default:** `{prop_info['default']}`\n\n"

        # Nested properties (object ise)
        if prop_info.get('type') == 'object' and 'properties' in prop_info:
            md += "### Properties:\n\n"
            for sub_name, sub_info in prop_info['properties'].items():
                md += f"- **{sub_name}**"
                if 'description' in sub_info:
                    md += f": {sub_info['description']}"
                md += "\n"

            md += "\n"

        # Referans (allOf, anyOf, $ref varsa)
        if '$ref' in prop_info:
            md += f"**Reference:** `{prop_info['$ref']}`\n\n"

        md += "---\n\n"

    return md


def generate_env_template(schema: Dict[str, Any]) -> str:
    """
    Schema'dan .env template oluştur

    Args:
        schema: JSON Schema

    Returns:
        .env template string
    """
    env = "# PPE Detection Configuration - Environment Variables\n"
    env += "# Otomatik oluşturulmuştur\n\n"

    properties = schema.get('properties', {})

    for prop_name, prop_info in properties.items():
        # Açıklama ekle
        if 'description' in prop_info:
            env += f"# {prop_info['description']}\n"

        # Environment variable adı
        env_var = prop_name.upper()

        # Default değer
        if 'default' in prop_info:
            default_val = prop_info['default']
            if isinstance(default_val, str):
                env += f'{env_var}="{default_val}"\n'
            else:
                env += f'{env_var}={default_val}\n'
        else:
            env += f'# {env_var}=\n'

        env += "\n"

    return env


def generate_yaml_template(schema: Dict[str, Any]) -> str:
    """
    Schema'dan YAML template oluştur

    Args:
        schema: JSON Schema

    Returns:
        YAML template string
    """
    import yaml

    # Basit template oluştur
    template = {}
    properties = schema.get('properties', {})

    for prop_name, prop_info in properties.items():
        if 'default' in prop_info:
            template[prop_name] = prop_info['default']

    return yaml.dump(template, default_flow_style=False, allow_unicode=True)


def print_schema_summary(schema: Dict[str, Any]) -> None:
    """
    Schema özetini yazdır

    Args:
        schema: JSON Schema
    """
    print("\n" + "=" * 70)
    print("Configuration Schema Summary")
    print("=" * 70)

    properties = schema.get('properties', {})
    print(f"\nToplam {len(properties)} ana yapılandırma bölümü:\n")

    for prop_name, prop_info in properties.items():
        prop_type = prop_info.get('type', 'unknown')
        desc = prop_info.get('description', 'No description')
        print(f"  - {prop_name} ({prop_type})")
        print(f"    {desc}")

    # Definitions/Components
    definitions = schema.get('$defs', {})
    if definitions:
        print(f"\n{len(definitions)} yapılandırma modeli tanımlı:\n")
        for def_name in definitions.keys():
            print(f"  - {def_name}")

    print("\n" + "=" * 70)


def main():
    """Ana fonksiyon"""
    print("🔧 Configuration Schema Generator")
    print("=" * 70)

    # Schema oluştur
    print("\n📋 JSON Schema oluşturuluyor...")
    schema = generate_json_schema()

    # Özet yazdır
    print_schema_summary(schema)

    # Çıktı dizini
    output_dir = Path(__file__).parent / "generated"
    output_dir.mkdir(exist_ok=True)

    # 1. JSON Schema kaydet
    print("\n💾 Dosyalar kaydediliyor...\n")
    save_schema(schema, output_dir / "config_schema.json")

    # 2. Markdown dokümantasyon
    md_doc = generate_markdown_doc(schema)
    md_path = output_dir / "CONFIG_SCHEMA.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_doc)
    print(f"✅ Markdown dokümantasyon kaydedildi: {md_path}")

    # 3. .env template
    env_template = generate_env_template(schema)
    env_path = output_dir / "template.env"
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_template)
    print(f"✅ .env template kaydedildi: {env_path}")

    # 4. YAML template
    yaml_template = generate_yaml_template(schema)
    yaml_path = output_dir / "template.yaml"
    with open(yaml_path, 'w', encoding='utf-8') as f:
        f.write(yaml_template)
    print(f"✅ YAML template kaydedildi: {yaml_path}")

    print("\n" + "=" * 70)
    print("✅ Schema generation tamamlandı!")
    print("=" * 70)
    print(f"\nOluşturulan dosyalar: {output_dir}/")
    print("  - config_schema.json     (JSON Schema)")
    print("  - CONFIG_SCHEMA.md       (Markdown dokümantasyon)")
    print("  - template.env           (.env template)")
    print("  - template.yaml          (YAML template)")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Hata: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
