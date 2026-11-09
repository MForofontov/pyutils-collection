"""JWT token generation and verification."""

import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta
from typing import Any


def generate_jwt_token(
    payload: dict[str, Any],
    secret_key: str,
    expires_in_hours: int = 24,
) -> str:
    """
    Generate a JWT token with the given payload and secret key.

    Parameters
    ----------
    payload : dict[str, Any]
        The payload data to include in the JWT token.
    secret_key : str
        The secret key used for signing the token.
    expires_in_hours : int, optional
        The number of hours until the token expires (by default 24).

    Returns
    -------
    str
        A JWT token string in the format "header.payload.signature".

    Raises
    ------
    TypeError
        If parameters are not of the correct type.
    ValueError
        If secret_key is empty or expires_in_hours is not positive.

    Examples
    --------
    >>> payload = {"user_id": 123, "username": "testuser"}
    >>> secret = "my_secret_key"
    >>> token = generate_jwt_token(payload, secret, 1)
    >>> len(token.split('.')) == 3  # header.payload.signature
    True
    >>> isinstance(token, str)
    True

    Notes
    -----
    This implementation uses HMAC-SHA256 for signing. The token includes
    standard claims like 'iat' (issued at) and 'exp' (expiration time).
    The header is fixed to use HS256 algorithm.

    Complexity
    ----------
    Time: O(n) where n is the size of the payload, Space: O(n)
    """
    # Input validation
    if not isinstance(payload, dict):
        raise TypeError(f"payload must be a dictionary, got {type(payload).__name__}")
    if not isinstance(secret_key, str):
        raise TypeError(f"secret_key must be a string, got {type(secret_key).__name__}")
    if not isinstance(expires_in_hours, int):
        raise TypeError(
            f"expires_in_hours must be an integer, got {type(expires_in_hours).__name__}"
        )

    # Value validation
    if len(secret_key) == 0:
        raise ValueError("secret_key cannot be empty")
    if expires_in_hours <= 0:
        raise ValueError(f"expires_in_hours must be positive, got {expires_in_hours}")

    # Create header
    header = {"alg": "HS256", "typ": "JWT"}

    # Create payload with timestamps
    now = datetime.now(UTC)
    exp_time = now + timedelta(hours=expires_in_hours)

    full_payload = {
        **payload,
        "iat": now.timestamp(),
        "exp": exp_time.timestamp(),
    }

    # Encode header and payload
    def encode_base64url(data: dict[str, Any]) -> str:
        json_str = json.dumps(data, separators=(",", ":"))
        encoded = base64.urlsafe_b64encode(json_str.encode("utf-8"))
        return encoded.decode("utf-8").rstrip("=")

    encoded_header = encode_base64url(header)
    encoded_payload = encode_base64url(full_payload)

    # Create signature
    message = f"{encoded_header}.{encoded_payload}"
    signature = hmac.new(
        secret_key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
    ).digest()

    encoded_signature = base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")

    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


__all__ = ["generate_jwt_token"]
