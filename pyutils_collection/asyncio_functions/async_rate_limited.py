"""Rate-limited async function execution."""

import asyncio
import math
import time
from collections import deque
from collections.abc import Awaitable, Callable, Iterable
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")


async def async_rate_limited(
    func: Callable[[T], Awaitable[R]],
    items: Iterable[T],
    max_calls: int,
    period: float = 1.0,
) -> list[R]:
    """Process items with a rate limit using an asynchronous function.

    Parameters
    ----------
    func : Callable[[T], Awaitable[R]]
        The asynchronous function to apply to each item.
    items : Iterable[T]
        The iterable of items to process.
    max_calls : int
        Maximum number of calls allowed within the given period.
    period : float, optional
        Time window in seconds for the rate limit (default is 1.0).

    Returns
    -------
    list[R]
        A list of results from processing the items.

    Raises
    ------
    ValueError
        If ``max_calls`` is not a positive integer or ``period`` is not a positive number.

    Notes
    -----
    Timestamp trimming uses a :class:`~collections.deque` for O(1) removal of
    expired entries.

    Examples
    --------
    >>> async def double(x: int) -> int:
    ...     await asyncio.sleep(0.1)
    ...     return x * 2
    >>> asyncio.run(async_rate_limited(double, [1, 2, 3], max_calls=2, period=1))
    [2, 4, 6]
    """
    if not isinstance(max_calls, int) or isinstance(max_calls, bool) or max_calls <= 0:
        raise ValueError("max_calls must be a positive integer")
    if (
        not isinstance(period, (int, float))
        or isinstance(period, bool)
        or not math.isfinite(period)
        or period <= 0
    ):
        raise ValueError("period must be a positive number")

    results: list[R] = []
    timestamps: deque[float] = deque()

    for item in items:
        now = time.monotonic()
        while timestamps and now - timestamps[0] >= period:
            timestamps.popleft()
        # A timer may wake early; keep waiting until capacity actually expires.
        while len(timestamps) >= max_calls:
            await asyncio.sleep(period - (now - timestamps[0]))
            now = time.monotonic()
            while timestamps and now - timestamps[0] >= period:
                timestamps.popleft()
        timestamps.append(now)
        results.append(await func(item))

    return results


__all__ = ["async_rate_limited"]
