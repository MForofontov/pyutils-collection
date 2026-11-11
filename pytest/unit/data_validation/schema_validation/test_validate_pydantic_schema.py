import importlib

import pytest

# Try to import pydantic - tests will be skipped if not available
try:
    from pydantic import BaseModel, Field, ValidationError
    from pyutils_collection.data_validation import validate_pydantic_schema

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = object  # type: ignore
    validate_pydantic_schema = None  # type: ignore

    def Field(**kwargs):
        return None  # type: ignore

    ValidationError = Exception  # type: ignore

validate_pydantic_schema_module = importlib.import_module(
    "pyutils_collection.data_validation.schema_validation.validate_pydantic_schema"
)

pytestmark = pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not installed")
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.data_validation]


class SimpleUserSchema(BaseModel):
    """Simple user schema for testing."""

    name: str
    age: int
    email: str


class UserWithOptionalSchema(BaseModel):
    """User schema with optional fields."""

    name: str
    age: int
    email: str | None = None
    active: bool = True


class NestedSchema(BaseModel):
    """Schema with nested objects."""

    user: SimpleUserSchema
    created_at: str
    metadata: dict = {}


def test_validate_pydantic_schema_simple_valid_data() -> None:
    """
    Test case 1: Simple valid data validation.
    """
    # Test basic valid data
    data = {"name": "John Doe", "age": 30, "email": "john@example.com"}
    result = validate_pydantic_schema(data, SimpleUserSchema)

    assert isinstance(result, SimpleUserSchema)
    assert result.name == "John Doe"
    assert result.age == 30
    assert result.email == "john@example.com"


def test_validate_pydantic_schema_optional_fields() -> None:
    """
    Test case 2: Schema with optional fields and defaults.
    """
    # Test with all fields
    data = {"name": "Jane", "age": 25, "email": "jane@example.com", "active": False}
    result = validate_pydantic_schema(data, UserWithOptionalSchema)

    assert result.name == "Jane"
    assert result.age == 25
    assert result.email == "jane@example.com"
    assert result.active is False

    # Test with optional fields missing (should use defaults)
    data = {"name": "Bob", "age": 35}
    result = validate_pydantic_schema(data, UserWithOptionalSchema)

    assert result.name == "Bob"
    assert result.age == 35
    assert result.email is None
    assert result.active is True


def test_validate_pydantic_schema_nested_objects() -> None:
    """
    Test case 3: Nested object validation.
    """
    data = {
        "user": {"name": "Alice", "age": 28, "email": "alice@example.com"},
        "created_at": "2023-01-01T00:00:00Z",
        "metadata": {"source": "api", "version": "1.0"},
    }

    result = validate_pydantic_schema(data, NestedSchema)

    assert isinstance(result.user, SimpleUserSchema)
    assert result.user.name == "Alice"
    assert result.user.age == 28
    assert result.created_at == "2023-01-01T00:00:00Z"
    assert result.metadata == {"source": "api", "version": "1.0"}


def test_validate_pydantic_schema_type_coercion() -> None:
    """
    Test case 4: Type coercion during validation.
    """
    # Test with string numbers that should be coerced
    data = {"name": "Charlie", "age": "40", "email": "charlie@example.com"}
    result = validate_pydantic_schema(data, SimpleUserSchema, strict=False)

    assert result.name == "Charlie"
    assert result.age == 40  # Should be coerced to int
    assert result.email == "charlie@example.com"


def test_validate_pydantic_schema_strict_mode() -> None:
    """
    Test case 5: Strict validation mode.
    """
    # Test strict mode with exact types
    data = {"name": "David", "age": 45, "email": "david@example.com"}
    result = validate_pydantic_schema(data, SimpleUserSchema, strict=True)

    assert result.name == "David"
    assert result.age == 45
    assert result.email == "david@example.com"


def test_validate_pydantic_schema_allow_extra_fields() -> None:
    """
    Test case 6: Allow extra fields validation.
    """
    # Test with extra fields allowed
    data = {
        "name": "Eve",
        "age": 32,
        "email": "eve@example.com",
        "extra_field": "should be allowed",
    }

    result = validate_pydantic_schema(data, SimpleUserSchema, allow_extra=True)

    assert result.name == "Eve"
    assert result.age == 32
    assert result.email == "eve@example.com"


def test_validate_pydantic_schema_edge_cases() -> None:
    """
    Test case 7: Edge cases and boundary conditions.
    """
    # Test with empty dict for schema with defaults
    data = {}

    class AllOptionalSchema(BaseModel):
        name: str = "default"
        count: int = 0

    result = validate_pydantic_schema(data, AllOptionalSchema)
    assert result.name == "default"
    assert result.count == 0

    # Test with None values where allowed
    data = {"name": "Test", "age": 25, "email": None}
    result = validate_pydantic_schema(data, UserWithOptionalSchema)
    assert result.email is None


