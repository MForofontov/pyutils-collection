"""
Unit tests for apply_filter function.

Tests cover:
- Normal cases: various filter types and methods
- Edge cases: small signals, extreme cutoffs, high order
- Error cases: invalid types, empty data, invalid parameters
"""

from typing import Any, cast

try:
    import numpy as np
    import scipy
    from pyutils_collection.scientific_computing_functions.signal_processing.apply_filter import apply_filter
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None  # type: ignore
    scipy = None
    apply_filter = None  # type: ignore

import pytest

pytestmark = [pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy and/or scipy not installed"), pytest.mark.unit, pytest.mark.scientific_computing]

# ========== Normal Operation Tests ==========


def test_apply_filter_lowpass_default() -> None:
    """Test case 1: Lowpass filter with default parameters."""
    # Arrange
    data: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0, 4.0, 3.0, 2.0, 1.0]

    # Act
    result = apply_filter(data, order=1)

    # Assert
    assert "filtered_signal" in result
    assert "filter_b" in result
    assert "filter_a" in result
    assert len(result["filtered_signal"]) == len(data)
    assert isinstance(result["filtered_signal"], np.ndarray)
    assert isinstance(result["filter_b"], np.ndarray)
    assert isinstance(result["filter_a"], np.ndarray)


def test_apply_filter_highpass() -> None:
    """Test case 2: Highpass filter."""
    # Arrange
    data: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0, 4.0, 3.0, 2.0, 1.0]

    # Act
    result = apply_filter(data, filter_type="highpass", cutoff=0.3, order=1)

    # Assert
    assert len(result["filtered_signal"]) == len(data)
    assert np.all(np.isfinite(result["filtered_signal"]))


def test_apply_filter_bandpass() -> None:
    """Test case 3: Bandpass filter with tuple cutoff."""
    # Arrange
    data: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0, 5.0, 4.0, 3.0, 2.0, 1.0]
    cutoff = (0.1, 0.4)

    # Act
    result = apply_filter(data, filter_type="bandpass", cutoff=cutoff, order=1)

    # Assert
    assert len(result["filtered_signal"]) == len(data)
    assert np.all(np.isfinite(result["filtered_signal"]))


def test_apply_filter_bandstop() -> None:
    """Test case 4: Bandstop filter."""
    # Arrange
    data: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0, 5.0, 4.0, 3.0, 2.0, 1.0]
    cutoff = (0.2, 0.4)

    # Act
    result = apply_filter(data, filter_type="bandstop", cutoff=cutoff, order=1)

    # Assert
    assert len(result["filtered_signal"]) == len(data)
    assert np.all(np.isfinite(result["filtered_signal"]))


def test_apply_filter_cheby1_method() -> None:
    """Test case 5: Chebyshev type 1 filter."""
    # Arrange
    data: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0, 4.0, 3.0, 2.0, 1.0]

    # Act
    result = apply_filter(data, filter_method="cheby1", order=1)

    # Assert
    assert len(result["filtered_signal"]) == len(data)
    assert np.all(np.isfinite(result["filtered_signal"]))


def test_apply_filter_cheby2_method() -> None:
    """Test case 6: Chebyshev type 2 filter."""
    # Arrange
    data: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0, 4.0, 3.0, 2.0, 1.0]

    # Act
    result = apply_filter(data, filter_method="cheby2", order=1)

    # Assert
    assert len(result["filtered_signal"]) == len(data)
    assert np.all(np.isfinite(result["filtered_signal"]))


def test_apply_filter_ellip_method() -> None:
    """Test case 7: Elliptic filter."""
    # Arrange
    data: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0, 4.0, 3.0, 2.0, 1.0]

    # Act
    result = apply_filter(data, filter_method="ellip", order=1)

    # Assert
    assert len(result["filtered_signal"]) == len(data)
    assert np.all(np.isfinite(result["filtered_signal"]))


