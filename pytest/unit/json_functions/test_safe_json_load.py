import pytest

pytestmark = [pytest.mark.unit, pytest.mark.json_functions]
import json

from pyutils_collection.json_functions.safe_json_load import safe_json_load


def test_safe_json_load_valid() -> None:

    """
    Test case 1: Valid JSON string should load as dict.
    """
    data = '{"a": 1, "b": 2}'
    result = safe_json_load(data)
    assert result == {"a": 1, "b": 2}


def test_safe_json_load_invalid() -> None:

    """
    Test case 2: Invalid JSON string returns default value.
    """
    data = "{a: 1, b: 2}"
    result = safe_json_load(data, default={"error": True})
    assert result == {"error": True}


def test_safe_json_load_empty() -> None:

    """
    Test case 3: Empty string returns None (default).
    """
    result = safe_json_load("", default=None)
    assert result is None


def test_safe_json_load_object_hook() -> None:

    """
    Test case 4: Custom object_hook is used for decoding.
    """
    data = '{"a": 1, "b": 2}'

    def hook(d):
        d["sum"] = d["a"] + d["b"]
        return d

    result = safe_json_load(data, object_hook=hook)
    assert result["sum"] == 3


def test_safe_json_load_custom_decoder() -> None:

    """
    Test case 5: Custom decoder class is used.
    """

    class MyDecoder(json.JSONDecoder):
        def decode(self, s):
            obj = super().decode(s)
            obj["custom"] = True
            return obj

    data = '{"a": 1}'
    result = safe_json_load(data, decoder=MyDecoder)
    assert result["custom"] is True


def test_safe_json_load_type_error_input() -> None:

    """
    Test case 6: Non-string input triggers TypeError and returns the default value.
    """
    data = {"a": 1}
    default_value = {"error": "type"}

    result = safe_json_load(data, default=default_value)

    assert result == default_value
