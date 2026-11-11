"""
Compare multiple models on the same dataset.
"""

import logging
from typing import Any

import numpy as np
from sklearn.base import clone
from sklearn.model_selection import cross_val_score

logger = logging.getLogger(__name__)


def compare_models(
    models: dict[str, Any],
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    cv_folds: int = 5,
    scoring: str = "accuracy",
) -> dict[str, dict[str, float]]:
    """
    Compare multiple models on the same dataset with train/test and CV scores.

    Parameters
    ----------
    models : dict[str, Any]
        Dictionary mapping model names to sklearn estimator objects.
    X_train : np.ndarray
        Training features.
    y_train : np.ndarray
        Training target.
    X_test : np.ndarray
        Test features.
    y_test : np.ndarray
        Test target.
    cv_folds : int, optional
        Number of cross-validation folds (by default 5).
    scoring : str, optional
        Scoring metric for cross-validation (by default 'accuracy').

    Returns
    -------
    dict[str, dict[str, float]]
        Dictionary mapping model names to performance metrics:
        - 'train_score': Training set score
        - 'test_score': Test set score
        - 'cv_mean': Mean CV score
        - 'cv_std': Std CV score

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values.

    Examples
    --------
    >>> import numpy as np
    >>> from sklearn.linear_model import LogisticRegression
    >>> from sklearn.tree import DecisionTreeClassifier
    >>> X_train = np.random.randn(100, 5)
    >>> y_train = np.random.randint(0, 2, 100)
    >>> X_test = np.random.randn(30, 5)
    >>> y_test = np.random.randint(0, 2, 30)
    >>> models = {
    ...     'logistic': LogisticRegression(),
    ...     'tree': DecisionTreeClassifier()
    ... }
    >>> results = compare_models(models, X_train, y_train, X_test, y_test)
    >>> 'logistic' in results and 'tree' in results
    True

    Notes
    -----
    Fits each model and evaluates with train, test, and cross-validation scores.

    Use battle-tested libraries: Built on sklearn's cross_val_score and scoring.
    Adds value through: convenient comparison interface and comprehensive metrics.

    Complexity
    ----------
    Time: O(m * n * k) where m=models, n=samples, k=cv_folds, Space: O(m)
    """

    # Type validation
    if not isinstance(models, dict):
        raise TypeError(f"models must be a dictionary, got {type(models).__name__}")
    if not isinstance(X_train, np.ndarray):
        raise TypeError(f"X_train must be a numpy array, got {type(X_train).__name__}")
    if not isinstance(y_train, np.ndarray):
        raise TypeError(f"y_train must be a numpy array, got {type(y_train).__name__}")
    if not isinstance(X_test, np.ndarray):
        raise TypeError(f"X_test must be a numpy array, got {type(X_test).__name__}")
    if not isinstance(y_test, np.ndarray):
        raise TypeError(f"y_test must be a numpy array, got {type(y_test).__name__}")
    if not isinstance(cv_folds, int):
        raise TypeError(f"cv_folds must be an integer, got {type(cv_folds).__name__}")
    if not isinstance(scoring, str):
        raise TypeError(f"scoring must be a string, got {type(scoring).__name__}")

    # Value validation
    if len(models) == 0:
        raise ValueError("models dictionary cannot be empty")
    if X_train.shape[0] != y_train.shape[0]:
        raise ValueError(
            f"X_train and y_train must have same number of samples: {X_train.shape[0]} != {y_train.shape[0]}"
        )
    if X_test.shape[0] != y_test.shape[0]:
        raise ValueError(
            f"X_test and y_test must have same number of samples: {X_test.shape[0]} != {y_test.shape[0]}"
        )
    if X_train.shape[1] != X_test.shape[1]:
        raise ValueError(
            f"X_train and X_test must have same number of features: {X_train.shape[1]} != {X_test.shape[1]}"
        )
    if cv_folds < 2:
        raise ValueError(f"cv_folds must be >= 2, got {cv_folds}")

    results = {}

    for name, model in models.items():
        if not hasattr(model, "fit") or not hasattr(model, "score"):
            raise ValueError(f"Model '{name}' must have fit and score methods")

        # Fit a clone so caller's estimator is not mutated
        fitted_model = clone(model)
        fitted_model.fit(X_train, y_train)

        # Calculate scores
        train_score = fitted_model.score(X_train, y_train)
        test_score = fitted_model.score(X_test, y_test)

        # Cross-validation
        cv_scores = cross_val_score(
            clone(model), X_train, y_train, cv=cv_folds, scoring=scoring
        )

        results[name] = {
            "train_score": float(train_score),
            "test_score": float(test_score),
            "cv_mean": float(np.mean(cv_scores)),
            "cv_std": float(np.std(cv_scores)),
        }

        logger.debug(
            f"Model '{name}': test={test_score:.4f}, cv={np.mean(cv_scores):.4f}±{np.std(cv_scores):.4f}"
        )

    return results


__all__ = ["compare_models"]
