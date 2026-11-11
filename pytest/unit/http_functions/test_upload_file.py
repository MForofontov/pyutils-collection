import urllib.error
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.http_functions]
from pyutils_collection.http_functions.upload_file import upload_file


@patch("pathlib.Path.exists", return_value=True)
@patch("pathlib.Path.is_file", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=b"test file content")
@patch("pyutils_collection.http_functions.upload_file.open_http")
@patch("mimetypes.guess_type", return_value=("text/plain", None))
def test_upload_file_successful(
    mock_guess_type: MagicMock,
    mock_urlopen: MagicMock,
    mock_file_open: MagicMock,
    mock_is_file: MagicMock,
    mock_exists: MagicMock,
) -> None:
    """Test case 1: Test successful file upload returns correct response structure."""
    # Mock response
    mock_response = Mock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = b'{"success": true}'
    mock_response.headers = {"Content-Type": "application/json"}
    mock_urlopen.return_value.__enter__.return_value = mock_response

    # Mock Path.name property
    with patch("pathlib.Path.name", "test.txt"):
        result = upload_file("https://example.com/upload", "/tmp/test.txt")

    assert result["status_code"] == 200
    assert result["content"] == '{"success": true}'
    assert result["success"] is True

    # Verify request was made with multipart data
    call_args = mock_urlopen.call_args[0]
    request = call_args[0]
    assert "multipart/form-data" in request.get_header("Content-type")
    assert request.data is not None


@patch("pathlib.Path.exists", return_value=True)
@patch("pathlib.Path.is_file", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=b"test content")
@patch("pyutils_collection.http_functions.upload_file.open_http")
@patch("mimetypes.guess_type", return_value=(None, None))
def test_upload_file_unknown_content_type(
    mock_guess_type: MagicMock,
    mock_urlopen: MagicMock,
    mock_file_open: MagicMock,
    mock_is_file: MagicMock,
    mock_exists: MagicMock,
) -> None:
    """Test case 2: Test file upload when content type cannot be determined uses default."""
    mock_response = Mock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = b"OK"
    mock_response.headers = {}
    mock_urlopen.return_value.__enter__.return_value = mock_response

    with patch("pathlib.Path.name", "unknown_file"):
        upload_file("https://example.com/upload", "/tmp/unknown_file")

    # Verify default content type was used
    call_args = mock_urlopen.call_args[0]
    request = call_args[0]
    body = request.data.decode("utf-8", errors="ignore")
    assert "application/octet-stream" in body


@patch("pathlib.Path.exists", return_value=True)
@patch("pathlib.Path.is_file", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=b"test content")
@patch("pyutils_collection.http_functions.upload_file.open_http")
@patch("mimetypes.guess_type", return_value=("text/plain", None))
def test_upload_file_with_custom_field_name(
    mock_guess_type: MagicMock,
    mock_urlopen: MagicMock,
    mock_file_open: MagicMock,
    mock_is_file: MagicMock,
    mock_exists: MagicMock,
) -> None:
    """Test case 3: Test file upload with custom field name parameter."""
    mock_response = Mock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = b"OK"
    mock_response.headers = {}
    mock_urlopen.return_value.__enter__.return_value = mock_response

    with patch("pathlib.Path.name", "test.txt"):
        upload_file(
            "https://example.com/upload", "/tmp/test.txt", field_name="document"
        )

    # Verify custom field name was used
    call_args = mock_urlopen.call_args[0]
    request = call_args[0]
    body = request.data.decode("utf-8", errors="ignore")
    assert 'name="document"' in body


