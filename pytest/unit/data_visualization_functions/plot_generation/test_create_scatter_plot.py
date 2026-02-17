"""
Unit tests for create_scatter_plot function.
"""

import pytest

# Try to import matplotlib and numpy - tests will be skipped if not available
try:
    import matplotlib.pyplot as plt
    import numpy as np

    from pyutils_collection.data_visualization_functions.plot_generation import create_scatter_plot

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None  # type: ignore
    np = None  # type: ignore
    create_scatter_plot = None  # type: ignore

pytestmark = pytest.mark.skipif(
    not MATPLOTLIB_AVAILABLE, reason="matplotlib or numpy not installed"
)
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.data_visualization]


def test_create_scatter_plot_basic() -> None:

    """
    Test case 1: Create basic scatter plot.
    """
    # Arrange
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 5, 7, 8]

    # Act
    fig, ax = create_scatter_plot(x, y, title="Basic Scatter")

    # Assert
    assert fig is not None
    assert ax is not None
    assert ax.get_title() == "Basic Scatter"
    assert len(ax.collections) == 1
    plt.close(fig)


def test_create_scatter_plot_with_styling() -> None:

    """
    Test case 2: Create scatter plot with custom styling.
    """
    # Arrange
    x = [1, 2, 3]
    y = [4, 5, 6]

    # Act
    fig, ax = create_scatter_plot(x, y, colors="red", sizes=100, alpha=0.8, marker="s")

    # Assert
    scatter = ax.collections[0]
    assert scatter.get_alpha() == 0.8
    plt.close(fig)


def test_create_scatter_plot_numpy_arrays() -> None:

    """
    Test case 3: Create scatter plot with numpy arrays.
    """
    # Arrange
    np.random.seed(42)
    x = np.random.randn(50)
    y = 2 * x + np.random.randn(50) * 0.5

    # Act
    fig, ax = create_scatter_plot(x, y, xlabel="X", ylabel="Y")

    # Assert
    assert ax.get_xlabel() == "X"
    assert ax.get_ylabel() == "Y"
    assert len(ax.collections[0].get_offsets()) == 50
    plt.close(fig)


def test_create_scatter_plot_with_grid() -> None:

    """
    Test case 4: Create scatter plot with grid enabled.
    """
    # Arrange
    x = [1, 2, 3, 4]
    y = [2, 3, 4, 5]

    # Act
    fig, ax = create_scatter_plot(x, y, grid=True)

    # Assert
    assert ax.grid
    plt.close(fig)


def test_create_scatter_plot_empty_x_raises_error() -> None:

    """
    Test case 5: ValueError for empty x data.
    """
    # Arrange
    x = []
    y = [1, 2, 3]
    expected_message = "x_data cannot be empty"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        create_scatter_plot(x, y)


def test_create_scatter_plot_mismatched_lengths_raises_error() -> None:

    """
    Test case 6: ValueError when x and y lengths don't match.
    """
    # Arrange
    x = [1, 2, 3]
    y = [1, 2]
    expected_message = "x_data length .* must match y_data length"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        create_scatter_plot(x, y)


def test_create_scatter_plot_invalid_alpha_raises_error() -> None:

    """
    Test case 7: ValueError for alpha outside [0, 1] range.
    """
    # Arrange
    x = [1, 2, 3]
    y = [1, 2, 3]

    # Act & Assert
    with pytest.raises(ValueError, match="alpha must be between 0 and 1"):
        create_scatter_plot(x, y, alpha=1.5)


def test_create_scatter_plot_invalid_x_type_raises_error() -> None:

    """
    Test case 8: TypeError for invalid x data type.
    """
    # Arrange
    x = "invalid"
    y = [1, 2, 3]
    expected_message = "x_data must be a list or numpy array"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        create_scatter_plot(x, y)


def test_create_scatter_plot_invalid_figsize_raises_error() -> None:

    """
    Test case 9: ValueError for negative figsize.
    """
    # Arrange
    x = [1, 2, 3]
    y = [1, 2, 3]

    # Act & Assert
    with pytest.raises(ValueError, match="figsize dimensions must be positive"):
        create_scatter_plot(x, y, figsize=(10, -6))
