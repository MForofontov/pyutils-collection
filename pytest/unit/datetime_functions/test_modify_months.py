from datetime import date, datetime

import pytest

try:
    import pytz
    from pyutils_collection.datetime_functions.modify_months import modify_months
    PYTZ_AVAILABLE = True
except ImportError:
    PYTZ_AVAILABLE = False
    pytz = None  # type: ignore
    modify_months = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.datetime,
    pytest.mark.skipif(not PYTZ_AVAILABLE, reason="pytz not installed"),
]


def test_modify_months_add_to_date_object() -> None:
    """
    Test case 1: modify_months adds months to a date object.
    """
    test_date: date = date(2023, 1, 15)
    result: date = modify_months(test_date, 3)
    assert isinstance(result, date)
    assert result == date(2023, 4, 15)


def test_modify_months_add_with_year_overflow() -> None:
    """
    Test case 2: modify_months adds months with year overflow.
    """
    test_date: date = date(2023, 10, 15)
    result: date = modify_months(test_date, 6)
    assert isinstance(result, date)
    assert result == date(2024, 4, 15)


def test_modify_months_subtract_from_date_object() -> None:
    """
    Test case 3: modify_months subtracts months from a date object.
    """
    test_date: date = date(2023, 6, 15)
    result: date = modify_months(test_date, -3)
    assert isinstance(result, date)
    assert result == date(2023, 3, 15)


def test_modify_months_subtract_with_year_underflow() -> None:
    """
    Test case 4: modify_months subtracts months with year underflow.
    """
    test_date: date = date(2023, 2, 15)
    result: date = modify_months(test_date, -6)
    assert isinstance(result, date)
    assert result == date(2022, 8, 15)


def test_modify_months_day_overflow() -> None:
    """
    Test case 5: modify_months handles day overflow (e.g., Jan 31 to Feb 28).
    """
    test_date: date = date(2023, 1, 31)
    result: date = modify_months(test_date, 1)
    assert isinstance(result, date)
    assert result == date(2023, 2, 28)  # Feb 31 doesn't exist

    test_date2: date = date(2023, 3, 31)
    result2: date = modify_months(test_date2, -1)
    assert isinstance(result2, date)
    assert result2 == date(2023, 2, 28)


def test_modify_months_leap_year_handling() -> None:
    """
    Test case 6: modify_months handles leap year correctly (e.g., Jan 31 to Feb 29 in leap year).
    """
    test_date: date = date(2020, 1, 31)
    result: date = modify_months(test_date, 1)
    assert isinstance(result, date)
    assert result == date(2020, 2, 29)  # 2020 is leap year


def test_modify_months_datetime_object() -> None:
    """
    Test case 7: modify_months works with datetime objects and preserves time.
    """
    test_datetime: datetime = datetime(2023, 1, 15, 12, 30, 0)
    result: datetime = modify_months(test_datetime, 2)
    assert isinstance(result, datetime)
    assert result.date() == date(2023, 3, 15)
    assert result.time() == test_datetime.time()


def test_modify_months_zero_change() -> None:
    """
    Test case 8: modify_months returns the same date when months=0.
    """
    test_date: date = date(2023, 6, 15)
    result: date = modify_months(test_date, 0)
    assert isinstance(result, date)
    assert result == test_date


def test_modify_months_invalid_input_type() -> None:
    """
    Test case 9: modify_months raises TypeError for invalid input types.
    """
    with pytest.raises(TypeError):
        modify_months("2023-01-15", 3)

    with pytest.raises(TypeError):
        modify_months(123, 3)

    with pytest.raises(TypeError):
        modify_months(None, 3)


def test_modify_months_invalid_months_type() -> None:
    """
    Test case 10: modify_months raises TypeError for invalid months argument types.
    """
    test_date: date = date(2023, 1, 15)

    with pytest.raises(TypeError):
        modify_months(test_date, "3")

    with pytest.raises(TypeError):
        modify_months(test_date, 3.5)

    with pytest.raises(TypeError):
        modify_months(test_date, None)

    with pytest.raises(TypeError):
        modify_months(test_date, True)


def test_modify_months_datetime_day_overflow() -> None:
    """
    Test case 11: modify_months handles day overflow with datetime objects.
    """
    test_datetime: datetime = datetime(2023, 1, 31, 10, 30, 45)
    result = modify_months(test_datetime, 1)
    assert isinstance(result, datetime)
    assert result == datetime(2023, 2, 28, 10, 30, 45)  # Feb 31 doesn't exist
