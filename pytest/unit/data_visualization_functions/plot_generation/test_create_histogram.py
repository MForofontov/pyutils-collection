"""
Unit tests for create_histogram function.
"""

import pytest

# Try to import matplotlib and numpy - tests will be skipped if not available
try:
    import matplotlib
    import numpy as np

    matplotlib.use("Agg")  # Use non-GUI backend for testing
    import matplotlib.pyplot as plt

    from pyutils_collection.data_visualization_functions.plot_generation.create_histogram import (
        create_histogram,
    )

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    matplotlib = None  # type: ignore
    numpy = None  # type: ignore
    np = None  # type: ignore
    plt = None  # type: ignore
    create_histogram = None  # type: ignore

pytestmark = pytest.mark.skipif(
    not MATPLOTLIB_AVAILABLE, reason="matplotlib or numpy not installed"
)
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.data_visualization]


def test_create_histogram_basic() -> None:

    """
    Test case 1: Create basic histogram with default settings.
    """
    # Arrange
    data = [1, 2, 2, 3, 3, 3, 4, 4, 5]

    # Act
    fig, ax = create_histogram(data)

    # Assert
    assert fig is not None
    assert ax is not None

    # Cleanup
    plt.close(fig)


def test_create_histogram_with_bins() -> None:

    """
    Test case 2: Create histogram with custom number of bins.
    """
    # Arrange
    data = np.random.randn(1000)
    bins = 50

    # Act
    fig, ax = create_histogram(data, bins=bins)

    # Assert
    assert fig is not None
    # Check that patches were created (histogram bars)
    assert len(ax.patches) > 0

    # Cleanup
    plt.close(fig)


def test_create_histogram_with_styling() -> None:

    """
    Test case 3: Create histogram with custom styling.
    """
    # Arrange
    data = [10, 20, 20, 30, 30, 30, 40, 40, 50]

    # Act
    fig, ax = create_histogram(
        data, title="Distribution", xlabel="Value", ylabel="Frequency", colors=["green"]
    )

    # Assert
    assert ax.get_title() == "Distribution"
    assert ax.get_xlabel() == "Value"
    assert ax.get_ylabel() == "Frequency"

    # Cleanup
    plt.close(fig)


def test_create_histogram_normalized() -> None:

    """
    Test case 4: Create normalized histogram (density plot).
    """
    # Arrange
    data = np.random.normal(0, 1, 1000)

    # Act
    fig, ax = create_histogram(data, density=True)

    # Assert
    assert fig is not None

    # Cleanup
    plt.close(fig)


def test_create_histogram_empty_data_raises_error() -> None:

    """
    Test case 5: ValueError for empty data.
    """
    # Arrange
    data = []
    expected_message = (
        "dataset.*cannot be empty|data cannot be empty|empty.*not.*allowed"
    )

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        create_histogram(data)


def test_create_histogram_invalid_bins_raises_error() -> None:

    """
    Test case 6: ValueError for invalid bins value.
    """
    # Arrange
    data = [1, 2, 3, 4, 5]
    expected_message = "bins must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        create_histogram(data, bins=0)


def test_create_histogram_invalid_type_raises_error() -> None:

    """
    Test case 7: TypeError for invalid data type.
    """
    # Arrange
    data = "not_a_list"
    expected_message = "data must be|Cannot convert|could not convert"

    # Act & Assert
    with pytest.raises((TypeError, ValueError), match=expected_message):
        create_histogram(data)


def test_create_histogram_invalid_alpha_raises_error() -> None:

    """
    Test case 8: ValueError for invalid alpha value.
    """
    # Arrange
    data = [1, 2, 3, 4, 5]
    expected_message = "alpha must be between 0 and 1"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        create_histogram(data, alpha=1.5)


def test_create_histogram_numpy_array() -> None:

    """
    Test case 9: Create histogram from numpy array.
    """
    # Arrange
    data = np.array([1, 2, 2, 3, 3, 3, 4, 4, 5])

    # Act
    fig, ax = create_histogram(data)

    # Assert
    assert fig is not None

    # Cleanup
    plt.close(fig)


__all__ = ["test_create_histogram_basic"]
