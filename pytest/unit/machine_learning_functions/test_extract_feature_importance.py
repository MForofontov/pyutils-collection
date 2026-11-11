import numpy as np
import pytest
from sklearn.dummy import DummyClassifier

from pyutils_collection.machine_learning_functions.extract_feature_importance import (
    extract_feature_importance,
)

pytestmark = [pytest.mark.unit, pytest.mark.machine_learning]


def test_extract_feature_importance_tree_model(classification_data) -> None:
    from sklearn.ensemble import RandomForestClassifier

    X_train, y_train, _, _ = classification_data
    model = RandomForestClassifier(n_estimators=10, random_state=42).fit(
        X_train, y_train
    )
    importances = extract_feature_importance(model, X_train, y_train)
    assert len(importances) == X_train.shape[1]
    assert abs(sum(importances.values()) - 1.0) < 1e-6


def test_extract_feature_importance_native_raises_for_unsupported_model(
    classification_data,
) -> None:
    X_train, y_train, _, _ = classification_data
    model = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
    with pytest.raises(ValueError, match="native feature importance"):
        extract_feature_importance(model, X_train, y_train, method="native")
