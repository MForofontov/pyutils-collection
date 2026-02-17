"""
Tests for remove_extra_whitespace function.
"""

from typing import Any, cast

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.regex]
from pyutils_collection.regex_functions.remove_extra_whitespace import remove_extra_whitespace


def test_remove_extra_whitespace_multiple_spaces() -> None:
    """Test removing multiple spaces."""
    text = "Hello    world"
    result = remove_extra_whitespace(text)
    assert result == "Hello world"


def test_remove_extra_whitespace_leading_trailing() -> None:
    """Test removing leading and trailing whitespace."""
    text = "  test  "
    result = remove_extra_whitespace(text)
    assert result == "test"


def test_remove_extra_whitespace_newlines() -> None:
    """Test removing multiple newlines."""
    text = "Line1\n\n\nLine2"
    result = remove_extra_whitespace(text)
    assert result == "Line1 Line2"


def test_remove_extra_whitespace_preserve_newlines() -> None:
    """Test preserving newlines."""
    text = "Line1\n\n\nLine2"
    result = remove_extra_whitespace(text, preserve_newlines=True)
    assert result == "Line1\nLine2"


def test_remove_extra_whitespace_tabs() -> None:
    """Test converting tabs to spaces."""
    text = "Hello\t\tworld"
    result = remove_extra_whitespace(text)
    assert result == "Hello world"


def test_remove_extra_whitespace_mixed() -> None:
    """Test mixed whitespace."""
    text = "  Multiple   \t  spaces  \n\n  and newlines  "
    result = remove_extra_whitespace(text)
    assert "Multiple" in result and "spaces" in result


def test_remove_extra_whitespace_empty() -> None:
    """Test empty string."""
    text = "   "
    result = remove_extra_whitespace(text)
    assert result == ""


def test_remove_extra_whitespace_invalid_type_text() -> None:
    """Test TypeError for invalid text type."""
    with pytest.raises(TypeError, match="text must be str"):
        remove_extra_whitespace(cast(Any, 123))


def test_remove_extra_whitespace_invalid_type_preserve() -> None:
    """Test TypeError for invalid preserve_newlines type."""
    with pytest.raises(TypeError, match="preserve_newlines must be bool"):
        remove_extra_whitespace("test", preserve_newlines=cast(Any, "yes"))
