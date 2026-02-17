import sys

import pytest

# Try to import cerberus - tests will be skipped if not available
try:
    from cerberus import Validator

    from pyutils_collection.data_validation import validate_cerberus_schema

    CERBERUS_AVAILABLE = True
except ImportError:
    CERBERUS_AVAILABLE = False
    Validator = None
    validate_cerberus_schema = None

pytestmark = pytest.mark.skipif(not CERBERUS_AVAILABLE, reason="Cerberus not installed")
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.data_validation]


def test_validate_cerberus_schema_simple_valid_data() -> None:
    """
    Test case 1: Simple valid data validation.
    """
    schema = {
        "name": {"type": "string", "required": True},
        "age": {"type": "integer", "min": 0, "max": 150},
        "email": {"type": "string"},
    }

    data = {"name": "John Doe", "age": 30, "email": "john@example.com"}
    result = validate_cerberus_schema(data, schema)

    assert result["name"] == "John Doe"
    assert result["age"] == 30
    assert result["email"] == "john@example.com"


def test_validate_cerberus_schema_with_defaults() -> None:
    """
    Test case 2: Schema with default values.
    """
    schema = {
        "name": {"type": "string", "required": True},
        "active": {"type": "boolean", "default": True},
        "tags": {"type": "list", "default": []},
        "score": {"type": "float", "default": 0.0},
    }

    data = {"name": "Jane Doe"}
    result = validate_cerberus_schema(data, schema, normalize=True)

    assert result["name"] == "Jane Doe"
    assert result["active"] is True
    assert result["tags"] == []
    assert result["score"] == 0.0


def test_validate_cerberus_schema_type_coercion() -> None:
    """
    Test case 3: Type coercion during validation.
    """
    schema = {
        "age": {"type": "integer", "coerce": int},
        "score": {"type": "float", "coerce": float},
        "active": {"type": "boolean", "coerce": bool},
    }

    data = {"age": "25", "score": "95.5", "active": "true"}
    result = validate_cerberus_schema(data, schema, normalize=True)

    assert result["age"] == 25
    assert result["score"] == 95.5
    assert result["active"] is True


def test_validate_cerberus_schema_nested_schemas() -> None:
    """
    Test case 4: Nested schema validation.
    """
    schema = {
        "user": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "age": {"type": "integer", "min": 0},
            },
        },
        "metadata": {"type": "dict", "default": {}},
    }

    data = {"user": {"name": "Alice", "age": 28}, "metadata": {"source": "api"}}

    result = validate_cerberus_schema(data, schema)

    assert result["user"]["name"] == "Alice"
    assert result["user"]["age"] == 28
    assert result["metadata"]["source"] == "api"


def test_validate_cerberus_schema_list_validation() -> None:
    """
    Test case 5: List schema validation.
    """
    schema = {
        "numbers": {"type": "list", "schema": {"type": "integer", "min": 0}},
        "tags": {"type": "list", "schema": {"type": "string", "maxlength": 20}},
    }

    data = {"numbers": [1, 2, 3, 4, 5], "tags": ["python", "validation", "test"]}

    result = validate_cerberus_schema(data, schema)

    assert result["numbers"] == [1, 2, 3, 4, 5]
    assert result["tags"] == ["python", "validation", "test"]


def test_validate_cerberus_schema_value_constraints() -> None:
    """
    Test case 6: Value constraint validation.
    """
    schema = {
        "name": {"type": "string", "minlength": 2, "maxlength": 50},
        "age": {"type": "integer", "min": 0, "max": 150},
        "email": {"type": "string", "regex": r"^[^@]+@[^@]+\.[^@]+$"},
        "status": {"type": "string", "allowed": ["active", "inactive", "pending"]},
    }

    data = {"name": "Bob", "age": 35, "email": "bob@example.com", "status": "active"}

    result = validate_cerberus_schema(data, schema)

    assert result["name"] == "Bob"
    assert result["age"] == 35
    assert result["email"] == "bob@example.com"
    assert result["status"] == "active"


def test_validate_cerberus_schema_allow_unknown_fields() -> None:
    """
    Test case 7: Allow unknown fields validation.
    """
    schema = {"name": {"type": "string", "required": True}, "age": {"type": "integer"}}

    data = {"name": "Charlie", "age": 40, "extra_field": "should be allowed"}

    result = validate_cerberus_schema(data, schema, allow_unknown=True)

    assert result["name"] == "Charlie"
    assert result["age"] == 40
    assert result["extra_field"] == "should be allowed"


