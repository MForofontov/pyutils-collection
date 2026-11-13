"""
Extract links from HTML content.
"""

from typing import cast
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag


def extract_links(
    element: BeautifulSoup | Tag,
    absolute: bool = False,
    base_url: str | None = None,
) -> list[str]:
    """
    Extract all links from HTML element.

    Parameters
    ----------
    element : BeautifulSoup | Tag
        HTML element to extract links from.
    absolute : bool, optional
        Whether to convert to absolute URLs (by default False).
    base_url : str | None, optional
        Base URL for absolute conversion (by default None).

    Returns
    -------
    list[str]
        List of extracted URLs.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If absolute is True but base_url is None.

    Examples
    --------
    >>> from bs4 import BeautifulSoup
    >>> html = '<a href="/page1">Link1</a><a href="/page2">Link2</a>'
    >>> soup = BeautifulSoup(html, "html.parser")
    >>> extract_links(soup)
    ['/page1', '/page2']

    >>> extract_links(soup, absolute=True, base_url="https://example.com")
    ['https://example.com/page1', 'https://example.com/page2']

    Notes
    -----
    Only extracts links from <a> tags with href attributes.
    Absolute conversion resolves URL references against the base document URL,
    including parent paths, network paths, queries, and fragments. Explicit
    schemes are preserved; this function does not filter navigation targets.

    Complexity
    ----------
    Time: O(n), Space: O(m), where n is element size, m is number of links
    """
    if not isinstance(element, (BeautifulSoup, Tag)):
        raise TypeError(
            f"element must be BeautifulSoup or Tag, got {type(element).__name__}"
        )
    if not isinstance(absolute, bool):
        raise TypeError(f"absolute must be a boolean, got {type(absolute).__name__}")
    if base_url is not None and not isinstance(base_url, str):
        raise TypeError(
            f"base_url must be a string or None, got {type(base_url).__name__}"
        )

    if absolute and base_url is None:
        raise ValueError("base_url must be provided when absolute is True")

    links: list[str] = []
    for tag in element.find_all("a", href=True):
        href = cast(str, tag["href"])
        if absolute and base_url:
            links.append(urljoin(base_url, href))
        else:
            links.append(href)

    return links


__all__ = ["extract_links"]
