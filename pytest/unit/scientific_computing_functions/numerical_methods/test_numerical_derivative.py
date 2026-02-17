"""
Unit tests for numerical_derivative function.

Tests cover:
- Normal cases: various methods, orders, and functions
- Edge cases: small datasets, non-uniform spacing
- Error cases: invalid types, dimensions, lengths
"""
from typing import Any, cast
try:
    import numpy as np
    import scipy
    from pyutils_collection.scientific_computing_functions.numerical_methods.numerical_derivative import (
        numerical_derivative,
    )
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None  # type: ignore
    scipy = None
    numerical_derivative = None  # type: ignore

import pytest

pytestmark = [
    pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy/scipy not installed"),
    pytest.mark.unit,
    pytest.mark.scientific_computing,
]

# ========== Normal Operation Tests ==========


def test_numerical_derivative_linear_function() -> None:
    """Test case 1: First derivative of linear function."""
    # Arrange
    x: list[float] = [0, 1, 2, 3, 4]
    y: list[float] = [0, 2, 4, 6, 8]  # y = 2x, dy/dx = 2

    # Act
    result = numerical_derivative(x, y, method="central")

    # Assert
    assert "derivative" in result
    assert "x" in result
    assert "method" in result
    assert "order" in result
    assert len(result["derivative"]) == len(x)
    assert np.allclose(result["derivative"], 2.0, atol=0.1)


def test_numerical_derivative_quadratic_function() -> None:
    """Test case 2: First derivative of quadratic function."""
    # Arrange
    x = np.linspace(0, 4, 10)
    y = x**2  # y = x^2, dy/dx = 2x
    expected = 2 * x

    # Act
    result = numerical_derivative(x, y, method="central")

    # Assert
    assert len(result["derivative"]) == len(x)
    # Check interior points (boundary points use forward/backward difference)
    assert np.allclose(result["derivative"][1:-1], expected[1:-1], atol=0.1)


def test_numerical_derivative_sine_function() -> None:
    """Test case 3: First derivative of sine function."""
    # Arrange
    x = np.linspace(0, 2 * np.pi, 50)
    y = np.sin(x)  # y = sin(x), dy/dx = cos(x)
    expected = np.cos(x)

    # Act
    result = numerical_derivative(x, y, method="central")

    # Assert
    assert len(result["derivative"]) == len(x)
    assert np.allclose(result["derivative"], expected, atol=0.1)


def test_numerical_derivative_exponential_function() -> None:
    """Test case 4: First derivative of exponential function."""
    # Arrange
    x = np.linspace(0, 2, 20)
    y = np.exp(x)  # y = e^x, dy/dx = e^x
    expected = np.exp(x)

    # Act
    result = numerical_derivative(x, y, method="gradient")

    # Assert
    assert len(result["derivative"]) == len(x)
    assert np.allclose(result["derivative"], expected, rtol=0.1)


def test_numerical_derivative_gradient_method() -> None:
    """Test case 5: NumPy gradient method."""
    # Arrange
    x: list[float] = [0, 1, 2, 3, 4]
    y: list[float] = [0, 1, 4, 9, 16]  # y = x^2

    # Act
    result = numerical_derivative(x, y, method="gradient")

    # Assert
    assert result["method"] == "gradient"
    assert len(result["derivative"]) == len(x)
    assert np.all(np.isfinite(result["derivative"]))


def test_numerical_derivative_forward_method() -> None:
    """Test case 6: Forward difference method."""
    # Arrange
    x: list[float] = [0, 1, 2, 3, 4]
    y: list[float] = [0, 1, 4, 9, 16]  # y = x^2

    # Act
    result = numerical_derivative(x, y, method="forward")

    # Assert
    assert result["method"] == "forward"
    assert len(result["derivative"]) == len(x)
    assert np.all(np.isfinite(result["derivative"]))


def test_numerical_derivative_backward_method() -> None:
    """Test case 7: Backward difference method."""
    # Arrange
    x: list[float] = [0, 1, 2, 3, 4]
    y: list[float] = [0, 1, 4, 9, 16]  # y = x^2

    # Act
    result = numerical_derivative(x, y, method="backward")

    # Assert
    assert result["method"] == "backward"
    assert len(result["derivative"]) == len(x)
    assert np.all(np.isfinite(result["derivative"]))


