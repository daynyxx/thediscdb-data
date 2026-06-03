import json
from pathlib import Path
from typing import Any

from models import Config
from parsers import parse_log_file, parse_summary_file


def strip_null(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: strip_null(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [strip_null(i) for i in obj]
    return obj


def run_finalize(_cfg: Config) -> None:
    print("\n=== Finalize ===")
    release_dir = input("Release folder: ").strip()
    if not release_dir:
        return

    summary_files = sorted(Path(release_dir).glob("*-summary.txt"))
    if not summary_files:
        print("No summary files found.")
        return

    for summary_path in summary_files:
        log_path = Path(str(summary_path).replace("-summary", ""))
        if not log_path.exists():
            print(f"No log file for {summary_path.name}")
            continue

        print(f"\nFinalizing {summary_path.name}...")

        disc_info = parse_log_file(str(log_path))
        with open(summary_path) as f:
            summary_content = f.read()
        summary_items = parse_summary_file(summary_content)

        disc_path = Path(str(log_path).replace(".txt", ".json"))
        if disc_path.exists():
            with open(disc_path) as f:
                disc_json: dict[str, Any] = json.load(f)
        else:
            disc_json = {"Titles": []}

        disc_json.setdefault("Titles", [])

        disc_json["Titles"] = []
        for lt in disc_info.titles:
            t: dict[str, Any] = {
                "Index": lt.index,
                "SourceFile": lt.playlist,
                "SegmentMap": lt.segment_map,
                "Duration": lt.length,
                "Size": lt.size,
                "DisplaySize": lt.display_size,
                "Comment": lt.comment,
                "Tracks": []
            }
            for ls in lt.segments:
                trd: dict[str, Any] = {
                    "Index": ls.index,
                    "Type": ls.type,
                    "Name": ls.name,
                    "AudioType": ls.audio_type,
                    "LanguageCode": ls.language_code,
                    "Language": ls.language,
                    "Resolution": ls.resolution,
                    "AspectRatio": ls.aspect_ratio,
                }
                t["Tracks"].append(trd)
            disc_json["Titles"].append(t)

        for si in summary_items:
            matches = [t for t in disc_json["Titles"]
                       if t.get("SegmentMap") == si.segment_map
                       and t.get("SourceFile") == si.source_file
                       and t.get("Duration") == si.duration]

            if len(matches) > 1:
                matches = [m for m in matches if m.get("Comment") == si.comment]

            if matches:
                match = matches[0]
                item_ref = {
                    "Title": si.title,
                    "Type": si.item_type,
                    "Description": si.description,
                    "Chapters": [{"Index": c.index, "Title": c.title} for c in si.chapters],
                    "Season": si.season,
                    "Episode": si.episode,
                }
                match["Item"] = item_ref

                for at in si.audio_tracks:
                    audio_tracks = [tr for tr in match["Tracks"] if tr["Type"] == "Audio"]
                    at_index = int(at["Index"])
                    if at_index - 1 < len(audio_tracks):
                        audio_tracks[at_index - 1]["Description"] = at["Name"]

                if si.upc:
                    release_path = Path(release_dir) / "release.json"
                    if release_path.exists():
                        with open(release_path) as f:
                            rel = json.load(f)
                        rel["upc"] = si.upc
                        with open(release_path, "w") as f:
                            json.dump(strip_null(rel), f, indent=2)

        with open(disc_path, "w") as f:
            json.dump(strip_null(disc_json), f, indent=2)
        print(f"  Saved {disc_path}")

    print("Finalize complete!")
