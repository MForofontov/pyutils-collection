"""Unit tests for save_session function."""

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

try:
    from pyutils_collection.playwright_functions.save_session import save_session
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    save_session = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.playwright_functions,
    pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="playwright not installed"),
]


def test_save_session_basic_success(tmp_path: Path) -> None:
    """
    Test case 1: Basic session save with cookies only.
    """
    # Arrange
    mock_context = MagicMock()
    mock_cookies = [
        {"name": "session", "value": "abc123", "domain": ".example.com"},
        {"name": "user", "value": "john", "domain": ".example.com"},
    ]
    mock_context.cookies.return_value = mock_cookies
    mock_context.pages = []  # No pages, won't save storage
    
    session_file = str(tmp_path / "session.json")
    
    # Act
    save_session(mock_context, session_file, include_storage=False)
    
    # Assert
    assert Path(session_file).exists()
    with open(session_file) as f:
        data = json.load(f)
    assert data["cookies"] == mock_cookies
    assert data["storage"] == {}


def test_save_session_with_storage(tmp_path: Path) -> None:
    """
    Test case 2: Save session with localStorage and sessionStorage.
    """
    # Arrange
    mock_context = MagicMock()
    mock_page = MagicMock()
    mock_context.cookies.return_value = []
    mock_context.pages = [mock_page]
    
    # Mock storage data
    mock_page.evaluate.side_effect = [
        [["key1", "value1"], ["key2", "value2"]],  # localStorage
        [["skey1", "svalue1"]],  # sessionStorage
    ]
    
    session_file = str(tmp_path / "session.json")
    
    # Act
    save_session(mock_context, session_file, include_storage=True)
    
    # Assert
    with open(session_file) as f:
        data = json.load(f)
    assert data["storage"]["localStorage"] == {"key1": "value1", "key2": "value2"}
    assert data["storage"]["sessionStorage"] == {"skey1": "svalue1"}


def test_save_session_creates_parent_directory(tmp_path: Path) -> None:
    """
    Test case 3: Automatically creates parent directories.
    """
    # Arrange
    mock_context = MagicMock()
    mock_context.cookies.return_value = []
    mock_context.pages = []
    
    session_file = str(tmp_path / "nested" / "deep" / "session.json")
    
    # Act
    save_session(mock_context, session_file)
    
    # Assert
    assert Path(session_file).exists()
    assert Path(session_file).parent.exists()


def test_save_session_storage_error_continues(tmp_path: Path) -> None:
    """
    Test case 4: Continues saving when storage retrieval fails.
    """
    # Arrange
    mock_context = MagicMock()
    mock_page = MagicMock()
    mock_context.cookies.return_value = [{"name": "test", "value": "123"}]
    mock_context.pages = [mock_page]
    
    # Mock storage retrieval failure
    mock_page.evaluate.side_effect = Exception("Storage access denied")
    
    session_file = str(tmp_path / "session.json")
    
    # Act
    save_session(mock_context, session_file, include_storage=True)
    
    # Assert - should still save cookies
    with open(session_file) as f:
        data = json.load(f)
    assert len(data["cookies"]) == 1
    assert data["storage"]["localStorage"] == {}
    assert data["storage"]["sessionStorage"] == {}


def test_save_session_invalid_session_file_type() -> None:
    """
    Test case 5: TypeError for non-string session_file.
    """
    # Arrange
    mock_context = MagicMock()
    
    # Act & Assert
    with pytest.raises(TypeError, match="session_file must be a string"):
        save_session(mock_context, 123)  # type: ignore


def test_save_session_empty_session_file() -> None:
    """
    Test case 6: ValueError for empty session_file.
    """
    # Arrange
    mock_context = MagicMock()
    
    # Act & Assert
    with pytest.raises(ValueError, match="session_file cannot be empty"):
        save_session(mock_context, "")


def test_save_session_invalid_include_storage_type() -> None:
    """
    Test case 7: TypeError for invalid include_storage type.
    """
    # Arrange
    mock_context = MagicMock()
    
    # Act & Assert
    with pytest.raises(TypeError, match="include_storage must be a boolean"):
        save_session(mock_context, "session.json", include_storage="yes")  # type: ignore


