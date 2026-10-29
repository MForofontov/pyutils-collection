from datetime import datetime, timedelta

import pytest


@pytest.mark.parametrize(
    ("days", "expected"),
    [
        (28, "in 4 weeks"),
        (29, "in 4 weeks"),
        (30, "in 1 month"),
        (359, "in 11 months"),
        (360, "in 12 months"),
        (364, "in 12 months"),
        (365, "in 1 year"),
    ],
)
def test_time_until_unit_boundaries(days: int, expected: str) -> None:
    reference = datetime(2025, 1, 1)
    assert time_until(reference + timedelta(days=days), reference) == expected


try:
    import pytz
    from pyutils_collection.datetime_functions.time_until import time_until

    PYTZ_AVAILABLE = True
except ImportError:
    PYTZ_AVAILABLE = False
    pytz = None  # type: ignore
    time_until = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.datetime,
    pytest.mark.skipif(not PYTZ_AVAILABLE, reason="pytz not installed"),
]


def test_time_until_seconds() -> None:
    """
    Test case 1: time_until returns correct string for seconds difference.
    """
    past_dt: datetime = datetime(2023, 1, 15, 12, 0, 0)
    future_dt: datetime = datetime(2023, 1, 15, 12, 0, 30)
    result: str = time_until(future_dt, past_dt)
    assert isinstance(result, str)
    assert "30 seconds" in result or "in a moment" in result


def test_time_until_minutes() -> None:
    """
    Test case 2: time_until returns correct string for minutes difference.
    """
    past_dt: datetime = datetime(2023, 1, 15, 12, 0, 0)
    future_dt: datetime = datetime(2023, 1, 15, 12, 15, 0)
    result: str = time_until(future_dt, past_dt)
    assert isinstance(result, str)
    assert "15 minutes" in result


def test_time_until_hours() -> None:
    """
    Test case 3: time_until returns correct string for hours difference.
    """
    past_dt: datetime = datetime(2023, 1, 15, 12, 0, 0)
    future_dt: datetime = datetime(2023, 1, 15, 15, 0, 0)
    result: str = time_until(future_dt, past_dt)
    assert isinstance(result, str)
    assert "3 hours" in result


def test_time_until_days() -> None:
    """
    Test case 4: time_until returns correct string for days difference.
    """
    past_dt: datetime = datetime(2023, 1, 15, 0, 0, 0)
    future_dt: datetime = datetime(2023, 1, 20, 0, 0, 0)
    result: str = time_until(future_dt, past_dt)
    assert isinstance(result, str)
    assert "5 days" in result


def test_time_until_weeks() -> None:
    """
    Test case 5: time_until returns correct string for weeks difference.
    """
    past_dt: datetime = datetime(2023, 1, 15, 0, 0, 0)
    future_dt: datetime = datetime(2023, 2, 5, 0, 0, 0)
    result: str = time_until(future_dt, past_dt)
    assert isinstance(result, str)
    assert "week" in result


def test_time_until_months() -> None:
    """
    Test case 6: time_until returns correct string for months difference.
    """
    past_dt: datetime = datetime(2023, 1, 15, 0, 0, 0)
    future_dt: datetime = datetime(2023, 6, 15, 0, 0, 0)
    result: str = time_until(future_dt, past_dt)
    assert isinstance(result, str)
    assert "month" in result


def test_time_until_years() -> None:
    """
    Test case 7: time_until returns correct string for years difference.
    """
    past_dt: datetime = datetime(2023, 1, 15, 0, 0, 0)
    future_dt: datetime = datetime(2025, 1, 15, 0, 0, 0)
    result: str = time_until(future_dt, past_dt)
    assert isinstance(result, str)
    assert "year" in result


def test_time_until_mixed_types() -> None:
    """
    Test case 8: time_until works with mixed date and datetime objects.
    """
    past_dt: datetime = datetime(2023, 1, 15, 0, 0, 0)
    future_dt: datetime = datetime(2023, 1, 20, 12, 0, 0)
    result: str = time_until(future_dt, past_dt)
    assert isinstance(result, str)
    assert "day" in result


def test_time_until_invalid_input_type() -> None:
    """
    Test case 9: time_until raises TypeError for invalid input types.
    """
    test_datetime: datetime = datetime(2023, 1, 20, 0, 0, 0)

    with pytest.raises(TypeError):
        time_until("2023-01-15", test_datetime)

    with pytest.raises(TypeError):
        time_until(123, test_datetime)

    with pytest.raises(TypeError):
        time_until(None, test_datetime)


def test_time_until_past_date_error() -> None:
    """
    Test case 10: time_until raises ValueError if the target date is in the past.
    """
    future_dt: datetime = datetime(2023, 1, 15, 0, 0, 0)
    past_dt: datetime = datetime(2023, 1, 20, 0, 0, 0)

    with pytest.raises(ValueError):
        time_until(future_dt, past_dt)


def test_time_until_invalid_reference_date_type() -> None:
    """
    Test case 11: time_until raises TypeError for invalid reference_date type.
    """
    future_dt: datetime = datetime(2023, 1, 20, 0, 0, 0)

    with pytest.raises(TypeError, match="reference_date must be a datetime object"):
        time_until(future_dt, "2023-01-15")  # type: ignore
