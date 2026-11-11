"""Recursive dictionary merging."""

import copy
from typing import Any


def merge_dicts_recursive(*dicts: dict[str, Any]) -> dict[str, Any]:
    """
    Recursively merge multiple dictionaries.

    Parameters
    ----------
    *dicts : dict
        Variable number of dictionaries to merge.

    Returns
    -------
    dict
        A new dictionary containing the merged result.

    Raises
    ------
    TypeError
        If any argument is not a dictionary.

    Examples
    --------
    >>> dict1 = {'a': 1, 'b': {'c': 2}}
    >>> dict2 = {'b': {'d': 3}, 'e': 4}
    >>> merge_dicts_recursive(dict1, dict2)
    {'a': 1, 'b': {'c': 2, 'd': 3}, 'e': 4}
    """
    if not all(isinstance(d, dict) for d in dicts):
        raise TypeError("All arguments must be dictionaries")

    result: dict[Any, Any] = {}

    for d in dicts:
        for key, value in d.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = merge_dicts_recursive(result[key], value)
            else:
                result[key] = copy.deepcopy(value)

    return result


__all__ = ["merge_dicts_recursive"]
