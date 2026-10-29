"""Bcrypt password hashing utility."""

import bcrypt


def hash_password_bcrypt(password: str, rounds: int = 12) -> str:
    """
    Hash a password using bcrypt with configurable cost factor.

    Parameters
    ----------
    password : str
        The password to hash, at most 72 bytes when encoded as UTF-8.
    rounds : int, optional
        The cost factor (number of rounds) for bcrypt hashing.
        Must be between 4 and 31. Higher values are more secure but slower
        (by default 12).

    Returns
    -------
    str
        The bcrypt hashed password as a string.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values.

    Examples
    --------
    >>> hashed = hash_password_bcrypt("my_secret_password")
    >>> len(hashed)
    60
    >>> hashed.startswith("$2b$")
    True
    >>> hashed = hash_password_bcrypt("password", rounds=10)
    >>> "$2b$10$" in hashed
    True

    Notes
    -----
    - bcrypt automatically generates a random salt for each hash
    - The resulting hash is always 60 characters long
    - Higher rounds values increase security but also computation time
    - Default of 12 rounds provides good security for most applications

    Complexity
    ----------
    Time: O(2^rounds), Space: O(1)
    """
    # Input validation
    if not isinstance(password, str):
        raise TypeError(f"password must be a string, got {type(password).__name__}")
    if not isinstance(rounds, int):
        raise TypeError(f"rounds must be an integer, got {type(rounds).__name__}")

    # Value validation
    if not password:
        raise ValueError("password cannot be empty")
    if not (4 <= rounds <= 31):
        raise ValueError(f"rounds must be between 4 and 31, got {rounds}")

    # Convert password to bytes and hash
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        raise ValueError("password cannot be longer than 72 bytes")
    salt = bcrypt.gensalt(rounds=rounds)
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return as string
    return hashed.decode("utf-8")


__all__ = ["hash_password_bcrypt"]
