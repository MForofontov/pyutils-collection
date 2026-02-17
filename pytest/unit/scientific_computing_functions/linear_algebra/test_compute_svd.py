"""
Unit tests for compute_svd function.

Tests cover normal operation, edge cases, and error conditions.
"""

from typing import Any, cast

try:
    import numpy as np
    import scipy
    from pyutils_collection.scientific_computing_functions.linear_algebra.compute_svd import compute_svd
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None  # type: ignore
    compute_svd = None  # type: ignore

import pytest

pytestmark = [
    pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy and/or scipy not installed"),
    pytest.mark.unit,
    pytest.mark.scientific_computing,
]

# Normal operation tests


def test_compute_svd_basic_matrix() -> None:
    """Test case 1: Normal operation with basic matrix."""
    # Arrange
    matrix: list[list[float]] = [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]

    # Act
    result = compute_svd(matrix)

    # Assert
    assert "U" in result
    assert "singular_values" in result
    assert "Vt" in result
    assert len(cast(np.ndarray, result["singular_values"])) == 2


def test_compute_svd_square_matrix() -> None:
    """Test case 2: Normal operation with square matrix."""
    # Arrange
    matrix: list[list[float]] = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]

    # Act
    result = compute_svd(matrix)

    # Assert
    assert cast(np.ndarray, result["U"]).shape == (3, 3)
    assert len(cast(np.ndarray, result["singular_values"])) == 3
    assert cast(np.ndarray, result["Vt"]).shape == (3, 3)


def test_compute_svd_reduced_matrices() -> None:
    """Test case 3: Normal operation with reduced matrices."""
    # Arrange
    matrix: list[list[float]] = [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]

    # Act
    result = compute_svd(matrix, full_matrices=False)

    # Assert
    assert cast(np.ndarray, result["U"]).shape == (3, 2)
    assert cast(np.ndarray, result["Vt"]).shape == (2, 2)


def test_compute_svd_numpy_array() -> None:
    """Test case 4: Normal operation with numpy array."""
    # Arrange
    matrix = np.array([[1.0, 2.0], [3.0, 4.0]])

    # Act
    result = compute_svd(matrix)

    # Assert
    assert isinstance(result["U"], np.ndarray)
    assert isinstance(result["singular_values"], np.ndarray)
    assert isinstance(result["Vt"], np.ndarray)


def test_compute_svd_low_rank_approximation() -> None:
    """Test case 5: Normal operation with low-rank approximation."""
    # Arrange
    matrix: list[list[float]] = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]

    # Act
    result = compute_svd(matrix, low_rank_k=2)

    # Assert
    assert "approximation" in result
    assert "approximation_error" in result
    assert cast(np.ndarray, result["approximation"]).shape == (3, 3)


def test_compute_svd_singular_values_only() -> None:
    """Test case 6: Normal operation computing only singular values."""
    # Arrange
    matrix: list[list[float]] = [[1.0, 2.0], [3.0, 4.0]]

    # Act
    result = compute_svd(matrix, compute_uv=False)

    # Assert
    assert "singular_values" in result
    assert "U" not in result
    assert "Vt" not in result


# Edge case tests


def test_compute_svd_identity_matrix() -> None:
    """Test case 7: Edge case with identity matrix."""
    # Arrange
    matrix = np.eye(3)

    # Act
    result = compute_svd(matrix)

    # Assert
    assert np.allclose(result["singular_values"], [1.0, 1.0, 1.0])


def test_compute_svd_rank_deficient() -> None:
    """Test case 8: Edge case with rank-deficient matrix."""
    # Arrange
    matrix: list[list[float]] = [[1.0, 2.0], [2.0, 4.0]]  # Rank 1

    # Act
    result = compute_svd(matrix)

    # Assert
    assert len(cast(np.ndarray, result["singular_values"])) == 2
    assert cast(np.ndarray, result["singular_values"])[1] < 1e-10  # Near zero


def test_compute_svd_tall_matrix() -> None:
    """Test case 9: Edge case with tall matrix (m >> n)."""
    # Arrange
    matrix = np.random.randn(100, 5)

    # Act
    result = compute_svd(matrix, full_matrices=False)

    # Assert
    assert cast(np.ndarray, result["U"]).shape == (100, 5)
    assert len(cast(np.ndarray, result["singular_values"])) == 5


def test_compute_svd_wide_matrix() -> None:
    """Test case 10: Edge case with wide matrix (n >> m)."""
    # Arrange
    matrix = np.random.randn(5, 100)

    # Act
    result = compute_svd(matrix, full_matrices=False)

    # Assert
    assert cast(np.ndarray, result["U"]).shape == (5, 5)
    assert len(cast(np.ndarray, result["singular_values"])) == 5


def test_compute_svd_single_column() -> None:
    """Test case 11: Edge case with single column matrix."""
    # Arrange
    matrix: list[list[float]] = [[1.0], [2.0], [3.0]]

    # Act
    result = compute_svd(matrix)

    # Assert
    assert len(cast(np.ndarray, result["singular_values"])) == 1
    assert cast(np.ndarray, result["singular_values"])[0] > 0


def test_compute_svd_single_row() -> None:
    """Test case 12: Edge case with single row matrix."""
    # Arrange
    matrix: list[list[float]] = [[1.0, 2.0, 3.0]]

    # Act
    result = compute_svd(matrix)

    # Assert
    assert len(cast(np.ndarray, result["singular_values"])) == 1


