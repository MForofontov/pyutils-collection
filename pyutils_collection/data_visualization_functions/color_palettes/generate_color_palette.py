"""
Generate a color palette with specified number of colors.
"""

import logging
from typing import Literal

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)


def generate_color_palette(
    n_colors: int,
    palette_type: Literal[
        "sequential", "diverging", "qualitative", "rainbow"
    ] = "qualitative",
    start_color: str | None = None,
    end_color: str | None = None,
    colormap: str | None = None,
) -> list[str]:
    """
    Generate a color palette with specified number of colors.

    Parameters
    ----------
    n_colors : int
        Number of colors to generate.
    palette_type : Literal['sequential', 'diverging', 'qualitative', 'rainbow'], optional
        Type of color palette (by default 'qualitative').
    start_color : str | None, optional
        Starting color for gradient (hex or named color) (by default None).
    end_color : str | None, optional
        Ending color for gradient (hex or named color) (by default None).
    colormap : str | None, optional
        Matplotlib colormap name to use (by default None).

    Returns
    -------
    list[str]
        List of color hex codes.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values.

    Examples
    --------
    >>> colors = generate_color_palette(5, palette_type='qualitative')
    >>> len(colors)
    5

    >>> colors = generate_color_palette(
    ...     10,
    ...     palette_type='sequential',
    ...     start_color='#FFFFFF',
    ...     end_color='#0000FF'
    ... )
    >>> len(colors)
    10

    >>> colors = generate_color_palette(8, colormap='viridis')
    >>> len(colors)
    8

    Notes
    -----
    Palette types:
    - sequential: Colors transition smoothly from start to end
    - diverging: Colors diverge from center (requires start and end colors)
    - qualitative: Distinct colors for categorical data
    - rainbow: Full spectrum of hues

    Complexity
    ----------
    Time: O(n), Space: O(n) where n is n_colors
    """
    # Type validation
    if not isinstance(n_colors, int):
        raise TypeError(f"n_colors must be an integer, got {type(n_colors).__name__}")
    if not isinstance(palette_type, str):
        raise TypeError(
            f"palette_type must be a string, got {type(palette_type).__name__}"
        )
    if start_color is not None and not isinstance(start_color, str):
        raise TypeError(
            f"start_color must be a string or None, got {type(start_color).__name__}"
        )
    if end_color is not None and not isinstance(end_color, str):
        raise TypeError(
            f"end_color must be a string or None, got {type(end_color).__name__}"
        )
    if colormap is not None and not isinstance(colormap, str):
        raise TypeError(
            f"colormap must be a string or None, got {type(colormap).__name__}"
        )

    # Value validation
    if n_colors <= 0:
        raise ValueError(f"n_colors must be positive, got {n_colors}")

    valid_palette_types = ["sequential", "diverging", "qualitative", "rainbow"]
    if palette_type not in valid_palette_types:
        raise ValueError(
            f"palette_type must be one of {valid_palette_types}, got '{palette_type}'"
        )

    # Use specified colormap if provided
    if colormap is not None:
        try:
            cmap = plt.get_cmap(colormap)
            colors = [
                mcolors.rgb2hex(cmap(i / (n_colors - 1 if n_colors > 1 else 1)))
                for i in range(n_colors)
            ]
            logger.debug(f"Generated {n_colors} colors from colormap '{colormap}'")
            return colors
        except Exception as e:
            raise ValueError(f"Invalid colormap '{colormap}': {e}") from e

    # Generate colors based on palette type
    if palette_type == "qualitative":
        # Use distinct colors from tableau palette
        base_colors = [
            "#1f77b4",
            "#ff7f0e",
            "#2ca02c",
            "#d62728",
            "#9467bd",
            "#8c564b",
            "#e377c2",
            "#7f7f7f",
            "#bcbd22",
            "#17becf",
        ]
        if n_colors <= len(base_colors):
            colors = base_colors[:n_colors]
        else:
            # Generate additional colors using HSV
            colors = base_colors.copy()
            hues = np.linspace(0, 1, n_colors - len(base_colors) + 1)[:-1]
            for hue in hues:
                rgb_arr = mcolors.hsv_to_rgb((hue, 0.7, 0.9))
                rgb: tuple[float, float, float] = (float(rgb_arr[0]), float(rgb_arr[1]), float(rgb_arr[2]))
                colors.append(mcolors.rgb2hex(rgb))

    elif palette_type == "sequential":
        # Sequential gradient
        if start_color is None:
            start_color = "#FFFFFF"
        if end_color is None:
            end_color = "#0000FF"

        start_rgb = mcolors.to_rgb(start_color)
        end_rgb = mcolors.to_rgb(end_color)

        colors = []
        for i in range(n_colors):
            t = i / (n_colors - 1) if n_colors > 1 else 0
            r = start_rgb[0] + t * (end_rgb[0] - start_rgb[0])
            g = start_rgb[1] + t * (end_rgb[1] - start_rgb[1])
            b = start_rgb[2] + t * (end_rgb[2] - start_rgb[2])
            rgb = (r, g, b)
            colors.append(mcolors.rgb2hex(rgb))

    elif palette_type == "diverging":
        # Diverging from center
        if start_color is None:
            start_color = "#0000FF"
        if end_color is None:
            end_color = "#FF0000"

        mid_color = "#FFFFFF"
        start_rgb = mcolors.to_rgb(start_color)
        mid_rgb = mcolors.to_rgb(mid_color)
        end_rgb = mcolors.to_rgb(end_color)

        colors = []
        for i in range(n_colors):
            t = i / (n_colors - 1) if n_colors > 1 else 0
            if t < 0.5:
                # Interpolate from start to mid
                t_scaled = t * 2
                r = start_rgb[0] + t_scaled * (mid_rgb[0] - start_rgb[0])
                g = start_rgb[1] + t_scaled * (mid_rgb[1] - start_rgb[1])
                b = start_rgb[2] + t_scaled * (mid_rgb[2] - start_rgb[2])
                rgb = (r, g, b)
            else:
                # Interpolate from mid to end
                t_scaled = (t - 0.5) * 2
                r = mid_rgb[0] + t_scaled * (end_rgb[0] - mid_rgb[0])
                g = mid_rgb[1] + t_scaled * (end_rgb[1] - mid_rgb[1])
                b = mid_rgb[2] + t_scaled * (end_rgb[2] - mid_rgb[2])
                rgb = (r, g, b)
            colors.append(mcolors.rgb2hex(rgb))

    else:  # rainbow
        # Full spectrum
        hues = np.linspace(0, 1, n_colors + 1)[:-1]
        colors = []
        for hue in hues:
            rgb_arr = mcolors.hsv_to_rgb((hue, 0.8, 0.9))
            rgb = (float(rgb_arr[0]), float(rgb_arr[1]), float(rgb_arr[2]))
            colors.append(mcolors.rgb2hex(rgb))

    logger.debug(f"Generated {n_colors} colors with palette_type='{palette_type}'")
    return colors


__all__ = ["generate_color_palette"]
