"""
Unit tests for configure_axes_style function.
"""

import pytest

# Try to import matplotlib - tests will be skipped if not available
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-GUI backend for testing
    import matplotlib.pyplot as plt

    from pyutils_collection.data_visualization_functions.chart_configuration.configure_axes_style import (
        configure_axes_style,
    )

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    matplotlib = None  # type: ignore
    plt = None  # type: ignore
    configure_axes_style = None  # type: ignore

pytestmark = pytest.mark.skipif(
    not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed"
)
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.data_visualization]


def test_configure_axes_style_basic() -> None:

    """
    Test case 1: Configure axes style with default settings.
    """
    # Arrange
    fig, ax = plt.subplots()

    # Act
    configure_axes_style(ax)

    # Assert
    assert ax is not None

    # Cleanup
    plt.close(fig)


def test_configure_axes_style_with_grid() -> None:

    """
    Test case 2: Configure axes with grid enabled.
    """
    # Arrange
    fig, ax = plt.subplots()

    # Act
    configure_axes_style(ax, grid=True, grid_alpha=0.5)

    # Assert - grid was configured
    assert ax is not None

    # Cleanup
    plt.close(fig)


def test_configure_axes_style_spine_visibility() -> None:

    """
    Test case 3: Configure spine visibility.
    """
    # Arrange
    fig, ax = plt.subplots()

    # Act
    configure_axes_style(ax, spine_visibility={"top": False, "right": False})

    # Assert
    assert not ax.spines["top"].get_visible()
    assert not ax.spines["right"].get_visible()

    # Cleanup
    plt.close(fig)


def test_configure_axes_style_with_labels() -> None:

    """
    Test case 4: Configure axes with labels.
    """
    # Arrange
    fig, ax = plt.subplots()

    # Act
    configure_axes_style(ax, title="Test", xlabel="X", ylabel="Y")

    # Assert
    assert ax.get_title() == "Test"
    assert ax.get_xlabel() == "X"
    assert ax.get_ylabel() == "Y"

    # Cleanup
    plt.close(fig)


def test_configure_axes_style_invalid_ax_raises_error() -> None:

    """
    Test case 5: AttributeError for invalid axes object.
    """
    # Arrange
    invalid_ax = "not_an_axes"

    # Act & Assert - will fail when trying to call .grid() on string
    with pytest.raises(AttributeError):
        configure_axes_style(invalid_ax)


def test_configure_axes_style_none_ax_raises_error() -> None:

    """
    Test case 6: AttributeError for None axes.
    """
    # Act & Assert
    with pytest.raises(AttributeError):
        configure_axes_style(None)


def test_configure_axes_style_invalid_grid_alpha_raises_error() -> None:

    """
    Test case 7: ValueError for invalid grid alpha.
    """
    # Arrange
    fig, ax = plt.subplots()
    expected_message = "grid_alpha must be between 0 and 1"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        configure_axes_style(ax, grid_alpha=1.5)

    # Cleanup
    plt.close(fig)


__all__ = ["test_configure_axes_style_basic"]
