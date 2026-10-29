"""
URL normalization for canonical URLs.
"""

from urllib.parse import parse_qs, urlencode, urlparse, urlunparse


def normalize_url(
    url: str,
    remove_default_port: bool = True,
    remove_fragment: bool = False,
    sort_query_params: bool = True,
    remove_trailing_slash: bool = False,
    lowercase_scheme_host: bool = True,
) -> str:
    """
    Normalize URL to canonical form.

    Standardizes URL format for comparison, deduplication, and caching.
    Uses urllib.parse as foundation but adds workflow logic for normalization
    rules and edge cases.

    Parameters
    ----------
    url : str
        URL to normalize.
    remove_default_port : bool, optional
        Remove default ports (80 for http, 443 for https) (by default True).
    remove_fragment : bool, optional
        Remove URL fragment (#section) (by default False).
    sort_query_params : bool, optional
        Sort query parameters alphabetically (by default True).
    remove_trailing_slash : bool, optional
        Remove trailing slash from path (by default False).
    lowercase_scheme_host : bool, optional
        Convert scheme and host to lowercase (by default True).

    Returns
    -------
    str
        Normalized URL.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If URL is empty or invalid.

    Examples
    --------
    >>> normalize_url("HTTP://EXAMPLE.COM:80/path")
    'http://example.com/path'
    >>> normalize_url("https://example.com/page?b=2&a=1")
    'https://example.com/page?a=1&b=2'
    >>> normalize_url("http://example.com/page/#section", remove_fragment=True)
    'http://example.com/page/'

    Notes
    -----
    Uses urllib.parse but adds:
    - Default port removal logic (80/443)
    - Query parameter sorting for canonical form
    - Fragment handling options
    - Scheme/host case normalization
    - Trailing slash normalization

    Useful for:
    - URL deduplication in crawlers
    - Cache key generation
    - URL comparison
    - Canonical link tags

    Complexity
    ----------
    Time: O(n + m log m) where n is URL length, m is query params, Space: O(n)
    """
    # Input validation
    if not isinstance(url, str):
        raise TypeError(f"url must be a string, got {type(url).__name__}")
    if not isinstance(remove_default_port, bool):
        raise TypeError(
            f"remove_default_port must be bool, got {type(remove_default_port).__name__}"
        )
    if not isinstance(remove_fragment, bool):
        raise TypeError(
            f"remove_fragment must be bool, got {type(remove_fragment).__name__}"
        )
    if not isinstance(sort_query_params, bool):
        raise TypeError(
            f"sort_query_params must be bool, got {type(sort_query_params).__name__}"
        )
    if not isinstance(remove_trailing_slash, bool):
        raise TypeError(
            f"remove_trailing_slash must be bool, got {type(remove_trailing_slash).__name__}"
        )
    if not isinstance(lowercase_scheme_host, bool):
        raise TypeError(
            f"lowercase_scheme_host must be bool, got {type(lowercase_scheme_host).__name__}"
        )

    if not url:
        raise ValueError("url cannot be empty")

    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValueError(f"Invalid URL: {e}") from e

    # Normalize scheme and host
    scheme = parsed.scheme.lower() if lowercase_scheme_host else parsed.scheme

    # Handle port
    port = parsed.port
    if port is not None and remove_default_port:
        # Remove default ports
        if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
            port = None

    if lowercase_scheme_host:
        # Use hostname and rebuild netloc (this lowercases the host)
        netloc = parsed.hostname or ""
        netloc = netloc.lower()
        if ":" in netloc:
            netloc = f"[{netloc}]"

        # Add port if present and not removed
        if port is not None:
            netloc = f"{netloc}:{port}"

        # Add username/password if present
        if "@" in parsed.netloc:
            user_info = parsed.netloc.rsplit("@", 1)[0]
            netloc = f"{user_info}@{netloc}"
    else:
        # Use original netloc to preserve case
        # But need to handle port removal if requested
        if port is None and remove_default_port:
            # Port was removed, need to strip it from netloc
            original_port = parsed.port
            if original_port is not None:
                # Remove :port from netloc
                netloc = parsed.netloc.rsplit(":", 1)[0]
            else:
                netloc = parsed.netloc
        else:
            netloc = parsed.netloc

    # Normalize path
    path = parsed.path
    if not path:
        path = "/"
    if remove_trailing_slash and path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    # Normalize query parameters
    query = ""
    if parsed.query:
        if sort_query_params:
            # Parse and sort query parameters
            params = parse_qs(parsed.query, keep_blank_values=True)
            # Sort keys and rebuild query string
            sorted_params = []
            for key in sorted(params.keys()):
                for value in params[key]:
                    sorted_params.append((key, value))
            query = urlencode(sorted_params)
        else:
            query = parsed.query

    # Handle fragment
    fragment = "" if remove_fragment else parsed.fragment

    # Reconstruct URL
    normalized = urlunparse((scheme, netloc, path, parsed.params, query, fragment))
    return normalized


__all__ = ["normalize_url"]
