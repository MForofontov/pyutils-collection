"""
Calculate comprehensive descriptive statistics with confidence intervals.

Uses numpy and scipy.stats for calculations, adds validation,
outlier detection, and comprehensive summary generation.
"""

import warnings
from typing import Any

import numpy as np
from scipy import stats


def comprehensive_stats(
    data: list[float] | np.ndarray,
    confidence_level: float = 0.95,
    include_distribution_tests: bool = True,
) -> dict[str, Any]:
    """
    Calculate comprehensive descriptive statistics with confidence intervals.

    Uses numpy and scipy.stats for calculations, adds validation,
    outlier detection, and comprehensive summary generation.

    Parameters
    ----------
    data : list[float] | np.ndarray
        Input data for statistical analysis.
    confidence_level : float, optional
        Confidence level for interval estimation (by default 0.95).
    include_distribution_tests : bool, optional
        Whether to include normality and distribution tests (by default True).

    Returns
    -------
    dict[str, Any]
        Dictionary containing comprehensive statistics including:
        - Central tendency: mean, median, mode
        - Dispersion: std, var, range, IQR
        - Shape: skewness, kurtosis
        - Confidence intervals
        - Outlier information
        - Distribution tests (if requested)

    Raises
    ------
    TypeError
        If data is not a list or numpy array.
    ValueError
        If data is empty or contains non-numeric values.
        If confidence_level is not between 0 and 1.

    Examples
    --------
    >>> data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    >>> stats_summary = comprehensive_stats(data)
    >>> stats_summary['mean']
    5.5
    >>> stats_summary['median']
    5.5

    Notes
    -----
    This function provides a complete statistical summary suitable
    for exploratory data analysis and reporting.

    Complexity
    ----------
    Time: O(n log n), Space: O(n)
    """
    # Input validation
    if not isinstance(data, (list, np.ndarray)):
        raise TypeError(
            f"data must be a list or numpy array, got {type(data).__name__}"
        )
    if not isinstance(confidence_level, (int, float)):
        raise TypeError(
            f"confidence_level must be a number, got {type(confidence_level).__name__}"
        )
    if not isinstance(include_distribution_tests, bool):
        raise TypeError(
            f"include_distribution_tests must be a boolean, got {type(include_distribution_tests).__name__}"
        )

    # Convert to numpy array
    try:
        arr = np.asarray(data, dtype=float)
    except (ValueError, TypeError) as e:
        raise ValueError(f"data contains non-numeric values: {e}") from e

    if arr.size == 0:
        raise ValueError("data cannot be empty")

    if not 0 < confidence_level < 1:
        raise ValueError(
            f"confidence_level must be between 0 and 1, got {confidence_level}"
        )

    # Remove NaN values with warning
    if np.isnan(arr).any():
        n_nan = np.isnan(arr).sum()
        warnings.warn(
            f"data contains {n_nan} NaN value(s), removing them",
            UserWarning,
            stacklevel=2,
        )
        arr = arr[~np.isnan(arr)]

    if arr.size == 0:
        raise ValueError("data contains only NaN values")

    # Calculate central tendency
    mean_val = float(np.mean(arr))
    median_val = float(np.median(arr))

    # Mode (using scipy.stats)
    mode_result = stats.mode(arr, keepdims=True)
    mode_val = float(mode_result.mode[0])
    mode_count = int(mode_result.count[0])

    # Calculate dispersion
    std_val = float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0
    var_val = float(np.var(arr, ddof=1)) if arr.size > 1 else 0.0
    min_val = float(np.min(arr))
    max_val = float(np.max(arr))
    range_val = max_val - min_val

    # Percentiles
    q1 = float(np.percentile(arr, 25))
    q3 = float(np.percentile(arr, 75))
    iqr = q3 - q1

    # Shape measures
    skewness = float(stats.skew(arr)) if arr.size > 2 else 0.0
    kurt = float(stats.kurtosis(arr)) if arr.size > 3 else 0.0

    # Confidence interval for mean
    if arr.size > 1 and std_val != 0:
        ci = stats.t.interval(
            confidence_level,
            df=arr.size - 1,
            loc=mean_val,
            scale=stats.sem(arr),
        )
        ci_lower = float(ci[0])
        ci_upper = float(ci[1])
    else:
        ci_lower = mean_val
        ci_upper = mean_val

    # Outlier detection (IQR method)
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = arr[(arr < lower_bound) | (arr > upper_bound)]
    n_outliers = len(outliers)

    # Build result dictionary
    result: dict[str, Any] = {
        "n": int(arr.size),
        "mean": mean_val,
        "median": median_val,
        "mode": mode_val,
        "mode_count": mode_count,
        "std": std_val,
        "variance": var_val,
        "min": min_val,
        "max": max_val,
        "range": range_val,
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "skewness": skewness,
        "kurtosis": kurt,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "confidence_level": confidence_level,
        "n_outliers": n_outliers,
        "outlier_percentage": (n_outliers / arr.size) * 100 if arr.size > 0 else 0.0,
    }

    # Distribution tests
    if include_distribution_tests and arr.size >= 3:
        # Shapiro-Wilk test for normality
        if arr.size >= 3:
            shapiro_stat, shapiro_p = stats.shapiro(arr)
            result["shapiro_statistic"] = float(shapiro_stat)
            result["shapiro_pvalue"] = float(shapiro_p)
            result["is_normal"] = shapiro_p > 0.05

        # Jarque-Bera test for normality
        if arr.size >= 2:
            jb_stat, jb_p = stats.jarque_bera(arr)
            result["jarque_bera_statistic"] = float(jb_stat)
            result["jarque_bera_pvalue"] = float(jb_p)

    return result


__all__ = ["comprehensive_stats"]
