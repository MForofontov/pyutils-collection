"""
Unit tests for numerical_integration function.

Tests cover:
- Normal cases: various integration methods and functions
- Edge cases: boundary conditions, different methods
- Error cases: invalid parameters, missing required params
"""
from typing import Any, cast
try:
    import numpy as np
    import scipy
    from pyutils_collection.scientific_computing_functions.numerical_methods.numerical_integration import (
        numerical_integration,
    )
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None  # type: ignore
    scipy = None
    numerical_integration = None  # type: ignore

import pytest

pytestmark = [
    pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy and/or scipy not installed"),
    pytest.mark.unit,
    pytest.mark.scientific_computing,
]

# ========== Normal Operation Tests ==========


def test_numerical_integration_quad_simple() -> None:
    """Test case 1: Quad integration of simple function."""

    # Arrange
    def f(x: float) -> float:
        return x**2

    # Integral of x^2 from 0 to 1 = 1/3

    # Act
    result = numerical_integration(func=f, a=0, b=1, method="quad")

    # Assert
    assert "result" in result
    assert "error" in result
    assert "method" in result
    assert cast(str, result["method"]) == "quad"
    assert abs(result["result"] - 1 / 3) < 0.001
    assert result["error"] < 1e-6


def test_numerical_integration_quad_sine() -> None:
    """Test case 2: Quad integration of sine function."""

    # Arrange
    def f(x: float) -> Any:
        return np.sin(x)

    # Integral of sin(x) from 0 to pi = 2

    # Act
    result = numerical_integration(func=f, a=0, b=np.pi, method="quad")

    # Assert
    assert abs(result["result"] - 2.0) < 0.001
    assert result["error"] < 1e-6


def test_numerical_integration_quad_exponential() -> None:
    """Test case 3: Quad integration of exponential function."""

    # Arrange
    def f(x: float) -> Any:
        return np.exp(x)

    # Integral of e^x from 0 to 1 = e - 1
    expected = np.e - 1

    # Act
    result = numerical_integration(func=f, a=0, b=1, method="quad")

    # Assert
    assert abs(result["result"] - expected) < 0.001
    assert result["error"] < 1e-6


def test_numerical_integration_trapz_with_x() -> None:
    """Test case 4: Trapezoidal rule with x and y values."""
    # Arrange
    x = [0, 0.5, 1.0]
    y = [0, 0.25, 1.0]  # y = x^2
    # Integral ≈ 0.375 (trapezoidal approximation)

    # Act
    result = numerical_integration(x=x, y=y, method="trapz")

    # Assert
    assert "result" in result
    assert "method" in result
    assert cast(str, result["method"]) == "trapz"
    assert abs(result["result"] - 0.375) < 0.01


def test_numerical_integration_trapz_without_x() -> None:
    """Test case 5: Trapezoidal rule with only y values (uniform spacing)."""
    # Arrange
    y: list[float] = [0, 1, 4, 9, 16]  # x = 0, 1, 2, 3, 4; y = x^2
    # With dx=1, trapz integral = 0.5*(0+1) + 0.5*(1+4) + 0.5*(4+9) + 0.5*(9+16) = 0.5+2.5+6.5+12.5 = 22

    # Act
    result = numerical_integration(y=y, method="trapz")

    # Assert
    assert "result" in result
    assert abs(result["result"] - 22.0) < 0.1


def test_numerical_integration_simps_with_x() -> None:
    """Test case 6: Simpson's rule with x and y values."""
    # Arrange
    x = [0, 0.5, 1.0]
    y = [0, 0.25, 1.0]  # y = x^2
    # Simpson's gives better approximation than trapz

    # Act
    result = numerical_integration(x=x, y=y, method="simps")

    # Assert
    assert cast(str, result["method"]) == "simps"
    assert abs(result["result"] - 1 / 3) < 0.01  # Should be closer to exact value


