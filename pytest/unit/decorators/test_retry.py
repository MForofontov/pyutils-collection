import logging

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.decorators]
from pyutils_collection.decorators.retry import retry

# Configure test_logger
test_logger = logging.getLogger("test_logger")
test_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
test_logger.addHandler(handler)


# Sample function to be decorated
@retry(3)
def sample_function_success() -> str:
    return "Function executed"


@retry(3)
def sample_function_failure() -> None:
    raise Exception("Function failed")


def test_retry_success() -> None:

    """
    Test case 1: Function executes successfully
    """
    assert sample_function_success() == "Function executed"


def test_retry_with_args() -> None:

    """
    Test case 2: Function with positional arguments
    """

    @retry(3)
    def function_with_args(a: int, b: int) -> int:
        return a + b

    assert function_with_args(1, 2) == 3


def test_retry_with_kwargs() -> None:

    """
    Test case 3: Function with keyword arguments
    """

    @retry(3)
    def function_with_kwargs(a: int, b: int = 0) -> int:
        return a + b

    assert function_with_kwargs(1, b=2) == 3


def test_retry_with_var_args() -> None:

    """
    Test case 4: Function with variable length arguments (*args and **kwargs)
    """

    @retry(3)
    def function_with_var_args(a: int, *args: str, **kwargs: float) -> str:
        return f"{a} - {args} - {kwargs}"

    assert (
        function_with_var_args(1, "arg1", "arg2", kwarg1=1.0, kwarg2=2.0)
        == "1 - ('arg1', 'arg2') - {'kwarg1': 1.0, 'kwarg2': 2.0}"
    )


def test_retry_with_0_max_retries() -> None:

    """
    Test case 5: Function with 0 max_retries
    """

    @retry(0)
    def function_with_0_max_retries() -> str:
        return "Function executed"

    assert function_with_0_max_retries() == "Function executed"


def test_retry_with_0_delay() -> None:

    """
    Test case 6: Function with 0 delay
    """

    @retry(3, delay=0)
    def function_with_0_delay() -> str:
        return "Function executed"

    assert function_with_0_delay() == "Function executed"


def test_retry_failure() -> None:

    """
    Test case 7: Function fails after retries
    """
    with pytest.raises(Exception, match="Function failed"):
        sample_function_failure()


def test_retry_with_logger(caplog) -> None:

    """
    Test case 8: Logger functionality when function fails
    """

    @retry(3, logger=test_logger)
    def logged_function() -> str:
        raise Exception("Function failed")

    with caplog.at_level(logging.WARNING):
        with pytest.raises(Exception, match="Function failed"):
            logged_function()
        assert "Attempt 1 failed for logged_function: Function failed" in caplog.text
        assert "Attempt 2 failed for logged_function: Function failed" in caplog.text
        assert "Attempt 3 failed for logged_function: Function failed" in caplog.text


def test_retry_with_negative_retries() -> None:

    """
    Test case 9: Function with negative max_retries
    """
    with pytest.raises(Exception, match="max_retries must be an positive integer or 0"):

        @retry(-1)
        def function_with_negative_retries() -> None:
            raise Exception("Function failed")

        function_with_negative_retries()


def test_retry_with_negative_delay() -> None:

    """
    Test case 10: Function with negative delay
    """
    with pytest.raises(
        Exception, match="delay must be a positive float or an positive integer or 0"
    ):

        @retry(3, delay=-1)
        def function_with_negative_delay() -> None:
            raise Exception("Function failed")

        function_with_negative_delay()


def test_retry_with_invalid_logger_type() -> None:

    """
    Test case 11: Invalid logger type
    """
    with pytest.raises(
        TypeError, match="logger must be an instance of logging.Logger or None"
    ):

        @retry(3, logger="test_logger")
        def invalid_logger() -> None:
            pass


def test_retry_with_invalid_max_retries_type() -> None:

    """
    Test case 12: Invalid max_retries type
    """
    with pytest.raises(TypeError, match="max_retries must be an positive integer or 0"):

        @retry("3")
        def invalid_max_retries() -> None:
            pass


def test_retry_with_invalid_max_retries_type_with_logger(caplog) -> None:

    """
    Test case 13: Invalid max_retries type with logger
    """
    with caplog.at_level(logging.ERROR):
        with pytest.raises(
            TypeError, match="max_retries must be an positive integer or 0"
        ):

            @retry("3", logger=test_logger)
            def invalid_max_retries_with_logger() -> None:
                pass

    assert "max_retries must be an positive integer or 0" in caplog.text


def test_retry_with_invalid_delay_type() -> None:

    """
    Test case 14: Invalid delay type
    """
    with pytest.raises(
        TypeError, match="delay must be a positive float or an positive integer or 0"
    ):

        @retry(3, delay="3")
        def invalid_delay() -> None:
            pass


def test_retry_with_invalid_delay_type_with_logger(caplog) -> None:

    """
    Test case 15: Invalid delay type with logger
    """
    with caplog.at_level(logging.ERROR):
        with pytest.raises(
            TypeError,
            match="delay must be a positive float or an positive integer or 0",
        ):

            @retry(3, delay="3", logger=test_logger)
            def invalid_delay_with_logger() -> None:
                pass

    assert "delay must be a positive float or an positive integer or 0" in caplog.text
