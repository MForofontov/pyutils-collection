import logging

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.decorators]
from pyutils_collection.decorators.log_signature import log_signature

# Configure test_logger
test_logger = logging.getLogger("test_logger")
test_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
test_logger.addHandler(handler)


@log_signature(logger=test_logger)
def add(a, b):
    return a + b


@log_signature(logger=test_logger)
def greet(name):
    return f"Hello, {name}!"


@log_signature(logger=test_logger)
def raise_value_error():
    raise ValueError("This is a ValueError")


@log_signature(logger=test_logger)
def return_value(value):
    return value


def test_log_signature_add(caplog) -> None:

    """
    Test case 1: Logging function signature for add function.
    """
    with caplog.at_level(logging.DEBUG):
        result = add(1, 2)
        assert result == 3
        assert "Executing add(a, b) with args: (1, 2) and kwargs: {}" in caplog.text


def test_log_signature_greet(caplog) -> None:

    """
    Test case 2: Logging function signature for greet function.
    """
    with caplog.at_level(logging.DEBUG):
        result = greet("Alice")
        assert result == "Hello, Alice!"
        assert (
            "Executing greet(name) with args: ('Alice',) and kwargs: {}" in caplog.text
        )


def test_log_signature_return_value(caplog) -> None:

    """
    Test case 3: Logging function signature for return_value function.
    """
    with caplog.at_level(logging.DEBUG):
        result = return_value(5)
        assert result == 5
        assert (
            "Executing return_value(value) with args: (5,) and kwargs: {}"
            in caplog.text
        )


def test_log_signature_with_kwargs(caplog) -> None:

    """
    Test case 4: Logging function signature with keyword arguments.
    """

    @log_signature(logger=test_logger)
    def with_kwargs(a, b=0):
        return a + b

    with caplog.at_level(logging.DEBUG):
        result = with_kwargs(1, b=2)
        assert result == 3
        assert (
            "Executing with_kwargs(a, b=0) with args: (1,) and kwargs: {'b': 2}"
            in caplog.text
        )


def test_log_signature_with_multiple_args(caplog) -> None:

    """
    Test case 5: Logging function signature with multiple arguments.
    """

    @log_signature(logger=test_logger)
    def multiple_args(a, b, c):
        return a + b + c

    with caplog.at_level(logging.DEBUG):
        result = multiple_args(1, 2, 3)
        assert result == 6
        assert (
            "Executing multiple_args(a, b, c) with args: (1, 2, 3) and kwargs: {}"
            in caplog.text
        )


def test_log_signature_raise_value_error(caplog) -> None:

    """
    Test case 6: Logging function signature for function that raises ValueError.
    """
    with caplog.at_level(logging.DEBUG):
        with pytest.raises(ValueError, match="This is a ValueError"):
            raise_value_error()
        assert (
            "Executing raise_value_error() with args: () and kwargs: {}" in caplog.text
        )


def test_log_signature_with_exception(caplog) -> None:

    """
    Test case 7: Logging function signature for function that raises a custom exception.
    """

    @log_signature(logger=test_logger)
    def raise_custom_exception():
        raise Exception("This is a CustomException")

    with caplog.at_level(logging.DEBUG):
        with pytest.raises(Exception, match="This is a CustomException"):
            raise_custom_exception()
        assert (
            "Executing raise_custom_exception() with args: () and kwargs: {}"
            in caplog.text
        )
        assert "Exception occurred in raise_custom_exception():" in caplog.text


def test_log_signature_invalid_logger() -> None:

    """
    Test case 8: Invalid logger.
    """
    with pytest.raises(
        TypeError, match="logger must be an instance of logging.Logger."
    ):

        @log_signature(logger="not_a_logger")
        def invalid_logger_func():
            pass