def test_numerical_derivative_central_method() -> None:
    """Test case 8: Central difference method (default)."""
    # Arrange
    x: list[float] = [0, 1, 2, 3, 4]
    y: list[float] = [0, 1, 4, 9, 16]  # y = x^2

    # Act
    result = numerical_derivative(x, y, method="central")

    # Assert
    assert result["method"] == "central"
    assert result["order"] == 1
    assert len(result["derivative"]) == len(x)
    assert np.all(np.isfinite(result["derivative"]))


def test_numerical_derivative_second_order() -> None:
    """Test case 9: Second derivative."""
    # Arrange
    x: list[float] = [0, 1, 2, 3, 4]
    y: list[float] = [0, 1, 4, 9, 16]  # y = x^2, d²y/dx² = 2

    # Act
    result = numerical_derivative(x, y, method="central", order=2)

    # Assert
    assert result["order"] == 2
    assert len(result["derivative"]) == len(x)
    assert np.allclose(result["derivative"], 2.0, atol=0.5)


def test_numerical_derivative_numpy_array_input() -> None:
    """Test case 10: NumPy array input."""
    # Arrange
    x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    y = np.array([0.0, 2.0, 4.0, 6.0, 8.0])

    # Act
    result = numerical_derivative(x, y)

    # Assert
    assert len(result["derivative"]) == len(x)
    assert isinstance(result["derivative"], np.ndarray)
    assert isinstance(result["x"], np.ndarray)


# ========== Edge Case Tests ==========


def test_numerical_derivative_minimum_points_first_order() -> None:
    """Test case 11: Minimum points for first derivative (2 points)."""
    # Arrange
    x = [0.0, 1.0]
    y = [0.0, 2.0]  # dy/dx = 2

    # Act
    result = numerical_derivative(x, y)

    # Assert
    assert len(result["derivative"]) == 2
    assert np.allclose(result["derivative"], 2.0, atol=0.1)


def test_numerical_derivative_minimum_points_second_order() -> None:
    """Test case 12: Minimum points for second derivative (3 points)."""
    # Arrange
    x: list[float] = [0, 1, 2]
    y: list[float] = [0, 1, 4]  # y = x^2, d²y/dx² = 2

    # Act
    result = numerical_derivative(x, y, order=2)

    # Assert
    assert len(result["derivative"]) == 3
    assert np.all(np.isfinite(result["derivative"]))


def test_numerical_derivative_non_uniform_spacing() -> None:
    """Test case 13: Non-uniform x spacing."""
    # Arrange
    x = [0, 0.5, 1.5, 3.0, 5.0]
    y = [0, 1, 4.5, 9.0, 15.0]  # Approximately y = 2x

    # Act
    result = numerical_derivative(x, y, method="central")

    # Assert
    assert len(result["derivative"]) == len(x)
    assert np.all(np.isfinite(result["derivative"]))
    # Should approximate dy/dx ≈ 2
    assert np.allclose(np.mean(result["derivative"]), 2.0, atol=1.0)


def test_numerical_derivative_constant_function() -> None:
    """Test case 14: Derivative of constant function (should be 0)."""
    # Arrange
    x: list[float] = [0, 1, 2, 3, 4]
    y: list[float] = [5, 5, 5, 5, 5]  # constant

    # Act
    result = numerical_derivative(x, y)

    # Assert
    assert len(result["derivative"]) == len(x)
    assert np.allclose(result["derivative"], 0.0, atol=1e-10)


def test_numerical_derivative_negative_values() -> None:
    """Test case 15: Negative x and y values."""
    # Arrange
    x = [-4.0, -3.0, -2.0, -1.0, 0.0]
    y = [16.0, 9.0, 4.0, 1.0, 0.0]  # y = x^2
    expected = 2 * np.array(x)

    # Act
    result = numerical_derivative(x, y, method="central")

    # Assert
    assert len(result["derivative"]) == len(x)
    # Check interior points (boundary points less accurate)
    assert np.allclose(result["derivative"][1:-1], expected[1:-1], atol=0.5)


def test_numerical_derivative_large_dataset() -> None:
    """Test case 16: Performance with large dataset."""
    # Arrange
    x = np.linspace(0, 10, 10000)
    y = np.sin(x)

    # Act
    result = numerical_derivative(x, y, method="gradient")

    # Assert
    assert len(result["derivative"]) == len(x)
    assert np.all(np.isfinite(result["derivative"]))


