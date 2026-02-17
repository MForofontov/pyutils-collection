"""
Unit tests for adjust_brightness function.
"""

import pytest

# Try to import matplotlib - tests will be skipped if not available
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-GUI backend for testing
    from pyutils_collection.data_visualization_functions.color_palettes.adjust_brightness import (
        adjust_brightness,
    )

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    matplotlib = None  # type: ignore
    adjust_brightness = None  # type: ignore

pytestmark = pytest.mark.skipif(
    not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed"
)
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.data_visualization]


def test_adjust_brightness_lighten() -> None:

    """
    Test case 1: Lighten a color.
    """
    # Arrange
    color = "#808080"  # Medium gray
    factor = 1.5  # Increase brightness

    # Act
    result = adjust_brightness(color, factor)

    # Assert
    assert isinstance(result, str)
    assert result.startswith("#")
    assert result != color  # Should be different


def test_adjust_brightness_darken() -> None:

    """
    Test case 2: Darken a color.
    """
    # Arrange
    color = "#CCCCCC"  # Light gray
    factor = 0.5  # Decrease brightness

    # Act
    result = adjust_brightness(color, factor)

    # Assert
    assert isinstance(result, str)
    assert result.startswith("#")


def test_adjust_brightness_no_change() -> None:

    """
    Test case 3: Factor of 1.0 should not change color.
    """
    # Arrange
    color = "#FF5733"
    factor = 1.0

    # Act
    result = adjust_brightness(color, factor)

    # Assert
    assert result.lower() == color.lower()


def test_adjust_brightness_black() -> None:

    """
    Test case 4: Adjust brightness of black color.
    """
    # Arrange
    color = "#000000"
    factor = 1.5

    # Act
    result = adjust_brightness(color, factor)

    # Assert
    assert isinstance(result, str)


def test_adjust_brightness_white() -> None:

    """
    Test case 5: Darken white color.
    """
    # Arrange
    color = "#FFFFFF"
    factor = 0.5

    # Act
    result = adjust_brightness(color, factor)

    # Assert
    assert result != color  # Should be darker


def test_adjust_brightness_negative_factor_raises_error() -> None:

    """
    Test case 6: ValueError for negative brightness factor.
    """
    # Arrange
    expected_message = "factor must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        adjust_brightness("#FF0000", factor=-0.5)


def test_adjust_brightness_zero_factor_raises_error() -> None:

    """
    Test case 7: ValueError for zero brightness factor.
    """
    # Arrange
    expected_message = "factor must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        adjust_brightness("#FF0000", factor=0)


def test_adjust_brightness_invalid_color_raises_error() -> None:

    """
    Test case 8: ValueError for invalid hex color.
    """
    # Arrange
    expected_message = "Invalid color specification"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        adjust_brightness("invalid", factor=1.0)


def test_adjust_brightness_invalid_type_raises_error() -> None:

    """
    Test case 9: TypeError for invalid color type.
    """
    # Arrange
    expected_message = "color must be a string"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        adjust_brightness(123, factor=1.0)


__all__ = ["test_adjust_brightness_lighten"]
