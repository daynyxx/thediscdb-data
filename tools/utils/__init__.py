def download(url: str, path: str) -> None:
    import requests
    if url:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)


from .io import read_json, write_json
from .path import clean_path, create_slug, get_sort_title
from .hash_utils import calculate_disc_hash, append_hash_to_log, clean_log

__all__ = [
    "read_json",
    "write_json",
    "clean_path",
    "create_slug",
    "get_sort_title",
    "download",
    "calculate_disc_hash",
    "append_hash_to_log",
    "clean_log",
]