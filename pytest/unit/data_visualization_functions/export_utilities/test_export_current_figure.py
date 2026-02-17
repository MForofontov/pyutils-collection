"""
Unit tests for export_current_figure function.
"""

import os
import tempfile

import pytest

# Try to import matplotlib - tests will be skipped if not available
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-GUI backend for testing
    import matplotlib.pyplot as plt

    from pyutils_collection.data_visualization_functions.export_utilities.export_current_figure import (
        export_current_figure,
    )

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    matplotlib = None  # type: ignore
    plt = None  # type: ignore
    export_current_figure = None  # type: ignore

pytestmark = pytest.mark.skipif(
    not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed"
)
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.data_visualization]


def test_export_current_figure_basic() -> None:

    """
    Test case 1: Export current figure to file.
    """
    # Arrange
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    plt.figure(fig.number)  # Make it the current figure

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "current_fig.png")

        # Act
        export_current_figure(filepath)

        # Assert
        assert os.path.exists(filepath)

    # Cleanup
    plt.close(fig)


def test_export_current_figure_pdf() -> None:

    """
    Test case 2: Export current figure as PDF.
    """
    # Arrange
    fig, ax = plt.subplots()
    ax.bar(["A", "B", "C"], [10, 20, 15])
    plt.figure(fig.number)

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "plot.pdf")

        # Act
        export_current_figure(filepath)

        # Assert
        assert os.path.exists(filepath)

    # Cleanup
    plt.close(fig)


def test_export_current_figure_with_dpi() -> None:

    """
    Test case 3: Export with custom DPI.
    """
    # Arrange
    fig, ax = plt.subplots()
    ax.scatter([1, 2, 3], [1, 2, 3])
    plt.figure(fig.number)

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "high_res.png")

        # Act
        export_current_figure(filepath, dpi=300)

        # Assert
        assert os.path.exists(filepath)

    # Cleanup
    plt.close(fig)


def test_export_current_figure_creates_directory() -> None:

    """
    Test case 4: Export creates directory if it doesn't exist.
    """
    # Arrange
    fig, ax = plt.subplots()
    ax.plot([1, 2], [1, 2])
    plt.figure(fig.number)

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "subdir", "nested", "plot.png")

        # Act
        export_current_figure(filepath)

        # Assert
        assert os.path.exists(filepath)

    # Cleanup
    plt.close(fig)


def test_export_current_figure_no_current_raises_error() -> None:

    """
    Test case 5: ValueError when no current figure exists.
    """
    # Arrange
    plt.close("all")  # Close all figures
    expected_message = "No active figure to export"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        export_current_figure("test.png")


def test_export_current_figure_invalid_filepath_raises_error() -> None:

    """
    Test case 6: TypeError for invalid filepath.
    """
    # Arrange
    fig, ax = plt.subplots()
    plt.figure(fig.number)
    expected_message = "filepath must be a string"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        export_current_figure(123)

    # Cleanup
    plt.close(fig)


def test_export_current_figure_empty_filepath_raises_error() -> None:

    """
    Test case 7: ValueError for empty filepath.
    """
    # Arrange
    fig, ax = plt.subplots()
    plt.figure(fig.number)
    expected_message = "filepath must have an extension"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        export_current_figure("")

    # Cleanup
    plt.close(fig)


def test_export_current_figure_invalid_dpi_raises_error() -> None:

    """
    Test case 8: ValueError for invalid DPI.
    """
    # Arrange
    fig, ax = plt.subplots()
    plt.figure(fig.number)
    expected_message = "dpi must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        export_current_figure("test.png", dpi=0)

    # Cleanup
    plt.close(fig)


__all__ = ["test_export_current_figure_basic"]
