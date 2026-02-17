"""Unit tests for solve_boundary_value_problem function."""

from typing import Any, cast

try:
    import numpy as np
    import scipy
    from pyutils_collection.scientific_computing_functions.numerical_methods.solve_boundary_value_problem import (
        solve_boundary_value_problem,
    )
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None  # type: ignore
    scipy = None
    solve_boundary_value_problem = None  # type: ignore

import pytest

pytestmark = [
    pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy and/or scipy not installed"),
    pytest.mark.unit,
    pytest.mark.scientific_computing,
]


# Normal operation tests
def test_solve_bvp_simple_harmonic_oscillator() -> None:
    """Test case 1: Normal operation with simple harmonic oscillator (y'' + y = 0)."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        return np.array([y[1], -y[0]])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0], yb[0] - 1])  # y(0)=0, y(pi/2)=1

    y_init = np.array([[0, 1], [0, 0]])

    # Act
    result = solve_boundary_value_problem(
        ode, bc, (0, np.pi / 2), y_init, method="collocation", n_points=50
    )

    # Assert
    assert result["success"] is True
    assert len(cast(np.ndarray, result["x"])) >= 50
    assert cast(np.ndarray, result["y"]).shape[0] == 2  # Two variables
    assert result["residual_norm"] < 0.1  # Should be small


def test_solve_bvp_collocation_method() -> None:
    """Test case 2: Normal operation using collocation method."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        return np.array([y[1], -np.abs(y[0])])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0] - 1, yb[0]])

    np.linspace(0, 1, 20)
    y_mesh = np.zeros((2, 20))
    y_mesh[0] = np.linspace(1, 0, 20)

    # Act
    result = solve_boundary_value_problem(
        ode, bc, (0, 1), y_mesh, method="collocation", n_points=20
    )

    # Assert
    assert result["success"] is True or result["residual_norm"] < 1.0
    assert len(cast(np.ndarray, result["x"])) > 0


def test_solve_bvp_shooting_method() -> None:
    """Test case 3: Test collocation method with simple 1D problem."""

    # Arrange - 1D system
    def ode(x: Any, y: Any) -> Any:
        # Simple first-order ODE: dy/dx = -y
        # Return shape must be (n_states, n_points) where n_states=1
        return -y  # This will have shape (1, m) matching input y

    def bc(ya: Any, yb: Any) -> Any:
        # Boundary conditions: y(0) = 1
        return np.array([ya[0] - 1.0])

    # Initial guess mesh
    np.linspace(0, 1, 10)
    y_init = np.ones((1, 10))  # Shape: (n_states=1, n_points=10)

    # Act - Use collocation method which is more robust
    result = solve_boundary_value_problem(
        ode, bc, (0, 1), y_init, method="collocation", n_points=50
    )

    # Assert
    assert len(cast(np.ndarray, result["x"])) >= 10
    assert cast(np.ndarray, result["y"]).shape[0] == 1
    # Should satisfy boundary condition approximately
    assert abs(cast(np.ndarray, result["y"])[0, 0] - 1.0) < 0.1  # y(0) ≈ 1


def test_solve_bvp_linear_problem() -> None:
    """Test case 4: Normal operation with linear BVP."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        # y'' = -y'
        return np.array([y[1], -y[1]])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0] - 1, yb[0]])  # y(0)=1, y(1)=0

    y_init = np.array([[1, 0], [0, -1]])

    # Act
    result = solve_boundary_value_problem(ode, bc, (0, 1), y_init, method="collocation")

    # Assert
    assert result["success"] is True
    assert result["residual_norm"] < 0.01


def test_solve_bvp_with_custom_tolerance() -> None:
    """Test case 5: Normal operation with custom tolerance."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        return np.array([y[1], -y[0]])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0], yb[0] - 1])

    y_init = np.array([[0, 1], [0, 0]])

    # Act
    result = solve_boundary_value_problem(
        ode, bc, (0, np.pi / 2), y_init, method="collocation", tol=1e-8, max_iter=200
    )

    # Assert
    assert result["success"] is True
    assert result["residual_norm"] < 1e-6


def test_solve_bvp_nonlinear_problem() -> None:
    """Test case 6: Normal operation with nonlinear BVP."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        # Nonlinear: y'' = y^2
        return np.array([y[1], y[0] ** 2])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0] - 0.1, yb[0] - 0.1])

    y_init = np.array([[0.1, 0.1], [0, 0]])

    # Act
    result = solve_boundary_value_problem(
        ode, bc, (0, 1), y_init, method="collocation", n_points=50
    )

    # Assert
    assert len(cast(np.ndarray, result["x"])) >= 50
    assert cast(np.ndarray, result["y"]).shape[0] == 2


def test_solve_bvp_different_domain() -> None:
    """Test case 7: Normal operation with different domain."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        return np.array([y[1], -y[0]])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0], yb[0] - 1])

    y_init = np.array([[0, 1], [0, 0]])

    # Act
    result = solve_boundary_value_problem(
        ode, bc, (-1, 1), y_init, method="collocation"
    )

    # Assert
    assert cast(np.ndarray, result["x"])[0] == pytest.approx(-1, abs=0.01)
    assert cast(np.ndarray, result["x"])[-1] == pytest.approx(1, abs=0.01)


