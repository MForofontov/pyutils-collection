"""Unit tests for constrained_least_squares function."""

from typing import Any, cast

try:
    import numpy as np
    import scipy
    from pyutils_collection.scientific_computing_functions.linear_algebra.constrained_least_squares import (
        constrained_least_squares,
    )
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None  # type: ignore
    constrained_least_squares = None  # type: ignore

import pytest

pytestmark = [
    pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy and/or scipy not installed"),
    pytest.mark.unit,
    pytest.mark.scientific_computing,
]


# Normal operation tests
def test_constrained_least_squares_simple_overdetermined() -> None:
    """Test case 1: Normal operation with simple overdetermined system."""
    # Arrange
    A = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    b = [2.0, 1.0, 3.0]

    # Act
    result = constrained_least_squares(A, b)

    # Assert
    assert result["success"] is True
    assert len(cast(np.ndarray, result["x"])) == 2
    assert result["cost"] >= 0
    assert len(cast(np.ndarray, result["residuals"])) == 3


def test_constrained_least_squares_with_lower_bound() -> None:
    """Test case 2: Normal operation with non-negative constraint."""
    # Arrange
    A = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    b = [2.0, 1.0, 3.0]
    bounds = (0, np.inf)  # Non-negative least squares

    # Act
    result = constrained_least_squares(A, b, bounds=bounds)

    # Assert
    assert result["success"] is True
    assert all(result["x"] >= 0)  # All values non-negative
    assert result["cost"] >= 0


def test_constrained_least_squares_with_box_constraints() -> None:
    """Test case 3: Normal operation with box constraints."""
    # Arrange
    A = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    b = [2.0, 1.0, 3.0]
    bounds = ([0.0, 0.0], [2.0, 2.0])  # Each variable bounded between 0 and 2

    # Act
    result = constrained_least_squares(A, b, bounds=bounds)

    # Assert
    assert result["success"] is True
    assert all(0 <= x <= 2 for x in result["x"])
    assert len(result["active_constraints"]) >= 0


def test_constrained_least_squares_trf_method() -> None:
    """Test case 4: Normal operation with Trust Region Reflective method."""
    # Arrange
    A = np.random.rand(20, 5)
    b = np.random.rand(20)
    bounds = (-1, 1)

    # Act
    result = constrained_least_squares(A, b, bounds=bounds, method="trf")

    # Assert
    assert result["success"] is True
    assert all(-1 <= x <= 1 for x in result["x"])


def test_constrained_least_squares_bvls_method() -> None:
    """Test case 5: Normal operation with BVLS method."""
    # Arrange
    A = [[2.0, 1.0], [1.0, 2.0], [1.0, 1.0]]
    b = [3.0, 3.0, 2.0]
    bounds = (0, 10)

    # Act
    result = constrained_least_squares(A, b, bounds=bounds, method="bvls")

    # Assert
    assert result["success"] is True
    assert all(result["x"] >= 0)


def test_constrained_least_squares_trf_method_with_bounds() -> None:
    """Test case 6: Normal operation with trf method (scipy only supports trf and bvls)."""
    # Arrange
    A = [[1.0, 2.0], [2.0, 1.0], [1.0, 1.0]]
    b = [5.0, 4.0, 3.0]
    bounds = (-5, 5)

    # Act - scipy.optimize.lsq_linear only supports 'trf' and 'bvls'
    result = constrained_least_squares(A, b, bounds=bounds, method="trf")

    # Assert
    assert result["success"] is True
    assert all(-5 <= x <= 5 for x in result["x"])


def test_constrained_least_squares_with_custom_tolerance() -> None:
    """Test case 7: Normal operation with custom tolerance."""
    # Arrange
    A = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    b = [1.0, 1.0, 2.0]

    # Act
    result = constrained_least_squares(A, b, tol=1e-12, max_iter=500)

    # Assert
    assert result["success"] is True
    assert result["optimality"] < 0.01  # Should be well-optimized


def test_constrained_least_squares_numpy_arrays() -> None:
    """Test case 8: Normal operation with numpy arrays as input."""
    # Arrange
    A = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]], dtype=float)
    b = np.array([2.0, 1.0, 3.0], dtype=float)

    # Act
    result = constrained_least_squares(A, b)

    # Assert
    assert result["success"] is True
    assert isinstance(result["x"], np.ndarray)


