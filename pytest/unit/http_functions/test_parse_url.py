import pytest

pytestmark = [pytest.mark.unit, pytest.mark.http_functions]
from pyutils_collection.http_functions.parse_url import parse_url


def test_parse_simple_https_url() -> None:

    """Test case 1: Test parsing a simple HTTPS URL returns correct components."""
    url = "https://example.com"
    result = parse_url(url)

    assert result["scheme"] == "https"
    assert result["netloc"] == "example.com"
    assert result["hostname"] == "example.com"
    assert result["port"] is None
    assert result["path"] == ""
    assert result["params"] == ""
    assert result["query"] == ""
    assert result["fragment"] == ""
    assert result["username"] is None
    assert result["password"] is None


def test_parse_url_with_path() -> None:

    """Test case 2: Test parsing URL with path component."""
    url = "https://example.com/api/v1/users"
    result = parse_url(url)

    assert result["scheme"] == "https"
    assert result["hostname"] == "example.com"
    assert result["path"] == "/api/v1/users"


def test_parse_url_with_port() -> None:

    """Test case 3: Test parsing URL with port number."""
    url = "https://example.com:8080/api"
    result = parse_url(url)

    assert result["scheme"] == "https"
    assert result["netloc"] == "example.com:8080"
    assert result["hostname"] == "example.com"
    assert result["port"] == 8080
    assert result["path"] == "/api"


def test_parse_url_with_query_parameters() -> None:

    """Test case 4: Test parsing URL with query parameters."""
    url = "https://example.com/search?q=python&page=1&sort=date"
    result = parse_url(url)

    assert result["scheme"] == "https"
    assert result["hostname"] == "example.com"
    assert result["path"] == "/search"
    assert result["query"] == "q=python&page=1&sort=date"


def test_parse_url_with_fragment() -> None:

    """Test case 5: Test parsing URL with fragment component."""
    url = "https://example.com/docs#section1"
    result = parse_url(url)

    assert result["scheme"] == "https"
    assert result["hostname"] == "example.com"
    assert result["path"] == "/docs"
    assert result["fragment"] == "section1"


def test_parse_url_with_username_and_password() -> None:

    """Test case 6: Test parsing URL with authentication credentials."""
    url = "https://user:pass@example.com/secure"
    result = parse_url(url)

    assert result["scheme"] == "https"
    assert result["netloc"] == "user:pass@example.com"
    assert result["hostname"] == "example.com"
    assert result["username"] == "user"
    assert result["password"] == "pass"
    assert result["path"] == "/secure"


def test_parse_url_with_username_only() -> None:

    """Test case 7: Test parsing URL with username but no password."""
    url = "https://user@example.com/api"
    result = parse_url(url)

    assert result["scheme"] == "https"
    assert result["netloc"] == "user@example.com"
    assert result["hostname"] == "example.com"
    assert result["username"] == "user"
    assert result["password"] is None
    assert result["path"] == "/api"


def test_parse_complex_url_all_components() -> None:

    """Test case 8: Test parsing a complex URL with all components present."""
    url = "https://user:pass@example.com:8080/api/v1/users?limit=10&offset=20#results"
    result = parse_url(url)

    assert result["scheme"] == "https"
    assert result["netloc"] == "user:pass@example.com:8080"
    assert result["hostname"] == "example.com"
    assert result["port"] == 8080
    assert result["path"] == "/api/v1/users"
    assert result["params"] == ""
    assert result["query"] == "limit=10&offset=20"
    assert result["fragment"] == "results"
    assert result["username"] == "user"
    assert result["password"] == "pass"


def test_parse_url_http_scheme() -> None:

    """Test case 9: Test parsing URL with HTTP scheme."""
    url = "http://example.com"
    result = parse_url(url)
    assert result["scheme"] == "http"


def test_parse_url_ftp_scheme() -> None:

    """Test case 10: Test parsing URL with FTP scheme."""
    url = "ftp://ftp.example.com"
    result = parse_url(url)
    assert result["scheme"] == "ftp"


def test_parse_url_with_ip_address() -> None:

    """Test case 11: Test parsing URL with IP address as hostname."""
    url = "http://192.168.1.1:8000/api"
    result = parse_url(url)

    assert result["scheme"] == "http"
    assert result["hostname"] == "192.168.1.1"
    assert result["port"] == 8000
    assert result["path"] == "/api"


def test_parse_url_with_params() -> None:

    """Test case 12: Test parsing URL with parameters (semicolon-separated)."""
    url = "http://example.com/path;param1=value1;param2=value2"
    result = parse_url(url)

    assert result["scheme"] == "http"
    assert result["hostname"] == "example.com"
    assert result["path"] == "/path"
    assert result["params"] == "param1=value1;param2=value2"


def test_parse_url_with_trailing_slash() -> None:

    """Test case 13: Test parsing URL with trailing slash in path."""
    url = "https://example.com/"
    result = parse_url(url)

    assert result["scheme"] == "https"
    assert result["hostname"] == "example.com"
    assert result["path"] == "/"
    assert result["query"] == ""
    assert result["fragment"] == ""


def test_parse_url_file_scheme() -> None:

    """Test case 14: Test parsing URL with file scheme."""
    url = "file:///path/to/file"
    result = parse_url(url)
    assert result["scheme"] == "file"


def test_parse_url_mailto_scheme() -> None:

    """Test case 15: Test parsing URL with mailto scheme."""
    url = "mailto:test@example.com"
    result = parse_url(url)
    assert result["scheme"] == "mailto"


def test_parse_url_empty_components() -> None:

    """Test case 16: Test parsing URL handles empty components correctly."""
    url = "https://example.com/"
    result = parse_url(url)

    assert result["scheme"] == "https"
    assert result["hostname"] == "example.com"
    assert result["path"] == "/"
    assert result["query"] == ""
    assert result["fragment"] == ""


def test_parse_url_with_empty_string() -> None:

    """Test case 17: Test parse_url function with empty string raises ValueError."""
    with pytest.raises(ValueError, match="URL must be a non-empty string"):
        parse_url("")


def test_parse_url_with_whitespace_string() -> None:

    """Test case 18: Test parse_url function with whitespace-only string raises ValueError."""
    with pytest.raises(ValueError, match="URL must be a non-empty string"):
        parse_url("   ")


def test_parse_url_with_none() -> None:

    """Test case 19: Test parse_url function with None raises TypeError."""
    with pytest.raises(TypeError):
        parse_url(None)
