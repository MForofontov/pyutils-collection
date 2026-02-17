from unittest.mock import patch

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.http_functions]
from pyutils_collection.http_functions.extract_domain import extract_domain


@patch("pyutils_collection.http_functions.extract_domain.is_valid_url")
def test_extract_domain_invalid_url(mock_is_valid_url) -> None:

    """
    Test case 1: Extract_domain function with invalid URL returns None.
    """
    mock_is_valid_url.return_value = False

    result = extract_domain("invalid-url")
    assert result is None

    mock_is_valid_url.assert_called_once_with("invalid-url")


@patch("pyutils_collection.http_functions.extract_domain.is_valid_url")
def test_extract_domain_simple_url(mock_is_valid_url) -> None:

    """
    Test case 2: Extract_domain function with simple valid URL returns hostname.
    """
    mock_is_valid_url.return_value = True

    result = extract_domain("https://example.com")
    assert result == "example.com"


@patch("pyutils_collection.http_functions.extract_domain.is_valid_url")
def test_extract_domain_with_www_subdomain(mock_is_valid_url) -> None:

    """
    Test case 3: Extract_domain function with www subdomain returns full hostname.
    """
    mock_is_valid_url.return_value = True

    result = extract_domain("https://www.example.com")
    assert result == "www.example.com"


@patch("pyutils_collection.http_functions.extract_domain.is_valid_url")
def test_extract_domain_with_complex_subdomain(mock_is_valid_url) -> None:

    """
    Test case 4: Extract_domain function with complex subdomain returns full hostname.
    """
    mock_is_valid_url.return_value = True

    result = extract_domain("https://api.subdomain.example.com")
    assert result == "api.subdomain.example.com"


@patch("pyutils_collection.http_functions.extract_domain.is_valid_url")
def test_extract_domain_with_port(mock_is_valid_url) -> None:

    """
    Test case 5: Extract_domain function with port returns hostname without port.
    """
    mock_is_valid_url.return_value = True

    result = extract_domain("https://example.com:8080")
    assert result == "example.com"


@patch("pyutils_collection.http_functions.extract_domain.is_valid_url")
def test_extract_domain_localhost_with_port(mock_is_valid_url) -> None:

    """
    Test case 6: Extract_domain function with localhost and port returns hostname.
    """
    mock_is_valid_url.return_value = True

    result = extract_domain("http://localhost:3000")
    assert result == "localhost"


@patch("pyutils_collection.http_functions.extract_domain.is_valid_url")
def test_extract_domain_with_path(mock_is_valid_url) -> None:

    """
    Test case 7: Extract_domain function with path returns hostname only.
    """
    mock_is_valid_url.return_value = True

    result = extract_domain("https://example.com/api/v1/users")
    assert result == "example.com"


@patch("pyutils_collection.http_functions.extract_domain.is_valid_url")
def test_extract_domain_with_long_path(mock_is_valid_url) -> None:

    """
    Test case 8: Extract_domain function with long path returns hostname only.
    """
    mock_is_valid_url.return_value = True

    result = extract_domain("https://www.example.com/very/long/path")
    assert result == "www.example.com"


@patch("pyutils_collection.http_functions.extract_domain.is_valid_url")
def test_extract_domain_with_query_parameters(mock_is_valid_url) -> None:

    """
    Test case 9: Extract_domain function with query parameters returns hostname only.
    """
    mock_is_valid_url.return_value = True

    result = extract_domain("https://example.com/search?q=test&page=1")
    assert result == "example.com"


@patch("pyutils_collection.http_functions.extract_domain.is_valid_url")
def test_extract_domain_with_fragment(mock_is_valid_url) -> None:

    """
    Test case 10: Extract_domain function with fragment returns hostname only.
    """
    mock_is_valid_url.return_value = True

    result = extract_domain("https://example.com/docs#section1")
    assert result == "example.com"


@patch("pyutils_collection.http_functions.extract_domain.is_valid_url")
def test_extract_domain_with_query_and_fragment(mock_is_valid_url) -> None:

    """
    Test case 11: Extract_domain function with query and fragment returns hostname only.
    """
    mock_is_valid_url.return_value = True

    result = extract_domain("https://example.com/api?key=value#top")
    assert result == "example.com"


@patch("pyutils_collection.http_functions.extract_domain.is_valid_url")
def test_extract_domain_with_username_and_password(mock_is_valid_url) -> None:

    """
    Test case 12: Extract_domain function with authentication returns hostname only.
    """
    mock_is_valid_url.return_value = True

    result = extract_domain("https://user:pass@example.com")
    assert result == "example.com"


