import os
from pathlib import Path
from typing import Any

from parsers.log_parser import parse_log_file
from utils.io import read_json, write_json
from utils.path import create_slug, get_sort_title


class TestMetadataJsonStructure:
    def test_metadata_json_has_required_fields(self, expected_metadata_json: dict[str, Any]) -> None:
        required_fields = [
            "Title",
            "FullTitle",
            "SortTitle",
            "Slug",
            "Type",
            "Year",
            "ImageUrl",
            "ExternalIds",
            "DateAdded"
        ]

        for field in required_fields:
            assert field in expected_metadata_json, f"Missing field: {field}"

    def test_metadata_json_type_is_movie(self, expected_metadata_json: dict[str, Any]) -> None:
        assert expected_metadata_json["Type"] == "Movie"

    def test_metadata_json_has_external_ids(self, expected_metadata_json: dict[str, Any]) -> None:
        external_ids = expected_metadata_json["ExternalIds"]
        assert "Tmdb" in external_ids or "Imdb" in external_ids

    def test_slug_format(self, expected_metadata_json: dict[str, Any]) -> None:
        slug = expected_metadata_json["Slug"]
        assert slug == "the-matrix-1999"
        assert " " not in slug
        assert slug.islower() or slug.replace("-", "").isalnum()

    def test_sort_title_format(self, expected_metadata_json: dict[str, Any]) -> None:
        sort_title = expected_metadata_json["SortTitle"]
        assert "The" not in sort_title[:5] or "," in sort_title


class TestDiscJsonStructure:
    def test_disc_json_has_required_fields(self, expected_disc_json: dict[str, Any]) -> None:
        required_fields = ["Index", "Slug", "Name", "Format", "ContentHash", "Titles"]
        for field in required_fields:
            assert field in expected_disc_json, f"Missing field: {field}"

    def test_disc_index_is_positive_int(self, expected_disc_json: dict[str, Any]) -> None:
        assert isinstance(expected_disc_json["Index"], int)
        assert expected_disc_json["Index"] >= 1

    def test_titles_is_list(self, expected_disc_json: dict[str, Any]) -> None:
        titles_list: list[dict[str, Any]] = expected_disc_json["Titles"]
        assert isinstance(titles_list, list)
        assert len(titles_list) > 0

    def test_title_has_required_fields(self, expected_disc_json: dict[str, Any]) -> None:
        for title in expected_disc_json["Titles"]:
            required = ["Index", "SourceFile", "SegmentMap", "Duration", "Size", "DisplaySize"]
            for field in required:
                assert field in title, f"Title missing field: {field}"

    def test_title_has_tracks_array(self, expected_disc_json: dict[str, Any]) -> None:
        for title in expected_disc_json["Titles"]:
            assert "Tracks" in title
            assert isinstance(title["Tracks"], list)

    def test_track_has_required_fields(self, expected_disc_json: dict[str, Any]) -> None:
        for title in expected_disc_json["Titles"]:
            for track in title["Tracks"]:
                assert "Index" in track
                assert "Type" in track
                assert "Name" in track

    def test_track_types_are_valid(self, expected_disc_json: dict[str, Any]) -> None:
        valid_types = ["Video", "Audio", "Subtitles"]
        for title in expected_disc_json["Titles"]:
            for track in title["Tracks"]:
                assert track["Type"] in valid_types, f"Invalid track type: {track['Type']}"

    def test_main_movie_has_item_reference(self, expected_disc_json: dict[str, Any]) -> None:
        main_movie = next(
            (t for t in expected_disc_json["Titles"] if t.get("Item", {}).get("Type") == "MainMovie"),
            None
        )
        assert main_movie is not None, "No MainMovie found in titles"


class TestSummaryTxtFormat:
    def test_summary_contains_name(self, expected_summary_txt: str) -> None:
        assert "Name:" in expected_summary_txt

    def test_summary_contains_duration(self, expected_summary_txt: str) -> None:
        assert "Duration:" in expected_summary_txt

    def test_summary_contains_type(self, expected_summary_txt: str) -> None:
        assert "Type:" in expected_summary_txt

    def test_summary_contains_source_file(self, expected_summary_txt: str) -> None:
        assert "Source file name:" in expected_summary_txt


