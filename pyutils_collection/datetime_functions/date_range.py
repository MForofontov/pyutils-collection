"""Lazy ranges of dates and datetimes."""

from collections.abc import Iterator
from datetime import date, datetime, timedelta


def date_range(
    start: date | datetime, stop: date | datetime, step: int | timedelta = 1
) -> Iterator[date | datetime]:
    """
    Yield dates or datetimes from start up to, excluding, stop.

    Parameters
    ----------
    start, stop : date or datetime
        Both must be dates or both datetimes. Datetimes must have compatible
        timezone awareness. Aware values must use the same timezone.
    step : int or timedelta, optional
        Nonzero increment; integers represent days (default 1). Negative steps
        descend. Plain dates require a whole-day timedelta.

    Yields
    ------
    date or datetime
        Values retaining the start's type and timezone. Datetime steps use
        local calendar arithmetic, including across daylight-saving transitions.

    Raises
    ------
    TypeError
        If endpoint types are invalid or mixed, or step has the wrong type.
    ValueError
        If step is zero, fractional days are used with dates, or timezones differ.

    Examples
    --------
    >>> list(date_range(date(2025, 1, 1), date(2025, 1, 3)))
    [datetime.date(2025, 1, 1), datetime.date(2025, 1, 2)]

    Notes
    -----
    Validation occurs when iteration begins. A step pointing away from stop
    produces an empty range. No out-of-range addition is attempted after overflow.

    Complexity
    ----------
    Time: O(n), Space: O(1).
    """
    if not isinstance(start, date) or not isinstance(stop, date):
        raise TypeError("start and stop must be dates or datetimes")
    if isinstance(start, datetime) != isinstance(stop, datetime):
        raise TypeError("start and stop must have matching date or datetime types")
    if isinstance(start, datetime) and isinstance(stop, datetime):
        if start.tzinfo != stop.tzinfo:
            raise ValueError("start and stop must use the same timezone")
    if isinstance(step, bool) or not isinstance(step, (int, timedelta)):
        raise TypeError("step must be an integer or timedelta")
    delta = timedelta(days=step) if isinstance(step, int) else step
    if not delta:
        raise ValueError("step must not be zero")
    if not isinstance(start, datetime) and (delta.seconds or delta.microseconds):
        raise ValueError("date steps must be whole days")

    ascending = delta > timedelta(0)
    current = start
    while (current < stop) if ascending else (current > stop):
        yield current
        try:
            current += delta
        except OverflowError:
            return


__all__ = ["date_range"]
