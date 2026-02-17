"""
Unit tests for smooth_timeseries function.
"""

import pytest

# Try to import matplotlib and numpy - tests will be skipped if not available
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-GUI backend for testing
    import numpy as np

    from pyutils_collection.data_visualization_functions.data_transformers.smooth_timeseries import (
        smooth_timeseries,
    )

    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False


def _scipy_available() -> bool:
    """Check if scipy is available."""
    try:
        import scipy.signal  # noqa: F401
        return True
    except ImportError:
        return False
    matplotlib = None
    np = None
    smooth_timeseries = None

pytestmark = [
    pytest.mark.skipif(
        not DEPENDENCIES_AVAILABLE, reason="matplotlib and numpy not installed"
    ),
    pytest.mark.unit,
    pytest.mark.data_visualization,
]


def test_smooth_timeseries_basic() -> None:

    """
    Test case 1: Smooth timeseries with default settings.
    """
    # Arrange
    data = [1, 2, 3, 2, 1, 2, 3, 4, 3, 2]

    # Act
    smoothed = smooth_timeseries(data)

    # Assert
    assert len(smoothed) == len(data)
    assert isinstance(smoothed, (list, np.ndarray))


def test_smooth_timeseries_moving_average() -> None:

    """
    Test case 2: Smooth using moving average method.
    """
    # Arrange
    data = [10, 20, 30, 40, 50]
    window_size = 3

    # Act
    smoothed = smooth_timeseries(data, method="moving_average", window_size=window_size)

    # Assert
    assert len(smoothed) == len(data)


def test_smooth_timeseries_exponential() -> None:

    """
    Test case 3: Smooth using exponential smoothing.
    """
    # Arrange
    data = np.random.randn(100)

    # Act
    smoothed = smooth_timeseries(data, method="exponential", window_size=10)

    # Assert
    assert len(smoothed) == len(data)


@pytest.mark.skipif(
    not _scipy_available(),
    reason="scipy not installed (moved to bioutils-collection)"
)
def test_smooth_timeseries_savitzky_golay() -> None:

    """
    Test case 4: Smooth using Savitzky-Golay filter.
    """
    # Arrange
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # Act
    smoothed = smooth_timeseries(
        data, method="savgol", window_size=5, polynomial_order=2
    )

    # Assert
    assert len(smoothed) == len(data)


def test_smooth_timeseries_numpy_array() -> None:

    """
    Test case 5: Smooth numpy array data.
    """
    # Arrange
    data = np.array([1.0, 2.0, 3.0, 2.0, 1.0])

    # Act
    smoothed = smooth_timeseries(data)

    # Assert
    assert isinstance(smoothed, np.ndarray)
    assert len(smoothed) == len(data)


def test_smooth_timeseries_empty_raises_error() -> None:

    """
    Test case 6: ValueError for empty data.
    """
    # Arrange
    expected_message = "data cannot be empty"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        smooth_timeseries([])


def test_smooth_timeseries_invalid_window_raises_error() -> None:

    """
    Test case 7: ValueError for invalid window size.
    """
    # Arrange
    data = [1, 2, 3, 4, 5]
    expected_message = "window_size must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        smooth_timeseries(data, window_size=0)


def test_smooth_timeseries_invalid_method_raises_error() -> None:

    """
    Test case 8: ValueError for invalid smoothing method.
    """
    # Arrange
    data = [1, 2, 3, 4, 5]
    expected_message = (
        "Unknown.*method|Invalid.*method|Unsupported.*method|method.*must be"
    )

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        smooth_timeseries(data, method="invalid", window_size=3)


def test_smooth_timeseries_invalid_type_raises_error() -> None:

    """
    Test case 9: TypeError for invalid data type.
    """
    # Arrange
    expected_message = "Cannot convert|could not convert|must be"

    # Act & Assert
    with pytest.raises((TypeError, ValueError), match=expected_message):
        smooth_timeseries("not_a_list", window_size=3)


__all__ = ["test_smooth_timeseries_basic"]
