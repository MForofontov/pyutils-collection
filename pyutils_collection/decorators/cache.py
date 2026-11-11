"""Function result caching decorator."""

import threading
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar, cast

P = ParamSpec("P")
R = TypeVar("R")
_MISSING = object()


def cache(func: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator to cache the results of a function call.

    Parameters
    ----------
    func : Callable[P, R]
        The function to be cached.

    Returns
    -------
    Callable[P, R]
        A wrapper function that caches the results of the input function.

    Raises
    ------
    TypeError
        If the decorated function is later called with unhashable arguments.

    Notes
    -----
    Keyword insertion order is part of the cache key. Exceptions from the
    wrapped function propagate unchanged and are never cached.

    Examples
    --------
    >>> @cache
    ... def add(a: int, b: int) -> int:
    ...     return a + b
    >>> add(1, 2)
    3
    >>> add(1, 2)  # Cached result
    3
    >>> add.cache_clear()
    """

    cached_results: dict[tuple[tuple[Any, ...], tuple[tuple[str, Any], ...]], Any] = {}
    cache_lock = threading.RLock()

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        """
        Wrapper function to cache the results of the input function.

        Parameters
        ----------
        *args : Any
            Positional arguments to pass to the wrapped function.
        **kwargs : Any
            Keyword arguments to pass to the wrapped function.

        Returns
        -------
        Any
            The cached result of the wrapped function.

        Raises
        ------
        TypeError
            If the arguments are unhashable.
        """
        key = (args, tuple(kwargs.items()))
        with cache_lock:
            # A single lookup validates hashability and checks for cached None.
            try:
                result = cached_results.get(key, _MISSING)
            except TypeError as exc:
                raise TypeError(f"Unhashable arguments: {exc}") from exc
            if result is _MISSING:
                result = func(*args, **kwargs)
                cached_results[key] = result
            return result  # type: ignore[no-any-return]

    def cache_clear() -> None:
        """Public method to clear the cached results for ``func``."""
        with cache_lock:
            cached_results.clear()

    wrapper.cache_clear = cache_clear  # type: ignore[attr-defined]

    return cast(Callable[P, R], wrapper)


__all__ = ["cache"]