def test_validate_pydantic_schema_complex_schemas() -> None:
    """
    Test case 8: Complex schemas with various field types.
    """

    class ComplexSchema(BaseModel):
        name: str
        tags: list[str] = []
        config: dict = {}
        score: float = 0.0
        enabled: bool = True

    data = {
        "name": "Complex Test",
        "tags": ["tag1", "tag2"],
        "config": {"key": "value"},
        "score": 95.5,
        "enabled": False,
    }

    result = validate_pydantic_schema(data, ComplexSchema)

    assert result.name == "Complex Test"
    assert result.tags == ["tag1", "tag2"]
    assert result.config == {"key": "value"}
    assert result.score == 95.5
    assert result.enabled is False


def test_validate_pydantic_schema_large_data() -> None:
    """
    Test case 9: Validate a large nested payload without a machine-specific deadline.
    """
    class UserBatchSchema(BaseModel):
        users: list[SimpleUserSchema]

    users = [
        {"name": f"User {index}", "age": index, "email": f"user{index}@example.com"}
        for index in range(1000)
    ]
    result = validate_pydantic_schema({"users": users}, UserBatchSchema)
    assert len(result.users) == len(users)
    assert [user.model_dump() for user in result.users] == users


def test_validate_pydantic_schema_type_error_invalid_schema() -> None:
    """
    Test case 10: TypeError for invalid schema model.
    """
    data = {"name": "Test", "age": 25}

    # Test with non-BaseModel class
    class NotAModel:
        pass

    with pytest.raises(
        TypeError, match="schema_model must be a Pydantic BaseModel class"
    ):
        validate_pydantic_schema(data, NotAModel)

    # Test with non-class object
    with pytest.raises(
        TypeError, match="schema_model must be a Pydantic BaseModel class"
    ):
        validate_pydantic_schema(data, "not a class")


def test_validate_pydantic_schema_type_error_invalid_parameters() -> None:
    """
    Test case 11: TypeError for invalid parameter types.
    """
    data = {"name": "Test", "age": 25, "email": "test@example.com"}

    with pytest.raises(TypeError, match="strict must be bool, got str"):
        validate_pydantic_schema(data, SimpleUserSchema, strict="true")

    with pytest.raises(TypeError, match="allow_extra must be bool, got int"):
        validate_pydantic_schema(data, SimpleUserSchema, allow_extra=1)

    with pytest.raises(TypeError, match="param_name must be str, got int"):
        validate_pydantic_schema(data, SimpleUserSchema, param_name=123)


def test_validate_pydantic_schema_value_error_validation_failure() -> None:
    """
    Test case 12: ValueError for validation failures.
    """
    # Test missing required field
    data = {"name": "Test", "age": 25}  # Missing email

    with pytest.raises(ValueError, match="data validation failed"):
        validate_pydantic_schema(data, SimpleUserSchema)

    # Test wrong type
    data = {"name": "Test", "age": "not a number", "email": "test@example.com"}

    with pytest.raises(ValueError, match="data validation failed"):
        validate_pydantic_schema(data, SimpleUserSchema)


def test_validate_pydantic_schema_value_error_extra_fields_forbidden() -> None:
    """
    Test case 13: ValueError when extra fields are forbidden.
    """
    data = {
        "name": "Test",
        "age": 25,
        "email": "test@example.com",
        "extra_field": "not allowed",
    }

    with pytest.raises(ValueError, match="data validation failed"):
        validate_pydantic_schema(data, SimpleUserSchema, allow_extra=False)


def test_validate_pydantic_schema_value_error_strict_mode() -> None:
    """
    Test case 14: ValueError in strict mode with type coercion.
    """
    # Test strict mode rejecting type coercion
    data = {"name": "Test", "age": "25", "email": "test@example.com"}  # age as string

    with pytest.raises(ValueError, match="data validation failed"):
        validate_pydantic_schema(data, SimpleUserSchema, strict=True)


def test_validate_pydantic_schema_value_error_nested_validation() -> None:
    """
    Test case 15: ValueError for nested object validation failures.
    """
    # Test invalid nested object
    data = {
        "user": {"name": "Test", "age": "invalid"},  # Invalid age in nested object
        "created_at": "2023-01-01",
    }

    with pytest.raises(ValueError, match="data validation failed"):
        validate_pydantic_schema(data, NestedSchema)


def test_validate_pydantic_schema_custom_param_name() -> None:
    """
    Test case 16: Custom parameter name in error messages.
    """
    data = {"name": "Test", "age": "invalid"}  # Missing email, invalid age

    with pytest.raises(ValueError, match="user_data validation failed"):
        validate_pydantic_schema(data, SimpleUserSchema, param_name="user_data")
