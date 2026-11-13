"""
Export the current matplotlib figure.
"""

import logging
from pathlib import Path

import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


def export_current_figure(
    filepath: str | Path,
    dpi: int = 300,
    close_after_save: bool = False,
) -> None:
    """
    Export the current matplotlib figure.

    Parameters
    ----------
    filepath : str | Path
        Output file path (extension determines format).
    dpi : int, optional
        Resolution in dots per inch (by default 300).
    close_after_save : bool, optional
        Whether to close the figure after saving (by default False).

    Returns
    -------
    None

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If dpi is invalid or no figure exists.

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> plt.figure()
    >>> plt.plot([1, 2, 3], [1, 4, 9])
    >>> export_current_figure('plot.png')

    >>> plt.plot([1, 2], [3, 4])
    >>> export_current_figure('output.pdf', dpi=600, close_after_save=True)

    Notes
    -----
    Uses plt.gcf() to get the current figure.
    If no figure exists, raises without creating a figure. An existing figure
    without axes is left open when rejected.
    Supported formats: PNG, PDF, SVG, JPG, EPS.

    Complexity
    ----------
    Time: O(n) where n is figure complexity, Space: O(n)
    """
    # Type validation
    if not isinstance(filepath, (str, Path)):
        raise TypeError(
            f"filepath must be a string or Path, got {type(filepath).__name__}"
        )

    if not isinstance(dpi, int):
        raise TypeError(f"dpi must be an integer, got {type(dpi).__name__}")

    if not isinstance(close_after_save, bool):
        raise TypeError(
            f"close_after_save must be a boolean, got {type(close_after_save).__name__}"
        )

    # Value validation
    if dpi < 1:
        raise ValueError(f"dpi must be positive, got {dpi}")

    filepath_obj = Path(filepath)

    if not filepath_obj.suffix:
        raise ValueError(f"filepath must have an extension (e.g., .png): '{filepath}'")

    # Get current figure
    if not plt.get_fignums():
        raise ValueError("No active figure to export")
    fig = plt.gcf()

    if fig is None or not fig.get_axes():
        raise ValueError("No active figure to export")

    logger.debug(
        f"Exporting current figure to {filepath} with dpi={dpi}, "
        f"close_after_save={close_after_save}"
    )

    # Create parent directory
    filepath_obj.parent.mkdir(parents=True, exist_ok=True)

    # Save figure
    plt.savefig(
        filepath_obj,
        dpi=dpi,
        bbox_inches="tight",
    )

    logger.info(f"Exported current figure to {filepath_obj}")

    # Close if requested
    if close_after_save:
        plt.close(fig)
        logger.debug("Closed figure after saving")


__all__ = ["export_current_figure"]