def test_save_session_with_logger(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """
    Test case 8: Session save with logging enabled.
    """
    # Arrange
    import logging
    logger = logging.getLogger("test_logger")
    
    mock_context = MagicMock()
    mock_context.cookies.return_value = [{"name": "test", "value": "val"}]
    mock_context.pages = []
    
    session_file = str(tmp_path / "session.json")
    
    # Act
    with caplog.at_level(logging.DEBUG):
        save_session(mock_context, session_file, logger=logger)
    
    # Assert
    assert "Saving session to" in caplog.text
    assert "Retrieved 1 cookies" in caplog.text
    assert "Session saved successfully" in caplog.text


def test_save_session_no_pages_no_storage(tmp_path: Path) -> None:
    """
    Test case 9: No storage saved when no pages exist in context.
    """
    # Arrange
    mock_context = MagicMock()
    mock_context.cookies.return_value = []
    mock_context.pages = []  # No pages available
    
    session_file = str(tmp_path / "session.json")
    
    # Act
    save_session(mock_context, session_file, include_storage=True)
    
    # Assert
    with open(session_file) as f:
        data = json.load(f)
    assert "storage" in data
    # Storage should be empty since no pages available


def test_save_session_multiple_cookies(tmp_path: Path) -> None:
    """
    Test case 10: Save session with multiple cookies.
    """
    # Arrange
    mock_context = MagicMock()
    cookies = [
        {"name": f"cookie{i}", "value": f"value{i}", "domain": ".example.com"}
        for i in range(10)
    ]
    mock_context.cookies.return_value = cookies
    mock_context.pages = []
    
    session_file = str(tmp_path / "session.json")
    
    # Act
    save_session(mock_context, session_file)
    
    # Assert
    with open(session_file) as f:
        data = json.load(f)
    assert len(data["cookies"]) == 10


def test_save_session_write_failure(tmp_path: Path) -> None:
    """
    Test case 11: RuntimeError when file write fails.
    """
    # Arrange
    mock_context = MagicMock()
    mock_context.cookies.return_value = []
    mock_context.pages = []
    
    # Act & Assert
    with patch(
        "pyutils_collection.playwright_functions.save_session.json.dump",
        side_effect=OSError("disk full"),
    ), pytest.raises(RuntimeError, match="Failed to save session"):
        save_session(mock_context, str(tmp_path / "session.json"))


def test_save_session_partial_write_preserves_original(tmp_path: Path) -> None:
    mock_context = MagicMock()
    mock_context.cookies.return_value = []
    mock_context.pages = []
    session = tmp_path / "session.json"
    session.write_text("original", encoding="utf-8")

    def fail_after_write(data, stream, **kwargs):
        stream.write("partial")
        raise OSError("disk full")

    with patch(
        "pyutils_collection.playwright_functions.save_session.json.dump",
        side_effect=fail_after_write,
    ), pytest.raises(RuntimeError, match="disk full"):
        save_session(mock_context, str(session))

    assert session.read_text(encoding="utf-8") == "original"
    assert list(tmp_path.iterdir()) == [session]


def test_save_session_replacement_failure_preserves_original(tmp_path: Path) -> None:
    mock_context = MagicMock()
    mock_context.cookies.return_value = []
    mock_context.pages = []
    session = tmp_path / "session.json"
    session.write_text("original", encoding="utf-8")

    with patch(
        "pyutils_collection.playwright_functions.save_session.os.replace",
        side_effect=PermissionError("replacement denied"),
    ), pytest.raises(RuntimeError, match="replacement denied"):
        save_session(mock_context, str(session))

    assert session.read_text(encoding="utf-8") == "original"
    assert list(tmp_path.iterdir()) == [session]


def test_save_session_invalid_logger_type() -> None:
    """
    Test case 12: TypeError for invalid logger type.
    """
    # Arrange
    mock_context = MagicMock()
    
    # Act & Assert
    with pytest.raises(TypeError, match="logger must be an instance of logging.Logger"):
        save_session(mock_context, "session.json", logger="not_a_logger")  # type: ignore


def test_save_session_empty_storage(tmp_path: Path) -> None:
    """
    Test case 13: Save session with empty storage.
    """
    # Arrange
    mock_context = MagicMock()
    mock_page = MagicMock()
    mock_context.cookies.return_value = []
    mock_context.pages = [mock_page]
    
    # Mock empty storage
    mock_page.evaluate.side_effect = [[], []]  # Empty localStorage and sessionStorage
    
    session_file = str(tmp_path / "session.json")
    
    # Act
    save_session(mock_context, session_file, include_storage=True)
    
    # Assert
    with open(session_file) as f:
        data = json.load(f)
    assert data["storage"]["localStorage"] == {}
    assert data["storage"]["sessionStorage"] == {}


def test_save_session_storage_warning_logged(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """
    Test case 14: Warning logged when storage retrieval fails.
    """
    # Arrange
    import logging
    logger = logging.getLogger("test_logger")
    
    mock_context = MagicMock()
    mock_page = MagicMock()
    mock_context.cookies.return_value = []
    mock_context.pages = [mock_page]
    
    mock_page.evaluate.side_effect = [
        Exception("localStorage error"),
        Exception("sessionStorage error"),
    ]
    
    session_file = str(tmp_path / "session.json")
    
    # Act
    with caplog.at_level(logging.WARNING):
        save_session(mock_context, session_file, include_storage=True, logger=logger)
    
    # Assert
    assert "Could not retrieve localStorage" in caplog.text
    assert "Could not retrieve sessionStorage" in caplog.text


def test_save_session_json_formatting(tmp_path: Path) -> None:
    """
    Test case 15: JSON file is properly formatted with indentation.
    """
    # Arrange
    mock_context = MagicMock()
    mock_context.cookies.return_value = [{"name": "test", "value": "val"}]
    mock_context.pages = []
    
    session_file = str(tmp_path / "session.json")
    
    # Act
    save_session(mock_context, session_file)
    
    # Assert
    with open(session_file) as f:
        content = f.read()
    # Check that it's indented (not minified)
    assert "\n" in content
    assert "  " in content  # Has indentation
