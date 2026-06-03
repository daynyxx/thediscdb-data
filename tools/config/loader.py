import json
from pathlib import Path
from typing import Any

from models import Config, DriveConfig

CONFIG_PATH = Path(__file__).parent.parent / "config.json"


def load_config() -> Config:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            data: dict[str, Any] = json.load(f)
        cfg = Config(
            data_repository_path=str(data.get("ImportBuddy", {}).get("DataRepositoryPath", "")),
            tmdb_api_key=str(data.get("TheMovieDb", {}).get("ApiKey", "")),
            makemkvcon_path=str(data.get("MakeMkv", {}).get("Path", "/usr/bin/makemkv")),
        )
        drives_data = data.get("MakeMkv", {})
        if isinstance(drives_data, dict):
            for d in drives_data.get("Drives", []):
                if isinstance(d, dict):
                    cfg.drives.append(DriveConfig(d["Index"], d["Letter"], d["Name"]))
        return cfg
    return Config()


def save_config(cfg: Config) -> None:
    data = {
        "ImportBuddy": {"DataRepositoryPath": cfg.data_repository_path},
        "TheMovieDb": {"ApiKey": cfg.tmdb_api_key},
        "MakeMkv": {
            "Path": cfg.makemkvcon_path,
            "Drives": [{"Index": d.index, "Letter": d.letter, "Name": d.name} for d in cfg.drives]
        }
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)
