"""
Tests for normalize_url function.
"""

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.url_functions]
from pyutils_collection.url_functions.normalize_url import normalize_url


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("HTTP://[2001:DB8::1]:80/a", "http://[2001:db8::1]/a"),
        ("https://[::1]:8443", "https://[::1]:8443/"),
        ("https://[::1]", "https://[::1]/"),
        ("http://user:@EXAMPLE.COM:80", "http://user:@example.com/"),
        ("http://:pass@EXAMPLE.COM", "http://:pass@example.com/"),
        ("http://@EXAMPLE.COM", "http://@example.com/"),
    ],
)
def test_normalize_url_preserves_authority(url: str, expected: str) -> None:
    assert normalize_url(url) == expected
    assert normalize_url(expected) == expected


def test_normalize_url_default_port_http() -> None:
    """
    Test case 1: Remove default HTTP port 80.
    """
    # Arrange
    url = "http://example.com:80/path"
    expected = "http://example.com/path"

    # Act
    result = normalize_url(url)

    # Assert
    assert result == expected


def test_normalize_url_default_port_https() -> None:
    """
    Test case 2: Remove default HTTPS port 443.
    """
    # Arrange
    url = "https://example.com:443/path"
    expected = "https://example.com/path"

    # Act
    result = normalize_url(url)

    # Assert
    assert result == expected


def test_normalize_url_non_default_port() -> None:
    """
    Test case 3: Keep non-default port.
    """
    # Arrange
    url = "http://example.com:8080/path"
    expected = "http://example.com:8080/path"

    # Act
    result = normalize_url(url)

    # Assert
    assert result == expected


def test_normalize_url_uppercase_scheme() -> None:
    """
    Test case 4: Convert uppercase scheme to lowercase.
    """
    # Arrange
    url = "HTTP://EXAMPLE.COM/path"
    expected = "http://example.com/path"

    # Act
    result = normalize_url(url)

    # Assert
    assert result == expected


def test_normalize_url_sort_query_params() -> None:
    """
    Test case 5: Sort query parameters alphabetically.
    """
    # Arrange
    url = "https://example.com/page?z=3&a=1&m=2"
    expected = "https://example.com/page?a=1&m=2&z=3"

    # Act
    result = normalize_url(url)

    # Assert
    assert result == expected


def test_normalize_url_remove_fragment() -> None:
    """
    Test case 6: Remove URL fragment.
    """
    # Arrange
    url = "http://example.com/page#section"
    expected = "http://example.com/page"

    # Act
    result = normalize_url(url, remove_fragment=True)

    # Assert
    assert result == expected


def test_normalize_url_keep_fragment() -> None:
    """
    Test case 7: Keep URL fragment by default.
    """
    # Arrange
    url = "http://example.com/page#section"
    expected = "http://example.com/page#section"

    # Act
    result = normalize_url(url, remove_fragment=False)

    # Assert
    assert result == expected


def test_normalize_url_remove_trailing_slash() -> None:
    """
    Test case 8: Remove trailing slash from path.
    """
    # Arrange
    url = "http://example.com/path/"
    expected = "http://example.com/path"

    # Act
    result = normalize_url(url, remove_trailing_slash=True)

    # Assert
    assert result == expected


def test_normalize_url_root_path_keeps_slash() -> None:
    """
    Test case 9: Root path keeps trailing slash.
    """
    # Arrange
    url = "http://example.com/"
    expected = "http://example.com/"

    # Act
    result = normalize_url(url, remove_trailing_slash=True)

    # Assert
    assert result == expected


def test_normalize_url_with_username_password() -> None:
    """
    Test case 10: Preserve username and password in URL.
    """
    # Arrange
    url = "http://user:pass@example.com/path"
    expected = "http://user:pass@example.com/path"

    # Act
    result = normalize_url(url)

    # Assert
    assert result == expected


def test_normalize_url_empty_string_raises_error() -> None:
    """
    Test case 11: ValueError for empty URL.
    """
    # Arrange
    url = ""
    expected_message = "url cannot be empty"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        normalize_url(url)


def test_normalize_url_invalid_type_raises_error() -> None:
    """
    Test case 12: TypeError for non-string URL.
    """
    # Arrange
    url = 123
    expected_message = "url must be a string, got int"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        normalize_url(url)  # type: ignore


def test_normalize_url_multiple_query_params_same_key() -> None:
    """
    Test case 13: Handle multiple values for same query parameter.
    """
    # Arrange
    url = "http://example.com?tag=python&tag=web&tag=api"
    # Should preserve all values and sort by key

    # Act
    result = normalize_url(url)

    # Assert
    assert "tag=python" in result
    assert "tag=web" in result
    assert "tag=api" in result


def test_normalize_url_no_sorting() -> None:
    """
    Test case 14: Preserve query parameter order when sort_query_params=False.
    """
    # Arrange
    url = "http://example.com?z=3&a=1"
    # urlunparse may add trailing slash for paths

    # Act
    result = normalize_url(url, sort_query_params=False)

    # Assert
    # Check query params are in original order
    assert "z=3" in result
    assert "a=1" in result
    assert result.index("z=3") < result.index("a=1")


def test_normalize_url_keep_uppercase() -> None:
    """
    Test case 15: Keep uppercase host with lowercase_scheme_host=False.
    """
    # Arrange
    url = "http://EXAMPLE.COM/path"

    # Act
    result = normalize_url(url, lowercase_scheme_host=False)

    # Assert
    assert "EXAMPLE.COM" in result
    assert "/path" in result
