"""Remove selected URL query parameters."""

from collections.abc import Iterable
from urllib.parse import unquote_plus, urlsplit


def remove_query_params(url: str, keys: Iterable[str]) -> str:
    """
    Remove every occurrence of selected query keys while preserving other fields.

    Parameters
    ----------
    url : str
        Nonempty absolute or relative URL.
    keys : Iterable[str]
        Decoded, case-sensitive query names. A bare string is not accepted.

    Returns
    -------
    str
        URL with matching fields removed. Remaining fields retain their order,
        repeated keys, blank values, and original percent encoding.

    Raises
    ------
    TypeError
        If url is not a string or keys is not an iterable of strings.
    ValueError
        If url is empty or cannot be parsed.

    Examples
    --------
    >>> remove_query_params('/search?q=python&utm_source=mail#top', ['utm_source'])
    '/search?q=python#top'

    Complexity
    ----------
    Time and space: O(n + k), for URL length n and number of keys k.
    """
    if not isinstance(url, str):
        raise TypeError("url must be a string")
    if not url:
        raise ValueError("url cannot be empty")
    if isinstance(keys, (str, bytes)):
        raise TypeError("keys must be an iterable of strings")
    names = list(keys)
    if not all(isinstance(key, str) for key in names):
        raise TypeError("keys must be an iterable of strings")
    removed = set(names)
    urlsplit(url)  # Validate the URL while preserving its original spelling below.
    before_fragment, fragment_separator, fragment = url.partition("#")
    base, query_separator, query = before_fragment.partition("?")
    if not query_separator:
        return url
    fields = query.split("&")
    kept = [
        field
        for field in fields
        if unquote_plus(field.partition("=")[0]) not in removed
    ]
    if kept == fields:
        return url
    query_part = "?" + "&".join(kept) if kept else ""
    return base + query_part + fragment_separator + fragment


__all__ = ["remove_query_params"]
