from pathlib import Path

import yaml


def load_config(home: Path | None = None) -> dict:
    """Read {home}/config.yaml, returning {} if missing or invalid."""
    if home is None:
        return {}
    config_file = home / "config.yaml"
    if not config_file.exists():
        return {}
    try:
        data = yaml.safe_load(config_file.read_text()) or {}
    except (yaml.YAMLError, OSError):
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def get_default_layout(home: Path | None = None) -> str:
    """Return the configured default layout name, or 'default'."""
    config = load_config(home)
    return config.get("default_layout", "default")
