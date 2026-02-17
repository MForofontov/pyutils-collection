"""
Unit tests for rgb_to_hex function.
"""

import pytest

try:
    import matplotlib
    from pyutils_collection.data_visualization_functions.color_palettes.rgb_to_hex import rgb_to_hex
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    matplotlib = None  # type: ignore
    rgb_to_hex = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.data_visualization,
    pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed"),
]


def test_rgb_to_hex_red() -> None:

    """
    Test case 1: Convert red RGB to hex.
    """
    # Arrange
    r, g, b = 255, 0, 0
    expected = "#FF0000"

    # Act
    result = rgb_to_hex(r, g, b)

    # Assert
    assert result == expected


def test_rgb_to_hex_green() -> None:

    """
    Test case 2: Convert green RGB to hex.
    """
    # Arrange
    r, g, b = 0, 255, 0
    expected = "#00FF00"

    # Act
    result = rgb_to_hex(r, g, b)

    # Assert
    assert result == expected


def test_rgb_to_hex_mixed() -> None:

    """
    Test case 3: Convert mixed RGB values to hex.
    """
    # Arrange
    r, g, b = 128, 64, 192
    expected = "#8040C0"

    # Act
    result = rgb_to_hex(r, g, b)

    # Assert
    assert result == expected


def test_rgb_to_hex_black() -> None:

    """
    Test case 4: Convert black RGB to hex.
    """
    # Arrange
    r, g, b = 0, 0, 0
    expected = "#000000"

    # Act
    result = rgb_to_hex(r, g, b)

    # Assert
    assert result == expected


def test_rgb_to_hex_white() -> None:

    """
    Test case 5: Convert white RGB to hex.
    """
    # Arrange
    r, g, b = 255, 255, 255
    expected = "#FFFFFF"

    # Act
    result = rgb_to_hex(r, g, b)

    # Assert
    assert result == expected


def test_rgb_to_hex_r_out_of_range_raises_error() -> None:

    """
    Test case 6: ValueError for r value out of range.
    """
    # Arrange
    r, g, b = 256, 0, 0
    expected_message = "r must be in range"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        rgb_to_hex(r, g, b)


def test_rgb_to_hex_negative_value_raises_error() -> None:

    """
    Test case 7: ValueError for negative RGB value.
    """
    # Arrange
    r, g, b = 100, -1, 100
    expected_message = "g must be in range"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        rgb_to_hex(r, g, b)


def test_rgb_to_hex_invalid_type_raises_error() -> None:

    """
    Test case 8: TypeError for non-integer input.
    """
    # Arrange
    r, g, b = "255", 0, 0
    expected_message = "r must be an integer"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        rgb_to_hex(r, g, b)