def test_apply_filter_numpy_array() -> None:
    """Test case 8: Filter with numpy array input."""
    # Arrange
    data = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 4.0, 3.0, 2.0, 1.0])

    # Act
    result = apply_filter(data, order=1)

    # Assert
    assert len(result["filtered_signal"]) == len(data)
    assert np.all(np.isfinite(result["filtered_signal"]))


def test_apply_filter_custom_sampling_rate() -> None:
    """Test case 9: Filter with custom sampling rate."""
    # Arrange
    data: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0, 4.0, 3.0, 2.0, 1.0]
    sampling_rate = 1000.0
    cutoff_hz = 100.0  # 100 Hz cutoff

    # Act
    result = apply_filter(data, cutoff=cutoff_hz, sampling_rate=sampling_rate, order=1)

    # Assert
    assert len(result["filtered_signal"]) == len(data)
    assert np.all(np.isfinite(result["filtered_signal"]))


# ========== Edge Case Tests ==========


def test_apply_filter_minimum_valid_signal() -> None:
    """Test case 10: Edge case with minimum valid signal length."""
    # Arrange
    # scipy filtfilt requires minimum length > 3 * max(len(a), len(b))
    data = [1.0, 2.0, 3.0, 4.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.5]

    # Act
    result = apply_filter(data, order=1)

    # Assert
    assert len(result["filtered_signal"]) == len(data)
    assert np.all(np.isfinite(result["filtered_signal"]))


def test_apply_filter_small_signal() -> None:
    """Test case 11: Edge case with small signal."""
    # Arrange
    data = list(np.sin(np.linspace(0, 2 * np.pi, 20)))

    # Act
    result = apply_filter(data, order=1)

    # Assert
    assert len(result["filtered_signal"]) == len(data)
    assert np.all(np.isfinite(result["filtered_signal"]))


def test_apply_filter_very_low_cutoff() -> None:
    """Test case 12: Edge case with very low cutoff frequency."""
    # Arrange
    data: list[float] = list(np.sin(np.linspace(0, 10, 100)))
    cutoff = 0.05  # Low cutoff

    # Act
    result = apply_filter(data, cutoff=cutoff, order=2)

    # Assert
    assert len(result["filtered_signal"]) == len(data)
    assert np.all(np.isfinite(result["filtered_signal"]))


def test_apply_filter_very_high_cutoff() -> None:
    """Test case 13: Edge case with moderate-high cutoff frequency."""
    # Arrange
    data: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0, 4.0, 3.0, 2.0, 1.0]
    cutoff = 0.45  # Moderate-high cutoff (below Nyquist)

    # Act
    result = apply_filter(data, cutoff=cutoff, order=1)

    # Assert
    assert len(result["filtered_signal"]) == len(data)
    assert np.all(np.isfinite(result["filtered_signal"]))


def test_apply_filter_high_order() -> None:
    """Test case 14: Edge case with high filter order."""
    # Arrange
    data = list(np.sin(np.linspace(0, 10, 100)))

    # Act
    result = apply_filter(data, order=10)

    # Assert
    assert len(result["filtered_signal"]) == len(data)
    assert np.all(np.isfinite(result["filtered_signal"]))


def test_apply_filter_large_signal() -> None:
    """Test case 15: Performance test with large signal."""
    # Arrange
    data = list(np.random.randn(10000))

    # Act
    result = apply_filter(data)

    # Assert
    assert len(result["filtered_signal"]) == len(data)
    assert np.all(np.isfinite(result["filtered_signal"]))


def test_apply_filter_data_with_nan() -> None:
    """Test case 16: Edge case with NaN values in longer signal."""
    # Arrange
    data = [1.0, 2.0, np.nan, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0]

    # Act
    result = apply_filter(data, order=2)

    # Assert
    # NaN values should be removed, resulting in shorter signal
    assert len(result["filtered_signal"]) == 11  # 12 - 1 NaN
    assert np.all(np.isfinite(result["filtered_signal"]))


# ========== Error Case Tests ==========


def test_apply_filter_invalid_data_type() -> None:
    """Test case 17: TypeError for invalid data type."""
    # Arrange
    invalid_data = "not a list"
    expected_message = "data must be a list or numpy array"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        apply_filter(cast(Any, invalid_data))


