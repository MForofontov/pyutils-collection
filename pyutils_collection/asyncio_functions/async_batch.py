"""Batch processing utilities for asynchronous operations."""

from collections.abc import Awaitable, Callable
from typing import TypeVar

# Define type variables for input and output types
T = TypeVar("T")
R = TypeVar("R")


async def async_batch(
    func: Callable[[list[T]], Awaitable[list[R]]],
    items: list[T],
    batch_size: int,
) -> list[R]:
    """
    Process items in batches using an asynchronous function.

    Parameters
    ----------
    func : Callable[[list[T]], list[R]]
        The asynchronous function to apply to each batch of items.
    items : list[T]
        The list of items to process.
    batch_size : int
        The size of each batch.

    Returns
    -------
    list[R]
        A list of results from processing all the batches.

    Raises
    ------
    TypeError
        If batch_size is not an integer or is a boolean.
    ValueError
        If batch_size is not positive.
    Exception
        Propagates any exception raised by ``func`` during batch processing.

    Examples
    --------
    >>> async def process_batch(batch: list[int]) -> list[int]:
    >>>     await asyncio.sleep(1)
    >>>     return [x * 2 for x in batch]
    >>> asyncio.run(async_batch(process_batch, [1, 2, 3, 4, 5], batch_size=2))
    [2, 4, 6, 8, 10]
    """
    if not isinstance(batch_size, int) or isinstance(batch_size, bool):
        raise TypeError("batch_size must be an integer")
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")

    # Initialize an empty list to store the results
    results = []

    # Iterate over the items in batches of the specified batch_size
    for i in range(0, len(items), batch_size):
        # Get the current batch of items
        batch = items[i : i + batch_size]

        # Apply ``func`` to the batch and await the result
        result = await func(batch)

        # Extend the results list with the result of the current batch
        results.extend(result)

    # Return the list of results from processing all the batches
    return results


__all__ = ["async_batch"]
