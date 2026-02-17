"""
Tests for remove_html_tags function.
"""

from typing import Any, cast

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.regex]
from pyutils_collection.regex_functions.remove_html_tags import remove_html_tags


def test_remove_html_tags_basic() -> None:
    """Test basic HTML tag removal."""
    html = "<p>Hello world</p>"
    result = remove_html_tags(html)
    assert result == "Hello world"


def test_remove_html_tags_nested() -> None:
    """Test nested HTML tags."""
    html = "<div><span>Text</span></div>"
    result = remove_html_tags(html)
    assert result == "Text"


def test_remove_html_tags_with_attributes() -> None:
    """Test tags with attributes."""
    html = '<p class="test" id="main">Content</p>'
    result = remove_html_tags(html)
    assert result == "Content"


def test_remove_html_tags_comments() -> None:
    """Test HTML comment removal."""
    html = "<!-- Comment --><p>Content</p>"
    result = remove_html_tags(html)
    assert result == "Content"


def test_remove_html_tags_script() -> None:
    """Test script tag removal."""
    html = "<p>Text</p><script>alert('test');</script>"
    result = remove_html_tags(html)
    assert result == "Text"


def test_remove_html_tags_multiple_elements() -> None:
    """Test multiple elements."""
    html = "<p>Hello</p> <b>world</b>!"
    result = remove_html_tags(html)
    assert "Hello" in result and "world" in result


def test_remove_html_tags_empty() -> None:
    """Test empty HTML."""
    html = "<p></p>"
    result = remove_html_tags(html)
    assert result == ""


def test_remove_html_tags_invalid_type_text() -> None:
    """Test TypeError for invalid text type."""
    with pytest.raises(TypeError, match="text must be str"):
        remove_html_tags(cast(Any, 123))


def test_remove_html_tags_invalid_type_keep_text() -> None:
    """Test TypeError for invalid keep_text type."""
    with pytest.raises(TypeError, match="keep_text must be bool"):
        remove_html_tags("<p>test</p>", keep_text=cast(Any, "yes"))
