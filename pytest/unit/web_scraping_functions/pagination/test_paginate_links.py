import pytest

try:
    from bs4 import BeautifulSoup
    from pyutils_collection.web_scraping_functions.pagination.paginate_links import paginate_links
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    BeautifulSoup = None  # type: ignore
    paginate_links = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.web_scraping,
    pytest.mark.skipif(not BS4_AVAILABLE, reason="beautifulsoup4 not installed"),
]


def test_paginate_links_simple_pagination() -> None:
    """
    Test case 1: Generate simple pagination URLs.
    """
    # Arrange
    base_url = "https://example.com/page"

    # Act
    result = paginate_links(base_url, start_page=1, end_page=3)

    # Assert
    assert result == [
        "https://example.com/page?page=1",
        "https://example.com/page?page=2",
        "https://example.com/page?page=3",
    ]


def test_paginate_links_custom_param() -> None:
    """
    Test case 2: Generate pagination with custom parameter name.
    """
    # Arrange
    base_url = "https://example.com/items"

    # Act
    result = paginate_links(base_url, start_page=1, end_page=2, page_param="p")

    # Assert
    assert result == ["https://example.com/items?p=1", "https://example.com/items?p=2"]


def test_paginate_links_existing_query_params() -> None:
    """
    Test case 3: Add pagination to URL with existing query parameters.
    """
    # Arrange
    base_url = "https://example.com/search?q=test"

    # Act
    result = paginate_links(base_url, start_page=1, end_page=2)

    # Assert
    assert result == [
        "https://example.com/search?q=test&page=1",
        "https://example.com/search?q=test&page=2",
    ]


def test_paginate_links_single_page() -> None:
    """
    Test case 4: Generate single page URL.
    """
    # Arrange
    base_url = "https://example.com/page"

    # Act
    result = paginate_links(base_url, start_page=5, end_page=5)

    # Assert
    assert result == ["https://example.com/page?page=5"]


def test_paginate_links_start_page_one() -> None:
    """
    Test case 5: Generate pagination starting from 1.
    """
    # Arrange
    base_url = "https://example.com/items"

    # Act
    result = paginate_links(base_url, start_page=1, end_page=3)

    # Assert
    assert len(result) == 3
    assert "page=1" in result[0]


def test_paginate_links_type_error_base_url() -> None:
    """
    Test case 6: TypeError for invalid base_url type.
    """
    # Act & Assert
    with pytest.raises(TypeError, match="base_url must be a string"):
        paginate_links(123, start_page=1, end_page=3)


def test_paginate_links_type_error_start_page() -> None:
    """
    Test case 7: TypeError for invalid start_page type.
    """
    # Act & Assert
    with pytest.raises(TypeError, match="start_page must be an integer"):
        paginate_links("https://example.com", start_page="1", end_page=3)


def test_paginate_links_type_error_end_page() -> None:
    """
    Test case 8: TypeError for invalid end_page type.
    """
    # Act & Assert
    with pytest.raises(TypeError, match="end_page must be an integer"):
        paginate_links("https://example.com", start_page=1, end_page="3")


def test_paginate_links_type_error_page_param() -> None:
    """
    Test case 9: TypeError for invalid page_param type.
    """
    # Act & Assert
    with pytest.raises(TypeError, match="page_param must be a string"):
        paginate_links("https://example.com", start_page=1, end_page=3, page_param=123)


def test_paginate_links_value_error_empty_url() -> None:
    """
    Test case 10: ValueError for empty base_url.
    """
    # Act & Assert
    with pytest.raises(ValueError, match="base_url cannot be empty"):
        paginate_links("", start_page=1, end_page=3)


def test_paginate_links_value_error_zero_start_page() -> None:
    """
    Test case 11: ValueError for zero start_page (must be positive).
    """
    # Act & Assert
    with pytest.raises(ValueError, match="start_page must be positive"):
        paginate_links("https://example.com", start_page=0, end_page=3)


def test_paginate_links_value_error_invalid_range() -> None:
    """
    Test case 12: ValueError when start_page > end_page.
    """
    # Act & Assert
    with pytest.raises(ValueError, match="start_page.*must be.*end_page"):
        paginate_links("https://example.com", start_page=5, end_page=3)


@pytest.mark.parametrize("query", ["", "?sort=asc"])
def test_pagination_query_precedes_fragment(query):
    from urllib.parse import parse_qs, urlsplit

    result = paginate_links(f"https://example.com/items{query}#details", 1, 2)
    for page, url in enumerate(result, 1):
        parsed = urlsplit(url)
        assert parsed.fragment == "details"
        assert parse_qs(parsed.query)["page"] == [str(page)]


def test_page_parameter_name_is_one_encoded_key():
    from urllib.parse import parse_qs, urlsplit

    result = paginate_links("https://example.com", 1, 1, "page&sort=bad")
    assert parse_qs(urlsplit(result[0]).query) == {"page&sort=bad": ["1"]}
