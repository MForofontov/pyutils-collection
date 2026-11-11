import numpy as np
import pytest

from pyutils_collection.machine_learning_functions.analyze_predictions import (
    analyze_predictions,
)

pytestmark = [pytest.mark.unit, pytest.mark.machine_learning]


def test_analyze_predictions_regression() -> None:
    y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y_pred = np.array([1.1, 2.2, 2.8, 4.1, 4.9])
    analysis = analyze_predictions(y_true, y_pred, task="regression")
    assert "residuals" in analysis
    assert "mean_error" in analysis


def test_analyze_predictions_classification() -> None:
    y_true = np.array([0, 1, 1, 0, 1])
    y_pred = np.array([0, 1, 0, 0, 1])
    analysis = analyze_predictions(y_true, y_pred, task="classification")
    assert "per_class_accuracy" in analysis
