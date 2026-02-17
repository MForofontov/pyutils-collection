"""Unit tests for adaptive_filter function."""

from typing import Any, cast

try:
    import numpy as np
    import scipy
    from pyutils_collection.scientific_computing_functions.signal_processing.adaptive_filter import (
        adaptive_filter,
    )
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None  # type: ignore
    scipy = None
    adaptive_filter = None  # type: ignore

import pytest

pytestmark = [pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy and/or scipy not installed"), pytest.mark.unit, pytest.mark.scientific_computing]


# Normal operation tests
def test_adaptive_filter_nlms_basic() -> None:
    """Test case 1: Normal operation with NLMS algorithm."""
    # Arrange
    np.random.seed(42)
    signal = np.sin(np.linspace(0, 4 * np.pi, 100)) + 0.1 * np.random.randn(100)

    # Act
    result = adaptive_filter(signal, filter_length=16, algorithm="nlms", step_size=0.1)

    # Assert
    assert len(result["filtered_signal"]) == 100
    assert len(result["error_signal"]) == 100
    assert len(result["filter_weights"]) == 16
    assert len(result["mse_history"]) > 0
    assert (
        result["convergence_iteration"] is None or result["convergence_iteration"] > 16
    )


def test_adaptive_filter_lms_algorithm() -> None:
    """Test case 2: Normal operation with LMS algorithm."""
    # Arrange
    signal: list[float] = [0.5, 0.3, 0.8, 0.2] * 25  # 100 samples

    # Act
    result = adaptive_filter(signal, filter_length=8, algorithm="lms", step_size=0.01)

    # Assert
    assert len(result["filtered_signal"]) == 100
    assert len(result["filter_weights"]) == 8
    assert result["mse_history"].shape[0] > 0


def test_adaptive_filter_rls_algorithm() -> None:
    """Test case 3: Normal operation with RLS algorithm."""
    # Arrange
    np.random.seed(42)
    signal = np.random.randn(100)

    # Act
    result = adaptive_filter(
        signal, filter_length=16, algorithm="rls", forgetting_factor=0.99
    )

    # Assert
    assert len(result["filtered_signal"]) == 100
    assert len(result["filter_weights"]) == 16
    # RLS should converge faster
    if result["convergence_iteration"] is not None:
        assert result["convergence_iteration"] < 100


def test_adaptive_filter_with_reference_signal() -> None:
    """Test case 4: Normal operation with custom reference signal."""
    # Arrange
    np.random.seed(42)
    signal = np.random.randn(100)
    reference = np.roll(signal, 10)  # Delayed version

    # Act
    result = adaptive_filter(
        signal, reference=reference, filter_length=32, algorithm="nlms"
    )

    # Assert
    assert len(result["filtered_signal"]) == 100
    assert len(result["error_signal"]) == 100


def test_adaptive_filter_small_step_size() -> None:
    """Test case 5: Normal operation with small step size (slow convergence)."""
    # Arrange
    signal: list[float] = [1.0] * 50 + [0.5] * 50

    # Act
    result = adaptive_filter(signal, filter_length=8, algorithm="nlms", step_size=0.001)

    # Assert
    assert len(result["mse_history"]) > 0
    # Small step size should take longer to converge (may not converge at all within signal length)
    assert (
        result["convergence_iteration"] is None or result["convergence_iteration"] > 15
    )


def test_adaptive_filter_large_step_size() -> None:
    """Test case 6: Normal operation with large step size (fast but potentially unstable)."""
    # Arrange
    signal = np.linspace(0, 1, 100).tolist()

    # Act
    result = adaptive_filter(signal, filter_length=8, algorithm="nlms", step_size=0.5)

    # Assert
    assert len(result["filtered_signal"]) == 100
    assert not np.any(np.isnan(result["filtered_signal"]))  # Should not diverge


def test_adaptive_filter_numpy_array_input() -> None:
    """Test case 7: Normal operation with numpy array input."""
    # Arrange
    signal = np.array([0.5, 0.3, 0.8, 0.2] * 25)

    # Act
    result = adaptive_filter(signal, filter_length=16, algorithm="nlms")

    # Assert
    assert isinstance(result["filtered_signal"], np.ndarray)
    assert isinstance(result["error_signal"], np.ndarray)


def test_adaptive_filter_different_forgetting_factors() -> None:
    """Test case 8: Normal operation with different forgetting factors for RLS."""
    # Arrange
    np.random.seed(42)
    signal = np.random.randn(100)

    # Act
    result_099 = adaptive_filter(
        signal, filter_length=8, algorithm="rls", forgetting_factor=0.99
    )
    result_095 = adaptive_filter(
        signal, filter_length=8, algorithm="rls", forgetting_factor=0.95
    )

    # Assert
    assert len(result_099["filtered_signal"]) == 100
    assert len(result_095["filtered_signal"]) == 100
    # Different forgetting factors should produce different results
    assert not np.allclose(result_099["filter_weights"], result_095["filter_weights"])


# Edge case tests
def test_adaptive_filter_minimum_signal_length() -> None:
    """Test case 9: Edge case with minimum viable signal length."""
    # Arrange
    filter_length = 8
    signal: list[float] = [1.0] * (filter_length + 5)  # Just above minimum

    # Act
    result = adaptive_filter(signal, filter_length=filter_length, algorithm="nlms")

    # Assert
    assert len(result["filtered_signal"]) == filter_length + 5
    assert len(result["filter_weights"]) == filter_length


def test_adaptive_filter_single_variable_filter() -> None:
    """Test case 10: Edge case with filter_length=1."""
    # Arrange
    signal: list[float] = [0.5, 0.3, 0.8, 0.2] * 10

    # Act
    result = adaptive_filter(signal, filter_length=1, algorithm="nlms")

    # Assert
    assert len(result["filter_weights"]) == 1
    assert len(result["filtered_signal"]) == 40


def test_adaptive_filter_constant_signal() -> None:
    """Test case 11: Edge case with constant signal."""
    # Arrange
    signal: list[float] = [5.0] * 100

    # Act
    result = adaptive_filter(signal, filter_length=8, algorithm="nlms")

    # Assert
    assert len(result["filtered_signal"]) == 100
    # Should converge quickly for constant signal
    assert (
        result["convergence_iteration"] is None or result["convergence_iteration"] < 100
    )


def test_adaptive_filter_forgetting_factor_one() -> None:
    """Test case 12: Edge case with forgetting factor = 1.0 (no forgetting)."""
    # Arrange
    signal = np.random.randn(50).tolist()

    # Act
    result = adaptive_filter(
        signal, filter_length=8, algorithm="rls", forgetting_factor=1.0
    )

    # Assert
    assert len(result["filtered_signal"]) == 50
    assert len(result["filter_weights"]) == 8


def test_adaptive_filter_long_signal() -> None:
    """Test case 13: Edge case with very long signal."""
    # Arrange
    np.random.seed(42)
    signal = np.random.randn(1000)

    # Act
    result = adaptive_filter(signal, filter_length=32, algorithm="nlms")

    # Assert
    assert len(result["filtered_signal"]) == 1000
    assert len(result["mse_history"]) > 0
    # Should eventually converge with enough samples
    assert (
        result["convergence_iteration"] is None
        or result["convergence_iteration"] <= 1000
    )


def test_adaptive_filter_large_filter_length() -> None:
    """Test case 14: Edge case with large filter length."""
    # Arrange
    signal = np.random.randn(200).tolist()
    filter_length = 64

    # Act
    result = adaptive_filter(signal, filter_length=filter_length, algorithm="nlms")

    # Assert
    assert len(result["filter_weights"]) == filter_length
    assert len(result["filtered_signal"]) == 200


# Error case tests
def test_adaptive_filter_invalid_signal_type() -> None:
    """Test case 15: TypeError for invalid signal type."""
    # Arrange
    invalid_signal = "not a signal"
    expected_message = "signal must be a list or numpy array"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        adaptive_filter(cast(Any, invalid_signal))


def test_adaptive_filter_invalid_reference_type() -> None:
    """Test case 16: TypeError for invalid reference type."""
    # Arrange
    signal: list[float] = [1.0, 2.0, 3.0, 4.0] * 10
    invalid_reference = "not a signal"
    expected_message = "reference must be a list, numpy array, or None"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        adaptive_filter(signal, reference=cast(Any, invalid_reference))


def test_adaptive_filter_empty_signal() -> None:
    """Test case 17: ValueError for empty signal."""
    # Arrange
    empty_signal: list[float] = []
    expected_message = "signal cannot be empty"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        adaptive_filter(empty_signal)


def test_adaptive_filter_multidimensional_signal() -> None:
    """Test case 18: ValueError for multidimensional signal."""
    # Arrange
    invalid_signal: list[list[float]] = [[1.0, 2.0], [3.0, 4.0]]
    expected_message = "signal must be 1D"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        adaptive_filter(cast(Any, invalid_signal))


def test_adaptive_filter_negative_filter_length() -> None:
    """Test case 19: ValueError for negative filter length."""
    # Arrange
    signal: list[float] = [1.0, 2.0, 3.0, 4.0] * 10
    expected_message = "filter_length must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        adaptive_filter(signal, filter_length=-8)


def test_adaptive_filter_zero_filter_length() -> None:
    """Test case 20: ValueError for zero filter length."""
    # Arrange
    signal: list[float] = [1.0, 2.0, 3.0, 4.0] * 10
    expected_message = "filter_length must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        adaptive_filter(signal, filter_length=0)


def test_adaptive_filter_filter_length_exceeds_signal() -> None:
    """Test case 21: ValueError for filter length exceeding signal length."""
    # Arrange
    signal: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0]
    expected_message = "filter_length .* cannot exceed signal length"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        adaptive_filter(signal, filter_length=10)