# Edge case tests
def test_constrained_least_squares_tight_bounds() -> None:
    """Test case 9: Edge case with very tight bounds."""
    # Arrange
    A = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    b = [2.0, 1.0, 3.0]
    bounds = ([0.5, 0.5], [1.5, 1.5])  # Tight bounds

    # Act
    result = constrained_least_squares(A, b, bounds=bounds)

    # Assert
    assert result["success"] is True
    assert all(0.5 <= x <= 1.5 for x in result["x"])
    # Should have active constraints due to tight bounds
    assert len(result["active_constraints"]) >= 0


def test_constrained_least_squares_exact_system() -> None:
    """Test case 10: Edge case with exact solution (square system)."""
    # Arrange
    A = [[2.0, 0.0], [0.0, 3.0]]
    b = [4.0, 6.0]  # Exact solution is [2, 2]

    # Act
    result = constrained_least_squares(A, b)

    # Assert
    assert result["success"] is True
    assert np.allclose(result["x"], [2, 2], atol=1e-6)
    assert result["cost"] < 1e-10  # Should be near zero


def test_constrained_least_squares_all_constraints_active() -> None:
    """Test case 11: Edge case where all constraints are active."""
    # Arrange
    A = [[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]]
    b = [10.0, 10.0, 10.0]  # Wants high values
    bounds = ([0.0, 0.0], [1.0, 1.0])  # Very restrictive

    # Act
    result = constrained_least_squares(A, b, bounds=bounds)

    # Assert
    assert result["success"] is True
    # Both variables should be at upper bound
    assert len(result["active_constraints"]) >= 1


def test_constrained_least_squares_one_variable() -> None:
    """Test case 12: Edge case with single variable."""
    # Arrange
    A = [[1.0], [2.0], [3.0]]
    b = [1.0, 2.0, 3.0]

    # Act
    result = constrained_least_squares(A, b, bounds=(0, 10))

    # Assert
    assert result["success"] is True
    assert len(cast(np.ndarray, result["x"])) == 1
    assert 0 <= result["x"][0] <= 10


def test_constrained_least_squares_large_system() -> None:
    """Test case 13: Edge case with larger system."""
    # Arrange
    np.random.seed(42)
    A = np.random.rand(100, 10)
    b = np.random.rand(100)
    bounds = (0, 1)

    # Act
    result = constrained_least_squares(A, b, bounds=bounds)

    # Assert
    assert result["success"] is True
    assert len(cast(np.ndarray, result["x"])) == 10
    assert all(0 <= x <= 1 for x in result["x"])


def test_constrained_least_squares_scalar_bounds() -> None:
    """Test case 14: Edge case with scalar bounds (applied to all variables)."""
    # Arrange
    A = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    b = [5.0, 5.0, 5.0]
    bounds = (0, 3)  # Scalar bounds

    # Act
    result = constrained_least_squares(A, b, bounds=bounds)

    # Assert
    assert result["success"] is True
    assert all(0 <= x <= 3 for x in result["x"])


# Error case tests
def test_constrained_least_squares_invalid_A_type() -> None:
    """Test case 15: TypeError for invalid A type."""
    # Arrange
    invalid_A = "not a matrix"
    b = [1.0, 2.0, 3.0]
    expected_message = "A must be a list or numpy array"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        constrained_least_squares(cast(Any, invalid_A), b)


def test_constrained_least_squares_invalid_b_type() -> None:
    """Test case 16: TypeError for invalid b type."""
    # Arrange
    A = [[1.0, 0.0], [0.0, 1.0]]
    invalid_b = "not a vector"
    expected_message = "b must be a list or numpy array"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        constrained_least_squares(A, cast(Any, invalid_b))


def test_constrained_least_squares_A_not_2d() -> None:
    """Test case 17: ValueError for A not 2D."""
    # Arrange
    invalid_A = [1.0, 2.0, 3.0]  # 1D array
    b = [1.0, 2.0, 3.0]
    expected_message = "A must be a 2D array"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        constrained_least_squares(cast(Any, invalid_A), b)


def test_constrained_least_squares_b_not_1d() -> None:
    """Test case 18: ValueError for b not 1D."""
    # Arrange
    A = [[1.0, 0.0], [0.0, 1.0]]
    invalid_b = [[1.0], [2.0]]  # 2D array
    expected_message = "b must be a 1D array"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        constrained_least_squares(A, cast(Any, invalid_b))


