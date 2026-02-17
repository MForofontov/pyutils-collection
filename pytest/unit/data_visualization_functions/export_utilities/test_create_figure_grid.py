"""
Unit tests for create_figure_grid function.
"""

import pytest

# Try to import matplotlib - tests will be skipped if not available
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-GUI backend for testing
    import matplotlib.pyplot as plt

    from pyutils_collection.data_visualization_functions.export_utilities.create_figure_grid import (
        create_figure_grid,
    )

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    matplotlib = None  # type: ignore
    plt = None  # type: ignore
    create_figure_grid = None  # type: ignore

pytestmark = pytest.mark.skipif(
    not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed"
)
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.data_visualization]


def test_create_figure_grid_basic() -> None:

    """
    Test case 1: Create basic figure grid.
    """
    # Act
    fig, axes = create_figure_grid(nrows=2, ncols=2)

    # Assert
    assert fig is not None
    assert axes is not None
    assert len(axes) == 2
    assert len(axes[0]) == 2

    # Cleanup
    plt.close(fig)


def test_create_figure_grid_single_row() -> None:

    """
    Test case 2: Create figure grid with single row.
    """
    # Act
    fig, axes = create_figure_grid(nrows=1, ncols=4)

    # Assert
    assert axes.shape == (1, 4) or len(axes) == 4

    # Cleanup
    plt.close(fig)


def test_create_figure_grid_single_col() -> None:

    """
    Test case 3: Create figure grid with single column.
    """
    # Act
    fig, axes = create_figure_grid(nrows=3, ncols=1)

    # Assert
    assert axes.shape == (3, 1) or len(axes) == 3

    # Cleanup
    plt.close(fig)


def test_create_figure_grid_large() -> None:

    """
    Test case 4: Create large figure grid.
    """
    # Act
    fig, axes = create_figure_grid(nrows=4, ncols=5)

    # Assert
    assert len(axes) == 4
    assert len(axes[0]) == 5

    # Cleanup
    plt.close(fig)


def test_create_figure_grid_custom_size() -> None:

    """
    Test case 5: Create figure grid with custom size.
    """
    # Act
    fig, axes = create_figure_grid(nrows=2, ncols=2, figsize=(12, 8))

    # Assert
    size = fig.get_size_inches()
    assert size[0] == 12
    assert size[1] == 8

    # Cleanup
    plt.close(fig)


def test_create_figure_grid_zero_rows_raises_error() -> None:

    """
    Test case 6: ValueError for zero rows.
    """
    # Arrange
    expected_message = "nrows must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        create_figure_grid(nrows=0, ncols=2)


def test_create_figure_grid_zero_cols_raises_error() -> None:

    """
    Test case 7: ValueError for zero columns.
    """
    # Arrange
    expected_message = "ncols must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        create_figure_grid(nrows=2, ncols=0)


def test_create_figure_grid_invalid_type_raises_error() -> None:

    """
    Test case 8: TypeError for invalid row/col type.
    """
    # Arrange
    expected_message = "nrows must be an integer"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        create_figure_grid(nrows="2", ncols=2)


def test_create_figure_grid_invalid_figsize_raises_error() -> None:

    """
    Test case 9: ValueError for invalid figsize.
    """
    # Arrange
    expected_message = "figsize must be a tuple of .* positive numbers|must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        create_figure_grid(nrows=2, ncols=2, figsize=(10, -5))


__all__ = ["test_create_figure_grid_basic"]
