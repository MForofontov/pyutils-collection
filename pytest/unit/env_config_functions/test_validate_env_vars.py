"""Tests for grouped environment configuration validation."""

import pytest
from pyutils_collection.env_config_functions import validate_env_vars

pytestmark = [pytest.mark.unit, pytest.mark.env_config]


def test_converters_defaults_and_no_mutation() -> None:
    schema = {"PORT": int, "DEBUG": bool, "NAME": str, "TIMEOUT": float}
    source = {"PORT": "8080", "DEBUG": "false", "NAME": " Ada ", "OTHER": "ignore"}
    defaults = {"TIMEOUT": 2.5}
    assert validate_env_vars(schema, defaults, source) == {
        "PORT": 8080,
        "DEBUG": False,
        "NAME": " Ada ",
        "TIMEOUT": 2.5,
    }
    assert source["DEBUG"] == "false"
    assert defaults == {"TIMEOUT": 2.5}


@pytest.mark.parametrize(
    "value,expected",
    [
        ("true", True),
        (" YES ", True),
        ("on", True),
        ("1", True),
        ("false", False),
        ("NO", False),
        ("off", False),
        ("0", False),
    ],
)
def test_boolean_conversion(value, expected) -> None:
    assert validate_env_vars({"DEBUG": bool}, environ={"DEBUG": value}) == {
        "DEBUG": expected
    }


def test_all_errors_reported_without_secret_values() -> None:
    with pytest.raises(ValueError) as caught:
        validate_env_vars(
            {"MISSING": str, "PORT": int, "BLANK": str, "DEBUG": bool},
            environ={"PORT": "secret-token", "BLANK": " ", "DEBUG": "perhaps"},
        )
    message = str(caught.value)
    assert all(name in message for name in ["MISSING", "PORT", "BLANK", "DEBUG"])
    assert "secret-token" not in message
    assert "perhaps" not in message


def test_process_environment_and_empty_custom_environment(monkeypatch) -> None:
    monkeypatch.setenv("PYUTILS_TEST_PORT", "42")
    assert validate_env_vars({"PYUTILS_TEST_PORT": int}) == {"PYUTILS_TEST_PORT": 42}
    with pytest.raises(ValueError, match="missing"):
        validate_env_vars({"PYUTILS_TEST_PORT": int}, environ={})
    assert validate_env_vars({}, environ={}) == {}


def test_defaults_apply_only_to_absent_values() -> None:
    assert validate_env_vars({"PORT": int}, {"PORT": 80}, {}) == {"PORT": 80}
    with pytest.raises(ValueError):
        validate_env_vars({"PORT": int}, {"PORT": 80}, {"PORT": "invalid"})


@pytest.mark.parametrize(
    "schema,defaults,environ,error",
    [
        ([], None, {}, TypeError),
        ({"PORT": 1}, None, {}, TypeError),
        ({1: int}, None, {}, TypeError),
        ({"": str}, None, {}, TypeError),
        ({}, [], {}, TypeError),
        ({}, {"UNKNOWN": 1}, {}, ValueError),
        ({}, None, [], TypeError),
    ],
)
def test_invalid_configuration(schema, defaults, environ, error) -> None:
    with pytest.raises(error):
        validate_env_vars(schema, defaults, environ)
