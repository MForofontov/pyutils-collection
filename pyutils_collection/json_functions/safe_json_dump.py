"""Safe JSON serialization with error handling."""

import json
from typing import Any, TypeVar

T = TypeVar("T")


def safe_json_dump(
    obj: Any,
    default: T | None = None,
    encoder: type[json.JSONEncoder] | None = None,
    **kwargs: Any,
) -> str | T:
    """
    Safely dump an object to a JSON string, returning a default value on error.

    Parameters
    ----------
    obj : Any
        The object to serialize.
    default : Any, optional
        Value to return if serialization fails (default: None).
    encoder : type, optional
        Custom JSONEncoder class.
    **kwargs
        Additional arguments for json.dumps.

    Returns
    -------
    str or T
        The JSON string, or the provided default value (which may be any type) if
        serialization fails.

    Examples
    --------
    >>> safe_json_dump({'a': 1})
    '{"a": 1}'
    >>> safe_json_dump(set([1, 2]), default='error')
    'error'
    """
    try:
        return (
            json.dumps(obj, cls=encoder, **kwargs)
            if encoder
            else json.dumps(obj, **kwargs)
        )
    except TypeError, ValueError:
        return default  # type: ignore[return-value]
