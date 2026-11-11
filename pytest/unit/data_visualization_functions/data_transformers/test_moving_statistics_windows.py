"""Check numerical rolling results against explicitly enumerated windows."""

import numpy as np

import pytest
from pyutils_collection.data_visualization_functions import calculate_moving_statistics

pytestmark = [pytest.mark.unit, pytest.mark.data_visualization]


@pytest.mark.parametrize(
    ("width", "windows"),
    [
        (1, [[1], [3], [9], [15], [21]]),
        (2, [[1], [1, 3], [3, 9], [9, 15], [15, 21]]),
        (3, [[1, 3], [1, 3, 9], [3, 9, 15], [9, 15, 21], [15, 21]]),
        (4, [[1, 3], [1, 3, 9], [1, 3, 9, 15], [3, 9, 15, 21], [9, 15, 21]]),
        (5, [[1, 3, 9], [1, 3, 9, 15], [1, 3, 9, 15, 21], [3, 9, 15, 21], [9, 15, 21]]),
    ],
)
def test_statistics_use_requested_windows(width: int, windows: list[list[int]]) -> None:
    data = np.array([1, 3, 9, 15, 21])
    original = data.copy()
    operations = {
        "mean": np.mean,
        "std": np.std,
        "min": np.min,
        "max": np.max,
        "median": np.median,
    }
    result = calculate_moving_statistics(data, width, list(operations))
    assert list(result) == list(operations)
    for name, operation in operations.items():
        expected = [operation(window) for window in windows]
        np.testing.assert_allclose(result[name], expected)
        assert result[name].shape == data.shape
        assert result[name].dtype == np.dtype(float)
    np.testing.assert_array_equal(data, original)
