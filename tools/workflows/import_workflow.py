import os
from datetime import datetime, timezone
from typing import Any

from models import (
    Config,
    Disc,
    DiscItemReference,
    Title,
    Track,
)
from parsers import parse_log_file
from services import MakeMkv, TmdbClient
from utils import (
    append_hash_to_log,
    calculate_disc_hash,
    clean_log,
    clean_path,
    create_slug,
    download,
    write_json,
)
from workflows.selectors import (
    find_disc_name,
    select_drive,
    select_format,
    select_item_type,
)


def run_import(cfg: Config) -> None:
    print("\n=== Import Disc ===")

    drive = select_drive(cfg)
    if not drive:
        return

    print(f"Using drive {drive.name} ({drive.letter})...")
    print("Scanning disc...")

    log_path = "/tmp/makemkv_scan.txt"
    mkv = MakeMkv(cfg.makemkvcon_path)
    _ = mkv.info(drive.index, log_path)

    print("Calculating content hash...")
    hash_info = calculate_disc_hash(drive.letter)
    if hash_info:
        print(f"  Content hash: {hash_info.hash}")

    disc_info = parse_log_file(log_path)
    print(f"  Disc: {disc_info.name}")
    print(f"  Type: {disc_info.type}")
    print(f"  Titles: {len(disc_info.titles)}")

    print("\nEnter TMDB ID (e.g. 11 for Star Wars or tmdb:11):")
    tid: str = input(": ").strip()
    if tid.startswith("tmdb:"):
        tid = tid[5:]

    item_type = select_item_type()
    disc_format = select_format()

    tmdb_data: dict[str, Any] | None = None
    imdb_id: str | None = None
    poster_url: str | None = None
    client: TmdbClient | None = None
    title_name = disc_info.name or "Unknown"
    year = datetime.now(timezone.utc).year

    if cfg.tmdb_api_key and tid.isdigit():
        client = TmdbClient(cfg.tmdb_api_key)
        try:
            if item_type == "Series":
                tmdb_data = client.get_series(tid)
                title_name = str(tmdb_data.get("name", title_name))
                year_str = str(tmdb_data.get("first_air_date", ""))
                year = int(year_str[:4]) if year_str else year
            else:
                tmdb_data = client.get_movie(tid)
                title_name = str(tmdb_data.get("title", title_name))
                year_str = str(tmdb_data.get("release_date", ""))
                year = int(year_str[:4]) if year_str else year

            imdb_id = str(tmdb_data.get("imdb_id") or (tmdb_data.get("external_ids", {}) or {}).get("imdb_id") or "")
            tmdb_poster = tmdb_data.get("poster_path")
            poster_url = f'https://image.tmdb.org/t/p/original{tmdb_poster}' if tmdb_poster else None
            print(f"  TMDB: {title_name} ({year})")
        except Exception as e:
            print(f"  TMDB lookup failed: {e}")

    folder_name = f"{title_name} ({year})"
    sub_folder = "series" if item_type == "Series" else "movie"
    base_path = os.path.join(cfg.data_repository_path, sub_folder, folder_name)
    base_path = clean_path(os.path.normpath(base_path))

    print(f"\nTarget: {base_path}")
    if not os.path.exists(base_path):
        os.makedirs(base_path)
        print("  Created directory")

    if poster_url:
        poster_path = os.path.join(base_path, "cover.jpg")
        if not os.path.exists(poster_path):
            try:
                download(poster_url, poster_path)
                print("  Downloaded cover")
            except Exception as e:
                print(f"  Cover download failed: {e}")

    if tmdb_data:
        tmdb_path = os.path.join(base_path, "tmdb.json")
        if not os.path.exists(tmdb_path):
            write_json(tmdb_path, tmdb_data)
            print("  Saved tmdb.json")

    if imdb_id and client:
        imdb_path = os.path.join(base_path, "imdb.json")
        if not os.path.exists(imdb_path):
            try:
                imdb_resp = client.get_imdb_data(imdb_id)
                write_json(imdb_path, imdb_resp)
                print("  Saved imdb.json")
            except Exception:
                pass

    meta: dict[str, Any] = {
        "title": title_name,
        "type": item_type,
        "year": year,
        "dateAdded": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "externalIds": {"tmdb": tid if tid.isdigit() else None, "imdb": imdb_id},
        "slug": create_slug(title_name, year)
    }
    if tmdb_data:
        meta["plot"] = tmdb_data.get("overview", "")
        if item_type == "Series":
            meta["fullTitle"] = tmdb_data.get("original_name", "")
        else:
            meta["fullTitle"] = tmdb_data.get("original_title", "")

    meta_path = os.path.join(base_path, "metadata.json")
    if not os.path.exists(meta_path):
        write_json(meta_path, meta)

    release_folders: list[str] = []
    if os.path.isdir(base_path):
        for d in os.listdir(base_path):
            full = os.path.join(base_path, d)
            if os.path.isdir(full) and d not in ("metadata.json", "tmdb.json", "imdb.json", "cover.jpg"):
                release_folders.append(d)

    has_releases = bool(release_folders)
    release_folder: str | None = None
    release_slug: str | None = None

    if has_releases:
        print("\nExisting releases found:")
        for r in release_folders:
            print(f"  {r}")
        add_new = input("Add new release? (y/n): ").strip().lower() == "y"
        if add_new:
            release_slug = input(f"Release slug (e.g. {year}-blu-ray): ").strip() or f"{year}-blu-ray"
            release_folder = os.path.join(base_path, release_slug)
        else:
            if len(release_folders) == 1:
                release_folder = os.path.join(base_path, release_folders[0])
                release_slug = release_folders[0]
            else:
                print("Select release:")
                for i, r in enumerate(release_folders):
                    print(f"  [{i + 1}] {r}")
                sel = input("Choice: ").strip()
                if sel:
                    idx = int(sel) - 1
                    if 0 <= idx < len(release_folders):
                        release_folder = os.path.join(base_path, release_folders[idx])
                        release_slug = release_folders[idx]
    else:
        release_slug = input(f"Release slug (e.g. {year}-blu-ray): ").strip() or f"{year}-blu-ray"
        release_folder = os.path.join(base_path, release_slug)

    if release_folder and not os.path.exists(release_folder):
        os.makedirs(release_folder)
        release_name: str = input("Release name: ").strip() or (release_slug or "")
        upc = input("UPC (optional): ").strip()
        asin = input("ASIN (optional): ").strip()
        release_date_str = input("Release date (e.g. 2024-01-15): ").strip()

        release_date: str | None = None
        if release_date_str:
            try:
                release_date = datetime.strptime(release_date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
            except ValueError:
                pass

        release_data: dict[str, Any] = {
            "slug": release_slug,
            "title": release_name,
            "year": year,
            "locale": "en-us",
            "regionCode": "1",
            "dateAdded": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        }
        if upc:
            release_data["upc"] = upc
        if asin:
            release_data["asin"] = asin
        if release_date:
            release_data["releaseDate"] = release_date

        write_json(os.path.join(release_folder, "release.json"), release_data)
        print("  Created release.json")

    if not release_folder:
        print("No release folder.")
        return

    disc_name, disc_index = find_disc_name(release_folder)
    disc_title = input(f"Disc name (e.g. Disc 1): ").strip() or disc_name
    disc_slug = input(f"Disc slug: ").strip() or disc_name

    from models import SummaryItem

    summary_items: list[SummaryItem] = []
    print("\nCreating summary file...")
    for title in disc_info.titles:
        print(f"\n  Title #{title.index}: {title.length} {title.display_size} ({title.segment_map})")

        types = ["Skip", "MainMovie", "Episode", "Extra", "Trailer", "DeletedScene"]
        print("    Type?", end="")
        for i, t in enumerate(types):
            print(f" {i}={t}", end="")
        print()

        type_choice = input("      choice (default 0=Skip): ").strip()
        if type_choice == "0" or not type_choice:
            continue

        item_type_name = types[int(type_choice)] if type_choice.isdigit() and 0 <= int(type_choice) < len(types) else "Episode"

        from models import Chapter as ChapterModel

        item = SummaryItem(
            title=title.comment or f"Title {title.index}",
            source_file=title.playlist or "",
            segment_map=title.segment_map or "",
            duration=title.length or "",
            size=title.display_size or "",
            comment=title.comment or "",
            item_type=item_type_name,
        )

        item.season = input(f"      Season (default 1): ").strip() or "1"
        ep = input(f"      Episode: ").strip()
        if ep:
            item.episode = ep

        print("  Chapters? (y/n): ", end="")
        if input().strip().lower() == "y":
            n = input("    Number of chapters: ").strip()
            if n.isdigit():
                for ci in range(1, int(n) + 1):
                    ct = input(f"    Chapter {ci} title: ").strip()
                    item.chapters.append(ChapterModel(index=ci, title=ct))

        print("  Audio tracks? (y/n): ", end="")
        if input().strip().lower() == "y":
            for ai, seg in enumerate(title.segments):
                if seg.type == "Audio":
                    an = input(f"    Audio track {ai + 1} name: ").strip()
                    if an:
                        item.audio_tracks.append({"index": ai + 1, "name": an})

        summary_items.append(item)

    summary_path = os.path.join(release_folder, f"{disc_name}-summary.txt")
    with open(summary_path, "w") as f:
        for item in summary_items:
            si = item
            if si.title:
                _ = f.write(f"Name: {si.title}\n")
            if si.item_type:
                _ = f.write(f"Type: {si.item_type}\n")
            if si.season:
                _ = f.write(f"Season: {si.season}\n")
            if si.episode:
                _ = f.write(f"Episode: {si.episode}\n")
            if si.source_file:
                _ = f.write(f"Source file name: {si.source_file}\n")
            if si.duration:
                _ = f.write(f"Duration: {si.duration}\n")
            if si.size:
                _ = f.write(f"Size: {si.size}\n")
            if si.segment_map:
                _ = f.write(f"Segment map: {si.segment_map}\n")
            if si.description:
                _ = f.write(f"Description: {si.description}\n")
            if si.chapters:
                _ = f.write("Chapters:\n")
                for c in si.chapters:
                    ch = c
                    _ = f.write(f"-{ch.title}\n")
            for at in si.audio_tracks:
                at_dict = at
                _ = f.write(f"AudioTrack[{at_dict['index']}]: {at_dict['name']}\n")
            if si.comment:
                _ = f.write(f"File name: {si.comment}\n")
            _ = f.write("---\n")

    print(f"  Saved {summary_path}")

    disc = Disc(
        index=disc_index,
        slug=disc_slug,
        name=disc_title,
        format=disc_format,
        content_hash=hash_info.hash if hash_info else None,
        titles=[]
    )

    print("\nFinalizing titles from log...")
    disc.titles = []
    for lt in disc_info.titles:
        t = Title(
            index=lt.index,
            source_file=lt.playlist,
            segment_map=lt.segment_map,
            duration=lt.length,
            size=lt.size,
            display_size=lt.display_size,
            comment=lt.comment,
            tracks=[]
        )
        for ls in lt.segments:
            track = Track(
                index=ls.index,
                type=ls.type,
                name=ls.name,
                audio_type=ls.audio_type,
                language_code=ls.language_code,
                language=ls.language,
                resolution=ls.resolution,
                aspect_ratio=ls.aspect_ratio,
            )
            t.tracks.append(track)
        disc.titles.append(t)

    from models import Chapter as ChapterModel

    for si in summary_items:
        s_item = si
        matches = [t for t in disc.titles
                   if t.segment_map == s_item.segment_map
                   and t.source_file == s_item.source_file
                   and t.duration == s_item.duration]

        if len(matches) > 1:
            matches = [m for m in matches if m.comment == s_item.comment]

        if matches:
            match = matches[0]
            ref = DiscItemReference(
                title=s_item.title,
                type=s_item.item_type,
                description=s_item.description,
                chapters=[ChapterModel(index=c.index, title=c.title) for c in s_item.chapters],
                season=s_item.season,
                episode=s_item.episode,
            )
            match.item = ref

            for at in s_item.audio_tracks:
                at_dict = at
                audio_tracks = [tr for tr in match.tracks if tr.type == "Audio"]
                at_index = int(at_dict["index"])
                if at_index - 1 < len(audio_tracks):
                    audio_tracks[at_index - 1].description = str(at_dict["name"])

    disc_json: dict[str, Any] = {
        "index": disc.index,
        "slug": disc.slug,
        "name": disc.name,
        "format": disc.format,
        "contentHash": disc.content_hash,
        "titles": []
    }

    for t in disc.titles:
        td: dict[str, Any] = {
            "index": t.index,
            "sourceFile": t.source_file,
            "segmentMap": t.segment_map,
            "duration": t.duration,
            "size": t.size,
            "displaySize": t.display_size,
            "comment": t.comment,
            "tracks": []
        }
        for tr in t.tracks:
            trd: dict[str, Any] = {
                "index": tr.index,
                "type": tr.type,
                "name": tr.name,
                "audioType": tr.audio_type,
                "languageCode": tr.language_code,
                "language": tr.language,
                "resolution": tr.resolution,
                "aspectRatio": tr.aspect_ratio,
            }
            if tr.description:
                trd["description"] = tr.description
            td["tracks"].append(trd)
        if t.item:
            td["item"] = {
                "title": t.item.title,
                "type": t.item.type,
                "description": t.item.description,
                "chapters": t.item.chapters,
                "season": t.item.season,
                "episode": t.item.episode,
            }
        disc_json["titles"].append(td)

    disc_path = os.path.join(release_folder, f"{disc_name}.json")
    write_json(disc_path, disc_json)
    print(f"  Saved {disc_path}")

    print("\n  Run makemkvcon to capture log? (y/n): ", end="")
    if input().strip().lower() == "y":
        out_path = os.path.join(release_folder, f"{disc_name}.txt")
        mkv = MakeMkv(cfg.makemkvcon_path)
        _ = mkv.info(drive.index, out_path)
        clean_log(out_path)
        if hash_info:
            append_hash_to_log(out_path, hash_info)
        print(f"  Saved {out_path}")

    print("\nImport complete!")
