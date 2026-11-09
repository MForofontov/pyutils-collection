"""Remove values from nested dictionaries using key paths."""

from typing import Any


def deep_delete(
    d: dict[str, Any], keys: str | list[str], missing_ok: bool = False
) -> None:
    """
    Delete a nested value in place, keeping empty parent dictionaries.

    Parameters
    ----------
    d : dict[str, Any]
        Dictionary to modify.
    keys : str or list[str]
        Dot-separated path or explicit keys, as in deep_set.
    missing_ok : bool, optional
        Ignore absent paths or non-dictionary parents (default False).

    Raises
    ------
    TypeError
        If d, keys, or missing_ok has the wrong type.
    ValueError
        If the explicit key list is empty.
    KeyError
        If the path does not exist and missing_ok is False.

    Examples
    --------
    >>> data = {'user': {'name': 'Ada'}}
    >>> deep_delete(data, 'user.name')
    >>> data
    {'user': {}}

    Complexity
    ----------
    Time and space: O(k), for k path components.
    """
    if not isinstance(d, dict):
        raise TypeError("d must be a dictionary")
    if not isinstance(missing_ok, bool):
        raise TypeError("missing_ok must be a bool")
    if isinstance(keys, str):
        keys = keys.split(".")
    if not isinstance(keys, list) or not all(isinstance(key, str) for key in keys):
        raise TypeError("keys must be a string or a list of strings")
    if not keys:
        raise ValueError("keys must contain at least one key")

    current = d
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            if missing_ok:
                return
            raise KeyError(tuple(keys))
        current = current[key]
    if keys[-1] not in current:
        if missing_ok:
            return
        raise KeyError(tuple(keys))
    del current[keys[-1]]


__all__ = ["deep_delete"]
