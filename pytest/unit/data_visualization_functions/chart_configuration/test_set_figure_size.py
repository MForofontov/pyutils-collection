"""
Unit tests for set_figure_size function.
"""

import pytest

# Try to import matplotlib - tests will be skipped if not available
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-GUI backend for testing
    import matplotlib.pyplot as plt

    from pyutils_collection.data_visualization_functions.chart_configuration.set_figure_size import (
        set_figure_size,
    )

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    matplotlib = None  # type: ignore
    plt = None  # type: ignore
    set_figure_size = None  # type: ignore

pytestmark = pytest.mark.skipif(
    not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed"
)
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.data_visualization]


def test_set_figure_size_basic() -> None:

    """
    Test case 1: Set figure size with default dimensions.
    """
    # Act
    set_figure_size(width=10, height=6)

    # Assert
    assert plt.rcParams["figure.figsize"][0] == 10
    assert plt.rcParams["figure.figsize"][1] == 6


def test_set_figure_size_square() -> None:

    """
    Test case 2: Set square figure size.
    """
    # Act
    set_figure_size(width=8, height=8)

    # Assert
    assert plt.rcParams["figure.figsize"][0] == 8
    assert plt.rcParams["figure.figsize"][1] == 8


def test_set_figure_size_large() -> None:

    """
    Test case 3: Set large figure size.
    """
    # Act
    set_figure_size(width=20, height=15)

    # Assert
    assert plt.rcParams["figure.figsize"][0] == 20
    assert plt.rcParams["figure.figsize"][1] == 15


def test_set_figure_size_small() -> None:

    """
    Test case 4: Set small figure size.
    """
    # Act
    set_figure_size(width=4, height=3)

    # Assert
    assert plt.rcParams["figure.figsize"][0] == 4
    assert plt.rcParams["figure.figsize"][1] == 3


def test_set_figure_size_invalid_width_type_raises_error() -> None:

    """
    Test case 5: TypeError for invalid width type.
    """
    # Arrange
    expected_message = "width must be a number"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        set_figure_size(width="10", height=6)


def test_set_figure_size_negative_width_raises_error() -> None:

    """
    Test case 6: ValueError for negative width.
    """
    # Arrange
    expected_message = "width must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        set_figure_size(width=-5, height=6)


def test_set_figure_size_zero_height_raises_error() -> None:

    """
    Test case 7: ValueError for zero height.
    """
    # Arrange
    expected_message = "height must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        set_figure_size(width=10, height=0)


def test_set_figure_size_invalid_height_type_raises_error() -> None:

    """
    Test case 8: TypeError for invalid height type.
    """
    # Arrange
    expected_message = "height must be a number"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        set_figure_size(width=10, height="6")


__all__ = ["test_set_figure_size_basic"]
