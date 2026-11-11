"""Map async work with bounded concurrency and ordered results."""

import asyncio
from collections.abc import Awaitable, Callable, Iterable
from itertools import islice
from typing import TypeVar, cast

T = TypeVar("T")
R = TypeVar("R")


async def async_map_limited(
    func: Callable[[T], Awaitable[R]], items: Iterable[T], limit: int = 10
) -> list[R]:
    """
    Apply an async callable with at most limit tasks running concurrently.

    Parameters
    ----------
    func : callable
        Async operation taking a single input item.
    items : Iterable[T]
        Finite input, consumed incrementally rather than scheduled all at once.
    limit : int, optional
        Positive concurrency limit (default 10). Booleans are rejected.

    Returns
    -------
    list[R]
        Results in input order, regardless of completion order.

    Raises
    ------
    TypeError
        If func is not callable, items is not iterable, or limit is not an integer.
    ValueError
        If limit is not positive.
    Exception
        Propagates operation or iterator errors after cancelling and awaiting
        remaining workers. Caller cancellation also cleans up all workers.

    Examples
    --------
    >>> async def double(value):
    ...     return value * 2
    >>> asyncio.run(async_map_limited(double, range(3), limit=2))
    [0, 2, 4]

    Complexity
    ----------
    Time: O(n) scheduling overhead, Space: O(n) results and O(limit) worker tasks.
    """
    if not callable(func):
        raise TypeError("func must be callable")
    if not isinstance(limit, int) or isinstance(limit, bool):
        raise TypeError("limit must be an integer")
    if limit <= 0:
        raise ValueError("limit must be positive")
    indexed = enumerate(items)
    first_items = list(islice(indexed, limit))
    # Reserve the first worker slots before any worker can consume more input.
    # Each later index appends exactly one slot before awaiting its operation.
    results: list[R | None] = [None] * len(first_items)

    async def worker(first: tuple[int, T]) -> None:
        index, item = first
        results[index] = await func(item)
        for index, item in indexed:
            results.append(None)
            results[index] = await func(item)

    tasks = [asyncio.create_task(worker(first)) for first in first_items]
    try:
        await asyncio.gather(*tasks)
    except BaseException:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise
    # Every reserved slot was assigned if all workers completed successfully.
    return cast(list[R], results)


__all__ = ["async_map_limited"]
