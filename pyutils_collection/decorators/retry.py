"""Function retry decorator."""

import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from pyutils_collection.logger_functions.logger import validate_logger

P = ParamSpec("P")
R = TypeVar("R")


def retry(
    max_retries: int, delay: int | float = 1.0, logger: logging.Logger | None = None
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    A decorator to retry a function call a specified number of times with a delay between attempts.

    Parameters
    ----------
    max_retries : int
        The maximum number of attempts (including the first call).
        For example, ``max_retries=3`` allows up to three total attempts
        before the last exception is re-raised.
    delay : int | float, optional
        The delay between retry attempts in seconds (default is 1.0).
    logger : logging.Logger | None, optional
        The logger to use for logging errors (default is None).

    Returns
    -------
    Callable[[Callable[P, R]], Callable[P, R]]
        The decorator function.

    Raises
    ------
    TypeError
        If max_retries is not an integer or delay is not a float.
    """
    validate_logger(logger)
    if not isinstance(max_retries, int) or max_retries < 0:
        if logger:
            logger.error("max_retries must be an positive integer or 0", exc_info=True)
        raise TypeError("max_retries must be an positive integer or 0")
    if not isinstance(delay, (int, float)) or delay < 0:
        if logger:
            logger.error(
                "delay must be a positive float or an positive integer or 0",
                exc_info=True,
            )
        raise TypeError("delay must be a positive float or an positive integer or 0")

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
            The wrapped function with retry logic.
        """

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            """
            The wrapper function that retries the function call.

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

            Raises
            ------
            Exception
                If the maximum number of retries is exceeded.
            """
            attempts: int = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if logger:
                        logger.error(
                            f"Attempt {attempts} failed for {func.__name__}: {e}",
                            exc_info=True,
                        )
                    if attempts >= max_retries:
                        raise
                    time.sleep(delay)

        return wrapper

    return decorator


__all__ = ["retry"]
