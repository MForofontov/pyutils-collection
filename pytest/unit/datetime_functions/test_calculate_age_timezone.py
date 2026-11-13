"""Reference-clock behavior for naive and timezone-aware birth dates."""

import importlib
from datetime import datetime, timedelta, timezone, tzinfo

import pytest

from pyutils_collection.datetime_functions import calculate_age

pytestmark = [pytest.mark.unit, pytest.mark.datetime]


@pytest.mark.parametrize("zone", [None, timezone.utc, timezone(timedelta(hours=-8))])
def test_default_reference_uses_birth_timezone(
    monkeypatch: pytest.MonkeyPatch, zone: tzinfo | None
) -> None:
    module = importlib.import_module(
        "pyutils_collection.datetime_functions.calculate_age"
    )
    requested: list[tzinfo | None] = []

    class Clock(datetime):
        @classmethod
        def now(cls, tz: tzinfo | None = None) -> "Clock":
            requested.append(tz)
            return cls(2026, 1, 1, tzinfo=tz)

    birth = Clock(2000, 1, 1, tzinfo=zone)
    monkeypatch.setattr(module, "datetime", Clock)
    assert calculate_age(birth) == 26
    assert requested == [zone]


def test_explicit_reference_keeps_existing_calendar_behavior() -> None:
    zone = timezone(timedelta(hours=3))
    birth = datetime(2000, 6, 15, tzinfo=zone)
    assert calculate_age(birth, datetime(2026, 6, 14, tzinfo=zone)) == 25
    assert calculate_age(birth, datetime(2026, 6, 15, tzinfo=zone)) == 26
