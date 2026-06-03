import json
from pathlib import Path
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock

import pytest


FIXTURES_DIR: Path = Path(__file__).parent / "fixtures"
EXPECTED_DIR: Path = FIXTURES_DIR / "expected_outputs"


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture
def expected_dir() -> Path:
    return EXPECTED_DIR


@pytest.fixture
def sample_log_path(fixtures_dir: Path) -> str:
    return str(fixtures_dir / "sample_makemkv_log.txt")


@pytest.fixture
def expected_disc_json(expected_dir: Path) -> dict[str, Any]:
    with open(expected_dir / "movie" / "disc01.json") as f:
        return dict[str, Any](json.load(f))  # type: ignore[return-value]


@pytest.fixture
def expected_metadata_json(expected_dir: Path) -> dict[str, Any]:
    with open(expected_dir / "metadata.json") as f:
        return dict[str, Any](json.load(f))  # type: ignore[return-value]


@pytest.fixture
def expected_summary_txt(expected_dir: Path) -> str:
    with open(expected_dir / "movie" / "disc01-summary.txt") as f:
        return f.read()


@pytest.fixture
def movie_log_path(fixtures_dir: Path) -> str:
    return str(fixtures_dir / "expected_outputs" / "movie" / "disc01.txt")


@pytest.fixture
def movie_summary_content(fixtures_dir: Path) -> str:
    with open(fixtures_dir / "expected_outputs" / "movie" / "disc01-summary.txt") as f:
        return f.read()


@pytest.fixture
def expected_movie_disc_json(expected_dir: Path) -> dict[str, Any]:
    with open(expected_dir / "movie" / "disc01.json") as f:
        return dict[str, Any](json.load(f))  # type: ignore[return-value]


@pytest.fixture
def tv_log_path(fixtures_dir: Path) -> str:
    return str(fixtures_dir / "expected_outputs" / "tv" / "disc01.txt")


@pytest.fixture
def tv_summary_content(fixtures_dir: Path) -> str:
    with open(fixtures_dir / "expected_outputs" / "tv" / "disc01-summary.txt") as f:
        return f.read()


@pytest.fixture
def expected_tv_disc_json(expected_dir: Path) -> dict[str, Any]:
    with open(expected_dir / "tv" / "disc01.json") as f:
        return dict[str, Any](json.load(f))  # type: ignore[return-value]


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    output_dir: Path = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def mock_tmdb_client() -> Generator[MagicMock, None, None]:
    mock = MagicMock()
    yield mock


@pytest.fixture
def mock_requests_download() -> Generator[MagicMock, None, None]:
    mock_download = MagicMock()
    mock_download.return_value = None
    yield mock_download


@pytest.fixture
def mock_make_mkv() -> Generator[MagicMock, None, None]:
    mock = MagicMock()
    yield mock