# ========== Error Case Tests ==========


def test_numerical_derivative_invalid_x_type() -> None:
    """Test case 17: TypeError for invalid x type."""
    # Arrange
    invalid_x = "not a list"
    y: list[float] = [0, 1, 2]
    expected_message = "x must be a list or numpy array"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        numerical_derivative(cast(Any, invalid_x), y)


def test_numerical_derivative_invalid_y_type() -> None:
    """Test case 18: TypeError for invalid y type."""
    # Arrange
    x: list[float] = [0, 1, 2]
    invalid_y = "not a list"
    expected_message = "y must be a list or numpy array"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        numerical_derivative(x, cast(Any, invalid_y))


def test_numerical_derivative_invalid_method_type() -> None:
    """Test case 19: TypeError for invalid method type."""
    # Arrange
    x: list[float] = [0, 1, 2]
    y: list[float] = [0, 1, 4]
    invalid_method = 123
    expected_message = "method must be a string"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        numerical_derivative(x, y, method=cast(Any, invalid_method))


def test_numerical_derivative_invalid_method_value() -> None:
    """Test case 20: ValueError for invalid method value."""
    # Arrange
    x: list[float] = [0, 1, 2]
    y: list[float] = [0, 1, 4]
    invalid_method = cast(Any, "invalid")
    expected_message = "method must be"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_derivative(x, y, method=invalid_method)


def test_numerical_derivative_invalid_order_type() -> None:
    """Test case 21: TypeError for invalid order type."""
    # Arrange
    x: list[float] = [0, 1, 2]
    y: list[float] = [0, 1, 4]
    invalid_order = 1.5
    expected_message = "order must be an integer"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        numerical_derivative(x, y, order=cast(Any, invalid_order))


def test_numerical_derivative_invalid_order_value() -> None:
    """Test case 22: ValueError for invalid order value."""
    # Arrange
    x: list[float] = [0, 1, 2]
    y: list[float] = [0, 1, 4]
    invalid_order = 3
    expected_message = "order must be 1 or 2"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_derivative(x, y, order=invalid_order)


def test_numerical_derivative_zero_order() -> None:
    """Test case 23: ValueError for order = 0."""
    # Arrange
    x: list[float] = [0, 1, 2]
    y: list[float] = [0, 1, 4]
    invalid_order = 0
    expected_message = "order must be 1 or 2"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_derivative(x, y, order=invalid_order)


def test_numerical_derivative_negative_order() -> None:
    """Test case 24: ValueError for negative order."""
    # Arrange
    x: list[float] = [0, 1, 2]
    y: list[float] = [0, 1, 4]
    invalid_order = -1
    expected_message = "order must be 1 or 2"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_derivative(x, y, order=invalid_order)


def test_numerical_derivative_non_numeric_x() -> None:
    """Test case 25: ValueError for non-numeric x values."""
    # Arrange
    invalid_x = ["a", "b", "c"]
    y: list[float] = [0, 1, 2]
    expected_message = "arrays contain non-numeric values"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_derivative(cast(Any, invalid_x), y)


def test_numerical_derivative_non_numeric_y() -> None:
    """Test case 26: ValueError for non-numeric y values."""
    # Arrange
    x: list[float] = [0, 1, 2]
    invalid_y = ["a", "b", "c"]
    expected_message = "arrays contain non-numeric values"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_derivative(x, cast(Any, invalid_y))


def test_numerical_derivative_multidimensional_x() -> None:
    """Test case 27: ValueError for multidimensional x."""
    # Arrange
    invalid_x: list[list[float]] = [[0, 1], [2, 3]]
    y: list[float] = [0, 1]
    expected_message = "x must be 1-dimensional"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_derivative(cast(Any, invalid_x), y)


def test_numerical_derivative_multidimensional_y() -> None:
    """Test case 28: ValueError for multidimensional y."""
    # Arrange
    x: list[float] = [0, 1]
    invalid_y: list[list[float]] = [[0, 1], [2, 3]]
    expected_message = "y must be 1-dimensional"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_derivative(x, cast(Any, invalid_y))


