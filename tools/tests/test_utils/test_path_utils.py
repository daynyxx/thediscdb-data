from utils.path import clean_path, create_slug, get_sort_title


class TestCleanPath:
    def test_removes_special_characters(self) -> None:
        assert clean_path("file<name>test") == "filenametest"
        assert clean_path("path:to:file") == "pathtofile"

    def test_preserves_normal_characters(self) -> None:
        assert clean_path("normal_file.txt") == "normal_file.txt"


class TestCreateSlug:
    def test_basic_title(self) -> None:
        assert create_slug("The Matrix") == "the-matrix"

    def test_title_with_year(self) -> None:
        assert create_slug("The Matrix", 1999) == "the-matrix-1999"

    def test_lowercase_conversion(self) -> None:
        assert create_slug("STAR WARS") == "star-wars"

    def test_removes_special_chars(self) -> None:
        assert create_slug("A Quiet Place") == "a-quiet-place"

    def test_strips_leading_trailing_hyphens(self) -> None:
        assert create_slug("  The Matrix  ") == "the-matrix"

    def test_preserves_numbers(self) -> None:
        assert create_slug("2001 A Space Odyssey", 1968) == "2001-a-space-odyssey-1968"


class TestGetSortTitle:
    def test_handles_the_prefix(self) -> None:
        assert get_sort_title("The Matrix") == "Matrix, The"

    def test_preserves_non_the_titles(self) -> None:
        assert get_sort_title("Star Wars") == "Star Wars"

    def test_case_insensitive(self) -> None:
        assert get_sort_title("THE Matrix") == "Matrix, The"

    def test_no_prefix(self) -> None:
        assert get_sort_title("Regular Title") == "Regular Title"
