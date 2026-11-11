import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression

from pyutils_collection.machine_learning_functions.compare_models import compare_models

pytestmark = [pytest.mark.unit, pytest.mark.machine_learning]


def test_compare_models_returns_metrics(
    classification_data, classification_models
) -> None:
    X_train, y_train, X_test, y_test = classification_data
    results = compare_models(
        classification_models, X_train, y_train, X_test, y_test, cv_folds=3
    )
    assert set(results.keys()) == set(classification_models.keys())
    for metrics in results.values():
        assert {"train_score", "test_score", "cv_mean", "cv_std"} <= metrics.keys()


def test_compare_models_does_not_mutate_caller_estimators(
    classification_data, classification_models
) -> None:
    X_train, y_train, X_test, y_test = classification_data
    original = LogisticRegression(max_iter=200)
    models = {"logistic": original}
    compare_models(models, X_train, y_train, X_test, y_test, cv_folds=3)
    with pytest.raises(Exception):
        original.predict(X_test)
