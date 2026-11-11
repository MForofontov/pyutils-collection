"""Attempt type conversion with fallback."""

from typing import Any, TypeVar

T = TypeVar("T")


def _convert_to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in ("true", "1", "yes", "on"):
            return True
        if normalized in ("false", "0", "no", "off", ""):
            return False
        raise ValueError(f"Cannot convert '{value}' to bool")
    return bool(value)


def try_convert_to_type(value: Any, target_type: type[T]) -> T:
    """
    Attempt to convert ``value`` to ``target_type``.

    Parameters
    ----------
    value : Any
        The value to be converted.
    target_type : type[T]
        The type to which ``value`` should be converted.

    Returns
    -------
    T
        The converted value if the conversion is successful.

    Raises
    ------
    TypeError
        If ``target_type`` is not a ``type``.
    ValueError
        If the conversion fails.
    """
    if not isinstance(target_type, type):
        raise TypeError("target_type must be a type")

    try:
        if target_type is bool:
            return _convert_to_bool(value)  # type: ignore[return-value]
        return target_type(value)  # type: ignore[call-arg]
    except (ValueError, TypeError) as e:
        raise ValueError(f"Failed to convert {value} to {target_type}") from e


__all__ = ["try_convert_to_type"]
