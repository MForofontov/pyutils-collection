"""Runtime type enforcement decorator."""

import inspect
import logging
from collections.abc import Callable
from functools import wraps
from types import UnionType
from typing import Any, ParamSpec, TypeVar, get_args, get_origin, get_type_hints

from pyutils_collection.logger_functions.logger import validate_logger

P = ParamSpec("P")
R = TypeVar("R")


def enforce_types(
    logger: logging.Logger | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    A decorator to enforce type checking on the arguments and return value of a function.

    Parameters
    ----------
    logger : logging.Logger | None
        The logger to use for logging type errors.

    Returns
    -------
    Callable[[Callable[P, R]], Callable[P, R]]
        The decorator function.

    Raises
    ------
    TypeError
        If the logger is not an instance of logging.Logger or None.

    Notes
    -----
    ``Any`` accepts every value. Union annotations accept a value matching any
    member, including when nested inside supported container annotations.
    """
    validate_logger(logger)

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        """
        The actual decorator function.

        Parameters
        ----------
        func : Callable[P, R]
            The function to be decorated.

        Returns
        -------
        Callable[P, R]
            The wrapped function.
        """

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            """
            The wrapper function that checks the types of the arguments and return value.

            Parameters
            ----------
            *args : Any
                Positional arguments for the decorated function.
            **kwargs : Any
                Keyword arguments for the decorated function.

            Returns
            -------
            Any
                The result of the decorated function.

            Raises
            ------
            TypeError
                If an argument or return value does not match the expected type.
            """

            def _is_instance(value: Any, expected_type: Any) -> bool:
                if expected_type is Any:
                    return True
                origin = get_origin(expected_type)
                if origin is None:
                    return isinstance(value, expected_type)
                args = get_args(expected_type)
                if origin is UnionType:
                    return any(_is_instance(value, member) for member in args)
                if origin in {list, set, frozenset}:
                    if not isinstance(value, origin):
                        return False
                    if not args:
                        return True
                    return all(_is_instance(v, args[0]) for v in value)
                if origin is tuple:
                    if not isinstance(value, tuple):
                        return False
                    if len(args) == 2 and args[1] is Ellipsis:
                        return all(_is_instance(v, args[0]) for v in value)
                    if len(args) != len(value):
                        return False
                    return all(
                        _is_instance(v, t) for v, t in zip(value, args, strict=False)
                    )
                if origin is dict:
                    if not isinstance(value, dict):
                        return False
                    if not args:
                        return True
                    key_t, val_t = args
                    return all(
                        _is_instance(k, key_t) and _is_instance(v, val_t)
                        for k, v in value.items()
                    )
                return isinstance(value, origin)

            hints = get_type_hints(func)
            sig = inspect.signature(func)
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()

            for arg_name, arg_value in bound.arguments.items():
                if arg_name in hints:
                    expected_type = hints[arg_name]
                    param = sig.parameters[arg_name]
                    if param.kind is inspect.Parameter.VAR_POSITIONAL:
                        if not all(_is_instance(v, expected_type) for v in arg_value):
                            error_message = f"Expected {expected_type} for *{arg_name}, got {arg_value!r}."
                            if logger:
                                logger.error(error_message, exc_info=True)
                            raise TypeError(error_message)
                        continue
                    if param.kind is inspect.Parameter.VAR_KEYWORD:
                        if not _is_instance(arg_value, expected_type):
                            error_message = f"Expected {expected_type} for **{arg_name}, got {type(arg_value)}."
                            if logger:
                                logger.error(error_message, exc_info=True)
                            raise TypeError(error_message)
                        continue
                    if not _is_instance(arg_value, expected_type):
                        error_message = f"Expected {expected_type} for argument '{arg_name}', got {type(arg_value)}."
                        if logger:
                            logger.error(error_message, exc_info=True)
                        raise TypeError(error_message)
            result = func(*args, **kwargs)
            if "return" in hints:
                expected_return_type = hints["return"]
                if not _is_instance(result, expected_return_type):
                    error_message = f"Expected return type {expected_return_type}, got {type(result)}."
                    if logger:
                        logger.error(error_message, exc_info=True)
                    raise TypeError(error_message)
            return result

        return wrapper

    return decorator


__all__ = ["enforce_types"]
