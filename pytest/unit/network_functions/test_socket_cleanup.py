"""Failure cleanup and ownership of socket timeout settings."""

import socket
from unittest.mock import MagicMock, patch

import pytest

from pyutils_collection.network_functions import (
    get_local_ip,
    is_internet_available,
    multicast_send,
)

pytestmark = [pytest.mark.unit, pytest.mark.network_functions]


@pytest.mark.parametrize("operation", ["local", "internet", "multicast"])
def test_socket_closed_after_operation_failure(operation: str) -> None:
    sock = MagicMock()
    error = OSError("injected socket failure")
    sock.connect.side_effect = error
    sock.sendto.side_effect = error
    original = socket.getdefaulttimeout()
    try:
        with patch.object(socket, "socket", return_value=sock):
            if operation == "local":
                assert get_local_ip() == "127.0.0.1"
            elif operation == "internet":
                assert is_internet_available() is False
            else:
                with pytest.raises(OSError) as caught:
                    multicast_send("hello", "224.0.0.1", 5007)
                assert caught.value is error
        sock.close.assert_called_once()
    finally:
        socket.setdefaulttimeout(original)


def test_probe_does_not_change_default_timeout() -> None:
    original = socket.getdefaulttimeout()
    sock = MagicMock()
    try:
        with patch.object(socket, "socket", return_value=sock):
            assert is_internet_available(timeout=3.25)
        assert socket.getdefaulttimeout() == original
        sock.settimeout.assert_called_once_with(3.25)
    finally:
        socket.setdefaulttimeout(original)
