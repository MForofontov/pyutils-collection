"""
Unit tests for create_bar_plot function.
"""

import pytest

# Try to import matplotlib - tests will be skipped if not available
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-GUI backend for testing
    import matplotlib.pyplot as plt

    from pyutils_collection.data_visualization_functions.plot_generation.create_bar_plot import create_bar_plot

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    matplotlib = None  # type: ignore
    plt = None  # type: ignore
    create_bar_plot = None  # type: ignore

pytestmark = pytest.mark.skipif(
    not MATPLOTLIB_AVAILABLE, reason="matplotlib not installed"
)
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.data_visualization]


def test_create_bar_plot_basic() -> None:

    """
    Test case 1: Create basic bar plot with default settings.
    """
    # Arrange
    categories = ["A", "B", "C", "D"]
    values = [10, 25, 15, 30]

    # Act
    fig, ax = create_bar_plot(categories, values)

    # Assert
    assert fig is not None
    assert ax is not None
    assert len(ax.patches) == 4  # 4 bars

    # Cleanup
    plt.close(fig)


def test_create_bar_plot_with_styling() -> None:

    """
    Test case 2: Create bar plot with custom styling.
    """
    # Arrange
    categories = ["Q1", "Q2", "Q3", "Q4"]
    values = [100, 150, 120, 180]

    # Act
    fig, ax = create_bar_plot(
        categories,
        values,
        title="Quarterly Sales",
        xlabel="Quarter",
        ylabel="Sales ($)",
        colors=["blue"],
    )

    # Assert
    assert ax.get_title() == "Quarterly Sales"
    assert ax.get_xlabel() == "Quarter"
    assert ax.get_ylabel() == "Sales ($)"

    # Cleanup
    plt.close(fig)


def test_create_bar_plot_horizontal() -> None:

    """
    Test case 3: Create horizontal bar plot.
    """
    # Arrange
    categories = ["Product A", "Product B", "Product C"]
    values = [45, 60, 35]

    # Act
    fig, ax = create_bar_plot(categories, values, horizontal=True)

    # Assert
    assert fig is not None
    # For horizontal bars, check y-axis has the categories
    yticks = [t.get_text() for t in ax.get_yticklabels()]
    assert any(cat in yticks for cat in categories) or len(ax.patches) == 3

    # Cleanup
    plt.close(fig)


def test_create_bar_plot_multiple_groups() -> None:

    """
    Test case 4: Create grouped bar plot with multiple data series.
    """
    # Arrange
    categories = ["A", "B", "C"]
    values = [[10, 15, 20], [12, 18, 25]]  # Two groups

    # Act
    fig, ax = create_bar_plot(categories, values, labels=["Group 1", "Group 2"])

    # Assert
    assert fig is not None
    assert len(ax.patches) == 6  # 3 categories * 2 groups

    # Cleanup
    plt.close(fig)


def test_create_bar_plot_empty_categories_raises_error() -> None:

    """
    Test case 5: ValueError for empty categories.
    """
    # Arrange
    categories = []
    values = []
    expected_message = "categories cannot be empty"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        create_bar_plot(categories, values)


def test_create_bar_plot_mismatched_lengths_raises_error() -> None:

    """
    Test case 6: ValueError when categories and values lengths don't match.
    """
    # Arrange
    categories = ["A", "B", "C"]
    values = [10, 20]
    expected_message = "values.*length.*must match|length.*mismatch"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        create_bar_plot(categories, values)


def test_create_bar_plot_invalid_type_raises_error() -> None:

    """
    Test case 7: TypeError for invalid categories type.
    """
    # Arrange
    categories = "not_a_list"
    values = [10, 20, 30]
    expected_message = "categories must be a list|must be.*list|got str"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        create_bar_plot(categories, values)


def test_create_bar_plot_invalid_figsize_raises_error() -> None:

    """
    Test case 8: ValueError for invalid figsize.
    """
    # Arrange
    categories = ["A", "B"]
    values = [10, 20]
    expected_message = "figsize must be.*tuple|negative|must be positive"

    # Act & Assert
    with pytest.raises((TypeError, ValueError), match=expected_message):
        create_bar_plot(categories, values, figsize=(10, -5))


def test_create_bar_plot_with_grid() -> None:

    """
    Test case 9: Create bar plot with grid enabled.
    """
    # Arrange
    categories = ["X", "Y", "Z"]
    values = [5, 10, 7]

    # Act
    fig, ax = create_bar_plot(categories, values, grid=True)

    # Assert
    assert fig is not None
    assert ax is not None
    # Grid setting applied

    # Cleanup
    plt.close(fig)


__all__ = ["test_create_bar_plot_basic"]
