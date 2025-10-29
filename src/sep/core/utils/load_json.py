import json
from pathlib import Path

def load_json(path: str | Path):
    """Loads a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)