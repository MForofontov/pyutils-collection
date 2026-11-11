import pytest

from pyutils_collection.machine_learning_functions.create_model_report import (
    create_model_report,
)

pytestmark = [pytest.mark.unit, pytest.mark.machine_learning]


def test_create_model_report_contains_header() -> None:
    results = {
        "a": {"train_score": 0.9, "test_score": 0.8, "cv_mean": 0.85, "cv_std": 0.02},
        "b": {"train_score": 0.7, "test_score": 0.75, "cv_mean": 0.72, "cv_std": 0.03},
    }
    report = create_model_report(results)
    assert "Model Comparison Report" in report
    assert "Best Model" in report


def test_create_model_report_missing_sort_key_raises() -> None:
    results = {
        "a": {"train_score": 0.9, "test_score": 0.8, "cv_mean": 0.85, "cv_std": 0.02},
        "b": {"train_score": 0.7, "test_score": 0.75},
    }
    with pytest.raises(ValueError, match="cv_mean"):
        create_model_report(results, sort_by="cv_mean")
