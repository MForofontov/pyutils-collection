"""Tests for keyed deduplication."""

import pytest
from pyutils_collection.iterable_functions import unique_by

pytestmark = [pytest.mark.unit, pytest.mark.iterable_functions]


def test_first_occurrences_and_object_identity() -> None:
    first = {"id": 1, "value": "first"}
    other = {"id": 2}
    result = unique_by(iter([first, {"id": 1}, other]), lambda item: item["id"])
    assert result == [first, other]
    assert result[0] is first


def test_empty_input() -> None:
    assert unique_by([], str) == []


def test_key_called_once_per_item() -> None:
    visited = []

    def key(item):
        visited.append(item)
        return item.lower()

    assert unique_by(["A", "a", "B"], key) == ["A", "B"]
    assert visited == ["A", "a", "B"]


@pytest.mark.parametrize("items,key", [(None, str), ([], None), ([1], lambda _: [])])
def test_invalid_inputs(items, key) -> None:
    with pytest.raises(TypeError):
        unique_by(items, key)
