"""Simple configuration handling."""

import json
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = ".dbconfig.json") -> Dict[str, Any]:
    """Load configuration from file."""
    path = Path(config_path)
    if path.exists():
        return json.loads(path.read_text())
    return {}


def save_config(config: Dict[str, Any], config_path: str = ".dbconfig.json") -> None:
    """Save configuration to file."""
    path = Path(config_path)
    path.write_text(json.dumps(config, indent=2))
