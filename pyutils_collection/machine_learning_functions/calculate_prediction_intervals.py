"""Calculate prediction confidence intervals using bootstrap."""

import logging
from typing import Any

import numpy as np
from sklearn.base import clone

logger = logging.getLogger(__name__)


def calculate_prediction_intervals(
    model: Any,
    X: np.ndarray,
    X_train: np.ndarray,
    y_train: np.ndarray,
    confidence_level: float = 0.95,
    n_bootstrap: int = 100,
    random_state: int | None = 42,
) -> dict[str, np.ndarray]:
    """
    Calculate prediction confidence intervals using bootstrap resampling.

    Generates prediction intervals by refitting the model on bootstrap
    resamples of the training data, then predicting on ``X``.

    Parameters
    ----------
    model : Any
        Trained sklearn model with fit and predict methods.
    X : np.ndarray
        Feature matrix for predictions.
    X_train : np.ndarray
        Training feature matrix used for bootstrap resampling.
    y_train : np.ndarray
        Training target values used for bootstrap resampling.
    confidence_level : float, optional
        Confidence level for intervals (by default 0.95 for 95% CI).
    n_bootstrap : int, optional
        Number of bootstrap samples (by default 100).
    random_state : int | None, optional
        Random seed for reproducibility (by default 42).

    Returns
    -------
    dict[str, np.ndarray]
        Dictionary containing:
        - 'predictions': Mean predictions
        - 'lower_bound': Lower confidence bound
        - 'upper_bound': Upper confidence bound
        - 'std': Standard deviation of predictions

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values.

    Examples
    --------
    >>> import numpy as np
    >>> from sklearn.linear_model import LinearRegression
    >>> X_train = np.random.randn(100, 5)
    >>> y_train = np.random.randn(100)
    >>> X_test = np.random.randn(20, 5)
    >>> model = LinearRegression().fit(X_train, y_train)
    >>> intervals = calculate_prediction_intervals(
    ...     model, X_test, X_train, y_train, n_bootstrap=50
    ... )
    >>> len(intervals['predictions']) == 20
    True
    >>> all(intervals['lower_bound'] <= intervals['predictions'])
    True
    >>> all(intervals['predictions'] <= intervals['upper_bound'])
    True

    Notes
    -----
    Uses bootstrap resampling of the training set with model refitting
    to estimate prediction uncertainty.

    Complexity
    ----------
    Time: O(n*m*b) where b=n_bootstrap, Space: O(n*b) for bootstrap storage
    """
    # Input validation
    if not isinstance(X, np.ndarray):
        raise TypeError(f"X must be numpy array, got {type(X).__name__}")
    if not isinstance(X_train, np.ndarray):
        raise TypeError(f"X_train must be numpy array, got {type(X_train).__name__}")
    if not isinstance(y_train, np.ndarray):
        raise TypeError(f"y_train must be numpy array, got {type(y_train).__name__}")
    if not isinstance(confidence_level, (int, float)):
        raise TypeError(
            f"confidence_level must be numeric, got {type(confidence_level).__name__}"
        )
    if not (0 < confidence_level < 1):
        raise ValueError(
            f"confidence_level must be between 0 and 1, got {confidence_level}"
        )
    if not isinstance(n_bootstrap, int):
        raise TypeError(f"n_bootstrap must be int, got {type(n_bootstrap).__name__}")
    if n_bootstrap < 10:
        raise ValueError(f"n_bootstrap must be >= 10, got {n_bootstrap}")
    if random_state is not None and not isinstance(random_state, int):
        raise TypeError(
            f"random_state must be int or None, got {type(random_state).__name__}"
        )
    if not hasattr(model, "predict"):
        raise ValueError("model must have a 'predict' method")
    if not hasattr(model, "fit"):
        raise ValueError("model must have a 'fit' method")
    if X_train.shape[0] != y_train.shape[0]:
        raise ValueError("X_train and y_train must have the same number of samples")
    if X_train.shape[1] != X.shape[1]:
        raise ValueError("X_train and X must have the same number of features")

    rng = np.random.default_rng(random_state)
    n_train_samples = X_train.shape[0]
    n_samples = X.shape[0]

    # Bootstrap predictions via refit
    bootstrap_predictions = np.zeros((n_bootstrap, n_samples))

    for i in range(n_bootstrap):
        indices = rng.choice(n_train_samples, size=n_train_samples, replace=True)
        bootstrap_model = clone(model)
        bootstrap_model.fit(X_train[indices], y_train[indices])
        bootstrap_predictions[i] = bootstrap_model.predict(X)

    # Calculate statistics
    mean_predictions = np.mean(bootstrap_predictions, axis=0)
    std_predictions = np.std(bootstrap_predictions, axis=0)

    # Calculate confidence intervals
    alpha = 1 - confidence_level
    lower_percentile = (alpha / 2) * 100
    upper_percentile = (1 - alpha / 2) * 100

    lower_bound = np.percentile(bootstrap_predictions, lower_percentile, axis=0)
    upper_bound = np.percentile(bootstrap_predictions, upper_percentile, axis=0)

    result = {
        "predictions": mean_predictions,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "std": std_predictions,
    }

    return result


__all__ = ["calculate_prediction_intervals"]