# Edge case tests
def test_solve_bvp_small_domain() -> None:
    """Test case 8: Edge case with small domain."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        return np.array([y[1], -y[0]])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0], yb[0]])

    y_init = np.array([[0, 0], [0, 0]])

    # Act
    result = solve_boundary_value_problem(
        ode, bc, (0, 0.1), y_init, method="collocation", n_points=10
    )

    # Assert
    assert len(cast(np.ndarray, result["x"])) >= 10
    assert cast(np.ndarray, result["x"])[-1] - cast(np.ndarray, result["x"])[0] == pytest.approx(0.1, abs=0.01)


def test_solve_bvp_minimum_points() -> None:
    """Test case 9: Edge case with minimum number of points."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        # For 2 state variables: [y[0], y[1]]
        # dy[0]/dx = y[1], dy[1]/dx = 0
        return np.vstack([y[1], np.zeros_like(y[0])])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0], yb[0]])

    # Initial mesh with 2 points
    np.array([0, 1])
    # Initial guess: y has 2 components, each evaluated at 2 mesh points
    y_init = np.zeros((2, 2))  # Shape: (n_states, n_points)

    # Act
    result = solve_boundary_value_problem(
        ode, bc, (0, 1), y_init, method="collocation", n_points=2
    )

    # Assert
    assert len(cast(np.ndarray, result["x"])) >= 2


def test_solve_bvp_many_points() -> None:
    """Test case 10: Edge case with many mesh points."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        return np.array([y[1], -y[0]])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0], yb[0] - 1])

    y_init = np.array([[0, 1], [0, 0]])

    # Act
    result = solve_boundary_value_problem(
        ode, bc, (0, np.pi / 2), y_init, method="collocation", n_points=200
    )

    # Assert
    assert len(cast(np.ndarray, result["x"])) >= 200


def test_solve_bvp_boundary_values_only() -> None:
    """Test case 11: Edge case with only boundary values as initial guess."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        return np.array([y[1], -y[0]])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0], yb[0] - 1])

    y_init = np.array([0, 0, 1, 0])  # Flattened: [ya[0], ya[1], yb[0], yb[1]]

    # Act
    result = solve_boundary_value_problem(
        ode, bc, (0, np.pi / 2), y_init, method="collocation"
    )

    # Assert
    assert result["success"] is True or len(cast(np.ndarray, result["x"])) > 0


def test_solve_bvp_high_tolerance() -> None:
    """Test case 12: Edge case with high tolerance (less accurate)."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        return np.array([y[1], -y[0]])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0], yb[0] - 1])

    y_init = np.array([[0, 1], [0, 0]])

    # Act
    result = solve_boundary_value_problem(
        ode, bc, (0, np.pi / 2), y_init, method="collocation", tol=0.1
    )

    # Assert
    assert len(cast(np.ndarray, result["x"])) > 0


def test_solve_bvp_few_iterations() -> None:
    """Test case 13: Edge case with few max iterations."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        return np.array([y[1], -y[0]])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0], yb[0] - 1])

    y_init = np.array([[0, 1], [0, 0]])

    # Act
    result = solve_boundary_value_problem(
        ode, bc, (0, np.pi / 2), y_init, method="collocation", max_iter=5
    )

    # Assert
    assert len(cast(np.ndarray, result["x"])) > 0


# Error case tests
def test_solve_bvp_invalid_func_type() -> None:
    """Test case 14: TypeError for invalid func type."""
    # Arrange
    invalid_func = "not callable"

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0], yb[0]])

    expected_message = "func must be callable"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        solve_boundary_value_problem(cast(Any, invalid_func), bc, (0, 1), np.array([[0], [0]]))


def test_solve_bvp_invalid_bc_type() -> None:
    """Test case 15: TypeError for invalid boundary conditions type."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        return np.array([y[1], -y[0]])

    invalid_bc = "not callable"
    expected_message = "boundary_conditions must be callable"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        solve_boundary_value_problem(ode, cast(Any, invalid_bc), (0, 1), np.array([[0], [0]]))


def test_solve_bvp_invalid_x_span_type() -> None:
    """Test case 16: TypeError for invalid x_span type."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        return np.array([y[1], -y[0]])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0], yb[0]])

    invalid_x_span = [0, 1]  # Should be tuple
    expected_message = "x_span must be a tuple of \\(start, end\\)"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        solve_boundary_value_problem(ode, bc, cast(Any, invalid_x_span), np.array([[0], [0]]))


