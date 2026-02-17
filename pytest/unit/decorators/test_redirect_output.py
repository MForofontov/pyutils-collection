import logging

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.decorators]
from pyutils_collection.decorators.redirect_output import redirect_output

# Configure test_logger
test_logger = logging.getLogger("test_logger")
test_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
test_logger.addHandler(handler)


def test_redirect_output_basic(tmpdir) -> None:

    """
    Test case 1: Basic functionality of redirecting output
    """
    output_file = tmpdir.join("output.txt")

    @redirect_output(str(output_file))
    def sample_function() -> None:
        print("Function executed")

    sample_function()
    with open(output_file) as f:
        assert f.read().strip() == "Function executed"


def test_redirect_output_with_args(tmpdir) -> None:

    """
    Test case 2: Function with positional arguments
    """
    output_file = tmpdir.join("output_args.txt")

    @redirect_output(str(output_file))
    def function_with_args(a: int, b: int) -> None:
        print(a + b)

    function_with_args(1, 2)
    with open(output_file) as f:
        assert f.read().strip() == "3"


def test_redirect_output_with_kwargs(tmpdir) -> None:

    """
    Test case 3: Function with keyword arguments
    """
    output_file = tmpdir.join("output_kwargs.txt")

    @redirect_output(str(output_file))
    def function_with_kwargs(a: int, b: int = 0) -> None:
        print(a + b)

    function_with_kwargs(1, b=2)
    with open(output_file) as f:
        assert f.read().strip() == "3"


def test_redirect_output_with_var_args(tmpdir) -> None:

    """
    Test case 4: Function with variable length arguments (*args and **kwargs)
    """
    output_file = tmpdir.join("output_var_args.txt")

    @redirect_output(str(output_file))
    def function_with_var_args(a: int, *args: str, **kwargs: float) -> None:
        print(f"{a} - {args} - {kwargs}")

    function_with_var_args(1, "arg1", "arg2", kwarg1=1.0, kwarg2=2.0)
    with open(output_file) as f:
        assert (
            f.read().strip() == "1 - ('arg1', 'arg2') - {'kwarg1': 1.0, 'kwarg2': 2.0}"
        )


def test_redirect_output_run_time_error_no_logger(tmpdir) -> None:

    """
    Test case 5: Redirecting output when an error occurs
    """
    output_file = tmpdir.join("invalid_path/output.txt")

    @redirect_output(str(output_file))
    def error_function() -> None:
        raise RuntimeError("An error occurred")

    with pytest.raises(RuntimeError):
        error_function()


def test_redirect_output_run_time_error_with_logger(tmpdir, caplog) -> None:

    """
    Test case 6: Logger functionality when an error occurs
    """
    output_file = tmpdir.join("invalid_path/output.txt")

    @redirect_output(str(output_file), logger=test_logger)
    def error_function() -> None:
        raise RuntimeError("An error occurred")

    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError):
            error_function()
        assert "Failed to redirect output" in caplog.text


def test_invalid_file_path_no_logger() -> None:

    """
    Test case 7: Invalid file path parameter
    """
    with pytest.raises(TypeError, match="file_path must be a string"):

        @redirect_output(123)
        def invalid_file_path_function() -> None:
            pass


def test_invalid_file_path_with_logger(caplog) -> None:

    """
    Test case 8: Invalid file path parameter with logger
    """
    with pytest.raises(TypeError, match="file_path must be a string"):
        with caplog.at_level(logging.ERROR):

            @redirect_output(123, logger=test_logger)
            def invalid_file_path_with_logger_function() -> None:
                pass

        assert "file_path must be a string" in caplog.text


def test_invalid_logger_type() -> None:

    """
    Test case 9: Invalid logger type
    """
    with pytest.raises(
        TypeError, match="logger must be an instance of logging.Logger or None"
    ):

        @redirect_output("output.txt", logger="not_a_logger")
        def invalid_logger_function() -> None:
            pass
