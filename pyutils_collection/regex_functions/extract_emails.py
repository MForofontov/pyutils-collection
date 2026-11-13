"""
Extract email addresses from text.
"""

import re
from typing import TypeVar

T = TypeVar("T")


def extract_emails(
    text: str,
    unique: bool = True,
) -> list[str]:
    """
    Extract all email addresses from text.

    Parameters
    ----------
    text : str
        Input text to search for email addresses.
    unique : bool, optional
        Return only unique emails (by default True).

    Returns
    -------
    list[str]
        List of extracted email addresses.

    Raises
    ------
    TypeError
        If parameters are of wrong type.

    Examples
    --------
    >>> text = "Contact us at support@example.com or sales@example.com"
    >>> extract_emails(text)
    ['support@example.com', 'sales@example.com']

    >>> text = "Email: user@test.com, also user@test.com"
    >>> extract_emails(text, unique=True)
    ['user@test.com']

    >>> extract_emails(text, unique=False)
    ['user@test.com', 'user@test.com']

    Notes
    -----
    Uses RFC 5322 simplified email pattern.
    Does not validate if email actually exists.

    Complexity
    ----------
    Time: O(n) where n is length of text
    Space: O(m) where m is number of emails found
    """
    # Type validation
    if not isinstance(text, str):
        raise TypeError(f"text must be str, got {type(text).__name__}")
    if not isinstance(unique, bool):
        raise TypeError(f"unique must be bool, got {type(unique).__name__}")

    # RFC 5322 simplified email pattern
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

    matches = re.findall(pattern, text)

    if unique:
        # Preserve order while removing duplicates
        seen = set()
        result = []
        for email in matches:
            email_lower = email.lower()
            if email_lower not in seen:
                seen.add(email_lower)
                result.append(email)
        return result

    return matches


__all__ = ["extract_emails"]
