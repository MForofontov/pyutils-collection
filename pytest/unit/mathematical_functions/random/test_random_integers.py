from typing import Any, cast

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.mathematical_functions]
from pyutils_collection.mathematical_functions.random.random_integers import random_integers


def test_random_integers_default_range() -> None:
    """
    Test case 1: Test random_integers with default range.
    """
    result = random_integers(10)
    assert len(result) == 10
    assert all(isinstance(x, int) for x in result)
    assert all(0 <= x <= 100 for x in result)


def test_random_integers_custom_range() -> None:
    """
    Test case 2: Test random_integers with custom range.
    """
    result = random_integers(5, 10, 20)
    assert len(result) == 5
    assert all(isinstance(x, int) for x in result)
    assert all(10 <= x <= 20 for x in result)


def test_random_integers_zero_count() -> None:
    """
    Test case 3: Test random_integers with zero count.
    """
    result = random_integers(0)
    assert result == []


def test_random_integers_single_value() -> None:
    """
    Test case 4: Test random_integers with min_value == max_value.
    """
    result = random_integers(5, 42, 42)
    assert len(result) == 5
    assert all(x == 42 for x in result)


def test_random_integers_negative_range() -> None:
    """
    Test case 5: Test random_integers with negative range.
    """
    result = random_integers(3, -10, -5)
    assert len(result) == 3
    assert all(-10 <= x <= -5 for x in result)


def test_random_integers_large_count() -> None:
    """
    Test case 6: Test random_integers with large count.
    """
    result = random_integers(1000, 1, 10)
    assert len(result) == 1000
    assert all(1 <= x <= 10 for x in result)
    # Check that we get some variety (not all the same number)
    assert len(set(result)) > 1


def test_random_integers_type_error_count() -> None:
    """
    Test case 7: Test random_integers with invalid type for count.
    """
    with pytest.raises(TypeError, match="count must be an integer"):
        random_integers(cast(Any, "5"))


def test_random_integers_type_error_min_value() -> None:
    """
    Test case 8: Test random_integers with invalid type for min_value.
    """
    with pytest.raises(TypeError, match="min_value must be an integer"):
        random_integers(5, cast(Any, "0"), 10)


def test_random_integers_type_error_max_value() -> None:
    """
    Test case 9: Test random_integers with invalid type for max_value.
    """
    with pytest.raises(TypeError, match="max_value must be an integer"):
        random_integers(5, 0, cast(Any, "10"))


def test_random_integers_value_error_negative_count() -> None:
    """
    Test case 10: Test random_integers with negative count.
    """
    with pytest.raises(ValueError, match="count must be non-negative"):
        random_integers(-1)


def test_random_integers_value_error_invalid_range() -> None:
    """
    Test case 11: Test random_integers with min_value > max_value.
    """
    with pytest.raises(
        ValueError, match="min_value must be less than or equal to max_value"
    ):
        random_integers(5, 10, 5)
