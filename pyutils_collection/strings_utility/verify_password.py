"""Password strength verification."""

import re
from collections.abc import Callable, Iterable


def verify_password(
    password: str,
    custom_checks: Iterable[Callable[[str], bool]] | None = None,
) -> bool:
    """
    Verify if a password meets the following criteria:
    - At least 8 characters long
    - Contains both uppercase and lowercase characters
    - Contains at least one numerical digit
    - Contains at least one special character (e.g., @, #, $, etc.)
    - Passes all custom checks provided

    Parameters
    ----------
    password : str
        The password to verify.
    custom_checks : Iterable[Callable[[str], bool]], optional
        An iterable of custom check functions that take the password as input and
        return a boolean. Defaults to ``None``. One-shot iterables are consumed
        once into a tuple before validation; rules then run in iteration order
        and stop at the first false result.

    Returns
    -------
    bool
        True if the password meets all criteria, False otherwise.

    Raises
    ------
    TypeError
        If the password is not a string or if ``custom_checks`` is not an
        iterable of callables.

    Examples
    --------
    >>> verify_password("Password123!")
    True
    >>> verify_password("password")
    False
    >>> verify_password("PASSWORD123")
    False
    >>> verify_password("Pass123")
    False
    >>> custom_check = lambda p: 'example' in p
    >>> verify_password("Password123!example", custom_checks=[custom_check])
    True
    >>> verify_password("Password123!", custom_checks=[custom_check])
    False
    """
    if not isinstance(password, str):
        raise TypeError("The password must be a string.")

    if custom_checks is None:
        custom_checks = ()
    elif not isinstance(custom_checks, Iterable) or isinstance(
        custom_checks, (str, bytes)
    ):
        raise TypeError("custom_checks must be an iterable of callables.")
    else:
        custom_checks = tuple(custom_checks)
        if not all(callable(check) for check in custom_checks):
            raise TypeError("custom_checks must be an iterable of callables.")

    # Check if the password is at least 8 characters long
    if len(password) < 8:
        return False

    # Check if the password contains both uppercase and lowercase characters
    if not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password):
        return False

    # Check if the password contains at least one numerical digit
    if not re.search(r"\d", password):
        return False

    # Check if the password contains at least one special character
    if not re.search(r"[!@#$%^&+=]", password):
        return False

    # Check custom rules
    for check in custom_checks:
        if not check(password):
            return False

    return True


__all__ = ["verify_password"]
