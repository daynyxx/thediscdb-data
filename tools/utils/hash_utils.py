import hashlib
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from models import HashFileInfo, HashInfo

from parsers import parse_csv_line


# TODO: Automate getting disc hash if the disc doesn't automount correctly
def calculate_disc_hash(drive_letter: str) -> HashInfo | None:
    blu_ray_path = f"/mnt/{drive_letter.lower()}/BDMV/STREAM"

    path = None
    pattern = "*.m2ts"
    if os.path.isdir(blu_ray_path):
        path = blu_ray_path

    if not path:
        return None

    files = sorted(Path(path).glob(pattern), key=lambda p: p.name)
    info = HashInfo(files=[])
    for idx, f in enumerate(files):
        stat = f.stat()
        info.files.append(HashFileInfo(
            index=idx,
            name=f.name,
            creation_time=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            size=stat.st_size
        ))

    md5 = hashlib.md5()
    for f in info.files:
        md5.update(f.size.to_bytes(8, 'little'))
    info.hash = md5.hexdigest().upper()
    return info


def append_hash_to_log(log_path: str, hash_info: HashInfo) -> None:
    lines: list[str] = []
    with open(log_path) as f:
        for line in f:
            if not line.startswith("HSH:"):
                lines.append(line.rstrip())

    for hf in hash_info.files:
        lines.append(f'HSH:{hf.index},"{hf.name}","{hf.creation_time}",{hf.size}')

    with open(log_path, "w") as f:
        _ = f.write("\n".join(lines) + "\n")


def clean_log(log_path: str) -> None:
    lines: list[str] = []
    changed = False
    with open(log_path) as f:
        for line in f:
            original = line
            if line.startswith("MSG:1004") or line.startswith("MSG:2003") or line.startswith("MSG:3338"):
                parts = parse_csv_line(line)
                for j in range(1, len(parts)):
                    if parts[j] and parts[j] not in ("0", "1", "2", "3", "6209", "6201", "6202", "6203"):
                        if parts[j] not in ("***", "Using LibreDrive mode", "Using direct disc access mode", "Loaded content hash table"):
                            line = line.replace(f'"{parts[j]}"', '"***"')
                            changed = True
            elif line.startswith("DRV:"):
                line = re.sub(r'"[^"]+"(?=[,)]|$)', '"***"', line, count=3)
                changed = True
            lines.append(line.rstrip() if line == original else line.rstrip())

    if changed:
        with open(log_path, "w") as f:
            _ = f.write("\n".join(lines) + "\n")
