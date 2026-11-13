"""Overflow follows each conversion helper's documented failure contract."""

import pytest

from pyutils_collection.iterable_functions.type_operations.safe_cast import safe_cast
from pyutils_collection.iterable_functions.type_operations.try_convert_to_type import (
    try_convert_to_type,
)

pytestmark = [pytest.mark.unit, pytest.mark.iterable_functions]
CASES = [
    (float("inf"), int),
    (-float("inf"), int),
    (10**400, float),
    (float("nan"), int),
]


@pytest.mark.parametrize("value,target", CASES)
@pytest.mark.parametrize("use_default", [False, True])
def test_safe_cast_overflow_uses_fallback(value, target, use_default):
    default = object() if use_default else None
    assert safe_cast(value, target, default) is (default if use_default else value)


@pytest.mark.parametrize("value,target", CASES)
def test_strict_conversion_preserves_numeric_error_cause(value, target):
    with pytest.raises(ValueError, match="Failed to convert") as caught:
        try_convert_to_type(value, target)
    assert isinstance(caught.value.__cause__, (OverflowError, ValueError))


@pytest.mark.parametrize("convert", [safe_cast, try_convert_to_type])
def test_unrelated_converter_errors_are_not_suppressed(convert):
    error = RuntimeError("converter failed")

    class Converter:
        def __init__(self, value):
            raise error

    with pytest.raises(RuntimeError) as caught:
        convert("input", Converter)
    assert caught.value is error