def test_adaptive_filter_invalid_algorithm() -> None:
    """Test case 22: ValueError for invalid algorithm."""
    # Arrange
    signal: list[float] = [1.0, 2.0, 3.0, 4.0] * 10
    expected_message = "Invalid algorithm"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        adaptive_filter(signal, algorithm=cast(Any, "invalid"))


def test_adaptive_filter_negative_step_size() -> None:
    """Test case 23: ValueError for negative step size."""
    # Arrange
    signal: list[float] = [1.0, 2.0, 3.0, 4.0] * 10
    expected_message = "step_size must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        adaptive_filter(signal, step_size=-0.1)


def test_adaptive_filter_zero_step_size() -> None:
    """Test case 24: ValueError for zero step size."""
    # Arrange
    signal: list[float] = [1.0, 2.0, 3.0, 4.0] * 10
    expected_message = "step_size must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        adaptive_filter(signal, step_size=0.0)


def test_adaptive_filter_invalid_forgetting_factor_zero() -> None:
    """Test case 25: ValueError for forgetting factor = 0."""
    # Arrange
    signal: list[float] = [1.0, 2.0, 3.0, 4.0] * 10
    expected_message = "forgetting_factor must be in \\(0, 1\\]"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        adaptive_filter(signal, algorithm="rls", forgetting_factor=0.0)


