"""
Pivot data for heatmap visualization.
"""

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


def pivot_for_heatmap(
    data: list[float] | np.ndarray,
    row_labels: list[Any] | np.ndarray,
    col_labels: list[Any] | np.ndarray,
    agg_func: str = "mean",
) -> tuple[np.ndarray, list[Any], list[Any]]:
    """
    Pivot data for heatmap visualization.

    Parameters
    ----------
    data : list[float] | np.ndarray
        Numeric values to aggregate.
    row_labels : list[Any] | np.ndarray
        Row category labels for each data point.
    col_labels : list[Any] | np.ndarray
        Column category labels for each data point.
    agg_func : str, optional
        Aggregation function for duplicate entries (by default 'mean'):
        - 'mean': Average
        - 'sum': Sum
        - 'median': Median
        - 'min': Minimum
        - 'max': Maximum
        - 'count': Count

    Returns
    -------
    tuple[np.ndarray, list[Any], list[Any]]
        Tuple of (matrix, row_labels, col_labels):
        - matrix: 2D array for heatmap
        - row_labels: Sorted unique row labels
        - col_labels: Sorted unique column labels

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If arrays have different lengths or agg_func is invalid.

    Examples
    --------
    >>> data = [10, 20, 30, 40]
    >>> rows = ['A', 'A', 'B', 'B']
    >>> cols = ['X', 'Y', 'X', 'Y']
    >>> matrix, row_labels, col_labels = pivot_for_heatmap(data, rows, cols, 'sum')
    >>> matrix
    array([[10., 20.],
           [30., 40.]])

    Notes
    -----
    Missing combinations are filled with NaN.
    Rows and columns are sorted alphabetically.

    Complexity
    ----------
    Time: O(n + r*c) where r=rows, c=cols, Space: O(r*c)
    """
    # Convert to numpy arrays
    try:
        data_array = np.asarray(data, dtype=float)
    except (ValueError, TypeError) as e:
        raise TypeError(f"Cannot convert data to numeric array: {e}") from e

    try:
        row_array = np.asarray(row_labels)
        col_array = np.asarray(col_labels)
    except (ValueError, TypeError) as e:
        raise TypeError(f"Cannot convert labels to array: {e}") from e

    # Validation
    if data_array.size == 0:
        raise ValueError("data cannot be empty")
    if row_array.size == 0:
        raise ValueError("row_labels cannot be empty")
    if col_array.size == 0:
        raise ValueError("col_labels cannot be empty")

    if not (data_array.size == row_array.size == col_array.size):
        raise ValueError(
            f"data, row_labels, and col_labels must have same length: "
            f"{data_array.size}, {row_array.size}, {col_array.size}"
        )

    # Validate aggregation function
    valid_funcs = ["mean", "sum", "median", "min", "max", "count"]
    if agg_func not in valid_funcs:
        raise ValueError(f"agg_func must be one of {valid_funcs}, got '{agg_func}'")

    logger.debug(f"Pivoting {data_array.size} values with agg_func='{agg_func}'")

    # Get unique labels (sorted)
    unique_rows = sorted(set(row_array))
    unique_cols = sorted(set(col_array))

    # Create mapping from labels to indices
    row_to_idx = {label: i for i, label in enumerate(unique_rows)}
    col_to_idx = {label: i for i, label in enumerate(unique_cols)}

    # Initialize matrix with NaN
    matrix = np.full((len(unique_rows), len(unique_cols)), np.nan)

    # Aggregate data into cells
    from collections import defaultdict

    cell_values = defaultdict(list)

    for value, row, col in zip(data_array, row_array, col_array, strict=False):
        cell_values[(row, col)].append(value)

    # Apply aggregation function
    from collections.abc import Callable
    agg_functions: dict[str, Callable[[list[float]], float]] = {
        "mean": lambda x: float(np.mean(x)),
        "sum": lambda x: float(np.sum(x)),
        "median": lambda x: float(np.median(x)),
        "min": lambda x: float(np.min(x)),
        "max": lambda x: float(np.max(x)),
        "count": lambda x: float(len(x)),
    }
    func = agg_functions[agg_func]

    for (row, col), values in cell_values.items():
        i = row_to_idx[row]
        j = col_to_idx[col]
        matrix[i, j] = func(values)

    logger.debug(f"Created {len(unique_rows)}x{len(unique_cols)} heatmap matrix")
    return matrix, unique_rows, unique_cols


__all__ = ["pivot_for_heatmap"]
