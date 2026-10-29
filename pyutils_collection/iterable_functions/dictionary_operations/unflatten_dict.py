"""Reconstruct nested dictionaries from separated key paths."""

from typing import Any


def unflatten_dict(d: dict[str, Any], separator: str = "_") -> dict[str, Any]:
    """
    Rebuild nested dictionaries from flat string keys.

    Parameters
    ----------
    d : dict[str, Any]
        Flat mapping whose keys encode paths. Leaf values are retained by reference.
    separator : str, optional
        Nonempty path separator, matching flatten_dict (default '_').

    Returns
    -------
    dict[str, Any]
        A new nested dictionary.

    Raises
    ------
    TypeError
        If d is not a dictionary or keys or separator are not strings.
    ValueError
        If separator is empty or a leaf conflicts with another key's parent path.

    Examples
    --------
    >>> unflatten_dict({'user_name': 'Ada', 'user_age': 36})
    {'user': {'name': 'Ada', 'age': 36}}

    Notes
    -----
    Separators inside original keys and empty dictionaries discarded by
    flatten_dict cannot be recovered. Empty path components are allowed.

    Complexity
    ----------
    Time and space: O(p), for total path length p, excluding leaf values.
    """
    if not isinstance(d, dict):
        raise TypeError("d must be a dictionary")
    if not isinstance(separator, str):
        raise TypeError("separator must be a string")
    if not separator:
        raise ValueError("separator must not be empty")
    if not all(isinstance(key, str) for key in d):
        raise TypeError("all keys must be strings")

    result: dict[str, Any] = {}
    # Track constructed branches separately from dictionary-valued leaves.
    branches: set[int] = set()
    for key, value in d.items():
        parts = key.split(separator)
        current = result
        for part in parts[:-1]:
            if part in current and id(current[part]) not in branches:
                raise ValueError(f"Conflicting key path: {key}")
            if part not in current:
                current[part] = {}
                branches.add(id(current[part]))
            current = current[part]
        if parts[-1] in current:
            raise ValueError(f"Conflicting key path: {key}")
        current[parts[-1]] = value
    return result


__all__ = ["unflatten_dict"]