def test_compute_svd_low_rank_k_equals_1() -> None:
    """Test case 13: Edge case with rank-1 approximation."""
    # Arrange
    matrix: list[list[float]] = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]

    # Act
    result = compute_svd(matrix, low_rank_k=1)

    # Assert
    assert "approximation" in result
    assert cast(float, result["approximation_error"]) >= 0


# Error case tests


def test_compute_svd_invalid_matrix_type() -> None:
    """Test case 14: TypeError for invalid matrix type."""
    # Arrange
    invalid_matrix = "not_a_matrix"
    expected_message = "matrix must be a list or numpy array"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        compute_svd(cast(Any, invalid_matrix))


def test_compute_svd_invalid_full_matrices_type() -> None:
    """Test case 15: TypeError for invalid full_matrices type."""
    # Arrange
    matrix: list[list[float]] = [[1.0, 2.0], [3.0, 4.0]]
    invalid_full_matrices = "true"
    expected_message = "full_matrices must be a boolean"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        compute_svd(matrix, full_matrices=cast(Any, invalid_full_matrices))


def test_compute_svd_invalid_compute_uv_type() -> None:
    """Test case 16: TypeError for invalid compute_uv type."""
    # Arrange
    matrix: list[list[float]] = [[1.0, 2.0], [3.0, 4.0]]
    invalid_compute_uv = 1
    expected_message = "compute_uv must be a boolean"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        compute_svd(matrix, compute_uv=cast(Any, invalid_compute_uv))


def test_compute_svd_invalid_low_rank_k_type() -> None:
    """Test case 17: TypeError for invalid low_rank_k type."""
    # Arrange
    matrix: list[list[float]] = [[1.0, 2.0], [3.0, 4.0]]
    invalid_k = 1.5
    expected_message = "low_rank_k must be an integer"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        compute_svd(matrix, low_rank_k=cast(Any, invalid_k))


def test_compute_svd_empty_matrix() -> None:
    """Test case 18: ValueError for empty matrix."""
    # Arrange
    empty_matrix: list[Any] = []
    expected_message = "matrix must be 2-dimensional"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        compute_svd(cast(Any, empty_matrix))


def test_compute_svd_non_numeric_values() -> None:
    """Test case 19: ValueError for non-numeric values."""
    # Arrange
    invalid_matrix = [[1, 2], ["a", "b"]]
    expected_message = "matrix contains non-numeric values"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        compute_svd(cast(Any, invalid_matrix))


def test_compute_svd_nan_values() -> None:
    """Test case 20: ValueError for NaN values."""
    # Arrange
    invalid_matrix = [[1, 2], [3, np.nan]]
    expected_message = "matrix contains NaN or Inf values"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        compute_svd(cast(Any, invalid_matrix))


def test_compute_svd_inf_values() -> None:
    """Test case 21: ValueError for infinite values."""
    # Arrange
    invalid_matrix = [[1, 2], [3, np.inf]]
    expected_message = "matrix contains NaN or Inf values"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        compute_svd(cast(Any, invalid_matrix))


def test_compute_svd_low_rank_k_negative() -> None:
    """Test case 22: ValueError for negative k."""
    # Arrange
    matrix: list[list[float]] = [[1.0, 2.0], [3.0, 4.0]]
    invalid_k = -1
    expected_message = "low_rank_k must be"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        compute_svd(matrix, low_rank_k=invalid_k)


def test_compute_svd_low_rank_k_too_large() -> None:
    """Test case 23: ValueError for k larger than rank."""
    # Arrange
    matrix: list[list[float]] = [[1.0, 2.0], [3.0, 4.0]]
    invalid_k = 10
    expected_message = "low_rank_k must be"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        compute_svd(matrix, low_rank_k=invalid_k)


def test_compute_svd_1d_array() -> None:
    """Test case 24: ValueError for 1D array."""
    # Arrange
    invalid_matrix = [1, 2, 3, 4]
    expected_message = "matrix must be 2-dimensional"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        compute_svd(cast(Any, invalid_matrix))


def test_compute_svd_jagged_array() -> None:
    """Test case 25: ValueError for jagged array."""
    # Arrange
    invalid_matrix = [[1, 2], [3, 4, 5]]
    expected_message = "matrix contains non-numeric values|setting an arr"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        compute_svd(cast(Any, invalid_matrix))


def test_compute_svd_low_rank_k_ignored_without_compute_uv() -> None:
    """Test case 26: low_rank_k is ignored when compute_uv=False."""
    # Arrange
    matrix: list[list[float]] = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]

    # Act - low_rank_k is silently ignored, no error raised
    result = compute_svd(matrix, low_rank_k=2, compute_uv=False)

    # Assert - should return only singular values, no approximation
    assert "singular_values" in result
    assert "approximation" not in result
    assert "U" not in result
    assert "Vt" not in result


def test_compute_svd_singular_values_conversion() -> None:
    """Test case 27: Verify singular values are float array when compute_uv=False."""
    # Arrange
    matrix = np.array([[3, 1], [1, 3]], dtype=np.float64)

    # Act
    result = compute_svd(matrix, compute_uv=False)

    # Assert
    assert "singular_values" in result
    assert isinstance(result["singular_values"], np.ndarray)
    singular_values = result["singular_values"]
    assert singular_values.dtype in [np.float32, np.float64]
    assert len(singular_values) == 2
