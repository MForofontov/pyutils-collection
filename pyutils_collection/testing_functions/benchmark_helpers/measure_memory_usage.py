"""
Measure memory usage of a function.
"""

import tracemalloc
from collections.abc import Callable
from typing import Any


def measure_memory_usage(
    func: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Measure memory usage of a function.

    Parameters
    ----------
    func : Callable[..., Any]
        Function to measure.
    *args : Any
        Positional arguments for func.
    **kwargs : Any
        Keyword arguments for func.

    Returns
    -------
    dict[str, Any]
        Dictionary containing 'current_bytes', 'peak_bytes', and 'result'.

    Raises
    ------
    TypeError
        If func is not callable.

    Examples
    --------
    >>> def test_func():
    ...     return [i for i in range(1000)]
    >>> result = measure_memory_usage(test_func)
    >>> 'peak_bytes' in result
    True

    Notes
    -----
    If the caller already owns an active tracing session, leave it active and
    report its current and peak totals without resetting that shared session.

    Complexity
    ----------
    Time: O(f), Space: O(f), where f is function complexity
    """
    if not callable(func):
        raise TypeError(f"func must be callable, got {type(func).__name__}")

    owns_tracing = not tracemalloc.is_tracing()
    if owns_tracing:
        tracemalloc.start()

    try:
        result = func(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
    finally:
        if owns_tracing:
            tracemalloc.stop()

    return {
        "current_bytes": current,
        "peak_bytes": peak,
        "result": result,
    }


__all__ = ["measure_memory_usage"]
