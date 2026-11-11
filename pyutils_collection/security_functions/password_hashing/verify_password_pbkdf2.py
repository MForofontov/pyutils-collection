"""Password verification using PBKDF2 algorithm."""

import hashlib
import hmac


def verify_password_pbkdf2(
    password: str,
    hashed_password: str,
    salt: bytes,
    iterations: int = 100000,
) -> bool:
    """
    Verify a password against a PBKDF2 hash.

    Parameters
    ----------
    password : str
        The plaintext password to verify.
    hashed_password : str
        The PBKDF2 hashed password as hex string to verify against.
    salt : bytes
        The salt used for the original hash.
    iterations : int, optional
        The number of iterations used for the original hash (by default 100000).

    Returns
    -------
    bool
        True if the password matches the hash, False otherwise.

    Raises
    ------
    TypeError
        If parameters are not of the correct type.
    ValueError
        If password or hashed_password is empty, or iterations is invalid.

    Examples
    --------
    >>> from .hash_password_pbkdf2 import hash_password_pbkdf2
    >>> hashed, salt = hash_password_pbkdf2("my_secret_password")
    >>> verify_password_pbkdf2("my_secret_password", hashed, salt)
    True
    >>> verify_password_pbkdf2("wrong_password", hashed, salt)
    False
    >>> verify_password_pbkdf2("", hashed, salt)  # doctest: +SKIP
    Traceback (most recent call last):
    ValueError: password cannot be empty

    Notes
    -----
    This function uses constant-time comparison through hashlib.pbkdf2_hmac
    to prevent timing attacks. The verification recreates the hash with
    the same parameters and compares the results.

    Complexity
    ----------
    Time: O(iterations), Space: O(1)
    """
    # Input validation
    if not isinstance(password, str):
        raise TypeError(f"password must be a string, got {type(password).__name__}")
    if not isinstance(hashed_password, str):
        raise TypeError(
            f"hashed_password must be a string, got {type(hashed_password).__name__}"
        )
    if not isinstance(salt, bytes):
        raise TypeError(f"salt must be bytes, got {type(salt).__name__}")
    if not isinstance(iterations, int):
        raise TypeError(
            f"iterations must be an integer, got {type(iterations).__name__}"
        )

    # Value validation
    if len(password) == 0:
        raise ValueError("password cannot be empty")
    if len(hashed_password) == 0:
        raise ValueError("hashed_password cannot be empty")
    if len(salt) == 0:
        raise ValueError("salt cannot be empty")
    if iterations < 1000:
        raise ValueError(
            f"iterations must be at least 1000 for security, got {iterations}"
        )

    # Validate hex format
    try:
        bytes.fromhex(hashed_password)
    except ValueError as e:
        raise ValueError(f"hashed_password must be a valid hex string: {e}") from e

    try:
        # Recreate hash with same parameters
        computed_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, iterations
        )

        # Compare hashes using constant-time comparison
        return hmac.compare_digest(computed_hash, bytes.fromhex(hashed_password))
    except Exception as e:
        raise ValueError(f"Error during password verification: {e}") from e


__all__ = ["verify_password_pbkdf2"]
