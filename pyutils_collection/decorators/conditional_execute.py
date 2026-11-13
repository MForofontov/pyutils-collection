"""Conditional function execution decorator."""

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

T = TypeVar("T")


def conditional_execute(
    predicate: Callable[[], bool],
) -> Callable[[Callable[P, T]], Callable[P, T | None]]:
    """
    Decorator to conditionally execute a function based on a predicate.

    Parameters
    ----------
    predicate : Callable[[], bool]
        A function that returns a boolean value. The decorated function will only be executed if this predicate returns True.

    Returns
    -------
    Callable[[Callable[P, T]], Callable[P, T | None]]
        A decorator that wraps the input function with conditional execution logic.

    Raises
    ------
    TypeError
        If the predicate is not callable.

    Notes
    -----
    Predicate failures are wrapped in RuntimeError with their cause retained.
    Exceptions from the decorated function propagate unchanged.
    """
    if not callable(predicate):
        raise TypeError("Predicate must be callable")

    def decorator(func: Callable[P, T]) -> Callable[P, T | None]:
        """
        Decorator function.

        Parameters
        ----------
        func : Callable[P, T]
            The function to be conditionally executed.

        Returns
        -------
        Callable[P, T | None]
            The wrapped function with conditional execution logic.
        """

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
            """
            Wrapper function to conditionally execute the input function.

            Parameters
            ----------
            *args : Any
                Positional arguments to pass to the wrapped function.
            **kwargs : Any
                Keyword arguments to pass to the wrapped function.

            Returns
            -------
            T | None
                The result of the wrapped function if the predicate returns True, otherwise None.

            Raises
            ------
            RuntimeError
                If the predicate function raises an error.
            """
            try:
                execute = bool(predicate())
            except Exception as exc:
                raise RuntimeError(
                    f"Predicate function raised an error: {exc}"
                ) from exc
            if execute:
                return func(*args, **kwargs)
            return None

        return wrapper

    return decorator


__all__ = ["conditional_execute"]
