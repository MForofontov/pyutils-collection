"""
Create a smooth color gradient between two colors.
"""

import logging

import matplotlib.colors as mcolors

logger = logging.getLogger(__name__)


def create_gradient(
    start_color: str,
    end_color: str,
    n_steps: int = 10,
) -> list[str]:
    """
    Create a smooth color gradient between two colors.

    Parameters
    ----------
    start_color : str
        Starting color (hex code or named color).
    end_color : str
        Ending color (hex code or named color).
    n_steps : int, optional
        Number of steps in the gradient (by default 10).

    Returns
    -------
    list[str]
        List of color hex codes forming the gradient.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values.

    Examples
    --------
    >>> gradient = create_gradient('#FF0000', '#0000FF', n_steps=5)
    >>> len(gradient)
    5

    >>> gradient = create_gradient('red', 'blue', n_steps=10)
    >>> len(gradient)
    10

    Notes
    -----
    The gradient is created by linear interpolation in RGB space.

    Complexity
    ----------
    Time: O(n), Space: O(n) where n is n_steps
    """
    # Type validation
    if not isinstance(start_color, str):
        raise TypeError(
            f"start_color must be a string, got {type(start_color).__name__}"
        )
    if not isinstance(end_color, str):
        raise TypeError(f"end_color must be a string, got {type(end_color).__name__}")
    if not isinstance(n_steps, int):
        raise TypeError(f"n_steps must be an integer, got {type(n_steps).__name__}")

    # Value validation
    if n_steps <= 0:
        raise ValueError(f"n_steps must be positive, got {n_steps}")

    try:
        start_rgb = mcolors.to_rgb(start_color)
        end_rgb = mcolors.to_rgb(end_color)
    except ValueError as e:
        raise ValueError(f"Invalid color specification: {e}") from e

    gradient = []
    for i in range(n_steps):
        t = i / (n_steps - 1) if n_steps > 1 else 0
        r = start_rgb[0] + t * (end_rgb[0] - start_rgb[0])
        g = start_rgb[1] + t * (end_rgb[1] - start_rgb[1])
        b = start_rgb[2] + t * (end_rgb[2] - start_rgb[2])
        rgb: tuple[float, float, float] = (r, g, b)
        gradient.append(mcolors.rgb2hex(rgb))

    logger.debug(
        f"Created gradient with {n_steps} steps from {start_color} to {end_color}"
    )
    return gradient


__all__ = ["create_gradient"]
