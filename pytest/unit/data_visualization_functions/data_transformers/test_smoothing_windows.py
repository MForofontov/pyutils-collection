"""Moving averages preserve alignment, input length, and caller-owned data."""

import numpy as np

import pytest
from pyutils_collection.data_visualization_functions import smooth_timeseries

pytestmark = [pytest.mark.unit, pytest.mark.data_visualization]


@pytest.mark.parametrize(
    ("data", "width", "expected"),
    [
        ([1, 3, 9, 15, 21], 1, [1, 3, 9, 15, 21]),
        ([1, 3, 9, 15, 21], 2, [1, 2, 6, 12, 18]),
        ([1, 3, 9, 15, 21], 3, [1, 13 / 3, 9, 15, 21]),
        ([1, 3, 9, 15, 21], 4, [1, 3, 7, 12, 21]),
        ([1, 3, 9, 15], 4, [1, 3, 7, 15]),
    ],
)
def test_moving_average_uses_all_complete_windows(
    data: list[int], width: int, expected: list[float]
) -> None:
    source = np.array(data)
    result = smooth_timeseries(source, window_size=width)
    np.testing.assert_allclose(result, expected)
    assert result.shape == source.shape
    assert result.dtype == np.dtype(float)
    result[0] = -100
    np.testing.assert_array_equal(source, data)


@pytest.mark.parametrize(("data", "width"), [([1], 2), ([1, 3, 9], 4)])
def test_moving_average_rejects_oversized_windows(data: list[int], width: int) -> None:
    with pytest.raises(ValueError, match="window_size.*cannot exceed"):
        smooth_timeseries(data, window_size=width)


def test_exponential_smoothing_allows_a_window_larger_than_the_series() -> None:
    result = smooth_timeseries([1, 5, 9], method="exponential", window_size=5)
    np.testing.assert_allclose(result, [1, 7 / 3, 41 / 9])