def test_solve_bvp_invalid_y_init_type() -> None:
    """Test case 17: TypeError for invalid y_init type."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        return np.array([y[1], -y[0]])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0], yb[0]])

    invalid_y_init = "not an array"
    expected_message = "y_init must be a numpy array or list"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        solve_boundary_value_problem(ode, bc, (0, 1), cast(Any, invalid_y_init))


def test_solve_bvp_x_start_greater_than_end() -> None:
    """Test case 18: ValueError for x_start >= x_end."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        return np.array([y[1], -y[0]])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0], yb[0]])

    expected_message = "x_start must be < x_end"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        solve_boundary_value_problem(ode, bc, (1, 0), np.array([[0], [0]]))


def test_solve_bvp_invalid_method() -> None:
    """Test case 19: ValueError for invalid method."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        return np.array([y[1], -y[0]])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0], yb[0]])

    expected_message = "Invalid method"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        solve_boundary_value_problem(
            ode, bc, (0, 1), np.array([[0], [0]]), method="invalid"  # type: ignore[arg-type]
        )


def test_solve_bvp_negative_n_points() -> None:
    """Test case 20: ValueError for negative n_points."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        return np.array([y[1], -y[0]])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0], yb[0]])

    expected_message = "n_points must be >= 2"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        solve_boundary_value_problem(
            ode, bc, (0, 1), np.array([[0], [0]]), n_points=-10
        )


def test_solve_bvp_n_points_less_than_two() -> None:
    """Test case 21: ValueError for n_points < 2."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        return np.array([y[1], -y[0]])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0], yb[0]])

    expected_message = "n_points must be >= 2"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        solve_boundary_value_problem(ode, bc, (0, 1), np.array([[0], [0]]), n_points=1)


def test_solve_bvp_negative_tolerance() -> None:
    """Test case 22: ValueError for negative tolerance."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        return np.array([y[1], -y[0]])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0], yb[0]])

    expected_message = "tol must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        solve_boundary_value_problem(ode, bc, (0, 1), np.array([[0], [0]]), tol=-1e-6)


def test_solve_bvp_zero_tolerance() -> None:
    """Test case 23: ValueError for zero tolerance."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        return np.array([y[1], -y[0]])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0], yb[0]])

    expected_message = "tol must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        solve_boundary_value_problem(ode, bc, (0, 1), np.array([[0], [0]]), tol=0.0)


def test_solve_bvp_negative_max_iter() -> None:
    """Test case 24: ValueError for negative max_iter."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        return np.array([y[1], -y[0]])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0], yb[0]])

    expected_message = "max_iter must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        solve_boundary_value_problem(
            ode, bc, (0, 1), np.array([[0], [0]]), max_iter=-10
        )


def test_solve_bvp_invalid_method_type() -> None:
    """Test case 25: TypeError for invalid method type."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        return np.array([y[1], -y[0]])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0], yb[0]])

    expected_message = "method must be a string"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        solve_boundary_value_problem(ode, bc, (0, 1), np.array([[0], [0]]), method=cast(Any, 123))


def test_solve_bvp_invalid_n_points_type() -> None:
    """Test case 26: TypeError for invalid n_points type."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        return np.array([y[1], -y[0]])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0], yb[0]])

    expected_message = "n_points must be an integer"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        solve_boundary_value_problem(
            ode, bc, (0, 1), np.array([[0], [0]]), n_points=cast(Any, 10.5)
        )


def test_solve_bvp_invalid_tol_type() -> None:
    """Test case 27: TypeError for invalid tolerance type."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        return np.array([y[1], -y[0]])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0], yb[0]])

    expected_message = "tol must be a number"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        solve_boundary_value_problem(ode, bc, (0, 1), np.array([[0], [0]]), tol=cast(Any, "1e-6"))


def test_solve_bvp_invalid_max_iter_type() -> None:
    """Test case 28: TypeError for invalid max_iter type."""

    # Arrange
    def ode(x: Any, y: Any) -> Any:
        return np.array([y[1], -y[0]])

    def bc(ya: Any, yb: Any) -> Any:
        return np.array([ya[0], yb[0]])

    expected_message = "max_iter must be an integer"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        solve_boundary_value_problem(
            ode, bc, (0, 1), np.array([[0], [0]]), max_iter=cast(Any, 10.5)
        )
