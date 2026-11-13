import pytest

pytestmark = [pytest.mark.unit, pytest.mark.testing]
from pyutils_collection.testing_functions.assertion_helpers.assert_almost_equal import (
    assert_almost_equal,
)


def test_assert_almost_equal_exactly_equal() -> None:
    """
    Test case 1: Assert exactly equal values.
    """
    # Act & Assert
    assert_almost_equal(1.0, 1.0)


def test_assert_almost_equal_within_tolerance() -> None:
    """
    Test case 2: Assert values within tolerance.
    """
    # Act & Assert
    assert_almost_equal(0.1 + 0.2, 0.3, 1e-9)


def test_assert_almost_equal_custom_tolerance() -> None:
    """
    Test case 4: Assert values with custom tolerance.
    """
    # Act & Assert
    assert_almost_equal(1.001, 1.002, 0.01)


def test_assert_almost_equal_integers() -> None:
    """
    Test case 5: Assert with integer values.
    """
    # Act & Assert
    assert_almost_equal(5, 5)


def test_assert_almost_equal_type_error_actual() -> None:
    """
    Test case 6: TypeError for invalid actual type.
    """
    # Act & Assert
    with pytest.raises(TypeError, match="actual must be a number"):
        assert_almost_equal("1.0", 1.0)


def test_assert_almost_equal_type_error_expected() -> None:
    """
    Test case 7: TypeError for invalid expected type.
    """
    # Act & Assert
    with pytest.raises(TypeError, match="expected must be a number"):
        assert_almost_equal(1.0, "1.0")


def test_assert_almost_equal_type_error_tolerance() -> None:
    """
    Test case 8: TypeError for invalid tolerance type.
    """
    # Act & Assert
    with pytest.raises(TypeError, match="tolerance must be a number"):
        assert_almost_equal(1.0, 1.0, "0.1")


def test_assert_almost_equal_value_error_negative_tolerance() -> None:
    """
    Test case 9: ValueError for negative tolerance.
    """
    # Act & Assert
    with pytest.raises(ValueError, match="tolerance must be non-negative"):
        assert_almost_equal(1.0, 1.0, -0.1)


def test_assert_almost_equal_assertion_error_exceeds_tolerance() -> None:
    """
    Test case 10: AssertionError when difference exceeds tolerance.
    """
    # Act & Assert
    with pytest.raises(
        AssertionError, match="Values differ by .* which exceeds tolerance"
    ):
        assert_almost_equal(1.0, 2.0, 0.1)


@pytest.mark.parametrize(
    ("actual", "expected"),
    [(float("nan"), 1.0), (1.0, float("nan")), (float("nan"), float("nan"))],
)
def test_almost_equal_rejects_nan(actual: float, expected: float) -> None:
    with pytest.raises(AssertionError):
        assert_almost_equal(actual, expected)


def test_almost_equal_rejects_nan_tolerance() -> None:
    with pytest.raises(ValueError):
        assert_almost_equal(1.0, 2.0, float("nan"))


@pytest.mark.parametrize("value", [float("inf"), -float("inf"), 10**400])
def test_almost_equal_identical_extreme_values(value: float) -> None:
    assert_almost_equal(value, value)


@pytest.mark.parametrize(
    ("actual", "expected"), [(float("inf"), 1.0), (float("inf"), -float("inf"))]
)
def test_almost_equal_different_infinities(actual: float, expected: float) -> None:
    with pytest.raises(AssertionError):
        assert_almost_equal(actual, expected)
