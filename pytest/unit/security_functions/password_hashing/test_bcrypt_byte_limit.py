"""Enforce bcrypt's byte boundary independently of the dependency version."""

import pytest
from pyutils_collection.security_functions.password_hashing.hash_password_bcrypt import (
    hash_password_bcrypt,
)
from pyutils_collection.security_functions.password_hashing.verify_password_bcrypt import (
    verify_password_bcrypt,
)

pytestmark = [pytest.mark.unit, pytest.mark.security]


@pytest.mark.parametrize("password", ["a" * 72, "é" * 36, "😀" * 18])
def test_bcrypt_utf8_byte_limit(password: str) -> None:
    hashed = hash_password_bcrypt(password, rounds=4)
    assert verify_password_bcrypt(password, hashed)
    with pytest.raises(ValueError, match="72 bytes"):
        hash_password_bcrypt(password + "a", rounds=4)
    assert not verify_password_bcrypt(password + "a", hashed)
