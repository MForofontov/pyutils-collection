"""Safe type casting utilities."""

from typing import Any, TypeVar

T = TypeVar("T")


def safe_cast(value: Any, target_type: type[T], default: T | None = None) -> T | Any:
    """
    Safely cast a value to a target type with optional fallback.

    Attempts to convert the value to the target type. If conversion fails,
    returns the default value or the original value if no default is provided.

    Parameters
    ----------
    value : Any
        The value to cast.
    target_type : type[T]
        The target type to cast to.
    default : T | None, optional
        Default value to return if casting fails (by default None).

    Returns
    -------
    T | Any
        The cast value if successful, otherwise the default or original value.

    Raises
    ------
    TypeError
        If target_type is not a type.

    Examples
    --------
    >>> safe_cast("123", int)
    123

    >>> safe_cast("abc", int, 0)
    0

    >>> safe_cast("abc", int)  # No default provided
    'abc'

    >>> safe_cast(42, str)
    '42'

    >>> safe_cast(None, str, "default")
    'default'

    Notes
    -----
    This function handles common type conversion scenarios and provides
    graceful fallback when conversion is not possible.

    Complexity
    ----------
    Time: O(1) for simple types, O(n) for complex conversions
    """
    # Input validation
    if not isinstance(target_type, type):
        raise TypeError(f"target_type must be a type, got {type(target_type).__name__}")

    # Handle None values
    if value is None:
        if default is not None:
            return default
        return value

    # Attempt type conversion
    try:
        if target_type is bool:
            # Special handling for boolean conversion
            if isinstance(value, str):
                if value.lower() in ("true", "1", "yes", "on"):
                    return True
                elif value.lower() in ("false", "0", "no", "off", ""):
                    return False
                else:
                    raise ValueError(f"Cannot convert '{value}' to bool")
            return bool(value)
        elif target_type is int:
            # Handle string to int conversion
            if isinstance(value, str):
                return int(float(value)) if "." in value else int(value)
            return int(value)
        elif target_type is float:
            return float(value)
        elif target_type is str:
            return str(value)
        elif target_type is list:
            if isinstance(value, (list, tuple)):
                return list(value)
            elif isinstance(value, (str, bytes)):
                return [value]
            elif hasattr(value, "__iter__"):
                return list(value)
            else:
                return [value]
        elif target_type is tuple:
            if isinstance(value, (list, tuple)):
                return tuple(value)
            elif isinstance(value, (str, bytes)):
                return (value,)
            elif hasattr(value, "__iter__"):
                return tuple(value)
            else:
                return (value,)
        else:
            # Generic conversion attempt
            return target_type(value)  # type: ignore[call-arg]
    except (ValueError, TypeError, AttributeError):
        # Conversion failed, return default or original value
        if default is not None:
            return default
        return value


def is_numeric(value: Any) -> bool:
    """
    Check if a value represents a numeric type.

    Parameters
    ----------
    value : Any
        The value to check.

    Returns
    -------
    bool
        True if the value is numeric, False otherwise.

    Examples
    --------
    >>> is_numeric(42)
    True

    >>> is_numeric(3.14)
    True

    >>> is_numeric("123")
    False

    >>> is_numeric("123.45")
    False

    Notes
    -----
    This function checks for actual numeric types (int, float, complex)
    and does not attempt string parsing.

    Complexity
    ----------
    Time: O(1)
    """
    return isinstance(value, (int, float, complex)) and not isinstance(value, bool)


__all__ = ["safe_cast", "is_numeric"]
