"""Unit tests for restore_session function."""

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock

import pytest

try:
    from pyutils_collection.playwright_functions.restore_session import restore_session
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    restore_session = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.playwright_functions,
    pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="playwright not installed"),
]


def test_restore_session_cookies_only(tmp_path: Path) -> None:
    """
    Test case 1: Restore session with cookies only.
    """
    # Arrange
    mock_context = MagicMock()
    
    session_data = {
        "cookies": [
            {"name": "session", "value": "abc123", "domain": ".example.com"},
            {"name": "user", "value": "john", "domain": ".example.com"},
        ],
        "storage": {},
    }
    
    session_file = tmp_path / "session.json"
    with open(session_file, "w") as f:
        json.dump(session_data, f)
    
    # Act
    restore_session(mock_context, str(session_file))
    
    # Assert
    mock_context.add_cookies.assert_called_once_with(session_data["cookies"])


def test_restore_session_with_storage(tmp_path: Path) -> None:
    """
    Test case 2: Restore session with localStorage and sessionStorage.
    """
    # Arrange
    mock_context = MagicMock()
    mock_page = MagicMock()
    mock_context.pages = []  # No existing pages
    mock_context.new_page.return_value = mock_page
    
    session_data = {
        "cookies": [],
        "storage": {
            "localStorage": {"key1": "value1", "key2": "value2"},
            "sessionStorage": {"skey1": "svalue1"},
        },
    }
    
    session_file = tmp_path / "session.json"
    with open(session_file, "w") as f:
        json.dump(session_data, f)
    
    # Act
    restore_session(mock_context, str(session_file), url="https://example.com")
    
    # Assert
    mock_page.goto.assert_called_once_with("https://example.com")
    assert mock_page.evaluate.call_count == 3  # 2 localStorage + 1 sessionStorage


def test_restore_session_uses_existing_page(tmp_path: Path) -> None:
    """
    Test case 3: Use existing page if available for storage restoration.
    """
    # Arrange
    mock_context = MagicMock()
    mock_page = MagicMock()
    mock_context.pages = [mock_page]  # Existing page
    
    session_data = {
        "cookies": [],
        "storage": {
            "localStorage": {"key1": "value1"},
            "sessionStorage": {},
        },
    }
    
    session_file = tmp_path / "session.json"
    with open(session_file, "w") as f:
        json.dump(session_data, f)
    
    # Act
    restore_session(mock_context, str(session_file), url="https://example.com")
    
    # Assert
    mock_context.new_page.assert_not_called()  # Should use existing page
    mock_page.goto.assert_called_once()


def test_restore_session_storage_without_url() -> None:
    """
    Test case 4: ValueError when storage exists but no URL provided.
    """
    # Arrange
    mock_context = MagicMock()
    
    session_data = {
        "cookies": [],
        "storage": {
            "localStorage": {"key": "value"},
            "sessionStorage": {},
        },
    }
    
    session_file = Path("/tmp/session.json")
    with open(session_file, "w") as f:
        json.dump(session_data, f)
    
    # Act & Assert
    with pytest.raises(RuntimeError, match="Failed to restore session"):
        restore_session(mock_context, str(session_file))


def test_restore_session_file_not_found() -> None:
    """
    Test case 5: FileNotFoundError for non-existent session file.
    """
    # Arrange
    mock_context = MagicMock()
    
    # Act & Assert
    with pytest.raises(FileNotFoundError, match="Session file not found"):
        restore_session(mock_context, "/nonexistent/session.json")


def test_restore_session_invalid_session_file_type() -> None:
    """
    Test case 6: TypeError for non-string session_file.
    """
    # Arrange
    mock_context = MagicMock()
    
    # Act & Assert
    with pytest.raises(TypeError, match="session_file must be a string"):
        restore_session(mock_context, 123)  # type: ignore


def test_restore_session_empty_session_file() -> None:
    """
    Test case 7: ValueError for empty session_file.
    """
    # Arrange
    mock_context = MagicMock()
    
    # Act & Assert
    with pytest.raises(ValueError, match="session_file cannot be empty"):
        restore_session(mock_context, "")


def test_restore_session_invalid_url_type(tmp_path: Path) -> None:
    """
    Test case 8: TypeError for invalid URL type.
    """
    # Arrange
    mock_context = MagicMock()
    
    session_data: dict[str, list[Any] | dict[str, Any]] = {"cookies": [], "storage": {}}
    session_file = tmp_path / "session.json"
    with open(session_file, "w") as f:
        json.dump(session_data, f)
    
    # Act & Assert
    with pytest.raises(TypeError, match="url must be a string or None"):
        restore_session(mock_context, str(session_file), url=123)  # type: ignore


