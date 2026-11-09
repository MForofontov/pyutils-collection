"""Validation shared by the command-line SSH helpers."""

import math


def validate_target(host: str, user: str | None, timeout: float) -> None:
    """Reject option-like destinations and non-finite subprocess deadlines."""
    if not host or host.startswith("-") or any(c.isspace() for c in host):
        raise ValueError("host must be a non-empty hostname or IP address")
    if "\x00" in host or "@" in host:
        raise ValueError("host must not contain NUL or a username")
    if user is not None and (
        not user
        or user.startswith("-")
        or any(c.isspace() for c in user)
        or any(c in user for c in "@\x00")
    ):
        raise ValueError("user must be a non-empty SSH username")
    if not math.isfinite(timeout):
        raise ValueError("timeout must be finite and positive")
