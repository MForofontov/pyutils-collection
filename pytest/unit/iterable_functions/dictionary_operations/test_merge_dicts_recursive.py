from typing import Any

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.iterable_functions]
from pyutils_collection.iterable_functions.dictionary_operations.merge_dicts_recursive import (
    merge_dicts_recursive,
)


def test_merge_dicts_recursive_success() -> None:
    """
    Test case 1: Test the merge_dicts_recursive function with basic dictionary merging.
    """
    dict1: dict[str, Any] = {"a": 1, "b": 2}
    dict2: dict[str, Any] = {"c": 3, "d": 4}
    expected_output: dict[str, Any] = {"a": 1, "b": 2, "c": 3, "d": 4}
    assert merge_dicts_recursive(dict1, dict2) == expected_output


def test_merge_dicts_recursive_overlapping_keys() -> None:
    """
    Test case 2: Test the merge_dicts_recursive function with overlapping keys.
    """
    dict1: dict[str, Any] = {"a": 1, "b": 2}
    dict2: dict[str, Any] = {"b": 3, "c": 4}
    expected_output: dict[str, Any] = {"a": 1, "b": 3, "c": 4}
    assert merge_dicts_recursive(dict1, dict2) == expected_output


def test_merge_dicts_recursive_nested() -> None:
    """
    Test case 3: Test the merge_dicts_recursive function with nested dictionaries.
    """
    dict1: dict[str, Any] = {"a": {"x": 1, "y": 2}}
    dict2: dict[str, Any] = {"a": {"y": 3, "z": 4}, "b": 5}
    expected_output: dict[str, Any] = {"a": {"x": 1, "y": 3, "z": 4}, "b": 5}
    assert merge_dicts_recursive(dict1, dict2) == expected_output


def test_merge_dicts_recursive_multiple() -> None:
    """
    Test case 4: Test the merge_dicts_recursive function with multiple dictionaries.
    """
    dict1: dict[str, Any] = {"a": 1}
    dict2: dict[str, Any] = {"b": 2}
    dict3: dict[str, Any] = {"c": 3}
    expected_output: dict[str, Any] = {"a": 1, "b": 2, "c": 3}
    assert merge_dicts_recursive(dict1, dict2, dict3) == expected_output


def test_merge_dicts_recursive_empty() -> None:
    """
    Test case 5: Test the merge_dicts_recursive function with empty dictionaries.
    """
    dict1: dict[str, Any] = {"a": 1}
    dict2: dict[str, Any] = {}
    expected_output: dict[str, Any] = {"a": 1}
    assert merge_dicts_recursive(dict1, dict2) == expected_output


def test_merge_dicts_recursive_deeply_nested() -> None:
    """
    Test case 6: Test the merge_dicts_recursive function with deeply nested dictionaries.
    """
    dict1: dict[str, Any] = {"a": {"b": {"c": 1}}}
    dict2: dict[str, Any] = {"a": {"b": {"d": 2}}}
    expected_output: dict[str, Any] = {"a": {"b": {"c": 1, "d": 2}}}
    assert merge_dicts_recursive(dict1, dict2) == expected_output


def test_merge_dicts_recursive_single_dict() -> None:
    """
    Test case 7: Test the merge_dicts_recursive function with a single dictionary.
    """
    dict1: dict[str, Any] = {"a": 1, "b": 2}
    expected_output: dict[str, Any] = {"a": 1, "b": 2}
    assert merge_dicts_recursive(dict1) == expected_output


def test_merge_dicts_recursive_no_modification() -> None:
    """
    Test case 8: Test that original dictionaries are not modified.
    """
    dict1: dict[str, Any] = {"a": {"x": 1}}
    dict2: dict[str, Any] = {"a": {"y": 2}}
    original_dict1: dict[str, Any] = dict1.copy()
    original_dict2: dict[str, Any] = dict2.copy()

    merge_dicts_recursive(dict1, dict2)

    assert dict1 == original_dict1
    assert dict2 == original_dict2


def test_merge_dicts_recursive_does_not_alias_nested_mutables() -> None:
    """Merged nested lists are independent from source dictionaries."""
    inner = {"c": [1]}
    merged = merge_dicts_recursive({"a": inner}, {"b": 2})
    inner["c"].append(2)
    assert merged == {"a": {"c": [1]}, "b": 2}


def test_merge_dicts_recursive_type_error() -> None:
    """
    Test case 9: Test the merge_dicts_recursive function with invalid type for arguments.
    """
    with pytest.raises(TypeError):
        merge_dicts_recursive({"a": 1}, "not a dict")
