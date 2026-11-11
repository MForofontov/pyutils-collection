"""
Calculate correlation coefficients with significance testing.

Uses scipy.stats for correlation calculations, adds validation,
multiple correlation methods, and comprehensive output.
"""

from typing import Literal

import numpy as np
from scipy import stats


def correlation_analysis(
    x: list[float] | np.ndarray,
    y: list[float] | np.ndarray,
    method: Literal["pearson", "spearman", "kendall"] = "pearson",
    alpha: float = 0.05,
) -> dict[str, float | bool | str]:
    """
    Calculate correlation coefficient with significance testing.

    Uses scipy.stats for correlation calculations, adds validation,
    multiple methods, and interpretation.

    Parameters
    ----------
    x : list[float] | np.ndarray
        First variable.
    y : list[float] | np.ndarray
        Second variable.
    method : {'pearson', 'spearman', 'kendall'}, optional
        Correlation method (by default 'pearson').
    alpha : float, optional
        Significance level (by default 0.05).

    Returns
    -------
    dict[str, float | bool | str]
        Dictionary containing:
        - correlation: Correlation coefficient
        - pvalue: p-value
        - significant: Whether correlation is significant
        - interpretation: Strength interpretation
        - method: Method used

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If arrays have different lengths or are empty.

    Examples
    --------
    >>> x = [1, 2, 3, 4, 5]
    >>> y = [2, 4, 5, 4, 5]
    >>> result = correlation_analysis(x, y, method='pearson')
    >>> result['correlation'] > 0
    True

    Notes
    -----
    Correlation strength interpretation:
    - 0.0-0.3: Weak
    - 0.3-0.7: Moderate
    - 0.7-1.0: Strong

    Complexity
    ----------
    Time: O(n), Space: O(1)
    """
    # Input validation
    if not isinstance(x, (list, np.ndarray)):
        raise TypeError(f"x must be a list or numpy array, got {type(x).__name__}")
    if not isinstance(y, (list, np.ndarray)):
        raise TypeError(f"y must be a list or numpy array, got {type(y).__name__}")
    if not isinstance(method, str):
        raise TypeError(f"method must be a string, got {type(method).__name__}")
    if method not in ("pearson", "spearman", "kendall"):
        raise ValueError(
            f"method must be 'pearson', 'spearman', or 'kendall', got '{method}'"
        )
    if not isinstance(alpha, (int, float)):
        raise TypeError(f"alpha must be a number, got {type(alpha).__name__}")
    if not 0 < alpha < 1:
        raise ValueError(f"alpha must be between 0 and 1, got {alpha}")

    # Convert to numpy arrays
    try:
        arr_x = np.asarray(x, dtype=float)
        arr_y = np.asarray(y, dtype=float)
    except (ValueError, TypeError) as e:
        raise ValueError(f"arrays contain non-numeric values: {e}") from e

    if arr_x.size == 0:
        raise ValueError("x cannot be empty")
    if arr_y.size == 0:
        raise ValueError("y cannot be empty")
    if arr_x.size != arr_y.size:
        raise ValueError(
            f"x and y must have the same length, got {arr_x.size} and {arr_y.size}"
        )

    # Remove NaN values pairwise
    mask = ~(np.isnan(arr_x) | np.isnan(arr_y))
    arr_x = arr_x[mask]
    arr_y = arr_y[mask]

    if arr_x.size < 3:
        raise ValueError("need at least 3 observations after removing NaN values")

    # Calculate correlation
    if method == "pearson":
        corr, p_value = stats.pearsonr(arr_x, arr_y)
    elif method == "spearman":
        corr, p_value = stats.spearmanr(arr_x, arr_y)
    elif method == "kendall":
        corr, p_value = stats.kendalltau(arr_x, arr_y)
    else:
        raise ValueError(f"Unknown method: {method}")

    # Interpret correlation strength
    abs_corr = abs(corr)
    if abs_corr < 0.3:
        interpretation = "weak"
    elif abs_corr < 0.7:
        interpretation = "moderate"
    else:
        interpretation = "strong"

    return {
        "correlation": float(corr),
        "pvalue": float(p_value),
        "significant": p_value < alpha,
        "interpretation": interpretation,
        "method": method,
        "n_observations": int(arr_x.size),
        "alpha": alpha,
    }


__all__ = ["correlation_analysis"]
