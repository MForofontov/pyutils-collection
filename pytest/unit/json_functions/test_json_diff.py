import pytest

pytestmark = [pytest.mark.unit, pytest.mark.json_functions]
from pyutils_collection.json_functions.json_diff import json_diff


def test_json_diff_dictionary_order_is_stable() -> None:
    a = {"z": 1, "nested": {"b": 1, "a": 1}, "removed": 3}
    b = {"new2": 4, "nested": {"a": 2, "b": 2, "new": 5}, "z": 2, "new1": 6}
    assert json_diff(a, b) == [
        ("z", 1, 2), ("nested.b", 1, 2), ("nested.a", 1, 2),
        ("nested.new", None, 5), ("removed", 3, None),
        ("new2", None, 4), ("new1", None, 6),
    ]


def test_json_diff_dicts() -> None:
    """Test case 1: Test json_diff with dictionary differences."""
    a = {"a": 1, "b": 2}
    b = {"a": 1, "b": 3, "c": 4}
    result = json_diff(a, b)
    assert ("b", 2, 3) in result or ("b", 2, 3) in [
        (p.split(".")[-1], av, bv) for p, av, bv in result
    ]
    assert ("c", None, 4) in result or ("c", None, 4) in [
        (p.split(".")[-1], av, bv) for p, av, bv in result
    ]


def test_json_diff_lists() -> None:
    """Test case 2: Test json_diff with list differences."""
    a = [1, 2, 3]
    b = [1, 4]
    result = json_diff(a, b)
    assert ("[1]", 2, 4) in result
    assert ("[2]", 3, None) in result


def test_json_diff_nested() -> None:
    """Test case 3: Test json_diff with nested structure differences."""
    a = {"a": {"x": 1, "y": 2}, "b": [1, 2]}
    b = {"a": {"x": 1, "y": 3}, "b": [1, 2, 3]}
    result = json_diff(a, b)
    assert any("a.y" in p and av == 2 and bv == 3 for p, av, bv in result)
    assert any("b[2]" in p and av is None and bv == 3 for p, av, bv in result)


def test_json_diff_type_change() -> None:
    """Test case 4: Test json_diff with type changes."""
    a = {"a": 1}
    b = [1]
    result = json_diff(a, b)
    assert ("", {"a": 1}, [1]) in result


def test_json_diff_list_length_difference() -> None:
    """Test case 5: Test json_diff with lists of different lengths."""
    a = [1, 2, 3, 4, 5]
    b = [1, 2]
    result = json_diff(a, b)
    # Should have differences for indices 2, 3, 4
    assert ("[2]", 3, None) in result
    assert ("[3]", 4, None) in result
    assert ("[4]", 5, None) in result


def test_json_diff_second_list_longer() -> None:
    """Test case 6: Ensure json_diff captures additions when the second list is longer."""
    a = ["alpha", "beta"]
    b = ["alpha", "beta", "gamma", "delta"]
    result = json_diff(a, b)

    assert ("[2]", None, "gamma") in result
    assert ("[3]", None, "delta") in result