def test_apply_filter_invalid_filter_type_type() -> None:
    """Test case 18: TypeError for invalid filter_type type."""
    # Arrange
    data = [1, 2, 3, 4, 5]
    invalid_type = 123
    expected_message = "filter_type must be a string"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        apply_filter(data, filter_type=invalid_type)  # type: ignore


def test_apply_filter_invalid_filter_type_value() -> None:
    """Test case 19: ValueError for invalid filter_type value."""
    # Arrange
    data = [1, 2, 3, 4, 5]
    invalid_type = "invalid"
    expected_message = "filter_type must be"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        apply_filter(data, filter_type=invalid_type)  # type: ignore


def test_apply_filter_invalid_cutoff_type() -> None:
    """Test case 20: TypeError for invalid cutoff type."""
    # Arrange
    data = [1, 2, 3, 4, 5]
    invalid_cutoff = "invalid"
    expected_message = "cutoff must be a number or tuple"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        apply_filter(data, cutoff=invalid_cutoff)  # type: ignore


def test_apply_filter_invalid_order_type() -> None:
    """Test case 21: TypeError for invalid order type."""
    # Arrange
    data = [1, 2, 3, 4, 5]
    invalid_order = 5.5
    expected_message = "order must be an integer"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        apply_filter(data, order=invalid_order)  # type: ignore


def test_apply_filter_invalid_order_value() -> None:
    """Test case 22: ValueError for order < 1."""
    # Arrange
    data: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0]
    invalid_order = 0
    expected_message = "order must be >= 1"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        apply_filter(data, order=invalid_order)


def test_apply_filter_negative_order() -> None:
    """Test case 23: ValueError for negative order."""
    # Arrange
    data: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0]
    invalid_order = -1
    expected_message = "order must be >= 1"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        apply_filter(data, order=invalid_order)


def test_apply_filter_invalid_filter_method_type() -> None:
    """Test case 24: TypeError for invalid filter_method type."""
    # Arrange
    data = [1, 2, 3, 4, 5]
    invalid_method = 123
    expected_message = "filter_method must be a string"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        apply_filter(data, filter_method=invalid_method)  # type: ignore


def test_apply_filter_invalid_filter_method_value() -> None:
    """Test case 25: ValueError for invalid filter_method value."""
    # Arrange
    data = [1, 2, 3, 4, 5]
    invalid_method = "invalid"
    expected_message = "filter_method must be"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        apply_filter(data, filter_method=invalid_method)  # type: ignore


def test_apply_filter_invalid_sampling_rate_type() -> None:
    """Test case 26: TypeError for invalid sampling_rate type."""
    # Arrange
    data = [1, 2, 3, 4, 5]
    invalid_rate = "invalid"
    expected_message = "sampling_rate must be a number"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        apply_filter(data, sampling_rate=invalid_rate)  # type: ignore


def test_apply_filter_negative_sampling_rate() -> None:
    """Test case 27: ValueError for negative sampling_rate."""
    # Arrange
    data: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0]
    invalid_rate = -1.0
    expected_message = "sampling_rate must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        apply_filter(data, sampling_rate=invalid_rate)


def test_apply_filter_zero_sampling_rate() -> None:
    """Test case 28: ValueError for zero sampling_rate."""
    # Arrange
    data: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0]
    invalid_rate = 0.0
    expected_message = "sampling_rate must be positive"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        apply_filter(data, sampling_rate=invalid_rate)


def test_apply_filter_empty_data() -> None:
    """Test case 29: ValueError for empty data."""
    # Arrange
    empty_data: list[float] = []
    expected_message = "data cannot be empty"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        apply_filter(empty_data)


def test_apply_filter_all_nan_data() -> None:
    """Test case 30: ValueError for data with only NaN values."""
    # Arrange
    nan_data = [np.nan, np.nan, np.nan]
    expected_message = "data contains only NaN values"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        apply_filter(nan_data)


