"""
Create scatter plot with customizable styling.
"""

import logging
from contextlib import suppress

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)


def create_scatter_plot(
    x_data: list[float] | np.ndarray,
    y_data: list[float] | np.ndarray,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    colors: list[str] | str | None = None,
    sizes: list[float] | float = 50,
    alpha: float = 0.6,
    grid: bool = True,
    figsize: tuple[int, int] = (10, 6),
    marker: str = "o",
) -> tuple[Figure, Axes]:
    """
    Create a scatter plot with customizable styling.

    Parameters
    ----------
    x_data : list[float] | np.ndarray
        X-axis data points.
    y_data : list[float] | np.ndarray
        Y-axis data points.
    title : str, optional
        Plot title (by default "").
    xlabel : str, optional
        X-axis label (by default "").
    ylabel : str, optional
        Y-axis label (by default "").
    colors : list[str] | str | None, optional
        Point colors, can be single color or list (by default None).
    sizes : list[float] | float, optional
        Point sizes (by default 50).
    alpha : float, optional
        Transparency level between 0 and 1 (by default 0.6).
    grid : bool, optional
        Whether to show grid (by default True).
    figsize : tuple[int, int], optional
        Figure size as (width, height) in inches (by default (10, 6)).
    marker : str, optional
        Marker style (by default 'o').

    Returns
    -------
    tuple[Figure, Axes]
        Matplotlib figure and axes objects.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If data dimensions don't match or parameters are invalid.

    Examples
    --------
    >>> x = np.random.randn(100)
    >>> y = 2 * x + np.random.randn(100) * 0.5
    >>> fig, ax = create_scatter_plot(
    ...     x, y,
    ...     title="Correlation Plot",
    ...     xlabel="Feature X",
    ...     ylabel="Feature Y",
    ...     colors='blue',
    ...     alpha=0.5
    ... )
    >>> plt.show()

    Notes
    -----
    Returned figures belong to the caller. If plotting fails after figure
    creation, only the newly created figure is closed before propagating the
    original exception.

    This function provides a clean interface for creating scatter plots with
    automatic validation and sensible defaults.

    Complexity
    ----------
    Time: O(n), Space: O(n) where n is number of data points
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
    if not isinstance(alpha, (int, float)):
        raise TypeError(f"alpha must be a number, got {type(alpha).__name__}")
    if not isinstance(grid, bool):
        raise TypeError(f"grid must be a boolean, got {type(grid).__name__}")
    if not isinstance(figsize, tuple) or len(figsize) != 2:
        raise TypeError("figsize must be a tuple of two integers")
    if not isinstance(marker, str):
        raise TypeError(f"marker must be a string, got {type(marker).__name__}")

    # Convert to numpy arrays
    x_data = np.asarray(x_data)
    y_data = np.asarray(y_data)

    # Value validation
    if len(x_data) == 0:
        raise ValueError("x_data cannot be empty")
    if len(y_data) == 0:
        raise ValueError("y_data cannot be empty")
    if len(x_data) != len(y_data):
        raise ValueError(
            f"x_data length ({len(x_data)}) must match y_data length ({len(y_data)})"
        )
    if not 0 <= alpha <= 1:
        raise ValueError(f"alpha must be between 0 and 1, got {alpha}")
    if figsize[0] <= 0 or figsize[1] <= 0:
        raise ValueError(f"figsize dimensions must be positive, got {figsize}")

    # Create plot
    fig, ax = plt.subplots(figsize=figsize)
    try:
        ax.scatter(x_data, y_data, c=colors, s=sizes, alpha=alpha, marker=marker)

        # Customize plot
        if title:
            ax.set_title(title, fontsize=14, fontweight="bold")
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=12)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=12)

        if grid:
            ax.grid(True, alpha=0.3, linestyle="--")

        plt.tight_layout()

        logger.debug(f"Created scatter plot with {len(x_data)} data points")

        return fig, ax
    except BaseException:
        with suppress(Exception):
            plt.close(fig)
        raise


__all__ = ["create_scatter_plot"]
