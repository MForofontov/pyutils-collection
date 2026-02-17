import logging

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.decorators]
from pyutils_collection.decorators.deprecated import deprecated

# Configure test_logger
test_logger = logging.getLogger("test_logger")
test_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levellevel)s - %(message)s")
handler.setFormatter(formatter)
test_logger.addHandler(handler)


def test_deprecated_with_logger(caplog) -> None:

    """
    Test case 1: Deprecated function with logger.
    """

    @deprecated(logger=test_logger)
    def old_function():
        return "This is an old function."

    with caplog.at_level(logging.WARNING):
        result = old_function()
    assert result == "This is an old function."
    assert "Call to deprecated function old_function." in caplog.text


def test_deprecated_without_logger(capsys) -> None:

    """
    Test case 2: Deprecated function without logger.
    """

    @deprecated()
    def old_function_no_logger():
        return "This is an old function."

    with pytest.warns(DeprecationWarning) as record:
        result = old_function_no_logger()
    capsys.readouterr()
    assert result == "This is an old function."
    assert "old_function_no_logger is deprecated." in str(record[0].message)


def test_deprecated_with_args(caplog) -> None:

    """
    Test case 3: Deprecated function with arguments.
    """

    @deprecated(logger=test_logger)
    def old_function_with_args(a, b):
        return a + b

    with caplog.at_level(logging.WARNING):
        result = old_function_with_args(1, 2)
    assert result == 3
    assert "Call to deprecated function old_function_with_args." in caplog.text


def test_deprecated_with_kwargs(caplog) -> None:

    """
    Test case 4: Deprecated function with keyword arguments.
    """

    @deprecated(logger=test_logger)
    def old_function_with_kwargs(a, b=0):
        return a + b

    with caplog.at_level(logging.WARNING):
        result = old_function_with_kwargs(a=1, b=2)
    assert result == 3
    assert "Call to deprecated function old_function_with_kwargs." in caplog.text


def test_deprecated_with_return_value(caplog) -> None:

    """
    Test case 5: Deprecated function with return value.
    """

    @deprecated(logger=test_logger)
    def old_function_with_return():
        return "Return value"

    with caplog.at_level(logging.WARNING):
        result = old_function_with_return()
    assert result == "Return value"
    assert "Call to deprecated function old_function_with_return." in caplog.text


def test_deprecated_with_exception(caplog) -> None:

    """
    Test case 6: Deprecated function that raises an exception.
    """

    @deprecated(logger=test_logger)
    def old_function_with_exception():
        raise ValueError("An error occurred")

    with caplog.at_level(logging.WARNING):
        with pytest.raises(ValueError, match="An error occurred"):
            old_function_with_exception()
    assert "Call to deprecated function old_function_with_exception." in caplog.text


def test_invalid_logger_type() -> None:

    """
    Test case 7: Invalid logger type.
    """
    with pytest.raises(
        TypeError, match="logger must be an instance of logging.Logger or None"
    ):

        @deprecated(logger="invalid_logger")
        def invalid_logger_type():
            return "Invalid logger type"
