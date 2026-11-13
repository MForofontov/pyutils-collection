"""Dictionary key-value inversion."""

from typing import Any


def invert_dict(d: dict[str, Any], allow_duplicates: bool = False) -> dict[Any, Any]:
    """
    Invert a dictionary, swapping keys and values.

    Parameters
    ----------
    d : dict
        The dictionary to invert.
    allow_duplicates : bool, optional
        If True, allow duplicate values (default False). If False, raises ValueError on duplicates.

    Returns
    -------
    dict
        An inverted dictionary.

    Raises
    ------
    TypeError
        If d is not a dictionary.
    ValueError
        If allow_duplicates is False and duplicate values exist.

    Examples
    --------
    >>> d = {'a': 1, 'b': 2, 'c': 1}
    >>> invert_dict(d, allow_duplicates=True)
    {1: ['a', 'c'], 2: ['b']}
    >>> invert_dict(d, allow_duplicates=False)
    Traceback (most recent call last):
    ValueError: Duplicate values found: [1]

    Notes
    -----
    With duplicates allowed, groups and their keys retain first-seen order.
    Buckets are built in one pass, with expected O(n) time for ordinary hash
    behavior and O(n) output space. The input dictionary is not modified.
    """
    if not isinstance(d, dict):
        raise TypeError(f"d must be a dictionary, got {type(d).__name__}")

    inverted: dict[Any, Any] = {}
    duplicates: list[Any] = []

    if allow_duplicates:
        for key, value in d.items():
            if value in inverted:
                inverted[value].append(key)
            else:
                inverted[value] = [key]
        return inverted

    for key, value in d.items():
        if value in inverted:
            if value not in duplicates:
                duplicates.append(value)
        else:
            inverted[value] = key

    if duplicates:
        raise ValueError(f"Duplicate values found: {duplicates}")

    return inverted


__all__ = ["invert_dict"]
