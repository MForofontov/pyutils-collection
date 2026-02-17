"""
Solve linear system of equations with validation and diagnostics.

Uses numpy.linalg.solve, adds validation, condition number checks,
and solution quality assessment.
"""

import numpy as np


def solve_linear_system(
    A: list[list[float]] | np.ndarray,
    b: list[float] | np.ndarray,
    check_condition: bool = True,
    condition_threshold: float = 1e10,
) -> dict[str, np.ndarray | float | bool]:
    """
    Solve linear system Ax = b with validation and diagnostics.

    Uses numpy.linalg.solve, adds validation, condition number checks,
    and solution quality assessment.

    Parameters
    ----------
    A : list[list[float]] | np.ndarray
        Coefficient matrix (n x n).
    b : list[float] | np.ndarray
        Right-hand side vector (n,).
    check_condition : bool, optional
        Whether to check condition number (by default True).
    condition_threshold : float, optional
        Threshold for ill-conditioned matrix warning (by default 1e10).

    Returns
    -------
    dict[str, np.ndarray | float | bool]
        Dictionary containing:
        - solution: Solution vector x
        - residual_norm: Norm of residual Ax - b
        - condition_number: Condition number of A (if checked)
        - well_conditioned: Whether matrix is well-conditioned

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If matrix dimensions are incompatible or matrix is singular.

    Examples
    --------
    >>> A = [[2, 1], [1, 3]]
    >>> b = [1, 2]
    >>> result = solve_linear_system(A, b)
    >>> result['solution']
    array([0.2, 0.6])

    Notes
    -----
    Uses LU decomposition for solving. For ill-conditioned systems,
    consider using least squares or regularization methods.

    Complexity
    ----------
    Time: O(n³), Space: O(n²)
    """
    # Input validation
    if not isinstance(A, (list, np.ndarray)):
        raise TypeError(f"A must be a list or numpy array, got {type(A).__name__}")
    if not isinstance(b, (list, np.ndarray)):
        raise TypeError(f"b must be a list or numpy array, got {type(b).__name__}")
    if not isinstance(check_condition, bool):
        raise TypeError(
            f"check_condition must be a boolean, got {type(check_condition).__name__}"
        )
    if not isinstance(condition_threshold, (int, float)):
        raise TypeError(
            f"condition_threshold must be a number, got {type(condition_threshold).__name__}"
        )

    # Convert to numpy arrays
    try:
        A_arr = np.asarray(A, dtype=float)
        b_arr = np.asarray(b, dtype=float)
    except (ValueError, TypeError) as e:
        raise ValueError(f"arrays contain non-numeric values: {e}") from e

    # Validate dimensions
    if A_arr.ndim != 2:
        raise ValueError(f"A must be 2-dimensional, got {A_arr.ndim} dimensions")
    if A_arr.shape[0] != A_arr.shape[1]:
        raise ValueError(f"A must be square, got shape {A_arr.shape}")
    if b_arr.ndim != 1:
        raise ValueError(f"b must be 1-dimensional, got {b_arr.ndim} dimensions")
    if A_arr.shape[0] != b_arr.shape[0]:
        raise ValueError(
            f"incompatible dimensions: A is {A_arr.shape}, b is {b_arr.shape}"
        )

    # Check for NaN or Inf
    if np.any(~np.isfinite(A_arr)):
        raise ValueError("A contains NaN or Inf values")
    if np.any(~np.isfinite(b_arr)):
        raise ValueError("b contains NaN or Inf values")

    # Check condition number
    condition_number = None
    well_conditioned = True
    if check_condition:
        try:
            condition_number = float(np.linalg.cond(A_arr))
            well_conditioned = condition_number < condition_threshold
        except np.linalg.LinAlgError:
            well_conditioned = False

    # Solve the system
    try:
        solution = np.linalg.solve(A_arr, b_arr)
    except np.linalg.LinAlgError as e:
        raise ValueError(f"failed to solve system: {e}") from e

    # Calculate residual
    residual = A_arr @ solution - b_arr
    residual_norm = float(np.linalg.norm(residual))

    result: dict[str, np.ndarray | float | bool] = {
        "solution": solution,
        "residual_norm": residual_norm,
        "well_conditioned": well_conditioned,
    }

    if condition_number is not None:
        result["condition_number"] = condition_number

    return result


__all__ = ["solve_linear_system"]
