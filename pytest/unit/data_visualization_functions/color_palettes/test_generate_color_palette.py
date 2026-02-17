"""
Unit tests for generate_color_palette function.
"""

import pytest

# Try to import matplotlib - tests will be skipped if not available
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-GUI backend for testing
    from pyutils_collection.data_visualization_functions.color_palettes.generate_color_palette import (
        generate_color_palette,
    )

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    matplotlib = None  # type: ignore
    generate_color_palette = None  # type: ignore

pytestmark = pytest.mark.skipif(
    not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed"
)
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.data_visualization]


def test_generate_color_palette_basic() -> None:

    """
    Test case 1: Generate basic color palette with default count.
    """
    # Act
    colors = generate_color_palette(n_colors=5)

    # Assert
    assert len(colors) == 5
    assert all(isinstance(c, str) for c in colors)


def test_generate_color_palette_large() -> None:

    """
    Test case 2: Generate large color palette.
    """
    # Act
    colors = generate_color_palette(n_colors=20)

    # Assert
    assert len(colors) == 20
    assert len(set(colors)) == 20  # All unique


def test_generate_color_palette_custom_scheme() -> None:

    """
    Test case 3: Generate palette with custom color scheme.
    """
    # Act
    colors = generate_color_palette(n_colors=5, colormap="viridis")

    # Assert
    assert len(colors) == 5
    # Colors should be hex strings
    assert all(c.startswith("#") for c in colors)


def test_generate_color_palette_diverging() -> None:

    """
    Test case 4: Generate diverging color palette.
    """
    # Act
    colors = generate_color_palette(n_colors=7, colormap="coolwarm")

    # Assert
    assert len(colors) == 7


def test_generate_color_palette_single_color() -> None:

    """
    Test case 5: Generate palette with single color.
    """
    # Act
    colors = generate_color_palette(n_colors=1)

    # Assert
    assert len(colors) == 1
    assert isinstance(colors[0], str)


def test_generate_color_palette_zero_colors_raises_error() -> None:

    """
    Test case 6: ValueError for zero colors.
    """
    # Arrange
    expected_message = "n_colors must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        generate_color_palette(n_colors=0)


def test_generate_color_palette_negative_colors_raises_error() -> None:

    """
    Test case 7: ValueError for negative number of colors.
    """
    # Arrange
    expected_message = "n_colors must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        generate_color_palette(n_colors=-5)


def test_generate_color_palette_invalid_type_raises_error() -> None:

    """
    Test case 8: TypeError for invalid n_colors type.
    """
    # Arrange
    expected_message = "n_colors must be an integer"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        generate_color_palette(n_colors="5")


def test_generate_color_palette_invalid_scheme_raises_error() -> None:

    """
    Test case 9: ValueError for invalid color scheme.
    """
    # Arrange
    expected_message = "not a valid value for name|Colormap .* is not recognized"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        generate_color_palette(n_colors=5, colormap="invalid_scheme")


__all__ = ["test_generate_color_palette_basic"]
