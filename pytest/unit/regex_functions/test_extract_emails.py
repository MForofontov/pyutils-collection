"""
Tests for extract_emails function.
"""

from typing import Any, cast

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.regex]
from pyutils_collection.regex_functions.extract_emails import extract_emails


def test_extract_emails_basic() -> None:
    """Test basic email extraction."""
    text = "Contact us at support@example.com"
    result = extract_emails(text)
    assert result == ["support@example.com"]


def test_extract_emails_multiple() -> None:
    """Test extracting multiple emails."""
    text = "Email: user@test.com or admin@site.org"
    result = extract_emails(text)
    assert len(result) == 2
    assert "user@test.com" in result
    assert "admin@site.org" in result


def test_extract_emails_unique() -> None:
    """Test unique email extraction."""
    text = "Contact: user@test.com and user@test.com"
    result = extract_emails(text, unique=True)
    assert result == ["user@test.com"]


def test_extract_emails_non_unique() -> None:
    """Test non-unique email extraction."""
    text = "Email: test@example.com twice: test@example.com"
    result = extract_emails(text, unique=False)
    assert len(result) == 2
    assert result == ["test@example.com", "test@example.com"]


def test_extract_emails_case_insensitive_unique() -> None:
    """Test case-insensitive uniqueness."""
    text = "Contact: User@Test.com and user@test.com"
    result = extract_emails(text, unique=True)
    assert len(result) == 1


def test_extract_emails_no_matches() -> None:
    """Test text with no emails."""
    text = "This text has no email addresses"
    result = extract_emails(text)
    assert result == []


def test_extract_emails_complex_format() -> None:
    """Test complex email formats."""
    text = "Reach john.doe+tag@sub.example.co.uk"
    result = extract_emails(text)
    assert "john.doe+tag@sub.example.co.uk" in result


def test_extract_emails_invalid_type_text() -> None:
    """Test TypeError for invalid text type."""
    with pytest.raises(TypeError, match="text must be str"):
        extract_emails(cast(Any, 123))


def test_extract_emails_invalid_type_unique() -> None:
    """Test TypeError for invalid unique type."""
    with pytest.raises(TypeError, match="unique must be bool"):
        extract_emails("test@example.com", unique=cast(Any, "yes"))
