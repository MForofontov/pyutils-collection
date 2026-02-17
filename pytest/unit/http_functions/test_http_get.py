import urllib.error
from unittest.mock import Mock, patch

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.http_functions]
from pyutils_collection.http_functions.http_get import http_get


@patch("urllib.request.urlopen")
def test_http_get_successful_request(mock_urlopen) -> None:

    """
    Test case 1: Successful HTTP GET request returns correct response structure.
    """
    # Mock response
    mock_response = Mock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = b'{"success": true}'
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.geturl.return_value = "https://example.com/api"
    mock_urlopen.return_value.__enter__.return_value = mock_response

    result = http_get("https://example.com/api")

    assert result["status_code"] == 200
    assert result["content"] == '{"success": true}'
    assert result["headers"] == {"Content-Type": "application/json"}
    assert result["url"] == "https://example.com/api"


@patch("urllib.request.urlopen")
def test_http_get_with_custom_headers(mock_urlopen) -> None:

    """
    Test case 2: HTTP GET request applies custom headers correctly.
    """
    mock_response = Mock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = b"test response"
    mock_response.headers = {}
    mock_response.geturl.return_value = "https://example.com"
    mock_urlopen.return_value.__enter__.return_value = mock_response

    headers = {"User-Agent": "TestAgent", "Authorization": "Bearer token"}
    result = http_get("https://example.com", headers=headers)

    # Verify the request was made with correct headers
    call_args = mock_urlopen.call_args[0]
    request = call_args[0]
    assert request.get_header("User-agent") == "TestAgent"
    assert request.get_header("Authorization") == "Bearer token"
    assert result["status_code"] == 200


@patch("urllib.request.urlopen")
def test_http_get_with_custom_timeout(mock_urlopen) -> None:

    """
    Test case 3: HTTP GET request with custom timeout value.
    """
    mock_response = Mock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = b"test"
    mock_response.headers = {}
    mock_response.geturl.return_value = "https://example.com"
    mock_urlopen.return_value.__enter__.return_value = mock_response

    http_get("https://example.com", timeout=60)

    # Verify timeout was passed correctly
    mock_urlopen.assert_called_once()
    assert mock_urlopen.call_args[1]["timeout"] == 60


@patch("urllib.request.urlopen")
def test_http_get_default_timeout(mock_urlopen) -> None:

    """
    Test case 4: Default timeout is 30 seconds when not specified.
    """
    mock_response = Mock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = b"test"
    mock_response.headers = {}
    mock_response.geturl.return_value = "https://example.com"
    mock_urlopen.return_value.__enter__.return_value = mock_response

    http_get("https://example.com")

    # Check that timeout=30 was passed
    assert mock_urlopen.call_args[1]["timeout"] == 30


def test_http_get_with_empty_url() -> None:

    """
    Test case 5: Empty URL raises ValueError.
    """
    with pytest.raises(ValueError, match="URL must be a non-empty string"):
        http_get("")


def test_http_get_with_whitespace_url() -> None:

    """
    Test case 6: Whitespace-only URL raises ValueError.
    """
    with pytest.raises(ValueError, match="URL must be a non-empty string"):
        http_get("   ")


def test_http_get_with_none_url() -> None:

    """
    Test case 7: None URL raises TypeError.
    """
    with pytest.raises(TypeError):
        http_get(None)


@patch("urllib.request.urlopen")
def test_http_get_http_error_with_response_body(mock_urlopen) -> None:

    """
    Test case 8: HTTP GET request with HTTP error that includes response body.
    """
    error = urllib.error.HTTPError(
        url="https://example.com",
        code=404,
        msg="Not Found",
        hdrs={"Content-Type": "text/plain"},
        fp=Mock(),
    )
    error.fp.read.return_value = b"Not found"
    mock_urlopen.side_effect = error

    with pytest.raises(urllib.error.HTTPError):
        http_get("https://example.com")


@patch("urllib.request.urlopen")
def test_http_get_http_error_without_response_body(mock_urlopen) -> None:

    """
    Test case 9: HTTP GET request with HTTP error but no response body.
    """
    error = urllib.error.HTTPError(
        url="https://example.com", code=500, msg="Server Error", hdrs=None, fp=None
    )
    mock_urlopen.side_effect = error

    with pytest.raises(urllib.error.HTTPError):
        http_get("https://example.com")


@patch("urllib.request.urlopen")
def test_http_get_url_error(mock_urlopen) -> None:

    """
    Test case 10: HTTP GET request with URL error raises exception.
    """
    mock_urlopen.side_effect = urllib.error.URLError("Connection failed")

    with pytest.raises(urllib.error.URLError):
        http_get("https://example.com")
