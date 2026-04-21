from pathlib import Path
from typing import Optional
import yaml

_DEFAULT_EXCLUDE = ["node_modules", ".venv", "__pycache__"]


def _read_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except (OSError, yaml.YAMLError) as e:
        raise RuntimeError(f"Failed to load config from {path}: {e}") from e


def load_global_config(config_path: Optional[Path] = None) -> dict:
    if config_path is None:
        config_path = Path(__file__).parent.parent / "vibe.yaml"
    # Merge home config (~/.vibe.yaml) with project config
    home_data = _read_yaml(Path.home() / ".vibe.yaml")
    proj_data = _read_yaml(config_path)
    data = {**home_data, **proj_data}  # project overrides home
    return {
        "scan_dirs": [str(Path(d).expanduser()) for d in data.get("scan_dirs", [])],
        "exclude": data.get("exclude", _DEFAULT_EXCLUDE),
        "port": data.get("port", 8888),
        "openrouter_api_key": data.get("openrouter_api_key"),
    }


def load_project_config(project_path: Path) -> Optional[dict]:
    vibe_yaml = project_path / "vibe.yaml"
    if not vibe_yaml.exists():
        return None
    try:
        with open(vibe_yaml) as f:
            return yaml.safe_load(f) or {}
    except (OSError, yaml.YAMLError) as e:
        raise RuntimeError(f"Failed to load config from {vibe_yaml}: {e}") from e
