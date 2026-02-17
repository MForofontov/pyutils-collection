"""
Unit tests for generate_categorical_colors function.
"""

import pytest

# Try to import matplotlib - tests will be skipped if not available
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-GUI backend for testing
    from pyutils_collection.data_visualization_functions.color_palettes.generate_categorical_colors import (
        generate_categorical_colors,
    )

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    matplotlib = None  # type: ignore
    generate_categorical_colors = None  # type: ignore

pytestmark = pytest.mark.skipif(
    not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed"
)
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.data_visualization]


def test_generate_categorical_colors_basic() -> None:

    """
    Test case 1: Generate categorical colors with default settings.
    """
    # Arrange
    n_colors = 4

    # Act
    colors = generate_categorical_colors(n_colors)

    # Assert
    assert isinstance(colors, list)
    assert len(colors) == 4
    assert all(isinstance(c, str) for c in colors)


def test_generate_categorical_colors_many_categories() -> None:

    """
    Test case 2: Generate colors for many categories.
    """
    # Arrange
    n_colors = 15

    # Act
    colors = generate_categorical_colors(n_colors)

    # Assert
    assert len(colors) == 15
    assert all(isinstance(c, str) for c in colors)


def test_generate_categorical_colors_single_category() -> None:

    """
    Test case 3: Generate color for single category.
    """
    # Arrange
    n_colors = 1

    # Act
    colors = generate_categorical_colors(n_colors)

    # Assert
    assert isinstance(colors, list)
    assert len(colors) == 1


def test_generate_categorical_colors_hex_format() -> None:

    """
    Test case 4: Generated colors are in hex format.
    """
    # Arrange
    n_colors = 5

    # Act
    colors = generate_categorical_colors(n_colors)

    # Assert
    assert all(c.startswith("#") for c in colors)
    assert all(len(c) == 7 for c in colors)  # #RRGGBB format


def test_generate_categorical_colors_unique() -> None:

    """
    Test case 5: All generated colors are unique.
    """
    # Arrange
    n_colors = 20

    # Act
    colors = generate_categorical_colors(n_colors)

    # Assert
    assert len(set(colors)) == len(colors)  # All unique


def test_generate_categorical_colors_empty_raises_error() -> None:

    """
    Test case 6: ValueError for zero or negative n_colors.
    """
    # Arrange
    expected_message = "n_colors must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        generate_categorical_colors(0)


def test_generate_categorical_colors_invalid_type_raises_error() -> None:

    """
    Test case 7: TypeError for invalid type.
    """
    # Arrange
    expected_message = "n_colors must be an integer"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        generate_categorical_colors("5")


def test_generate_categorical_colors_none_raises_error() -> None:

    """
    Test case 8: TypeError for None value.
    """
    # Arrange
    expected_message = "n_colors must be an integer"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        generate_categorical_colors(None)


__all__ = ["test_generate_categorical_colors_basic"]
