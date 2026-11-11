"""
Create a formatted report comparing multiple models.
"""

import logging

logger = logging.getLogger(__name__)


def create_model_report(
    results: dict[str, dict[str, float]],
    sort_by: str = "test_score",
    ascending: bool = False,
) -> str:
    """
    Create a formatted text report from model comparison results.

    Parameters
    ----------
    results : dict[str, dict[str, float]]
        Results from compare_models function.
    sort_by : str, optional
        Metric to sort by (by default 'test_score').
    ascending : bool, optional
        Whether to sort ascending (by default False).

    Returns
    -------
    str
        Formatted report string with model rankings and metrics.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values.

    Examples
    --------
    >>> results = {
    ...     'logistic': {'train_score': 0.85, 'test_score': 0.82, 'cv_mean': 0.83, 'cv_std': 0.02},
    ...     'tree': {'train_score': 0.95, 'test_score': 0.78, 'cv_mean': 0.80, 'cv_std': 0.03}
    ... }
    >>> report = create_model_report(results)
    >>> 'Model Comparison Report' in report
    True

    >>> # Sort by CV score
    >>> report_cv = create_model_report(results, sort_by='cv_mean')
    >>> len(report_cv) > 0
    True

    Notes
    -----
    Creates a nicely formatted table for easy model comparison.

    Use battle-tested libraries: Pure Python string formatting.
    Adds value through: readable reporting and automatic ranking.

    Complexity
    ----------
    Time: O(m log m) for sorting, Space: O(m) where m is number of models
    """
    # Type validation
    if not isinstance(results, dict):
        raise TypeError(f"results must be a dictionary, got {type(results).__name__}")
    if not isinstance(sort_by, str):
        raise TypeError(f"sort_by must be a string, got {type(sort_by).__name__}")
    if not isinstance(ascending, bool):
        raise TypeError(f"ascending must be a boolean, got {type(ascending).__name__}")

    # Value validation
    if len(results) == 0:
        raise ValueError("results dictionary cannot be empty")

    # Check that sort_by metric exists in all models
    for name, metrics in results.items():
        if sort_by not in metrics:
            raise ValueError(
                f"Metric '{sort_by}' not found in results for model '{name}'. "
                f"Available: {list(metrics.keys())}"
            )

    # Sort models by specified metric
    sorted_models = sorted(
        results.items(), key=lambda x: x[1][sort_by], reverse=not ascending
    )

    # Create report
    lines = []
    lines.append("=" * 70)
    lines.append("Model Comparison Report")
    lines.append("=" * 70)
    lines.append(f"Sorted by: {sort_by} ({'ascending' if ascending else 'descending'})")
    lines.append("")

    # Header
    header = f"{'Rank':<6} {'Model':<20} {'Train':<10} {'Test':<10} {'CV Mean':<12} {'CV Std':<10}"
    lines.append(header)
    lines.append("-" * 70)

    # Model rows
    for rank, (name, metrics) in enumerate(sorted_models, 1):
        train = metrics.get("train_score", 0)
        test = metrics.get("test_score", 0)
        cv_mean = metrics.get("cv_mean", 0)
        cv_std = metrics.get("cv_std", 0)

        row = f"{rank:<6} {name:<20} {train:>8.4f}  {test:>8.4f}  {cv_mean:>10.4f}  {cv_std:>8.4f}"
        lines.append(row)

    lines.append("=" * 70)

    # Best model summary
    best_name, best_metrics = sorted_models[0]
    lines.append("")
    lines.append(f"Best Model: {best_name}")
    lines.append(f"Test Score: {best_metrics.get('test_score', 0):.4f}")
    lines.append(
        f"CV Score:   {best_metrics.get('cv_mean', 0):.4f} ± {best_metrics.get('cv_std', 0):.4f}"
    )

    report = "\n".join(lines)

    logger.debug(f"Created model report for {len(results)} models")

    return report


__all__ = ["create_model_report"]
