"""Validate and convert environment configuration as a group."""

import os
from collections.abc import Callable, Mapping
from typing import Any


def validate_env_vars(
    schema: dict[str, Callable[[str], Any]],
    defaults: dict[str, Any] | None = None,
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """
    Convert schema variables and report all missing or invalid values together.

    Parameters
    ----------
    schema : dict[str, callable]
        Variable names mapped to converters such as str, int, or float. The bool
        converter accepts true/false, yes/no, on/off, and 1/0, ignoring case and
        surrounding whitespace. Other converters receive the original string.
    defaults : dict[str, Any], optional
        Already-converted defaults for absent variables. Keys must be in schema.
    environ : Mapping[str, str], optional
        Source mapping (default os.environ). The mapping is never modified.

    Returns
    -------
    dict[str, Any]
        Converted values and defaults in schema order. Unlisted variables are ignored.

    Raises
    ------
    TypeError
        If schema, defaults, environ, or schema entries have invalid types.
    ValueError
        If defaults contains unknown keys, or any required value is missing,
        blank, or cannot be converted. Error messages omit variable values.

    Examples
    --------
    >>> validate_env_vars({'PORT': int, 'DEBUG': bool},
    ...                   environ={'PORT': '8080', 'DEBUG': 'false'})
    {'PORT': 8080, 'DEBUG': False}

    Complexity
    ----------
    Time and space: O(n), excluding converter costs, for n schema entries.
    """
    if not isinstance(schema, dict) or not all(
        isinstance(name, str) and name and callable(converter)
        for name, converter in schema.items()
    ):
        raise TypeError("schema must map nonempty string names to callables")
    if defaults is None:
        defaults = {}
    if not isinstance(defaults, dict):
        raise TypeError("defaults must be a dictionary or None")
    if defaults.keys() - schema.keys():
        raise ValueError("defaults contains keys absent from schema")
    if environ is None:
        environ = os.environ
    if not isinstance(environ, Mapping):
        raise TypeError("environ must be a mapping or None")

    result: dict[str, Any] = {}
    errors: list[str] = []
    boolean_values = {
        "true": True,
        "yes": True,
        "on": True,
        "1": True,
        "false": False,
        "no": False,
        "off": False,
        "0": False,
    }
    for name, converter in schema.items():
        if name not in environ:
            if name in defaults:
                result[name] = defaults[name]
            else:
                errors.append(f"{name}: missing")
            continue
        value = environ[name]
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{name}: must be a nonempty string")
            continue
        try:
            result[name] = (
                boolean_values[value.strip().lower()]
                if converter is bool
                else converter(value)
            )
        except Exception:
            errors.append(f"{name}: invalid value")
    if errors:
        raise ValueError("Environment validation failed: " + "; ".join(errors))
    return result


__all__ = ["validate_env_vars"]
