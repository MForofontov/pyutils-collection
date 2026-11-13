"""Figures created by failed plotting helpers must not remain registered."""

from collections.abc import Callable

import matplotlib.pyplot as plt
import pytest

from pyutils_collection.data_visualization_functions import (
    create_bar_plot,
    create_histogram,
    create_line_plot,
    create_scatter_plot,
)

pytestmark = [pytest.mark.unit, pytest.mark.data_visualization]


@pytest.mark.parametrize(
    "operation",
    [
        lambda: create_bar_plot(["a"], [1.0], colors=["invalid-color"]),
        lambda: create_histogram([1.0, 2.0], bins="invalid-bins"),
        lambda: create_line_plot([1.0], [1.0], colors=["invalid-color"]),
        lambda: create_scatter_plot([1.0], [1.0], colors="invalid-color"),
    ],
    ids=["bar", "histogram", "line", "scatter"],
)
def test_failed_plot_closes_only_its_figure(operation: Callable[[], object]) -> None:
    existing = set(plt.get_fignums())
    caller_figure = plt.figure()
    before = set(plt.get_fignums())
    try:
        with pytest.raises(ValueError):
            operation()
        assert set(plt.get_fignums()) == before
        assert plt.fignum_exists(caller_figure.number)
    finally:
        for number in set(plt.get_fignums()) - existing:
            plt.close(number)
