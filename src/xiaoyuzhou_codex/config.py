import json
from copy import deepcopy
from pathlib import Path


def _merge(left: dict, right: dict) -> dict:
    result = deepcopy(left)
    for key, value in right.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(public_path: Path, private_path: Path | None = None) -> dict:
    public = json.loads(public_path.read_text(encoding="utf-8"))
    if private_path is None or not private_path.exists():
        return public
    private = json.loads(private_path.read_text(encoding="utf-8"))
    return _merge(public, private)


