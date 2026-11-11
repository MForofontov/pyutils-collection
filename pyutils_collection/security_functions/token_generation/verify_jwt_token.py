"""JWT token verification."""

import base64
import hashlib
import hmac
import json
import math
from datetime import UTC, datetime
from typing import Any


def verify_jwt_token(
    token: str,
    secret_key: str,
) -> dict[str, Any]:
    """
    Verify and decode a JWT token.

    Parameters
    ----------
    token : str
        The JWT token to verify and decode.
    secret_key : str
        The secret key used for verifying the token signature.

    Returns
    -------
    dict[str, Any]
        The decoded payload if the token is valid.

    Raises
    ------
    TypeError
        If parameters are not of the correct type.
    ValueError
        If token format is invalid, signature verification fails,
        or token is expired.

    Examples
    --------
    >>> from .generate_jwt_token import generate_jwt_token
    >>> payload = {"user_id": 123}
    >>> secret = "my_secret_key"
    >>> token = generate_jwt_token(payload, secret, 1)
    >>> decoded = verify_jwt_token(token, secret)
    >>> decoded["user_id"] == 123
    True
    >>> "iat" in decoded and "exp" in decoded
    True

    Notes
    -----
    This function verifies the token signature using HMAC-SHA256 and
    checks the expiration time. It returns the full payload including
    both custom claims and standard JWT claims.

    Complexity
    ----------
    Time: O(n) where n is the size of the token, Space: O(n)
    """
    # Input validation
    if not isinstance(token, str):
        raise TypeError(f"token must be a string, got {type(token).__name__}")
    if not isinstance(secret_key, str):
        raise TypeError(f"secret_key must be a string, got {type(secret_key).__name__}")

    # Value validation
    if len(token) == 0:
        raise ValueError("token cannot be empty")
    if len(secret_key) == 0:
        raise ValueError("secret_key cannot be empty")

    # Split token into parts
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("invalid JWT format: token must have exactly 3 parts")

    encoded_header, encoded_payload, encoded_signature = parts

    def decode_base64url(data: str) -> bytes:
        """Decode base64url encoded data."""
        # Add padding if necessary
        padding = 4 - (len(data) % 4)
        if padding != 4:
            data += "=" * padding
        try:
            return base64.b64decode(data, altchars=b"-_", validate=True)
        except Exception as e:
            raise ValueError(f"invalid base64url encoding: {e}") from e

    try:
        # Decode header and payload
        header_bytes = decode_base64url(encoded_header)
        payload_bytes = decode_base64url(encoded_payload)
        signature_bytes = decode_base64url(encoded_signature)

        header = json.loads(header_bytes.decode("utf-8"))
        payload = json.loads(payload_bytes.decode("utf-8"))

    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ValueError(f"invalid base64url encoding: {e}") from e

    if not isinstance(header, dict) or not isinstance(payload, dict):
        raise ValueError("JWT header and payload must be JSON objects")

    # Verify algorithm
    if header.get("alg") != "HS256":
        raise ValueError(f"unsupported algorithm: {header.get('alg')}")

    # Verify signature
    message = f"{encoded_header}.{encoded_payload}"
    expected_signature = hmac.new(
        secret_key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
    ).digest()

    if not hmac.compare_digest(signature_bytes, expected_signature):
        raise ValueError("invalid token signature")

    # Check expiration
    if "exp" in payload:
        exp_timestamp = payload["exp"]
        if (
            not isinstance(exp_timestamp, (int, float))
            or isinstance(exp_timestamp, bool)
            or (isinstance(exp_timestamp, float) and not math.isfinite(exp_timestamp))
        ):
            raise ValueError("invalid expiration time format")

        current_timestamp = datetime.now(UTC).timestamp()
        if current_timestamp >= exp_timestamp:
            raise ValueError("token has expired")

    return payload


__all__ = ["verify_jwt_token"]
