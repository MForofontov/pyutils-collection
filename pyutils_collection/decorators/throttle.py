"""Function throttling decorator."""

import logging
import threading
import time
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from pyutils_collection.logger_functions.logger import validate_logger

P = ParamSpec("P")
R = TypeVar("R")


def throttle(
    rate_limit: int | float, logger: logging.Logger | None = None
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    A decorator to enforce a rate limit on a function, ensuring it is not called more often than the specified rate.

    Parameters
    ----------
    rate_limit : float
        The minimum time interval (in seconds) between consecutive calls to the function.
    logger : logging.Logger | None, optional
        The logger to use for logging errors (default is None).

    Returns
    -------
    Callable[[Callable[P, R]], Callable[P, R]]
        The decorator function.

    Raises
    ------
    TypeError
        If rate_limit is not a float or an integer.
    """
    validate_logger(logger)

    if not isinstance(rate_limit, (int, float)) or rate_limit < 0:
        if logger:
            logger.error(
                "Type error in throttle decorator: rate_limit must be a positive float or an integer.",
                exc_info=True,
            )
        raise TypeError("rate_limit must be a positive float or an integer")

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        """
        The actual decorator function.

        Parameters
        ----------
        func : Callable[P, R]
            The function to be decorated.

        Returns
        -------
        Callable[P, R]
            The wrapped function.
        """
        last_called = 0.0
        throttle_lock = threading.Lock()

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            """
            The wrapper function that enforces the rate limit.

            Parameters
            ----------
            *args : Any
                Positional arguments for the decorated function.
            **kwargs : Any
                Keyword arguments for the decorated function.

            Returns
            -------
            Any
                The result of the decorated function.
            """
            nonlocal last_called
            with throttle_lock:
                current_time = time.time()
                elapsed_time = current_time - last_called
                if elapsed_time < rate_limit:
                    if logger:
                        logger.error(
                            f"Function {func.__name__} called too frequently. Rate limit: {rate_limit} seconds.",
                            exc_info=True,
                        )
                    raise RuntimeError(
                        f"Function {func.__name__} called too frequently. Rate limit: {rate_limit} seconds."
                    )
                last_called = current_time
            return func(*args, **kwargs)

        return wrapper

    return decorator


__all__ = ["throttle"]
