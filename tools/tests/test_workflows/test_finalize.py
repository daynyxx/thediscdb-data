from typing import Any

from parsers.log_parser import parse_log_file, parse_summary_file
from workflows.finalize import strip_null


def _run_finalize_logic(log_path: str, summary_content: str) -> dict[str, Any]:
    disc_info = parse_log_file(log_path)
    summary_items = parse_summary_file(summary_content)

    disc_json: dict[str, Any] = {"Titles": []}

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

    return strip_null(disc_json)


def _titles_functionally_equal(a: dict[str, Any], b: dict[str, Any]) -> tuple[bool, str]:
    keys_to_compare = [
        "SourceFile", "SegmentMap", "Duration", "Size", "DisplaySize", "Index", "Comment"
    ]
    for key in keys_to_compare:
        if a.get(key) != b.get(key):
            return False, f"Title {a.get('Index')}: {key} mismatch"

    a_tracks = sorted(a.get("Tracks", []), key=lambda t: t.get("Index", 0))
    b_tracks = sorted(b.get("Tracks", []), key=lambda t: t.get("Index", 0))
    if len(a_tracks) != len(b_tracks):
        return False, f"Title {a.get('Index')}: track count mismatch"

    for i, (a_t, b_t) in enumerate(zip(a_tracks, b_tracks)):
        track_keys = ["Index", "Type", "Name", "AudioType", "LanguageCode", "Language",
                      "Resolution", "AspectRatio"]
        for key in track_keys:
            if a_t.get(key) != b_t.get(key):
                return False, f"Title {a.get('Index')} Track {i}: {key} mismatch"

    if "Item" in a or "Item" in b:
        a_item = a.get("Item", {})
        b_item = b.get("Item", {})
        item_keys = ["Title", "Type", "Season", "Episode", "Description"]
        for key in item_keys:
            if key in ["Season", "Episode"] and key in a_item and key in b_item:
                if str(a_item[key]) != str(b_item[key]):
                    return False, f"Title {a.get('Index')}: Item.{key} mismatch"
            elif a_item.get(key) != b_item.get(key):
                return False, f"Title {a.get('Index')}: Item.{key} mismatch"

        a_chapters = a_item.get("Chapters", [])
        b_chapters = b_item.get("Chapters", [])
        if len(a_chapters) == len(b_chapters) == 0:
            pass
        elif len(a_chapters) != len(b_chapters):
            return False, f"Title {a.get('Index')}: chapters count mismatch"
        else:
            for ca, cb in zip(a_chapters, b_chapters):
                if ca.get("Index") != cb.get("Index"):
                    return False, f"Title {a.get('Index')}: chapter index mismatch"
                if ca.get("Title") != cb.get("Title"):
                    return False, f"Title {a.get('Index')}: chapter title mismatch"

    return True, ""


