"""
Compute numerical derivative with validation and multiple methods.

Uses numpy.gradient or finite difference methods, adds validation
and comprehensive derivative computation.
"""

from typing import Literal

import numpy as np


def numerical_derivative(
    x: list[float] | np.ndarray,
    y: list[float] | np.ndarray,
    method: Literal["gradient", "forward", "backward", "central"] = "central",
    order: int = 1,
) -> dict[str, np.ndarray]:
    """
    Compute numerical derivative with validation and multiple methods.

    Uses numpy.gradient or finite difference methods, adds validation
    and comprehensive derivative computation.

    Parameters
    ----------
    x : list[float] | np.ndarray
        Independent variable values.
    y : list[float] | np.ndarray
        Dependent variable values (function values).
    method : {'gradient', 'forward', 'backward', 'central'}, optional
        Differentiation method (by default 'central').
        - gradient: NumPy gradient (2nd order accurate)
        - forward: Forward difference
        - backward: Backward difference
        - central: Central difference (most accurate)
    order : int, optional
        Derivative order (1 or 2, by default 1).

    Returns
    -------
    dict[str, np.ndarray]
        Dictionary containing:
        - derivative: Computed derivative values
        - x: Independent variable values
        - method: Method used
        - order: Derivative order

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If arrays have different lengths or are too short.

    Examples
    --------
    >>> x = [0, 1, 2, 3, 4]
    >>> y = [0, 1, 4, 9, 16]  # y = x^2, dy/dx = 2x
    >>> result = numerical_derivative(x, y, method='central')
    >>> result['derivative']
    array([0., 2., 4., 6., 8.])

    Notes
    -----
    Central difference is most accurate for interior points.
    Forward/backward used at boundaries.

    Complexity
    ----------
    Time: O(n), Space: O(n)
    """
    # Input validation
    if not isinstance(x, (list, np.ndarray)):
        raise TypeError(f"x must be a list or numpy array, got {type(x).__name__}")
    if not isinstance(y, (list, np.ndarray)):
        raise TypeError(f"y must be a list or numpy array, got {type(y).__name__}")
    if not isinstance(method, str):
        raise TypeError(f"method must be a string, got {type(method).__name__}")
    if method not in ("gradient", "forward", "backward", "central"):
        raise ValueError(
            f"method must be 'gradient', 'forward', 'backward', or 'central', got '{method}'"
        )
    if not isinstance(order, int):
        raise TypeError(f"order must be an integer, got {type(order).__name__}")
    if order not in (1, 2):
        raise ValueError(f"order must be 1 or 2, got {order}")

    # Convert to numpy arrays
    try:
        x_arr = np.asarray(x, dtype=float)
        y_arr = np.asarray(y, dtype=float)
    except (ValueError, TypeError) as e:
        raise ValueError(f"arrays contain non-numeric values: {e}") from e

    if x_arr.ndim != 1:
        raise ValueError(f"x must be 1-dimensional, got {x_arr.ndim} dimensions")
    if y_arr.ndim != 1:
        raise ValueError(f"y must be 1-dimensional, got {y_arr.ndim} dimensions")
    if x_arr.size != y_arr.size:
        raise ValueError(
            f"x and y must have same length, got {x_arr.size} and {y_arr.size}"
        )
    if x_arr.size < 2:
        raise ValueError(f"need at least 2 points, got {x_arr.size}")
    if order == 2 and x_arr.size < 3:
        raise ValueError(f"need at least 3 points for 2nd derivative, got {x_arr.size}")

    if np.any(~np.isfinite(x_arr)):
        raise ValueError("x contains NaN or Inf values")
    if np.any(~np.isfinite(y_arr)):
        raise ValueError("y contains NaN or Inf values")

    # Compute derivative
    if method == "gradient":
        # Use numpy gradient (2nd order accurate)
        derivative = np.gradient(y_arr, x_arr, edge_order=2)
        if order == 2:
            derivative = np.gradient(derivative, x_arr, edge_order=2)

    elif method == "forward":
        # Forward difference
        if order == 1:
            dx = np.diff(x_arr)
            dy = np.diff(y_arr)
            derivative = np.zeros(x_arr.size)
            derivative[:-1] = dy / dx
            # Use backward difference for last point
            derivative[-1] = (y_arr[-1] - y_arr[-2]) / (x_arr[-1] - x_arr[-2])
        else:  # order == 2
            # Second derivative using forward difference
            derivative = np.zeros(x_arr.size)
            for i in range(x_arr.size - 2):
                h1 = x_arr[i + 1] - x_arr[i]
                h2 = x_arr[i + 2] - x_arr[i + 1]
                derivative[i] = (
                    2 * y_arr[i] / (h1 * (h1 + h2))
                    - 2 * y_arr[i + 1] / (h1 * h2)
                    + 2 * y_arr[i + 2] / (h2 * (h1 + h2))
                )
            # Use backward for last two points
            derivative[-2] = derivative[-3]
            derivative[-1] = derivative[-3]

    elif method == "backward":
        # Backward difference
        if order == 1:
            dx = np.diff(x_arr)
            dy = np.diff(y_arr)
            derivative = np.zeros(x_arr.size)
            derivative[1:] = dy / dx
            # Use forward difference for first point
            derivative[0] = (y_arr[1] - y_arr[0]) / (x_arr[1] - x_arr[0])
        else:  # order == 2
            derivative = np.zeros(x_arr.size)
            for i in range(2, x_arr.size):
                h1 = x_arr[i] - x_arr[i - 1]
                h2 = x_arr[i - 1] - x_arr[i - 2]
                derivative[i] = (
                    2 * y_arr[i] / (h1 * (h1 + h2))
                    - 2 * y_arr[i - 1] / (h1 * h2)
                    + 2 * y_arr[i - 2] / (h2 * (h1 + h2))
                )
            # Use forward for first two points
            derivative[0] = derivative[2]
            derivative[1] = derivative[2]

    elif method == "central":
        # Central difference (most accurate)
        if order == 1:
            derivative = np.zeros(x_arr.size)
            # Central difference for interior points
            for i in range(1, x_arr.size - 1):
                h_forward = x_arr[i + 1] - x_arr[i]
                h_backward = x_arr[i] - x_arr[i - 1]
                derivative[i] = (
                    (y_arr[i + 1] - y_arr[i]) / h_forward
                    + (y_arr[i] - y_arr[i - 1]) / h_backward
                ) / 2
            # Forward for first, backward for last
            derivative[0] = (y_arr[1] - y_arr[0]) / (x_arr[1] - x_arr[0])
            derivative[-1] = (y_arr[-1] - y_arr[-2]) / (x_arr[-1] - x_arr[-2])
        else:  # order == 2
            derivative = np.zeros(x_arr.size)
            for i in range(1, x_arr.size - 1):
                h_forward = x_arr[i + 1] - x_arr[i]
                h_backward = x_arr[i] - x_arr[i - 1]
                derivative[i] = 2 * (
                    y_arr[i + 1] / (h_forward * (h_forward + h_backward))
                    - y_arr[i] / (h_forward * h_backward)
                    + y_arr[i - 1] / (h_backward * (h_forward + h_backward))
                )
            # Use adjacent values for boundaries
            derivative[0] = derivative[1]
            derivative[-1] = derivative[-2]

    else:
        raise ValueError(f"Unknown method: {method}")

    return {
        "derivative": derivative,
        "x": x_arr,
        "method": method,  # type: ignore[dict-item]
        "order": order,  # type: ignore[dict-item]
    }


__all__ = ["numerical_derivative"]
