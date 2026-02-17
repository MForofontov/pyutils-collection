"""
Unit tests for hex_to_rgb function.
"""

import pytest

try:
    import matplotlib
    from pyutils_collection.data_visualization_functions.color_palettes.hex_to_rgb import hex_to_rgb
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    matplotlib = None  # type: ignore
    hex_to_rgb = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.data_visualization,
    pytest.mark.skipif(not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed"),
]


def test_hex_to_rgb_with_hash() -> None:

    """
    Test case 1: Convert hex color with # prefix.
    """
    # Arrange
    hex_color = "#FF0000"
    expected = (255, 0, 0)

    # Act
    result = hex_to_rgb(hex_color)

    # Assert
    assert result == expected


def test_hex_to_rgb_without_hash() -> None:

    """
    Test case 2: Convert hex color without # prefix.
    """
    # Arrange
    hex_color = "00FF00"
    expected = (0, 255, 0)

    # Act
    result = hex_to_rgb(hex_color)

    # Assert
    assert result == expected


def test_hex_to_rgb_blue() -> None:

    """
    Test case 3: Convert blue hex color.
    """
    # Arrange
    hex_color = "#0000FF"
    expected = (0, 0, 255)

    # Act
    result = hex_to_rgb(hex_color)

    # Assert
    assert result == expected


def test_hex_to_rgb_mixed_case() -> None:

    """
    Test case 4: Convert mixed case hex color.
    """
    # Arrange
    hex_color = "#AbCdEf"
    expected = (171, 205, 239)

    # Act
    result = hex_to_rgb(hex_color)

    # Assert
    assert result == expected


def test_hex_to_rgb_invalid_length_raises_error() -> None:

    """
    Test case 5: ValueError for invalid hex length.
    """
    # Arrange
    hex_color = "#FFF"
    expected_message = "hex_color must be 6 characters"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        hex_to_rgb(hex_color)


def test_hex_to_rgb_invalid_characters_raises_error() -> None:

    """
    Test case 6: ValueError for invalid hex characters.
    """
    # Arrange
    hex_color = "GGGGGG"
    expected_message = "Invalid hex color code"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        hex_to_rgb(hex_color)


def test_hex_to_rgb_invalid_type_raises_error() -> None:

    """
    Test case 7: TypeError for non-string input.
    """
    # Arrange
    hex_color = 123456
    expected_message = "hex_color must be a string"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        hex_to_rgb(hex_color)
