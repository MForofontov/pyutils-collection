"""
Create line plot with multiple series and comprehensive customization.
"""

import logging
from contextlib import suppress
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)


def create_line_plot(
    x_data: list[float] | np.ndarray,
    y_data: list[float] | np.ndarray | list[list[float]] | list[np.ndarray],
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    labels: list[str] | None = None,
    colors: list[str] | None = None,
    line_styles: list[str] | None = None,
    markers: list[str] | None = None,
    grid: bool = True,
    legend: bool = True,
    figsize: tuple[int, int] = (10, 6),
) -> tuple[Figure, Axes]:
    """
    Create a line plot with multiple series and comprehensive customization.

    Parameters
    ----------
    x_data : list[float] | np.ndarray
        X-axis data points.
    y_data : list[float] | np.ndarray | list[list[float]] | list[np.ndarray]
        Y-axis data points. Can be a single series or multiple series.
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
    line_styles : list[str] | None, optional
        Line styles for each series, e.g., '-', '--', '-.', ':' (by default None).
    markers : list[str] | None, optional
        Markers for each series, e.g., 'o', 's', '^' (by default None).
    grid : bool, optional
        Whether to show grid (by default True).
    legend : bool, optional
        Whether to show legend (by default True).
    figsize : tuple[int, int], optional
        Figure size as (width, height) in inches (by default (10, 6)).

    Returns
    -------
    tuple[Figure, Axes]
        Matplotlib figure and axes objects for further customization.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If data dimensions don't match or are invalid.

    Examples
    --------
    >>> x = [1, 2, 3, 4, 5]
    >>> y1 = [1, 4, 2, 3, 5]
    >>> y2 = [2, 3, 4, 5, 6]
    >>> fig, ax = create_line_plot(
    ...     x, [y1, y2],
    ...     title="Sales Data",
    ...     xlabel="Month",
    ...     ylabel="Revenue ($)",
    ...     labels=["Product A", "Product B"]
    ... )
    >>> plt.show()

    Notes
    -----
    Returned figures belong to the caller. If plotting fails after figure
    creation, only the newly created figure is closed before propagating the
    original exception.

    This function provides a convenient wrapper around matplotlib with sensible
    defaults and automatic handling of multiple series.

    Complexity
    ----------
    Time: O(n*m) where n is data points and m is number of series
    Space: O(n*m)
    """
    # Type validation
    if not isinstance(x_data, (list, np.ndarray)):
        raise TypeError(
            f"x_data must be a list or numpy array, got {type(x_data).__name__}"
        )
    if not isinstance(y_data, (list, np.ndarray)):
        raise TypeError(
            f"y_data must be a list or numpy array, got {type(y_data).__name__}"
        )
    if not isinstance(title, str):
        raise TypeError(f"title must be a string, got {type(title).__name__}")
    if not isinstance(xlabel, str):
        raise TypeError(f"xlabel must be a string, got {type(xlabel).__name__}")
    if not isinstance(ylabel, str):
        raise TypeError(f"ylabel must be a string, got {type(ylabel).__name__}")
    if not isinstance(grid, bool):
        raise TypeError(f"grid must be a boolean, got {type(grid).__name__}")
    if not isinstance(legend, bool):
        raise TypeError(f"legend must be a boolean, got {type(legend).__name__}")
    if not isinstance(figsize, tuple) or len(figsize) != 2:
        raise TypeError("figsize must be a tuple of two integers")

    # Convert to numpy arrays
    x_data = np.asarray(x_data)

    # Value validation
    if len(x_data) == 0:
        raise ValueError("x_data cannot be empty")

    if figsize[0] <= 0 or figsize[1] <= 0:
        raise ValueError(f"figsize dimensions must be positive, got {figsize}")

    # Handle multiple series
    if isinstance(y_data, np.ndarray) and y_data.ndim == 1:
        y_series = [y_data]
    elif isinstance(y_data, list) and len(y_data) > 0:
        if isinstance(y_data[0], (list, np.ndarray)):
            y_series = [np.asarray(y) for y in y_data]
        else:
            y_series = [np.asarray(y_data)]
    else:
        y_series = [np.asarray(y_data)]

    # Validate dimensions
    for i, y in enumerate(y_series):
        if len(y) != len(x_data):
            raise ValueError(
                f"y_data series {i} length ({len(y)}) must match x_data length ({len(x_data)})"
            )

    num_series = len(y_series)

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

    if line_styles is not None:
        if not isinstance(line_styles, list):
            raise TypeError(
                f"line_styles must be a list, got {type(line_styles).__name__}"
            )
        if len(line_styles) != num_series:
            raise ValueError(
                f"Number of line_styles ({len(line_styles)}) must match number of series ({num_series})"
            )

    if markers is not None:
        if not isinstance(markers, list):
            raise TypeError(f"markers must be a list, got {type(markers).__name__}")
        if len(markers) != num_series:
            raise ValueError(
                f"Number of markers ({len(markers)}) must match number of series ({num_series})"
            )

    # Create plot
    fig, ax = plt.subplots(figsize=figsize)
    try:
        for i, y in enumerate(y_series):
            plot_kwargs: dict[str, Any] = {}

            if labels is not None:
                plot_kwargs["label"] = labels[i]
            if colors is not None:
                plot_kwargs["color"] = colors[i]
            if line_styles is not None:
                plot_kwargs["linestyle"] = line_styles[i]
            if markers is not None:
                plot_kwargs["marker"] = markers[i]

            ax.plot(x_data, y, **plot_kwargs)

        # Customize plot
        if title:
            ax.set_title(title, fontsize=14, fontweight="bold")
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=12)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=12)

        if grid:
            ax.grid(True, alpha=0.3, linestyle="--")

        if legend and labels is not None:
            ax.legend(loc="best", framealpha=0.9)

        plt.tight_layout()

        logger.debug(
            f"Created line plot with {num_series} series and {len(x_data)} data points"
        )

        return fig, ax
    except BaseException:
        with suppress(Exception):
            plt.close(fig)
        raise


__all__ = ["create_line_plot"]