def test_validate_cerberus_schema_without_normalization() -> None:
    """
    Test case 8: Validation without normalization.
    """
    schema = {
        "name": {"type": "string", "required": True},
        "count": {"type": "integer", "default": 0},
    }

    data = {"name": "David"}
    result = validate_cerberus_schema(data, schema, normalize=False)

    assert result["name"] == "David"
    assert "count" not in result  # Default not applied without normalization


def test_validate_cerberus_schema_edge_cases() -> None:
    """
    Test case 9: Edge cases and boundary conditions.
    """
    # Test empty schema
    result = validate_cerberus_schema({}, {})
    assert result == {}

    # Test empty data with optional schema
    schema = {"name": {"type": "string", "default": "Anonymous"}}
    result = validate_cerberus_schema({}, schema, normalize=True)
    assert result["name"] == "Anonymous"

    # Test boundary values
    schema = {"score": {"type": "integer", "min": 0, "max": 100}}

    # Test minimum boundary
    result = validate_cerberus_schema({"score": 0}, schema)
    assert result["score"] == 0

    # Test maximum boundary
    result = validate_cerberus_schema({"score": 100}, schema)
    assert result["score"] == 100


def test_validate_cerberus_schema_performance_large_data() -> None:
    """
    Test case 10: Performance with large data structures.
    """
    schema = {
        "items": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {"id": {"type": "integer"}, "name": {"type": "string"}},
            },
        }
    }

    # Create large dataset
    large_data = {"items": [{"id": i, "name": f"item_{i}"} for i in range(1000)]}

    import time

    start_time = time.time()
    result = validate_cerberus_schema(large_data, schema)
    elapsed_time = time.time() - start_time

    assert len(result["items"]) == 1000
    assert elapsed_time < 2.0  # Should complete within 2 seconds


def test_validate_cerberus_schema_type_error_invalid_data() -> None:
    """
    Test case 11: TypeError for invalid data type.
    """
    schema = {"name": {"type": "string"}}

    with pytest.raises(TypeError, match="data must be a dictionary, got list"):
        validate_cerberus_schema([1, 2, 3], schema)

    with pytest.raises(TypeError, match="data must be a dictionary, got str"):
        validate_cerberus_schema("not a dict", schema)

    # Test with custom param name
    with pytest.raises(TypeError, match="user_data must be a dictionary, got int"):
        validate_cerberus_schema(123, schema, param_name="user_data")


def test_validate_cerberus_schema_type_error_invalid_schema() -> None:
    """
    Test case 12: TypeError for invalid schema type.
    """
    data = {"name": "Test"}

    with pytest.raises(TypeError, match="schema must be a dictionary, got list"):
        validate_cerberus_schema(data, [1, 2, 3])

    with pytest.raises(TypeError, match="schema must be a dictionary, got str"):
        validate_cerberus_schema(data, "not a dict")


def test_validate_cerberus_schema_type_error_invalid_parameters() -> None:
    """
    Test case 13: TypeError for invalid parameter types.
    """
    data = {"name": "Test"}
    schema = {"name": {"type": "string"}}

    with pytest.raises(TypeError, match="allow_unknown must be bool, got str"):
        validate_cerberus_schema(data, schema, allow_unknown="true")

    with pytest.raises(TypeError, match="normalize must be bool, got int"):
        validate_cerberus_schema(data, schema, normalize=1)

    with pytest.raises(TypeError, match="param_name must be str, got int"):
        validate_cerberus_schema(data, schema, param_name=123)


def test_validate_cerberus_schema_value_error_missing_required() -> None:
    """
    Test case 14: ValueError for missing required fields.
    """
    schema = {
        "name": {"type": "string", "required": True},
        "email": {"type": "string", "required": True},
    }

    data = {"name": "Test"}  # Missing required email

    with pytest.raises(ValueError, match="data validation failed"):
        validate_cerberus_schema(data, schema)


def test_validate_cerberus_schema_value_error_type_mismatch() -> None:
    """
    Test case 15: ValueError for type mismatches.
    """
    schema = {"age": {"type": "integer"}, "active": {"type": "boolean"}}

    data = {"age": "not a number", "active": "not a boolean"}

    with pytest.raises(ValueError, match="data validation failed"):
        validate_cerberus_schema(data, schema)