def test_adaptive_filter_invalid_forgetting_factor_above_one() -> None:
    """Test case 26: ValueError for forgetting factor > 1."""
    # Arrange
    signal: list[float] = [1.0, 2.0, 3.0, 4.0] * 10
    expected_message = "forgetting_factor must be in \\(0, 1\\]"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        adaptive_filter(signal, algorithm="rls", forgetting_factor=1.5)


def test_adaptive_filter_reference_length_mismatch() -> None:
    """Test case 27: ValueError for reference signal length mismatch."""
    # Arrange
    signal: list[float] = [1.0, 2.0, 3.0, 4.0] * 10
    reference: list[float] = [1.0, 2.0, 3.0]  # Different length
    expected_message = "reference must have same length as signal"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        adaptive_filter(signal, reference=reference)


def test_adaptive_filter_invalid_filter_length_type() -> None:
    """Test case 28: TypeError for invalid filter_length type."""
    # Arrange
    signal: list[float] = [1.0, 2.0, 3.0, 4.0] * 10
    expected_message = "filter_length must be an integer"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        adaptive_filter(signal, filter_length=cast(Any, 8.5))


def test_adaptive_filter_invalid_algorithm_type() -> None:
    """Test case 29: TypeError for invalid algorithm type."""
    # Arrange
    signal: list[float] = [1.0, 2.0, 3.0, 4.0] * 10
    expected_message = "algorithm must be a string"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        adaptive_filter(signal, algorithm=cast(Any, 123))


def test_adaptive_filter_invalid_step_size_type() -> None:
    """Test case 30: TypeError for invalid step_size type."""
    # Arrange
    signal: list[float] = [1.0, 2.0, 3.0, 4.0] * 10
    expected_message = "step_size must be a number"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        adaptive_filter(signal, step_size=cast(Any, "0.1"))


def test_adaptive_filter_invalid_forgetting_factor_type() -> None:
    """Test case 31: TypeError for invalid forgetting_factor type."""
    # Arrange
    signal: list[float] = [1.0, 2.0, 3.0, 4.0] * 10
    expected_message = "forgetting_factor must be a number"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        adaptive_filter(signal, forgetting_factor=cast(Any, "0.99"))
