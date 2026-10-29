"""Safe JSON deserialization with error handling."""

import json
from typing import Any


def safe_json_load(
    json_string: str,
    object_hook: Any | None = None,
    default: Any | None = None,
    decoder: type[json.JSONDecoder] | None = None,
) -> Any:
    """
    Safely load a JSON string, returning a default value on error.

    Parameters
    ----------
    json_string : str
        The JSON string to parse.
    object_hook : callable, optional
        Function for custom object decoding.
    default : Any, optional
        Value to return if parsing fails (default: None).
    decoder : type, optional
        Custom JSONDecoder class.

    Returns
    -------
    Any
        The parsed object, or default if parsing fails.

    Examples
    --------
    >>> safe_json_load('{"a": 1}')
    {'a': 1}
    >>> safe_json_load('invalid', default={'error': True})
    {'error': True}
    """
    try:
        kwargs = {}
        if object_hook is not None:
            kwargs["object_hook"] = object_hook
        if decoder is not None:
            kwargs["cls"] = decoder
        return json.loads(json_string, **kwargs)
    except json.JSONDecodeError, TypeError, ValueError:
        return default


__all__ = ["safe_json_load"]
