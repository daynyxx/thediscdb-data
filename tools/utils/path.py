import re


def clean_path(path: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '', path)


def create_slug(name: str, year: int | None = None) -> str:
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    if year:
        slug = f"{slug}-{year}"
    return slug


def get_sort_title(title: str) -> str:
    if title.lower().startswith("the "):
        return title[4:].strip() + ", The"
    return title
