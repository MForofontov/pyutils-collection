"""Time-based cache expiration decorator."""

import threading
import time
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar, cast

P = ParamSpec("P")
R = TypeVar("R")


def cache_with_expiration(
    expiration_time: int,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    A decorator to cache the results of a function call for a specified amount of time.

    Parameters
    ----------
    expiration_time : int
        Nonnegative cache lifetime in elapsed seconds. Zero disables reuse.

    Returns
    -------
    Callable[[Callable[P, R]], Callable[P, R]]
        The decorator function.

    Raises
    ------
    ValueError
        If `expiration_time` is not a nonnegative integer.

    Notes
    -----
    Expiration uses a monotonic clock, so system clock adjustments do not change
    cache lifetimes. Lifetime starts before the wrapped call. Keyword insertion
    order is part of the key. Wrapped exceptions propagate unchanged and are
    never cached.
    """
    if not isinstance(expiration_time, int) or expiration_time < 0:
        raise ValueError("expiration_time must be a positive integer")

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        """
        The actual decorator function.

        Parameters
        ----------
        func : Callable[P, R]
            The function to be decorated.

        Returns
        -------
        Callable[P, R]]
            The wrapped function.
        """
        cached_results: dict[
            tuple[tuple[Any, ...], tuple[tuple[str, Any], ...]], tuple[float, Any]
        ] = {}
        cache_lock = threading.RLock()

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            """
            The wrapper function that caches the result of the decorated function.

            Parameters
            ----------
            *args : Any
                Positional arguments for the decorated function.
            **kwargs : Any
                Keyword arguments for the decorated function.

            Returns
            -------
            Any
                The result of the decorated function, either from the cache or freshly computed.

            Raises
            ------
            TypeError
                If the arguments are unhashable
            """
            key = (args, tuple(kwargs.items()))
            with cache_lock:
                current_time = time.monotonic()
                try:
                    cached = cached_results.get(key)
                except TypeError as exc:
                    raise TypeError(f"Unhashable arguments: {exc}") from exc
                if cached is not None:
                    cached_time, cached_value = cached
                    if current_time - cached_time < expiration_time:
                        return cached_value  # type: ignore[no-any-return]
                    del cached_results[key]
                result = func(*args, **kwargs)
                cached_results[key] = (current_time, result)

            return result

        def cache_clear() -> None:
            """Clear the cache."""
            with cache_lock:
                cached_results.clear()

        wrapper.cache_clear = cache_clear  # type: ignore[attr-defined]

        return cast(Callable[P, R], wrapper)

    return decorator


__all__ = ["cache_with_expiration"]
