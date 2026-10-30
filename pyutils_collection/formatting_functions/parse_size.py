"""Parse human-readable size strings into bytes."""

import re
from fractions import Fraction


def parse_size(size_str: str, binary: bool = True) -> int:
    """
    Parse a human-readable size string into bytes.

    Parameters
    ----------
    size_str : str
        Size string to parse (e.g., "1.5 GB", "2 MiB", "512KB").
    binary : bool, optional
        Assume binary units (1024) if True, decimal units (1000) if False (by default True).

    Returns
    -------
    int
        Size in bytes.

    Raises
    ------
    TypeError
        If size_str is not a string or binary is not a boolean.
    ValueError
        If size_str has invalid format or contains negative value.

    Examples
    --------
    >>> parse_size("1.5 GB")
    1610612736
    >>> parse_size("1.5 GB", binary=False)
    1500000000
    >>> parse_size("2 MiB")
    2097152
    >>> parse_size("512 KB", binary=False)
    512000
    >>> parse_size("1024")
    1024
    >>> parse_size("0 B")
    0

    Notes
    -----
    Supported units (case-insensitive):
    - Binary (1024-based): B, K/KB/KiB, M/MB/MiB, G/GB/GiB, T/TB/TiB, P/PB/PiB, E/EB/EiB, Z/ZB/ZiB, Y/YB/YiB
    - Decimal (1000-based): B, K/KB, M/MB, G/GB, T/TB, P/PB, E/EB, Z/ZB, Y/YB

    If no unit is specified, bytes are assumed.

    Complexity
    ----------
    Time and space depend on input length and numeric precision.
    """
    # Input validation
    if not isinstance(size_str, str):
        raise TypeError(f"size_str must be a string, got {type(size_str).__name__}")
    if not isinstance(binary, bool):
        raise TypeError(f"binary must be a boolean, got {type(binary).__name__}")

    # Normalize input
    size_str = size_str.strip()
    if not size_str:
        raise ValueError("size_str cannot be empty")

    # Parse number and unit
    match = re.match(r"^([0-9.]+)\s*([a-zA-Z]*)$", size_str)
    if not match:
        raise ValueError(f"Invalid size format: {size_str}")

    number_str, unit = match.groups()

    # Parse number
    try:
        number = Fraction(number_str)
    except ValueError:
        raise ValueError(f"Invalid number in size string: {number_str}") from None

    if number < 0:
        raise ValueError(f"Size cannot be negative: {number}")

    # Normalize unit
    unit = unit.upper().strip()
    if not unit or unit == "B":
        return int(number)

    # Define multipliers
    if binary:
        multipliers = {
            "K": 1024,
            "KB": 1024,
            "KIB": 1024,
            "M": 1024**2,
            "MB": 1024**2,
            "MIB": 1024**2,
            "G": 1024**3,
            "GB": 1024**3,
            "GIB": 1024**3,
            "T": 1024**4,
            "TB": 1024**4,
            "TIB": 1024**4,
            "P": 1024**5,
            "PB": 1024**5,
            "PIB": 1024**5,
            "E": 1024**6,
            "EB": 1024**6,
            "EIB": 1024**6,
            "Z": 1024**7,
            "ZB": 1024**7,
            "ZIB": 1024**7,
            "Y": 1024**8,
            "YB": 1024**8,
            "YIB": 1024**8,
        }
    else:
        multipliers = {
            "K": 1000,
            "KB": 1000,
            "M": 1000**2,
            "MB": 1000**2,
            "G": 1000**3,
            "GB": 1000**3,
            "T": 1000**4,
            "TB": 1000**4,
            "P": 1000**5,
            "PB": 1000**5,
            "E": 1000**6,
            "EB": 1000**6,
            "Z": 1000**7,
            "ZB": 1000**7,
            "Y": 1000**8,
            "YB": 1000**8,
        }

    if unit not in multipliers:
        raise ValueError(f"Unknown unit: {unit}")

    return int(number * multipliers[unit])


__all__ = ["parse_size"]
