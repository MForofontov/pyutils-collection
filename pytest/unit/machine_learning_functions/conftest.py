"""Shared fixtures for machine learning function tests."""

import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeClassifier


@pytest.fixture
def classification_data() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(42)
    X_train = rng.standard_normal((80, 5))
    y_train = (X_train[:, 0] > 0).astype(int)
    X_test = rng.standard_normal((20, 5))
    y_test = (X_test[:, 0] > 0).astype(int)
    return X_train, y_train, X_test, y_test


@pytest.fixture
def regression_data() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(42)
    X_train = rng.standard_normal((80, 5))
    y_train = X_train[:, 0] + rng.standard_normal(80) * 0.1
    X_test = rng.standard_normal((20, 5))
    y_test = X_test[:, 0] + rng.standard_normal(20) * 0.1
    return X_train, y_train, X_test, y_test


@pytest.fixture
def classification_models() -> dict:
    return {
        "logistic": LogisticRegression(max_iter=200),
        "tree": DecisionTreeClassifier(max_depth=3),
        "forest": RandomForestClassifier(n_estimators=10, random_state=42),
    }


@pytest.fixture
def regression_model() -> LinearRegression:
    return LinearRegression()
