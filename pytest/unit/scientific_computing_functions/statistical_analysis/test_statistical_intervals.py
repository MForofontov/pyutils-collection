"""Intervals must match the selected statistical model and confidence level."""

import numpy as np
from scipy import stats

import pytest
from pyutils_collection.scientific_computing_functions.statistical_analysis.bootstrap_statistic import (
    bootstrap_statistic,
)
from pyutils_collection.scientific_computing_functions.statistical_analysis.comprehensive_stats import (
    comprehensive_stats,
)
from pyutils_collection.scientific_computing_functions.statistical_analysis.correlation_analysis import (
    correlation_analysis,
)
from pyutils_collection.scientific_computing_functions.statistical_analysis.perform_t_test import (
    perform_t_test,
)

pytestmark = [pytest.mark.unit, pytest.mark.scientific_computing]


@pytest.mark.parametrize("equal_var", [False, True])
@pytest.mark.parametrize("alternative", ["two-sided", "less", "greater"])
def test_t_test_interval_matches_selected_model(equal_var, alternative):
    first, second = [1.0, 2.0, 3.0], [5.0, 9.0, 20.0, 30.0]
    result = perform_t_test(
        first, second, equal_var=equal_var, alternative=alternative, alpha=0.1
    )
    reference = stats.ttest_ind(
        first, second, equal_var=equal_var, alternative=alternative
    )
    interval = reference.confidence_interval(confidence_level=0.9)
    np.testing.assert_allclose(
        [result["ci_lower"], result["ci_upper"]], [interval.low, interval.high]
    )
    assert result["degrees_of_freedom"] == pytest.approx(reference.df)


def test_constant_sample_interval_collapses_to_mean():
    result = comprehensive_stats([5.0] * 10, include_distribution_tests=False)
    assert result["ci_lower"] == result["ci_upper"] == 5.0


@pytest.mark.parametrize(
    "function,inputs,parameter",
    [
        (comprehensive_stats, ([1.0, 2.0, 3.0],), "confidence_level"),
        (bootstrap_statistic, ([1.0, 2.0, 3.0],), "confidence_level"),
        (correlation_analysis, ([1.0, 2.0, 3.0], [3.0, 1.0, 2.0]), "alpha"),
        (perform_t_test, ([1.0, 2.0, 3.0], [3.0, 1.0, 2.0]), "alpha"),
    ],
)
def test_nan_probability_is_rejected(function, inputs, parameter):
    with pytest.raises(ValueError, match=f"{parameter} must be between 0 and 1"):
        function(*inputs, **{parameter: float("nan")})
