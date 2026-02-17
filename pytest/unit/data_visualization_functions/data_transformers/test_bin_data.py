"""
Unit tests for bin_data function.
"""

import pytest

# Try to import matplotlib and numpy - tests will be skipped if not available
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-GUI backend for testing
    import numpy as np

    from pyutils_collection.data_visualization_functions.data_transformers.bin_data import bin_data

    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    matplotlib = None  # type: ignore
    np = None  # type: ignore
    bin_data = None  # type: ignore

pytestmark = [
    pytest.mark.skipif(
        not DEPENDENCIES_AVAILABLE, reason="matplotlib and numpy not installed"
    ),
    pytest.mark.unit,
    pytest.mark.data_visualization,
]


def test_bin_data_basic() -> None:

    """
    Test case 1: Bin data with default settings.
    """
    # Arrange
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # Act
    binned_indices, bin_edges = bin_data(data, bins=5)

    # Assert
    assert len(bin_edges) == 6  # bins + 1 edges
    assert len(binned_indices) == len(data)


def test_bin_data_custom_bins() -> None:

    """
    Test case 2: Bin data with custom number of bins.
    """
    # Arrange
    data = np.random.randn(1000)

    # Act
    binned_indices, bin_edges = bin_data(data, bins=20)

    # Assert
    assert len(bin_edges) == 21
    assert len(binned_indices) == len(data)


def test_bin_data_custom_bin_edges() -> None:

    """
    Test case 3: Bin data with custom bin edges.
    """
    # Arrange
    data = [1, 2, 3, 4, 5]
    custom_edges = [0, 2, 4, 6]

    # Act
    binned_indices, bin_edges = bin_data(data, bins=custom_edges)

    # Assert
    assert len(bin_edges) == len(custom_edges)


def test_bin_data_numpy_array() -> None:

    """
    Test case 4: Bin numpy array data.
    """
    # Arrange
    data = np.array([1.5, 2.5, 3.5, 4.5, 5.5])

    # Act
    binned_indices, bin_edges = bin_data(data, bins=5)

    # Assert
    assert isinstance(bin_edges, np.ndarray)
    assert isinstance(binned_indices, np.ndarray)


def test_bin_data_empty_raises_error() -> None:

    """
    Test case 5: ValueError for empty data.
    """
    # Arrange
    expected_message = "data cannot be empty"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        bin_data([])


def test_bin_data_invalid_bins_raises_error() -> None:

    """
    Test case 6: ValueError for invalid number of bins.
    """
    # Arrange
    data = [1, 2, 3, 4, 5]
    expected_message = "bins must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        bin_data(data, bins=0)


def test_bin_data_invalid_type_raises_error() -> None:

    """
    Test case 7: TypeError for invalid data type.
    """
    # Arrange
    expected_message = "Cannot convert|could not convert|must be"

    # Act & Assert
    with pytest.raises((TypeError, ValueError), match=expected_message):
        bin_data("not_a_list")


def test_bin_data_single_value() -> None:

    """
    Test case 8: Bin data with single unique value.
    """
    # Arrange
    data = [5, 5, 5, 5, 5]

    # Act
    binned_indices, bin_edges = bin_data(data, bins=3)

    # Assert
    assert len(binned_indices) == len(data)


__all__ = ["test_bin_data_basic"]
