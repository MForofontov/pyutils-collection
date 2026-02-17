"""
Unit tests for aggregate_by_group function.
"""

import pytest

# Try to import matplotlib - tests will be skipped if not available
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-GUI backend for testing
    from pyutils_collection.data_visualization_functions.data_transformers.aggregate_by_group import (
        aggregate_by_group,
    )

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    matplotlib = None  # type: ignore
    aggregate_by_group = None  # type: ignore

pytestmark = pytest.mark.skipif(
    not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed"
)
pytestmark = pytest.mark.unit
pytestmark = pytest.mark.data_visualization


def test_aggregate_by_group_mean() -> None:

    """
    Test case 1: Aggregate data by group using mean.
    """
    # Arrange
    data = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]
    groups = ["A", "B", "A", "B", "A", "B"]

    # Act
    result = aggregate_by_group(data, groups, agg_func="mean")

    # Assert
    assert isinstance(result, dict)
    assert "A" in result
    assert "B" in result
    assert result["A"] == 30.0  # (10 + 30 + 50) / 3
    assert result["B"] == 40.0  # (20 + 40 + 60) / 3


def test_aggregate_by_group_sum() -> None:

    """
    Test case 2: Aggregate data by group using sum.
    """
    # Arrange
    data = [5.0, 10.0, 15.0, 20.0]
    groups = ["X", "X", "Y", "Y"]

    # Act
    result = aggregate_by_group(data, groups, agg_func="sum")

    # Assert
    assert result["X"] == 15  # 5 + 10
    assert result["Y"] == 35  # 15 + 20


def test_aggregate_by_group_count() -> None:

    """
    Test case 3: Aggregate data by group using count.
    """
    # Arrange
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    groups = ["A", "A", "B", "B", "B"]

    # Act
    result = aggregate_by_group(data, groups, agg_func="count")

    # Assert
    assert result["A"] == 2
    assert result["B"] == 3


def test_aggregate_by_group_max() -> None:

    """
    Test case 4: Aggregate data by group using max.
    """
    # Arrange
    data = [10.0, 5.0, 20.0, 15.0, 30.0]
    groups = ["G1", "G1", "G2", "G1", "G2"]

    # Act
    result = aggregate_by_group(data, groups, agg_func="max")

    # Assert
    assert result["G1"] == 15  # max(10, 5, 15)
    assert result["G2"] == 30  # max(20, 30)


def test_aggregate_by_group_min() -> None:

    """
    Test case 5: Aggregate data by group using min.
    """
    # Arrange
    data = [10.0, 5.0, 20.0, 15.0, 30.0]
    groups = ["G1", "G1", "G2", "G1", "G2"]

    # Act
    result = aggregate_by_group(data, groups, agg_func="min")

    # Assert
    assert result["G1"] == 5  # min(10, 5, 15)
    assert result["G2"] == 20  # min(20, 30)


def test_aggregate_by_group_empty_data_raises_error() -> None:

    """
    Test case 6: ValueError for empty data.
    """
    # Arrange
    expected_message = "data cannot be empty"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        aggregate_by_group([], [])


def test_aggregate_by_group_mismatched_lengths_raises_error() -> None:

    """
    Test case 7: ValueError when data and groups have different lengths.
    """
    # Arrange
    data = [1.0, 2.0, 3.0]
    groups = ["A", "B"]
    expected_message = "data and groups must have.*same length"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        aggregate_by_group(data, groups)


def test_aggregate_by_group_invalid_method_raises_error() -> None:

    """
    Test case 8: ValueError for invalid aggregation method.
    """
    # Arrange
    data = [1.0, 2.0, 3.0]
    groups = ["A", "A", "B"]
    expected_message = "Unknown aggregation|invalid"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        aggregate_by_group(data, groups, agg_func="invalid")


def test_aggregate_by_group_invalid_type_raises_error() -> None:

    """
    Test case 9: TypeError for invalid data type.
    """
    # Arrange
    expected_message = "Cannot convert|could not convert|must be"

    # Act & Assert
    from typing import cast, Any
    with pytest.raises((TypeError, ValueError), match=expected_message):
        aggregate_by_group(cast(Any, "not_a_list"), ["A", "B"])


