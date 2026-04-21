from pathlib import Path
from typing import Optional
import yaml

_DEFAULT_EXCLUDE = ["node_modules", ".venv", "__pycache__"]


def load_global_config(config_path: Optional[Path] = None) -> dict:
    if config_path is None:
        config_path = Path(__file__).parent.parent / "vibe.yaml"
    if not config_path.exists():
        return {"scan_dirs": [], "exclude": _DEFAULT_EXCLUDE, "port": 8888}
    try:
        with open(config_path) as f:
            data = yaml.safe_load(f) or {}
    except (OSError, yaml.YAMLError) as e:
        raise RuntimeError(f"Failed to load config from {config_path}: {e}") from e
    return {
        "scan_dirs": [str(Path(d).expanduser()) for d in data.get("scan_dirs", [])],
        "exclude": data.get("exclude", _DEFAULT_EXCLUDE),
        "port": data.get("port", 8888),
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
