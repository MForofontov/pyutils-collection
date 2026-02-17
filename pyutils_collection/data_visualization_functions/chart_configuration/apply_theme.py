"""
Apply a theme to matplotlib's global configuration.
"""

import logging

import matplotlib.pyplot as plt
from cycler import cycler

from .chart_theme import ChartTheme

logger = logging.getLogger(__name__)


def apply_theme(theme: ChartTheme) -> None:
    """
    Apply a theme to matplotlib's global configuration.

    Parameters
    ----------
    theme : ChartTheme
        Theme configuration to apply.

    Raises
    ------
    TypeError
        If theme is not a ChartTheme instance.

    Examples
    --------
    >>> theme = get_preset_theme('dark')
    >>> apply_theme(theme)
    >>> # All subsequent plots will use the dark theme

    >>> custom_theme = ChartTheme(
    ...     name="custom",
    ...     background_color="#f5f5f5",
    ...     color_cycle=["#FF6B6B", "#4ECDC4", "#45B7D1"]
    ... )
    >>> apply_theme(custom_theme)

    Notes
    -----
    This function modifies matplotlib's global rcParams. Changes persist
    for the entire session unless reset with reset_theme().

    Complexity
    ----------
    Time: O(1), Space: O(1)
    """
    if not isinstance(theme, ChartTheme):
        raise TypeError(
            f"theme must be a ChartTheme instance, got {type(theme).__name__}"
        )

    # Apply theme settings
    plt.rcParams["figure.facecolor"] = theme.background_color
    plt.rcParams["axes.facecolor"] = theme.background_color
    plt.rcParams["axes.edgecolor"] = theme.grid_color
    plt.rcParams["axes.grid"] = True
    plt.rcParams["grid.color"] = theme.grid_color
    plt.rcParams["grid.alpha"] = theme.grid_alpha
    plt.rcParams["axes.titlesize"] = theme.title_fontsize
    plt.rcParams["axes.labelsize"] = theme.label_fontsize
    plt.rcParams["xtick.labelsize"] = theme.tick_fontsize
    plt.rcParams["ytick.labelsize"] = theme.tick_fontsize
    plt.rcParams["legend.fontsize"] = theme.legend_fontsize
    plt.rcParams["lines.linewidth"] = theme.line_width
    plt.rcParams["font.family"] = theme.font_family

    # Set color cycle
    plt.rcParams["axes.prop_cycle"] = cycler(color=theme.color_cycle)

    logger.info(f"Applied theme: {theme.name}")


__all__ = ["apply_theme"]
