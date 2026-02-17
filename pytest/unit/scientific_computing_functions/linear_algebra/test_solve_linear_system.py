"""
Unit tests for solve_linear_system function.

Tests cover normal operation, edge cases, and error conditions.
"""

from typing import Any, cast

try:
    import numpy as np
    import scipy
    from pyutils_collection.scientific_computing_functions.linear_algebra.solve_linear_system import (
        solve_linear_system,
    )
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None  # type: ignore
    scipy = None
    solve_linear_system = None  # type: ignore

import pytest

pytestmark = [
    pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy and/or scipy not installed"),
    pytest.mark.unit,
    pytest.mark.scientific_computing,
]

# Normal operation tests


def test_solve_linear_system_basic() -> None:
    """Test case 1: Normal operation with basic system."""
    # Arrange
    A = [[2.0, 1.0], [1.0, 3.0]]
    b = [1.0, 2.0]

    # Act
    result = solve_linear_system(A, b)

    # Assert
    assert "solution" in result
    assert "residual_norm" in result
    assert "condition_number" in result
    assert "well_conditioned" in result
    assert result["residual_norm"] < 1e-10


def test_solve_linear_system_identity() -> None:
    """Test case 2: Normal operation with identity matrix."""
    # Arrange
    A = np.eye(3)
    b = [1.0, 2.0, 3.0]

    # Act
    result = solve_linear_system(A, b)

    # Assert
    assert np.allclose(result["solution"], [1, 2, 3])
    assert result["residual_norm"] < 1e-10


def test_solve_linear_system_3x3() -> None:
    """Test case 3: Normal operation with 3x3 system."""
    # Arrange
    A = [[3.0, 2.0, -1.0], [2.0, -2.0, 4.0], [-1.0, 0.5, -1.0]]
    b = [1.0, -2.0, 0.0]

    # Act
    result = solve_linear_system(A, b)

    # Assert
    assert len(cast(np.ndarray, result["solution"])) == 3
    assert result["residual_norm"] < 1e-8


def test_solve_linear_system_numpy_arrays() -> None:
    """Test case 4: Normal operation with numpy arrays."""
    # Arrange
    A = np.array([[4.0, 1.0], [1.0, 3.0]])
    b = np.array([1.0, 2.0])

    # Act
    result = solve_linear_system(A, b)

    # Assert
    assert isinstance(result["solution"], np.ndarray)
    assert result["residual_norm"] < 1e-10


def test_solve_linear_system_without_condition_check() -> None:
    """Test case 5: Normal operation without condition number check."""
    # Arrange
    A = [[2.0, 1.0], [1.0, 3.0]]
    b = [1.0, 2.0]

    # Act
    result = solve_linear_system(A, b, check_condition=False)

    # Assert
    assert "solution" in result
    assert "condition_number" not in result


def test_solve_linear_system_well_conditioned() -> None:
    """Test case 6: Normal operation with well-conditioned matrix."""
    # Arrange
    A = [[10.0, 1.0], [1.0, 10.0]]
    b = [1.0, 1.0]

    # Act
    result = solve_linear_system(A, b)

    # Assert
    assert result["well_conditioned"] is True
    assert result["condition_number"] < 100


# Edge case tests


def test_solve_linear_system_large_system() -> None:
    """Test case 7: Edge case with large system."""
    # Arrange
    n = 50
    A = np.random.randn(n, n)
    A = A + A.T  # Make symmetric for better conditioning
    b = np.random.randn(n)

    # Act
    result = solve_linear_system(A, b)

    # Assert
    assert len(cast(np.ndarray, result["solution"])) == n
    assert result["residual_norm"] < 1e-6


def test_solve_linear_system_diagonal_matrix() -> None:
    """Test case 8: Edge case with diagonal matrix."""
    # Arrange
    A = np.diag([2.0, 3.0, 4.0])
    b = [2.0, 6.0, 12.0]

    # Act
    result = solve_linear_system(A, b)

    # Assert
    assert np.allclose(result["solution"], [1, 2, 3])


