"""
Normalize data to a specified range.
"""

import logging

import numpy as np
from numpy.typing import ArrayLike

logger = logging.getLogger(__name__)


def normalize_data(
    data: ArrayLike,
    method: str = "minmax",
    feature_range: tuple[float, float] = (0.0, 1.0),
) -> np.ndarray:
    """
    Normalize data to a specified range.

    Parameters
    ----------
    data : ArrayLike
        Input data to normalize.
    method : str, optional
        Normalization method (by default 'minmax'):
        - 'minmax': Scale to feature_range
        - 'zscore': Standardize to mean=0, std=1
        - 'robust': Scale using median and IQR
    feature_range : tuple[float, float], optional
        Target range for minmax scaling (by default (0.0, 1.0)).

    Returns
    -------
    np.ndarray
        Normalized data.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If method is invalid or data is constant.

    Examples
    --------
    >>> data = [1, 2, 3, 4, 5]
    >>> normalize_data(data)
    array([0.  , 0.25, 0.5 , 0.75, 1.  ])

    >>> normalize_data(data, method='zscore')
    array([-1.41421356, -0.70710678,  0.        ,  0.70710678,  1.41421356])

    Notes
    -----
    MinMax scaling: X' = (X - X_min) / (X_max - X_min) * (max - min) + min
    Z-score: X' = (X - mean) / std
    Robust: X' = (X - median) / IQR

    Complexity
    ----------
    Time: O(n), Space: O(n)
    """
    # Type validation
    if not isinstance(method, str):
        raise TypeError(f"method must be a string, got {type(method).__name__}")
    if not isinstance(feature_range, tuple) or len(feature_range) != 2:
        raise TypeError("feature_range must be a tuple of two floats")

    # Convert to numpy array
    try:
        data_array = np.asarray(data, dtype=float)
    except (ValueError, TypeError) as e:
        raise TypeError(f"Cannot convert data to numeric array: {e}") from e

    if data_array.size == 0:
        raise ValueError("data cannot be empty")

    # Value validation
    valid_methods = ["minmax", "zscore", "robust"]
    if method not in valid_methods:
        raise ValueError(f"method must be one of {valid_methods}, got '{method}'")

    min_val, max_val = feature_range
    if not isinstance(min_val, (int, float)) or not isinstance(max_val, (int, float)):
        raise TypeError("feature_range values must be numeric")
    if min_val >= max_val:
        raise ValueError(f"feature_range min must be < max, got {feature_range}")

    logger.debug(f"Normalizing data with method='{method}'")

    if method == "minmax":
        data_min = np.min(data_array)
        data_max = np.max(data_array)

        if data_min == data_max:
            raise ValueError("Cannot normalize constant data with minmax method")

        # Scale to [0, 1] then to feature_range
        normalized = (data_array - data_min) / (data_max - data_min)
        normalized = normalized * (max_val - min_val) + min_val

    elif method == "zscore":
        mean = np.mean(data_array)
        std = np.std(data_array)

        if std == 0:
            raise ValueError("Cannot normalize constant data with zscore method")

        normalized = (data_array - mean) / std

    else:  # robust
        median = np.median(data_array)
        q75, q25 = np.percentile(data_array, [75, 25])
        iqr = q75 - q25

        if iqr == 0:
            raise ValueError("Cannot normalize constant data with robust method")

        normalized = (data_array - median) / iqr

    logger.debug(f"Normalized {data_array.size} values")
    return np.asarray(normalized)


__all__ = ["normalize_data"]