@patch("pathlib.Path.exists", return_value=True)
@patch("pathlib.Path.is_file", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=b"test content")
@patch("pyutils_collection.http_functions.upload_file.open_http")
@patch("mimetypes.guess_type", return_value=("text/plain", None))
def test_upload_file_with_custom_headers(
    mock_guess_type: MagicMock,
    mock_urlopen: MagicMock,
    mock_file_open: MagicMock,
    mock_is_file: MagicMock,
    mock_exists: MagicMock,
) -> None:
    """Test case 4: Test file upload with additional custom headers."""
    mock_response = Mock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = b"OK"
    mock_response.headers = {}
    mock_urlopen.return_value.__enter__.return_value = mock_response

    headers = {"Authorization": "Bearer token", "X-Custom": "value"}

    with patch("pathlib.Path.name", "test.txt"):
        upload_file("https://example.com/upload", "/tmp/test.txt", headers=headers)

    # Verify headers were added
    call_args = mock_urlopen.call_args[0]
    request = call_args[0]
    assert request.get_header("Authorization") == "Bearer token"
    assert request.get_header("X-custom") == "value"


@patch("pathlib.Path.exists", return_value=True)
@patch("pathlib.Path.is_file", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=b"test content")
@patch("pyutils_collection.http_functions.upload_file.open_http")
@patch("mimetypes.guess_type", return_value=("text/plain", None))
def test_upload_file_with_additional_data(
    mock_guess_type: MagicMock,
    mock_urlopen: MagicMock,
    mock_file_open: MagicMock,
    mock_is_file: MagicMock,
    mock_exists: MagicMock,
) -> None:
    """Test case 5: Test file upload with additional form data fields."""
    mock_response = Mock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = b"OK"
    mock_response.headers = {}
    mock_urlopen.return_value.__enter__.return_value = mock_response

    additional_data = {"description": "Test file", "category": "documents"}

    with patch("pathlib.Path.name", "test.txt"):
        upload_file(
            "https://example.com/upload",
            "/tmp/test.txt",
            additional_data=additional_data,
        )

    # Verify additional data was included in multipart form
    call_args = mock_urlopen.call_args[0]
    request = call_args[0]
    body = request.data.decode("utf-8", errors="ignore")
    assert 'name="description"' in body
    assert "Test file" in body
    assert 'name="category"' in body
    assert "documents" in body


@patch("pathlib.Path.exists", return_value=True)
@patch("pathlib.Path.is_file", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=b"test content")
@patch("pyutils_collection.http_functions.upload_file.open_http")
@patch("mimetypes.guess_type", return_value=("text/plain", None))
def test_upload_file_with_custom_timeout(
    mock_guess_type: MagicMock,
    mock_urlopen: MagicMock,
    mock_file_open: MagicMock,
    mock_is_file: MagicMock,
    mock_exists: MagicMock,
) -> None:
    """Test case 6: Test file upload with custom timeout value."""
    mock_response = Mock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = b"OK"
    mock_response.headers = {}
    mock_urlopen.return_value.__enter__.return_value = mock_response

    with patch("pathlib.Path.name", "test.txt"):
        upload_file("https://example.com/upload", "/tmp/test.txt", timeout=60)

    # Verify timeout was passed correctly
    mock_urlopen.assert_called_once()
    assert mock_urlopen.call_args[1]["timeout"] == 60


@patch("pathlib.Path.exists", return_value=True)
@patch("pathlib.Path.is_file", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=b"test content")
@patch("pyutils_collection.http_functions.upload_file.open_http")
@patch("mimetypes.guess_type", return_value=("text/plain", None))
def test_upload_file_default_timeout(
    mock_guess_type: MagicMock,
    mock_urlopen: MagicMock,
    mock_file_open: MagicMock,
    mock_is_file: MagicMock,
    mock_exists: MagicMock,
) -> None:
    """Test case 7: Test that default timeout is 30 seconds when not specified."""
    mock_response = Mock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = b"OK"
    mock_response.headers = {}
    mock_urlopen.return_value.__enter__.return_value = mock_response

    with patch("pathlib.Path.name", "test.txt"):
        upload_file("https://example.com/upload", "/tmp/test.txt")

        # Check that timeout=30 was passed
        assert mock_urlopen.call_args[1]["timeout"] == 30


def test_upload_file_with_empty_url() -> None:
    """Test case 8: Test upload_file function with empty URL raises ValueError."""
    with pytest.raises(ValueError, match="URL must be a non-empty string"):
        upload_file("", "test.txt")