def test_solve_linear_system_sparse_solution() -> None:
    """Test case 9: Edge case with sparse solution."""
    # Arrange
    A = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    b = [0.0, 0.0, 5.0]

    # Act
    result = solve_linear_system(A, b)

    # Assert
    assert np.allclose(result["solution"], [0, 0, 5])


def test_solve_linear_system_ill_conditioned() -> None:
    """Test case 10: Edge case with ill-conditioned matrix."""
    # Arrange
    A = [[1.0, 1.0], [1.0, 1.0001]]  # Nearly singular
    b = [2.0, 2.0]

    # Act
    result = solve_linear_system(A, b, condition_threshold=1e3)

    # Assert
    assert result["well_conditioned"] is False
    assert result["condition_number"] > 1e3


def test_solve_linear_system_negative_values() -> None:
    """Test case 11: Edge case with negative values."""
    # Arrange
    A = [[-2.0, 1.0], [1.0, -3.0]]
    b = [-1.0, -2.0]

    # Act
    result = solve_linear_system(A, b)

    # Assert
    assert len(cast(np.ndarray, result["solution"])) == 2
    assert result["residual_norm"] < 1e-10


def test_solve_linear_system_zero_rhs() -> None:
    """Test case 12: Edge case with zero right-hand side."""
    # Arrange
    A = [[2.0, 1.0], [1.0, 3.0]]
    b = [0.0, 0.0]

    # Act
    result = solve_linear_system(A, b)

    # Assert
    assert np.allclose(result["solution"], [0, 0])


def test_solve_linear_system_single_equation() -> None:
    """Test case 13: Edge case with 1x1 system."""
    # Arrange
    A = [[5.0]]
    b = [10.0]

    # Act
    result = solve_linear_system(A, b)

    # Assert
    assert np.allclose(result["solution"], [2.0])


# Error case tests


def test_solve_linear_system_invalid_A_type() -> None:
    """Test case 14: TypeError for invalid A type."""
    # Arrange
    invalid_A = cast(Any, "not_a_matrix")
    b = [1.0, 2.0]
    expected_message = "A must be a list or numpy array"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        solve_linear_system(invalid_A, b)


def test_solve_linear_system_invalid_b_type() -> None:
    """Test case 15: TypeError for invalid b type."""
    # Arrange
    A = [[1.0, 2.0], [3.0, 4.0]]
    invalid_b = cast(Any, "not_a_vector")
    expected_message = "b must be a list or numpy array"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        solve_linear_system(A, invalid_b)


def test_solve_linear_system_invalid_check_condition_type() -> None:
    """Test case 16: TypeError for invalid check_condition type."""
    # Arrange
    A = [[1.0, 2.0], [3.0, 4.0]]
    b = [1.0, 2.0]
    invalid_check = cast(Any, "true")
    expected_message = "check_condition must be a boolean"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        solve_linear_system(A, b, check_condition=invalid_check)


def test_solve_linear_system_invalid_threshold_type() -> None:
    """Test case 17: TypeError for invalid threshold type."""
    # Arrange
    A = [[1.0, 2.0], [3.0, 4.0]]
    b = [1.0, 2.0]
    invalid_threshold = cast(Any, "1e10")
    expected_message = "condition_threshold must be a number"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        solve_linear_system(A, b, condition_threshold=invalid_threshold)


def test_solve_linear_system_non_square_A() -> None:
    """Test case 18: ValueError for non-square matrix."""
    # Arrange
    A = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    b = [1.0, 2.0]
    expected_message = "A must be square"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        solve_linear_system(A, b)


def test_solve_linear_system_dimension_mismatch() -> None:
    """Test case 19: ValueError for dimension mismatch."""
    # Arrange
    A = [[1.0, 2.0], [3.0, 4.0]]
    b = [1.0, 2.0, 3.0]
    expected_message = "incompatible dimensions"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        solve_linear_system(A, b)


