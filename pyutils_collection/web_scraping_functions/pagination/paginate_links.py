"""
Generate pagination links.
"""

from urllib.parse import urlencode, urlsplit, urlunsplit


def paginate_links(
    base_url: str,
    start_page: int = 1,
    end_page: int = 10,
    page_param: str = "page",
) -> list[str]:
    """
    Generate list of pagination URLs.

    Parameters
    ----------
    base_url : str
        Base URL template.
    start_page : int, optional
        Starting page number (by default 1).
    end_page : int, optional
        Ending page number (by default 10).
    page_param : str, optional
        Query parameter name for page (by default "page").

    Returns
    -------
    list[str]
        List of pagination URLs.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If base_url is empty, start_page > end_page, or page numbers are non-positive.

    Examples
    --------
    >>> urls = paginate_links("https://example.com/items", 1, 3)
    >>> urls
    ['https://example.com/items?page=1', 'https://example.com/items?page=2', 'https://example.com/items?page=3']

    >>> urls = paginate_links("https://example.com/items?sort=asc", 1, 2, "p")
    >>> urls[0]
    'https://example.com/items?sort=asc&p=1'

    Notes
    -----
    Automatically handles existing query parameters.
    Preserves fragments and URL-encodes the page parameter name.

    Complexity
    ----------
    Time: O(n), Space: O(n), where n is number of pages
    """
    if not isinstance(base_url, str):
        raise TypeError(f"base_url must be a string, got {type(base_url).__name__}")
    if not isinstance(start_page, int):
        raise TypeError(
            f"start_page must be an integer, got {type(start_page).__name__}"
        )
    if not isinstance(end_page, int):
        raise TypeError(f"end_page must be an integer, got {type(end_page).__name__}")
    if not isinstance(page_param, str):
        raise TypeError(f"page_param must be a string, got {type(page_param).__name__}")

    if not base_url.strip():
        raise ValueError("base_url cannot be empty")

    if start_page <= 0:
        raise ValueError(f"start_page must be positive, got {start_page}")

    if end_page <= 0:
        raise ValueError(f"end_page must be positive, got {end_page}")

    if start_page > end_page:
        raise ValueError(f"start_page ({start_page}) must be <= end_page ({end_page})")

    urls = []
    parsed = urlsplit(base_url)

    for page in range(start_page, end_page + 1):
        page_query = urlencode({page_param: page})
        query = f"{parsed.query}&{page_query}" if parsed.query else page_query
        url = urlunsplit(parsed._replace(query=query))
        urls.append(url)

    return urls


__all__ = ["paginate_links"]
