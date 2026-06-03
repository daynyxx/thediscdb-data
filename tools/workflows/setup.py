import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import save_config
from utils import calculate_disc_hash
from workflows.selectors import select_drive
from models import Config, DriveConfig


def run_calc_hash(cfg: Config) -> None:
    print("\n=== Calculate Disc Hash ===")
    drive = select_drive(cfg)
    if not drive:
        return
    hash_info = calculate_disc_hash(drive.letter)
    if hash_info:
        print(f"Hash: {hash_info.hash}")
        print(f"Files: {len(hash_info.files)}")
    else:
        print("No disc found or unsupported format.")


def setup_config(cfg: Config) -> None:
    print("\n=== Setup ===")
    print(f"Data repo path [{cfg.data_repository_path}]: ", end="")
    val = input().strip()
    if val:
        cfg.data_repository_path = val
    print(f"TMDB API key [{cfg.tmdb_api_key}]: ", end="")
    val = input().strip()
    if val:
        cfg.tmdb_api_key = val
    print(f"makemkvcon path [{cfg.makemkvcon_path}]: ", end="")
    val = input().strip()
    if val:
        cfg.makemkvcon_path = val

    print("\nDrives:")
    for d in cfg.drives:
        print(f"  [{d.index}] {d.name} ({d.letter})")

    add = input("Add drive? (y/n): ").strip().lower() == "y"
    while add:
        idx = input("Drive index: ").strip()
        letter = input("Drive letter: ").strip()
        name = input("Drive name: ").strip()
        if idx.isdigit() and letter:
            cfg.drives.append(DriveConfig(int(idx), letter, name))
        add = input("Add another? (y/n): ").strip().lower() == "y"

    save_config(cfg)
    print("Config saved.")