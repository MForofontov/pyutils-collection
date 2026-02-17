"""
Unit tests for get_colorblind_safe_palette function.
"""

import pytest

# Try to import matplotlib - tests will be skipped if not available
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-GUI backend for testing
    from pyutils_collection.data_visualization_functions.color_palettes.get_colorblind_safe_palette import (
        get_colorblind_safe_palette,
    )

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    matplotlib = None  # type: ignore
    get_colorblind_safe_palette = None  # type: ignore

pytestmark = pytest.mark.skipif(
    not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed"
)
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.data_visualization]


def test_get_colorblind_safe_palette_default() -> None:

    """
    Test case 1: Get default colorblind safe palette with 8 colors.
    """
    # Act
    colors = get_colorblind_safe_palette(8)

    # Assert
    assert isinstance(colors, list)
    assert len(colors) == 8
    assert all(isinstance(c, str) for c in colors)


def test_get_colorblind_safe_palette_specific_count() -> None:

    """
    Test case 2: Get specific number of colorblind safe colors.
    """
    # Act
    colors = get_colorblind_safe_palette(n_colors=5)

    # Assert
    assert len(colors) == 5


def test_get_colorblind_safe_palette_large() -> None:

    """
    Test case 3: Get large colorblind safe palette.
    """
    # Act
    colors = get_colorblind_safe_palette(n_colors=10)

    # Assert
    assert len(colors) == 10


def test_get_colorblind_safe_palette_single_color() -> None:

    """
    Test case 4: Get single colorblind safe color.
    """
    # Act
    colors = get_colorblind_safe_palette(n_colors=1)

    # Assert
    assert len(colors) == 1
    assert isinstance(colors[0], str)


def test_get_colorblind_safe_palette_hex_format() -> None:

    """
    Test case 5: Verify colors are in hex format.
    """
    # Act
    colors = get_colorblind_safe_palette(n_colors=5)

    # Assert
    assert all(c.startswith("#") for c in colors)
    assert all(len(c) == 7 for c in colors)


def test_get_colorblind_safe_palette_zero_colors_raises_error() -> None:

    """
    Test case 6: ValueError for zero colors.
    """
    # Arrange
    expected_message = "n_colors must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        get_colorblind_safe_palette(n_colors=0)


def test_get_colorblind_safe_palette_negative_colors_raises_error() -> None:

    """
    Test case 7: ValueError for negative number of colors.
    """
    # Arrange
    expected_message = "n_colors must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        get_colorblind_safe_palette(n_colors=-3)


def test_get_colorblind_safe_palette_invalid_type_raises_error() -> None:

    """
    Test case 8: TypeError for invalid n_colors type.
    """
    # Arrange
    expected_message = "n_colors must be an integer"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        get_colorblind_safe_palette(n_colors="5")


__all__ = ["test_get_colorblind_safe_palette_default"]
