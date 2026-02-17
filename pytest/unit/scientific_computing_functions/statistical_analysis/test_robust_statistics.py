"""
Unit tests for robust_statistics function.

Tests cover normal operation, edge cases, and error conditions.
"""

import warnings
from typing import Any, cast

try:
    import numpy as np
    import scipy
    from pyutils_collection.scientific_computing_functions.statistical_analysis.robust_statistics import (
        robust_statistics,
    )
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None  # type: ignore[assignment]
    scipy = None
    robust_statistics = None  # type: ignore[assignment]

import pytest

pytestmark = [
    pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy/scipy not installed"),
    pytest.mark.unit,
    pytest.mark.scientific_computing,
]

# Normal operation tests


def test_robust_statistics_basic_dataset() -> None:
    """Test case 1: Normal operation with basic dataset."""
    # Arrange
    data = [1.0, 2.0, 3.0, 4.0, 5.0]

    # Act
    result = robust_statistics(data)

    # Assert
    assert "median" in result
    assert "mad" in result
    assert "trimmed_mean" in result
    assert "winsorized_mean" in result
    assert "iqr" in result
    assert result["median"] == 3


def test_robust_statistics_with_outliers() -> None:
    """Test case 2: Normal operation with outliers."""
    # Arrange
    data = [1.0, 2.0, 3.0, 4.0, 5.0, 100.0]  # 100 is an outlier

    # Act
    result = robust_statistics(data)

    # Assert
    assert result["median"] == 3.5  # Not affected by outlier
    assert (
        result["trimmed_mean"] < result["winsorized_mean"] or result["trimmed_mean"] > 0
    )
    assert result["mad"] > 0


def test_robust_statistics_numpy_array() -> None:
    """Test case 3: Normal operation with numpy array."""
    # Arrange
    data = np.array([10.0, 20.0, 30.0, 40.0, 50.0])

    # Act
    result = robust_statistics(data)

    # Assert
    assert result["median"] == 30.0
    assert result["iqr"] == 20.0


def test_robust_statistics_high_outliers() -> None:
    """Test case 4: Normal operation with extreme high outliers."""
    # Arrange
    data = [1.0, 2.0, 3.0, 4.0, 5.0, 1000.0, 2000.0]

    # Act
    result = robust_statistics(data)

    # Assert
    assert result["median"] == 4  # Robust to outliers
    assert result["mad"] > 0


def test_robust_statistics_negative_values() -> None:
    """Test case 5: Normal operation with negative values."""
    # Arrange
    data = [-10.0, -5.0, 0.0, 5.0, 10.0]

    # Act
    result = robust_statistics(data)

    # Assert
    assert result["median"] == 0
    assert result["iqr"] == 10.0


def test_robust_statistics_large_dataset() -> None:
    """Test case 6: Normal operation with large dataset."""
    # Arrange
    np.random.seed(42)
    data = np.random.normal(0, 1, 1000)

    # Act
    result = robust_statistics(data)

    # Assert
    assert abs(result["median"]) < 0.5  # Near 0
    assert result["mad"] > 0
    assert result["iqr"] > 0


# Edge case tests


def test_robust_statistics_identical_values() -> None:
    """Test case 7: Edge case with all identical values."""
    # Arrange
    data = [5.0] * 10

    # Act
    result = robust_statistics(data)

    # Assert
    assert result["median"] == 5.0
    assert result["mad"] == 0.0  # No deviation
    assert result["iqr"] == 0.0  # No range
    assert result["trimmed_mean"] == 5.0
    assert result["winsorized_mean"] == 5.0


def test_robust_statistics_small_dataset() -> None:
    """Test case 8: Edge case with minimum dataset size."""
    # Arrange
    data = [1.0, 2.0, 3.0]

    # Act
    result = robust_statistics(data)

    # Assert
    assert result["median"] == 2.0
    assert "mad" in result
    assert "iqr" in result


def test_robust_statistics_two_values() -> None:
    """Test case 9: Edge case with only two values."""
    # Arrange
    data = [1.0, 2.0]

    # Act
    result = robust_statistics(data)

    # Assert
    assert result["median"] == 1.5
    assert result["iqr"] == 0.5


def test_robust_statistics_single_outlier_low() -> None:
    """Test case 10: Edge case with single low outlier."""
    # Arrange
    data = [-1000.0, 1.0, 2.0, 3.0, 4.0, 5.0]

    # Act
    result = robust_statistics(data)

    # Assert
    assert result["median"] == 2.5  # Not affected by outlier
    assert result["mad"] > 0


def test_robust_statistics_even_count() -> None:
    """Test case 11: Edge case with even number of values."""
    # Arrange
    data = [1.0, 2.0, 3.0, 4.0]

    # Act
    result = robust_statistics(data)

    # Assert
    assert result["median"] == 2.5
    assert result["iqr"] == 1.5


