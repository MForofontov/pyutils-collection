"""Calculate the power of a number."""

import math

# Safety limits to prevent overflow and memory exhaustion
_MAX_EXPONENT = 10000
_MAX_BASE_ABS = 10**308  # Close to float max


def power(base: int | float, exponent: int | float) -> int | float:
    """
    Calculate base raised to the power of exponent.

    Parameters
    ----------
    base : int | float
        The base number.
    exponent : int | float
        The exponent.

    Returns
    -------
    int | float
        The result of base^exponent. Returns int if both inputs are int and
        result is a whole number, otherwise returns float.

    Raises
    ------
    TypeError
        If base or exponent is not numeric.
    ValueError
        If computation would overflow or consume excessive memory.
        Base must be in range [-10^308, 10^308] and exponent in range [-10000, 10000].

    Examples
    --------
    >>> power(2, 3)
    8
    >>> power(2.5, 2)
    6.25
    >>> power(9, 0.5)
    3.0
    >>> power(10, -1)
    0.1

    Notes
    -----
    Safety limits are enforced to prevent:
    - Float overflow to infinity
    - Memory exhaustion from large integer results
    - Hanging operations from extreme computations

    Complexity
    ----------
    Time: O(log exponent) for integer exponentiation, O(1) for float
    Space: O(1) for bounded results
    """
    if not isinstance(base, (int, float)):
        raise TypeError("base must be numeric (int or float)")

    if not isinstance(exponent, (int, float)):
        raise TypeError("exponent must be numeric (int or float)")

    # Check for NaN and Inf
    if isinstance(base, float) and (math.isnan(base) or math.isinf(base)):
        raise ValueError("base cannot be NaN or Inf")
    if isinstance(exponent, float) and (
        math.isnan(exponent) or math.isinf(exponent)
    ):
        raise ValueError("exponent cannot be NaN or Inf")

    # Safety limits to prevent overflow/memory exhaustion
    if abs(base) > _MAX_BASE_ABS:
        raise ValueError(
            f"base magnitude must be <= {_MAX_BASE_ABS:.2e} to prevent overflow"
        )
    if abs(exponent) > _MAX_EXPONENT:
        raise ValueError(
            f"exponent magnitude must be <= {_MAX_EXPONENT} to prevent overflow"
        )

    # Additional check for potentially dangerous combinations
    if abs(base) > 1 and exponent > 1000:
        # Estimate result size to prevent memory exhaustion
        log_result = abs(exponent * math.log10(abs(base)))
        if log_result > 300:  # Would exceed ~10^300
            raise ValueError(
                "computation would result in value too large (> 10^300), "
                "risking overflow or memory exhaustion"
            )

    result = base**exponent

    # Check if result overflowed to inf
    if isinstance(result, float) and math.isinf(result):
        raise ValueError("computation resulted in overflow (infinity)")

    # Check if result is NaN
    if isinstance(result, float) and math.isnan(result):
        raise ValueError("computation resulted in NaN (invalid operation)")

    # Return int if both inputs are int and result is a whole number
    if (
        isinstance(base, int)
        and isinstance(exponent, int)
        and isinstance(result, (int, float))
    ):
        if result == int(result):
            return int(result)

    return result


__all__ = ["power"]
