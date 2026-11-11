from typing import Any

import pytest


@pytest.mark.parametrize("keys", [["new", 1], ["new", []], [None]])
def test_deep_set_rejects_invalid_keys_without_mutation(keys) -> None:
    data = {"existing": 1}
    with pytest.raises(TypeError, match="keys must be a string or a list of strings"):
        deep_set(data, keys, 2)
    assert data == {"existing": 1}


pytestmark = [pytest.mark.unit, pytest.mark.iterable_functions]
from pyutils_collection.iterable_functions.dictionary_operations.deep_set import (
    deep_set,
)


def test_deep_set_basic_functionality() -> None:
    """
    Test case 1: Normal operation with basic deep set functionality.
    """
    # Arrange
    input_data: dict[str, Any] = {"user": {}}
    key_path: str = "user.name"
    value: str = "John"
    expected_output: dict[str, Any] = {"user": {"name": "John"}}

    # Act
    deep_set(input_data, key_path, value)

    # Assert
    assert input_data == expected_output


def test_deep_set_list_of_keys() -> None:
    """
    Test case 2: Normal operation with list of keys.
    """
    # Arrange
    input_data: dict[str, Any] = {}
    key_path: list[str] = ["user", "profile", "settings", "theme"]
    value: str = "dark"
    expected_output: dict[str, Any] = {
        "user": {"profile": {"settings": {"theme": "dark"}}}
    }

    # Act
    deep_set(input_data, key_path, value)

    # Assert
    assert input_data == expected_output


def test_deep_set_existing_nested_structure() -> None:
    """
    Test case 3: Normal operation on existing nested structure.
    """
    # Arrange
    input_data: dict[str, Any] = {"user": {"name": "John"}}
    key_path: str = "user.profile.age"
    value: int = 30
    expected_output: dict[str, Any] = {"user": {"name": "John", "profile": {"age": 30}}}

    # Act
    deep_set(input_data, key_path, value)

    # Assert
    assert input_data == expected_output


def test_deep_set_overwrite_existing_value() -> None:
    """
    Test case 4: Normal operation overwriting existing value.
    """
    # Arrange
    input_data: dict[str, Any] = {"user": {"name": "John"}}
    key_path: str = "user.name"
    value: str = "Jane"
    expected_output: dict[str, Any] = {"user": {"name": "Jane"}}

    # Act
    deep_set(input_data, key_path, value)

    # Assert
    assert input_data == expected_output


def test_deep_set_root_level_key() -> None:
    """
    Test case 5: Normal operation with root level key.
    """
    # Arrange
    input_data: dict[str, Any] = {}
    key_path: str = "name"
    value: str = "John"
    expected_output: dict[str, Any] = {"name": "John"}

    # Act
    deep_set(input_data, key_path, value)

    # Assert
    assert input_data == expected_output


def test_deep_set_deeply_nested_structure() -> None:
    """
    Test case 6: Normal operation with deeply nested structure.
    """
    # Arrange
    input_data: dict[str, Any] = {}
    key_path: str = "level1.level2.level3.level4"
    value: str = "value"
    expected_output: dict[str, Any] = {
        "level1": {"level2": {"level3": {"level4": "value"}}}
    }

    # Act
    deep_set(input_data, key_path, value)

    # Assert
    assert input_data == expected_output


def test_deep_set_mixed_data_types() -> None:
    """
    Test case 7: Normal operation with mixed data types.
    """
    # Arrange
    input_data: dict[str, Any] = {}
    expected_output: dict[str, Any] = {
        "data": {"list": [1, 2, 3], "number": 42, "string": "hello"}
    }

    # Act
    deep_set(input_data, "data.list", [1, 2, 3])
    deep_set(input_data, "data.number", 42)
    deep_set(input_data, "data.string", "hello")

    # Assert
    assert input_data == expected_output


def test_deep_set_empty_string_in_path() -> None:
    """
    Test case 8: Edge case with empty string in path.
    """
    # Arrange
    input_data: dict[str, Any] = {}
    key_path: str = ".nested"
    value: str = "value"
    expected_output: dict[str, Any] = {"": {"nested": "value"}}

    # Act
    deep_set(input_data, key_path, value)

    # Assert
    assert input_data == expected_output


def test_deep_set_single_key() -> None:
    """
    Test case 9: Edge case with single key.
    """
    # Arrange
    input_data: dict[str, Any] = {}
    key_path: str = "key"
    value: str = "value"
    expected_output: dict[str, Any] = {"key": "value"}

    # Act
    deep_set(input_data, key_path, value)

    # Assert
    assert input_data == expected_output


def test_deep_set_numeric_keys_in_path() -> None:
    """
    Test case 10: Normal operation with numeric keys in path.
    """
    # Arrange
    input_data: dict[str, Any] = {}
    key_path: str = "users.0.name"
    value: str = "John"
    expected_output: dict[str, Any] = {"users": {"0": {"name": "John"}}}

    # Act
    deep_set(input_data, key_path, value)

    # Assert
    assert input_data == expected_output


def test_deep_set_invalid_type_error() -> None:
    """
    Test case 11: TypeError for invalid input type.
    """
    # Arrange
    invalid_input: str = "not a dict"
    key_path: str = "key"
    value: str = "value"
    expected_message: str = "d must be a dictionary, got str"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        deep_set(invalid_input, key_path, value)


def test_deep_set_empty_key_path_list() -> None:
    """Test case 12: ValueError when key path list is empty."""

    input_data: dict[str, Any] = {}

    with pytest.raises(ValueError, match="keys must contain at least one key"):
        deep_set(input_data, [], "value")
