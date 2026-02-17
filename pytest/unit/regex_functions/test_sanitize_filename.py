"""
Tests for sanitize_filename function.
"""

from typing import Any, cast

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.regex]
from pyutils_collection.regex_functions.sanitize_filename import sanitize_filename


def test_sanitize_filename_invalid_chars() -> None:
    """Test removing invalid characters."""
    filename = "file_name:test.txt"
    result = sanitize_filename(filename)
    assert ":" not in result
    assert result == "file_name_test.txt"


def test_sanitize_filename_custom_replacement() -> None:
    """Test custom replacement character."""
    filename = "file*name?.txt"
    result = sanitize_filename(filename, replacement="-")
    assert result == "file-name-.txt"


def test_sanitize_filename_leading_trailing() -> None:
    """Test removing leading/trailing spaces."""
    filename = "  file.txt  "
    result = sanitize_filename(filename)
    assert result == "file.txt"


def test_sanitize_filename_max_length() -> None:
    """Test maximum length enforcement."""
    filename = "a" * 300 + ".txt"
    result = sanitize_filename(filename, max_length=50)
    assert len(result) <= 50
    assert result.endswith(".txt")


def test_sanitize_filename_preserve_extension() -> None:
    """Test preserving file extension."""
    filename = "very_long_filename" * 20 + ".txt"
    result = sanitize_filename(filename, max_length=20)
    assert result.endswith(".txt")


def test_sanitize_filename_windows_reserved() -> None:
    """Test handling Windows reserved names."""
    filename = "CON.txt"
    result = sanitize_filename(filename)
    assert result != "CON.txt"


def test_sanitize_filename_multiple_dots() -> None:
    """Test filename with multiple dots."""
    filename = "file.backup.txt"
    result = sanitize_filename(filename)
    assert result == "file.backup.txt"


def test_sanitize_filename_invalid_type_filename() -> None:
    """Test TypeError for invalid filename type."""
    with pytest.raises(TypeError, match="filename must be str"):
        sanitize_filename(cast(Any, 123))


def test_sanitize_filename_invalid_max_length() -> None:
    """Test ValueError for invalid max_length."""
    with pytest.raises(ValueError, match="max_length must be positive"):
        sanitize_filename("test.txt", max_length=0)


def test_sanitize_filename_empty_result() -> None:
    """Test ValueError for empty sanitized filename."""
    with pytest.raises(ValueError, match="empty or invalid"):
        sanitize_filename("///")
