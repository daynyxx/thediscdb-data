import json
from typing import Any


def read_json(path: str) -> dict[str, Any]:
    with open(path) as f:
        return json.load(f)


def write_json(path: str, data: dict[str, Any]) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)