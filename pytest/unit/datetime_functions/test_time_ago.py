from datetime import datetime, timedelta

import pytest


@pytest.mark.parametrize(
    ("days", "expected"),
    [
        (28, "4 weeks ago"),
        (29, "4 weeks ago"),
        (30, "1 month ago"),
        (359, "11 months ago"),
        (360, "12 months ago"),
        (364, "12 months ago"),
        (365, "1 year ago"),
    ],
)
def test_time_ago_unit_boundaries(days: int, expected: str) -> None:
    reference = datetime(2025, 1, 1)
    assert time_ago(reference - timedelta(days=days), reference) == expected


try:
    import pytz
    from pyutils_collection.datetime_functions.time_ago import time_ago

    PYTZ_AVAILABLE = True
except ImportError:
    PYTZ_AVAILABLE = False
    pytz = None  # type: ignore
    time_ago = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.datetime,
    pytest.mark.skipif(not PYTZ_AVAILABLE, reason="pytz not installed"),
]


def test_time_ago_seconds() -> None:
    """
    Test case 1: time_ago returns correct string for seconds difference.
    """
    reference = datetime(2023, 1, 15, 12, 0, 30)
    past = datetime(2023, 1, 15, 12, 0, 0)
    result = time_ago(past, reference)
    assert isinstance(result, str)
    assert result == "30 seconds ago"


def test_time_ago_minutes() -> None:
    """
    Test case 2: time_ago returns correct string for minutes difference.
    """
    reference = datetime(2023, 1, 15, 12, 30, 0)
    past = datetime(2023, 1, 15, 12, 0, 0)
    result = time_ago(past, reference)
    assert isinstance(result, str)
    assert result == "30 minutes ago"


def test_time_ago_hours() -> None:
    """
    Test case 3: time_ago returns correct string for hours difference.
    """
    reference = datetime(2023, 1, 15, 15, 0, 0)
    past = datetime(2023, 1, 15, 12, 0, 0)
    result = time_ago(past, reference)
    assert isinstance(result, str)
    assert result == "3 hours ago"


def test_time_ago_days() -> None:
    """
    Test case 4: time_ago returns correct string for days difference.
    """
    reference = datetime(2023, 1, 18, 0, 0, 0)
    past = datetime(2023, 1, 15, 0, 0, 0)
    result = time_ago(past, reference)
    assert isinstance(result, str)
    assert result == "3 days ago"


def test_time_ago_weeks() -> None:
    """
    Test case 5: time_ago returns correct string for weeks difference.
    """
    reference = datetime(2023, 2, 5, 0, 0, 0)
    past = datetime(2023, 1, 15, 0, 0, 0)
    result = time_ago(past, reference)
    assert isinstance(result, str)
    assert result == "3 weeks ago"


def test_time_ago_just_now() -> None:
    """
    Test case 6: time_ago returns 'just now' for very recent times.
    """
    reference = datetime(2023, 1, 15, 12, 0, 5)
    past = datetime(2023, 1, 15, 12, 0, 0)
    result = time_ago(past, reference)
    assert isinstance(result, str)
    assert result == "just now"


def test_time_ago_future_value_error() -> None:
    """
    Test case 7: time_ago raises ValueError if the first argument is in the future relative to reference.
    """
    reference = datetime(2023, 1, 15, 12, 0, 0)
    future = datetime(2023, 1, 15, 13, 0, 0)
    with pytest.raises(ValueError):
        time_ago(future, reference)


def test_time_ago_invalid_type() -> None:
    """
    Test case 8: time_ago raises TypeError for invalid input types.
    """
    with pytest.raises(TypeError):
        time_ago("2023-01-15")
    with pytest.raises(TypeError):
        time_ago(123)
    with pytest.raises(TypeError):
        time_ago(None)
