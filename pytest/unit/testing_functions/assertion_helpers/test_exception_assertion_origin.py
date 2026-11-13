import pytest

from pyutils_collection.testing_functions import assert_raises_with_message

pytestmark = [pytest.mark.unit, pytest.mark.testing]


@pytest.mark.parametrize("expected", [AssertionError, Exception])
def test_helper_cannot_satisfy_its_own_exception_expectation(
    expected: type[Exception],
) -> None:
    with pytest.raises(AssertionError, match="no exception was raised"):
        assert_raises_with_message(lambda: None, expected, "")


@pytest.mark.parametrize("expected", [AssertionError, Exception])
def test_actual_assertion_from_callable_is_accepted(expected: type[Exception]) -> None:
    def fail() -> None:
        raise AssertionError("caller failure")

    assert_raises_with_message(fail, expected, "caller failure")
