"""Tests for nested dictionary deletion."""

import pytest
from pyutils_collection.iterable_functions import deep_delete

pytestmark = [pytest.mark.unit, pytest.mark.iterable_functions]


def test_delete_keeps_empty_parent_and_siblings() -> None:
    data = {"user": {"name": "Ada"}, "other": 1}
    assert deep_delete(data, "user.name") is None
    assert data == {"user": {}, "other": 1}


def test_explicit_keys_support_dots_and_empty_keys() -> None:
    data = {"a.b": {"": 1}}
    keys = ["a.b", ""]
    deep_delete(data, keys)
    assert data == {"a.b": {}}
    assert keys == ["a.b", ""]


@pytest.mark.parametrize("keys", ["missing", "a.missing", "scalar.child"])
def test_missing_paths(keys) -> None:
    data = {"a": {}, "scalar": 1}
    with pytest.raises(KeyError):
        deep_delete(data, keys)
    deep_delete(data, keys, missing_ok=True)
    assert data == {"a": {}, "scalar": 1}


@pytest.mark.parametrize(
    "data,keys,missing_ok,error",
    [
        ([], "a", False, TypeError),
        ({}, None, False, TypeError),
        ({}, ["a", 1], False, TypeError),
        ({}, [], False, ValueError),
        ({}, "a", 1, TypeError),
    ],
)
def test_invalid_inputs(data, keys, missing_ok, error) -> None:
    with pytest.raises(error):
        deep_delete(data, keys, missing_ok)
