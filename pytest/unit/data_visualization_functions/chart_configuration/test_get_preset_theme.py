"""
Unit tests for get_preset_theme function.
"""

import pytest

# Try to import matplotlib - tests will be skipped if not available
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-GUI backend for testing
    from pyutils_collection.data_visualization_functions.chart_configuration.chart_theme import ChartTheme
    from pyutils_collection.data_visualization_functions.chart_configuration.get_preset_theme import (
        get_preset_theme,
    )

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    matplotlib = None  # type: ignore
    ChartTheme = None  # type: ignore
    get_preset_theme = None  # type: ignore

pytestmark = pytest.mark.skipif(
    not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed"
)
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.data_visualization]


def test_get_preset_theme_default() -> None:

    """
    Test case 1: Get default theme.
    """
    # Act
    theme = get_preset_theme("default")

    # Assert
    assert isinstance(theme, ChartTheme)
    assert theme.name == "default"


def test_get_preset_theme_dark() -> None:

    """
    Test case 2: Get dark theme.
    """
    # Act
    theme = get_preset_theme("dark")

    # Assert
    assert isinstance(theme, ChartTheme)
    assert theme.name == "dark"


def test_get_preset_theme_minimal() -> None:

    """
    Test case 3: Get minimal theme.
    """
    # Act
    theme = get_preset_theme("minimal")

    # Assert
    assert isinstance(theme, ChartTheme)
    assert theme.name == "minimal"


def test_get_preset_theme_scientific() -> None:

    """
    Test case 4: Get publication theme (scientific is not a valid theme).
    """
    # Act
    theme = get_preset_theme("publication")

    # Assert
    assert isinstance(theme, ChartTheme)
    assert theme.name == "publication"


def test_get_preset_theme_invalid_name_raises_error() -> None:

    """
    Test case 5: ValueError for non-existent theme.
    """
    # Arrange
    invalid_name = "nonexistent_theme"
    expected_message = "theme_name must be one of|not found"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        get_preset_theme(invalid_name)


def test_get_preset_theme_empty_string_raises_error() -> None:

    """
    Test case 6: ValueError for empty theme name.
    """
    # Arrange
    expected_message = "theme_name must be one of|cannot be empty"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        get_preset_theme("")


def test_get_preset_theme_invalid_type_raises_error() -> None:

    """
    Test case 7: TypeError for invalid type.
    """
    # Arrange
    expected_message = "theme_name must be a string"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        get_preset_theme(123)


__all__ = ["test_get_preset_theme_default"]
