import logging
from functools import wraps
from typing import Any, Callable

import pytest

try:
    import aiohttp
    from pyutils_collection.decorators.async_handle_error import async_handle_error
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    aiohttp = None  # type: ignore
    
    # Create dummy decorator for when aiohttp is not available
    def async_handle_error(*args: Any, **kwargs: Any) -> Callable:  # type: ignore
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*f_args: Any, **f_kwargs: Any) -> Any:
                return await func(*f_args, **f_kwargs)
            return wrapper
        if len(args) == 1 and callable(args[0]):
            return decorator(args[0])
        return decorator

pytestmark = [
    pytest.mark.unit,
    pytest.mark.decorators,
    pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed"),
]

# Configure test_logger
test_logger = logging.getLogger("test_logger")
test_logger.setLevel(logging.ERROR)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
test_logger.addHandler(handler)


# Define sample functions for use in tests
@async_handle_error()
async def sample_function_success(x: int, y: int) -> int:
    return x + y


@async_handle_error()
async def sample_function_exception(x: int, y: int) -> int:
    raise ValueError("Test exception")


@async_handle_error(logger=test_logger)
async def sample_function_with_logger(x: int, y: int) -> int:
    raise ValueError("Test exception")


@async_handle_error()
async def sample_function_with_args(x: int, y: int, z: int) -> int:
    return x + y + z


@async_handle_error()
async def sample_function_with_kwargs(x: int, y: int, z: int = 0) -> int:
    return x + y + z


@async_handle_error()
async def sample_function_with_mixed_args_kwargs(
    x: int, y: int, *args: int, z: int = 0, **kwargs: int
) -> int:
    return x + y + z + sum(args) + sum(kwargs.values())


@async_handle_error()
async def sample_function_no_args() -> str:
    return "success"


@pytest.mark.asyncio
async def test_sync_function_success():
    """
    Test case 1: Synchronous function that succeeds.
    """
    result = await sample_function_success(1, 2)
    assert result == 3


@pytest.mark.asyncio
async def test_sync_function_with_args():
    """
    Test case 2: Synchronous function with positional arguments.
    """
    result = await sample_function_with_args(1, 2, 3)
    assert result == 6


@pytest.mark.asyncio
async def test_sync_function_with_kwargs():
    """
    Test case 3: Synchronous function with keyword arguments.
    """
    result = await sample_function_with_kwargs(1, 2, z=3)
    assert result == 6


@pytest.mark.asyncio
async def test_sync_function_with_mixed_args_kwargs():
    """
    Test case 4: Synchronous function with mixed positional and keyword arguments.
    """
    result = await sample_function_with_mixed_args_kwargs(1, 2, 3, 4, z=5, a=6, b=7)
    assert result == 28


@pytest.mark.asyncio
async def test_sync_function_with_no_args():
    """
    Test case 5: Synchronous function with no arguments.
    """
    result = await sample_function_no_args()
    assert result == "success"


def test_non_async_function_with_logger(caplog) -> None:

    """
    Test case 6: Synchronous function that logs an error with logging enabled.
    """
    with caplog.at_level(logging.ERROR):

        @async_handle_error(logger=test_logger)
        def sample_function(x: int, y: int) -> int:
            return x + y

        assert (
            "An error occurred in sample_function: The function to be wrapped must be asynchronous"
            in caplog.text
        )


@pytest.mark.asyncio
async def test_async_function_with_logger(caplog):
    """
    Test case 7: Asynchronous function that logs an exception with logging enabled.
    """
    with caplog.at_level(logging.ERROR):
        result = await sample_function_with_logger(1, 2)
        assert result is None
        assert (
            "An error occurred in sample_function_with_logger: Test exception"
            in caplog.text
        )


def test_non_async_function() -> None:

    """
    Test case 8: Synchronous function that raises an error.
    """
    with pytest.raises(
        TypeError, match="The function to be wrapped must be asynchronous"
    ):

        @async_handle_error()
        def sample_function(x: int, y: int) -> int:
            return x + y


@pytest.mark.asyncio
async def test_async_function_exception(caplog, capsys):
    """
    Test case 9: Asynchronous function that raises an exception. The error
    should be logged via the default logger and no output should be printed.
    """
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError, match="Test exception"):
            await sample_function_exception(1, 2)
    assert (
        "An error occurred in sample_function_exception: Test exception" in caplog.text
    )
    captured = capsys.readouterr()
    assert captured.out == ""


@pytest.mark.asyncio
async def test_sync_function_with_invalid_logger():
    """
    Test case 10: Synchronous function that logs an exception with an invalid logger.
    """
    with pytest.raises(
        TypeError, match="logger must be an instance of logging.Logger or None"
    ):

        @async_handle_error(logger="invalid_logger")
        async def sample_function(x: int, y: int) -> int:
            return x + y