def test_restore_session_with_logger(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """
    Test case 9: Session restore with logging enabled.
    """
    # Arrange
    import logging
    logger = logging.getLogger("test_logger")
    
    mock_context = MagicMock()
    
    session_data = {
        "cookies": [{"name": "test", "value": "val"}],
        "storage": {},
    }
    
    session_file = tmp_path / "session.json"
    with open(session_file, "w") as f:
        json.dump(session_data, f)
    
    # Act
    with caplog.at_level(logging.DEBUG):
        restore_session(mock_context, str(session_file), logger=logger)
    
    # Assert
    assert "Restoring session from" in caplog.text
    assert "Restored 1 cookies" in caplog.text
    assert "Session restored successfully" in caplog.text


def test_restore_session_multiple_storage_items(tmp_path: Path) -> None:
    """
    Test case 10: Restore multiple localStorage and sessionStorage items.
    """
    # Arrange
    mock_context = MagicMock()
    mock_page = MagicMock()
    mock_context.pages = [mock_page]
    
    session_data = {
        "cookies": [],
        "storage": {
            "localStorage": {f"lkey{i}": f"lval{i}" for i in range(5)},
            "sessionStorage": {f"skey{i}": f"sval{i}" for i in range(3)},
        },
    }
    
    session_file = tmp_path / "session.json"
    with open(session_file, "w") as f:
        json.dump(session_data, f)
    
    # Act
    restore_session(mock_context, str(session_file), url="https://example.com")
    
    # Assert
    assert mock_page.evaluate.call_count == 8  # 5 localStorage + 3 sessionStorage


def test_restore_session_empty_storage(tmp_path: Path) -> None:
    """
    Test case 11: Restore session with empty storage.
    """
    # Arrange
    mock_context = MagicMock()
    
    session_data = {
        "cookies": [{"name": "test", "value": "val"}],
        "storage": {
            "localStorage": {},
            "sessionStorage": {},
        },
    }
    
    session_file = tmp_path / "session.json"
    with open(session_file, "w") as f:
        json.dump(session_data, f)
    
    # Act
    restore_session(mock_context, str(session_file))
    
    # Assert
    mock_context.add_cookies.assert_called_once()
    # No page navigation should happen for empty storage


def test_restore_session_only_local_storage(tmp_path: Path) -> None:
    """
    Test case 12: Restore session with only localStorage (no sessionStorage).
    """
    # Arrange
    mock_context = MagicMock()
    mock_page = MagicMock()
    mock_context.pages = [mock_page]
    
    session_data = {
        "cookies": [],
        "storage": {
            "localStorage": {"key": "value"},
            "sessionStorage": {},
        },
    }
    
    session_file = tmp_path / "session.json"
    with open(session_file, "w") as f:
        json.dump(session_data, f)
    
    # Act
    restore_session(mock_context, str(session_file), url="https://example.com")
    
    # Assert
    mock_page.goto.assert_called_once()
    assert mock_page.evaluate.call_count == 1  # Only localStorage


def test_restore_session_invalid_json(tmp_path: Path) -> None:
    """
    Test case 13: RuntimeError for invalid JSON file.
    """
    # Arrange
    mock_context = MagicMock()
    
    session_file = tmp_path / "invalid.json"
    with open(session_file, "w") as f:
        f.write("{ invalid json")
    
    # Act & Assert
    with pytest.raises(RuntimeError, match="Failed to restore session"):
        restore_session(mock_context, str(session_file))


def test_restore_session_invalid_logger_type() -> None:
    """
    Test case 14: TypeError for invalid logger type.
    """
    # Arrange
    mock_context = MagicMock()
    
    # Act & Assert
    with pytest.raises(TypeError, match="logger must be an instance of logging.Logger"):
        restore_session(mock_context, "session.json", logger="not_a_logger")  # type: ignore


def test_restore_session_missing_cookies_key(tmp_path: Path) -> None:
    """
    Test case 15: Handle missing cookies key in session data.
    """
    # Arrange
    mock_context = MagicMock()
    
    session_data: dict[str, dict[str, Any]] = {
        "storage": {},
    }  # Missing cookies key
    
    session_file = tmp_path / "session.json"
    with open(session_file, "w") as f:
        json.dump(session_data, f)
    
    # Act
    restore_session(mock_context, str(session_file))
    
    # Assert - should handle gracefully, no cookies to add
    mock_context.add_cookies.assert_not_called()


def test_restore_session_storage_logging(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """
    Test case 16: Logs storage restoration details.
    """
    # Arrange
    import logging
    logger = logging.getLogger("test_logger")
    
    mock_context = MagicMock()
    mock_page = MagicMock()
    mock_context.pages = [mock_page]
    
    session_data = {
        "cookies": [],
        "storage": {
            "localStorage": {"key1": "val1", "key2": "val2"},
            "sessionStorage": {"skey": "sval"},
        },
    }
    
    session_file = tmp_path / "session.json"
    with open(session_file, "w") as f:
        json.dump(session_data, f)
    
    # Act
    with caplog.at_level(logging.DEBUG):
        restore_session(mock_context, str(session_file), url="https://example.com", logger=logger)
    
    # Assert
    assert "Restored 2 localStorage items" in caplog.text
    assert "Restored 1 sessionStorage items" in caplog.text


def test_restore_session_goto_failure(tmp_path: Path) -> None:
    """
    Test case 17: RuntimeError when page navigation fails.
    """
    # Arrange
    mock_context = MagicMock()
    mock_page = MagicMock()
    mock_context.pages = [mock_page]
    mock_page.goto.side_effect = Exception("Navigation failed")
    
    session_data = {
        "cookies": [],
        "storage": {
            "localStorage": {"key": "value"},
            "sessionStorage": {},
        },
    }
    
    session_file = tmp_path / "session.json"
    with open(session_file, "w") as f:
        json.dump(session_data, f)
    
    # Act & Assert
    with pytest.raises(RuntimeError, match="Failed to restore session"):
        restore_session(mock_context, str(session_file), url="https://example.com")