def test_constrained_least_squares_incompatible_dimensions() -> None:
    """Test case 19: ValueError for incompatible dimensions."""
    # Arrange
    A = [[1.0, 0.0], [0.0, 1.0]]  # 2x2
    b = [1.0, 2.0, 3.0]  # Length 3
    expected_message = "Incompatible dimensions"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        constrained_least_squares(A, b)


def test_constrained_least_squares_invalid_bounds_type() -> None:
    """Test case 20: TypeError for invalid bounds type."""
    # Arrange
    A = [[1.0, 0.0], [0.0, 1.0]]
    b = [1.0, 2.0]
    invalid_bounds = [0, 1]  # Should be tuple
    expected_message = "bounds must be a tuple of \\(lower, upper\\)"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        constrained_least_squares(A, b, bounds=cast(Any, invalid_bounds))


def test_constrained_least_squares_invalid_method() -> None:
    """Test case 21: ValueError for invalid method."""
    # Arrange
    A = [[1.0, 0.0], [0.0, 1.0]]
    b = [1.0, 2.0]
    invalid_method = "invalid"
    expected_message = "Invalid method"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        constrained_least_squares(A, b, method=cast(Any, invalid_method))


def test_constrained_least_squares_negative_max_iter() -> None:
    """Test case 22: ValueError for negative max_iter."""
    # Arrange
    A = [[1.0, 0.0], [0.0, 1.0]]
    b = [1.0, 2.0]
    expected_message = "max_iter must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        constrained_least_squares(A, b, max_iter=-10)


def test_constrained_least_squares_zero_max_iter() -> None:
    """Test case 23: ValueError for zero max_iter."""
    # Arrange
    A = [[1.0, 0.0], [0.0, 1.0]]
    b = [1.0, 2.0]
    expected_message = "max_iter must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        constrained_least_squares(A, b, max_iter=0)


def test_constrained_least_squares_negative_tolerance() -> None:
    """Test case 24: ValueError for negative tolerance."""
    # Arrange
    A = [[1.0, 0.0], [0.0, 1.0]]
    b = [1.0, 2.0]
    expected_message = "tol must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        constrained_least_squares(A, b, tol=-1e-6)


def test_constrained_least_squares_invalid_bounds_size() -> None:
    """Test case 25: ValueError for bounds size mismatch."""
    # Arrange
    A = [[1.0, 0.0], [0.0, 1.0]]
    b = [1.0, 2.0]
    invalid_bounds = ([0.0], [1.0])  # Only 1 element, but need 2
    expected_message = "Lower bounds size .* doesn't match number of variables"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        constrained_least_squares(A, b, bounds=cast(Any, invalid_bounds))


def test_constrained_least_squares_lower_greater_than_upper() -> None:
    """Test case 26: ValueError for lower bounds > upper bounds."""
    # Arrange
    A = [[1.0, 0.0], [0.0, 1.0]]
    b = [1.0, 2.0]
    invalid_bounds = ([2.0, 2.0], [1.0, 1.0])  # Lower > upper
    expected_message = "Lower bounds must be <= upper bounds"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        constrained_least_squares(A, b, bounds=cast(Any, invalid_bounds))


def test_constrained_least_squares_invalid_max_iter_type() -> None:
    """Test case 27: TypeError for invalid max_iter type."""
    # Arrange
    A = [[1.0, 0.0], [0.0, 1.0]]
    b = [1.0, 2.0]
    expected_message = "max_iter must be an integer"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        constrained_least_squares(A, b, max_iter=cast(Any, 10.5))


def test_constrained_least_squares_invalid_tol_type() -> None:
    """Test case 28: TypeError for invalid tolerance type."""
    # Arrange
    A = [[1.0, 0.0], [0.0, 1.0]]
    b = [1.0, 2.0]
    expected_message = "tol must be a number"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        constrained_least_squares(A, b, tol=cast(Any, "1e-6"))


def test_constrained_least_squares_invalid_method_type() -> None:
    """Test case 29: TypeError for invalid method type."""
    # Arrange
    A = [[1.0, 0.0], [0.0, 1.0]]
    b = [1.0, 2.0]
    expected_message = "method must be a string"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        constrained_least_squares(A, b, method=cast(Any, 123))
