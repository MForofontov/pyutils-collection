"""Parallel processing with error collection."""

from collections.abc import Callable
from multiprocessing import Pool, cpu_count
from typing import TypeVar

# Define type variables for input and output types
T = TypeVar("T")
R = TypeVar("R")


def _wrapper(args: tuple[Callable[[T], R], T]) -> tuple[R | None, Exception | None]:
    func, item = args
    try:
        return func(item), None
    except Exception as e:
        return None, e


def parallel_gather_errors(
    func: Callable[[T], R], data: list[T], num_processes: int | None = None
) -> tuple[list[R | None], list[Exception]]:
    """
    Apply a function to a list of items in parallel and gather any exceptions raised by the processes.

    Parameters
    ----------
    func : Callable[[T], R]
        The function to apply to each item in the list.
    data : list[T]
        The list of data items to process.
    num_processes : int | None, optional
        The number of processes to use for parallel execution. If None, it defaults
        to the number of available CPUs (by default None).

    Returns
    -------
    tuple[list[R], list[Exception]]
        A tuple containing the list of results and the list of exceptions. If an exception occurs
        for an item, its corresponding result is not included in the result list.

    Examples
    --------
    >>> def risky_func(x: int) -> int:
    >>>     if x == 2:
    >>>         raise ValueError("Bad value!")
    >>>     return x * x
    >>> parallel_gather_errors(risky_func, [1, 2, 3])
    ([1, 9], [ValueError('Bad value!')])
    """
    # Initialize lists to store results and errors
    results = []
    errors = []

    # If num_processes is not specified, default to the number of available CPUs minus one
    if num_processes is None:
        num_processes = max(
            cpu_count() - 1,
            1,
        )  # Pool will default to the number of available CPUs (minus 1)

    # Create a pool of worker processes
    with Pool(processes=num_processes) as pool:
        processed = pool.map(_wrapper, [(func, item) for item in data])
        for result, error in processed:
            if error is None:
                results.append(result)
            else:
                errors.append(error)
    return results, errors


__all__ = ["parallel_gather_errors"]
