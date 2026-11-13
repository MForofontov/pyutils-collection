"""Classify address families using platform-specific constants."""

import socket
from types import SimpleNamespace
from typing import Any

import psutil
import pytest

from pyutils_collection.cli_functions import get_network_info

pytestmark = [pytest.mark.unit, pytest.mark.cli_functions]


@pytest.mark.parametrize(
    ("family", "category"),
    [
        (socket.AF_INET, "ipv4"),
        (socket.AF_INET6, "ipv6"),
        (psutil.AF_LINK, "mac"),
        (99999, "other"),
    ],
)
def test_native_family_classification(
    monkeypatch: pytest.MonkeyPatch, family: Any, category: str
) -> None:
    address = SimpleNamespace(
        family=family, address="test-address", netmask=None, broadcast=None, ptp=None
    )
    monkeypatch.setattr(psutil, "net_if_addrs", lambda: {"test": [address]})
    result = get_network_info()["test"]
    assert result[category] == [
        {"address": "test-address", "netmask": None, "broadcast": None, "ptp": None}
    ]
    assert sum(map(len, result.values())) == 1
