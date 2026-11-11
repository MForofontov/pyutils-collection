"""
Generate visually distinct categorical colors.
"""

import logging

import numpy as np
from matplotlib.colors import to_hex

logger = logging.getLogger(__name__)


def generate_categorical_colors(n_colors: int) -> list[str]:
    """
    Generate visually distinct categorical colors.

    Parameters
    ----------
    n_colors : int
        Number of distinct colors to generate.

    Returns
    -------
    list[str]
        List of hex color codes.

    Raises
    ------
    TypeError
        If n_colors is not an integer.
    ValueError
        If n_colors is not positive.

    Examples
    --------
    >>> colors = generate_categorical_colors(5)
    >>> len(colors)
    5

    >>> colors = generate_categorical_colors(10)
    >>> all(c.startswith('#') for c in colors)
    True

    Notes
    -----
    Uses HSV color space with evenly distributed hues for maximum distinction.
    Saturation and value are optimized for visibility.

    Complexity
    ----------
    Time: O(n), Space: O(n)
    """
    # Type validation
    if not isinstance(n_colors, int):
        raise TypeError(f"n_colors must be an integer, got {type(n_colors).__name__}")

    # Value validation
    if n_colors < 1:
        raise ValueError(f"n_colors must be positive, got {n_colors}")

    logger.debug(f"Generating {n_colors} categorical colors")

    # Generate evenly spaced hues
    hues = np.linspace(0, 1, n_colors, endpoint=False)

    # Use high saturation and value for distinct, vibrant colors
    saturation = 0.75
    value = 0.85

    colors = []
    for hue in hues:
        # Convert HSV to RGB
        h_sector = int(hue * 6)
        f = float(hue * 6 - h_sector)
        p = value * (1 - saturation)
        q = value * (1 - f * saturation)
        t = value * (1 - (1 - f) * saturation)

        if h_sector == 0:
            r, g, b = value, t, p
        elif h_sector == 1:
            r, g, b = q, value, p
        elif h_sector == 2:
            r, g, b = p, value, t
        elif h_sector == 3:
            r, g, b = p, q, value
        elif h_sector == 4:
            r, g, b = t, p, value
        else:
            r, g, b = value, p, q

        hex_color = to_hex((r, g, b), keep_alpha=False)
        colors.append(hex_color)

    logger.debug(f"Generated colors: {colors}")
    return colors


__all__ = ["generate_categorical_colors"]
