"""
Configure axes styling with comprehensive options.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def configure_axes_style(
    ax: Any,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    title_fontsize: int | None = None,
    label_fontsize: int | None = None,
    grid: bool = True,
    grid_style: str = "--",
    grid_alpha: float = 0.3,
    spine_visibility: dict[str, bool] | None = None,
) -> None:
    """
    Configure axes styling with comprehensive options.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes object to configure.
    title : str, optional
        Title for the axes (by default "").
    xlabel : str, optional
        Label for x-axis (by default "").
    ylabel : str, optional
        Label for y-axis (by default "").
    title_fontsize : int | None, optional
        Font size for title (by default None, uses current setting).
    label_fontsize : int | None, optional
        Font size for labels (by default None, uses current setting).
    grid : bool, optional
        Whether to show grid (by default True).
    grid_style : str, optional
        Grid line style (by default '--').
    grid_alpha : float, optional
        Grid transparency (by default 0.3).
    spine_visibility : dict[str, bool] | None, optional
        Dictionary controlling spine visibility, e.g., {'top': False, 'right': False}
        (by default None).

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values.

    Examples
    --------
    >>> fig, ax = plt.subplots()
    >>> ax.plot([1, 2, 3], [1, 4, 2])
    >>> configure_axes_style(
    ...     ax,
    ...     title="Sample Plot",
    ...     xlabel="X Axis",
    ...     ylabel="Y Axis",
    ...     spine_visibility={'top': False, 'right': False}
    ... )

    Notes
    -----
    This function provides fine-grained control over axes appearance,
    commonly used for publication-quality figures.

    Complexity
    ----------
    Time: O(1), Space: O(1)
    """
    # Type validation
    if not isinstance(title, str):
        raise TypeError(f"title must be a string, got {type(title).__name__}")
    if not isinstance(xlabel, str):
        raise TypeError(f"xlabel must be a string, got {type(xlabel).__name__}")
    if not isinstance(ylabel, str):
        raise TypeError(f"ylabel must be a string, got {type(ylabel).__name__}")
    if title_fontsize is not None and not isinstance(title_fontsize, int):
        raise TypeError(
            f"title_fontsize must be an integer or None, got {type(title_fontsize).__name__}"
        )
    if label_fontsize is not None and not isinstance(label_fontsize, int):
        raise TypeError(
            f"label_fontsize must be an integer or None, got {type(label_fontsize).__name__}"
        )
    if not isinstance(grid, bool):
        raise TypeError(f"grid must be a boolean, got {type(grid).__name__}")
    if not isinstance(grid_style, str):
        raise TypeError(f"grid_style must be a string, got {type(grid_style).__name__}")
    if not isinstance(grid_alpha, (int, float)):
        raise TypeError(f"grid_alpha must be a number, got {type(grid_alpha).__name__}")
    if spine_visibility is not None and not isinstance(spine_visibility, dict):
        raise TypeError(
            f"spine_visibility must be a dict or None, got {type(spine_visibility).__name__}"
        )

    # Value validation
    if title_fontsize is not None and title_fontsize <= 0:
        raise ValueError(f"title_fontsize must be positive, got {title_fontsize}")
    if label_fontsize is not None and label_fontsize <= 0:
        raise ValueError(f"label_fontsize must be positive, got {label_fontsize}")
    if not 0 <= grid_alpha <= 1:
        raise ValueError(f"grid_alpha must be between 0 and 1, got {grid_alpha}")

    # Apply title and labels
    if title:
        kwargs: dict[str, str | int] = {"fontweight": "bold"}
        if title_fontsize is not None:
            kwargs["fontsize"] = title_fontsize
        ax.set_title(title, **kwargs)

    if xlabel:
        kwargs_xlabel: dict[str, str | int] = {}
        if label_fontsize is not None:
            kwargs_xlabel["fontsize"] = label_fontsize
        ax.set_xlabel(xlabel, **kwargs_xlabel)

    if ylabel:
        kwargs_ylabel: dict[str, str | int] = {}
        if label_fontsize is not None:
            kwargs_ylabel["fontsize"] = label_fontsize
        ax.set_ylabel(ylabel, **kwargs_ylabel)

    # Configure grid
    if grid:
        ax.grid(True, linestyle=grid_style, alpha=grid_alpha)
    else:
        ax.grid(False)

    # Configure spines
    if spine_visibility is not None:
        for spine_name, visible in spine_visibility.items():
            if spine_name not in ["top", "bottom", "left", "right"]:
                raise ValueError(f"Invalid spine name: {spine_name}")
            ax.spines[spine_name].set_visible(visible)

    logger.debug(f"Configured axes style with title='{title}'")


__all__ = ["configure_axes_style"]
