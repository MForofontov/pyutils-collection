"""Numerical reconstruction and input ownership across matrix shapes."""

import numpy as np
import pytest

from pyutils_collection.scientific_computing_functions.linear_algebra.compute_svd import (
    compute_svd,
)

pytestmark = [pytest.mark.unit, pytest.mark.scientific_computing]


@pytest.mark.parametrize("shape", [(8, 3), (3, 8), (4, 4)])
@pytest.mark.parametrize("full", [True, False])
@pytest.mark.parametrize("rank", [1, 3])
def test_rank_reconstruction_preserves_values_and_input(
    shape: tuple[int, int], full: bool, rank: int
) -> None:
    matrix = np.random.default_rng(57).normal(size=shape)
    original = matrix.copy()
    u, s, vt = np.linalg.svd(matrix, full_matrices=full)
    expected = u[:, :rank] @ np.diag(s[:rank]) @ vt[:rank, :]
    result = compute_svd(matrix, full_matrices=full, low_rank_k=rank)
    assert result.keys() == {
        "U",
        "singular_values",
        "Vt",
        "approximation",
        "approximation_error",
        "rank_k",
    }
    np.testing.assert_allclose(
        result["approximation"], expected, rtol=1e-12, atol=1e-12
    )
    assert result["approximation_error"] == pytest.approx(
        np.linalg.norm(original - expected, "fro"), rel=1e-12, abs=1e-12
    )
    np.testing.assert_array_equal(matrix, original)
    np.testing.assert_array_equal(result["U"], u)
    np.testing.assert_array_equal(result["Vt"], vt)
    assert result["rank_k"] == rank
