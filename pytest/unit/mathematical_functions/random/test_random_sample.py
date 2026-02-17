from typing import Any, cast

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.mathematical_functions]
from pyutils_collection.mathematical_functions.random.random_sample import random_sample


def test_random_sample_without_replacement() -> None:
    """
    Test case 1: Test random_sample without replacement.
    """
    population = [1, 2, 3, 4, 5]
    result = random_sample(population, 3, replace=False)
    assert len(result) == 3
    assert all(x in population for x in result)
    assert len(set(result)) == 3  # All elements should be unique


def test_random_sample_with_replacement() -> None:
    """
    Test case 2: Test random_sample with replacement.
    """
    population = [1, 2, 3]
    result = random_sample(population, 10, replace=True)
    assert len(result) == 10
    assert all(x in population for x in result)


def test_random_sample_full_population() -> None:
    """
    Test case 3: Test random_sample with count equal to population size.
    """
    population = [1, 2, 3, 4]
    result = random_sample(population, 4, replace=False)
    assert len(result) == 4
    assert set(result) == set(population)


def test_random_sample_zero_count() -> None:
    """
    Test case 4: Test random_sample with zero count.
    """
    population = [1, 2, 3]
    result = random_sample(population, 0)
    assert result == []


def test_random_sample_strings() -> None:
    """
    Test case 5: Test random_sample with string population.
    """
    population = ["apple", "banana", "cherry", "date"]
    result = random_sample(population, 2, replace=False)
    assert len(result) == 2
    assert all(x in population for x in result)
    assert len(set(result)) == 2


def test_random_sample_mixed_types() -> None:
    """
    Test case 6: Test random_sample with mixed type population.
    """
    population = [1, "two", 3.0, True, None]
    result = random_sample(population, 3, replace=False)
    assert len(result) == 3
    assert all(x in population for x in result)


def test_random_sample_single_element() -> None:
    """
    Test case 7: Test random_sample with single element population.
    """
    population = [42]
    result = random_sample(population, 1, replace=False)
    assert result == [42]


def test_random_sample_with_replacement_exceeds_population() -> None:
    """
    Test case 8: Test random_sample with replacement when count > population size.
    """
    population = [1, 2]
    result = random_sample(population, 5, replace=True)
    assert len(result) == 5
    assert all(x in population for x in result)


def test_random_sample_large_population() -> None:
    """
    Test case 9: Test random_sample with large population.
    """
    population = list(range(1000))
    result = random_sample(population, 10, replace=False)
    assert len(result) == 10
    assert all(x in population for x in result)
    assert len(set(result)) == 10


def test_random_sample_type_error_population() -> None:
    """
    Test case 10: Test random_sample with invalid type for population.
    """
    with pytest.raises(TypeError, match="population must be a list"):
        random_sample(cast(Any, "not a list"), 3)


def test_random_sample_type_error_count() -> None:
    """
    Test case 11: Test random_sample with invalid type for count.
    """
    with pytest.raises(TypeError, match="count must be an integer"):
        random_sample([1, 2, 3], cast(Any, "2"))


def test_random_sample_type_error_replace() -> None:
    """
    Test case 12: Test random_sample with invalid type for replace.
    """
    with pytest.raises(TypeError, match="replace must be a boolean"):
        random_sample([1, 2, 3], 2, replace=cast(Any, "true"))


def test_random_sample_value_error_negative_count() -> None:
    """
    Test case 13: Test random_sample with negative count.
    """
    with pytest.raises(ValueError, match="count must be non-negative"):
        random_sample([1, 2, 3], -1)


def test_random_sample_value_error_empty_population() -> None:
    """
    Test case 14: Test random_sample with empty population.
    """
    with pytest.raises(ValueError, match="population cannot be empty"):
        random_sample([], 1)


def test_random_sample_value_error_count_exceeds_population() -> None:
    """
    Test case 15: Test random_sample when count exceeds population size without replacement.
    """
    with pytest.raises(
        ValueError, match="count cannot exceed population size when replace=False"
    ):
        random_sample([1, 2, 3], 5, replace=False)
