"""
Unit tests for calculate_moving_statistics function.
"""

import pytest

# Try to import matplotlib and numpy - tests will be skipped if not available
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-GUI backend for testing
    import numpy as np

    from pyutils_collection.data_visualization_functions.data_transformers.calculate_moving_statistics import (
        calculate_moving_statistics,
    )

    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    matplotlib = None  # type: ignore
    np = None  # type: ignore
    calculate_moving_statistics = None  # type: ignore

pytestmark = [
    pytest.mark.skipif(
        not DEPENDENCIES_AVAILABLE, reason="matplotlib and numpy not installed"
    ),
    pytest.mark.unit,
    pytest.mark.data_visualization,
]


def test_calculate_moving_statistics_mean() -> None:

    """
    Test case 1: Calculate moving mean.
    """
    # Arrange
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    window_size = 3

    # Act
    result = calculate_moving_statistics(
        data, window_size=window_size, statistics=["mean"]
    )

    # Assert
    assert isinstance(result, dict)
    assert "mean" in result
    assert len(result["mean"]) == len(data)


def test_calculate_moving_statistics_median() -> None:

    """
    Test case 2: Calculate moving median.
    """
    # Arrange
    data = [10, 1, 10, 2, 10, 3, 10, 4]
    window_size = 3

    # Act
    result = calculate_moving_statistics(
        data, window_size=window_size, statistics=["median"]
    )

    # Assert
    assert isinstance(result, dict)
    assert "median" in result
    assert len(result["median"]) == len(data)


def test_calculate_moving_statistics_std() -> None:

    """
    Test case 3: Calculate moving standard deviation.
    """
    # Arrange
    data = np.random.randn(100)
    window_size = 10

    # Act
    result = calculate_moving_statistics(
        data, window_size=window_size, statistics=["std"]
    )

    # Assert
    assert isinstance(result, dict)
    assert "std" in result
    assert len(result["std"]) == len(data)
    assert all(v >= 0 for v in result["std"])  # Standard deviation is non-negative


def test_calculate_moving_statistics_max() -> None:

    """
    Test case 4: Calculate moving maximum.
    """
    # Arrange
    data = [3, 1, 4, 1, 5, 9, 2, 6]
    window_size = 3

    # Act
    result = calculate_moving_statistics(
        data, window_size=window_size, statistics=["max"]
    )

    # Assert
    assert isinstance(result, dict)
    assert "max" in result
    assert len(result["max"]) == len(data)


def test_calculate_moving_statistics_min() -> None:

    """
    Test case 5: Calculate moving minimum.
    """
    # Arrange
    data = [3, 1, 4, 1, 5, 9, 2, 6]
    window_size = 3

    # Act
    result = calculate_moving_statistics(
        data, window_size=window_size, statistics=["min"]
    )

    # Assert
    assert isinstance(result, dict)
    assert "min" in result
    assert len(result["min"]) == len(data)


def test_calculate_moving_statistics_empty_raises_error() -> None:

    """
    Test case 6: ValueError for empty data.
    """
    # Arrange
    expected_message = "data cannot be empty"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        calculate_moving_statistics([], window_size=3)


def test_calculate_moving_statistics_invalid_window_raises_error() -> None:

    """
    Test case 7: ValueError for invalid window size.
    """
    # Arrange
    data = [1, 2, 3, 4, 5]
    expected_message = "window_size must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        calculate_moving_statistics(data, window_size=-1)


def test_calculate_moving_statistics_invalid_statistic_raises_error() -> None:

    """
    Test case 8: ValueError for invalid statistic type.
    """
    # Arrange
    data = [1, 2, 3, 4, 5]
    expected_message = "Unknown statistic|invalid"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        calculate_moving_statistics(data, window_size=3, statistics=["invalid"])


def test_calculate_moving_statistics_invalid_type_raises_error() -> None:

    """
    Test case 9: TypeError for invalid data type.
    """
    # Arrange
    expected_message = "Cannot convert|could not convert|must be"

    # Act & Assert
    with pytest.raises((TypeError, ValueError), match=expected_message):
        calculate_moving_statistics("not_a_list", window_size=3)


__all__ = ["test_calculate_moving_statistics_mean"]
