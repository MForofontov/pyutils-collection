import time

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.testing]
from pyutils_collection.testing_functions.benchmark_helpers.benchmark_function import benchmark_function


def test_benchmark_function_simple_function() -> None:
    """
    Test case 1: Benchmark simple function.
    """

    # Arrange
    def simple_func(x):
        return x * 2

    # Act
    result = benchmark_function(simple_func, 5, iterations=10)

    # Assert
    assert "total_time" in result
    assert "avg_time" in result
    assert "min_time" in result
    assert "max_time" in result
    assert result["total_time"] >= 0
    assert result["avg_time"] >= 0


def test_benchmark_function_with_sleep() -> None:
    """
    Test case 2: Benchmark function with sleep.
    """

    # Arrange
    def slow_func():
        time.sleep(0.01)
        return True

    # Act
    result = benchmark_function(slow_func, iterations=5)

    # Assert
    assert result["avg_time"] >= 0.01


def test_benchmark_function_single_iteration() -> None:
    """
    Test case 3: Benchmark with single iteration.
    """

    # Arrange
    def test_func() -> None:

        return 42

    # Act
    result = benchmark_function(test_func, iterations=1)

    # Assert
    assert result["min_time"] == result["max_time"]
    assert result["avg_time"] == result["total_time"]


def test_benchmark_function_with_args() -> None:
    """
    Test case 4: Benchmark function with arguments.
    """

    # Arrange
    def add_func(a, b):
        return a + b

    # Act
    result = benchmark_function(add_func, 1, 2, iterations=10)

    # Assert
    assert result["avg_time"] >= 0


def test_benchmark_function_with_kwargs() -> None:
    """
    Test case 5: Benchmark function with kwargs.
    """

    # Arrange
    def multiply_func(x=1, y=1):
        return x * y

    # Act
    result = benchmark_function(multiply_func, iterations=10, x=5, y=3)

    # Assert
    assert result["avg_time"] >= 0


def test_benchmark_function_type_error_func() -> None:
    """
    Test case 6: TypeError for non-callable func.
    """
    # Act & Assert
    with pytest.raises(TypeError, match="func must be callable"):
        benchmark_function("not callable", iterations=10)


def test_benchmark_function_type_error_iterations() -> None:
    """
    Test case 7: TypeError for invalid iterations type.
    """

    # Arrange
    def test_func() -> None:

        return True

    # Act & Assert
    with pytest.raises(TypeError, match="iterations must be an integer"):
        benchmark_function(test_func, iterations="10")


def test_benchmark_function_value_error_zero_iterations() -> None:
    """
    Test case 8: ValueError for zero iterations.
    """

    # Arrange
    def test_func() -> None:

        return True

    # Act & Assert
    with pytest.raises(ValueError, match="iterations must be positive"):
        benchmark_function(test_func, iterations=0)


def test_benchmark_function_value_error_negative_iterations() -> None:
    """
    Test case 9: ValueError for negative iterations.
    """

    # Arrange
    def test_func() -> None:

        return True

    # Act & Assert
    with pytest.raises(ValueError, match="iterations must be positive"):
        benchmark_function(test_func, iterations=-1)
