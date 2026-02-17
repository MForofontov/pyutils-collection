"""
Tests for extract_urls function.
"""

from typing import Any, cast

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.regex]
from pyutils_collection.regex_functions.extract_urls import extract_urls


def test_extract_urls_basic() -> None:
    """Test basic URL extraction."""
    text = "Visit https://example.com"
    result = extract_urls(text)
    assert result == ["https://example.com"]


def test_extract_urls_multiple_schemes() -> None:
    """Test extracting URLs with different schemes."""
    text = "Sites: https://example.com and http://test.org and ftp://files.com"
    result = extract_urls(text)
    assert len(result) == 3


def test_extract_urls_filter_https_only() -> None:
    """Test filtering by specific scheme."""
    text = "Links: https://secure.com and http://insecure.com"
    result = extract_urls(text, include_schemes=["https"])
    assert result == ["https://secure.com"]


def test_extract_urls_unique() -> None:
    """Test unique URL extraction."""
    text = "Link: https://example.com and https://example.com"
    result = extract_urls(text, unique=True)
    assert result == ["https://example.com"]


def test_extract_urls_non_unique() -> None:
    """Test non-unique URL extraction."""
    text = "https://test.com twice: https://test.com"
    result = extract_urls(text, unique=False)
    assert len(result) == 2


def test_extract_urls_with_paths() -> None:
    """Test URLs with paths and parameters."""
    text = "API: https://api.example.com/v1/users?id=123&sort=asc"
    result = extract_urls(text)
    assert len(result) == 1
    assert "api.example.com" in result[0]


def test_extract_urls_no_matches() -> None:
    """Test text with no URLs."""
    text = "This is just plain text"
    result = extract_urls(text)
    assert result == []


def test_extract_urls_invalid_type_text() -> None:
    """Test TypeError for invalid text type."""
    with pytest.raises(TypeError, match="text must be str"):
        extract_urls(cast(Any, 123))


def test_extract_urls_invalid_type_schemes() -> None:
    """Test TypeError for invalid include_schemes type."""
    with pytest.raises(TypeError, match="include_schemes must be list"):
        extract_urls("https://test.com", include_schemes=cast(Any, "https"))
