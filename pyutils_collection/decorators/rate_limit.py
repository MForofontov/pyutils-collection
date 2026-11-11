"""Rate limiting decorator."""

import logging
import threading
import time
from collections import deque
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from pyutils_collection.logger_functions.logger import validate_logger

P = ParamSpec("P")
R = TypeVar("R")


class RateLimitExceededException(Exception):
    """Exception raised when the rate limit is exceeded."""


def rate_limit(
    max_calls: int,
    period: int,
    logger: logging.Logger | None = None,
    exception_message: str | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    A decorator to limit the number of times a function can be called within a specific period.

    Parameters
    ----------
    max_calls : int
        The maximum number of allowed calls within the period.
    period : int
        The time period in seconds.
    logger : logging.Logger | None
        The logger to use for logging rate limit warnings.
    exception_message : str | None
        Custom exception message when the rate limit is exceeded.

    Returns
    -------
    Callable[[Callable[P, R]], Callable[P, R]]
        The decorator function.

    Raises
    ------
    ValueError
        If either max_calls or period is not a positive integer.
    TypeError
        If logger is not an instance of logging.Logger or None.
    """
    validate_logger(logger)
    if not isinstance(max_calls, int) or max_calls <= 0:
        if logger:
            logger.error("max_calls must be a positive integer", exc_info=True)
        raise ValueError("max_calls must be a positive integer")
    if not isinstance(period, int) or period <= 0:
        if logger:
            logger.error("period must be a positive integer", exc_info=True)
        raise ValueError("period must be a positive integer")
    if not isinstance(exception_message, str) and exception_message is not None:
        if logger:
            logger.error("exception_message must be a string or None", exc_info=True)
        raise TypeError("exception_message must be a string or None")

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
            The wrapped function
        """
        # Store timestamps of function calls using a deque with fixed length
        calls: deque[float] = deque(maxlen=max_calls)
        calls_lock = threading.Lock()

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

            Raises
            ------
            RateLimitExceededException
                If the rate limit is exceeded.
            """
            nonlocal calls  # Indicates that 'calls' refers to the deque in the enclosing scope
            with calls_lock:
                current_time = time.time()
                # Remove calls that are outside the allowed period
                while calls and current_time - calls[0] >= period:
                    calls.popleft()

                # Check if the number of calls exceeds the limit
                if len(calls) >= max_calls:
                    message = (
                        exception_message
                        or f"Rate limit exceeded for {func.__name__}. Try again later."
                    )
                    if logger:
                        logger.warning(message, exc_info=True)
                    raise RateLimitExceededException(message)

                # Append the current timestamp to the list of calls
                calls.append(current_time)
            return func(*args, **kwargs)

        return wrapper

    return decorator


__all__ = ["RateLimitExceededException", "rate_limit"]
