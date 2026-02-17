"""
Apply digital filter to signal with validation and multiple filter types.

Uses scipy.signal for filtering, adds validation, filter design helpers,
and comprehensive output.
"""

from typing import Literal

import numpy as np
from scipy import signal


def apply_filter(
    data: list[float] | np.ndarray,
    filter_type: Literal["lowpass", "highpass", "bandpass", "bandstop"] = "lowpass",
    cutoff: float | tuple[float, float] = 0.1,
    order: int = 5,
    filter_method: Literal["butter", "cheby1", "cheby2", "ellip"] = "butter",
    sampling_rate: float = 1.0,
) -> dict[str, np.ndarray]:
    """
    Apply digital filter to signal with validation.

    Uses scipy.signal for filtering, adds validation, filter design,
    and comprehensive output.

    Parameters
    ----------
    data : list[float] | np.ndarray
        Input signal to filter.
    filter_type : {'lowpass', 'highpass', 'bandpass', 'bandstop'}, optional
        Type of filter (by default 'lowpass').
    cutoff : float | tuple[float, float], optional
        Cutoff frequency/frequencies normalized to Nyquist (by default 0.1).
        For bandpass/bandstop, provide tuple of (low, high).
    order : int, optional
        Filter order (by default 5).
    filter_method : {'butter', 'cheby1', 'cheby2', 'ellip'}, optional
        Filter design method (by default 'butter').
    sampling_rate : float, optional
        Sampling rate in Hz (by default 1.0).

    Returns
    -------
    dict[str, np.ndarray]
        Dictionary containing:
        - filtered_signal: Filtered output signal
        - filter_b: Filter numerator coefficients
        - filter_a: Filter denominator coefficients

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If data is empty, cutoff is invalid, or order < 1.

    Examples
    --------
    >>> data = [1, 2, 3, 4, 5, 4, 3, 2, 1]
    >>> result = apply_filter(data, filter_type='lowpass', cutoff=0.3)
    >>> len(result['filtered_signal']) == len(data)
    True

    Notes
    -----
    Butterworth filter provides maximally flat passband.
    Chebyshev filters provide sharper cutoff but with ripple.

    Complexity
    ----------
    Time: O(n * order), Space: O(n)
    """
    # Input validation
    if not isinstance(data, (list, np.ndarray)):
        raise TypeError(
            f"data must be a list or numpy array, got {type(data).__name__}"
        )
    if not isinstance(filter_type, str):
        raise TypeError(
            f"filter_type must be a string, got {type(filter_type).__name__}"
        )
    if filter_type not in ("lowpass", "highpass", "bandpass", "bandstop"):
        raise ValueError(
            f"filter_type must be 'lowpass', 'highpass', 'bandpass', or 'bandstop', got '{filter_type}'"
        )
    if not isinstance(cutoff, (int, float, tuple, list)):
        raise TypeError(
            f"cutoff must be a number or tuple, got {type(cutoff).__name__}"
        )
    if not isinstance(order, int):
        raise TypeError(f"order must be an integer, got {type(order).__name__}")
    if order < 1:
        raise ValueError(f"order must be >= 1, got {order}")
    if not isinstance(filter_method, str):
        raise TypeError(
            f"filter_method must be a string, got {type(filter_method).__name__}"
        )
    if filter_method not in ("butter", "cheby1", "cheby2", "ellip"):
        raise ValueError(
            f"filter_method must be 'butter', 'cheby1', 'cheby2', or 'ellip', got '{filter_method}'"
        )
    if not isinstance(sampling_rate, (int, float)):
        raise TypeError(
            f"sampling_rate must be a number, got {type(sampling_rate).__name__}"
        )
    if sampling_rate <= 0:
        raise ValueError(f"sampling_rate must be positive, got {sampling_rate}")

    # Convert to numpy array
    try:
        arr = np.asarray(data, dtype=float)
    except (ValueError, TypeError) as e:
        raise ValueError(f"data contains non-numeric values: {e}") from e

    if arr.size == 0:
        raise ValueError("data cannot be empty")

    # Remove NaN values
    arr = arr[~np.isnan(arr)]
    if arr.size == 0:
        raise ValueError("data contains only NaN values")

    # Validate and normalize cutoff frequencies
    nyquist = sampling_rate / 2.0

    if filter_type in ("bandpass", "bandstop"):
        if not isinstance(cutoff, (tuple, list)):
            raise ValueError(
                f"cutoff must be a tuple for {filter_type} filter, got {type(cutoff).__name__}"
            )
        if len(cutoff) != 2:
            raise ValueError(f"cutoff must have 2 elements for {filter_type} filter")
        cutoff_norm_list = [c / nyquist for c in cutoff]
        if cutoff_norm_list[0] >= cutoff_norm_list[1]:
            raise ValueError("cutoff[0] must be < cutoff[1]")
        if any(c <= 0 or c >= 1 for c in cutoff_norm_list):
            raise ValueError("normalized cutoff frequencies must be between 0 and 1")
        cutoff_norm: float | list[float] = cutoff_norm_list
    else:
        if isinstance(cutoff, (tuple, list)):
            raise ValueError(
                f"cutoff must be a scalar for {filter_type} filter, got tuple/list"
            )
        cutoff_norm_scalar: float = cutoff / nyquist
        if cutoff_norm_scalar <= 0 or cutoff_norm_scalar >= 1:
            raise ValueError(
                f"normalized cutoff must be between 0 and 1, got {cutoff_norm_scalar}"
            )
        cutoff_norm = cutoff_norm_scalar

    # Design filter
    try:
        if filter_method == "butter":
            b, a = signal.butter(order, cutoff_norm, btype=filter_type)
        elif filter_method == "cheby1":
            b, a = signal.cheby1(order, 0.5, cutoff_norm, btype=filter_type)
        elif filter_method == "cheby2":
            b, a = signal.cheby2(order, 40, cutoff_norm, btype=filter_type)
        elif filter_method == "ellip":
            b, a = signal.ellip(order, 0.5, 40, cutoff_norm, btype=filter_type)
        else:
            raise ValueError(f"Unknown filter method: {filter_method}")
    except Exception as e:
        raise ValueError(f"failed to design filter: {e}") from e

    # Apply filter
    try:
        filtered = signal.filtfilt(b, a, arr)
    except Exception as e:
        raise ValueError(f"failed to apply filter: {e}") from e

    return {
        "filtered_signal": filtered,
        "filter_b": b,
        "filter_a": a,
    }


__all__ = ["apply_filter"]
