"""
Unit tests for ChartTheme dataclass.
"""

import pytest

try:
    import matplotlib
    from pyutils_collection.data_visualization_functions.chart_configuration import ChartTheme
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    matplotlib = None  # type: ignore
    ChartTheme = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.data_visualization,
    pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed"),
]


def test_chart_theme_default_values() -> None:

    """
    Test case 1: Create ChartTheme with default values.
    """
    # Act
    theme = ChartTheme(name="test", background_color="white", grid_color="gray")

    # Assert
    assert theme.name == "test"
    assert theme.background_color == "white"
    assert theme.grid_color == "gray"
    assert isinstance(theme.color_cycle, list)


def test_chart_theme_custom_values() -> None:

    """
    Test case 2: Create ChartTheme with custom values.
    """
    # Arrange
    colors = ["#FF0000", "#00FF00", "#0000FF"]

    # Act
    theme = ChartTheme(
        name="custom", background_color="black", color_cycle=colors, title_fontsize=16
    )

    # Assert
    assert theme.name == "custom"
    assert theme.background_color == "black"
    assert theme.color_cycle == colors
    assert theme.title_fontsize == 16


def test_chart_theme_font_sizes() -> None:

    """
    Test case 3: Verify font size attributes.
    """
    # Act
    theme = ChartTheme(
        name="fonts",
        background_color="white",
        grid_color="gray",
        title_fontsize=16,
        label_fontsize=12,
        tick_fontsize=10,
    )

    # Assert
    assert theme.title_fontsize == 16
    assert theme.label_fontsize == 12
    assert theme.tick_fontsize == 10


def test_chart_theme_invalid_font_size_raises_error() -> None:

    """
    Test case 4: ValueError for negative title font size.
    """
    # Arrange & Act & Assert
    with pytest.raises(ValueError, match="title_fontsize must be positive"):
        ChartTheme(
            name="test", background_color="white", grid_color="gray", title_fontsize=-1
        )


def test_chart_theme_invalid_title_size_raises_error() -> None:

    """
    Test case 5: ValueError for zero label font size.
    """
    # Arrange & Act & Assert
    with pytest.raises(ValueError, match="label_fontsize must be positive"):
        ChartTheme(
            name="test", background_color="white", grid_color="gray", label_fontsize=0
        )


def test_chart_theme_invalid_label_size_raises_error() -> None:

    """
    Test case 6: ValueError for negative tick font size.
    """
    # Arrange & Act & Assert
    with pytest.raises(ValueError, match="tick_fontsize must be positive"):
        ChartTheme(
            name="test", background_color="white", grid_color="gray", tick_fontsize=-5
        )


def test_chart_theme_empty_color_palette_raises_error() -> None:

    """
    Test case 7: ValueError for empty color cycle.
    """
    # Arrange & Act & Assert
    with pytest.raises(ValueError, match="color_cycle cannot be empty"):
        ChartTheme(
            name="test", background_color="white", grid_color="gray", color_cycle=[]
        )
