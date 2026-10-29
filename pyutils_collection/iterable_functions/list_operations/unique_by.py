"""Order-preserving deduplication by a computed key."""

from collections.abc import Callable, Hashable, Iterable
from typing import TypeVar

T = TypeVar("T")


def unique_by(items: Iterable[T], key: Callable[[T], Hashable]) -> list[T]:
    """
    Keep the first item for each distinct key, preserving input order.

    Parameters
    ----------
    items : Iterable[T]
        Items to deduplicate, including one-shot iterators.
    key : callable
        Function returning a hashable key for each item.

    Returns
    -------
    list[T]
        First occurrences, retaining the original item objects.

    Raises
    ------
    TypeError
        If items is not iterable, key is not callable, or a key is unhashable.

    Examples
    --------
    >>> unique_by(['A', 'a', 'B'], str.lower)
    ['A', 'B']

    Complexity
    ----------
    Time: O(n) expected, Space: O(k), for k distinct keys.
    """
    if not callable(key):
        raise TypeError("key must be callable")
    seen: set[Hashable] = set()
    result: list[T] = []
    for item in items:
        item_key = key(item)
        if item_key not in seen:
            seen.add(item_key)
            result.append(item)
    return result


__all__ = ["unique_by"]
