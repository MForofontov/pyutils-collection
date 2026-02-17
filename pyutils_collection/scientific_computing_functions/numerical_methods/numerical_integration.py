"""
Perform numerical integration with validation and multiple methods.

Uses scipy.integrate, adds validation, method selection,
and comprehensive integration output.
"""

from collections.abc import Callable
from typing import Literal

import numpy as np
from scipy import integrate


def numerical_integration(
    func: Callable[[float], float] | None = None,
    x: list[float] | np.ndarray | None = None,
    y: list[float] | np.ndarray | None = None,
    a: float | None = None,
    b: float | None = None,
    method: Literal["quad", "trapz", "simps"] = "quad",
    **kwargs: float,
) -> dict[str, float]:
    """
    Perform numerical integration with validation and multiple methods.

    Uses scipy.integrate, adds validation, method selection,
    and error estimation.

    Parameters
    ----------
    func : Callable[[float], float] | None, optional
        Function to integrate (for quad, romberg methods).
    x : list[float] | np.ndarray | None, optional
        Sample points (for trapz, simps methods).
    y : list[float] | np.ndarray | None, optional
        Function values at sample points (for trapz, simps methods).
    a : float | None, optional
        Lower integration limit (for quad, romberg methods).
    b : float | None, optional
        Upper integration limit (for quad, romberg methods).
    method : {'quad', 'trapz', 'simps'}, optional
        Integration method (by default 'quad').
        - quad: Adaptive quadrature (most accurate)
        - trapz: Trapezoidal rule (simple, requires data)
        - simps: Simpson's rule (better accuracy, requires data)
    **kwargs
        Additional arguments passed to integration method.

    Returns
    -------
    dict[str, float]
        Dictionary containing:
        - result: Integration result
        - error: Estimated error (if available)
        - method: Method used

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If required parameters are missing or invalid.

    Examples
    --------
    >>> def f(x): return x**2
    >>> result = numerical_integration(func=f, a=0, b=1, method='quad')
    >>> abs(result['result'] - 1/3) < 0.001
    True

    >>> x = [0, 0.5, 1.0]
    >>> y = [0, 0.25, 1.0]
    >>> result = numerical_integration(x=x, y=y, method='trapz')
    >>> result['result']
    0.375

    Notes
    -----
    - quad: Best for smooth functions, adaptive
    - trapz: Simple, works with data points
    - simps: Better accuracy than trapz

    Complexity
    ----------
    Time: Varies by method, Space: O(n) for data methods
    """
    # Input validation
    if not isinstance(method, str):
        raise TypeError(f"method must be a string, got {type(method).__name__}")
    if method not in ("quad", "trapz", "simps"):
        raise ValueError(
            f"method must be 'quad', 'trapz', or 'simps', got '{method}'"
        )

    # Method-specific validation and integration
    if method == "quad":
        if func is None:
            raise ValueError("func is required for quad method")
        if not callable(func):
            raise TypeError("func must be callable")
        if a is None or b is None:
            raise ValueError("a and b are required for quad method")
        if not isinstance(a, (int, float)):
            raise TypeError(f"a must be a number, got {type(a).__name__}")
        if not isinstance(b, (int, float)):
            raise TypeError(f"b must be a number, got {type(b).__name__}")

        try:
            result, error = integrate.quad(func, a, b, **kwargs)
        except Exception as e:
            raise ValueError(f"integration failed: {e}") from e

        return {
            "result": float(result),
            "error": float(error),
            "method": method,  # type: ignore[dict-item]
        }

    elif method in ("trapz", "simps"):
        if y is None:
            raise ValueError(f"y is required for {method} method")
        if not isinstance(y, (list, np.ndarray)):
            raise TypeError(f"y must be a list or numpy array, got {type(y).__name__}")

        try:
            y_arr = np.asarray(y, dtype=float)
        except (ValueError, TypeError) as e:
            raise ValueError(f"y contains non-numeric values: {e}") from e

        if y_arr.size == 0:
            raise ValueError("y cannot be empty")
        if np.any(~np.isfinite(y_arr)):
            raise ValueError("y contains NaN or Inf values")

        if x is not None:
            if not isinstance(x, (list, np.ndarray)):
                raise TypeError(
                    f"x must be a list or numpy array, got {type(x).__name__}"
                )
            try:
                x_arr = np.asarray(x, dtype=float)
            except (ValueError, TypeError) as e:
                raise ValueError(f"x contains non-numeric values: {e}") from e

            if x_arr.size != y_arr.size:
                raise ValueError(
                    f"x and y must have same length, got {x_arr.size} and {y_arr.size}"
                )
            if np.any(~np.isfinite(x_arr)):
                raise ValueError("x contains NaN or Inf values")
        else:
            x_arr = None

        try:
            if method == "trapz":
                result = integrate.trapezoid(y_arr, x_arr)
            elif method == "simps":
                result = integrate.simpson(y_arr, x=x_arr)
        except Exception as e:
            raise ValueError(f"integration failed: {e}") from e

        return {
            "result": float(result),
            "method": method,  # type: ignore[dict-item]
        }

    else:
        raise ValueError(f"Unknown method: {method}")


__all__ = ["numerical_integration"]