class TestOutputGeneration:
    def test_generate_metadata_json(self, temp_output_dir: Path, expected_metadata_json: dict[str, Any]) -> None:
        path = temp_output_dir / "metadata.json"

        generated = {
            "Title": expected_metadata_json["Title"],
            "FullTitle": expected_metadata_json["FullTitle"],
            "SortTitle": expected_metadata_json["SortTitle"],
            "Slug": expected_metadata_json["Slug"],
            "Type": expected_metadata_json["Type"],
            "Year": expected_metadata_json["Year"],
            "DateAdded": "2024-07-15"
        }

        write_json(str(path), generated)
        result = read_json(str(path))

        assert result["Title"] == "The Matrix"
        assert result["Slug"] == "the-matrix-1999"
        assert result["Type"] == "Movie"

    def test_generate_disc_json_from_parsed_log(self, temp_output_dir: Path, sample_log_path: str) -> None:
        disc_info = parse_log_file(sample_log_path)

        disc_json: dict[str, Any] = {
            "Index": 1,
            "Slug": "blu-ray",
            "Name": "Blu-ray",
            "Format": "Blu-Ray",
            "ContentHash": "DD9D27D60067857C442FB33AB8086CEC",
            "Titles": []  # type: ignore[list-item]
        }

        for lt in disc_info.titles:
            if lt.length == "2:16:20":
                title_data: dict[str, Any] = {
                    "Index": lt.index,
                    "SourceFile": lt.playlist,
                    "SegmentMap": lt.segment_map,
                    "Duration": lt.length,
                    "Size": lt.size,
                    "DisplaySize": lt.display_size,
                    "Tracks": []  # type: ignore[list-item]
                }
                for seg in lt.segments:
                    if seg.type == "Video":
                        tracks: list[dict[str, Any]] = title_data["Tracks"]  # type: ignore[index]
                        tracks.append({
                            "Index": seg.index,
                            "Name": seg.name,
                            "Type": seg.type,
                            "Resolution": seg.resolution,
                            "AspectRatio": seg.aspect_ratio
                        })
                titles: list[dict[str, Any]] = disc_json["Titles"]  # type: ignore[index]
                titles.append(title_data)
                break

        path = temp_output_dir / "disc01.json"
        disc_for_write: dict[str, Any] = {"Index": disc_json["Index"], "Name": disc_json["Name"], "Titles": disc_json["Titles"]}
        write_json(str(path), disc_for_write)
        result = read_json(str(path))

        assert result["Index"] == 1
        assert result["Name"] == "Blu-ray"
        assert len(result["Titles"]) == 1
        assert result["Titles"][0]["Duration"] == "2:16:20"
        assert len(result["Titles"][0]["Tracks"]) >= 1


class TestPosterDownload:
    def test_poster_url_construction(self) -> None:
        poster_path = "/abc123.jpg"
        expected_url = "https://image.tmdb.org/t/p/original/abc123.jpg"
        constructed_url = f"https://image.tmdb.org/t/p/original{poster_path}"
        assert constructed_url == expected_url

    def test_cover_path_format(self) -> None:
        base_path = "/data/movie/The Matrix (1999)"
        cover_path = os.path.join(base_path, "cover.jpg")
        assert cover_path.endswith("cover.jpg")


class TestSlugGeneration:
    def test_matrix_slug(self) -> None:
        assert create_slug("The Matrix", 1999) == "the-matrix-1999"

    def test_office_slug(self) -> None:
        assert create_slug("The Office", 2005) == "the-office-2005"

    def test_star_wars_slug(self) -> None:
        assert create_slug("Star Wars", 1977) == "star-wars-1977"

    def test_sort_title_with_the_prefix(self) -> None:
        assert get_sort_title("The Matrix") == "Matrix, The"
        assert get_sort_title("The Office") == "Office, The"


class TestEndToEndOutputStructure:
    def test_release_folder_structure(self, temp_output_dir: Path) -> None:
        base = temp_output_dir / "The Matrix (1999)"
        release = base / "2018-the-matrix-trilogy-4k"

        base.mkdir(parents=True, exist_ok=True)
        release.mkdir(parents=True, exist_ok=True)

        _ = (base / "cover.jpg").write_text("fake image data")
        _ = write_json(str(base / "metadata.json"), {"Title": "The Matrix"})
        _ = write_json(str(base / "tmdb.json"), {"id": 603})
        _ = write_json(str(base / "imdb.json"), {"imdb_id": "tt0133093"})
        _ = write_json(str(release / "release.json"), {"Slug": "2018-the-matrix-trilogy-4k"})
        _ = write_json(str(release / "disc01.json"), {"Index": 1})
        _ = (release / "disc01.txt").write_text("log content")
        _ = (release / "disc01-summary.txt").write_text("summary content")

        assert (base / "cover.jpg").exists()
        assert (base / "metadata.json").exists()
        assert (base / "tmdb.json").exists()
        assert (base / "imdb.json").exists()
        assert (release / "release.json").exists()
        assert (release / "disc01.json").exists()
        assert (release / "disc01.txt").exists()
        assert (release / "disc01-summary.txt").exists()

    def test_json_files_are_valid(
        self, temp_output_dir: Path, expected_metadata_json: dict[str, Any], expected_disc_json: dict[str, Any]
    ) -> None:
        metadata_path = temp_output_dir / "metadata.json"
        disc_path = temp_output_dir / "disc01.json"

        write_json(str(metadata_path), expected_metadata_json)
        write_json(str(disc_path), expected_disc_json)

        loaded_metadata = read_json(str(metadata_path))
        loaded_disc = read_json(str(disc_path))

        assert loaded_metadata == expected_metadata_json
        assert loaded_disc == expected_disc_json

    def test_disc_json_titles_have_tracks(self, expected_disc_json: dict[str, Any]) -> None:
        for title in expected_disc_json["Titles"]:
            assert len(title["Tracks"]) > 0
            for track in title["Tracks"]:
                assert "Type" in track
                assert track["Type"] in ["Video", "Audio", "Subtitles"]