def test_robust_statistics_mixed_scale() -> None:
    """Test case 12: Edge case with mixed scale values."""
    # Arrange
    data = [0.01, 0.02, 100, 200, 300]

    # Act
    result = robust_statistics(data)

    # Assert
    assert result["median"] == 100
    assert result["mad"] > 0


# Error case tests


def test_robust_statistics_invalid_data_type() -> None:
    """Test case 13: TypeError for invalid data type."""
    # Arrange
    invalid_data = cast(Any, "not_a_list")
    expected_message = "data must be a list or numpy array"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        robust_statistics(invalid_data)


def test_robust_statistics_empty_data() -> None:
    """Test case 14: ValueError for empty data."""
    # Arrange
    empty_data: list[float] = []
    expected_message = "data cannot be empty"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        robust_statistics(empty_data)


def test_robust_statistics_single_value() -> None:
    """Test case 15: Edge case with single value."""
    # Arrange
    single_value = [5.0]

    # Act
    result = robust_statistics(single_value)

    # Assert
    assert result["median"] == 5.0
    assert result["mad"] == 0.0
    assert result["iqr"] == 0.0


def test_robust_statistics_non_numeric_values() -> None:
    """Test case 16: ValueError for non-numeric values."""
    # Arrange
    invalid_data = cast(Any, [1, 2, "three", 4, 5])
    expected_message = "data contains non-numeric values"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        robust_statistics(invalid_data)


def test_robust_statistics_dict_input() -> None:
    """Test case 17: TypeError for dictionary input."""
    # Arrange
    invalid_data = cast(Any, {"a": 1, "b": 2})
    expected_message = "data must be a list or numpy array"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        robust_statistics(invalid_data)


def test_robust_statistics_none_input() -> None:
    """Test case 18: TypeError for None input."""
    # Arrange
    invalid_data = cast(Any, None)
    expected_message = "data must be a list or numpy array"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        robust_statistics(invalid_data)


def test_robust_statistics_nested_list() -> None:
    """Test case 19: TypeError for nested list."""
    # Arrange
    invalid_data = cast(Any, [[1, 2], [3, 4]])
    expected_message = "only 0-dimensional arrays can be converted to Python scalars"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        robust_statistics(invalid_data)


def test_robust_statistics_inf_values() -> None:
    """Test case 20: Edge case with infinite values."""
    # Arrange
    data_with_inf = [1, 2, np.inf, 4, 5]

    # Act
    result = robust_statistics(data_with_inf)

    # Assert - function handles inf but some results may be nan/inf
    assert result["median"] == 4.0
    assert result["mad"] > 0


def test_robust_statistics_nan_warning_single() -> None:
    """Test case 21: NaN warning path with single NaN value."""
    # Arrange
    data_with_nan = [1, 2, np.nan, 4, 5]

    # Act & Assert - should warn about NaN removal
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = robust_statistics(data_with_nan)

        # Verify warning was raised
        assert len(w) == 1
        assert issubclass(w[0].category, UserWarning)
        assert "1 NaN value(s)" in str(w[0].message)

    # Result should be calculated on valid data only
    assert result["median"] == 3.0
    assert result["mad"] > 0


def test_robust_statistics_nan_warning_multiple() -> None:
    """Test case 22: NaN warning path with multiple NaN values."""
    # Arrange
    data_with_nans = [1, 2, np.nan, 4, np.nan, 5, np.nan]

    # Act & Assert - should warn about NaN removal
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = robust_statistics(data_with_nans)

        # Verify warning was raised with correct count
        assert len(w) == 1
        assert issubclass(w[0].category, UserWarning)
        assert "3 NaN value(s)" in str(w[0].message)

    # Result should be calculated on valid data only [1, 2, 4, 5]
    assert result["median"] == 3.0


def test_robust_statistics_all_nan_after_removal() -> None:
    """Test case 23: ValueError when only NaN values remain."""
    # Arrange
    data_all_nan = [np.nan, np.nan, np.nan]
    expected_message = "data contains only NaN values"

    # Act & Assert - should raise ValueError after removing all NaNs
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        with pytest.raises(ValueError, match=expected_message):
            robust_statistics(data_all_nan)


def test_robust_statistics_mixed_nan_and_values() -> None:
    """Test case 24: NaN warning with mixed valid and NaN values."""
    # Arrange
    data_mixed = [np.nan, 10, 20, np.nan, 30, 40, np.nan, 50]

    # Act
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = robust_statistics(data_mixed)

        # Verify warning
        assert len(w) == 1
        assert "3 NaN value(s)" in str(w[0].message)

    # Assert - calculated on [10, 20, 30, 40, 50]
    assert result["median"] == 30.0
    assert result["iqr"] == 20.0
