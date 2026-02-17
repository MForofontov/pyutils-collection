"""
Unit tests for configure_export_defaults function.
"""

import pytest

# Try to import matplotlib - tests will be skipped if not available
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-GUI backend for testing
    import matplotlib.pyplot as plt

    from pyutils_collection.data_visualization_functions.export_utilities.configure_export_defaults import (
        configure_export_defaults,
    )

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    matplotlib = None  # type: ignore
    plt = None  # type: ignore
    configure_export_defaults = None  # type: ignore

pytestmark = pytest.mark.skipif(
    not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed"
)
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.data_visualization]


def test_configure_export_defaults_basic() -> None:

    """
    Test case 1: Configure export defaults with basic settings.
    """
    # Act
    configure_export_defaults(dpi=150, format="png")

    # Assert
    assert plt.rcParams["savefig.dpi"] == 150
    assert plt.rcParams["savefig.format"] == "png"


def test_configure_export_defaults_high_dpi() -> None:

    """
    Test case 2: Configure with high DPI for publication.
    """
    # Act
    configure_export_defaults(dpi=300)

    # Assert
    assert plt.rcParams["savefig.dpi"] == 300


def test_configure_export_defaults_pdf_format() -> None:

    """
    Test case 3: Configure for PDF export.
    """
    # Act
    configure_export_defaults(format="pdf")

    # Assert
    assert plt.rcParams["savefig.format"] == "pdf"


def test_configure_export_defaults_transparent() -> None:

    """
    Test case 4: Configure with transparent background.
    """
    # Act
    configure_export_defaults(transparent=True)

    # Assert
    assert plt.rcParams["savefig.transparent"]


def test_configure_export_defaults_bbox_tight() -> None:

    """
    Test case 5: Configure with tight bounding box.
    """
    # Act
    configure_export_defaults(bbox_inches="tight")

    # Assert
    assert plt.rcParams["savefig.bbox"] == "tight"


def test_configure_export_defaults_invalid_dpi_raises_error() -> None:

    """
    Test case 6: ValueError for invalid DPI.
    """
    # Arrange
    expected_message = "dpi must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        configure_export_defaults(dpi=-100)


def test_configure_export_defaults_zero_dpi_raises_error() -> None:

    """
    Test case 7: ValueError for zero DPI.
    """
    # Arrange
    expected_message = "dpi must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        configure_export_defaults(dpi=0)


def test_configure_export_defaults_invalid_format_raises_error() -> None:

    """
    Test case 8: ValueError for invalid format.
    """
    # Arrange
    expected_message = "format must be one of"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        configure_export_defaults(format="invalid_format")


def test_configure_export_defaults_invalid_type_raises_error() -> None:

    """
    Test case 9: TypeError for invalid DPI type.
    """
    # Arrange
    expected_message = "dpi must be|must be a number"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        configure_export_defaults(dpi="150")


__all__ = ["test_configure_export_defaults_basic"]
