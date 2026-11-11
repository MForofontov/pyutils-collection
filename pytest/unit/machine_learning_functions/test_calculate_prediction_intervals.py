import numpy as np
import pytest
from sklearn.linear_model import LinearRegression

from pyutils_collection.machine_learning_functions.calculate_prediction_intervals import (
    calculate_prediction_intervals,
)

pytestmark = [pytest.mark.unit, pytest.mark.machine_learning]


def test_calculate_prediction_intervals_shape(regression_data) -> None:
    X_train, y_train, X_test, _ = regression_data
    model = LinearRegression().fit(X_train, y_train)
    intervals = calculate_prediction_intervals(
        model, X_test, X_train, y_train, n_bootstrap=20, random_state=42
    )
    assert len(intervals["predictions"]) == len(X_test)
    assert np.all(intervals["lower_bound"] <= intervals["predictions"])
    assert np.all(intervals["predictions"] <= intervals["upper_bound"])


def test_calculate_prediction_intervals_requires_training_data(
    regression_data,
) -> None:
    X_train, y_train, X_test, _ = regression_data
    model = LinearRegression().fit(X_train, y_train)
    with pytest.raises(TypeError):
        calculate_prediction_intervals(model, X_test)  # type: ignore[call-arg]
