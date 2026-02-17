"""
Perform Singular Value Decomposition with validation and options.

Uses numpy.linalg.svd, adds validation, low-rank approximation,
and comprehensive output.
"""

import numpy as np


def compute_svd(
    matrix: list[list[float]] | np.ndarray,
    full_matrices: bool = True,
    compute_uv: bool = True,
    low_rank_k: int | None = None,
) -> dict[str, np.ndarray | float | int]:
    """
    Perform Singular Value Decomposition with validation and options.

    Uses numpy.linalg.svd, adds validation, low-rank approximation,
    and comprehensive output.

    Parameters
    ----------
    matrix : list[list[float]] | np.ndarray
        Matrix to decompose (m x n).
    full_matrices : bool, optional
        Compute full or reduced matrices (by default True).
    compute_uv : bool, optional
        Whether to compute U and V matrices (by default True).
    low_rank_k : int | None, optional
        If provided, return rank-k approximation (by default None).

    Returns
    -------
    dict[str, np.ndarray | float]
        Dictionary containing:
        - U: Left singular vectors (if computed)
        - singular_values: Singular values
        - Vt: Right singular vectors transposed (if computed)
        - approximation: Low-rank approximation (if k provided)
        - approximation_error: Frobenius norm error (if k provided)

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If matrix contains invalid values or k is invalid.

    Examples
    --------
    >>> matrix = [[1, 2], [3, 4], [5, 6]]
    >>> result = compute_svd(matrix)
    >>> len(result['singular_values'])
    2

    Notes
    -----
    SVD is useful for dimensionality reduction, matrix approximation,
    and solving ill-conditioned least squares problems.

    Complexity
    ----------
    Time: O(min(m²n, mn²)), Space: O(mn)
    """
    # Input validation
    if not isinstance(matrix, (list, np.ndarray)):
        raise TypeError(
            f"matrix must be a list or numpy array, got {type(matrix).__name__}"
        )
    if not isinstance(full_matrices, bool):
        raise TypeError(
            f"full_matrices must be a boolean, got {type(full_matrices).__name__}"
        )
    if not isinstance(compute_uv, bool):
        raise TypeError(
            f"compute_uv must be a boolean, got {type(compute_uv).__name__}"
        )
    if low_rank_k is not None and not isinstance(low_rank_k, int):
        raise TypeError(
            f"low_rank_k must be an integer or None, got {type(low_rank_k).__name__}"
        )

    # Convert to numpy array
    try:
        mat = np.asarray(matrix, dtype=float)
    except (ValueError, TypeError) as e:
        raise ValueError(f"matrix contains non-numeric values: {e}") from e

    # Validate dimensions
    if mat.ndim != 2:
        raise ValueError(f"matrix must be 2-dimensional, got {mat.ndim} dimensions")

    # Check for NaN or Inf
    if np.any(~np.isfinite(mat)):
        raise ValueError("matrix contains NaN or Inf values")

    # Validate low_rank_k
    if low_rank_k is not None:
        max_rank = min(mat.shape)
        if low_rank_k < 1:
            raise ValueError(f"low_rank_k must be >= 1, got {low_rank_k}")
        if low_rank_k > max_rank:
            raise ValueError(
                f"low_rank_k must be <= min(m, n) = {max_rank}, got {low_rank_k}"
            )

    # Compute SVD
    try:
        if compute_uv:
            U, s, Vt = np.linalg.svd(mat, full_matrices=full_matrices)
            result: dict[str, np.ndarray | float | int] = {
                "U": U,
                "singular_values": s,
                "Vt": Vt,
            }
        else:
            s = np.linalg.svd(mat, compute_uv=False)
            result = {"singular_values": s}
    except np.linalg.LinAlgError as e:
        raise ValueError(f"failed to compute SVD: {e}") from e

    # Compute low-rank approximation if requested
    if low_rank_k is not None and compute_uv:
        # Reconstruct with only top k singular values
        U_k = U[:, :low_rank_k]
        s_k = s[:low_rank_k]
        Vt_k = Vt[:low_rank_k, :]

        approximation = U_k @ np.diag(s_k) @ Vt_k
        error = np.linalg.norm(mat - approximation, "fro")

        result["approximation"] = approximation
        result["approximation_error"] = float(error)
        result["rank_k"] = int(low_rank_k)

    return result


__all__ = ["compute_svd"]
