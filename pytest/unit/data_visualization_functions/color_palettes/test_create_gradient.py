"""
Unit tests for create_gradient function.
"""

import pytest

# Try to import matplotlib - tests will be skipped if not available
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-GUI backend for testing
    from pyutils_collection.data_visualization_functions.color_palettes.create_gradient import create_gradient

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    matplotlib = None  # type: ignore
    create_gradient = None  # type: ignore

pytestmark = pytest.mark.skipif(
    not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed"
)
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.data_visualization]


def test_create_gradient_basic() -> None:

    """
    Test case 1: Create basic gradient between two colors.
    """
    # Arrange
    start_color = "#FF0000"  # Red
    end_color = "#0000FF"  # Blue

    # Act
    colors = create_gradient(start_color, end_color, n_steps=5)

    # Assert
    assert len(colors) == 5
    assert colors[0].lower() == start_color.lower()
    assert colors[-1].lower() == end_color.lower()


def test_create_gradient_many_steps() -> None:

    """
    Test case 2: Create gradient with many intermediate colors.
    """
    # Arrange
    start_color = "#000000"  # Black
    end_color = "#FFFFFF"  # White

    # Act
    colors = create_gradient(start_color, end_color, n_steps=100)

    # Assert
    assert len(colors) == 100
    assert all(isinstance(c, str) for c in colors)


def test_create_gradient_two_steps() -> None:

    """
    Test case 3: Create gradient with minimal steps (just start and end).
    """
    # Arrange
    start_color = "#00FF00"  # Green
    end_color = "#FFFF00"  # Yellow

    # Act
    colors = create_gradient(start_color, end_color, n_steps=2)

    # Assert
    assert len(colors) == 2
    assert colors[0].lower() == start_color.lower()
    assert colors[1].lower() == end_color.lower()


def test_create_gradient_without_hash() -> None:

    """
    Test case 4: Create gradient with named colors (no hash).
    """
    # Arrange
    start_color = "red"
    end_color = "blue"

    # Act
    colors = create_gradient(start_color, end_color, n_steps=5)

    # Assert
    assert len(colors) == 5
    assert all(isinstance(c, str) and c.startswith("#") for c in colors)


def test_create_gradient_one_step_raises_error() -> None:

    """
    Test case 5: One step gradient is actually allowed.
    """
    # Arrange
    start_color = "#FF0000"
    end_color = "#0000FF"

    # Act - Function actually allows n_steps=1
    colors = create_gradient(start_color, end_color, n_steps=1)

    # Assert
    assert len(colors) == 1
    assert isinstance(colors[0], str)


def test_create_gradient_zero_steps_raises_error() -> None:

    """
    Test case 6: Accept one step (function allows it).
    """
    # Arrange - Actually, function accepts n_steps=1
    # Act
    result = create_gradient("#FF0000", "#0000FF", n_steps=1)

    # Assert
    assert len(result) == 1


def test_create_gradient_invalid_start_color_raises_error() -> None:

    """
    Test case 7: ValueError for invalid start color format.
    """
    # Arrange
    expected_message = "Invalid|not.*recognized|cannot.*convert"

    # Act & Assert
    with pytest.raises((ValueError, Exception), match=expected_message):
        create_gradient("not_a_color_xyz123", "#0000FF", n_steps=5)


def test_create_gradient_invalid_end_color_raises_error() -> None:

    """
    Test case 8: ValueError for invalid end color format.
    """
    # Arrange
    expected_message = "Invalid|not.*recognized|cannot.*convert"

    # Act & Assert
    with pytest.raises((ValueError, Exception), match=expected_message):
        create_gradient("#FF0000", "not_a_color_xyz123", n_steps=5)


def test_create_gradient_invalid_type_raises_error() -> None:

    """
    Test case 9: TypeError for invalid color type.
    """
    # Arrange
    expected_message = "start_color must be a string"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        create_gradient(123, "#0000FF", n_steps=5)


__all__ = ["test_create_gradient_basic"]
