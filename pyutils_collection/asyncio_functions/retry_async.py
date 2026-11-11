"""Async function retry utilities."""

import asyncio
import math
from collections.abc import Awaitable, Callable
from typing import TypeVar

# Define a type variable for the return type of the function
T = TypeVar("T")


async def retry_async(
    func: Callable[..., Awaitable[T]],
    retries: int,
    delay: float,
) -> T:
    """
    Retry an asynchronous function a specified number of times if it fails.

    Parameters
    ----------
    func : Callable[..., Awaitable[T]]
        The asynchronous function to retry.
    retries : int
        The maximum number of attempts, including the initial call (at least 1).
    delay : float
        The delay in seconds between retry attempts.

    Returns
    -------
    T
        The result of the function if successful.

    Raises
    ------
    TypeError
        If retries is not an integer or delay is not a number, or either is a boolean.
    ValueError
        If retries is not positive or delay is negative or non-finite.
    Exception
        If the function fails after all retries.

    Examples
    --------
    >>> async def unstable_func() -> int:
    >>>     if random.random() < 0.5:
    >>>         raise ValueError("Failed!")
    >>>     return 42
    >>> asyncio.run(retry_async(unstable_func, retries=3, delay=1))
    42
    """
    if not isinstance(retries, int) or isinstance(retries, bool):
        raise TypeError("retries must be an integer")
    if retries <= 0:
        raise ValueError("retries must be positive")
    if not isinstance(delay, (int, float)) or isinstance(delay, bool):
        raise TypeError("delay must be a number")
    if delay < 0 or not math.isfinite(delay):
        raise ValueError("delay must be finite and non-negative")

    for _ in range(retries - 1):
        try:
            return await func()
        except Exception:
            await asyncio.sleep(delay)
    return await func()


__all__ = ["retry_async"]
