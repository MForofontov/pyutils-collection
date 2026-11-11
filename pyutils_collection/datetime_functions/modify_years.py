"""Modify years on a date or datetime object."""

from datetime import date, datetime


def modify_years(date_obj: datetime | date, years: int) -> datetime | date:
    """
    Add or subtract a specified number of years from a datetime or
    date object.

    Parameters
    ----------
    date_obj : datetime | date
        The date or datetime to modify.
    years : int
        Number of years to add (positive) or subtract (negative).

    Returns
    -------
    datetime | date
        The modified date or datetime.

    Raises
    ------
    TypeError
        If ``date_obj`` is not a :class:`datetime.datetime` or
        :class:`datetime.date`.
    TypeError
        If ``years`` is not an integer.
    ValueError
        If the resulting date would be invalid (e.g., February 29 on a
        non-leap year).

    Examples
    --------
    >>> from datetime import date, datetime
    >>> modify_years(date(2020, 2, 29), 1)
    datetime.date(2021, 2, 28)
    >>> modify_years(datetime(2020, 5, 17), -2)
    datetime.datetime(2018, 5, 17, 0, 0)
    """
    if not isinstance(date_obj, (datetime, date)):
        raise TypeError("date_obj must be a datetime or date object")

    if not isinstance(years, int) or isinstance(years, bool):
        raise TypeError("years must be an integer")

    new_year = date_obj.year + years

    try:
        if isinstance(date_obj, datetime):
            return date_obj.replace(year=new_year)
        else:
            return date_obj.replace(year=new_year)
    except ValueError:
        # Handle Feb 29 on non-leap year
        if date_obj.month == 2 and date_obj.day == 29:
            if isinstance(date_obj, datetime):
                return date_obj.replace(year=new_year, day=28)
            else:
                return date_obj.replace(year=new_year, day=28)
        else:
            raise
