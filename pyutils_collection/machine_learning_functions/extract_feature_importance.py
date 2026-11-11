"""Extract feature importance from various model types."""

import logging
from typing import Any

import numpy as np
from sklearn.inspection import permutation_importance

logger = logging.getLogger(__name__)


def extract_feature_importance(
    model: Any,
    X: np.ndarray,
    y: np.ndarray,
    feature_names: list[str] | None = None,
    method: str = "auto",
    n_repeats: int = 10,
) -> dict[str, float]:
    """
    Extract feature importance from any model type with unified interface.

    Handles tree-based (feature_importances_), linear (coef_), and any model
    via permutation importance. Automatically detects the best method.

    Parameters
    ----------
    model : Any
        Trained sklearn model.
    X : np.ndarray
        Feature matrix used for permutation importance.
    y : np.ndarray
        Target values for permutation importance.
    feature_names : list[str] | None, optional
        Feature names for the output dict (by default None uses indices).
    method : str, optional
        Extraction method: 'auto', 'native', 'permutation' (by default 'auto').
    n_repeats : int, optional
        Number of repeats for permutation importance (by default 10).

    Returns
    -------
    dict[str, float]
        Dictionary mapping feature names to importance scores (normalized 0-1).

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values.

    Examples
    --------
    >>> import numpy as np
    >>> from sklearn.ensemble import RandomForestClassifier
    >>> X = np.random.randn(100, 5)
    >>> y = np.random.randint(0, 2, 100)
    >>> model = RandomForestClassifier(n_estimators=10, random_state=42).fit(X, y)
    >>> importances = extract_feature_importance(model, X, y, feature_names=['a','b','c','d','e'])
    >>> len(importances) == 5
    True
    >>> all(0 <= v <= 1 for v in importances.values())
    True

    Notes
    -----
    Provides unified interface across different model types:
    - Tree-based: Uses feature_importances_ attribute
    - Linear models: Uses abs(coef_)
    - Any model: Falls back to permutation importance

    Use battle-tested libraries: Built on sklearn's permutation_importance.
    Adds value through: unified API, automatic method detection, normalization.

    Complexity
    ----------
    Time: O(n*m) for native, O(n*m*k) for permutation (k=n_repeats), Space: O(m)
    """
    # Input validation
    if not isinstance(X, np.ndarray):
        raise TypeError(f"X must be numpy array, got {type(X).__name__}")
    if not isinstance(y, np.ndarray):
        raise TypeError(f"y must be numpy array, got {type(y).__name__}")
    if feature_names is not None and not isinstance(feature_names, list):
        raise TypeError(
            f"feature_names must be list or None, got {type(feature_names).__name__}"
        )
    if not isinstance(method, str):
        raise TypeError(f"method must be str, got {type(method).__name__}")
    if method not in ["auto", "native", "permutation"]:
        raise ValueError(
            f"method must be 'auto', 'native', or 'permutation', got {method}"
        )
    if not isinstance(n_repeats, int):
        raise TypeError(f"n_repeats must be int, got {type(n_repeats).__name__}")
    if n_repeats < 1:
        raise ValueError(f"n_repeats must be positive, got {n_repeats}")

    n_features = X.shape[1]

    if feature_names is None:
        feature_names = [f"feature_{i}" for i in range(n_features)]

    if len(feature_names) != n_features:
        raise ValueError(
            f"feature_names length ({len(feature_names)}) must match X columns ({n_features})"
        )

    # Extract importances based on method
    importances = None

    if method in ["auto", "native"]:
        # Try tree-based feature_importances_
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            logger.debug("Using tree-based feature_importances_")

        # Try linear model coef_
        elif hasattr(model, "coef_"):
            coef = model.coef_
            # Handle multi-class case (average across classes)
            if coef.ndim > 1:
                importances = np.abs(coef).mean(axis=0)
            else:
                importances = np.abs(coef)
            logger.debug("Using linear model coefficients")

        # If auto and no native method found, use permutation
        elif method == "auto":
            method = "permutation"
        else:
            raise ValueError(
                "Model does not support native feature importance extraction"
            )

    # Use permutation importance if requested or no native method
    if importances is None:
        logger.debug("Using permutation importance")
        perm_importance = permutation_importance(
            model, X, y, n_repeats=n_repeats, random_state=42
        )
        importances = perm_importance.importances_mean

    # Normalize to 0-1 range
    importances = np.asarray(importances)
    if importances.sum() > 0:
        importances = importances / importances.sum()

    # Create result dictionary
    result = {
        name: float(imp)
        for name, imp in zip(feature_names, importances, strict=True)
    }

    return result


__all__ = ["extract_feature_importance"]
