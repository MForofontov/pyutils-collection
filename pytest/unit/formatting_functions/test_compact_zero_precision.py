"""Integer digits must survive fractional-zero trimming."""

import pytest

from pyutils_collection.formatting_functions import format_number_compact

pytestmark = [pytest.mark.unit, pytest.mark.formatting]


@pytest.mark.parametrize(
    ("number", "expected"),
    [(10_000, "10K"), (100_000, "100K"), (-10_000, "-10K"),
     (10_000_000, "10M"), (999_999, "1000K")],
)
def test_integer_trailing_zeros_are_significant(number: int, expected: str) -> None:
    assert format_number_compact(number, precision=0) == expected
