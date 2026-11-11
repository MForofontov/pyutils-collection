"""
Advanced query parameter manipulation.
"""

from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse


def merge_query_params(
    base_url: str,
    params: dict[str, Any],
    replace: bool = False,
    list_separator: str | None = None,
) -> str:
    """
    Merge query parameters into URL with advanced handling.

    Adds or updates query parameters in URL with support for nested parameters,
    arrays, and merging strategies. Uses urllib.parse but adds workflow logic
    for complex parameter manipulation.

    Parameters
    ----------
    base_url : str
        Base URL to add parameters to.
    params : dict[str, Any]
        Parameters to add/merge. Values can be strings, lists, or nested dicts.
    replace : bool, optional
        Replace existing params instead of merging (by default False).
    list_separator : str | None, optional
        Separator for list values (by default None uses multiple keys).

    Returns
    -------
    str
        URL with merged query parameters.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If base_url is empty.

    Examples
    --------
    >>> merge_query_params("http://example.com?a=1", {"b": "2"})
    'http://example.com?a=1&b=2'
    >>> merge_query_params("http://example.com?a=1", {"a": "2"}, replace=True)
    'http://example.com?a=2'
    >>> merge_query_params("http://example.com", {"tags": ["python", "web"]})
    'http://example.com?tags=python&tags=web'
    >>> merge_query_params("http://example.com", {"tags": ["python", "web"]}, list_separator=",")
    'http://example.com?tags=python%2Cweb'

    Notes
    -----
    Uses urllib.parse but adds:
    - List/array parameter handling
    - Replace vs merge strategies
    - List separator options
    - Type coercion for parameter values
    - Preservation of existing parameters

    Common use cases:
    - API client query building
    - Pagination URL generation
    - Filter/search URL construction
    - Analytics tracking parameters

    Complexity
    ----------
    Time: O(n + m) where n is existing params, m is new params, Space: O(n + m)
    """
    # Input validation
    if not isinstance(base_url, str):
        raise TypeError(f"base_url must be a string, got {type(base_url).__name__}")
    if not isinstance(params, dict):
        raise TypeError(f"params must be a dict, got {type(params).__name__}")
    if not isinstance(replace, bool):
        raise TypeError(f"replace must be a bool, got {type(replace).__name__}")
    if list_separator is not None and not isinstance(list_separator, str):
        raise TypeError(
            f"list_separator must be str or None, got {type(list_separator).__name__}"
        )

    if not base_url:
        raise ValueError("base_url cannot be empty")

    # Parse URL
    parsed = urlparse(base_url)

    # Get existing query parameters
    existing_params: dict[str, list[str]] = {}
    if parsed.query and not replace:
        existing_params = parse_qs(parsed.query, keep_blank_values=True)

    # Prepare new parameters
    final_params: list[tuple[str, str]] = []

    # Add existing parameters if not replacing
    if not replace:
        for key, values in existing_params.items():
            if key in params:
                continue
            for value in values:
                final_params.append((key, value))

    # Add/merge new parameters
    remaining_keys = set(params)
    for key, value in params.items():
        remaining_keys.remove(key)
        # Handle different value types
        if isinstance(value, list):
            if not value:
                continue
            if list_separator is not None:
                # Join list with separator
                final_params.append((key, list_separator.join(str(v) for v in value)))
            else:
                # Add multiple key-value pairs
                for item in value:
                    final_params.append((key, str(item)))
        elif isinstance(value, dict):
            # Flatten nested dict (simple one-level flattening)
            for nested_key, nested_value in value.items():
                full_key = f"{key}[{nested_key}]"
                # A later explicit key overrides this generated nested key.
                if full_key not in remaining_keys:
                    final_params.append((full_key, str(nested_value)))
        elif value is None:
            # Skip None values
            continue
        else:
            # Convert to string
            final_params.append((key, str(value)))

    # Build query string
    query_string = urlencode(final_params)

    # Reconstruct URL
    result = urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            query_string,
            parsed.fragment,
        )
    )

    return result


__all__ = ["merge_query_params"]