def test_solve_linear_system_singular_matrix() -> None:
    """Test case 20: ValueError for singular matrix."""
    # Arrange
    A = [[1.0, 2.0], [2.0, 4.0]]  # Singular
    b = [1.0, 2.0]

    # Act & Assert
    with pytest.raises((ValueError, np.linalg.LinAlgError)):
        solve_linear_system(A, b)


def test_solve_linear_system_empty_A() -> None:
    """Test case 21: ValueError for empty matrix."""
    # Arrange
    empty_A: list[list[float]] = []
    b: list[float] = []
    expected_message = "A must be 2-dimensional"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        solve_linear_system(empty_A, b)


def test_solve_linear_system_nan_in_A() -> None:
    """Test case 22: ValueError for NaN in A."""
    # Arrange
    A = [[1.0, 2.0], [np.nan, 4.0]]
    b = [1.0, 2.0]
    expected_message = "A contains NaN or Inf values"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        solve_linear_system(A, b)


def test_solve_linear_system_inf_in_A() -> None:
    """Test case 23: ValueError for inf in A."""
    # Arrange
    A = [[1.0, 2.0], [3.0, np.inf]]
    b = [1.0, 2.0]
    expected_message = "A contains NaN or Inf values"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        solve_linear_system(A, b)


def test_solve_linear_system_nan_in_b() -> None:
    """Test case 24: ValueError for NaN in b."""
    # Arrange
    A = [[1.0, 2.0], [3.0, 4.0]]
    b = [1.0, np.nan]
    expected_message = "b contains NaN or Inf values"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        solve_linear_system(A, b)


def test_solve_linear_system_negative_threshold() -> None:
    """Test case 25: Edge case with negative threshold (may not raise)."""
    # Arrange
    A = [[1.0, 2.0], [3.0, 4.0]]
    b = [1.0, 2.0]

    # Act - function may accept negative threshold or raise error
    try:
        result = solve_linear_system(A, b, condition_threshold=-1.0)
        # If it succeeds, verify solution exists
        assert "solution" in result
    except ValueError:
        # If it raises, that's also acceptable
        pass


def test_solve_linear_system_non_numeric_in_A() -> None:
    """Test case 26: ValueError for non-numeric values in A."""
    # Arrange
    invalid_A = cast(Any, [[1, "two"], [3, 4]])
    b = [1.0, 2.0]
    expected_message = "arrays contain non-numeric values"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        solve_linear_system(invalid_A, b)


def test_solve_linear_system_non_numeric_in_b() -> None:
    """Test case 27: ValueError for non-numeric values in b."""
    # Arrange
    A = [[1.0, 2.0], [3.0, 4.0]]
    invalid_b = cast(Any, [1, "two"])
    expected_message = "arrays contain non-numeric values"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        solve_linear_system(A, invalid_b)


def test_solve_linear_system_1d_A() -> None:
    """Test case 28: ValueError for 1D array as A."""
    # Arrange
    invalid_A = cast(Any, [1, 2, 3, 4])
    b = [1.0, 2.0]
    expected_message = "A must be 2-dimensional"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        solve_linear_system(invalid_A, b)


def test_solve_linear_system_condition_check_singular_matrix() -> None:
    """Test case 29: Test condition check handles singular matrix (LinAlgError path)."""
    # Arrange - Create a nearly singular matrix that may cause LinAlgError during condition number computation
    A = [[1e-10, 0.0], [0.0, 1e-10]]
    b = [1.0, 1.0]

    # Act - This should handle the LinAlgError gracefully and set well_conditioned=False
    try:
        result = solve_linear_system(A, b, check_condition=True)
        # If it succeeds, verify result structure
        assert "solution" in result
        assert "well_conditioned" in result
    except ValueError:
        # Singular matrix may also raise ValueError during solve
        pass


def test_solve_linear_system_invalid_b_dimension() -> None:
    """Test case 30: ValueError for b with wrong dimensions."""
    # Arrange
    A = [[1.0, 2.0], [3.0, 4.0]]
    invalid_b = cast(Any, [[1], [2]])  # 2D array instead of 1D
    expected_message = "b must be 1-dimensional"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        solve_linear_system(A, invalid_b)