def test_numerical_integration_simps_without_x() -> None:
    """Test case 7: Simpson's rule with only y values."""
    # Arrange
    y: list[float] = [0, 1, 4]  # Minimum 3 points for Simpson's

    # Act
    result = numerical_integration(y=y, method="simps")

    # Assert
    assert cast(str, result["method"]) == "simps"
    assert isinstance(result["result"], float)
    assert np.isfinite(result["result"])


def test_numerical_integration_negative_limits() -> None:
    """Test case 8: Integration with negative limits."""

    # Arrange
    def f(x: float) -> float:
        return x**2

    # Integral from -1 to 1
    expected = 2 / 3

    # Act
    result = numerical_integration(func=f, a=-1, b=1, method="quad")

    # Assert
    assert abs(result["result"] - expected) < 0.001


def test_numerical_integration_reversed_limits() -> None:
    """Test case 9: Integration with b < a (should be negative)."""

    # Arrange
    def f(x: float) -> float:
        return x**2

    # Integral from 1 to 0 = -1/3

    # Act
    result = numerical_integration(func=f, a=1, b=0, method="quad")

    # Assert
    assert abs(result["result"] + 1 / 3) < 0.001  # Negative result


# ========== Edge Case Tests ==========


def test_numerical_integration_zero_interval() -> None:
    """Test case 10: Integration over zero-width interval."""

    # Arrange
    def f(x: float) -> float:
        return x**2

    # Act
    result = numerical_integration(func=f, a=1, b=1, method="quad")

    # Assert
    assert abs(result["result"]) < 1e-10  # Should be zero


def test_numerical_integration_large_interval() -> None:
    """Test case 11: Integration over large interval."""

    # Arrange
    def f(x: float) -> Any:
        return np.exp(-x)

    # Integral of e^(-x) from 0 to infinity ≈ 1
    # Use large upper bound

    # Act
    result = numerical_integration(func=f, a=0, b=100, method="quad")

    # Assert
    assert abs(result["result"] - 1.0) < 0.01


def test_numerical_integration_constant_function() -> None:
    """Test case 12: Integration of constant function."""

    # Arrange
    def f(x: float) -> float:
        return 5.0

    # Integral of 5 from 0 to 2 = 10

    # Act
    result = numerical_integration(func=f, a=0, b=2, method="quad")

    # Assert
    assert abs(result["result"] - 10.0) < 0.001


def test_numerical_integration_numpy_arrays() -> None:
    """Test case 13: Using numpy arrays for x and y."""
    # Arrange
    x = np.array([0.0, 0.5, 1.0])
    y = np.array([0.0, 0.25, 1.0])

    # Act
    result = numerical_integration(x=x, y=y, method="trapz")

    # Assert
    assert isinstance(result["result"], float)
    assert np.isfinite(result["result"])


def test_numerical_integration_many_points() -> None:
    """Test case 14: Integration with many sample points."""
    # Arrange
    x = np.linspace(0, 1, 1000)
    y = x**2

    # Act
    result = numerical_integration(x=x, y=y, method="trapz")

    # Assert
    # Should be very close to exact value 1/3 with many points
    assert abs(result["result"] - 1 / 3) < 0.001


def test_numerical_integration_float_limits() -> None:
    """Test case 15: Float limits with decimals."""

    # Arrange
    def f(x: float) -> float:
        return x

    # Integral of x from 0.5 to 1.5 = (1.5^2 - 0.5^2)/2 = 1.0

    # Act
    result = numerical_integration(func=f, a=0.5, b=1.5, method="quad")

    # Assert
    assert abs(result["result"] - 1.0) < 0.001


# ========== Error Case Tests ==========


def test_numerical_integration_invalid_method_type() -> None:
    """Test case 16: TypeError for invalid method type."""

    # Arrange
    def f(x: float) -> float:
        return x

    invalid_method = 123
    expected_message = "method must be a string"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        numerical_integration(func=f, a=0, b=1, method=cast(Any, invalid_method))


