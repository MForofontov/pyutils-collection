"""
Mock datetime fixture that freezes time.
"""

from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from unittest.mock import patch


@contextmanager
def mock_datetime_fixture(
    year: int = 2025,
    month: int = 1,
    day: int = 1,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
) -> Generator[datetime]:
    """
    Create a mock datetime fixture that freezes time.

    Parameters
    ----------
    year : int, optional
        Year (by default 2025).
    month : int, optional
        Month (by default 1).
    day : int, optional
        Day (by default 1).
    hour : int, optional
        Hour (by default 0).
    minute : int, optional
        Minute (by default 0).
    second : int, optional
        Second (by default 0).

    Yields
    ------
    datetime
        Fixed datetime object.

    Raises
    ------
    TypeError
        If parameters are of wrong type.

    Examples
    --------
    >>> with mock_datetime_fixture(2025, 12, 11) as mock_dt:
    ...     print(mock_dt.year)
    2025

    Notes
    -----
    datetime.now() will return the mocked time during the context.

    Complexity
    ----------
    Time: O(1), Space: O(1)
    """
    if not isinstance(year, int):
        raise TypeError(f"year must be an integer, got {type(year).__name__}")
    if not isinstance(month, int):
        raise TypeError(f"month must be an integer, got {type(month).__name__}")
    if not isinstance(day, int):
        raise TypeError(f"day must be an integer, got {type(day).__name__}")
    if not isinstance(hour, int):
        raise TypeError(f"hour must be an integer, got {type(hour).__name__}")
    if not isinstance(minute, int):
        raise TypeError(f"minute must be an integer, got {type(minute).__name__}")
    if not isinstance(second, int):
        raise TypeError(f"second must be an integer, got {type(second).__name__}")

    mock_dt = datetime(year, month, day, hour, minute, second)

    with patch("datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_dt
        mock_datetime.utcnow.return_value = mock_dt
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        yield mock_dt


__all__ = ["mock_datetime_fixture"]
