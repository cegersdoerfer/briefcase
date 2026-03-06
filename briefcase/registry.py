import os
from pathlib import Path

import yaml

REGISTRY_DIR = Path.home() / ".briefcase"
REPOS_DIR = REGISTRY_DIR / "repos"
REGISTRY_FILE = REGISTRY_DIR / "registry.yaml"


def get_paths(home: Path | None = None) -> tuple[Path, Path, Path]:
    """Return (base_dir, repos_dir, registry_file) for the given home, env var, or default."""
    if home is not None:
        base = Path(home)
    else:
        base = Path(os.environ.get("BRIEFCASE_HOME", str(Path.home() / ".briefcase")))
    return base, base / "repos", base / "registry.yaml"


def ensure_dirs(home: Path | None = None) -> None:
    base, repos, _ = get_paths(home)
    base.mkdir(parents=True, exist_ok=True)
    repos.mkdir(parents=True, exist_ok=True)


def load_registry(home: Path | None = None) -> dict:
    _, _, registry_file = get_paths(home)
    if not registry_file.exists():
        return {}
    try:
        data = yaml.safe_load(registry_file.read_text()) or {}
    except (yaml.YAMLError, OSError):
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def save_registry(data: dict, home: Path | None = None) -> None:
    ensure_dirs(home)
    _, _, registry_file = get_paths(home)
    registry_file.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))


def add_tool(name: str, repo_url: str, notes: str | None = None, tags: list[str] | None = None, home: Path | None = None) -> None:
    _, repos, _ = get_paths(home)
    registry = load_registry(home)
    if name in registry:
        raise ValueError(f"Tool '{name}' already exists in registry.")
    entry = {
        "repo_url": repo_url,
        "local_path": str(repos / name),
    }
    if notes:
        entry["notes"] = notes
    if tags:
        entry["tags"] = tags
    registry[name] = entry
    save_registry(registry, home)


def get_tool(name: str, home: Path | None = None) -> dict | None:
    registry = load_registry(home)
    tool = registry.get(name)
    if tool is None:
        return None
    return {"name": name, **tool}


def list_tools(home: Path | None = None) -> list[dict]:
    registry = load_registry(home)
    return [{"name": name, **info} for name, info in registry.items()]
