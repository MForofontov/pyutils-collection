"""Calculate age from a birth datetime."""

from datetime import datetime


def calculate_age(
    birth_date: datetime,
    reference_date: datetime | None = None,
) -> int:
    """
    Calculate the age in years from a birth datetime.

    Parameters
    ----------
    birth_date : datetime
        The birth datetime.
    reference_date : datetime, optional
        Datetime against which to calculate the age. Defaults to now in the
        birth date's timezone, or local naive time for a naive birth date.

    Returns
    -------
    int
        Age in completed years.

    Raises
    ------
    TypeError
        If ``birth_date`` or ``reference_date`` is not a ``datetime`` instance.
    ValueError
        If ``birth_date`` occurs after ``reference_date``.

    Examples
    --------
    >>> from datetime import datetime
    >>> calculate_age(datetime(2000, 1, 1), datetime(2020, 1, 1))
    20
    """
    if not isinstance(birth_date, datetime):
        raise TypeError("birth_date must be a datetime object")

    if reference_date is None:
        reference_date = datetime.now(tz=birth_date.tzinfo)
    elif not isinstance(reference_date, datetime):
        raise TypeError("reference_date must be a datetime object")

    if birth_date > reference_date:
        raise ValueError("birth_date cannot be in the future")

    age = reference_date.year - birth_date.year
    if (reference_date.month, reference_date.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age
