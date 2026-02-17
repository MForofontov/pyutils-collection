"""
Aggregate data by group with various statistics.
"""

import logging
from collections.abc import Callable
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


def aggregate_by_group(
    data: list[float] | np.ndarray,
    groups: list[Any] | np.ndarray,
    agg_func: str | Callable[[np.ndarray], float] = "mean",
) -> dict[Any, float]:
    """
    Aggregate data by group with various statistics.

    Parameters
    ----------
    data : list[float] | np.ndarray
        Numeric data to aggregate.
    groups : list[Any] | np.ndarray
        Group labels for each data point.
    agg_func : str | Callable, optional
        Aggregation function (by default 'mean'):
        - 'mean': Average
        - 'sum': Sum
        - 'median': Median
        - 'min': Minimum
        - 'max': Maximum
        - 'std': Standard deviation
        - 'count': Count of values
        - Callable: Custom function

    Returns
    -------
    dict[Any, float]
        Mapping of group labels to aggregated values.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If data and groups have different lengths or agg_func is invalid.

    Examples
    --------
    >>> data = [1, 2, 3, 4, 5, 6]
    >>> groups = ['A', 'B', 'A', 'B', 'A', 'B']
    >>> aggregate_by_group(data, groups, 'sum')
    {'A': 9.0, 'B': 12.0}

    >>> aggregate_by_group(data, groups, 'mean')
    {'A': 3.0, 'B': 4.0}

    Notes
    -----
    For custom functions, the function should accept a numpy array and return a scalar.

    Complexity
    ----------
    Time: O(n), Space: O(k) where k is number of unique groups
    """
    # Convert to numpy arrays
    try:
        data_array = np.asarray(data, dtype=float)
    except (ValueError, TypeError) as e:
        raise TypeError(f"Cannot convert data to numeric array: {e}") from e

    try:
        groups_array = np.asarray(groups)
    except (ValueError, TypeError) as e:
        raise TypeError(f"Cannot convert groups to array: {e}") from e

    # Validation
    if data_array.size == 0:
        raise ValueError("data cannot be empty")
    if groups_array.size == 0:
        raise ValueError("groups cannot be empty")

    if data_array.size != groups_array.size:
        raise ValueError(
            f"data and groups must have same length: {data_array.size} != {groups_array.size}"
        )

    # Get aggregation function
    if isinstance(agg_func, str):
        agg_functions: dict[str, Callable[[np.ndarray], float]] = {
            "mean": lambda x: float(np.mean(x)),
            "sum": lambda x: float(np.sum(x)),
            "median": lambda x: float(np.median(x)),
            "min": lambda x: float(np.min(x)),
            "max": lambda x: float(np.max(x)),
            "std": lambda x: float(np.std(x)),
            "count": lambda x: float(len(x)),
        }

        if agg_func not in agg_functions:
            raise ValueError(
                f"agg_func must be one of {list(agg_functions.keys())}, got '{agg_func}'"
            )

        func = agg_functions[agg_func]
    elif callable(agg_func):
        func = agg_func
    else:
        raise TypeError(
            f"agg_func must be string or callable, got {type(agg_func).__name__}"
        )

    logger.debug(f"Aggregating {data_array.size} values by group using {agg_func}")

    # Group data and aggregate
    unique_groups = np.unique(groups_array)
    result = {}

    for group in unique_groups:
        mask = groups_array == group
        group_data = data_array[mask]
        aggregated_value = float(func(group_data))
        result[group] = aggregated_value

    logger.debug(f"Aggregated into {len(result)} groups")
    return result


__all__ = ["aggregate_by_group"]
