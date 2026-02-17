"""
Unit tests for create_line_plot function.
"""

import pytest

# Try to import matplotlib and numpy - tests will be skipped if not available
try:
    import matplotlib.pyplot as plt
    import numpy as np

    from pyutils_collection.data_visualization_functions.plot_generation import create_line_plot

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None  # type: ignore
    np = None  # type: ignore
    create_line_plot = None  # type: ignore

pytestmark = pytest.mark.skipif(
    not MATPLOTLIB_AVAILABLE, reason="matplotlib or numpy not installed"
)
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.data_visualization]


def test_create_line_plot_single_series() -> None:

    """
    Test case 1: Create line plot with single series.
    """
    # Arrange
    x = [1, 2, 3, 4, 5]
    y = [1, 4, 9, 16, 25]

    # Act
    fig, ax = create_line_plot(x, y, title="Squared", xlabel="X", ylabel="Y")

    # Assert
    assert fig is not None
    assert ax is not None
    assert ax.get_title() == "Squared"
    assert ax.get_xlabel() == "X"
    assert ax.get_ylabel() == "Y"
    assert len(ax.lines) == 1
    plt.close(fig)


def test_create_line_plot_multiple_series() -> None:

    """
    Test case 2: Create line plot with multiple series.
    """
    # Arrange
    x = [1, 2, 3, 4]
    y = [[1, 4, 9, 16], [1, 2, 3, 4]]
    labels = ["Squared", "Linear"]

    # Act
    fig, ax = create_line_plot(x, y, labels=labels, title="Multi Series")

    # Assert
    assert len(ax.lines) == 2
    legend = ax.get_legend()
    assert legend is not None
    legend_texts = [t.get_text() for t in legend.get_texts()]
    assert "Squared" in legend_texts
    assert "Linear" in legend_texts
    plt.close(fig)


def test_create_line_plot_with_grid_and_markers() -> None:

    """
    Test case 3: Create line plot with grid and markers enabled.
    """
    # Arrange
    x = [1, 2, 3]
    y = [2, 4, 6]

    # Act
    fig, ax = create_line_plot(x, y, grid=True, markers=["o"])

    # Assert
    assert ax.grid
    assert ax.lines[0].get_marker() == "o"
    plt.close(fig)


def test_create_line_plot_numpy_arrays() -> None:

    """
    Test case 4: Create line plot with numpy arrays.
    """
    # Arrange
    x = np.array([0, 1, 2, 3, 4])
    y = np.array([0, 1, 4, 9, 16])

    # Act
    fig, ax = create_line_plot(x, y)

    # Assert
    assert len(ax.lines) == 1
    line_data = ax.lines[0].get_ydata()
    np.testing.assert_array_equal(line_data, y)
    plt.close(fig)


def test_create_line_plot_empty_x_raises_error() -> None:

    """
    Test case 5: ValueError for empty x data.
    """
    # Arrange
    x = []
    y = [1, 2, 3]
    expected_message = "x_data cannot be empty"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        create_line_plot(x, y)


def test_create_line_plot_empty_y_raises_error() -> None:

    """
    Test case 6: ValueError for empty y data.
    """
    # Arrange
    x = [1, 2, 3]
    y = []
    expected_message = "y_data series 0 length .* must match x_data length"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        create_line_plot(x, y)


def test_create_line_plot_mismatched_lengths_raises_error() -> None:

    """
    Test case 7: ValueError when x and y lengths don't match.
    """
    # Arrange
    x = [1, 2, 3]
    y = [1, 4, 9, 16]
    expected_message = "y_data series 0 length .* must match x_data length"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        create_line_plot(x, y)


def test_create_line_plot_invalid_x_type_raises_error() -> None:

    """
    Test case 8: TypeError for invalid x data type.
    """
    # Arrange
    x = "invalid"
    y = [1, 2, 3]
    expected_message = "x_data must be a list or numpy array"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        create_line_plot(x, y)


def test_create_line_plot_invalid_figsize_raises_error() -> None:

    """
    Test case 9: ValueError for negative figsize.
    """
    # Arrange
    x = [1, 2, 3]
    y = [1, 2, 3]

    # Act & Assert
    with pytest.raises(ValueError, match="figsize dimensions must be positive"):
        create_line_plot(x, y, figsize=(-10, 6))


def test_create_line_plot_custom_colors() -> None:

    """
    Test case 10: Create line plot with custom colors.
    """
    # Arrange
    x = [1, 2, 3]
    y = [[1, 2, 3], [2, 4, 6]]
    colors = ["red", "blue"]

    # Act
    fig, ax = create_line_plot(x, y, colors=colors)

    # Assert
    assert len(ax.lines) == 2
    plt.close(fig)
