import json
from pathlib import Path
from typing import Any

from utils.io import read_json, write_json


class TestWriteJson:
    def test_writes_valid_json(self, temp_output_dir: Path) -> None:
        path = temp_output_dir / "test.json"
        data = {"key": "value", "number": 42}

        write_json(str(path), data)

        assert path.exists()
        with open(path) as f:
            loaded: dict[str, Any] = json.load(f)
        assert loaded == data

    def test_writes_nested_structure(self, temp_output_dir: Path) -> None:
        path = temp_output_dir / "nested.json"
        data = {
            "outer": {"inner": {"deep": "value"}},
            "list": [1, 2, 3]
        }

        write_json(str(path), data)

        with open(path) as f:
            loaded: dict[str, Any] = json.load(f)
        assert loaded == data

    def test_writes_empty_object(self, temp_output_dir: Path) -> None:
        path = temp_output_dir / "empty.json"
        write_json(str(path), {})

        with open(path) as f:
            loaded: dict[str, Any] = json.load(f)
        assert loaded == {}

    def test_preserves_numeric_types(self, temp_output_dir: Path) -> None:
        path = temp_output_dir / "types.json"
        data = {
            "integer": 42,
            "float": 3.14,
            "negative": -10,
            "zero": 0
        }

        write_json(str(path), data)

        with open(path) as f:
            loaded: dict[str, Any] = json.load(f)
        assert loaded == data


class TestReadJson:
    def test_reads_json_file(self, temp_output_dir: Path) -> None:
        path = temp_output_dir / "read.json"
        data = {"test": "data", "count": 123}
        with open(path, "w") as f:
            json.dump(data, f)

        result = read_json(str(path))
        assert result == data

    def test_reads_nested_json(self, temp_output_dir: Path) -> None:
        path = temp_output_dir / "nested.json"
        data = {"a": {"b": {"c": [1, 2, 3]}}}
        with open(path, "w") as f:
            json.dump(data, f)

        result = read_json(str(path))
        assert result == data

    def test_reads_empty_object(self, temp_output_dir: Path) -> None:
        path = temp_output_dir / "empty.json"
        with open(path, "w") as f:
            json.dump({}, f)

        result = read_json(str(path))
        assert result == {}


class TestJsonRoundTrip:
    def test_write_and_read_preserves_data(self, temp_output_dir: Path) -> None:
        path = temp_output_dir / "roundtrip.json"
        original = {
            "title": "The Matrix",
            "year": 1999,
            "genres": ["Action", "Sci-Fi"],
            "nested": {"key": "value"}
        }

        write_json(str(path), original)
        result = read_json(str(path))

        assert result == original
