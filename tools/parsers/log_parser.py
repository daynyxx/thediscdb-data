import re

from models import Chapter, DiscInfo, HashFileInfo, LogSegment, LogTitle, SummaryItem


def parse_log_file(path: str) -> DiscInfo:
    disc_info = DiscInfo()
    titles = []
    current_title = None
    current_segment = None

    with open(path) as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        prefix = line.split(":")[0] if ":" in line else ""

        match prefix:
            case "" | "TCOUNT" | "MSG" | "DRV" | "#":
                i += 1
                continue
            case "CINFO":
                parts = parse_csv_line(line)
                code = int(parts[1])
                subcode = int(parts[2])
                msg = parts[3] if len(parts) > 3 else ""
                match code:
                    case 1:
                        disc_info.type = msg
                    case 2:
                        disc_info.name = msg
                    case 28:
                        disc_info.language_code = msg
                    case 29:
                        disc_info.language = msg
                    case _:
                        pass
            case "TINFO":
                parts = parse_csv_line(line)
                tidx = int(parts[1])
                code = int(parts[2])
                subcode = int(parts[3])
                msg = parts[4] if len(parts) > 4 else ""

                if current_title is not None and current_title.index != tidx:
                    if current_segment is not None:
                        current_title.segments.append(current_segment)
                        current_segment = None
                    titles.append(current_title)
                    current_segment = None

                if current_title is None or current_title.index != tidx:
                    current_title = LogTitle(index=tidx)

                if current_segment is not None:
                    current_title.segments.append(current_segment)
                    current_segment = None

                match code:
                    case 8:
                        current_title.chapter_count = int(msg) if msg else 0
                    case 9:
                        current_title.length = msg
                    case 10:
                        current_title.display_size = msg
                    case 11:
                        current_title.size = int(msg) if msg else 0
                    case 16 | 24:
                        current_title.playlist = msg
                    case 26:
                        current_title.segment_map = msg
                    case 27:
                        current_title.comment = msg
                    case 49:
                        current_title.java_comment = msg
                    case _:
                        pass
            case "SINFO":
                parts = parse_csv_line(line)
                tidx = int(parts[1])
                seg_idx = int(parts[2])
                code = int(parts[3])
                subcode = int(parts[4])
                msg = parts[5] if len(parts) > 5 else ""

                if current_title is not None and current_title.index != tidx:
                    if current_segment is not None:
                        current_title.segments.append(current_segment)
                        current_segment = None
                    titles.append(current_title)
                    current_segment = None

                if current_title is None or current_title.index != tidx:
                    current_title = LogTitle(index=tidx)

                if code == 1:
                    if current_segment is not None:
                        current_title.segments.append(current_segment)
                    current_segment = LogSegment(index=seg_idx, type=msg)
                elif current_segment is not None:
                    match code:
                        case 2:
                            current_segment.audio_type = msg
                        case 3:
                            current_segment.language_code = msg
                        case 4:
                            current_segment.language = msg
                        case 7:
                            current_segment.name = msg
                        case 19:
                            current_segment.resolution = msg
                        case 20:
                            current_segment.aspect_ratio = msg
                        case _:
                            pass
            case "HSH":
                parts = parse_csv_line(line)
                if len(parts) >= 5:
                    disc_info.hash_info.append(HashFileInfo(
                        index=int(parts[1]),
                        name=parts[2],
                        creation_time=parts[3],
                        size=int(parts[4]) if parts[4] else 0
                    ))
            case _:
                pass

        i += 1

    if current_segment is not None and current_title is not None:
        current_title.segments.append(current_segment)
        current_segment = None
    if current_title is not None:
        titles.append(current_title)

    disc_info.titles = titles
    return disc_info


def parse_csv_line(line: str) -> list[str]:
    result: list[str] = []
    current = ""
    in_quotes = False
    if ":" in line:
        colon = line.index(":")
        prefix = line[:colon]
        result.append(prefix)
        line = line[colon + 1:]
    for ch in line:
        if ch == '"':
            in_quotes = not in_quotes
        elif ch == ',' and not in_quotes:
            result.append(current.strip('"'))
            current = ""
        else:
            current += ch
    if current or line.endswith(','):
        result.append(current.strip('"'))
    return result


def parse_summary_file(content: str) -> list[SummaryItem]:
    items = []
    current = None
    collecting_chapters = False
    chapter_num = 1

    for line in content.split("\n"):
        line = line.strip()
        if not line:
            continue

        colon_pos = line.find(":")
        if colon_pos > 0:
            key = line[:colon_pos].strip()
            val = line[colon_pos + 1:].strip()

            match key:
                case "Name":
                    if current and current.title is not None:
                        items.append(current)
                        current = None
                    current = SummaryItem(title=val)
                    collecting_chapters = False
                    chapter_num = 1
                case _:
                    if current is None:
                        continue
                    match key:
                        case "Source file name" | "Source title ID":
                            current.source_file = val
                        case "Duration":
                            collecting_chapters = False
                            chapter_num = 1
                            current.duration = val
                        case "Size":
                            current.size = val
                        case "Segment map":
                            current.segment_map = val
                        case "Type":
                            current.item_type = val
                        case "Season":
                            current.season = val
                        case "Episode":
                            current.episode = val
                        case "Description":
                            current.description = val
                        case "Upc":
                            current.upc = val
                        case "Chapters":
                            collecting_chapters = True
                        case "File name":
                            collecting_chapters = False
                            chapter_num = 1
                            if not current.comment:
                                current.comment = val
                        case _:
                            m = re.search(r'AudioTrack\[(\d+)\]:\s*(.+)', line, re.IGNORECASE)
                            if m:
                                current.audio_tracks.append({"index": int(m.group(1)), "name": m.group(2).strip()})
        else:
            if line.startswith("---"):
                if current and current.title:
                    items.append(current)
                    current = None
            elif collecting_chapters and line.startswith("-"):
                if current is not None:
                    current.chapters.append(Chapter(index=chapter_num, title=line[1:].strip()))
                    chapter_num += 1

    if current and current.title:
        items.append(current)

    return items
