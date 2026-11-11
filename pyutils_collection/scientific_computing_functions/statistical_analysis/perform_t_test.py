"""
Perform independent samples t-test with comprehensive output.

Uses scipy.stats.ttest_ind, adds validation, effect size calculation,
and interpretation helpers.
"""

from typing import Literal

import numpy as np
from scipy import stats


def perform_t_test(
    group1: list[float] | np.ndarray,
    group2: list[float] | np.ndarray,
    alternative: Literal["two-sided", "less", "greater"] = "two-sided",
    equal_var: bool = True,
    alpha: float = 0.05,
) -> dict[str, float | bool | str]:
    """
    Perform independent samples t-test with comprehensive output.

    Uses scipy.stats.ttest_ind, adds validation, effect size calculation,
    and interpretation helpers.

    Parameters
    ----------
    group1 : list[float] | np.ndarray
        First group of observations.
    group2 : list[float] | np.ndarray
        Second group of observations.
    alternative : {'two-sided', 'less', 'greater'}, optional
        Alternative hypothesis (by default 'two-sided').
    equal_var : bool, optional
        Assume equal variances (by default True).
    alpha : float, optional
        Significance level (by default 0.05).

    Returns
    -------
    dict[str, float | bool | str]
        Dictionary containing:
        - statistic: t-statistic value
        - pvalue: p-value
        - significant: Whether result is significant
        - cohens_d: Cohen's d effect size
        - interpretation: Effect size interpretation
        - ci_lower: Confidence interval lower bound
        - ci_upper: Confidence interval upper bound

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If groups are empty or contain invalid values.

    Examples
    --------
    >>> group1 = [1, 2, 3, 4, 5]
    >>> group2 = [2, 3, 4, 5, 6]
    >>> result = perform_t_test(group1, group2)
    >>> result['pvalue'] < 0.05
    False
    >>> 'cohens_d' in result
    True

    Notes
    -----
    Cohen's d effect size interpretation:
    - Small: 0.2
    - Medium: 0.5
    - Large: 0.8

    Confidence intervals use the same variance assumption and alternative as
    the t-test. One-sided intervals have one infinite bound. Welch's test
    reports its fractional degrees of freedom; the equal-variance test retains
    its integer degrees of freedom. Cohen's d uses the pooled standard deviation.

    Complexity
    ----------
    Time: O(n + m), Space: O(1)
    """
    # Input validation
    if not isinstance(group1, (list, np.ndarray)):
        raise TypeError(
            f"group1 must be a list or numpy array, got {type(group1).__name__}"
        )
    if not isinstance(group2, (list, np.ndarray)):
        raise TypeError(
            f"group2 must be a list or numpy array, got {type(group2).__name__}"
        )
    if not isinstance(alternative, str):
        raise TypeError(
            f"alternative must be a string, got {type(alternative).__name__}"
        )
    if alternative not in ("two-sided", "less", "greater"):
        raise ValueError(
            f"alternative must be 'two-sided', 'less', or 'greater', got '{alternative}'"
        )
    if not isinstance(equal_var, bool):
        raise TypeError(f"equal_var must be a boolean, got {type(equal_var).__name__}")
    if not isinstance(alpha, (int, float)):
        raise TypeError(f"alpha must be a number, got {type(alpha).__name__}")
    if not 0 < alpha < 1:
        raise ValueError(f"alpha must be between 0 and 1, got {alpha}")

    # Convert to numpy arrays
    try:
        arr1 = np.asarray(group1, dtype=float)
        arr2 = np.asarray(group2, dtype=float)
    except (ValueError, TypeError) as e:
        raise ValueError(f"groups contain non-numeric values: {e}") from e

    if arr1.size == 0:
        raise ValueError("group1 cannot be empty")
    if arr2.size == 0:
        raise ValueError("group2 cannot be empty")

    # Remove NaN values
    arr1 = arr1[~np.isnan(arr1)]
    arr2 = arr2[~np.isnan(arr2)]

    if arr1.size == 0:
        raise ValueError("group1 contains only NaN values")
    if arr2.size == 0:
        raise ValueError("group2 contains only NaN values")

    # Perform t-test
    test_result = stats.ttest_ind(
        arr1, arr2, equal_var=equal_var, alternative=alternative
    )
    t_stat, p_value = test_result

    # Calculate Cohen's d effect size
    mean1 = np.mean(arr1)
    mean2 = np.mean(arr2)
    std1 = np.std(arr1, ddof=1)
    std2 = np.std(arr2, ddof=1)

    # Pooled standard deviation
    n1 = arr1.size
    n2 = arr2.size
    pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))

    cohens_d = (mean1 - mean2) / pooled_std if pooled_std > 0 else 0.0

    # Interpret effect size
    abs_d = abs(cohens_d)
    if abs_d < 0.2:
        interpretation = "negligible"
    elif abs_d < 0.5:
        interpretation = "small"
    elif abs_d < 0.8:
        interpretation = "medium"
    else:
        interpretation = "large"

    # Calculate confidence interval for difference
    interval = test_result.confidence_interval(confidence_level=1 - alpha)
    df = float(test_result.df)
    diff = mean1 - mean2

    return {
        "statistic": float(t_stat),
        "pvalue": float(p_value),
        "significant": p_value < alpha,
        "cohens_d": float(cohens_d),
        "effect_size_interpretation": interpretation,
        "mean_difference": float(diff),
        "ci_lower": float(interval.low),
        "ci_upper": float(interval.high),
        "degrees_of_freedom": int(df) if equal_var else df,
        "alpha": alpha,
    }


__all__ = ["perform_t_test"]
