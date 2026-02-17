import logging
import time

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.decorators]
from pyutils_collection.decorators.throttle import throttle

# Configure test_logger
test_logger = logging.getLogger("test_logger")
test_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
test_logger.addHandler(handler)


# Sample function to be decorated
@throttle(rate_limit=1.0)
def sample_function() -> str:
    return "Function executed"


def test_throttle_success() -> None:

    """
    Test case 1: Function executes successfully with sufficient interval
    """
    assert sample_function() == "Function executed"
    time.sleep(1.1)
    assert sample_function() == "Function executed"


def test_throttle_with_args() -> None:

    """
    Test case 2: Function with positional arguments
    """

    @throttle(rate_limit=1.0)
    def function_with_args(a: int, b: int) -> int:
        return a + b

    assert function_with_args(1, 2) == 3
    time.sleep(1.1)
    assert function_with_args(1, 2) == 3


def test_throttle_with_kwargs() -> None:

    """
    Test case 3: Function with keyword arguments
    """

    @throttle(rate_limit=1.0)
    def function_with_kwargs(a: int, b: int = 0) -> int:
        return a + b

    assert function_with_kwargs(1, b=2) == 3
    time.sleep(1.1)
    assert function_with_kwargs(1, b=2) == 3


def test_throttle_with_var_args() -> None:

    """
    Test case 4: Function with variable length arguments (*args and **kwargs)
    """

    @throttle(rate_limit=1.0)
    def function_with_var_args(a: int, *args: str, **kwargs: float) -> str:
        return f"{a} - {args} - {kwargs}"

    assert (
        function_with_var_args(1, "arg1", "arg2", kwarg1=1.0, kwarg2=2.0)
        == "1 - ('arg1', 'arg2') - {'kwarg1': 1.0, 'kwarg2': 2.0}"
    )
    time.sleep(1.1)
    assert (
        function_with_var_args(1, "arg1", "arg2", kwarg1=1.0, kwarg2=2.0)
        == "1 - ('arg1', 'arg2') - {'kwarg1': 1.0, 'kwarg2': 2.0}"
    )


def test_throttle_failure() -> None:

    """
    Test case 5: Function fails when called too frequently
    """
    assert sample_function() == "Function executed"
    with pytest.raises(
        RuntimeError,
        match="Function sample_function called too frequently. Rate limit: 1.0 seconds.",
    ):
        sample_function()


def test_throttle_with_logger(caplog) -> None:

    """
    Test case 6: Logger functionality when function is called too frequently
    """

    @throttle(rate_limit=1.0, logger=test_logger)
    def logged_function() -> str:
        return "Function executed"

    assert logged_function() == "Function executed"
    with caplog.at_level(logging.ERROR):
        with pytest.raises(
            RuntimeError,
            match="Function logged_function called too frequently. Rate limit: 1.0 seconds.",
        ):
            logged_function()
        assert (
            "Function logged_function called too frequently. Rate limit: 1.0 seconds."
            in caplog.text
        )


def test_invalid_logger_type() -> None:

    """
    Test case 7: Invalid logger type
    """
    with pytest.raises(
        TypeError, match="logger must be an instance of logging.Logger or None"
    ):

        @throttle(rate_limit=1.0, logger="not_a_logger")
        def invalid_logger_function() -> None:
            pass


def test_invalid_rate_limit_type() -> None:

    """
    Test case 8: Invalid rate_limit type
    """
    with pytest.raises(
        TypeError, match="rate_limit must be a positive float or an integer"
    ):

        @throttle(rate_limit="one")
        def invalid_rate_limit_function() -> None:
            pass


def test_invalid_rate_limit_type_with_logger(caplog) -> None:

    """
    Test case 9: Invalid rate_limit type with logger
    """
    with caplog.at_level(logging.ERROR):
        with pytest.raises(
            TypeError, match="rate_limit must be a positive float or an integer"
        ):

            @throttle(rate_limit="one", logger=test_logger)
            def invalid_rate_limit_function_with_logger() -> None:
                pass

        assert (
            "Type error in throttle decorator: rate_limit must be a positive float or an integer."
            in caplog.text
        )


def test_invalid_rate_limit_value() -> None:

    """
    Test case 10: Invalid rate_limit value
    """
    with pytest.raises(
        TypeError, match="rate_limit must be a positive float or an integer"
    ):

        @throttle(rate_limit=-1)
        def invalid_rate_limit_value_function() -> None:
            pass


def test_invalid_rate_limit_value_with_logger(caplog) -> None:

    """
    Test case 11: Invalid rate_limit value with logger
    """
    with caplog.at_level(logging.ERROR):
        with pytest.raises(
            TypeError, match="rate_limit must be a positive float or an integer"
        ):

            @throttle(rate_limit=-1, logger=test_logger)
            def invalid_rate_limit_value_function_with_logger() -> None:
                pass

        assert (
            "Type error in throttle decorator: rate_limit must be a positive float or an integer."
            in caplog.text
        )
