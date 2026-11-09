"""
Smooth timeseries data using various methods.
"""

import logging

import numpy as np
from numpy.typing import ArrayLike

logger = logging.getLogger(__name__)


def smooth_timeseries(
    data: ArrayLike,
    method: str = "moving_average",
    window_size: int = 5,
    polynomial_order: int = 2,
) -> np.ndarray:
    """
    Smooth timeseries data using various methods.

    Parameters
    ----------
    data : ArrayLike
        Input timeseries data.
    method : str, optional
        Smoothing method (by default 'moving_average'):
        - 'moving_average': Simple moving average
        - 'exponential': Exponential moving average
        - 'savgol': Savitzky-Golay filter (requires scipy)
    window_size : int, optional
        Window size for smoothing (by default 5). Moving-average windows must
        not exceed the number of samples.
    polynomial_order : int, optional
        Polynomial order for Savitzky-Golay filter (by default 2).

    Returns
    -------
    np.ndarray
        Smoothed timeseries data.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If method is invalid or window_size is inappropriate.

    Examples
    --------
    >>> data = [1, 5, 3, 8, 2, 9, 4, 7]
    >>> smoothed = smooth_timeseries(data, method='moving_average', window_size=3)
    >>> len(smoothed)
    8

    >>> smoothed = smooth_timeseries(data, method='exponential', window_size=3)
    >>> smoothed.shape
    (8,)

    Notes
    -----
    Moving averages use complete windows and retain original values at boundary
    positions without a complete window. Even widths place the extra sample on
    the left of the current sample. Output length matches input length.
    Exponential moving average uses alpha = 2 / (window_size + 1).

    Complexity
    ----------
    Time: O(n*w) for moving average, O(n) for exponential, Space: O(n)
    """
    # Type validation
    if not isinstance(method, str):
        raise TypeError(f"method must be a string, got {type(method).__name__}")
    if not isinstance(window_size, int):
        raise TypeError(
            f"window_size must be an integer, got {type(window_size).__name__}"
        )
    if not isinstance(polynomial_order, int):
        raise TypeError(
            f"polynomial_order must be an integer, got {type(polynomial_order).__name__}"
        )

    # Convert to numpy array
    try:
        data_array = np.asarray(data, dtype=float)
    except (ValueError, TypeError) as e:
        raise TypeError(f"Cannot convert data to numeric array: {e}") from e

    if data_array.size == 0:
        raise ValueError("data cannot be empty")

    # Validate parameters
    valid_methods = ["moving_average", "exponential", "savgol"]
    if method not in valid_methods:
        raise ValueError(f"method must be one of {valid_methods}, got '{method}'")

    if window_size < 1:
        raise ValueError(f"window_size must be positive, got {window_size}")

    if method == "moving_average" and window_size > data_array.size:
        raise ValueError(
            f"window_size ({window_size}) cannot exceed data length ({data_array.size})"
        )

    if method == "savgol" and window_size % 2 == 0:
        raise ValueError(
            f"window_size must be odd for savgol method, got {window_size}"
        )

    if method == "savgol" and polynomial_order >= window_size:
        raise ValueError(
            f"polynomial_order ({polynomial_order}) must be < window_size ({window_size})"
        )

    logger.debug(f"Smoothing {data_array.size} values with method='{method}'")

    if method == "moving_average":
        # Use convolution for moving average
        kernel = np.ones(window_size) / window_size
        smoothed = np.convolve(data_array, kernel, mode="same")

        # Retain originals only where no complete window fits.
        half_window = window_size // 2
        smoothed[:half_window] = data_array[:half_window]
        right_window = (window_size - 1) // 2
        if right_window:
            smoothed[-right_window:] = data_array[-right_window:]

    elif method == "exponential":
        # Exponential moving average
        alpha = 2.0 / (window_size + 1)
        smoothed = np.zeros_like(data_array)
        smoothed[0] = data_array[0]

        for i in range(1, len(data_array)):
            smoothed[i] = alpha * data_array[i] + (1 - alpha) * smoothed[i - 1]

    else:  # savgol
        try:
            from scipy.signal import savgol_filter
        except ImportError as e:
            raise ImportError(
                "Savitzky-Golay filter requires scipy: pip install scipy"
            ) from e

        smoothed = savgol_filter(data_array, window_size, polynomial_order)

    logger.debug(
        f"Smoothed timeseries: original_std={data_array.std():.3f}, "
        f"smoothed_std={smoothed.std():.3f}"
    )
    return smoothed


__all__ = ["smooth_timeseries"]
