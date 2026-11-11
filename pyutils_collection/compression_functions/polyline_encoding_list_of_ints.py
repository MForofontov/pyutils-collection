"""Polyline encoding for integer lists."""


def polyline_encoding_list_of_ints(list_of_ints: list[int], precision: int = 0) -> str:
    """
    Encode a list of integers using polyline encoding.

    Parameters
    ----------
    list_of_ints : list[int]
        List of integers to be encoded.
    precision : int, optional
        Number of decimal places for precision encoding (default: 0).

    Returns
    -------
    str
        The encoded polyline string.

    Raises
    ------
    ValueError
        If the input list is empty or precision is negative.

    Examples
    --------
    >>> polyline_encoding_list_of_ints([1, 2])
    '?AA'
    """
    if not list_of_ints:
        raise ValueError("Input list cannot be empty.")
    if precision < 0:
        raise ValueError("Precision must be non-negative.")

    # Start with precision encoded as first character
    encoded_text: str = chr(precision + 63)
    last_number: int = 0

    for number in list_of_ints:
        scaled_number = int(round(number * (10**precision)))
        delta: int = scaled_number - last_number
        last_number = scaled_number

        # Encode the delta using the polyline encoding scheme
        delta = ~(delta << 1) if delta < 0 else (delta << 1)
        while delta >= 0x20:
            encoded_text += chr((0x20 | (delta & 0x1F)) + 63)
            delta >>= 5
        encoded_text += chr(delta + 63)

    return encoded_text


__all__ = ["polyline_encoding_list_of_ints"]
