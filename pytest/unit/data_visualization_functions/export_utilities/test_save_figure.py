"""
Unit tests for save_figure function.
"""

import shutil
import tempfile
from pathlib import Path

import pytest

# Try to import matplotlib - tests will be skipped if not available
try:
    import matplotlib.pyplot as plt

    from pyutils_collection.data_visualization_functions.export_utilities import save_figure

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None  # type: ignore
    save_figure = None  # type: ignore

pytestmark = pytest.mark.skipif(
    not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed"
)
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.data_visualization]


def test_save_figure_png() -> None:

    """
    Test case 1: Save figure as PNG.
    """
    # Arrange
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    temp_dir = tempfile.mkdtemp()
    filepath = Path(temp_dir) / "test.png"

    try:
        # Act
        save_figure(fig, filepath)

        # Assert
        assert filepath.exists()
        assert filepath.stat().st_size > 0
    finally:
        plt.close(fig)
        shutil.rmtree(temp_dir)


def test_save_figure_pdf() -> None:

    """
    Test case 2: Save figure as PDF.
    """
    # Arrange
    fig, ax = plt.subplots()
    ax.scatter([1, 2, 3], [4, 5, 6])
    temp_dir = tempfile.mkdtemp()
    filepath = Path(temp_dir) / "test.pdf"

    try:
        # Act
        save_figure(fig, filepath, dpi=150)

        # Assert
        assert filepath.exists()
    finally:
        plt.close(fig)
        shutil.rmtree(temp_dir)


def test_save_figure_with_transparent_background() -> None:

    """
    Test case 3: Save figure with transparent background.
    """
    # Arrange
    fig, ax = plt.subplots()
    ax.plot([1, 2], [3, 4])
    temp_dir = tempfile.mkdtemp()
    filepath = Path(temp_dir) / "transparent.png"

    try:
        # Act
        save_figure(fig, filepath, transparent=True)

        # Assert
        assert filepath.exists()
    finally:
        plt.close(fig)
        shutil.rmtree(temp_dir)


def test_save_figure_creates_directory() -> None:

    """
    Test case 4: Save figure creates parent directories.
    """
    # Arrange
    fig, ax = plt.subplots()
    ax.plot([1], [1])
    temp_dir = tempfile.mkdtemp()
    filepath = Path(temp_dir) / "subdir" / "nested" / "test.png"

    try:
        # Act
        save_figure(fig, filepath)

        # Assert
        assert filepath.exists()
        assert filepath.parent.exists()
    finally:
        plt.close(fig)
        shutil.rmtree(temp_dir)


def test_save_figure_invalid_type_raises_error() -> None:

    """
    Test case 5: TypeError for non-Figure object.
    """
    # Arrange
    not_a_figure = "invalid"
    expected_message = "fig must be a Figure object"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        save_figure(not_a_figure, "test.png")


def test_save_figure_no_extension_raises_error() -> None:

    """
    Test case 6: ValueError for filepath without extension.
    """
    # Arrange
    fig, ax = plt.subplots()
    expected_message = "filepath must have an extension"

    try:
        # Act & Assert
        with pytest.raises(ValueError, match=expected_message):
            save_figure(fig, "noextension")
    finally:
        plt.close(fig)


def test_save_figure_invalid_dpi_raises_error() -> None:

    """
    Test case 7: ValueError for negative DPI.
    """
    # Arrange
    fig, ax = plt.subplots()
    expected_message = "dpi must be positive"

    try:
        # Act & Assert
        with pytest.raises(ValueError, match=expected_message):
            save_figure(fig, "test.png", dpi=-100)
    finally:
        plt.close(fig)
