from parsers.log_parser import parse_csv_line, parse_log_file, parse_summary_file


class TestParseLogFile:
    def test_parses_real_log_file(self, sample_log_path: str) -> None:
        disc_info = parse_log_file(sample_log_path)

        assert disc_info.name == "The Matrix"
        assert disc_info.type == "Blu-ray disc"
        assert len(disc_info.titles) > 0

    def test_finds_main_movie_title(self, sample_log_path: str) -> None:
        disc_info = parse_log_file(sample_log_path)

        main_title = next(
            (t for t in disc_info.titles if t.length == "2:16:20"),
            None
        )
        assert main_title is not None
        assert main_title.index == 8
        assert main_title.playlist == "00822.mpls"

    def test_extracts_video_track(self, sample_log_path: str) -> None:
        disc_info = parse_log_file(sample_log_path)

        main_title = next(
            (t for t in disc_info.titles if t.length == "2:16:20"),
            None
        )
        assert main_title is not None

        video_segments = [s for s in main_title.segments if s.type == "Video"]
        assert len(video_segments) > 0
        assert video_segments[0].name == "Mpeg4 AVC High@L4.1"

    def test_extracts_audio_tracks(self, sample_log_path: str) -> None:
        disc_info = parse_log_file(sample_log_path)

        main_title = next(
            (t for t in disc_info.titles if t.length == "2:16:20"),
            None
        )
        assert main_title is not None

        audio_segments = [s for s in main_title.segments if s.type == "Audio"]
        assert len(audio_segments) >= 2

        truehd_track = next(
            (s for s in audio_segments if "TrueHD" in (s.name or "")),
            None
        )
        assert truehd_track is not None

    def test_extracts_subtitle_tracks(self, sample_log_path: str) -> None:
        disc_info = parse_log_file(sample_log_path)

        main_title = next(
            (t for t in disc_info.titles if t.length == "2:16:20"),
            None
        )
        assert main_title is not None

        subtitle_segments = [s for s in main_title.segments if s.type == "Subtitles"]
        assert len(subtitle_segments) > 0

    def test_title_has_segment_map(self, sample_log_path: str) -> None:
        disc_info = parse_log_file(sample_log_path)

        main_title = next(
            (t for t in disc_info.titles if t.length == "2:16:20"),
            None
        )
        assert main_title is not None
        assert main_title.segment_map == "1162"

    def test_title_has_chapter_count(self, sample_log_path: str) -> None:
        disc_info = parse_log_file(sample_log_path)

        main_title = next(
            (t for t in disc_info.titles if t.length == "2:16:20"),
            None
        )
        assert main_title is not None
        assert main_title.chapter_count == 38

    def test_title_has_size_info(self, sample_log_path: str) -> None:
        disc_info = parse_log_file(sample_log_path)

        main_title = next(
            (t for t in disc_info.titles if t.length == "2:16:20"),
            None
        )
        assert main_title is not None
        assert main_title.display_size == "36.8 GB"
        assert main_title.size == 39531675648

    def test_finds_short_title(self, sample_log_path: str) -> None:
        disc_info = parse_log_file(sample_log_path)

        short_title = next(
            (t for t in disc_info.titles if t.length == "0:00:29"),
            None
        )
        assert short_title is not None
        assert short_title.index == 0


class TestParseCsvLine:
    def test_parses_simple_line(self) -> None:
        line = "PREFIX:value1,value2"
        result = parse_csv_line(line)
        assert result == ["PREFIX", "value1", "value2"]

    def test_parses_quoted_values(self) -> None:
        line = 'PREFIX:"quoted,value",normal'
        result = parse_csv_line(line)
        assert result == ["PREFIX", "quoted,value", "normal"]

    def test_parses_empty_values(self) -> None:
        line = "PREFIX:val1,,val3,"
        result = parse_csv_line(line)
        assert result == ["PREFIX", "val1", "", "val3", ""]

    def test_handles_nested_colons(self) -> None:
        line = 'PREFIX:1,2,"text:with:colons"'
        result = parse_csv_line(line)
        assert result == ["PREFIX", "1", "2", "text:with:colons"]


class TestParseSummaryFile:
    def test_parses_simple_summary(self) -> None:
        content = """Name: The Matrix
Duration: 2:16:20
Size: 36.8 GB
Type: MainMovie
File name: The Matrix.mkv
---"""

        items = parse_summary_file(content)
        assert len(items) == 1
        assert items[0].title == "The Matrix"
        assert items[0].duration == "2:16:20"
        assert items[0].item_type == "MainMovie"

    def test_parses_multiple_items(self) -> None:
        content = """Name: Movie One
Duration: 1:30:00
Type: MainMovie
File name: movie1.mkv
---
Name: Movie Two
Duration: 1:45:00
Type: MainMovie
File name: movie2.mkv"""

        items = parse_summary_file(content)
        assert len(items) == 2
        assert items[0].title == "Movie One"
        assert items[1].title == "Movie Two"

    def test_parses_episode_format(self) -> None:
        content = """Name: Pilot
Type: Episode
Season: 1
Episode: 1
Duration: 0:23:25
File name: pilot.mkv
---
Name: Second Episode
Type: Episode
Season: 1
Episode: 2
File name: episode2.mkv"""

        items = parse_summary_file(content)
        assert len(items) == 2
        assert items[0].season == "1"
        assert items[0].episode == "1"
        assert items[1].episode == "2"

    def test_parses_chapters(self) -> None:
        content = """Name: Movie
Type: MainMovie
Chapters:
- Chapter One
- Chapter Two
- Chapter Three
File name: movie.mkv"""

        items = parse_summary_file(content)
        assert len(items) == 1
        assert len(items[0].chapters) == 3
        assert items[0].chapters[0].title == "Chapter One"
