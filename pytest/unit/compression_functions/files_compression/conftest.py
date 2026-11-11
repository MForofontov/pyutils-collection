"""Portable permission metadata for compression preflight checks."""

import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def deny_read_access(monkeypatch: pytest.MonkeyPatch) -> Callable[[Path], None]:
    """Remove read bits consistently; Windows chmod cannot revoke read access."""
    original_stat = os.stat
    denied: set[str] = set()

    def fake_stat(path: Any, *args: Any, **kwargs: Any) -> os.stat_result:
        result = original_stat(path, *args, **kwargs)
        if not isinstance(path, int) and os.path.abspath(os.fsdecode(path)) in denied:
            fields = list(result)
            fields[0] &= ~0o444
            return os.stat_result(fields)
        return result

    def deny(path: Path) -> None:
        denied.add(os.path.abspath(path))
        monkeypatch.setattr(os, "stat", fake_stat)

    return deny
