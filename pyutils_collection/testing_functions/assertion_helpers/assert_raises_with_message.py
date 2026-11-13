"""
Assert function raises exception with specific message pattern.
"""

from collections.abc import Callable
from typing import Any


def assert_raises_with_message(
    func: Callable[..., Any],
    exception_type: type[Exception],
    message_pattern: str,
    *args: Any,
    **kwargs: Any,
) -> None:
    """
    Assert that a function raises an exception with a specific message pattern.

    Parameters
    ----------
    func : Callable[..., Any]
        Function to call.
    exception_type : Type[Exception]
        Expected exception type.
    message_pattern : str
        Expected substring in exception message.
    *args : Any
        Positional arguments for func.
    **kwargs : Any
        Keyword arguments for func.

    Returns
    -------
    None

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    AssertionError
        If function doesn't raise expected exception or message doesn't match.

    Notes
    -----
    Only exceptions raised by ``func`` satisfy the expectation, including when
    expecting ``AssertionError`` or the base ``Exception`` class.

    Examples
    --------
    >>> def failing_func():
    ...     raise ValueError("Invalid input")
    >>> assert_raises_with_message(failing_func, ValueError, "Invalid")

    Complexity
    ----------
    Time: O(1), Space: O(1)
    """
    if not callable(func):
        raise TypeError(f"func must be callable, got {type(func).__name__}")
    if not isinstance(exception_type, type) or not issubclass(
        exception_type, Exception
    ):
        raise TypeError("exception_type must be an Exception type")
    if not isinstance(message_pattern, str):
        raise TypeError(
            f"message_pattern must be a string, got {type(message_pattern).__name__}"
        )

    try:
        func(*args, **kwargs)
    except exception_type as e:
        if message_pattern not in str(e):
            raise AssertionError(
                f"Exception message '{str(e)}' does not contain expected pattern '{message_pattern}'"
            ) from None
    except Exception as e:
        raise AssertionError(
            f"Expected {exception_type.__name__}, but got {type(e).__name__}: {str(e)}"
        ) from None
    else:
        raise AssertionError(
            f"Expected {exception_type.__name__} to be raised, but no exception was raised"
        )
