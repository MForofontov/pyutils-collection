"""Automated model selection by trying multiple models."""

import logging
from typing import Any

import numpy as np
from sklearn.base import clone
from sklearn.model_selection import cross_val_score

logger = logging.getLogger(__name__)


def auto_select_best_model(
    models: dict[str, Any],
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray | None = None,
    y_test: np.ndarray | None = None,
    cv_folds: int = 5,
    scoring: str = "accuracy",
    refit: bool = True,
) -> dict[str, Any]:
    """
    Automatically select the best model by comparing multiple candidates.

    Trains and evaluates multiple models, returning the best performer
    with comprehensive comparison metrics.

    Parameters
    ----------
    models : dict[str, Any]
        Dictionary mapping model names to sklearn estimator objects (unfitted).
    X_train : np.ndarray
        Training features.
    y_train : np.ndarray
        Training target.
    X_test : np.ndarray | None, optional
        Test features for final evaluation (by default None).
    y_test : np.ndarray | None, optional
        Test target for final evaluation (by default None).
    cv_folds : int, optional
        Number of cross-validation folds (by default 5).
    scoring : str, optional
        Scoring metric for evaluation (by default 'accuracy').
    refit : bool, optional
        Whether to refit best model on full training set (by default True).

    Returns
    -------
    dict[str, Any]
        Selection results:
        - 'best_model_name': Name of best model
        - 'best_model': Fitted best model (if refit=True)
        - 'best_score': CV score of best model
        - 'all_scores': Dict of all model CV scores
        - 'test_score': Test score if test data provided
        - 'ranking': List of model names sorted by performance

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
    >>> from sklearn.ensemble import RandomForestClassifier
    >>> X_train = np.random.randn(100, 5)
    >>> y_train = np.random.randint(0, 2, 100)
    >>> X_test = np.random.randn(30, 5)
    >>> y_test = np.random.randint(0, 2, 30)
    >>> models = {
    ...     'logistic': LogisticRegression(max_iter=200),
    ...     'tree': DecisionTreeClassifier(),
    ...     'forest': RandomForestClassifier(n_estimators=10)
    ... }
    >>> result = auto_select_best_model(models, X_train, y_train, X_test, y_test)
    >>> result['best_model_name'] in models
    True
    >>> len(result['ranking']) == 3
    True

    Notes
    -----
    Provides automated model selection with comprehensive comparison.
    Uses cross-validation to avoid overfitting in selection.

    Use battle-tested libraries: Built on sklearn's cross_val_score.
    Adds value through: automated comparison, ranking, best model selection,
    convenient workflow that combines training and evaluation.

    Complexity
    ----------
    Time: O(m*n*k) where m=models, n=samples, k=cv_folds, Space: O(m)
    """
    # Input validation
    if not isinstance(models, dict):
        raise TypeError(f"models must be dict, got {type(models).__name__}")
    if len(models) == 0:
        raise ValueError("models dictionary cannot be empty")
    if not isinstance(X_train, np.ndarray):
        raise TypeError(f"X_train must be numpy array, got {type(X_train).__name__}")
    if not isinstance(y_train, np.ndarray):
        raise TypeError(f"y_train must be numpy array, got {type(y_train).__name__}")
    if X_test is not None and not isinstance(X_test, np.ndarray):
        raise TypeError(
            f"X_test must be numpy array or None, got {type(X_test).__name__}"
        )
    if y_test is not None and not isinstance(y_test, np.ndarray):
        raise TypeError(
            f"y_test must be numpy array or None, got {type(y_test).__name__}"
        )
    if (X_test is None) != (y_test is None):
        raise ValueError("X_test and y_test must both be provided or both be None")
    if not isinstance(cv_folds, int):
        raise TypeError(f"cv_folds must be int, got {type(cv_folds).__name__}")
    if cv_folds < 2:
        raise ValueError(f"cv_folds must be >= 2, got {cv_folds}")
    if not isinstance(scoring, str):
        raise TypeError(f"scoring must be str, got {type(scoring).__name__}")
    if not isinstance(refit, bool):
        raise TypeError(f"refit must be bool, got {type(refit).__name__}")

    # Evaluate all models
    all_scores = {}
    all_cv_results = {}

    logger.info(f"Evaluating {len(models)} models with {cv_folds}-fold CV")

    for name, model in models.items():
        logger.debug(f"Evaluating model: {name}")

        # Cross-validation
        cv_scores = cross_val_score(
            model, X_train, y_train, cv=cv_folds, scoring=scoring
        )

        mean_score = float(np.mean(cv_scores))
        std_score = float(np.std(cv_scores))

        all_scores[name] = mean_score
        all_cv_results[name] = {
            "mean": mean_score,
            "std": std_score,
            "scores": cv_scores.tolist(),
        }

    # Find best model
    best_model_name = max(all_scores, key=lambda x: all_scores[x])
    best_score = all_scores[best_model_name]

    # Create ranking
    ranking = sorted(all_scores.keys(), key=lambda x: all_scores[x], reverse=True)

    logger.info(f"Best model: {best_model_name} (CV score: {best_score:.4f})")

    # Prepare result
    result: dict[str, Any] = {
        "best_model_name": best_model_name,
        "best_score": best_score,
        "all_scores": all_scores,
        "all_cv_results": all_cv_results,
        "ranking": ranking,
    }

    # Refit best model on full training set
    best_model = clone(models[best_model_name])
    if refit:
        logger.debug(f"Refitting best model ({best_model_name}) on full training set")
        best_model.fit(X_train, y_train)
        result["best_model"] = best_model

    # Test set evaluation if provided
    if X_test is not None and y_test is not None:
        if not refit:
            # Need to fit model for test evaluation
            best_model.fit(X_train, y_train)
            result["best_model"] = best_model

        test_score = float(best_model.score(X_test, y_test))
        result["test_score"] = test_score
        logger.info(f"Test score: {test_score:.4f}")

    return result


__all__ = ["auto_select_best_model"]
