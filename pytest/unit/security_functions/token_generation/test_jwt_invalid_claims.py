"""Malformed signed claims must fail predictably rather than bypass expiry."""

import base64
import hashlib
import hmac
import json

import pytest
from pyutils_collection.security_functions.token_generation.verify_jwt_token import (
    verify_jwt_token,
)

pytestmark = [pytest.mark.unit, pytest.mark.security]


def signed_token(header, payload):
    def encode(value):
        return base64.urlsafe_b64encode(json.dumps(value).encode()).decode().rstrip("=")

    message = f"{encode(header)}.{encode(payload)}"
    signature = hmac.new(b"secret", message.encode(), hashlib.sha256).digest()
    return message + "." + base64.urlsafe_b64encode(signature).decode().rstrip("=")


@pytest.mark.parametrize(
    "expiry", [float("nan"), float("inf"), -float("inf"), True, False]
)
def test_invalid_expiration(expiry):
    with pytest.raises(ValueError, match="expiration"):
        verify_jwt_token(signed_token({"alg": "HS256"}, {"exp": expiry}), "secret")


@pytest.mark.parametrize(
    "header,payload",
    [([], {}), (None, {}), ({"alg": "HS256"}, []), ({"alg": "HS256"}, 1)],
)
def test_non_object_claims(header, payload):
    with pytest.raises(ValueError, match="JSON objects"):
        verify_jwt_token(signed_token(header, payload), "secret")


def test_signature_rejects_non_base64_characters():
    token = signed_token({"alg": "HS256"}, {"user": "example"})
    with pytest.raises(ValueError, match="base64url"):
        verify_jwt_token(token + "!", "secret")
