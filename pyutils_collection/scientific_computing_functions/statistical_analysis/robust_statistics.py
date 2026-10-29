"""
Calculate robust statistics resistant to outliers.

Uses scipy.stats for robust measures, adds validation and
comprehensive robust summary generation.
"""

import warnings

import numpy as np
from scipy import stats


def robust_statistics(
    data: list[float] | np.ndarray,
) -> dict[str, float]:
    """
    Calculate robust statistics resistant to outliers.

    Uses scipy.stats for robust measures, adds validation and
    comprehensive robust summary generation.

    Parameters
    ----------
    data : list[float] | np.ndarray
        Input data for robust statistical analysis.

    Returns
    -------
    dict[str, float]
        Dictionary containing robust statistics:
        - median: Median value
        - mad: Median absolute deviation
        - trimmed_mean: Mean after trimming outliers
        - winsorized_mean: Mean after winsorizing outliers
        - iqr: Interquartile range

    Raises
    ------
    TypeError
        If data is not a one-dimensional list or numpy array.
    ValueError
        If data is empty or contains non-numeric values.

    Examples
    --------
    >>> data = [1, 2, 3, 4, 5, 100]  # 100 is an outlier
    >>> robust = robust_statistics(data)
    >>> robust['median']
    3.5
    >>> robust['trimmed_mean']  # Less affected by outlier
    3.0

    Notes
    -----
    Robust statistics are less sensitive to outliers and extreme values
    compared to traditional measures like mean and standard deviation.

    Complexity
    ----------
    Time: O(n log n), Space: O(n)
    """
    # Input validation
    if not isinstance(data, (list, np.ndarray)):
        raise TypeError(
            f"data must be a list or numpy array, got {type(data).__name__}"
        )

    # Convert to numpy array
    try:
        arr = np.asarray(data, dtype=float)
    except (ValueError, TypeError) as e:
        raise ValueError(f"data contains non-numeric values: {e}") from e

    if arr.size == 0:
        raise ValueError("data cannot be empty")

    if arr.ndim != 1:
        raise TypeError("data must be one-dimensional")

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

    # Median
    median_val = float(np.median(arr))

    # Median Absolute Deviation (MAD)
    mad = float(np.median(np.abs(arr - median_val)))

    # Trimmed mean (trim 10% from each tail)
    trimmed_mean = float(stats.trim_mean(arr, 0.1))

    # Winsorized mean (winsorize 5% from each tail)
    winsorized = stats.mstats.winsorize(arr, limits=[0.05, 0.05])
    winsorized_mean = float(np.mean(winsorized))

    # IQR
    q1 = float(np.percentile(arr, 25))
    q3 = float(np.percentile(arr, 75))
    iqr = q3 - q1

    return {
        "median": median_val,
        "mad": mad,
        "trimmed_mean": trimmed_mean,
        "winsorized_mean": winsorized_mean,
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
    }


__all__ = ["robust_statistics"]
