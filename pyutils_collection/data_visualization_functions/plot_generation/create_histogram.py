"""
Create histogram with support for multiple distributions.
"""

import logging
from contextlib import suppress
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)


def create_histogram(
    data: list[float] | np.ndarray | list[list[float]] | list[np.ndarray],
    bins: int | str = "auto",
    title: str = "",
    xlabel: str = "",
    ylabel: str = "Frequency",
    labels: list[str] | None = None,
    colors: list[str] | None = None,
    alpha: float = 0.7,
    density: bool = False,
    cumulative: bool = False,
    grid: bool = True,
    legend: bool = True,
    figsize: tuple[int, int] = (10, 6),
) -> tuple[Figure, Axes]:
    """
    Create a histogram with support for multiple distributions.

    Parameters
    ----------
    data : list[float] | np.ndarray | list[list[float]] | list[np.ndarray]
        Data to plot. Can be single dataset or multiple datasets.
    bins : int | str, optional
        Number of bins or binning strategy ('auto', 'sturges', 'scott', etc.) (by default 'auto').
    title : str, optional
        Plot title (by default "").
    xlabel : str, optional
        X-axis label (by default "").
    ylabel : str, optional
        Y-axis label (by default "Frequency").
    labels : list[str] | None, optional
        Legend labels for each dataset (by default None).
    colors : list[str] | None, optional
        Colors for each dataset (by default None).
    alpha : float, optional
        Transparency level between 0 and 1 (by default 0.7).
    density : bool, optional
        Whether to normalize to create a probability density (by default False).
    cumulative : bool, optional
        Whether to create cumulative histogram (by default False).
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
        If data is empty or parameters are invalid.

    Examples
    --------
    >>> data = np.random.randn(1000)
    >>> fig, ax = create_histogram(
    ...     data,
    ...     bins=30,
    ...     title="Normal Distribution",
    ...     xlabel="Value",
    ...     alpha=0.8
    ... )
    >>> plt.show()

    >>> # Multiple distributions
    >>> data1 = np.random.randn(1000)
    >>> data2 = np.random.randn(1000) + 2
    >>> fig, ax = create_histogram(
    ...     [data1, data2],
    ...     labels=["Group A", "Group B"],
    ...     alpha=0.6
    ... )

    Notes
    -----
    Returned figures belong to the caller. If plotting fails after figure
    creation, only the newly created figure is closed before propagating the
    original exception.

    Automatically handles multiple distributions with proper overlap visualization.

    Complexity
    ----------
    Time: O(n*log(n)) for binning, Space: O(n) where n is data size
    """
    # Type validation
    if not isinstance(data, (list, np.ndarray)):
        raise TypeError(
            f"data must be a list or numpy array, got {type(data).__name__}"
        )
    if not isinstance(bins, (int, str)):
        raise TypeError(f"bins must be an integer or string, got {type(bins).__name__}")
    if not isinstance(title, str):
        raise TypeError(f"title must be a string, got {type(title).__name__}")
    if not isinstance(xlabel, str):
        raise TypeError(f"xlabel must be a string, got {type(xlabel).__name__}")
    if not isinstance(ylabel, str):
        raise TypeError(f"ylabel must be a string, got {type(ylabel).__name__}")
    if not isinstance(alpha, (int, float)):
        raise TypeError(f"alpha must be a number, got {type(alpha).__name__}")
    if not isinstance(density, bool):
        raise TypeError(f"density must be a boolean, got {type(density).__name__}")
    if not isinstance(cumulative, bool):
        raise TypeError(
            f"cumulative must be a boolean, got {type(cumulative).__name__}"
        )
    if not isinstance(grid, bool):
        raise TypeError(f"grid must be a boolean, got {type(grid).__name__}")
    if not isinstance(legend, bool):
        raise TypeError(f"legend must be a boolean, got {type(legend).__name__}")
    if not isinstance(figsize, tuple) or len(figsize) != 2:
        raise TypeError("figsize must be a tuple of two integers")

    # Value validation
    if isinstance(bins, int) and bins <= 0:
        raise ValueError(f"bins must be positive, got {bins}")
    if not 0 <= alpha <= 1:
        raise ValueError(f"alpha must be between 0 and 1, got {alpha}")
    if figsize[0] <= 0 or figsize[1] <= 0:
        raise ValueError(f"figsize dimensions must be positive, got {figsize}")

    # Handle multiple datasets
    if isinstance(data, np.ndarray) and data.ndim == 1:
        datasets = [data]
    elif isinstance(data, list) and len(data) > 0:
        if isinstance(data[0], (list, np.ndarray)):
            datasets = [np.asarray(d) for d in data]
        else:
            datasets = [np.asarray(data)]
    else:
        datasets = [np.asarray(data)]

    # Validate datasets
    for i, dataset in enumerate(datasets):
        if len(dataset) == 0:
            raise ValueError(f"dataset {i} cannot be empty")

    num_datasets = len(datasets)

    # Validate optional parameters
    if labels is not None:
        if not isinstance(labels, list):
            raise TypeError(f"labels must be a list, got {type(labels).__name__}")
        if len(labels) != num_datasets:
            raise ValueError(
                f"Number of labels ({len(labels)}) must match number of datasets ({num_datasets})"
            )

    if colors is not None:
        if not isinstance(colors, list):
            raise TypeError(f"colors must be a list, got {type(colors).__name__}")
        if len(colors) != num_datasets:
            raise ValueError(
                f"Number of colors ({len(colors)}) must match number of datasets ({num_datasets})"
            )

    # Create plot
    fig, ax = plt.subplots(figsize=figsize)
    try:
        for i, dataset in enumerate(datasets):
            hist_kwargs: dict[str, Any] = {
                "bins": bins,
                "alpha": alpha,
                "density": density,
                "cumulative": cumulative,
            }

            if labels is not None:
                hist_kwargs["label"] = labels[i]
            if colors is not None:
                hist_kwargs["color"] = colors[i]

            ax.hist(dataset, **hist_kwargs)

        # Customize plot
        if title:
            ax.set_title(title, fontsize=14, fontweight="bold")
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=12)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=12)

        if grid:
            ax.grid(True, alpha=0.3, linestyle="--", axis="y")

        if legend and labels is not None:
            ax.legend(loc="best", framealpha=0.9)

        plt.tight_layout()

        total_points = sum(len(d) for d in datasets)
        logger.debug(
            f"Created histogram with {num_datasets} datasets and {total_points} total data points"
        )

        return fig, ax
    except BaseException:
        with suppress(Exception):
            plt.close(fig)
        raise


__all__ = ["create_histogram"]
