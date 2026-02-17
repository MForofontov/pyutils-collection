import logging

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.decorators]
from pyutils_collection.decorators.handle_error import handle_error

# Configure test_logger
test_logger = logging.getLogger("test_logger")
test_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
test_logger.addHandler(handler)


@handle_error("An error occurred")
def raise_value_error():
    raise ValueError("This is a ValueError")


@handle_error("An error occurred")
def raise_type_error():
    raise TypeError("This is a TypeError")


@handle_error("An error occurred")
def return_value(value):
    return value


@handle_error("An error occurred")
def add(a, b):
    return a + b


@handle_error("An error occurred", logger=test_logger)
def raise_value_error_with_logging():
    raise ValueError("This is a ValueError")


@handle_error("An error occurred", logger=test_logger)
def raise_type_error_with_logging():
    raise TypeError("This is a TypeError")


def test_handle_error_no_error() -> None:

    """
    Test case 1: No error occurs.
    """
    assert return_value(5) == 5
    assert return_value("test") == "test"


def test_handle_error_add() -> None:

    """
    Test case 2: Adding two numbers.
    """
    assert add(1, 2) == 3
    assert add(-1, 1) == 0


def test_handle_error_with_kwargs() -> None:

    """
    Test case 3: Function with keyword arguments.
    """

    @handle_error("An error occurred")
    def with_kwargs(a, b=0):
        return a + b

    assert with_kwargs(1, b=2) == 3
    assert with_kwargs(a=1, b=2) == 3


def test_handle_error_with_multiple_args() -> None:

    """
    Test case 4: Function with multiple arguments.
    """

    @handle_error("An error occurred")
    def multiple_args(a, b, c):
        return a + b + c

    assert multiple_args(1, 2, 3) == 6
    assert multiple_args("a", "b", "c") == "abc"


def test_handle_error_value_error(capfd) -> None:

    """
    Test case 5: Handling ValueError.
    """
    result = raise_value_error()
    out, err = capfd.readouterr()
    assert result is None
    assert "An error occurred: This is a ValueError" in out


def test_handle_error_type_error(capfd) -> None:

    """
    Test case 6: Handling TypeError.
    """
    result = raise_type_error()
    out, err = capfd.readouterr()
    assert result is None
    assert "An error occurred: This is a TypeError" in out


def test_handle_error_with_exception_in_kwargs(capfd) -> None:

    """
    Test case 7: Function with keyword arguments that raises an exception.
    """

    @handle_error("An error occurred")
    def with_kwargs_exception(a, b=0):
        if b == 0:
            raise ValueError("b cannot be zero")
        return a + b

    result = with_kwargs_exception(1, b=0)
    out, err = capfd.readouterr()
    assert result is None
    assert "An error occurred: b cannot be zero" in out


def test_handle_error_with_custom_exception(capfd) -> None:

    """
    Test case 8: Function that raises a custom exception.
    """

    class CustomException(Exception):
        pass

    @handle_error("An error occurred")
    def raise_custom_exception():
        raise CustomException("This is a CustomException")

    result = raise_custom_exception()
    out, err = capfd.readouterr()
    assert result is None
    assert "An error occurred: This is a CustomException" in out


def test_handle_error_value_error_with_logging(caplog) -> None:

    """
    Test case 9: Handling ValueError with logging.
    """
    with caplog.at_level(logging.ERROR):
        result = raise_value_error_with_logging()
        assert result is None
        assert "An error occurred: This is a ValueError" in caplog.text


def test_handle_error_type_error_with_logging(caplog) -> None:

    """
    Test case 10: Handling TypeError with logging.
    """
    with caplog.at_level(logging.ERROR):
        result = raise_type_error_with_logging()
        assert result is None
        assert "An error occurred: This is a TypeError" in caplog.text


def test_handle_invalid_logger() -> None:

    """
    Test case 11: Invalid logger.
    """
    with pytest.raises(TypeError):

        @handle_error("An error occurred", logger="test_logger")
        def raise_value_error_invalid_logger():
            raise ValueError("This is a ValueError")
