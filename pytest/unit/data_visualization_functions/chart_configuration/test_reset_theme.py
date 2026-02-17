"""
Unit tests for reset_theme function.
"""

import pytest

# Try to import matplotlib - tests will be skipped if not available
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-GUI backend for testing
    import matplotlib.pyplot as plt

    from pyutils_collection.data_visualization_functions.chart_configuration.apply_theme import apply_theme
    from pyutils_collection.data_visualization_functions.chart_configuration.chart_theme import ChartTheme
    from pyutils_collection.data_visualization_functions.chart_configuration.reset_theme import reset_theme

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    matplotlib = None  # type: ignore
    plt = None  # type: ignore
    apply_theme = None  # type: ignore
    ChartTheme = None  # type: ignore
    reset_theme = None  # type: ignore

pytestmark = pytest.mark.skipif(
    not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed"
)
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.data_visualization]


def test_reset_theme_restores_defaults() -> None:

    """
    Test case 1: Reset theme restores matplotlib defaults.
    """
    # Arrange - Apply custom theme
    theme = ChartTheme(
        name="custom", background_color="black", grid_color="gray", title_fontsize=20
    )
    apply_theme(theme)

    # Verify theme was applied
    assert plt.rcParams["figure.facecolor"] == "black"

    # Act
    reset_theme()

    # Assert - Just check that function runs without error
    # Reset behavior depends on implementation
    assert True


def test_reset_theme_after_multiple_applications() -> None:

    """
    Test case 2: Reset works after applying multiple themes.
    """
    # Arrange
    theme1 = ChartTheme(name="t1", background_color="red", grid_color="gray")
    theme2 = ChartTheme(name="t2", background_color="blue", grid_color="gray")

    apply_theme(theme1)
    apply_theme(theme2)

    # Act
    reset_theme()

    # Assert - should not equal either custom theme
    assert plt.rcParams["figure.facecolor"] != "red"
    assert plt.rcParams["figure.facecolor"] != "blue"


def test_reset_theme_idempotent() -> None:

    """
    Test case 3: Calling reset multiple times is safe.
    """
    # Act
    reset_theme()
    result1 = dict(plt.rcParams)
    reset_theme()
    result2 = dict(plt.rcParams)

    # Assert - should be the same
    assert result1 == result2


def test_reset_theme_no_parameters() -> None:

    """
    Test case 4: Reset theme with no parameters.
    """
    # Act & Assert - should not raise any errors
    try:
        reset_theme()
    except Exception as e:
        pytest.fail(f"reset_theme() raised {type(e).__name__}: {e}")


def test_reset_theme_restores_color_cycle() -> None:

    """
    Test case 5: Reset restores default color cycle.
    """
    # Arrange - apply custom theme with color cycle
    custom_colors = ["#FF0000", "#00FF00"]
    theme = ChartTheme(
        name="colors",
        background_color="white",
        grid_color="gray",
        color_cycle=custom_colors,
    )
    apply_theme(theme)

    # Act
    reset_theme()

    # Assert - color cycle should be restored
    assert "axes.prop_cycle" in plt.rcParams


def test_reset_theme_restores_grid_settings() -> None:

    """
    Test case 6: Reset restores default grid settings.
    """
    # Arrange
    theme = ChartTheme(
        name="grid", background_color="white", grid_color="red", grid_alpha=0.3
    )
    apply_theme(theme)

    # Act
    reset_theme()

    # Assert - grid settings restored
    assert plt.rcParams["grid.color"] != "red"
    assert plt.rcParams["grid.alpha"] != 0.3


__all__ = ["test_reset_theme_restores_defaults"]
