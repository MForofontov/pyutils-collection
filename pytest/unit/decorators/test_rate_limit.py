import logging

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.decorators]
from pyutils_collection.decorators.rate_limit import RateLimitExceededException, rate_limit

# Configure test_logger
test_logger = logging.getLogger("test_logger")
test_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
test_logger.addHandler(handler)


# Sample function to be decorated
@rate_limit(max_calls=2, period=5)
def sample_function() -> str:
    return "Function executed"


def test_rate_limit_single_call() -> None:

    """
    Test case 1: Single call within the rate limit period
    """

    @rate_limit(max_calls=1, period=5)
    def single_call_function() -> str:
        return "Function executed"

    assert single_call_function() == "Function executed"


def test_rate_limit_basic() -> None:

    """
    Test case 2: Basic functionality of rate limiting
    """
    assert sample_function() == "Function executed"
    assert sample_function() == "Function executed"
    with pytest.raises(RateLimitExceededException):
        sample_function()


def test_rate_limit_custom_message() -> None:

    """
    Test case 3: Custom exception message when rate limit is exceeded
    """

    @rate_limit(max_calls=1, period=5, exception_message="Custom rate limit message")
    def custom_message_function() -> str:
        return "Function executed"

    assert custom_message_function() == "Function executed"
    with pytest.raises(RateLimitExceededException, match="Custom rate limit message"):
        custom_message_function()


def test_rate_limit_with_logger(caplog) -> None:

    """
    Test case 4: Logger functionality when rate limit is exceeded
    """
    logger = logging.getLogger("rate_limit_logger")
    logger.setLevel(logging.WARNING)

    @rate_limit(max_calls=1, period=5, logger=logger)
    def logged_function() -> str:
        return "Function executed"

    with caplog.at_level(logging.WARNING):
        assert logged_function() == "Function executed"
        with pytest.raises(RateLimitExceededException):
            logged_function()
        assert (
            "Rate limit exceeded for logged_function. Try again later." in caplog.text
        )


def test_rate_limit_with_args() -> None:

    """
    Test case 5: Function with positional arguments
    """

    @rate_limit(max_calls=2, period=5)
    def function_with_args(a: int, b: int) -> int:
        return a + b

    assert function_with_args(1, 2) == 3
    assert function_with_args(3, 4) == 7
    with pytest.raises(RateLimitExceededException):
        function_with_args(5, 6)


def test_rate_limit_with_kwargs() -> None:

    """
    Test case 6: Function with keyword arguments
    """

    @rate_limit(max_calls=2, period=5)
    def function_with_kwargs(a: int, b: int = 0) -> int:
        return a + b

    assert function_with_kwargs(1, b=2) == 3
    assert function_with_kwargs(3, b=4) == 7
    with pytest.raises(RateLimitExceededException):
        function_with_kwargs(5, b=6)


def test_rate_limit_with_variable_length_args() -> None:

    """
    Test case 7: Function with variable length arguments (*args and **kwargs)
    """

    @rate_limit(max_calls=2, period=5)
    def function_with_var_args(a: int, *args: str, **kwargs: float) -> str:
        return f"{a} - {args} - {kwargs}"

    assert (
        function_with_var_args(1, "arg1", "arg2", kwarg1=1.0, kwarg2=2.0)
        == "1 - ('arg1', 'arg2') - {'kwarg1': 1.0, 'kwarg2': 2.0}"
    )
    assert (
        function_with_var_args(1, "arg3", kwarg3=3.0)
        == "1 - ('arg3',) - {'kwarg3': 3.0}"
    )
    with pytest.raises(RateLimitExceededException):
        function_with_var_args(1, "arg4", kwarg4=4.0)


def test_rate_limit_exceeding_calls() -> None:

    """
    Test case 8: Exceeding function call within the rate limit period
    """

    @rate_limit(max_calls=1, period=5)
    def exceeding_function_call() -> str:
        return "Function executed"

    assert exceeding_function_call() == "Function executed"
    with pytest.raises(RateLimitExceededException):
        exceeding_function_call()


def test_rate_limit_with_multiple_calls() -> None:

    """
    Test case 9: Function with multiple calls within the rate limit period
    """

    @rate_limit(max_calls=3, period=5)
    def multiple_call_function() -> str:
        return "Function executed"

    assert multiple_call_function() == "Function executed"
    assert multiple_call_function() == "Function executed"
    assert multiple_call_function() == "Function executed"
    with pytest.raises(RateLimitExceededException):
        multiple_call_function()


def test_rate_limit_reset_after_period() -> None:

    """
    Test case 10: Ensure rate limit resets after the specified period
    """
    import time

    @rate_limit(max_calls=2, period=2)
    def reset_function() -> str:
        return "Function executed"

    assert reset_function() == "Function executed"
    assert reset_function() == "Function executed"
    with pytest.raises(RateLimitExceededException):
        reset_function()

    time.sleep(2)  # Wait for the period to reset

    assert reset_function() == "Function executed"
    assert reset_function() == "Function executed"
    with pytest.raises(RateLimitExceededException):
        reset_function()


def test_invalid_max_calls() -> None:

    """
    Test case 11: Invalid max_calls parameter
    """
    with pytest.raises(ValueError, match="max_calls must be a positive integer"):

        @rate_limit(max_calls=-1, period=5)
        def invalid_max_calls_function() -> None:
            pass


def test_invalid_period() -> None:

    """
    Test case 12: Invalid period parameter
    """
    with pytest.raises(ValueError, match="period must be a positive integer"):

        @rate_limit(max_calls=1, period=-5)
        def invalid_period_function() -> None:
            pass


def test_invalid_logger_type() -> None:

    """
    Test case 13: Invalid logger type
    """
    with pytest.raises(
        TypeError, match="logger must be an instance of logging.Logger or None"
    ):

        @rate_limit(max_calls=1, period=5, logger="not_a_logger")
        def invalid_logger_function() -> None:
            pass


def test_invalid_max_calls_with_logger(caplog) -> None:

    """
    Test case 14: Invalid max_calls parameter with logger
    """
    with pytest.raises(ValueError, match="max_calls must be a positive integer"):
        with caplog.at_level(logging.ERROR):

            @rate_limit(max_calls=-1, period=5, logger=test_logger)
            def invalid_max_calls_function() -> None:
                pass

            assert "max_calls must be a positive integer" in caplog.text


def test_invalid_period_with_logger(caplog) -> None:

    """
    Test case 15: Invalid period parameter with logger
    """
    with pytest.raises(ValueError, match="period must be a positive integer"):
        with caplog.at_level(logging.ERROR):

            @rate_limit(max_calls=1, period=-5, logger=test_logger)
            def invalid_period_function() -> None:
                pass

            assert "period must be a positive integer" in caplog.text


def test_invalid_exception_message_type() -> None:

    """
    Test case 16: Invalid exception_message parameter type
    """
    with pytest.raises(TypeError, match="exception_message must be a string or None"):

        @rate_limit(max_calls=1, period=60, exception_message=123)
        def invalid_message_function() -> None:
            pass


def test_invalid_exception_message_type_with_logger(caplog) -> None:

    """
    Test case 17: Invalid exception_message parameter type with logger
    """
    with pytest.raises(TypeError, match="exception_message must be a string or None"):
        with caplog.at_level(logging.ERROR):

            @rate_limit(
                max_calls=1,
                period=60,
                exception_message=["invalid"],
                logger=test_logger,
            )
            def invalid_message_with_logger_function() -> None:
                pass

            assert "exception_message must be a string or None" in caplog.text
