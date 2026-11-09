"""
Calculate moving statistics for timeseries data.
"""

import logging

import numpy as np
from numpy.typing import ArrayLike

logger = logging.getLogger(__name__)


def calculate_moving_statistics(
    data: ArrayLike,
    window_size: int,
    statistics: list[str] | None = None,
) -> dict[str, np.ndarray]:
    """
    Calculate moving statistics for timeseries data.

    Parameters
    ----------
    data : ArrayLike
        Input timeseries data.
    window_size : int
        Number of samples in a full rolling window. Even widths include the
        extra sample on the left of the current sample.
    statistics : list[str] | None, optional
        Statistics to calculate (by default ['mean', 'std']):
        - 'mean': Moving average
        - 'std': Moving standard deviation
        - 'min': Moving minimum
        - 'max': Moving maximum
        - 'median': Moving median

    Returns
    -------
    dict[str, np.ndarray]
        Dictionary mapping statistic names to arrays of values.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If window_size is invalid or statistics contains invalid values.

    Examples
    --------
    >>> data = [1, 2, 3, 4, 5, 6, 7, 8]
    >>> stats = calculate_moving_statistics(data, window_size=3)
    >>> 'mean' in stats and 'std' in stats
    True

    >>> stats = calculate_moving_statistics(data, 3, ['mean', 'min', 'max'])
    >>> len(stats)
    3

    Notes
    -----
    Uses centered windows where possible. Edge values use partial windows.
    For an even width, the current sample is the right of the two central
    samples. Standard deviation uses the population definition (``ddof=0``).

    Complexity
    ----------
    Time: O(n*w*k) where w=window, k=statistics, Space: O(n*k)
    """
    # Type validation
    if not isinstance(window_size, int):
        raise TypeError(
            f"window_size must be an integer, got {type(window_size).__name__}"
        )

    if statistics is not None and not isinstance(statistics, list):
        raise TypeError(
            f"statistics must be a list or None, got {type(statistics).__name__}"
        )

    # Convert to numpy array
    try:
        data_array = np.asarray(data, dtype=float)
    except (ValueError, TypeError) as e:
        raise TypeError(f"Cannot convert data to numeric array: {e}") from e

    if data_array.size == 0:
        raise ValueError("data cannot be empty")

    # Value validation
    if window_size < 1:
        raise ValueError(f"window_size must be positive, got {window_size}")

    if window_size > data_array.size:
        raise ValueError(
            f"window_size ({window_size}) cannot exceed data length ({data_array.size})"
        )

    # Default statistics
    if statistics is None:
        statistics = ["mean", "std"]

    valid_stats = ["mean", "std", "min", "max", "median"]
    for stat in statistics:
        if stat not in valid_stats:
            raise ValueError(
                f"Invalid statistic '{stat}', must be one of {valid_stats}"
            )

    logger.debug(
        f"Calculating moving statistics {statistics} with window_size={window_size}"
    )

    # Calculate statistics
    result = {}

    for stat in statistics:
        values = np.zeros_like(data_array)

        for i in range(len(data_array)):
            # Determine window bounds
            start = max(0, i - window_size // 2)
            end = min(len(data_array), i + (window_size - 1) // 2 + 1)

            window_data = data_array[start:end]

            # Calculate statistic
            if stat == "mean":
                values[i] = np.mean(window_data)
            elif stat == "std":
                values[i] = np.std(window_data)
            elif stat == "min":
                values[i] = np.min(window_data)
            elif stat == "max":
                values[i] = np.max(window_data)
            elif stat == "median":
                values[i] = np.median(window_data)

        result[stat] = values

    logger.debug(f"Calculated {len(statistics)} moving statistics")
    return result


__all__ = ["calculate_moving_statistics"]
