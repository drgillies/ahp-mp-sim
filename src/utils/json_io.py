import json
from pathlib import Path
from typing import Any


def load_json_file(path: str | Path) -> dict[str, Any]:
    """Load and return JSON object from a file path."""
    with open(path, "r", encoding="utf-8") as file_obj:
        return json.load(file_obj)
