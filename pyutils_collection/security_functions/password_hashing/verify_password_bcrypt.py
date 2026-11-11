"""Password verification using bcrypt algorithm."""

import bcrypt


def verify_password_bcrypt(
    password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a password against a bcrypt hash.

    Parameters
    ----------
    password : str
        The plaintext password to verify.
    hashed_password : str
        The bcrypt hashed password to verify against.

    Returns
    -------
    bool
        True if the password matches the hash, False otherwise. Passwords longer
        than 72 UTF-8 bytes return False rather than being silently truncated.

    Raises
    ------
    TypeError
        If password or hashed_password is not a string.
    ValueError
        If password or hashed_password is empty, or if hashed_password
        is not a valid bcrypt hash format.

    Examples
    --------
    >>> # First hash a password
    >>> from .hash_password_bcrypt import hash_password_bcrypt
    >>> hashed = hash_password_bcrypt("my_secret_password")
    >>> verify_password_bcrypt("my_secret_password", hashed)
    True
    >>> verify_password_bcrypt("wrong_password", hashed)
    False
    >>> verify_password_bcrypt("", hashed)  # doctest: +SKIP
    Traceback (most recent call last):
    ValueError: password cannot be empty

    Notes
    -----
    This function uses constant-time comparison to prevent timing attacks.
    The bcrypt.checkpw function handles the salt extraction and comparison
    automatically.

    Complexity
    ----------
    Time: O(2^rounds), Space: O(1)
    """
    # Input validation
    if not isinstance(password, str):
        raise TypeError(f"password must be a string, got {type(password).__name__}")
    if not isinstance(hashed_password, str):
        raise TypeError(
            f"hashed_password must be a string, got {type(hashed_password).__name__}"
        )

    # Value validation
    if len(password) == 0:
        raise ValueError("password cannot be empty")
    if len(hashed_password) == 0:
        raise ValueError("hashed_password cannot be empty")

    # Validate bcrypt hash format
    if not hashed_password.startswith(("$2a$", "$2b$", "$2x$", "$2y$")):
        raise ValueError("Invalid bcrypt hash format")
    if len(hashed_password) != 60:
        raise ValueError("hashed_password must be exactly 60 characters long")

    try:
        # Verify password against hash
        password_bytes = password.encode("utf-8")
        if len(password_bytes) > 72:
            return False
        return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))
    except Exception:
        return False


__all__ = ["verify_password_bcrypt"]
