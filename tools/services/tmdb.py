from typing import Any

import requests


class TmdbClient:
    def __init__(self, api_key: str) -> None:
        self.api_key: str = api_key
        self.base: str = "https://api.themoviedb.org/3"

    def _get(self, path: str, **params: str) -> dict[str, Any]:
        params["api_key"] = self.api_key
        r = requests.get(self.base + path, params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    def get_movie(self, id: str) -> dict[str, Any]:
        return self._get(f"/movie/{id}")

    def get_series(self, id: str) -> dict[str, Any]:
        return self._get(f"/tv/{id}")

    def get_imdb_data(self, imdb_id: str) -> dict[str, Any]:
        r = requests.get(f"https://v3.somedomain.top/imdb/{imdb_id}", timeout=30)
        r.raise_for_status()
        return r.json()