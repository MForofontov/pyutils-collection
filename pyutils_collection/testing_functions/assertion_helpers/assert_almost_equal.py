"""
Assert two floats are almost equal within tolerance.
"""


def assert_almost_equal(
    actual: float,
    expected: float,
    tolerance: float = 1e-9,
) -> None:
    """
    Assert that two floats are almost equal within tolerance.

    Parameters
    ----------
    actual : float
        Actual value.
    expected : float
        Expected value.
    tolerance : float, optional
        Allowed difference (by default 1e-9).

    Returns
    -------
    None

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If tolerance is negative or NaN.
    AssertionError
        If values differ by more than tolerance or either value is NaN.
        Matching infinities compare equal.

    Examples
    --------
    >>> assert_almost_equal(0.1 + 0.2, 0.3)
    >>> assert_almost_equal(1.0001, 1.0002, 0.001)

    Complexity
    ----------
    Time: O(1), Space: O(1)
    """
    if not isinstance(actual, (int, float)):
        raise TypeError(f"actual must be a number, got {type(actual).__name__}")
    if not isinstance(expected, (int, float)):
        raise TypeError(f"expected must be a number, got {type(expected).__name__}")
    if not isinstance(tolerance, (int, float)):
        raise TypeError(f"tolerance must be a number, got {type(tolerance).__name__}")

    if tolerance < 0 or tolerance != tolerance:
        raise ValueError(f"tolerance must be non-negative and not NaN, got {tolerance}")

    diff = abs(actual - expected)
    if actual != expected and not diff <= tolerance:
        raise AssertionError(
            f"Values differ by {diff}, which exceeds tolerance {tolerance}: "
            f"actual={actual}, expected={expected}"
        )


__all__ = ["assert_almost_equal"]