def test_numerical_integration_invalid_method_value() -> None:
    """Test case 17: ValueError for invalid method value."""

    # Arrange
    def f(x: float) -> float:
        return x

    invalid_method = "invalid"
    expected_message = "method must be"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_integration(func=f, a=0, b=1, method=invalid_method)  # type: ignore[arg-type]


def test_numerical_integration_quad_missing_func() -> None:
    """Test case 18: ValueError for quad without func."""
    # Arrange
    expected_message = "func is required for quad method"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_integration(func=None, a=0, b=1, method="quad")


def test_numerical_integration_quad_non_callable_func() -> None:
    """Test case 19: TypeError for non-callable func."""
    # Arrange
    invalid_func = "not a function"
    expected_message = "func must be callable"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        numerical_integration(func=cast(Any, invalid_func), a=0, b=1, method="quad")


def test_numerical_integration_quad_missing_a() -> None:
    """Test case 20: ValueError for quad without a."""

    # Arrange
    def f(x: float) -> float:
        return x

    expected_message = "a and b are required"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_integration(func=f, a=None, b=1, method="quad")


def test_numerical_integration_quad_missing_b() -> None:
    """Test case 21: ValueError for quad without b."""

    # Arrange
    def f(x: float) -> float:
        return x

    expected_message = "a and b are required"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_integration(func=f, a=0, b=None, method="quad")


def test_numerical_integration_quad_invalid_a_type() -> None:
    """Test case 22: TypeError for invalid a type."""

    # Arrange
    def f(x: float) -> float:
        return x

    invalid_a = "not a number"
    expected_message = "a must be a number"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        numerical_integration(func=f, a=cast(Any, invalid_a), b=1, method="quad")


def test_numerical_integration_quad_invalid_b_type() -> None:
    """Test case 23: TypeError for invalid b type."""

    # Arrange
    def f(x: float) -> float:
        return x

    invalid_b = "not a number"
    expected_message = "b must be a number"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        numerical_integration(func=f, a=0, b=cast(Any, invalid_b), method="quad")


def test_numerical_integration_trapz_missing_y() -> None:
    """Test case 24: ValueError for trapz without y."""
    # Arrange
    expected_message = "y is required for trapz method"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_integration(y=None, method="trapz")


def test_numerical_integration_trapz_invalid_y_type() -> None:
    """Test case 25: TypeError for invalid y type."""
    # Arrange
    invalid_y = "not a list"
    expected_message = "y must be a list or numpy array"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        numerical_integration(y=cast(Any, invalid_y), method="trapz")


def test_numerical_integration_trapz_non_numeric_y() -> None:
    """Test case 26: ValueError for non-numeric y values."""
    # Arrange
    invalid_y = ["a", "b", "c"]
    expected_message = "y contains non-numeric values"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_integration(y=cast(Any, invalid_y), method="trapz")


def test_numerical_integration_trapz_empty_y() -> None:
    """Test case 27: ValueError for empty y."""
    # Arrange
    empty_y: list[float] = []
    expected_message = "y cannot be empty"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_integration(y=empty_y, method="trapz")


def test_numerical_integration_trapz_nan_in_y() -> None:
    """Test case 28: ValueError for NaN in y."""
    # Arrange
    invalid_y = [0.0, np.nan, 2.0]
    expected_message = "y contains NaN or Inf values"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_integration(y=invalid_y, method="trapz")


def test_numerical_integration_trapz_inf_in_y() -> None:
    """Test case 29: ValueError for Inf in y."""
    # Arrange
    invalid_y = [0.0, np.inf, 2.0]
    expected_message = "y contains NaN or Inf values"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_integration(y=invalid_y, method="trapz")


def test_numerical_integration_trapz_invalid_x_type() -> None:
    """Test case 30: TypeError for invalid x type."""
    # Arrange
    y: list[float] = [0, 1, 2]
    invalid_x = "not a list"
    expected_message = "x must be a list or numpy array"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        numerical_integration(x=cast(Any, invalid_x), y=y, method="trapz")


