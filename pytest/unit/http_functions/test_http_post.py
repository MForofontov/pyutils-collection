import json
import urllib.error
from unittest.mock import Mock, patch

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.http_functions]
from pyutils_collection.http_functions.http_post import http_post


@patch("urllib.request.urlopen")
def test_http_post_no_data(mock_urlopen) -> None:

    """Test case 1: Test HTTP POST request with no data payload."""
    mock_response = Mock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = b'{"success": true}'
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.geturl.return_value = "https://example.com/api"
    mock_urlopen.return_value.__enter__.return_value = mock_response

    result = http_post("https://example.com/api")

    assert result["status_code"] == 200
    assert result["content"] == '{"success": true}'

    # Verify no data was sent
    call_args = mock_urlopen.call_args[0]
    request = call_args[0]
    assert request.data is None


@patch("urllib.request.urlopen")
def test_http_post_with_dict_data(mock_urlopen) -> None:

    """Test case 2: Test HTTP POST request with dictionary data gets JSON encoded."""
    mock_response = Mock()
    mock_response.getcode.return_value = 201
    mock_response.read.return_value = b'{"created": true}'
    mock_response.headers = {}
    mock_response.geturl.return_value = "https://example.com/api"
    mock_urlopen.return_value.__enter__.return_value = mock_response

    data = {"name": "test", "value": 123}
    result = http_post("https://example.com/api", data=data)

    assert result["status_code"] == 201

    # Verify JSON data was sent with correct content type
    call_args = mock_urlopen.call_args[0]
    request = call_args[0]
    assert request.data == json.dumps(data).encode("utf-8")
    assert request.get_header("Content-type") == "application/json"


@patch("urllib.request.urlopen")
def test_http_post_with_string_data(mock_urlopen) -> None:

    """Test case 3: Test HTTP POST request with string data uses form encoding."""
    mock_response = Mock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = b"OK"
    mock_response.headers = {}
    mock_response.geturl.return_value = "https://example.com/api"
    mock_urlopen.return_value.__enter__.return_value = mock_response

    data = "name=test&value=123"
    result = http_post("https://example.com/api", data=data)

    assert result["status_code"] == 200

    # Verify string data was sent with correct content type
    call_args = mock_urlopen.call_args[0]
    request = call_args[0]
    assert request.data == data.encode("utf-8")
    assert request.get_header("Content-type") == "application/x-www-form-urlencoded"


@patch("urllib.request.urlopen")
def test_http_post_with_custom_headers(mock_urlopen) -> None:

    """Test case 4: Test HTTP POST request with custom headers are properly set."""
    mock_response = Mock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = b"test response"
    mock_response.headers = {}
    mock_response.geturl.return_value = "https://example.com"
    mock_urlopen.return_value.__enter__.return_value = mock_response

    headers = {"User-Agent": "TestAgent", "Authorization": "Bearer token"}
    result = http_post("https://example.com", headers=headers)

    # Verify the request was made with correct headers
    call_args = mock_urlopen.call_args[0]
    request = call_args[0]
    assert request.get_header("User-agent") == "TestAgent"
    assert request.get_header("Authorization") == "Bearer token"
    assert result["status_code"] == 200


@patch("urllib.request.urlopen")
def test_http_post_with_custom_timeout(mock_urlopen) -> None:

    """Test case 5: Test HTTP POST request with custom timeout value."""
    mock_response = Mock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = b"test"
    mock_response.headers = {}
    mock_response.geturl.return_value = "https://example.com"
    mock_urlopen.return_value.__enter__.return_value = mock_response

    http_post("https://example.com", timeout=60)

    # Verify timeout was passed correctly
    mock_urlopen.assert_called_once()
    assert mock_urlopen.call_args[1]["timeout"] == 60


@patch("urllib.request.urlopen")
def test_http_post_default_timeout(mock_urlopen) -> None:

    """Test case 6: Test that default timeout is 30 seconds when not specified."""
    mock_response = Mock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = b"test"
    mock_response.headers = {}
    mock_response.geturl.return_value = "https://example.com"
    mock_urlopen.return_value.__enter__.return_value = mock_response

    http_post("https://example.com")

    # Check that timeout=30 was passed
    assert mock_urlopen.call_args[1]["timeout"] == 30


@patch("urllib.request.urlopen")
def test_http_post_http_error_with_response_body(mock_urlopen) -> None:

    """Test case 7: Test HTTP POST request with HTTP error that includes response body."""
    error = urllib.error.HTTPError(
        url="https://example.com",
        code=400,
        msg="Bad Request",
        hdrs={"Content-Type": "application/json"},
        fp=Mock(),
    )
    error.fp.read.return_value = b'{"error": "validation failed"}'
    mock_urlopen.side_effect = error

    result = http_post("https://example.com", data={"test": "data"})

    assert result["status_code"] == 400
    assert result["content"] == '{"error": "validation failed"}'
    assert result["headers"] == {"Content-Type": "application/json"}
    assert result["url"] == "https://example.com"


@patch("urllib.request.urlopen")
def test_http_post_complex_nested_data(mock_urlopen) -> None:

    """Test case 8: Test HTTP POST request with complex nested dictionary data."""
    mock_response = Mock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = b'{"received": true}'
    mock_response.headers = {}
    mock_response.geturl.return_value = "https://example.com/api"
    mock_urlopen.return_value.__enter__.return_value = mock_response

    data = {
        "user": {"name": "John Doe", "age": 30, "preferences": ["music", "movies"]},
        "settings": {"notifications": True, "theme": "dark"},
    }

    result = http_post("https://example.com/api", data=data)

    assert result["status_code"] == 200

    # Verify JSON encoding worked correctly
    call_args = mock_urlopen.call_args[0]
    request = call_args[0]
    sent_data = json.loads(request.data.decode("utf-8"))
    assert sent_data == data


@patch("urllib.request.urlopen")
def test_http_post_url_error(mock_urlopen) -> None:

    """Test case 9: Test HTTP POST request handles URLError correctly."""
    from urllib.error import URLError

    mock_urlopen.side_effect = URLError("Connection refused")

    with pytest.raises(
        URLError, match="Failed to reach https://example.com: Connection refused"
    ):
        http_post("https://example.com", data={"test": "data"})


def test_http_post_with_empty_url() -> None:

    """Test case 10: Test http_post function with empty URL raises ValueError."""
    with pytest.raises(ValueError, match="URL must be a non-empty string"):
        http_post("")


def test_http_post_with_whitespace_url() -> None:

    """Test case 11: Test http_post function with whitespace-only URL raises ValueError."""
    with pytest.raises(ValueError, match="URL must be a non-empty string"):
        http_post("   ")


def test_http_post_with_none_url() -> None:

    """Test case 12: Test http_post function with None URL raises TypeError."""
    with pytest.raises(TypeError):
        http_post(None)
