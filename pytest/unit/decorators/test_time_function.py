import logging
import time
from functools import wraps
from typing import Any, Callable

import pytest

try:
    import psutil
    from pyutils_collection.decorators.time_function import time_function
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None  # type: ignore
    
    # Create dummy decorator for when psutil is not available
    def time_function(*args: Any, **kwargs: Any) -> Callable:  # type: ignore
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*f_args: Any, **f_kwargs: Any) -> Any:
                return func(*f_args, **f_kwargs)
            return wrapper
        if len(args) == 1 and callable(args[0]):
            return decorator(args[0])
        return decorator

pytestmark = [
    pytest.mark.unit,
    pytest.mark.decorators,
    pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed"),
]

# Configure test_logger
test_logger = logging.getLogger("test_logger")
test_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
test_logger.addHandler(handler)


# Sample function to be decorated
@time_function()
def sample_function() -> str:
    time.sleep(1)
    return "Function executed"


def test_time_function_success(capfd) -> None:

    """
    Test case 1: Function executes successfully and prints execution time
    """
    result = sample_function()
    assert result == "Function executed"

    captured = capfd.readouterr()
    assert "sample_function executed in" in captured.out


def test_time_function_with_logger(caplog) -> None:

    """
    Test case 2: Function executes successfully and logs execution time
    """

    @time_function(logger=test_logger)
    def function_with_logger() -> str:
        time.sleep(1)
        return "Function executed"

    with caplog.at_level(logging.DEBUG):
        result = function_with_logger()
        assert result == "Function executed"
        assert "function_with_logger executed in" in caplog.text


def test_time_function_with_args(capfd) -> None:

    """
    Test case 3: Function with positional arguments
    """

    @time_function()
    def function_with_args(a: int, b: int) -> int:
        time.sleep(1)
        return a + b

    result = function_with_args(1, 2)
    assert result == 3

    captured = capfd.readouterr()
    assert "function_with_args executed in" in captured.out


def test_time_function_with_kwargs(capfd) -> None:

    """
    Test case 4: Function with keyword arguments
    """

    @time_function()
    def function_with_kwargs(a: int, b: int = 0) -> int:
        time.sleep(1)
        return a + b

    result = function_with_kwargs(1, b=2)
    assert result == 3

    captured = capfd.readouterr()
    assert "function_with_kwargs executed in" in captured.out


def test_time_function_with_var_args(capfd) -> None:

    """
    Test case 5: Function with variable length arguments (*args and **kwargs)
    """

    @time_function()
    def function_with_var_args(a: int, *args: str, **kwargs: float) -> str:
        time.sleep(1)
        return f"{a} - {args} - {kwargs}"

    result = function_with_var_args(1, "arg1", "arg2", kwarg1=1.0, kwarg2=2.0)
    assert result == "1 - ('arg1', 'arg2') - {'kwarg1': 1.0, 'kwarg2': 2.0}"

    captured = capfd.readouterr()
    assert "function_with_var_args executed in" in captured.out


def test_time_function_exception(capfd) -> None:

    """
    Test case 6: Function raises an exception
    """

    @time_function()
    def function_with_exception() -> None:
        time.sleep(1)
        raise ValueError("Sample error")

    with pytest.raises(ValueError, match="Sample error"):
        function_with_exception()

    captured = capfd.readouterr()
    assert "function_with_exception executed in" in captured.out