def test_numerical_integration_trapz_non_numeric_x() -> None:
    """Test case 31: ValueError for non-numeric x values."""
    # Arrange
    invalid_x = ["a", "b", "c"]
    y: list[float] = [0, 1, 2]
    expected_message = "x contains non-numeric values"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_integration(x=cast(Any, invalid_x), y=y, method="trapz")


def test_numerical_integration_trapz_length_mismatch() -> None:
    """Test case 32: ValueError for mismatched x and y lengths."""
    # Arrange
    x: list[float] = [0, 1]
    y: list[float] = [0, 1, 2, 3]
    expected_message = "x and y must have same length"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_integration(x=x, y=y, method="trapz")


def test_numerical_integration_trapz_nan_in_x() -> None:
    """Test case 33: ValueError for NaN in x."""
    # Arrange
    invalid_x = [0.0, np.nan, 2.0]
    y = [0.0, 1.0, 2.0]
    expected_message = "x contains NaN or Inf values"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_integration(x=invalid_x, y=y, method="trapz")


def test_numerical_integration_trapz_inf_in_x() -> None:
    """Test case 34: ValueError for Inf in x."""
    # Arrange
    invalid_x = [0.0, np.inf, 2.0]
    y = [0.0, 1.0, 2.0]
    expected_message = "x contains NaN or Inf values"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_integration(x=invalid_x, y=y, method="trapz")


def test_numerical_integration_simps_missing_y() -> None:
    """Test case 35: ValueError for simps without y."""
    # Arrange
    expected_message = "y is required for simps method"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_integration(y=None, method="simps")


def test_numerical_integration_return_structure_quad() -> None:
    """Test case 36: Verify complete return structure for quad."""

    # Arrange
    def f(x: float) -> float:
        return x

    # Act
    result = numerical_integration(func=f, a=0, b=1, method="quad")

    # Assert
    assert isinstance(result, dict)
    assert "result" in result
    assert "error" in result
    assert "method" in result
    assert cast(str, result["method"]) == "quad"
    assert isinstance(result["result"], float)
    assert isinstance(result["error"], float)


def test_numerical_integration_return_structure_trapz() -> None:
    """Test case 37: Verify complete return structure for trapz."""
    # Arrange
    y: list[float] = [0, 1, 2]

    # Act
    result = numerical_integration(y=y, method="trapz")

    # Assert
    assert isinstance(result, dict)
    assert "result" in result
    assert "method" in result
    assert cast(str, result["method"]) == "trapz"
    assert isinstance(result["result"], float)
    # trapz doesn't have error estimate
    assert "error" not in result or result.get("error") is None


def test_numerical_integration_trapz_integration_failure() -> None:
    """Test case 38: ValueError when trapz has invalid y data."""
    # Arrange - NaN values caught by validation
    invalid_y = np.array([np.nan, np.nan, np.nan])

    # Act & Assert
    with pytest.raises(ValueError, match="y contains NaN or Inf values"):
        numerical_integration(y=invalid_y, method="trapz")


def test_numerical_integration_simps_integration_failure() -> None:
    """Test case 39: ValueError when simps has invalid y data."""
    # Arrange - NaN values caught by validation
    invalid_y = np.array([np.nan, np.nan, np.nan])

    # Act & Assert
    with pytest.raises(ValueError, match="y contains NaN or Inf values"):
        numerical_integration(y=invalid_y, method="simps")


def test_numerical_integration_unknown_method() -> None:
    """Test case 40: ValueError for unknown integration method."""

    # Arrange
    def f(x: float) -> float:
        return x

    expected_message = "method must be 'quad', 'trapz', or 'simps'"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        numerical_integration(func=f, a=0, b=1, method="invalid_method")  # type: ignore[arg-type]
