"""
Unit tests for normalize_data function.
"""

import pytest

# Try to import numpy - tests will be skipped if not available
try:
    import numpy as np

    from pyutils_collection.data_visualization_functions.data_transformers import normalize_data

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None  # type: ignore
    normalize_data = None  # type: ignore

pytestmark = [
    pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy not installed"),
    pytest.mark.unit,
    pytest.mark.data_visualization,
]


def test_normalize_data_minmax_default() -> None:

    """
    Test case 1: Normalize data using minmax with default range [0, 1].
    """
    # Arrange
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    expected = np.array([0.0, 0.25, 0.5, 0.75, 1.0])

    # Act
    result = normalize_data(data, method="minmax")

    # Assert
    np.testing.assert_array_almost_equal(result, expected)


def test_normalize_data_minmax_custom_range() -> None:

    """
    Test case 2: Normalize data using minmax with custom range.
    """
    # Arrange
    data = [0.0, 5.0, 10.0]
    expected = np.array([-1.0, 0.0, 1.0])

    # Act
    result = normalize_data(data, method="minmax", feature_range=(-1.0, 1.0))

    # Assert
    np.testing.assert_array_almost_equal(result, expected)


def test_normalize_data_zscore() -> None:

    """
    Test case 3: Normalize data using z-score standardization.
    """
    # Arrange
    data = [1.0, 2.0, 3.0, 4.0, 5.0]

    # Act
    result = normalize_data(data, method="zscore")

    # Assert
    assert np.abs(np.mean(result)) < 1e-10  # Mean should be ~0
    assert np.abs(np.std(result) - 1.0) < 1e-10  # Std should be ~1


def test_normalize_data_robust() -> None:

    """
    Test case 4: Normalize data using robust scaling.
    """
    # Arrange
    data = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]

    # Act
    result = normalize_data(data, method="robust")

    # Assert
    assert result is not None
    assert len(result) == len(data)


def test_normalize_data_numpy_array() -> None:

    """
    Test case 5: Normalize numpy array input.
    """
    # Arrange
    data = np.array([10, 20, 30, 40, 50])

    # Act
    result = normalize_data(data, method="minmax")

    # Assert
    assert isinstance(result, np.ndarray)
    assert result[0] == 0.0
    assert result[-1] == 1.0


def test_normalize_data_empty_raises_error() -> None:

    """
    Test case 6: ValueError for empty data.
    """
    # Arrange
    data: list[float] = []
    expected_message = "data cannot be empty"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        normalize_data(data)


def test_normalize_data_constant_minmax_raises_error() -> None:

    """
    Test case 7: ValueError for constant data with minmax.
    """
    # Arrange
    data = [5.0, 5.0, 5.0, 5.0]
    expected_message = "Cannot normalize constant data with minmax method"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        normalize_data(data, method="minmax")


def test_normalize_data_invalid_method_raises_error() -> None:

    """
    Test case 8: ValueError for invalid normalization method.
    """
    # Arrange
    data = [1.0, 2.0, 3.0]
    expected_message = "method must be one of"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        normalize_data(data, method="invalid")


def test_normalize_data_invalid_type_raises_error() -> None:

    """
    Test case 9: TypeError for invalid data type.
    """
    # Arrange
    from typing import cast, Any
    data = cast(Any, "invalid")
    expected_message = "Cannot convert data to numeric array"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        normalize_data(data)