def test_validate_cerberus_schema_value_error_constraint_violations() -> None:
    """
    Test case 16: ValueError for constraint violations.
    """
    schema = {
        "age": {"type": "integer", "min": 0, "max": 150},
        "name": {"type": "string", "minlength": 2, "maxlength": 50},
        "status": {"type": "string", "allowed": ["active", "inactive"]},
    }

    # Test age constraint violation
    data = {"age": -5, "name": "Test", "status": "active"}
    with pytest.raises(ValueError, match="data validation failed"):
        validate_cerberus_schema(data, schema)

    # Test string length violation
    data = {"age": 25, "name": "X", "status": "active"}  # Name too short
    with pytest.raises(ValueError, match="data validation failed"):
        validate_cerberus_schema(data, schema)

    # Test allowed values violation
    data = {"age": 25, "name": "Test", "status": "invalid"}
    with pytest.raises(ValueError, match="data validation failed"):
        validate_cerberus_schema(data, schema)


def test_validate_cerberus_schema_value_error_unknown_fields() -> None:
    """
    Test case 17: ValueError for unknown fields when not allowed.
    """
    schema = {"name": {"type": "string", "required": True}}

    data = {"name": "Test", "unknown_field": "not allowed"}

    with pytest.raises(ValueError, match="data validation failed"):
        validate_cerberus_schema(data, schema, allow_unknown=False)


def test_validate_cerberus_schema_value_error_nested_validation() -> None:
    """
    Test case 18: ValueError for nested validation failures.
    """
    schema = {
        "user": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "age": {"type": "integer", "min": 0},
            },
        }
    }

    # Test missing required field in nested object
    data = {"user": {"age": 25}}  # Missing name
    with pytest.raises(ValueError, match="data validation failed"):
        validate_cerberus_schema(data, schema)

    # Test constraint violation in nested object
    data = {"user": {"name": "Test", "age": -5}}  # Negative age
    with pytest.raises(ValueError, match="data validation failed"):
        validate_cerberus_schema(data, schema)


def test_validate_cerberus_schema_custom_param_name() -> None:
    """
    Test case 19: Custom parameter name in error messages.
    """
    schema = {"name": {"type": "string", "required": True}}
    data = {}  # Missing required field

    with pytest.raises(ValueError, match="config_data validation failed"):
        validate_cerberus_schema(data, schema, param_name="config_data")


def test_validate_cerberus_schema_cerberus_not_available() -> None:
    """Test case 20: ImportError when Cerberus is not available."""
    # Save the original module if it exists
    original_module = sys.modules.get(
        "data_validation.schema_validation.validate_cerberus_schema"
    )

    try:
        # Temporarily remove and reimport with CERBERUS_AVAILABLE = False
        if "pyutils_collection.data_validation.schema_validation.validate_cerberus_schema" in sys.modules:
            del sys.modules[
                "pyutils_collection.data_validation.schema_validation.validate_cerberus_schema"
            ]

        # Mock the module
        import pyutils_collection.data_validation.schema_validation.validate_cerberus_schema as module

        original_available = module.CERBERUS_AVAILABLE
        module.CERBERUS_AVAILABLE = False

        with pytest.raises(
            ImportError, match="Cerberus is required for schema validation"
        ):
            module.validate_cerberus_schema({}, {})

        # Restore
        module.CERBERUS_AVAILABLE = original_available
    finally:
        # Restore the original module
        if original_module:
            sys.modules[
                "data_validation.schema_validation.validate_cerberus_schema"
            ] = original_module


def test_validate_cerberus_schema_normalize_type_error() -> None:
    """Test case 21: TypeError for invalid normalize parameter."""
    schema = {"name": {"type": "string"}}
    data = {"name": "test"}
    with pytest.raises(TypeError, match="normalize must be bool"):
        validate_cerberus_schema(data, schema, normalize="yes")


def test_validate_cerberus_schema_param_name_type_error() -> None:
    """Test case 22: TypeError for invalid param_name parameter."""
    schema = {"name": {"type": "string"}}
    data = {"name": "test"}
    with pytest.raises(TypeError, match="param_name must be str"):
        validate_cerberus_schema(data, schema, param_name=123)


def test_validate_cerberus_schema_allow_unknown_type_error() -> None:
    """Test case 23: TypeError for invalid allow_unknown parameter."""
    schema = {"name": {"type": "string"}}
    data = {"name": "test"}
    with pytest.raises(TypeError, match="allow_unknown must be bool"):
        validate_cerberus_schema(data, schema, allow_unknown="yes")