def test_apply_filter_non_numeric_data() -> None:
    """Test case 31: ValueError for non-numeric data."""
    # Arrange
    invalid_data = ["a", "b", "c"]
    expected_message = "data contains non-numeric values"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        apply_filter(cast(Any, invalid_data))


def test_apply_filter_bandpass_scalar_cutoff() -> None:
    """Test case 32: ValueError for bandpass filter with scalar cutoff."""
    # Arrange
    data: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0]
    cutoff = 0.3  # Scalar instead of tuple
    expected_message = "cutoff must be a tuple for bandpass filter"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        apply_filter(data, filter_type="bandpass", cutoff=cutoff)


def test_apply_filter_bandstop_scalar_cutoff() -> None:
    """Test case 33: ValueError for bandstop filter with scalar cutoff."""
    # Arrange
    data: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0]
    cutoff = 0.3  # Scalar instead of tuple
    expected_message = "cutoff must be a tuple for bandstop filter"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        apply_filter(data, filter_type="bandstop", cutoff=cutoff)


def test_apply_filter_bandpass_wrong_tuple_length() -> None:
    """Test case 34: ValueError for bandpass filter with wrong tuple length."""
    # Arrange
    data: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0]
    cutoff = (0.1, 0.2, 0.3)  # 3 elements instead of 2
    expected_message = "cutoff must have 2 elements"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        apply_filter(data, filter_type="bandpass", cutoff=cast(Any, cutoff))


def test_apply_filter_bandpass_inverted_cutoff() -> None:
    """Test case 35: ValueError for bandpass with inverted cutoff frequencies."""
    # Arrange
    data: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0]
    cutoff = (0.4, 0.2)  # Low > High
    expected_message = "cutoff\\[0\\] must be < cutoff\\[1\\]"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        apply_filter(data, filter_type="bandpass", cutoff=cutoff)


def test_apply_filter_bandpass_equal_cutoff() -> None:
    """Test case 36: ValueError for bandpass with equal cutoff frequencies."""
    # Arrange
    data: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0]
    cutoff = (0.3, 0.3)  # Low == High
    expected_message = "cutoff\\[0\\] must be < cutoff\\[1\\]"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        apply_filter(data, filter_type="bandpass", cutoff=cutoff)


def test_apply_filter_lowpass_tuple_cutoff() -> None:
    """Test case 37: ValueError for lowpass filter with tuple cutoff."""
    # Arrange
    data: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0]
    cutoff = (0.2, 0.4)  # Tuple instead of scalar
    expected_message = "cutoff must be a scalar for lowpass filter"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        apply_filter(data, filter_type="lowpass", cutoff=cutoff)


def test_apply_filter_highpass_tuple_cutoff() -> None:
    """Test case 38: ValueError for highpass filter with tuple cutoff."""
    # Arrange
    data: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0]
    cutoff = (0.2, 0.4)  # Tuple instead of scalar
    expected_message = "cutoff must be a scalar for highpass filter"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        apply_filter(data, filter_type="highpass", cutoff=cutoff)


def test_apply_filter_cutoff_out_of_range_low() -> None:
    """Test case 39: ValueError for cutoff frequency <= 0."""
    # Arrange
    data: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0]
    cutoff = 0.0  # Zero normalized cutoff
    expected_message = "normalized cutoff must be between 0 and 1"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        apply_filter(data, cutoff=cutoff)


def test_apply_filter_cutoff_out_of_range_high() -> None:
    """Test case 40: ValueError for cutoff frequency >= 1."""
    # Arrange
    data: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0]
    cutoff = 1.0  # Equals Nyquist
    expected_message = "normalized cutoff must be between 0 and 1"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        apply_filter(data, cutoff=cutoff)


def test_apply_filter_bandpass_cutoff_out_of_range() -> None:
    """Test case 41: ValueError for bandpass cutoff frequencies out of range."""
    # Arrange
    data: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0]
    cutoff = (0.0, 0.5)  # Low frequency is 0
    expected_message = "normalized cutoff frequencies must be between 0 and 1"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        apply_filter(data, filter_type="bandpass", cutoff=cutoff)
