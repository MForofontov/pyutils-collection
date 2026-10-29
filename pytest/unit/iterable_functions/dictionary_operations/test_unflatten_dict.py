"""Tests for reconstructing flattened dictionaries."""

import pytest
from pyutils_collection.iterable_functions import flatten_dict, unflatten_dict

pytestmark = [pytest.mark.unit, pytest.mark.iterable_functions]


def test_round_trip() -> None:
    source = {"user": {"name": "Ada", "profile": {"age": 36}}, "tags": [1, 2]}
    assert unflatten_dict(flatten_dict(source)) == source


def test_multichar_separator_and_empty_components() -> None:
    assert unflatten_dict({"user::name": "Ada", "::value": 2}, "::") == {
        "user": {"name": "Ada"},
        "": {"value": 2},
    }


def test_empty_and_shared_leaves() -> None:
    assert unflatten_dict({}) == {}
    value = {"x": []}
    result = unflatten_dict({"a_b": value})
    assert result["a"]["b"] is value


@pytest.mark.parametrize(
    "data",
    [
        {"a": 1, "a_b": 2},
        {"a_b": 2, "a": 1},
        {"a": {}, "a_b": 2},
        {"a_b": 2, "a": {}},
    ],
)
def test_conflicts_do_not_modify_input(data) -> None:
    from copy import deepcopy

    before = deepcopy(data)
    with pytest.raises(ValueError, match="Conflicting"):
        unflatten_dict(data)
    assert data == before


@pytest.mark.parametrize(
    "data,separator,error",
    [
        ([], "_", TypeError),
        ({1: 2}, "_", TypeError),
        ({}, None, TypeError),
        ({}, "", ValueError),
    ],
)
def test_invalid_inputs(data, separator, error) -> None:
    with pytest.raises(error):
        unflatten_dict(data, separator)