@patch("pyutils_collection.http_functions.extract_domain.is_valid_url")
def test_extract_domain_ftp_with_username(mock_is_valid_url) -> None:

    """
    Test case 13: Extract_domain function with FTP and username returns hostname only.
    """
    mock_is_valid_url.return_value = True

    result = extract_domain("ftp://username@ftp.example.com")
    assert result == "ftp.example.com"


@patch("pyutils_collection.http_functions.extract_domain.is_valid_url")
def test_extract_domain_with_ipv4_address(mock_is_valid_url) -> None:

    """
    Test case 14: Extract_domain function with IPv4 address returns IP address.
    """
    mock_is_valid_url.return_value = True

    result = extract_domain("http://192.168.1.1")
    assert result == "192.168.1.1"


@patch("pyutils_collection.http_functions.extract_domain.is_valid_url")
def test_extract_domain_with_ipv4_and_port(mock_is_valid_url) -> None:

    """
    Test case 15: Extract_domain function with IPv4 and port returns IP only.
    """
    mock_is_valid_url.return_value = True

    result = extract_domain("https://127.0.0.1:8080")
    assert result == "127.0.0.1"


@patch("pyutils_collection.http_functions.extract_domain.is_valid_url")
def test_extract_domain_with_ipv4_and_path(mock_is_valid_url) -> None:

    """
    Test case 16: Extract_domain function with IPv4 and path returns IP only.
    """
    mock_is_valid_url.return_value = True

    result = extract_domain("http://10.0.0.1/api")
    assert result == "10.0.0.1"


@patch("pyutils_collection.http_functions.extract_domain.is_valid_url")
def test_extract_domain_https_scheme(mock_is_valid_url) -> None:

    """
    Test case 17: Extract_domain function with HTTPS scheme returns hostname.
    """
    mock_is_valid_url.return_value = True

    result = extract_domain("https://example.com")
    assert result == "example.com"


@patch("pyutils_collection.http_functions.extract_domain.is_valid_url")
def test_extract_domain_http_scheme(mock_is_valid_url) -> None:

    """
    Test case 18: Extract_domain function with HTTP scheme returns hostname.
    """
    mock_is_valid_url.return_value = True

    result = extract_domain("http://example.com")
    assert result == "example.com"


@patch("pyutils_collection.http_functions.extract_domain.is_valid_url")
def test_extract_domain_ftp_scheme(mock_is_valid_url) -> None:

    """
    Test case 19: Extract_domain function with FTP scheme returns hostname.
    """
    mock_is_valid_url.return_value = True

    result = extract_domain("ftp://ftp.example.com")
    assert result == "ftp.example.com"


@patch("pyutils_collection.http_functions.extract_domain.is_valid_url")
def test_extract_domain_file_scheme(mock_is_valid_url) -> None:

    """
    Test case 20: Extract_domain function with file scheme returns hostname.
    """
    mock_is_valid_url.return_value = True

    result = extract_domain("file://server.local/path")
    assert result == "server.local"


@patch("pyutils_collection.http_functions.extract_domain.is_valid_url")
def test_extract_domain_complex_url(mock_is_valid_url) -> None:

    """
    Test case 21: Extract_domain function with complex URL returns hostname only.
    """
    mock_is_valid_url.return_value = True

    complex_url = "https://user:pass@api.subdomain.example.com:8080/v1/users?limit=10&offset=20#results"
    result = extract_domain(complex_url)
    assert result == "api.subdomain.example.com"


def test_extract_domain_integration_valid_url() -> None:

    """
    Test case 22: Extract_domain function with real validation and valid URL.
    """
    # Test with real validation (without mocking)
    result = extract_domain("https://example.com")
    assert result == "example.com"


def test_extract_domain_integration_invalid_url() -> None:

    """
    Test case 23: Extract_domain function with real validation and invalid URL.
    """
    # Test with real validation (without mocking)
    result = extract_domain("invalid-url")
    assert result is None


def test_extract_domain_integration_complex_url() -> None:

    """
    Test case 24: Extract_domain function with real validation and complex URL.
    """
    # Test with real validation (without mocking)
    result = extract_domain("https://www.google.com/search?q=test")
    assert result == "www.google.com"


def test_extract_domain_empty_string() -> None:
    """
    Test case 25: Test extract_domain with empty string.
    """
    result = extract_domain("")
    assert result is None


def test_extract_domain_invalid_url_type() -> None:
    """
    Test case 26: Test extract_domain with invalid URL type.
    """
    with pytest.raises(TypeError):
        extract_domain(None)


def test_extract_domain_invalid_url_int() -> None:
    """
    Test case 27: Test extract_domain with integer input.
    """
    with pytest.raises(TypeError):
        extract_domain(123)


def test_extract_domain_invalid_url_list() -> None:
    """
    Test case 28: Test extract_domain with list input.
    """
    with pytest.raises(TypeError):
        extract_domain(["https://example.com"])
