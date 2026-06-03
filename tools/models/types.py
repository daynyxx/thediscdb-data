from dataclasses import dataclass, field


@dataclass
class DriveConfig:
    index: int
    letter: str
    name: str


@dataclass
class Config:
    data_repository_path: str = ""
    tmdb_api_key: str = ""
    makemkvcon_path: str = "/usr/bin/makemkv"
    drives: list[DriveConfig] = field(default_factory=list)


@dataclass
class Track:
    index: int = 0
    name: str | None = None
    type: str | None = None
    resolution: str | None = None
    aspect_ratio: str | None = None
    audio_type: str | None = None
    language_code: str | None = None
    language: str | None = None
    description: str | None = None


@dataclass
class Chapter:
    index: int = 0
    title: str | None = None


@dataclass
class DiscItemReference:
    title: str | None = None
    type: str | None = None
    description: str | None = None
    chapters: list[Chapter] = field(default_factory=list)
    season: str | None = None
    episode: str | None = None


@dataclass
class Title:
    index: int = 0
    comment: str | None = None
    source_file: str | None = None
    segment_map: str | None = None
    duration: str | None = None
    size: int = 0
    display_size: str | None = None
    item: DiscItemReference | None = None
    tracks: list[Track] = field(default_factory=list)


@dataclass
class Disc:
    index: int = 0
    slug: str | None = None
    name: str | None = None
    format: str | None = None
    content_hash: str | None = None
    titles: list[Title] = field(default_factory=list)


@dataclass
class HashFileInfo:
    index: int = 0
    name: str = ""
    creation_time: str = ""
    size: int = 0


@dataclass
class HashInfo:
    hash: str | None = None
    files: list[HashFileInfo] = field(default_factory=list)


@dataclass
class LogSegment:
    index: int = 0
    type: str | None = None
    name: str | None = None
    audio_type: str | None = None
    language_code: str | None = None
    language: str | None = None
    resolution: str | None = None
    aspect_ratio: str | None = None


@dataclass
class LogTitle:
    index: int = 0
    chapter_count: int = 0
    length: str | None = None
    display_size: str | None = None
    size: int = 0
    playlist: str | None = None
    segment_map: str | None = None
    comment: str | None = None
    java_comment: str | None = None
    segments: list[LogSegment] = field(default_factory=list)


@dataclass
class DiscInfo:
    name: str | None = None
    type: str | None = None
    language_code: str | None = None
    language: str | None = None
    titles: list[LogTitle] = field(default_factory=list)
    hash_info: list[HashFileInfo] = field(default_factory=list)


@dataclass
class SummaryItem:
    title: str | None = None
    source_file: str | None = None
    segment_map: str | None = None
    duration: str | None = None
    size: str | None = None
    comment: str | None = None
    item_type: str | None = None
    season: str | None = None
    episode: str | None = None
    year: int = 0
    upc: str | None = None
    description: str | None = None
    chapters: list[Chapter] = field(default_factory=list)
    audio_tracks: list[dict[str, int | str]] = field(default_factory=list)
