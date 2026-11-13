"""An explicit bootstrap seed must not reset the caller's global generator."""

import numpy as np

import pytest
from pyutils_collection.scientific_computing_functions.statistical_analysis import (
    bootstrap_statistic,
)

pytestmark = [pytest.mark.unit, pytest.mark.scientific_computing]


@pytest.mark.parametrize("statistic", ["mean", "median", "std"])
def test_seeded_bootstrap_preserves_global_random_state(statistic):
    original = np.random.get_state()
    data = np.array([1.0, 2.0, np.nan, 4.0, 8.0])
    preserved = data.copy()
    try:
        np.random.seed(123)
        before = np.random.get_state()
        first = bootstrap_statistic(
            data, statistic=statistic, n_iterations=100, random_seed=42
        )
        after = np.random.get_state()
        assert before[0] == after[0]
        np.testing.assert_array_equal(before[1], after[1])
        assert before[2:] == after[2:]
        assert first == bootstrap_statistic(
            data, statistic=statistic, n_iterations=100, random_seed=42
        )
        np.testing.assert_array_equal(data, preserved)
    finally:
        np.random.set_state(original)
