from models import Config, DriveConfig


def select_drive(cfg: Config) -> DriveConfig | None:
    if len(cfg.drives) == 0:
        print("No drives configured in config.json. Please add drives.")
        return None
    if len(cfg.drives) == 1:
        return cfg.drives[0]
    print("Select a drive:")
    for i, d in enumerate(cfg.drives):
        print(f"  [{i + 1}] {d.name} ({d.letter})")
    choice = input("Choice: ").strip()
    if not choice:
        return None
    idx = int(choice) - 1
    if 0 <= idx < len(cfg.drives):
        return cfg.drives[idx]
    return None


def select_format() -> str:
    print("Select disc format:")
    print("  [1] Blu-Ray")
    print("  [2] UHD")
    print("  [3] DVD")
    choice = input("Choice: ").strip()
    return {"1": "Blu-Ray", "2": "UHD", "3": "DVD"}.get(choice, "Blu-Ray")


def select_item_type() -> str:
    print("Select item type:")
    print("  [1] Movie")
    print("  [2] Series")
    choice = input("Choice: ").strip()
    return "Series" if choice == "2" else "Movie"


def find_disc_name(base_path: str) -> tuple[str, int]:
    from pathlib import Path

    for i in range(1, 100):
        name = f"disc{i:02d}"
        if not any(f.name.startswith(name) for f in Path(base_path).iterdir()):
            return name, i
    return "disc01", 1