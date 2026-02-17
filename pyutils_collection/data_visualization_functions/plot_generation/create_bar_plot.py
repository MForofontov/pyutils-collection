"""
Create bar plot with support for grouped and stacked bars.
"""

import logging
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)


def create_bar_plot(
    categories: list[str],
    values: list[float] | list[list[float]],
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    labels: list[str] | None = None,
    colors: list[str] | None = None,
    horizontal: bool = False,
    stacked: bool = False,
    grid: bool = True,
    legend: bool = True,
    figsize: tuple[int, int] = (10, 6),
) -> tuple[Figure, Axes]:
    """
    Create a bar plot with support for grouped and stacked bars.

    Parameters
    ----------
    categories : list[str]
        Category names for the x-axis (or y-axis if horizontal).
    values : list[float] | list[list[float]]
        Values for each category. Can be single series or multiple series.
    title : str, optional
        Plot title (by default "").
    xlabel : str, optional
        X-axis label (by default "").
    ylabel : str, optional
        Y-axis label (by default "").
    labels : list[str] | None, optional
        Legend labels for each series (by default None).
    colors : list[str] | None, optional
        Colors for each series (by default None).
    horizontal : bool, optional
        Whether to create horizontal bars (by default False).
    stacked : bool, optional
        Whether to stack bars (by default False).
    grid : bool, optional
        Whether to show grid (by default True).
    legend : bool, optional
        Whether to show legend (by default True).
    figsize : tuple[int, int], optional
        Figure size as (width, height) in inches (by default (10, 6)).

    Returns
    -------
    tuple[Figure, Axes]
        Matplotlib figure and axes objects.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If data dimensions don't match or are invalid.

    Examples
    --------
    >>> categories = ['Q1', 'Q2', 'Q3', 'Q4']
    >>> sales = [100, 150, 120, 180]
    >>> fig, ax = create_bar_plot(
    ...     categories, sales,
    ...     title="Quarterly Sales",
    ...     xlabel="Quarter",
    ...     ylabel="Sales ($K)"
    ... )
    >>> plt.show()

    >>> # Grouped bars
    >>> values = [[100, 150, 120, 180], [90, 140, 110, 170]]
    >>> fig, ax = create_bar_plot(
    ...     categories, values,
    ...     labels=["2023", "2024"],
    ...     title="Year-over-Year Comparison"
    ... )

    Notes
    -----
    Supports both single and multiple bar series with automatic positioning
    for grouped bars.

    Complexity
    ----------
    Time: O(n*m) where n is categories and m is number of series
    Space: O(n*m)
    """
    # Type validation
    if not isinstance(categories, list):
        raise TypeError(f"categories must be a list, got {type(categories).__name__}")
    if not isinstance(values, list):
        raise TypeError(f"values must be a list, got {type(values).__name__}")
    if not isinstance(title, str):
        raise TypeError(f"title must be a string, got {type(title).__name__}")
    if not isinstance(xlabel, str):
        raise TypeError(f"xlabel must be a string, got {type(xlabel).__name__}")
    if not isinstance(ylabel, str):
        raise TypeError(f"ylabel must be a string, got {type(ylabel).__name__}")
    if not isinstance(horizontal, bool):
        raise TypeError(
            f"horizontal must be a boolean, got {type(horizontal).__name__}"
        )
    if not isinstance(stacked, bool):
        raise TypeError(f"stacked must be a boolean, got {type(stacked).__name__}")
    if not isinstance(grid, bool):
        raise TypeError(f"grid must be a boolean, got {type(grid).__name__}")
    if not isinstance(legend, bool):
        raise TypeError(f"legend must be a boolean, got {type(legend).__name__}")
    if not isinstance(figsize, tuple) or len(figsize) != 2:
        raise TypeError("figsize must be a tuple of two integers")

    # Value validation
    if len(categories) == 0:
        raise ValueError("categories cannot be empty")
    if not all(isinstance(cat, str) for cat in categories):
        raise TypeError("All category items must be strings")
    if figsize[0] <= 0 or figsize[1] <= 0:
        raise ValueError(f"figsize dimensions must be positive, got {figsize}")

    # Handle multiple series
    value_series: list[list[float]]
    if len(values) > 0 and isinstance(values[0], list):
        value_series = [list(v) for v in values]  # type: ignore[arg-type]
    else:
        value_series = [values]  # type: ignore[list-item]

    # Validate dimensions
    for i, series in enumerate(value_series):
        if len(series) != len(categories):
            raise ValueError(
                f"values series {i} length ({len(series)}) must match categories length ({len(categories)})"
            )

    num_series = len(value_series)

    # Validate optional parameters
    if labels is not None:
        if not isinstance(labels, list):
            raise TypeError(f"labels must be a list, got {type(labels).__name__}")
        if len(labels) != num_series:
            raise ValueError(
                f"Number of labels ({len(labels)}) must match number of series ({num_series})"
            )

    if colors is not None:
        if not isinstance(colors, list):
            raise TypeError(f"colors must be a list, got {type(colors).__name__}")
        if len(colors) != num_series:
            raise ValueError(
                f"Number of colors ({len(colors)}) must match number of series ({num_series})"
            )

    # Create plot
    fig, ax = plt.subplots(figsize=figsize)

    x = np.arange(len(categories))
    width = 0.8 / num_series if not stacked else 0.8

    if stacked:
        # Stacked bars
        bottom = np.zeros(len(categories))
        for i, series in enumerate(value_series):
            kwargs: dict[str, Any] = {}
            if labels is not None:
                kwargs["label"] = labels[i]
            if colors is not None:
                kwargs["color"] = colors[i]

            if horizontal:
                # barh uses 'height' parameter instead of 'width'
                ax.barh(x, series, height=width, left=bottom, **kwargs)
            else:
                ax.bar(x, series, width=width, bottom=bottom, **kwargs)

            bottom += np.array(series)
    else:
        # Grouped bars
        for i, series in enumerate(value_series):
            offset = (i - num_series / 2 + 0.5) * width
            kwargs = {}
            if labels is not None:
                kwargs["label"] = labels[i]
            if colors is not None:
                kwargs["color"] = colors[i]

            if horizontal:
                # barh uses 'height' parameter instead of 'width'
                ax.barh(x + offset, series, height=width, **kwargs)
            else:
                ax.bar(x + offset, series, width=width, **kwargs)

    # Set ticks and labels
    if horizontal:
        ax.set_yticks(x)
        ax.set_yticklabels(categories)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=12)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=12)
        if grid:
            ax.grid(True, alpha=0.3, linestyle="--", axis="x")
    else:
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha="right")
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=12)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=12)
        if grid:
            ax.grid(True, alpha=0.3, linestyle="--", axis="y")

    if title:
        ax.set_title(title, fontsize=14, fontweight="bold")

    if legend and labels is not None:
        ax.legend(loc="best", framealpha=0.9)

    plt.tight_layout()

    logger.debug(
        f"Created bar plot with {len(categories)} categories and {num_series} series"
    )

    return fig, ax


__all__ = ["create_bar_plot"]
