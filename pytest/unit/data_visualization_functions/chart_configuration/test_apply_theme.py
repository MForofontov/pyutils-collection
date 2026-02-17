"""
Unit tests for apply_theme function.
"""

import pytest

# Try to import matplotlib - tests will be skipped if not available
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-GUI backend for testing
    import matplotlib.pyplot as plt

    from pyutils_collection.data_visualization_functions.chart_configuration.apply_theme import apply_theme
    from pyutils_collection.data_visualization_functions.chart_configuration.chart_theme import ChartTheme

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    matplotlib = None  # type: ignore
    plt = None  # type: ignore
    apply_theme = None  # type: ignore
    ChartTheme = None  # type: ignore

pytestmark = pytest.mark.skipif(
    not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed"
)
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.data_visualization]


def test_apply_theme_basic() -> None:

    """
    Test case 1: Apply theme to current matplotlib settings.
    """
    # Arrange
    theme = ChartTheme(
        name="test", background_color="white", grid_color="gray", title_fontsize=14
    )

    # Act
    apply_theme(theme)

    # Assert
    assert plt.rcParams["figure.facecolor"] == "white"
    assert plt.rcParams["axes.titlesize"] == 14


def test_apply_theme_dark() -> None:

    """
    Test case 2: Apply dark theme.
    """
    # Arrange
    theme = ChartTheme(
        name="dark", background_color="black", grid_color="#333333", title_fontsize=16
    )

    # Act
    apply_theme(theme)

    # Assert
    assert plt.rcParams["figure.facecolor"] == "black"
    assert plt.rcParams["axes.titlesize"] == 16


def test_apply_theme_custom_fonts() -> None:

    """
    Test case 3: Apply theme with custom font sizes.
    """
    # Arrange
    theme = ChartTheme(
        name="custom",
        background_color="white",
        grid_color="gray",
        title_fontsize=18,
        label_fontsize=14,
        tick_fontsize=12,
    )

    # Act
    apply_theme(theme)

    # Assert
    assert plt.rcParams["axes.titlesize"] == 18
    assert plt.rcParams["axes.labelsize"] == 14
    assert plt.rcParams["xtick.labelsize"] == 12


def test_apply_theme_color_cycle() -> None:

    """
    Test case 4: Apply theme with custom color cycle.
    """
    # Arrange
    colors = ["#FF0000", "#00FF00", "#0000FF"]
    theme = ChartTheme(
        name="colors", background_color="white", grid_color="gray", color_cycle=colors
    )

    # Act
    apply_theme(theme)

    # Assert
    # Color cycle is set in rcParams
    assert "axes.prop_cycle" in plt.rcParams


def test_apply_theme_invalid_type_raises_error() -> None:

    """
    Test case 5: TypeError for invalid theme type.
    """
    # Arrange
    invalid_theme = {"name": "dict"}
    expected_message = "theme must be a ChartTheme instance"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        apply_theme(invalid_theme)


def test_apply_theme_none_raises_error() -> None:

    """
    Test case 6: TypeError for None theme.
    """
    # Arrange
    expected_message = "theme must be a ChartTheme instance"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        apply_theme(None)


def test_apply_theme_grid_settings() -> None:

    """
    Test case 7: Apply theme with grid settings.
    """
    # Arrange
    theme = ChartTheme(
        name="grid", background_color="white", grid_color="lightgray", grid_alpha=0.5
    )

    # Act
    apply_theme(theme)

    # Assert
    assert plt.rcParams["grid.color"] == "lightgray"
    assert plt.rcParams["grid.alpha"] == 0.5


__all__ = ["test_apply_theme_basic"]
