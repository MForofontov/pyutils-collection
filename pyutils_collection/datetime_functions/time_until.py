"""Calculate human-readable time until future datetime."""

from datetime import datetime


def time_until(future_date: datetime, reference_date: datetime | None = None) -> str:
    """
    Get a human-readable description of how long until a future date.

    Parameters
    ----------
    future_date : datetime
        The future datetime to compare.
    reference_date : datetime, optional
        The reference datetime to compare against (default: now).

    Returns
    -------
    str
        Human-readable time difference string (e.g., "in 2 hours", "in 3 days").

    Raises
    ------
    TypeError
        If future_date or reference_date is not a datetime object.
    ValueError
        If future_date is in the past relative to reference_date.

    Examples
    --------
    >>> from datetime import datetime, timedelta
    >>> future = datetime.now() + timedelta(hours=2)
    >>> time_until(future)
    'in 2 hours'
    >>> future = datetime.now() + timedelta(days=3)
    >>> time_until(future)
    'in 3 days'

    Complexity
    ----------
    Time: O(1), Space: O(1)
    """
    if not isinstance(future_date, datetime):
        raise TypeError("future_date must be a datetime object")
    if reference_date is None:
        reference_date = (
            datetime.now(tz=future_date.tzinfo)
            if future_date.tzinfo
            else datetime.now()
        )
    if not isinstance(reference_date, datetime):
        raise TypeError("reference_date must be a datetime object")
    if future_date < reference_date:
        raise ValueError("future_date cannot be in the past relative to reference_date")
    diff = future_date - reference_date
    seconds = diff.total_seconds()
    if seconds < 60:
        return "in a moment" if seconds < 10 else f"in {int(seconds)} seconds"
    minutes = seconds / 60
    if minutes < 60:
        return f"in {int(minutes)} minute{'s' if int(minutes) != 1 else ''}"
    hours = minutes / 60
    if hours < 24:
        return f"in {int(hours)} hour{'s' if int(hours) != 1 else ''}"
    days = diff.days
    if days < 7:
        return f"in {days} day{'s' if days != 1 else ''}"
    weeks = days // 7
    if days < 30:
        return f"in {weeks} week{'s' if weeks != 1 else ''}"
    months = days // 30  # Approximate
    if days < 365:
        return f"in {months} month{'s' if months != 1 else ''}"
    years = days // 365  # Approximate
    return f"in {years} year{'s' if years != 1 else ''}"
