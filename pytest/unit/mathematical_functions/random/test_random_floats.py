from typing import Any, cast

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.mathematical_functions]
from pyutils_collection.mathematical_functions.random.random_floats import random_floats


def test_random_floats_default_range() -> None:
    """
    Test case 1: Test random_floats with default range.
    """
    result = random_floats(10)
    assert len(result) == 10
    assert all(isinstance(x, float) for x in result)
    assert all(0.0 <= x < 1.0 for x in result)


def test_random_floats_custom_range() -> None:
    """
    Test case 2: Test random_floats with custom range.
    """
    result = random_floats(5, 5.0, 10.0)
    assert len(result) == 5
    assert all(isinstance(x, float) for x in result)
    assert all(5.0 <= x < 10.0 for x in result)


def test_random_floats_zero_count() -> None:
    """
    Test case 3: Test random_floats with zero count.
    """
    result = random_floats(0)
    assert result == []


def test_random_floats_negative_range() -> None:
    """
    Test case 4: Test random_floats with negative range.
    """
    result = random_floats(3, -5.5, -1.1)
    assert len(result) == 3
    assert all(-5.5 <= x < -1.1 for x in result)


def test_random_floats_integer_inputs() -> None:
    """
    Test case 5: Test random_floats with integer min/max values.
    """
    result = random_floats(5, 1, 10)
    assert len(result) == 5
    assert all(isinstance(x, float) for x in result)
    assert all(1.0 <= x < 10.0 for x in result)


def test_random_floats_large_count() -> None:
    """
    Test case 6: Test random_floats with large count.
    """
    result = random_floats(1000, 0.0, 1.0)
    assert len(result) == 1000
    assert all(0.0 <= x < 1.0 for x in result)
    # Check that we get variety (should not all be exactly the same)
    assert len(set(result)) > 900  # Very high probability of uniqueness


def test_random_floats_type_error_count() -> None:
    """
    Test case 7: Test random_floats with invalid type for count.
    """
    with pytest.raises(TypeError, match="count must be an integer"):
        random_floats(cast(Any, "5"))


def test_random_floats_type_error_min_value() -> None:
    """
    Test case 8: Test random_floats with invalid type for min_value.
    """
    with pytest.raises(TypeError, match="min_value must be numeric"):
        random_floats(5, cast(Any, "0.0"), 1.0)


def test_random_floats_type_error_max_value() -> None:
    """
    Test case 9: Test random_floats with invalid type for max_value.
    """
    with pytest.raises(TypeError, match="max_value must be numeric"):
        random_floats(5, 0.0, cast(Any, "1.0"))


def test_random_floats_value_error_negative_count() -> None:
    """
    Test case 10: Test random_floats with negative count.
    """
    with pytest.raises(ValueError, match="count must be non-negative"):
        random_floats(-1)


def test_random_floats_value_error_invalid_range() -> None:
    """
    Test case 11: Test random_floats with min_value >= max_value.
    """
    with pytest.raises(ValueError, match="min_value must be less than max_value"):
        random_floats(5, 10.0, 10.0)


def test_random_floats_value_error_min_greater_than_max() -> None:
    """
    Test case 12: Test random_floats with min_value > max_value.
    """
    with pytest.raises(ValueError, match="min_value must be less than max_value"):
        random_floats(5, 10.0, 5.0)
