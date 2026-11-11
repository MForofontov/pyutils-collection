"""Automated overfitting detection and diagnosis."""

import logging
from typing import Any

import numpy as np
from sklearn.model_selection import cross_val_score

logger = logging.getLogger(__name__)


def detect_overfitting(
    model: Any,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    cv_folds: int = 5,
    scoring: str = "accuracy",
    gap_threshold: float = 0.1,
) -> dict[str, Any]:
    """
    Detect overfitting with automated diagnosis and recommendations.

    Analyzes train/test/CV score gaps and provides actionable insights
    for addressing overfitting issues.

    Parameters
    ----------
    model : Any
        Trained sklearn model.
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
        Scoring metric (by default 'accuracy').
    gap_threshold : float, optional
        Threshold for concerning train-test gap (by default 0.1).

    Returns
    -------
    dict[str, Any]
        Overfitting diagnosis:
        - train_score, test_score, cv_mean, cv_std
        - overfitting_detected (bool)
        - severity ('none', 'mild', 'moderate', 'severe')
        - recommendations (list of strings)

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values.

    Examples
    --------
    >>> import numpy as np
    >>> from sklearn.tree import DecisionTreeClassifier
    >>> X_train = np.random.randn(100, 5)
    >>> y_train = np.random.randint(0, 2, 100)
    >>> X_test = np.random.randn(30, 5)
    >>> y_test = np.random.randint(0, 2, 30)
    >>> model = DecisionTreeClassifier(max_depth=20).fit(X_train, y_train)
    >>> diagnosis = detect_overfitting(model, X_train, y_train, X_test, y_test)
    >>> 'overfitting_detected' in diagnosis
    True
    >>> 'severity' in diagnosis
    True

    Notes
    -----
    Provides automated detection and actionable recommendations.

    Use battle-tested libraries: Built on sklearn's cross_val_score.
    Adds value through: automated diagnosis, severity assessment,
    specific recommendations based on gap magnitude.

    Complexity
    ----------
    Time: O(n*k) where k=cv_folds, Space: O(1)
    """
    # Input validation
    if not isinstance(X_train, np.ndarray):
        raise TypeError(f"X_train must be numpy array, got {type(X_train).__name__}")
    if not isinstance(y_train, np.ndarray):
        raise TypeError(f"y_train must be numpy array, got {type(y_train).__name__}")
    if not isinstance(X_test, np.ndarray):
        raise TypeError(f"X_test must be numpy array, got {type(X_test).__name__}")
    if not isinstance(y_test, np.ndarray):
        raise TypeError(f"y_test must be numpy array, got {type(y_test).__name__}")
    if not isinstance(cv_folds, int):
        raise TypeError(f"cv_folds must be int, got {type(cv_folds).__name__}")
    if cv_folds < 2:
        raise ValueError(f"cv_folds must be >= 2, got {cv_folds}")
    if not isinstance(scoring, str):
        raise TypeError(f"scoring must be str, got {type(scoring).__name__}")
    if not isinstance(gap_threshold, (int, float)):
        raise TypeError(
            f"gap_threshold must be numeric, got {type(gap_threshold).__name__}"
        )
    if gap_threshold <= 0:
        raise ValueError(f"gap_threshold must be positive, got {gap_threshold}")

    # Calculate scores
    train_score = float(model.score(X_train, y_train))
    test_score = float(model.score(X_test, y_test))

    # Cross-validation on training set
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv_folds, scoring=scoring)
    cv_mean = float(np.mean(cv_scores))
    cv_std = float(np.std(cv_scores))

    # Calculate gaps
    train_test_gap = train_score - test_score
    train_cv_gap = train_score - cv_mean
    cv_test_gap = cv_mean - test_score

    # Detect overfitting
    overfitting_detected = train_test_gap > gap_threshold

    # Assess severity relative to gap_threshold
    if not overfitting_detected:
        severity = "none"
    elif train_test_gap < gap_threshold * 1.5:
        severity = "mild"
    elif train_test_gap < gap_threshold * 2.5:
        severity = "moderate"
    else:
        severity = "severe"

    # Generate recommendations
    recommendations = []

    if overfitting_detected:
        if train_test_gap > 0.3:
            recommendations.append(
                "CRITICAL: Very large train-test gap (>30%) - model is severely overfitting"
            )

        # Model complexity recommendations
        if train_score > 0.95:
            recommendations.append(
                "Training score is very high (>95%) - reduce model complexity"
            )
            recommendations.append(
                "Try: decrease max_depth, increase min_samples_split, add regularization"
            )

        # Cross-validation insights
        if cv_std > 0.1:
            recommendations.append(
                f"High CV variance (std={cv_std:.3f}) - model is unstable"
            )
            recommendations.append(
                "Try: more training data, simpler model, or feature selection"
            )

        if train_cv_gap > 0.15:
            recommendations.append(
                "Large gap between train and CV scores - likely overfitting"
            )
            recommendations.append(
                "Try: regularization (L1/L2), dropout, or early stopping"
            )

        # Data recommendations
        if len(X_train) < 100:
            recommendations.append("Small training set - consider collecting more data")

        if X_train.shape[1] > len(X_train) // 2:
            recommendations.append(
                "High feature-to-sample ratio - try feature selection or dimensionality reduction"
            )

        # General recommendations
        recommendations.append(
            "General strategies: cross-validation, ensemble methods, or simpler model"
        )

    else:
        # Model is good
        if test_score > 0.8:
            recommendations.append(
                "Model performance looks good - no overfitting detected"
            )
        elif test_score < 0.6:
            recommendations.append("Low test score - model may be underfitting")
            recommendations.append(
                "Try: more complex model, feature engineering, or more training epochs"
            )
        else:
            recommendations.append(
                "Model performance is acceptable - monitor on new data"
            )

    result = {
        "train_score": train_score,
        "test_score": test_score,
        "cv_mean": cv_mean,
        "cv_std": cv_std,
        "train_test_gap": train_test_gap,
        "train_cv_gap": train_cv_gap,
        "cv_test_gap": cv_test_gap,
        "overfitting_detected": overfitting_detected,
        "severity": severity,
        "recommendations": recommendations,
    }

    return result


__all__ = ["detect_overfitting"]
