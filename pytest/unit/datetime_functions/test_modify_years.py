from datetime import date, datetime

import pytest

try:
    import pytz
    from pyutils_collection.datetime_functions.modify_years import modify_years
    PYTZ_AVAILABLE = True
except ImportError:
    PYTZ_AVAILABLE = False
    pytz = None  # type: ignore
    modify_years = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.datetime,
    pytest.mark.skipif(not PYTZ_AVAILABLE, reason="pytz not installed"),
]


def test_modify_years_add_to_date_object() -> None:
    """
    Test case 1: Test modify_years function adding years to date object.
    """
    test_date: date = date(2023, 1, 15)
    result: date = modify_years(test_date, 2)
    assert isinstance(result, date)
    assert result == date(2025, 1, 15)


def test_modify_years_add_to_datetime_object() -> None:
    """
    Test case 2: Test modify_years function adding years to datetime object.
    """
    test_datetime: datetime = datetime(2023, 1, 15, 12, 30, 0)
    result: datetime = modify_years(test_datetime, 3)
    assert isinstance(result, datetime)
    assert result.date() == date(2026, 1, 15)
    assert result.time() == test_datetime.time()


def test_modify_years_subtract_from_date_object() -> None:
    """
    Test case 3: Test modify_years function subtracting years from date object.
    """
    test_date: date = date(2023, 1, 15)
    result: date = modify_years(test_date, -3)
    assert isinstance(result, date)
    assert result == date(2020, 1, 15)


def test_modify_years_subtract_from_datetime_object() -> None:
    """
    Test case 4: Test modify_years function subtracting years from datetime object.
    """
    test_datetime: datetime = datetime(2023, 6, 15, 12, 30, 0)
    result: datetime = modify_years(test_datetime, -2)
    assert isinstance(result, datetime)
    assert result.date() == date(2021, 6, 15)
    assert result.time() == test_datetime.time()


def test_modify_years_zero_change() -> None:
    """
    Test case 5: Test modify_years function with zero years.
    """
    test_date: date = date(2023, 1, 15)
    result: date = modify_years(test_date, 0)
    assert isinstance(result, date)
    assert result == test_date


def test_modify_years_leap_year_handling_add() -> None:
    """
    Test case 6: Test modify_years function with leap year Feb 29 handling when adding.
    """
    test_date: date = date(2020, 2, 29)  # 2020 is leap year
    result: date = modify_years(test_date, 1)
    assert isinstance(result, date)
    assert result == date(2021, 2, 28)  # 2021 is not leap year


def test_modify_years_leap_year_handling_subtract() -> None:
    """
    Test case 7: Test modify_years function with leap year Feb 29 handling when subtracting.
    """
    test_date: date = date(2020, 2, 29)  # 2020 is leap year
    result: date = modify_years(test_date, -1)
    assert isinstance(result, date)
    assert result == date(2019, 2, 28)  # 2019 is not leap year


def test_modify_years_leap_to_leap() -> None:
    """
    Test case 8: Test modify_years function from leap year to leap year.
    """
    test_date: date = date(2020, 2, 29)
    result_add: date = modify_years(test_date, 4)
    assert result_add == date(2024, 2, 29)  # 2024 is also leap year

    test_date2: date = date(2024, 2, 29)
    result_subtract: date = modify_years(test_date2, -4)
    assert result_subtract == date(2020, 2, 29)  # 2020 is also leap year


def test_modify_years_leap_year_datetime() -> None:
    """
    Test case 9: Test modify_years with datetime object on Feb 29 leap year.
    """
    test_datetime: datetime = datetime(2020, 2, 29, 15, 30, 45)
    result = modify_years(test_datetime, 1)
    assert isinstance(result, datetime)
    assert result == datetime(2021, 2, 28, 15, 30, 45)  # Feb 29 adjusted to Feb 28


def test_modify_years_leap_year_feb29_to_non_leap_datetime() -> None:
    """
    Test case 10: Test modify_years with datetime on Feb 29 to non-leap year (exception handling).
    """
    # Feb 29, 2020 (leap year) as datetime
    test_datetime = datetime(2020, 2, 29, 15, 30, 45)
    # Add 1 year to 2021 (non-leap year) - should adjust to Feb 28
    result = modify_years(test_datetime, 1)
    assert result.year == 2021
    assert result.month == 2
    assert result.day == 28
    assert result.hour == 15
    assert result.minute == 30
    assert result.second == 45


def test_modify_years_invalid_input_type() -> None:
    """
    Test case 11: Test modify_years function with invalid input type raises TypeError.
    """
    with pytest.raises(TypeError):
        modify_years("2023-01-15", 2)

    with pytest.raises(TypeError):
        modify_years(123, 2)

    with pytest.raises(TypeError):
        modify_years(None, 2)


def test_modify_years_invalid_years_type() -> None:
    """
    Test case 12: Test modify_years function with invalid years type raises TypeError.
    """
    test_date: date = date(2023, 1, 15)

    with pytest.raises(TypeError):
        modify_years(test_date, "2")

    with pytest.raises(TypeError):
        modify_years(test_date, 2.5)

    with pytest.raises(TypeError):
        modify_years(test_date, None)

    with pytest.raises(TypeError):
        modify_years(test_date, True)
