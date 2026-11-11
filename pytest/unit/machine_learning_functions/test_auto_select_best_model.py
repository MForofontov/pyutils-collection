import pytest
from sklearn.linear_model import LogisticRegression

from pyutils_collection.machine_learning_functions.auto_select_best_model import (
    auto_select_best_model,
)

pytestmark = [pytest.mark.unit, pytest.mark.machine_learning]


def test_auto_select_best_model_returns_ranking(
    classification_data, classification_models
) -> None:
    X_train, y_train, X_test, y_test = classification_data
    result = auto_select_best_model(
        classification_models,
        X_train,
        y_train,
        X_test,
        y_test,
        cv_folds=3,
    )
    assert result["best_model_name"] in classification_models
    assert len(result["ranking"]) == len(classification_models)
    assert "best_model" in result


def test_auto_select_best_model_does_not_mutate_caller_estimators(
    classification_data, classification_models
) -> None:
    X_train, y_train, X_test, y_test = classification_data
    original = LogisticRegression(max_iter=200)
    models = {"logistic": original, **classification_models}
    auto_select_best_model(models, X_train, y_train, cv_folds=3)
    with pytest.raises(Exception):
        original.predict(X_test)
