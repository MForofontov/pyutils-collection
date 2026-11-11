"""Real-valued exponentiation and documented arithmetic failures."""

import pytest
from pyutils_collection.mathematical_functions import power

pytestmark = [pytest.mark.unit, pytest.mark.mathematical_functions]


@pytest.mark.parametrize(
    ("base", "exponent", "cause"),
    [
        (-4, 0.5, None),
        (0, -1, ZeroDivisionError),
        (0.0, -0.5, ZeroDivisionError),
        (1e200, 2, OverflowError),
        (-1e200, 3, OverflowError),
    ],
)
def test_invalid_real_power_raises_value_error(
    base: int | float, exponent: int | float, cause: type[Exception] | None
) -> None:
    with pytest.raises(ValueError) as caught:
        power(base, exponent)
    if cause is not None:
        assert isinstance(caught.value.__cause__, cause)


@pytest.mark.parametrize(
    ("base", "exponent", "expected"),
    [
        (2, 100, 2**100),
        (10, -1, 0.1),
        (-4, 2.0, 16.0),
        (-2, -3, -0.125),
        (0, 0, 1),
        (0.0, 0.0, 1.0),
        (-2, 3, -8),
    ],
)
def test_valid_power_preserves_value_and_type(
    base: int | float, exponent: int | float, expected: int | float
) -> None:
    result = power(base, exponent)
    assert result == expected
    assert type(result) is type(expected)
