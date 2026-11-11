"""Function timeout decorator."""

import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from pyutils_collection.logger_functions.logger import validate_logger

P = ParamSpec("P")
R = TypeVar("R")


class TimeoutException(Exception):
    pass


def timeout(
    seconds: int, logger: logging.Logger | None = None
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    A decorator that enforces a timeout on a function.
    The wrapped function runs in a separate thread so this implementation works
    on all platforms, including Windows. If the timeout is reached, the
    decorated call returns ``TimeoutException`` while the original thread may
    continue running in the background.

    Parameters
    ----------
    seconds : int
        The maximum number of seconds the function is allowed to run.
    logger : logging.Logger | None
        The logger to use for logging timeout messages. If None, messages are printed to the console.

    Returns
    -------
    Callable[[Callable[P, R]], Callable[P, R]]
        The decorator function.

    Raises
    ------
    TypeError
        If ``seconds`` is not an integer or if ``logger`` is not an instance of
        ``logging.Logger`` or ``None``.
    """
    validate_logger(logger)

    if not isinstance(seconds, int) or seconds < 0:
        if logger:
            logger.error(
                "Type error in timeout decorator: seconds must be a positive integer.",
                exc_info=True,
            )
        raise TypeError("seconds must be a positive integer")

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

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            """
            The wrapper function that enforces the timeout.

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

            def _run_func() -> Any:
                return func(*args, **kwargs)

            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(_run_func)
            try:
                return future.result(timeout=seconds)  # type: ignore[no-any-return]
            except FuturesTimeoutError as exc:
                message = (
                    f"Function {func.__name__} timed out after {seconds} seconds"
                )
                if logger:
                    logger.error(message)
                future.cancel()
                raise TimeoutException(message) from exc
            finally:
                executor.shutdown(wait=False, cancel_futures=True)

        return wrapper

    return decorator


__all__ = ["TimeoutException", "timeout"]
