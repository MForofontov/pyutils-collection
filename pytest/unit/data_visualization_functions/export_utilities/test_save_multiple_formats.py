"""
Unit tests for save_multiple_formats function.
"""

import os
import tempfile

import pytest

# Try to import matplotlib - tests will be skipped if not available
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-GUI backend for testing
    import matplotlib.pyplot as plt

    from pyutils_collection.data_visualization_functions.export_utilities.save_multiple_formats import (
        save_multiple_formats,
    )

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    matplotlib = None  # type: ignore
    plt = None  # type: ignore
    save_multiple_formats = None  # type: ignore

pytestmark = pytest.mark.skipif(
    not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed"
)
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.data_visualization]


def test_save_multiple_formats_basic() -> None:

    """
    Test case 1: Save figure in multiple formats.
    """
    # Arrange
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 2, 3])

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "test_plot")
        formats = ["png", "pdf"]

        # Act
        result = save_multiple_formats(fig, base_path, formats=formats)

        # Assert
        assert len(result) == 2
        assert os.path.exists(f"{base_path}.png")
        assert os.path.exists(f"{base_path}.pdf")

    # Cleanup
    plt.close(fig)


def test_save_multiple_formats_single_format() -> None:

    """
    Test case 2: Save figure in single format.
    """
    # Arrange
    fig, ax = plt.subplots()
    ax.plot([1, 2], [1, 2])

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "single")
        formats = ["svg"]

        # Act
        result = save_multiple_formats(fig, base_path, formats=formats)

        # Assert
        assert len(result) == 1
        assert os.path.exists(f"{base_path}.svg")

    # Cleanup
    plt.close(fig)


def test_save_multiple_formats_many_formats() -> None:

    """
    Test case 3: Save figure in many formats.
    """
    # Arrange
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "multi")
        formats = ["png", "pdf", "svg", "jpg"]

        # Act
        result = save_multiple_formats(fig, base_path, formats=formats)

        # Assert
        assert len(result) == 4
        for fmt in formats:
            assert os.path.exists(f"{base_path}.{fmt}")

    # Cleanup
    plt.close(fig)


def test_save_multiple_formats_custom_dpi() -> None:

    """
    Test case 4: Save with custom DPI.
    """
    # Arrange
    fig, ax = plt.subplots()
    ax.plot([1, 2], [1, 2])

    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, "high_dpi")
        formats = ["png"]

        # Act
        save_multiple_formats(fig, base_path, formats=formats, dpi=300)

        # Assert
        assert os.path.exists(f"{base_path}.png")

    # Cleanup
    plt.close(fig)


def test_save_multiple_formats_invalid_fig_raises_error() -> None:

    """
    Test case 5: TypeError for invalid figure.
    """
    # Arrange
    expected_message = "fig must be.*Figure|must be.*matplotlib"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        save_multiple_formats("not_a_figure", "path", formats=["png"])


def test_save_multiple_formats_empty_formats_raises_error() -> None:

    """
    Test case 6: ValueError for empty formats list.
    """
    # Arrange
    fig, ax = plt.subplots()
    expected_message = "formats cannot be empty|formats.*empty"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        save_multiple_formats(fig, "path", formats=[])

    # Cleanup
    plt.close(fig)


def test_save_multiple_formats_invalid_format_raises_error() -> None:

    """
    Test case 7: ValueError for invalid format.
    """
    # Arrange
    fig, ax = plt.subplots()
    expected_message = "Invalid format"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        save_multiple_formats(fig, "path", formats=["invalid_format"])

    # Cleanup
    plt.close(fig)


def test_save_multiple_formats_invalid_dpi_raises_error() -> None:

    """
    Test case 8: ValueError for invalid DPI.
    """
    # Arrange
    fig, ax = plt.subplots()
    expected_message = "dpi must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        save_multiple_formats(fig, "path", formats=["png"], dpi=-100)

    # Cleanup
    plt.close(fig)


__all__ = ["test_save_multiple_formats_basic"]
