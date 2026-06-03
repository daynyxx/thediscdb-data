from unittest.mock import MagicMock, patch

import pytest

from services.tmdb import TmdbClient


@pytest.fixture
def api_key() -> str:
    return "test_api_key_12345"


@pytest.fixture
def tmdb_client(api_key: str) -> TmdbClient:
    return TmdbClient(api_key)


class TestTmdbClientInit:
    def test_stores_api_key(self, api_key: str) -> None:
        client = TmdbClient(api_key)
        assert client.api_key == api_key

    def test_sets_base_url(self, api_key: str) -> None:
        client = TmdbClient(api_key)
        assert client.base == "https://api.themoviedb.org/3"


class TestTmdbClientGetMovie:
    @patch("services.tmdb.requests.get")
    def test_get_movie_returns_dict(self, mock_get: MagicMock, tmdb_client: TmdbClient) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": 603,
            "title": "The Matrix",
            "overview": "A sci-fi classic"
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = tmdb_client.get_movie("603")

        assert isinstance(result, dict)
        assert result["id"] == 603
        assert result["title"] == "The Matrix"

    @patch("services.tmdb.requests.get")
    def test_get_movie_calls_correct_url(self, mock_get: MagicMock, tmdb_client: TmdbClient) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 603}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        _ = tmdb_client.get_movie("603")

        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "/movie/603" in call_args[0][0]

    @patch("services.tmdb.requests.get")
    def test_get_movie_includes_api_key(self, mock_get: MagicMock, tmdb_client: TmdbClient) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        _ = tmdb_client.get_movie("603")

        call_args = mock_get.call_args
        params = call_args[1].get("params", {})
        assert "api_key" in params


class TestTmdbClientGetSeries:
    @patch("services.tmdb.requests.get")
    def test_get_series_returns_dict(self, mock_get: MagicMock, tmdb_client: TmdbClient) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": 2316,
            "name": "The Office",
            "overview": "A comedy series"
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = tmdb_client.get_series("2316")

        assert isinstance(result, dict)
        assert result["id"] == 2316
        assert result["name"] == "The Office"

    @patch("services.tmdb.requests.get")
    def test_get_series_calls_correct_url(self, mock_get: MagicMock, tmdb_client: TmdbClient) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 2316}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        _ = tmdb_client.get_series("2316")

        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "/tv/2316" in call_args[0][0]


class TestTmdbClientGetImdbData:
    @patch("services.tmdb.requests.get")
    def test_get_imdb_data_returns_dict(self, mock_get: MagicMock, tmdb_client: TmdbClient) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "imdb_id": "tt0133093",
            "title": "The Matrix"
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = tmdb_client.get_imdb_data("tt0133093")

        assert isinstance(result, dict)
        assert result["imdb_id"] == "tt0133093"

    @patch("services.tmdb.requests.get")
    def test_get_imdb_data_calls_external_api(self, mock_get: MagicMock, tmdb_client: TmdbClient) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        _ = tmdb_client.get_imdb_data("tt0133093")

        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "somedomain.top" in call_args[0][0]


class TestTmdbPosterUrl:
    @patch("services.tmdb.requests.get")
    def test_poster_url_construction(self, mock_get: MagicMock, tmdb_client: TmdbClient) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "poster_path": "/abc123.jpg"
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = tmdb_client.get_movie("603")

        _ = "https://image.tmdb.org/t/p/original/abc123.jpg"
        assert result["poster_path"] == "/abc123.jpg"
