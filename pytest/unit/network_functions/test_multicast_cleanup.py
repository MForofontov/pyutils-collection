"""Socket setup failures must release the socket as well as receive failures."""

from unittest.mock import Mock

import pytest
from pyutils_collection.network_functions.multicast_receive import multicast_receive

pytestmark = [pytest.mark.unit, pytest.mark.network_functions]


@pytest.mark.parametrize("operation", ["setsockopt", "bind", "settimeout"])
def test_multicast_setup_failure_closes_socket(monkeypatch, operation):
    sock = Mock()
    getattr(sock, operation).side_effect = OSError("setup failed")
    monkeypatch.setattr("socket.socket", lambda *args: sock)
    with pytest.raises(OSError, match="setup failed"):
        multicast_receive("224.0.0.1", 5007)
    sock.close.assert_called_once_with()
