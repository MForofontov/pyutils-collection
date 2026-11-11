import numpy as np
import pytest
from sklearn.tree import DecisionTreeClassifier

from pyutils_collection.machine_learning_functions.detect_overfitting import (
    detect_overfitting,
)

pytestmark = [pytest.mark.unit, pytest.mark.machine_learning]


def test_detect_overfitting_returns_diagnosis(classification_data) -> None:
    X_train, y_train, X_test, y_test = classification_data
    model = DecisionTreeClassifier(max_depth=10).fit(X_train, y_train)
    diagnosis = detect_overfitting(
        model, X_train, y_train, X_test, y_test, cv_folds=3, gap_threshold=0.05
    )
    assert "overfitting_detected" in diagnosis
    assert diagnosis["severity"] in {"none", "mild", "moderate", "severe"}


def test_detect_overfitting_severity_uses_gap_threshold(classification_data) -> None:
    X_train, y_train, X_test, y_test = classification_data
    model = DecisionTreeClassifier(max_depth=10).fit(X_train, y_train)
    diagnosis = detect_overfitting(
        model,
        X_train,
        y_train,
        X_test,
        y_test,
        cv_folds=3,
        gap_threshold=0.5,
    )
    if diagnosis["overfitting_detected"]:
        assert diagnosis["severity"] in {"mild", "moderate", "severe"}