def test_numerical_derivative_length_mismatch() -> None:
    """Test case 29: ValueError for mismatched array lengths."""
    # Arrange
    x: list[float] = [0, 1, 2]
    y: list[float] = [0, 1, 2, 3, 4]
    expected_message = "x and y must have same length"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_derivative(x, y)


def test_numerical_derivative_single_point() -> None:
    """Test case 30: ValueError for single data point."""
    # Arrange
    x: list[float] = [0]
    y: list[float] = [0]
    expected_message = "need at least 2 points"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_derivative(x, y)


def test_numerical_derivative_empty_arrays() -> None:
    """Test case 31: ValueError for empty arrays."""
    # Arrange
    x: list[float] = []
    y: list[float] = []
    expected_message = "need at least 2 points"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_derivative(x, y)


def test_numerical_derivative_insufficient_points_second_order() -> None:
    """Test case 32: ValueError for insufficient points for 2nd derivative."""
    # Arrange
    x: list[float] = [0, 1]
    y: list[float] = [0, 2]
    expected_message = "need at least 3 points for 2nd derivative"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_derivative(x, y, order=2)


def test_numerical_derivative_nan_in_x() -> None:
    """Test case 33: ValueError for NaN in x."""
    # Arrange
    x = [0.0, np.nan, 2.0]
    y = [0.0, 1.0, 4.0]
    expected_message = "x contains NaN or Inf values"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_derivative(x, y)


def test_numerical_derivative_nan_in_y() -> None:
    """Test case 34: ValueError for NaN in y."""
    # Arrange
    x = [0.0, 1.0, 2.0]
    y = [0.0, np.nan, 4.0]
    expected_message = "y contains NaN or Inf values"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_derivative(x, y)


def test_numerical_derivative_inf_in_x() -> None:
    """Test case 35: ValueError for Inf in x."""
    # Arrange
    x = [0.0, np.inf, 2.0]
    y = [0.0, 1.0, 4.0]
    expected_message = "x contains NaN or Inf values"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_derivative(x, y)


def test_numerical_derivative_inf_in_y() -> None:
    """Test case 36: ValueError for Inf in y."""
    # Arrange
    x = [0.0, 1.0, 2.0]
    y = [0.0, np.inf, 4.0]
    expected_message = "y contains NaN or Inf values"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_derivative(x, y)


def test_numerical_derivative_all_methods_second_order() -> None:
    """Test case 37: All methods with second order derivative."""
    # Arrange
    x: list[float] = [0, 1, 2, 3, 4]
    y: list[float] = [0, 1, 4, 9, 16]  # y = x^2, d²y/dx² = 2

    # Act & Assert - all methods should work
    for method in ["gradient", "forward", "backward", "central"]:
        result = numerical_derivative(x, y, method=cast(Any, method), order=2)
        assert result["order"] == 2
        assert result["method"] == method
        assert len(result["derivative"]) == len(x)
        assert np.all(np.isfinite(result["derivative"]))


def test_numerical_derivative_float_input() -> None:
    """Test case 38: Float values in input."""
    # Arrange
    x = [0.0, 0.5, 1.0, 1.5, 2.0]
    y = [0.0, 0.25, 1.0, 2.25, 4.0]  # y = x^2

    # Act
    result = numerical_derivative(x, y, method="central")

    # Assert
    assert len(result["derivative"]) == len(x)
    assert np.all(np.isfinite(result["derivative"]))
    # dy/dx = 2x - check interior points
    expected = 2 * np.array(x)
    assert np.allclose(result["derivative"][1:-1], expected[1:-1], atol=0.2)


def test_numerical_derivative_return_structure() -> None:
    """Test case 39: Verify complete return structure."""
    # Arrange
    x: list[float] = [0, 1, 2, 3, 4]
    y: list[float] = [0, 1, 4, 9, 16]

    # Act
    result = numerical_derivative(x, y, method="central", order=1)

    # Assert
    assert isinstance(result, dict)
    assert set(result.keys()) == {"derivative", "x", "method", "order"}
    assert isinstance(result["derivative"], np.ndarray)
    assert isinstance(result["x"], np.ndarray)
    assert result["method"] == "central"
    assert result["order"] == 1
    assert len(result["derivative"]) == len(x)
    assert len(result["x"]) == len(x)
