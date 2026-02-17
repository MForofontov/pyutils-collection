"""
Unit tests for pivot_for_heatmap function.
"""

import pytest
from typing import cast, Any

# Try to import matplotlib and numpy - tests will be skipped if not available
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-GUI backend for testing
    import numpy as np

    from pyutils_collection.data_visualization_functions.data_transformers.pivot_for_heatmap import (
        pivot_for_heatmap,
    )

    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    matplotlib = None  # type: ignore
    np = None  # type: ignore
    pivot_for_heatmap = None  # type: ignore

pytestmark = [
    pytest.mark.skipif(
        not DEPENDENCIES_AVAILABLE, reason="matplotlib and numpy not installed"
    ),
    pytest.mark.unit,
    pytest.mark.data_visualization,
]


def test_pivot_for_heatmap_basic() -> None:

    """
    Test case 1: Pivot data for heatmap with basic input.
    """
    # Arrange
    data = [10.0, 20.0, 30.0, 40.0]
    rows = ["A", "A", "B", "B"]
    cols = ["X", "Y", "X", "Y"]

    # Act
    matrix, row_labels, col_labels = pivot_for_heatmap(data, rows, cols)

    # Assert
    assert isinstance(matrix, np.ndarray)
    assert matrix.shape == (2, 2)
    assert list(row_labels) == ["A", "B"]
    assert list(col_labels) == ["X", "Y"]


def test_pivot_for_heatmap_larger_grid() -> None:

    """
    Test case 2: Pivot data for larger heatmap grid.
    """
    # Arrange
    data = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]
    rows = ["R1", "R1", "R1", "R2", "R2", "R2"]
    cols = ["C1", "C2", "C3", "C1", "C2", "C3"]

    # Act
    matrix, row_labels, col_labels = pivot_for_heatmap(data, rows, cols)

    # Assert
    assert matrix.shape == (2, 3)
    assert list(row_labels) == ["R1", "R2"]
    assert list(col_labels) == ["C1", "C2", "C3"]


def test_pivot_for_heatmap_missing_combinations() -> None:

    """
    Test case 3: Pivot with missing row/column combinations.
    """
    # Arrange
    data = [1.0, 2.0, 3.0]
    rows = ["A", "A", "B"]
    cols = ["X", "Y", "X"]

    # Act
    matrix, row_labels, col_labels = pivot_for_heatmap(data, rows, cols)

    # Assert
    assert isinstance(matrix, np.ndarray)
    assert matrix.shape == (2, 2)
    # B-Y combination should be NaN
    assert np.isnan(matrix[1, 1])


def test_pivot_for_heatmap_single_cell() -> None:

    """
    Test case 4: Pivot with single data point.
    """
    # Arrange
    data = [42.0]
    rows = ["A"]
    cols = ["X"]

    # Act
    matrix, row_labels, col_labels = pivot_for_heatmap(data, rows, cols)

    # Assert
    assert matrix.shape == (1, 1)
    assert matrix[0, 0] == 42


def test_pivot_for_heatmap_empty_raises_error() -> None:

    """
    Test case 5: ValueError for empty inputs.
    """
    # Arrange
    expected_message = "data cannot be empty"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        pivot_for_heatmap([], [], [])


def test_pivot_for_heatmap_mismatched_lengths_raises_error() -> None:

    """
    Test case 6: ValueError when input lengths don't match.
    """
    # Arrange
    data = [1.0, 2.0]
    rows = ["A", "B"]
    cols = ["X"]
    expected_message = "data.*row_labels.*col_labels.*same length|length.*mismatch"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        pivot_for_heatmap(data, rows, cols)


def test_pivot_for_heatmap_invalid_type_raises_error() -> None:

    """
    Test case 7: TypeError for invalid input type.
    """
    # Arrange
    expected_message = "data must be|Cannot convert|could not convert"

    # Act & Assert
    from typing import cast, Any
    with pytest.raises((TypeError, ValueError), match=expected_message):
        pivot_for_heatmap(cast(Any, "not_a_list"), ["A"], ["X"])


def test_pivot_for_heatmap_duplicate_coordinates() -> None:

    """
    Test case 8: Aggregate duplicate row/col combinations.
    """
    # Arrange
    data = [10.0, 20.0, 30.0]
    rows = ["A", "A", "A"]
    cols = ["X", "X", "X"]

    # Act - aggregate duplicates using sum
    matrix, row_labels, col_labels = pivot_for_heatmap(data, rows, cols, agg_func="sum")

    # Assert
    assert matrix.shape == (1, 1)
    assert matrix[0, 0] == 60.0  # Sum of 10, 20, 30


def test_pivot_for_heatmap_invalid_data_type_raises_error() -> None:

    """
    Test case 9: TypeError for invalid input type (second variant).
    """
    # Arrange
    expected_message = "Cannot convert data to numeric array"

    # Act & Assert
    from typing import cast, Any
    with pytest.raises(TypeError, match=expected_message):
        pivot_for_heatmap(cast(Any, "not_a_list"), ["A"], ["X"])


def test_pivot_for_heatmap_handles_duplicate_coordinates() -> None:

    """
    Test case 8: Handle duplicate row/col coordinates.
    """
    # Arrange
    rows = ["A", "A"]
    cols = ["X", "X"]
    values = [10.0, 20.0]

    # Act
    matrix, row_labels, col_labels = pivot_for_heatmap(
        values, rows, cols, agg_func="mean"
    )

    # Assert
    assert matrix.shape == (1, 1)
    assert matrix[0, 0] == 15.0  # Mean of 10 and 20
    assert len(row_labels) == 1
    assert len(col_labels) == 1


