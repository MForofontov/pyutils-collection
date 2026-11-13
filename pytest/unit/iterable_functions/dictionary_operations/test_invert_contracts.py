"""Ordering, independent buckets, and duplicate error preservation."""

import pytest

from pyutils_collection.iterable_functions.dictionary_operations.invert_dict import (
    invert_dict,
)

pytestmark = [pytest.mark.unit, pytest.mark.iterable_functions]


def test_duplicate_buckets_follow_first_seen_order() -> None:
    data = {"first": 2, "second": 1, "third": 2, "fourth": 3, "fifth": 1}
    result = invert_dict(data, allow_duplicates=True)
    assert list(result.items()) == [(2, ["first", "third"]), (1, ["second", "fifth"]), (3, ["fourth"])]
    result[2].append("new")
    assert result[1] == ["second", "fifth"]
    assert list(data.items()) == [("first", 2), ("second", 1), ("third", 2), ("fourth", 3), ("fifth", 1)]


def test_duplicate_error_order_is_preserved() -> None:
    data = {"a": 2, "b": 1, "c": 2, "d": 1, "e": 2}
    with pytest.raises(ValueError) as caught:
        invert_dict(data)
    assert str(caught.value) == "Duplicate values found: [2, 1]"


def test_unhashable_values_still_fail_without_mutating_input() -> None:
    data = {"a": [1]}
    with pytest.raises(TypeError):
        invert_dict(data, allow_duplicates=True)
    assert data == {"a": [1]}
