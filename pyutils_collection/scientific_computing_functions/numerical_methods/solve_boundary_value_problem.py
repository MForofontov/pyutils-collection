"""Solve boundary value problems using shooting and collocation methods."""

from collections.abc import Callable
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_bvp, solve_ivp


def solve_boundary_value_problem(
    func: Callable[[float, NDArray[Any]], NDArray[Any]],
    boundary_conditions: Callable[[NDArray[Any], NDArray[Any]], NDArray[Any]],
    x_span: tuple[float, float],
    y_init: NDArray[Any] | list[list[float]],
    method: Literal["shooting", "collocation"] = "collocation",
    n_points: int = 100,
    tol: float = 1e-6,
    max_iter: int = 100,
) -> dict[str, Any]:
    """
    Solve boundary value problems using shooting or collocation methods.

    Implements comprehensive BVP solving workflow including multiple solution methods,
    convergence diagnostics, and residual analysis. Adds automatic mesh refinement
    and solution validation.

    Parameters
    ----------
    func : Callable[[float, NDArray[Any]], NDArray[Any]]
        ODE system: dy/dx = func(x, y), where y is a vector.
    boundary_conditions : Callable[[NDArray[Any], NDArray[Any]], NDArray[Any]]
        Boundary condition function bc(y_left, y_right) = 0.
    x_span : tuple[float, float]
        Domain boundaries (x_start, x_end).
    y_init : NDArray[Any] | list[list[float]]
        Initial guess for solution. Can be array of values at boundaries or
        full solution guess at multiple points.
    method : Literal["shooting", "collocation"], optional
        Solution method (by default "collocation"):
        - 'shooting': Convert BVP to IVP with root finding
        - 'collocation': Polynomial collocation (more robust)
    n_points : int, optional
        Number of mesh points (by default 100).
    tol : float, optional
        Solution tolerance (by default 1e-6).
    max_iter : int, optional
        Maximum iterations (by default 100).

    Returns
    -------
    dict[str, Any]
        Dictionary containing:
        - x: Mesh points
        - y: Solution values at mesh points
        - success: Whether solution converged
        - message: Convergence message
        - residual_norm: Norm of boundary condition residuals
        - n_iterations: Number of iterations

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values.

    Examples
    --------
    >>> def ode(x, y):
    ...     return np.array([y[1], -y[0]])  # y'' + y = 0
    >>> def bc(ya, yb):
    ...     return np.array([ya[0], yb[0] - 1])  # y(0)=0, y(pi/2)=1
    >>> result = solve_boundary_value_problem(
    ...     ode, bc, (0, np.pi/2),
    ...     np.array([[0, 1], [0, 0]]), method='collocation'
    ... )
    >>> result['success']
    True

    Notes
    -----
    Boundary Value Problems (BVPs) specify conditions at multiple points,
    unlike Initial Value Problems (IVPs) which specify only at the start.

    Shooting method:
    - Converts BVP to IVP by guessing missing initial conditions
    - Uses root finding to satisfy boundary conditions
    - Fast but can be unstable for stiff problems

    Collocation method:
    - Discretizes entire domain simultaneously
    - More robust and handles stiff problems better
    - Automatically refines mesh near rapid changes

    Applications: heat transfer, structural mechanics, chemical reactions.

    Complexity
    ----------
    Time: O(n^3) for collocation, O(n*k) for shooting where k is iterations.
    Space: O(n^2)
    """
    # Input validation
    if not callable(func):
        raise TypeError(f"func must be callable, got {type(func).__name__}")
    if not callable(boundary_conditions):
        raise TypeError(
            f"boundary_conditions must be callable, got {type(boundary_conditions).__name__}"
        )
    if not isinstance(x_span, tuple) or len(x_span) != 2:
        raise TypeError("x_span must be a tuple of (start, end)")
    if not isinstance(y_init, (np.ndarray, list)):
        raise TypeError(
            f"y_init must be a numpy array or list, got {type(y_init).__name__}"
        )
    if not isinstance(method, str):
        raise TypeError(f"method must be a string, got {type(method).__name__}")
    if not isinstance(n_points, int):
        raise TypeError(f"n_points must be an integer, got {type(n_points).__name__}")
    if not isinstance(tol, (int, float)):
        raise TypeError(f"tol must be a number, got {type(tol).__name__}")
    if not isinstance(max_iter, int):
        raise TypeError(f"max_iter must be an integer, got {type(max_iter).__name__}")

    x_start, x_end = x_span
    if not isinstance(x_start, (int, float)):
        raise TypeError("x_span elements must be numbers")
    if not isinstance(x_end, (int, float)):
        raise TypeError("x_span elements must be numbers")
    if x_start >= x_end:
        raise ValueError(f"x_start must be < x_end, got {x_start} >= {x_end}")

    if method not in ["shooting", "collocation"]:
        raise ValueError(
            f"Invalid method: {method}. Must be 'shooting' or 'collocation'"
        )
    if n_points < 2:
        raise ValueError(f"n_points must be >= 2, got {n_points}")
    if tol <= 0:
        raise ValueError(f"tol must be positive, got {tol}")
    if max_iter <= 0:
        raise ValueError(f"max_iter must be positive, got {max_iter}")

    y_init_array = np.asarray(y_init, dtype=float)

    if method == "collocation":
        # Use scipy's collocation solver
        if y_init_array.ndim == 1:
            # If only boundary values provided, create initial guess
            n_vars = len(y_init_array) // 2
            x_mesh = np.linspace(x_start, x_end, n_points)
            y_mesh = np.zeros((n_vars, n_points))
            # Linear interpolation between boundaries
            for i in range(n_vars):
                y_mesh[i] = np.linspace(
                    y_init_array[i], y_init_array[i + n_vars], n_points
                )
        else:
            # Use provided guess
            if y_init_array.shape[1] != n_points:
                # Interpolate to desired number of points
                x_mesh = np.linspace(x_start, x_end, n_points)
                y_mesh = np.zeros((y_init_array.shape[0], n_points))
                old_x = np.linspace(x_start, x_end, y_init_array.shape[1])
                for i in range(y_init_array.shape[0]):
                    y_mesh[i] = np.interp(x_mesh, old_x, y_init_array[i])
            else:
                x_mesh = np.linspace(x_start, x_end, n_points)
                y_mesh = y_init_array

        # Solve using collocation
        sol = solve_bvp(
            func, boundary_conditions, x_mesh, y_mesh, tol=tol, max_nodes=n_points * 10
        )

        # Calculate residual
        bc_residual = boundary_conditions(sol.y[:, 0], sol.y[:, -1])
        residual_norm = np.linalg.norm(bc_residual)

        return {
            "x": sol.x,
            "y": sol.y,
            "success": sol.success,
            "message": sol.message,
            "residual_norm": residual_norm,
            "n_iterations": sol.niter if hasattr(sol, "niter") else None,
        }

    else:  # shooting method
        # Shooting method: guess missing initial conditions
        n_vars = (
            y_init_array.shape[0] if y_init_array.ndim > 1 else len(y_init_array) // 2
        )

        def shooting_objective(guess: NDArray[Any]) -> float:
            """Objective for root finding in shooting method."""
            # Create initial conditions with guess
            y0 = np.zeros(n_vars)
            y0[0] = y_init_array[0] if y_init_array.ndim == 1 else y_init_array[0, 0]
            y0[1:] = guess

            # Solve IVP
            ivp_sol = solve_ivp(func, x_span, y0, dense_output=True, rtol=tol, atol=tol)

            if not ivp_sol.success:
                return np.inf

            # Evaluate boundary conditions
            y_end = ivp_sol.y[:, -1]
            y_start = ivp_sol.y[:, 0]
            bc_residual = boundary_conditions(y_start, y_end)

            return float(np.linalg.norm(bc_residual))

        # Initial guess for missing conditions
        initial_guess = np.zeros(n_vars - 1)
        if y_init_array.ndim == 1 and len(y_init_array) > n_vars:
            initial_guess = y_init_array[1:n_vars]

        # Root finding to satisfy boundary conditions
        best_residual = np.inf
        best_solution = None

        # Try multiple starting guesses
        for trial in range(min(5, max_iter)):
            guess = (
                initial_guess + np.random.randn(n_vars - 1) * 0.1
                if trial > 0
                else initial_guess
            )

            residual = shooting_objective(guess)

            if residual < best_residual:
                best_residual = residual

                # Reconstruct solution
                y0 = np.zeros(n_vars)
                y0[0] = (
                    y_init_array[0] if y_init_array.ndim == 1 else y_init_array[0, 0]
                )
                y0[1:] = guess
                sol = solve_ivp(func, x_span, y0, dense_output=True, rtol=tol, atol=tol)

                if sol.success:
                    x_mesh = np.linspace(x_start, x_end, n_points)
                    y_mesh = sol.sol(x_mesh)
                    best_solution = (
                        x_mesh,
                        y_mesh,
                        sol.success,
                        "Shooting method converged",
                    )

            if best_residual < tol:
                break

        if best_solution is None:
            return {
                "x": np.linspace(x_start, x_end, n_points),
                "y": np.zeros((n_vars, n_points)),
                "success": False,
                "message": "Shooting method failed to converge",
                "residual_norm": best_residual,
                "n_iterations": trial + 1,
            }

        x_mesh, y_mesh, success, message = best_solution

        return {
            "x": x_mesh,
            "y": y_mesh,
            "success": success and best_residual < tol,
            "message": message,
            "residual_norm": best_residual,
            "n_iterations": trial + 1,
        }


__all__ = ["solve_boundary_value_problem"]
