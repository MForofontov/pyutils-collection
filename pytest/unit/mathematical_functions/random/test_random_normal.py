import math
from typing import Any, cast

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.mathematical_functions]
from pyutils_collection.mathematical_functions.random.random_normal import random_normal


def test_random_normal_default_parameters() -> None:
    """
    Test case 1: Test random_normal with default parameters.
    """
    result = random_normal(100)
    assert len(result) == 100
    assert all(isinstance(x, float) for x in result)

    # Check that mean is approximately 0 (within reasonable bounds for random data)
    sample_mean = sum(result) / len(result)
    assert abs(sample_mean) < 0.5  # Should be close to 0 for large sample


def test_random_normal_custom_parameters() -> None:
    """
    Test case 2: Test random_normal with custom mean and stddev.
    """
    result = random_normal(1000, mean=10.0, stddev=2.0)
    assert len(result) == 1000
    assert all(isinstance(x, float) for x in result)

    # Check that sample mean is approximately the specified mean
    sample_mean = sum(result) / len(result)
    assert abs(sample_mean - 10.0) < 1.0  # Should be close to 10 for large sample


def test_random_normal_zero_count() -> None:
    """
    Test case 3: Test random_normal with zero count.
    """
    result = random_normal(0)
    assert result == []


def test_random_normal_single_value() -> None:
    """
    Test case 4: Test random_normal with count=1.
    """
    result = random_normal(1, mean=5.0, stddev=1.0)
    assert len(result) == 1
    assert isinstance(result[0], float)


def test_random_normal_integer_parameters() -> None:
    """
    Test case 5: Test random_normal with integer mean and stddev.
    """
    result = random_normal(10, mean=5, stddev=2)
    assert len(result) == 10
    assert all(isinstance(x, float) for x in result)


def test_random_normal_large_count() -> None:
    """
    Test case 6: Test random_normal with large count.
    """
    result = random_normal(10000, mean=0.0, stddev=1.0)
    assert len(result) == 10000

    # For large samples, check statistical properties
    sample_mean = sum(result) / len(result)
    sample_var = sum((x - sample_mean) ** 2 for x in result) / (len(result) - 1)
    sample_stddev = math.sqrt(sample_var)

    # Mean should be close to 0, stddev close to 1
    assert abs(sample_mean) < 0.1
    assert abs(sample_stddev - 1.0) < 0.1


def test_random_normal_type_error_count() -> None:
    """
    Test case 7: Test random_normal with invalid type for count.
    """
    with pytest.raises(TypeError, match="count must be an integer"):
        random_normal(cast(Any, "10"))


def test_random_normal_type_error_mean() -> None:
    """
    Test case 8: Test random_normal with invalid type for mean.
    """
    with pytest.raises(TypeError, match="mean must be numeric"):
        random_normal(10, mean=cast(Any, "0.0"))


def test_random_normal_type_error_stddev() -> None:
    """
    Test case 9: Test random_normal with invalid type for stddev.
    """
    with pytest.raises(TypeError, match="stddev must be numeric"):
        random_normal(10, stddev=cast(Any, "1.0"))


def test_random_normal_value_error_negative_count() -> None:
    """
    Test case 10: Test random_normal with negative count.
    """
    with pytest.raises(ValueError, match="count must be non-negative"):
        random_normal(-1)


def test_random_normal_value_error_zero_stddev() -> None:
    """
    Test case 11: Test random_normal with zero stddev.
    """
    with pytest.raises(ValueError, match="stddev must be positive"):
        random_normal(10, stddev=0.0)


def test_random_normal_value_error_negative_stddev() -> None:
    """
    Test case 12: Test random_normal with negative stddev.
    """
    with pytest.raises(ValueError, match="stddev must be positive"):
        random_normal(10, stddev=-1.0)
