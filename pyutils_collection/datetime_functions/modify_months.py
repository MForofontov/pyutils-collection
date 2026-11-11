"""Modify months on a date or datetime object."""

from calendar import monthrange
from datetime import date, datetime


def modify_months(date_obj: datetime | date, months: int) -> datetime | date:
    """
    Add or subtract a specified number of months from a datetime or date object.

    Args:
        date_obj: The datetime or date object to modify
        months: Number of months to add (positive) or subtract (negative)

    Returns:
        New datetime or date object with months modified

    Raises:
        TypeError: If date_obj is not a datetime or date object
        TypeError: If months is not an integer
        ValueError: If the resulting date would be invalid
    """
    if not isinstance(date_obj, (datetime, date)):
        raise TypeError("date_obj must be a datetime or date object")

    if not isinstance(months, int) or isinstance(months, bool):
        raise TypeError("months must be an integer")

    # Calculate new year and month
    new_month = date_obj.month + months
    new_year = date_obj.year + (new_month - 1) // 12
    new_month = ((new_month - 1) % 12) + 1

    # Handle day overflow (e.g., Jan 31 + 1 month = Feb 28/29)
    try:
        if isinstance(date_obj, datetime):
            return date_obj.replace(year=new_year, month=new_month)
        else:
            return date_obj.replace(year=new_year, month=new_month)
    except ValueError:
        # Day doesn't exist in the new month (e.g., Feb 30)
        # Move to the last day of the new month
        last_day = monthrange(new_year, new_month)[1]

        if isinstance(date_obj, datetime):
            return date_obj.replace(year=new_year, month=new_month, day=last_day)
        else:
            return date_obj.replace(year=new_year, month=new_month, day=last_day)
