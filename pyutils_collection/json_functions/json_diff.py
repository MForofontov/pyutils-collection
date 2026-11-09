"""JSON difference comparison utilities."""

from itertools import chain
from typing import Any


def json_diff(a: Any, b: Any, path: str = "") -> list[tuple[str, Any, Any]]:
    """
    Compute the difference between two JSON-serializable objects.

    Parameters
    ----------
    a : Any
        First object to compare.
    b : Any
        Second object to compare.
    path : str, optional
        Current path in the object hierarchy (default: "").

    Returns
    -------
    list of tuple
        List of (path, a_value, b_value) for changed/added/removed fields.
        Dictionary keys follow a's insertion order, then keys added by b.

    Examples
    --------
    >>> json_diff({'a': 1}, {'a': 2, 'b': 3})
    [('a', 1, 2), ('b', None, 3)]
    >>> json_diff([1, 2], [1, 3])
    [('[1]', 2, 3)]
    """
    diffs = []
    if type(a) is not type(b):
        diffs.append((path, a, b))
        return diffs
    if isinstance(a, dict):
        for k in chain(a, (key for key in b if key not in a)):
            new_path = f"{path}.{k}" if path else k
            if k in a and k in b:
                diffs.extend(json_diff(a[k], b[k], new_path))
            elif k in a:
                diffs.append((new_path, a[k], None))
            else:
                diffs.append((new_path, None, b[k]))
    elif isinstance(a, list):
        for i, (ai, bi) in enumerate(zip(a, b, strict=False)):
            new_path = f"{path}[{i}]"
            diffs.extend(json_diff(ai, bi, new_path))
        if len(a) > len(b):
            for i in range(len(b), len(a)):
                diffs.append((f"{path}[{i}]", a[i], None))
        elif len(b) > len(a):
            for i in range(len(a), len(b)):
                diffs.append((f"{path}[{i}]", None, b[i]))
    else:
        if a != b:
            diffs.append((path, a, b))
    return diffs
