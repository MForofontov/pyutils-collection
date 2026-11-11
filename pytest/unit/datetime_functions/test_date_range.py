"""Tests for lazy date and datetime ranges."""

from datetime import date, datetime, timedelta, timezone
from itertools import islice

import pytest
from pyutils_collection.datetime_functions import date_range

pytestmark = [pytest.mark.unit, pytest.mark.datetime]


def test_dates_exclude_stop() -> None:
    assert list(date_range(date(2024, 2, 28), date(2024, 3, 2))) == [
        date(2024, 2, 28),
        date(2024, 2, 29),
        date(2024, 3, 1),
    ]


def test_descending_and_direction_mismatch() -> None:
    start, stop = date(2025, 1, 5), date(2025, 1, 1)
    assert list(date_range(start, stop, -2)) == [start, date(2025, 1, 3)]
    assert list(date_range(start, stop)) == []
    assert list(date_range(stop, start, -1)) == []
    assert list(date_range(start, start)) == []


def test_datetime_subday_step_preserves_timezone() -> None:
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    assert list(
        date_range(start, start + timedelta(hours=1), timedelta(minutes=20))
    ) == [
        start,
        start + timedelta(minutes=20),
        start + timedelta(minutes=40),
    ]


def test_lazy_and_safe_at_date_limits() -> None:
    assert list(islice(date_range(date.min, date.max), 2)) == [date.min, date(1, 1, 2)]
    assert list(date_range(date.max - timedelta(days=1), date.max, 2)) == [
        date.max - timedelta(days=1),
    ]
    assert list(date_range(date.min + timedelta(days=1), date.min, -2)) == [
        date.min + timedelta(days=1),
    ]


@pytest.mark.parametrize(
    "start,stop,step,error",
    [
        ("2025-01-01", date.today(), 1, TypeError),
        (date.today(), datetime.now(), 1, TypeError),
        (date.min, date.max, True, TypeError),
        (date.min, date.max, 1.5, TypeError),
        (date.min, date.max, 0, ValueError),
        (date.min, date.max, timedelta(hours=12), ValueError),
        (date.max, date.min, timedelta(hours=-12), ValueError),
        (
            datetime(2025, 1, 1),
            datetime(2025, 1, 2, tzinfo=timezone.utc),
            1,
            ValueError,
        ),
    ],
)
def test_invalid_ranges(start, stop, step, error) -> None:
    with pytest.raises(error):
        list(date_range(start, stop, step))