def test_upload_file_with_whitespace_url() -> None:
    """Test case 9: Test upload_file function with whitespace-only URL raises ValueError."""
    with pytest.raises(ValueError, match="URL must be a non-empty string"):
        upload_file("   ", "test.txt")


def test_upload_file_with_none_url() -> None:
    """Test case 10: Test upload_file function with None URL raises ValueError."""
    with pytest.raises(ValueError, match="URL must be a non-empty string"):
        upload_file(None, "test.txt")


def test_upload_file_with_empty_file_path() -> None:
    """Test case 11: Test upload_file function with empty file path raises ValueError."""
    with pytest.raises(ValueError, match="file_path must be a non-empty string"):
        upload_file("https://example.com/upload", "")


def test_upload_file_with_whitespace_file_path() -> None:
    """Test case 12: Test upload_file function with whitespace-only file path raises ValueError."""
    with pytest.raises(ValueError, match="file_path must be a non-empty string"):
        upload_file("https://example.com/upload", "   ")


def test_upload_file_with_none_file_path() -> None:
    """Test case 13: Test upload_file function with None file path raises ValueError."""
    with pytest.raises(ValueError, match="file_path must be a non-empty string"):
        upload_file("https://example.com/upload", None)


@patch("pathlib.Path.exists", return_value=False)
def test_upload_file_not_found(mock_exists: MagicMock) -> None:
    """Test case 14: Test upload_file function when file doesn't exist raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="File not found"):
        upload_file("https://example.com/upload", "/tmp/nonexistent.txt")


@patch("pathlib.Path.exists", return_value=True)
@patch("pathlib.Path.is_file", return_value=False)
def test_upload_file_not_a_file(
    mock_is_file: MagicMock, mock_exists: MagicMock
) -> None:
    """Test case 15: Test upload_file function when path is not a file raises ValueError."""
    with pytest.raises(ValueError, match="Path is not a file"):
        upload_file("https://example.com/upload", "/tmp/directory")


@patch("pathlib.Path.exists", return_value=True)
@patch("pathlib.Path.is_file", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=b"test content")
@patch("pyutils_collection.http_functions.upload_file.open_http")
@patch("mimetypes.guess_type", return_value=("text/plain", None))
def test_upload_file_http_error(
    mock_guess_type: MagicMock,
    mock_urlopen: MagicMock,
    mock_file_open: MagicMock,
    mock_is_file: MagicMock,
    mock_exists: MagicMock,
) -> None:
    """Test case 16: Test file upload with HTTP error response returns error details."""
    from email.message import Message

    hdrs = Message()
    hdrs["Content-Type"] = "application/json"
    fp_mock = Mock()
    fp_mock.read = Mock(return_value=b'{"error": "invalid file"}')
    error = urllib.error.HTTPError(
        url="https://example.com/upload",
        code=400,
        msg="Bad Request",
        hdrs=hdrs,
        fp=fp_mock,
    )
    mock_urlopen.side_effect = error

    with patch("pathlib.Path.name", "test.txt"):
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            upload_file("https://example.com/upload", "/tmp/test.txt")
        assert exc_info.value.code == 400
        assert exc_info.value.msg == "Bad Request"


@patch("pathlib.Path.exists", return_value=True)
@patch("pathlib.Path.is_file", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=b"test content")
@patch("pyutils_collection.http_functions.upload_file.open_http")
@patch("mimetypes.guess_type", return_value=("text/plain", None))
def test_upload_file_url_error(
    mock_guess_type: MagicMock,
    mock_urlopen: MagicMock,
    mock_file_open: MagicMock,
    mock_is_file: MagicMock,
    mock_exists: MagicMock,
) -> None:
    """Test case 17: Test file upload when request fails returns error details."""
    mock_urlopen.side_effect = urllib.error.URLError("Connection failed")

    with patch("pathlib.Path.name", "test.txt"):
        with pytest.raises(urllib.error.URLError, match="Connection failed"):
            upload_file("https://example.com/upload", "/tmp/test.txt")
