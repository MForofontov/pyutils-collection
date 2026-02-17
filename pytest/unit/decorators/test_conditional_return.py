import pytest

pytestmark = [pytest.mark.unit, pytest.mark.decorators]
from pyutils_collection.decorators.conditional_return import conditional_return


def test_conditional_return_true() -> None:

    """
    Test case 1: Condition is true, return the specified value
    """

    def condition(x):
        return x > 10

    @conditional_return(condition, return_value="Condition met")
    def sample_function(x):
        return "Condition not met"

    assert sample_function(15) == "Condition met"


def test_conditional_return_false() -> None:

    """
    Test case 2: Condition is false, return the result of the wrapped function
    """

    def condition(x):
        return x > 10

    @conditional_return(condition, return_value="Condition met")
    def sample_function(x):
        return "Condition not met"

    assert sample_function(5) == "Condition not met"


def test_conditional_return_with_kwargs() -> None:

    """
    Test case 3: Condition with keyword arguments
    """

    def condition(x, y):
        return x + y > 10

    @conditional_return(condition, return_value="Condition met")
    def sample_function(x, y):
        return "Condition not met"

    assert sample_function(5, y=6) == "Condition met"
    assert sample_function(3, y=4) == "Condition not met"


def test_conditional_return_with_multiple_args() -> None:

    """
    Test case 4: Condition with multiple positional arguments
    """

    def condition(x, y, z):
        return x + y + z > 10

    @conditional_return(condition, return_value="Condition met")
    def sample_function(x, y, z):
        return "Condition not met"

    assert sample_function(3, 4, 5) == "Condition met"
    assert sample_function(1, 2, 3) == "Condition not met"


def test_conditional_return_with_default_args() -> None:

    """
    Test case 5: Condition with default arguments
    """

    def condition(x, y=5):
        return x + y > 10

    @conditional_return(condition, return_value="Condition met")
    def sample_function(x, y=5):
        return "Condition not met"

    assert sample_function(6) == "Condition met"
    assert sample_function(4) == "Condition not met"
    assert sample_function(3, y=8) == "Condition met"


def test_conditional_return_with_no_args() -> None:

    """
    Test case 6: Condition with no arguments
    """

    def condition():
        return True

    @conditional_return(condition, return_value="Condition met")
    def sample_function():
        return "Condition not met"

    assert sample_function() == "Condition met"


def test_conditional_return_condition_raises_error() -> None:

    """
    Test case 7: Condition function raises an error
    """

    def condition(x):
        raise ValueError("Test error")

    @conditional_return(condition, return_value="Condition met")
    def sample_function(x):
        return "Condition not met"

    with pytest.raises(
        RuntimeError, match="Condition function raised an error: Test error"
    ):
        sample_function(5)


def test_conditional_return_invalid_condition() -> None:

    """
    Test case 8: Invalid condition (not callable)
    """
    with pytest.raises(TypeError, match="Condition must be callable"):

        @conditional_return("not_callable", return_value="Condition met")
        def sample_function(x):
            return "Condition not met"
