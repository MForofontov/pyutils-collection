"""Timezone conversion functionality."""

from datetime import datetime

import pytz


def convert_timezone(
    dt: datetime,
    to_timezone: str | pytz.BaseTzInfo,
    from_timezone: str | pytz.BaseTzInfo | None = None,
) -> datetime:
    """
    Convert a datetime object from one timezone to another.

    Parameters
    ----------
    dt : datetime
        The datetime object to convert.
    to_timezone : str or pytz.BaseTzInfo
        Target timezone (string name or pytz timezone object).
    from_timezone : str or pytz.BaseTzInfo, optional
        Source timezone (string name or pytz timezone object).
        If None and dt is naive, assumes UTC.

    Returns
    -------
    datetime
        Datetime object converted to the target timezone.

    Raises
    ------
    TypeError
        If dt is not a datetime object.
    ValueError
        If timezone names are invalid.

    Examples
    --------
    >>> from datetime import datetime
    >>> dt = datetime(2023, 12, 25, 15, 30)
    >>> convert_timezone(dt, 'US/Eastern', 'UTC')
    datetime.datetime(2023, 12, 25, 10, 30, tzinfo=<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>)
    """
    if not isinstance(dt, datetime):
        raise TypeError("dt must be a datetime object")

    # Convert timezone strings to pytz objects
    to_tz: pytz.BaseTzInfo
    if isinstance(to_timezone, str):
        try:
            to_tz = pytz.timezone(to_timezone)
        except pytz.exceptions.UnknownTimeZoneError as exc:
            raise ValueError(f"Unknown timezone: {to_timezone}") from exc
    else:
        to_tz = to_timezone  # Already a tzinfo object

    # Handle source timezone
    if dt.tzinfo is None:
        # Naive datetime
        from_tz: pytz.BaseTzInfo
        if from_timezone is None:
            # Assume UTC
            from_tz = pytz.UTC
        elif isinstance(from_timezone, str):
            try:
                from_tz = pytz.timezone(from_timezone)
            except pytz.exceptions.UnknownTimeZoneError as exc:
                raise ValueError(f"Unknown timezone: {from_timezone}") from exc
        else:
            from_tz = from_timezone

        # Localize the naive datetime
        dt = from_tz.localize(dt)

    # Convert to target timezone
    return dt.astimezone(to_tz)
