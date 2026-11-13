"""Format large numbers into compact notation."""


def format_number_compact(
    number: int | float,
    precision: int = 1,
    threshold: int = 1000,
) -> str:
    """
    Format a large number into compact notation with suffixes.

    Parameters
    ----------
    number : int | float
        Number to format.
    precision : int, optional
        Maximum number of decimal places to display (by default 1). Fractional
        trailing zeros are removed; integer trailing zeros are preserved.
    threshold : int, optional
        Minimum value to start using compact notation (by default 1000).

    Returns
    -------
    str
        Formatted number string (e.g., "1.5M", "2.3K", "450").

    Raises
    ------
    TypeError
        If number is not a number, precision is not an integer, or threshold is not an integer.
    ValueError
        If precision or threshold is negative.

    Examples
    --------
    >>> format_number_compact(1500)
    '1.5K'
    >>> format_number_compact(1500000)
    '1.5M'
    >>> format_number_compact(2300000000)
    '2.3B'
    >>> format_number_compact(500)
    '500'
    >>> format_number_compact(1500, precision=2)
    '1.5K'
    >>> format_number_compact(999, threshold=1000)
    '999'
    >>> format_number_compact(1000, threshold=1000)
    '1K'
    >>> format_number_compact(10000, precision=0)
    '10K'
    >>> format_number_compact(0)
    '0'
    >>> format_number_compact(-1500)
    '-1.5K'

    Notes
    -----
    Suffixes used: K (thousand), M (million), B (billion), T (trillion), Q (quadrillion)
    Numbers below threshold are returned as-is without suffix.

    Complexity
    ----------
    Time: O(1), Space: O(1)
    """
    # Input validation
    if not isinstance(number, (int, float)):
        raise TypeError(f"number must be a number, got {type(number).__name__}")
    if not isinstance(precision, int):
        raise TypeError(f"precision must be an integer, got {type(precision).__name__}")
    if not isinstance(threshold, int):
        raise TypeError(f"threshold must be an integer, got {type(threshold).__name__}")

    if precision < 0:
        raise ValueError(f"precision must be non-negative, got {precision}")
    if threshold < 0:
        raise ValueError(f"threshold must be non-negative, got {threshold}")

    # Handle special cases
    if number == 0:
        return "0"

    # Handle negative numbers
    abs_number = abs(number)

    # If below threshold, return as-is
    if abs_number < threshold:
        if isinstance(number, float) and number % 1 != 0:
            return f"{number:.{precision}f}"
        return str(int(number))

    # Define suffixes and their thresholds
    suffixes = [
        ("Q", 1_000_000_000_000_000),  # Quadrillion
        ("T", 1_000_000_000_000),  # Trillion
        ("B", 1_000_000_000),  # Billion
        ("M", 1_000_000),  # Million
        ("K", 1_000),  # Thousand
    ]

    # Find appropriate suffix
    for suffix, divisor in suffixes:
        if abs_number >= divisor:
            value = number / divisor
            # Format with precision
            formatted = f"{value:.{precision}f}"
            if "." in formatted:
                formatted = formatted.rstrip("0").rstrip(".")
            return f"{formatted}{suffix}"

    # Fallback (should not reach here given logic above)
    return str(int(number))


__all__ = ["format_number_compact"]
