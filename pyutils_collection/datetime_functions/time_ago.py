"""Calculate human-readable time ago from datetime."""

from datetime import datetime


def time_ago(past_date: datetime, reference_date: datetime | None = None) -> str:
    """
    Get a human-readable description of how long ago a date was.

    Parameters
    ----------
    past_date : datetime
        The past datetime to compare.
    reference_date : datetime, optional
        The reference datetime to compare against (default: now).

    Returns
    -------
    str
        Human-readable time difference string (e.g., "2 hours ago", "3 days ago").

    Raises
    ------
    TypeError
        If past_date or reference_date is not a datetime object.
    ValueError
        If past_date is in the future relative to reference_date.

    Examples
    --------
    >>> from datetime import datetime, timedelta
    >>> past = datetime.now() - timedelta(hours=2)
    >>> time_ago(past)
    '2 hours ago'
    >>> past = datetime.now() - timedelta(days=3)
    >>> time_ago(past)
    '3 days ago'
    """
    if not isinstance(past_date, datetime):
        raise TypeError("past_date must be a datetime object")
    if reference_date is None:
        reference_date = (
            datetime.now(tz=past_date.tzinfo) if past_date.tzinfo else datetime.now()
        )
    if not isinstance(reference_date, datetime):
        raise TypeError("reference_date must be a datetime object")
    if past_date > reference_date:
        raise ValueError("past_date cannot be in the future relative to reference_date")
    diff = reference_date - past_date
    seconds = diff.total_seconds()
    if seconds < 60:
        return "just now" if seconds < 10 else f"{int(seconds)} seconds ago"
    minutes = seconds / 60
    if minutes < 60:
        return f"{int(minutes)} minute{'s' if int(minutes) != 1 else ''} ago"
    hours = minutes / 60
    if hours < 24:
        return f"{int(hours)} hour{'s' if int(hours) != 1 else ''} ago"
    days = diff.days
    if days < 7:
        return f"{days} day{'s' if days != 1 else ''} ago"
    weeks = days // 7
    if days < 30:
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    months = days // 30  # Approximate
    if days < 365:
        return f"{months} month{'s' if months != 1 else ''} ago"
    years = days // 365  # Approximate
    return f"{years} year{'s' if years != 1 else ''} ago"
