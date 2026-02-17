import logging

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.decorators]
from pyutils_collection.decorators.enforce_types import enforce_types

# Configure test_logger
test_logger = logging.getLogger("test_logger")
test_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
test_logger.addHandler(handler)


# Example function to be decorated
@enforce_types(logger=test_logger)
def sample_function(a: int, b: str) -> str:
    return f"{a} - {b}"


def test_valid_types() -> None:

    """
    Test case 1: Valid types for arguments and return value
    """
    result = sample_function(1, "test")
    assert result == "1 - test"


def test_valid_types_with_logger(caplog) -> None:

    """
    Test case 2: Valid types for arguments and return value, with logger
    """

    @enforce_types(logger=test_logger)
    def sample_function_valid_with_logger(a: int, b: str) -> str:
        return f"{a} - {b}"

    with caplog.at_level(logging.INFO):
        result = sample_function_valid_with_logger(1, "test")
    assert result == "1 - test"
    assert "Argument 'a' must be of type int" not in caplog.text
    assert "Return value must be of type int" not in caplog.text


def test_valid_types_with_kwargs() -> None:

    """
    Test case 3: Valid types for arguments with kwargs
    """

    @enforce_types()
    def sample_function_valid_kwargs(a: int, b: str) -> str:
        return f"{a} - {b}"

    result = sample_function_valid_kwargs(a=1, b="test")
    assert result == "1 - test"


def test_valid_types_with_kwargs_and_logger(caplog) -> None:

    """
    Test case 4: Valid types for arguments with kwargs, with logger
    """

    @enforce_types(logger=test_logger)
    def sample_function_valid_kwargs_with_logger(a: int, b: str) -> str:
        return f"{a} - {b}"

    with caplog.at_level(logging.INFO):
        result = sample_function_valid_kwargs_with_logger(a=1, b="test")
    assert result == "1 - test"
    assert "Argument 'a' must be of type int" not in caplog.text
    assert "Return value must be of type int" not in caplog.text


def test_missing_type_annotations() -> None:

    """
    Test case 5: Function without type annotations
    """

    @enforce_types()
    def sample_function_no_annotations(a, b):
        return f"{a} - {b}"

    result = sample_function_no_annotations(1, "test")
    assert result == "1 - test"


def test_default_argument_values() -> None:

    """
    Test case 6: Function with default argument values
    """

    @enforce_types()
    def sample_function_default_args(a: int, b: str = "default") -> str:
        return f"{a} - {b}"

    result = sample_function_default_args(1)
    assert result == "1 - default"


def test_variable_length_arguments() -> None:

    """
    Test case 7: Function with variable length arguments (*args and **kwargs)
    """

    @enforce_types()
    def sample_function_var_args(a: int, *args: str, **kwargs: dict[str, float]) -> str:
        return f"{a} - {args} - {kwargs}"

    result = sample_function_var_args(1, "arg1", "arg2", kwarg1=1.0, kwarg2=2.0)
    assert result == "1 - ('arg1', 'arg2') - {'kwarg1': 1.0, 'kwarg2': 2.0}"


def test_invalid_argument_type() -> None:

    """
    Test case 8: Invalid type for argument, no logger provided
    """

    @enforce_types()
    def sample_function_invalid_arg(a: int, b: str) -> str:
        return f"{a} - {b}"

    with pytest.raises(
        TypeError, match="Expected <class 'int'> for argument 'a', got <class 'str'>."
    ):
        sample_function_invalid_arg("invalid", "test")


def test_invalid_return_type() -> None:

    """
    Test case 9: Invalid type for return value, no logger provided
    """

    @enforce_types()
    def sample_function_invalid_return(a: int, b: str) -> int:
        return f"{a} - {b}"

    with pytest.raises(
        TypeError, match="Expected return type <class 'int'>, got <class 'str'>."
    ):
        sample_function_invalid_return(1, "test")


def test_invalid_argument_type_with_logger(caplog) -> None:

    """
    Test case 10: Invalid type for argument, with logger
    """

    @enforce_types(logger=test_logger)
    def sample_function_invalid_arg_with_logger(a: int, b: str) -> str:
        return f"{a} - {b}"

    with pytest.raises(
        TypeError, match="Expected <class 'int'> for argument 'a', got <class 'str'>."
    ):
        with caplog.at_level(logging.ERROR):
            sample_function_invalid_arg_with_logger("invalid", "test")
        assert "Argument 'a' must be of type int" in caplog.text


def test_invalid_return_type_with_logger(caplog) -> None:

    """
    Test case 11: Invalid type for return value, with logger
    """

    @enforce_types(logger=test_logger)
    def sample_function_invalid_return_with_logger(a: int, b: str) -> int:
        return f"{a} - {b}"

    with pytest.raises(
        TypeError, match="Expected return type <class 'int'>, got <class 'str'>."
    ):
        with caplog.at_level(logging.ERROR):
            sample_function_invalid_return_with_logger(1, "test")
        assert "Return value must be of type int" in caplog.text


def test_invalid_argument_type_with_kwargs() -> None:

    """
    Test case 12: Invalid type for argument with kwargs, no logger provided
    """

    @enforce_types()
    def sample_function_invalid_arg_kwargs(a: int, b: str) -> str:
        return f"{a} - {b}"

    with pytest.raises(
        TypeError, match="Expected <class 'int'> for argument 'a', got <class 'str'>."
    ):
        sample_function_invalid_arg_kwargs(a="invalid", b="test")


def test_invalid_argument_type_with_kwargs_and_logger(caplog) -> None:

    """
    Test case 13: Invalid type for argument with kwargs, with logger
    """

    @enforce_types(logger=test_logger)
    def sample_function_invalid_arg_kwargs_with_logger(a: int, b: str) -> str:
        return f"{a} - {b}"

    with pytest.raises(
        TypeError, match="Expected <class 'int'> for argument 'a', got <class 'str'>."
    ):
        with caplog.at_level(logging.ERROR):
            sample_function_invalid_arg_kwargs_with_logger(a="invalid", b="test")
        assert "Argument 'a' must be of type int" in caplog.text


def test_mixed_valid_and_invalid_arguments() -> None:

    """
    Test case 14: Mixed valid and invalid arguments
    """

    @enforce_types()
    def sample_function_mixed_args(a: int, b: str, c: float) -> str:
        return f"{a} - {b} - {c}"

    with pytest.raises(
        TypeError, match="Expected <class 'float'> for argument 'c', got <class 'str'>."
    ):
        sample_function_mixed_args(1, "test", "invalid")


def test_invalid_logger_type() -> None:

    """
    Test case 15: Invalid logger type
    """
    with pytest.raises(
        TypeError, match="logger must be an instance of logging.Logger or None"
    ):

        @enforce_types(logger="invalid_logger")
        def sample_function_invalid_logger(a: int, b: str) -> str:
            return f"{a} - {b}"