def _disc_functionally_equivalent(actual: dict[str, Any], expected: dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []

    if "Titles" not in expected:
        if "Titles" not in actual:
            return True, []
        errors.append("Expected no Titles but found some")
        return False, errors

    actual_by_key = {
        (t.get("SegmentMap"), t.get("SourceFile"), t.get("Duration")): t
        for t in actual.get("Titles", [])
    }
    expected_by_key = {
        (t.get("SegmentMap"), t.get("SourceFile"), t.get("Duration")): t
        for t in expected.get("Titles", [])
    }

    for key, expected_title in expected_by_key.items():
        if key not in actual_by_key:
            errors.append(f"Expected title with key {key} not found in actual")
            continue

        actual_title = actual_by_key[key]
        match, error = _titles_functionally_equal(actual_title, expected_title)
        if not match:
            errors.append(error)

    return len(errors) == 0, errors


class TestFinalizeMovie:
    def test_finalize_produces_mainmovie_item_reference(
        self, movie_log_path: str, movie_summary_content: str,         expected_movie_disc_json: dict[str, Any]
    ) -> None:
        result = _run_finalize_logic(movie_log_path, movie_summary_content)

        mainmovie = next(
            (t for t in result.get("Titles", []) if t.get("Item", {}).get("Type") == "MainMovie"),
 None
        )
        assert mainmovie is not None, "No MainMovie Item reference found"

        expected_mainmovie = next(
            (t for t in expected_movie_disc_json.get("Titles", []) if t.get("Item", {}).get("Type") == "MainMovie"),
            None
        )
        assert expected_mainmovie is not None, "Expected MainMovie not found in expected"

        assert mainmovie.get("SourceFile") == expected_mainmovie.get("SourceFile")
        assert mainmovie.get("SegmentMap") == expected_mainmovie.get("SegmentMap")
        assert mainmovie.get("Item", {}).get("Title") == expected_mainmovie.get("Item", {}).get("Title")

    def test_finalize_produces_extra_item_references(
        self, movie_log_path: str, movie_summary_content: str,         expected_movie_disc_json: dict[str, Any]
    ) -> None:
        result = _run_finalize_logic(movie_log_path, movie_summary_content)

        expected_extras = [
            t for t in expected_movie_disc_json.get("Titles", []) if t.get("Item", {}).get("Type") == "Extra"
        ]

        assert len(expected_extras) > 0, "No Extras found in expected JSON"

        for expected_extra in expected_extras:
            key = (
                expected_extra.get("SegmentMap"),
                expected_extra.get("SourceFile"),
                expected_extra.get("Duration")
            )
            actual_title = next(
                (t for t in result.get("Titles", []) if
                 t.get("SegmentMap") == key[0] and t.get("SourceFile") == key[1] and t.get("Duration") == key[2]),
                None
            )
            assert actual_title is not None, f"Expected title not found for {expected_extra.get('Item', {}).get('Title')}"
            assert actual_title.get("Item", {}).get("Type") == "Extra"

    def test_finalize_output_functionally_equivalent_to_expected(
        self, movie_log_path: str, movie_summary_content: str,         expected_movie_disc_json: dict[str, Any]
    ) -> None:
        result = _run_finalize_logic(movie_log_path, movie_summary_content)

        is_equivalent, errors = _disc_functionally_equivalent(result, expected_movie_disc_json)

        assert is_equivalent, f"Finalize output not functionally equivalent:\n  " + "\n  ".join(errors)

    def test_finalize_mainmovie_has_chapters(self, movie_log_path: str, movie_summary_content: str) -> None:
        result = _run_finalize_logic(movie_log_path, movie_summary_content)

        mainmovie = next(
            (t for t in result.get("Titles", []) if t.get("Item", {}).get("Type") == "MainMovie"),
            None
        )
        assert mainmovie is not None
        assert "Chapters" in mainmovie.get("Item", {})
        assert len(mainmovie.get("Item", {}).get("Chapters", [])) > 0


class TestFinalizeTV:
    def test_finalize_produces_episode_item_references(
        self, tv_log_path: str, tv_summary_content: str,         expected_tv_disc_json: dict[str, Any]
    ) -> None:
        result = _run_finalize_logic(tv_log_path, tv_summary_content)

        expected_episodes = [
            t for t in expected_tv_disc_json.get("Titles", []) if t.get("Item", {}).get("Type") == "Episode"
        ]

        assert len(expected_episodes) > 0, "No Episodes found in expected JSON"

        for expected_ep in expected_episodes:
            key = (
                expected_ep.get("SegmentMap"),
                expected_ep.get("SourceFile"),
                expected_ep.get("Duration")
            )
            actual_title = next(
                (t for t in result.get("Titles", []) if
                 t.get("SegmentMap") == key[0] and t.get("SourceFile") == key[1] and t.get("Duration") == key[2]),
                None
            )
            assert actual_title is not None, f"Expected episode not found"
            assert actual_title.get("Item", {}).get("Type") == "Episode"
            assert actual_title.get("Item", {}).get("Season") == expected_ep.get("Item", {}).get("Season")
            assert actual_title.get("Item", {}).get("Episode") == expected_ep.get("Item", {}).get("Episode")

    def test_finalize_produces_extra_item_references_with_season_episode(
        self, tv_log_path: str, tv_summary_content: str,         expected_tv_disc_json: dict[str, Any]
    ) -> None:
        result = _run_finalize_logic(tv_log_path, tv_summary_content)

        expected_extras = [
            t for t in expected_tv_disc_json.get("Titles", []) if t.get("Item", {}).get("Type") == "Extra"
        ]

        assert len(expected_extras) > 0, "No Extras found in expected JSON"

        for expected_extra in expected_extras:
            key = (
                expected_extra.get("SegmentMap"),
                expected_extra.get("SourceFile"),
                expected_extra.get("Duration")
            )
            actual_title = next(
                (t for t in result.get("Titles", []) if
                 t.get("SegmentMap") == key[0] and t.get("SourceFile") == key[1] and t.get("Duration") == key[2]),
                None
            )
            assert actual_title is not None
            assert actual_title.get("Item", {}).get("Type") == "Extra"
            assert "Season" in actual_title.get("Item", {})
            assert "Episode" in actual_title.get("Item", {})

    def test_finalize_output_functionally_equivalent_to_expected(
        self, tv_log_path: str, tv_summary_content: str,         expected_tv_disc_json: dict[str, Any]
    ) -> None:
        result = _run_finalize_logic(tv_log_path, tv_summary_content)

        is_equivalent, errors = _disc_functionally_equivalent(result, expected_tv_disc_json)

        assert is_equivalent, f"Finalize output not functionally equivalent:\n  " + "\n  ".join(errors)
