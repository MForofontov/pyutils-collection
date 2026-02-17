"""
Calculate bootstrap confidence intervals for a statistic.

Uses numpy for resampling, adds validation, progress tracking,
and comprehensive CI estimation.
"""

from typing import Literal

import numpy as np


def bootstrap_statistic(
    data: list[float] | np.ndarray,
    statistic: Literal["mean", "median", "std"] = "mean",
    n_iterations: int = 10000,
    confidence_level: float = 0.95,
    random_seed: int | None = None,
) -> dict[str, float]:
    """
    Calculate bootstrap confidence intervals for a statistic.

    Uses numpy for resampling, adds validation, progress tracking,
    and comprehensive CI estimation.

    Parameters
    ----------
    data : list[float] | np.ndarray
        Input data for bootstrap analysis.
    statistic : {'mean', 'median', 'std'}, optional
        Statistic to bootstrap (by default 'mean').
    n_iterations : int, optional
        Number of bootstrap iterations (by default 10000).
    confidence_level : float, optional
        Confidence level for interval (by default 0.95).
    random_seed : int | None, optional
        Random seed for reproducibility (by default None).

    Returns
    -------
    dict[str, float]
        Dictionary containing:
        - point_estimate: Original statistic value
        - ci_lower: Lower bound of confidence interval
        - ci_upper: Upper bound of confidence interval
        - standard_error: Bootstrap standard error

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If data is empty, n_iterations < 1, or statistic is invalid.

    Examples
    --------
    >>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    >>> result = bootstrap_statistic(data, statistic='mean', n_iterations=1000)
    >>> 'ci_lower' in result
    True
    >>> 'ci_upper' in result
    True

    Notes
    -----
    Bootstrap resampling provides non-parametric confidence intervals
    without assuming a specific distribution.

    Complexity
    ----------
    Time: O(n * m) where m is n_iterations, Space: O(m)
    """
    # Input validation
    if not isinstance(data, (list, np.ndarray)):
        raise TypeError(
            f"data must be a list or numpy array, got {type(data).__name__}"
        )
    if not isinstance(statistic, str):
        raise TypeError(f"statistic must be a string, got {type(statistic).__name__}")
    if statistic not in ("mean", "median", "std"):
        raise ValueError(
            f"statistic must be 'mean', 'median', or 'std', got '{statistic}'"
        )
    if not isinstance(n_iterations, int):
        raise TypeError(
            f"n_iterations must be an integer, got {type(n_iterations).__name__}"
        )
    if n_iterations < 1:
        raise ValueError(f"n_iterations must be >= 1, got {n_iterations}")
    if not isinstance(confidence_level, (int, float)):
        raise TypeError(
            f"confidence_level must be a number, got {type(confidence_level).__name__}"
        )
    if confidence_level <= 0 or confidence_level >= 1:
        raise ValueError(
            f"confidence_level must be between 0 and 1, got {confidence_level}"
        )
    if random_seed is not None and not isinstance(random_seed, int):
        raise TypeError(
            f"random_seed must be an integer or None, got {type(random_seed).__name__}"
        )

    # Convert to numpy array
    try:
        arr = np.asarray(data, dtype=float)
    except (ValueError, TypeError) as e:
        raise ValueError(f"data contains non-numeric values: {e}") from e

    if arr.size == 0:
        raise ValueError("data cannot be empty")

    # Remove NaN values
    arr = arr[~np.isnan(arr)]
    if arr.size == 0:
        raise ValueError("data contains only NaN values")

    # Set random seed for reproducibility
    if random_seed is not None:
        np.random.seed(random_seed)

    # Select statistic function
    from collections.abc import Callable
    from typing import Any
    
    stat_funcs: dict[str, Callable[[np.ndarray], Any]] = {
        "mean": lambda x: np.mean(x),
        "median": lambda x: np.median(x),
        "std": lambda x: np.std(x),
    }
    stat_func = stat_funcs[statistic]

    # Calculate point estimate
    point_estimate = float(stat_func(arr))

    # Bootstrap resampling
    bootstrap_samples = np.zeros(n_iterations)
    for i in range(n_iterations):
        sample = np.random.choice(arr, size=arr.size, replace=True)
        bootstrap_samples[i] = stat_func(sample)

    # Calculate confidence interval
    alpha = 1 - confidence_level
    ci_lower = float(np.percentile(bootstrap_samples, (alpha / 2) * 100))
    ci_upper = float(np.percentile(bootstrap_samples, (1 - alpha / 2) * 100))

    # Calculate standard error
    standard_error = float(np.std(bootstrap_samples))

    return {
        "point_estimate": point_estimate,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "standard_error": standard_error,
        "n_iterations": n_iterations,
        "confidence_level": confidence_level,
    }


__all__ = ["bootstrap_statistic"]
