import numpy as np
import pytest
from sklearn.linear_model import LinearRegression, LogisticRegression

from pyutils_collection.machine_learning_functions.evaluate_model_performance import (
    evaluate_model_performance,
)

pytestmark = [pytest.mark.unit, pytest.mark.machine_learning]


def test_evaluate_model_performance_classification(classification_data) -> None:
    X_train, y_train, _, _ = classification_data
    model = LogisticRegression(max_iter=200).fit(X_train, y_train)
    metrics = evaluate_model_performance(
        model, X_train, y_train, task="classification"
    )
    assert "accuracy" in metrics
    assert "f1" in metrics


def test_evaluate_model_performance_regression(regression_data) -> None:
    X_train, y_train, _, _ = regression_data
    model = LinearRegression().fit(X_train, y_train)
    metrics = evaluate_model_performance(model, X_train, y_train, task="regression")
    assert "mse" in metrics
    assert "r2" in metrics
